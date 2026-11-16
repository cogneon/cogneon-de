#!/usr/bin/env python3
"""WordPress -> Markdown: wiederholbarer Export fuer cogneon.de.

Liest Beitraege, Seiten, Autoren, Kategorien und Medien ueber die oeffentliche
WordPress-REST-API und schreibt sie als Markdown mit Frontmatter in den
docs-Ordner. Das Skript kann beliebig oft laufen:

- Dateien mit `frozen: true` im Frontmatter werden nie ueberschrieben.
- Medien werden nur geladen, wenn sie lokal noch fehlen.
- Alte URLs landen in migration/url-map.csv (Grundlage fuer den URL-Check).

Beispiele:
    python scripts/wp_export.py --inventory-only
    python scripts/wp_export.py --limit 10            # Pilot
    python scripts/wp_export.py                       # Vollexport
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import os
import re
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

import requests
import yaml
from bs4 import BeautifulSoup, Comment
from markdownify import MarkdownConverter

USER_AGENT = "cogneon-de-export/1.0 (+https://github.com/cogneon/cogneon-de)"
CORE_TYPES_SKIP = {
    "attachment", "nav_menu_item", "wp_block", "wp_template",
    "wp_template_part", "wp_global_styles", "wp_navigation",
    "wp_font_family", "wp_font_face",
}
SHORTCODE_RE = re.compile(r"(?<!\[)\[([a-zA-Z][\w-]{2,})(?:\s[^\]\n]*)?\](?!\()")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------

class WordPress:
    """Kleiner Client fuer die WordPress-REST-API mit Paging und Retries."""

    def __init__(self, base_url: str, delay: float = 0.2):
        self.base_url = base_url.rstrip("/") + "/"
        self.api = urljoin(self.base_url, "wp-json/")
        self.delay = delay
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        # Optional: Anmeldung mit WordPress-Anwendungspasswort. Die Werte kommen
        # nur aus der Umgebung (lokal oder GitHub-Secret) und werden nie ausgegeben.
        user, password = os.environ.get("WP_USER"), os.environ.get("WP_APP_PASSWORD")
        self.authenticated = bool(user and password)
        if self.authenticated:
            self.session.auth = (user, password)

    def _get(self, url: str, params: dict | None = None, stream: bool = False):
        last = None
        for attempt in range(4):
            try:
                resp = self.session.get(url, params=params, timeout=60, stream=stream)
                if resp.status_code in (429, 500, 502, 503, 504):
                    raise requests.HTTPError(f"HTTP {resp.status_code}", response=resp)
                time.sleep(self.delay)
                return resp
            except requests.RequestException as exc:  # noqa: PERF203
                last = exc
                time.sleep(2 ** attempt)
        raise RuntimeError(f"Abruf fehlgeschlagen: {url} ({last})")

    def get(self, route: str, params: dict | None = None):
        return self._get(urljoin(self.api, route.lstrip("/")), params)

    def count(self, route: str) -> int | None:
        resp = self.get(route, {"per_page": 1, "_fields": "id"})
        if resp.status_code != 200:
            return None
        return int(resp.headers.get("X-WP-Total", 0))

    def items(self, route: str, params: dict | None = None, limit: int | None = None):
        """Alle Eintraege einer Sammlung, seitenweise."""
        page, got = 1, 0
        params = dict(params or {})
        params.setdefault("per_page", 100 if not limit else min(100, limit))
        while True:
            resp = self.get(route, {**params, "page": page})
            if resp.status_code == 400 and page > 1:
                return  # hinter der letzten Seite
            if resp.status_code != 200:
                raise RuntimeError(f"{route}: HTTP {resp.status_code}")
            batch = resp.json()
            if not batch:
                return
            for item in batch:
                yield item
                got += 1
                if limit and got >= limit:
                    return
            if page >= int(resp.headers.get("X-WP-TotalPages", page)):
                return
            page += 1

    def download(self, url: str, target: Path) -> int:
        resp = self._get(url, stream=True)
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code}")
        target.parent.mkdir(parents=True, exist_ok=True)
        size = 0
        with open(target, "wb") as fh:
            for chunk in resp.iter_content(65536):
                fh.write(chunk)
                size += len(chunk)
        return size


# --------------------------------------------------------------------------
# HTML -> Markdown
# --------------------------------------------------------------------------

class Converter(MarkdownConverter):
    """Markdownify mit sichtbaren Zeilenumbruechen (<br>), die Zensical versteht."""

    def convert_br(self, el, text, *args, **kwargs):
        return "<br>\n"

    def convert_a(self, el, text, *args, **kwargs):
        result = super().convert_a(el, text, *args, **kwargs)
        if el.get("data-embed") and result.endswith(")"):
            result += "{ .embed }"
        return result


def markdownify(html_text: str, **options) -> str:
    return Converter(**options).convert(html_text)


@dataclass
class Converted:
    markdown: str
    media: list[str] = field(default_factory=list)      # absolute URLs
    embeds: list[str] = field(default_factory=list)     # iframe-Quellen
    shortcodes: list[str] = field(default_factory=list)
    blocks: list[str] = field(default_factory=list)     # CSS-Klassen der WordPress-Bloecke
    lost_embeds: list[str] = field(default_factory=list)
    headings_shifted: bool = False
    relinked: list[str] = field(default_factory=list)    # Kachel-Links, auf Text umgehaengt
    h1_count: int = 0
    images_without_alt: int = 0


def _same_site(url: str, site_host: str) -> bool:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    return host in ("", site_host.removeprefix("www."))


def _local_path(url: str) -> str:
    """Absolute URL der eigenen Site -> wurzelrelativer Pfad (URL bleibt gleich)."""
    parts = urlparse(url)
    path = parts.path or "/"
    if parts.query:
        path += "?" + parts.query
    if parts.fragment:
        path += "#" + parts.fragment
    return path



QUOTE_CHARS = "‘’‚‛′“”„″«»'"
LEGACY_SHORTCODE_RE = re.compile(r"\[(av_video|av_button|bctt|vimeo|pdf-embedder)\b(.*?)\]", re.S)
PROVIDER_NAMES = {"youtube": "YouTube", "x": "X", "vimeo": "Vimeo", "twitter": "X"}


def _shortcode_attrs(raw: str) -> dict:
    """Attribute eines Shortcodes lesen. WordPress hat die Anfuehrungszeichen typografisch ersetzt."""
    text = html.unescape(raw)
    for char in QUOTE_CHARS:
        text = text.replace(char, '"')
    return {k.lower(): v for k, v in re.findall(r'([\w-]+)\s*=\s*"(.*?)"(?=\s+[\w-]+\s*=|\s*$)', text.strip(), flags=re.S)}


def _embed_link(url: str, title: str = "", provider: str = "") -> str:
    """Einheitliche HTML-Form fuer Einbettungen. Wird beim Umwandeln zu einem Link mit Klasse 'embed'."""
    host = urlparse(url).netloc.removeprefix("www.")
    name = PROVIDER_NAMES.get(provider.lower(), "") or host
    label = f"{name}: {title}" if title else f"Eingebetteter Inhalt: {name}"
    return f'<p><a href="{html.escape(url, quote=True)}" data-embed="1">{html.escape(label)}</a></p>'


def replace_legacy_shortcodes(source: str) -> str:
    """Shortcodes frueherer Themes und Plugins, die WordPress nur noch als Text ausgibt."""

    def repl(match):
        kind, attrs = match.group(1), _shortcode_attrs(match.group(2))
        if kind == "av_video" and attrs.get("src"):
            return _embed_link(attrs["src"])
        if kind == "av_button" and attrs.get("link"):
            url = attrs["link"].split(",", 1)[-1].strip()
            if url.startswith("http"):
                return f'<p><a href="{html.escape(url, quote=True)}">{html.escape(attrs.get("label") or url)}</a></p>'
        if kind == "bctt" and attrs.get("tweet"):
            return f"<blockquote><p>{attrs['tweet']}</p></blockquote>"
        if kind == "vimeo":
            found = re.search(r"(\d{6,})", html.unescape(match.group(2)))
            if found:
                return _embed_link(f"https://vimeo.com/{found.group(1)}", provider="vimeo")
        if kind == "pdf-embedder" and attrs.get("url"):
            name = unquote(urlparse(attrs["url"]).path.rsplit("/", 1)[-1])
            return f'<p><a href="{html.escape(attrs["url"], quote=True)}">PDF: {html.escape(name)}</a></p>'
        return match.group(0)

    return LEGACY_SHORTCODE_RE.sub(repl, source)


def _embed_privacy_target(container) -> tuple[str, str]:
    """Original-Adresse und Titel einer Einbettung, die das Plugin Embed Privacy verdeckt."""
    title, url = "", ""
    direct = container.select_one(".embed-privacy-url a[href]")
    if direct:
        url = direct["href"]
        title = re.sub(r"\s*direkt öffnen\s*$", "", direct.get_text(strip=True)).strip("„“\"” ")
    script = container.find("script")
    if script and script.string:
        embed = html.unescape(re.sub(r"\\+([/\"])", r"\1", script.string))
        if not title:
            found = re.search(r'title="([^"]+)"', embed)
            title = found.group(1) if found else ""
        if not url:
            status = re.findall(r'href="(https?://(?:twitter|x)\.com/[^"]+/status/\d+[^"]*)"', embed)
            src = re.search(r'src="(https?://[^"]+)"', embed)
            url = status[-1] if status else (src.group(1) if src else "")
    return url, title


def convert_html(source: str, base_url: str) -> Converted:
    site_host = urlparse(base_url).netloc.lower()
    soup = BeautifulSoup(replace_legacy_shortcodes(source or ""), "html.parser")
    out = Converted(markdown="")

    # Embed Privacy: Platzhalter durch die eigentliche Einbettung ersetzen.
    for container in soup.select(".embed-privacy-container"):
        provider = container.get("data-embed-provider", "")
        url, title = _embed_privacy_target(container)
        if url:
            out.embeds.append(url)
            container.replace_with(BeautifulSoup(_embed_link(url, title, provider), "html.parser"))
        else:
            out.lost_embeds.append(provider or "unbekannt")
            container.decompose()

    # Barrierefreiheit: eine Hauptueberschrift je Seite. Die setzt der Export aus dem Titel,
    # Ueberschriften im Inhalt ruecken deshalb eine Ebene tiefer, wenn dort eine h1 steht.
    if soup.find("h1"):
        for level in (5, 4, 3, 2, 1):
            for tag in soup.find_all(f"h{level}"):
                tag.name = f"h{level + 1}"
        out.headings_shifted = True

    for tag in soup.find_all(class_=True):
        for cls in tag.get("class", []):
            if re.fullmatch(r"(wp-block-[a-z0-9-]+|uagb-block-[a-z-]+[a-z])", cls) or cls.startswith("wp-block-uagb-"):
                out.blocks.append(cls)
    out.blocks = sorted(set(out.blocks))

    for node in soup.find_all(string=lambda s: isinstance(s, Comment)):
        node.extract()
    for tag in soup.find_all(["script", "style", "noscript", "svg", "form"]):
        tag.decompose()

    # Einbettungen: als Link stehen lassen, spaeter per Klick-zum-Laden ersetzen.
    for frame in soup.find_all("iframe"):
        src = frame.get("src") or frame.get("data-src") or frame.get("data-lazy-src")
        if not src:
            frame.decompose()
            continue
        src = urljoin(base_url, src)
        out.embeds.append(src)
        frame.replace_with(BeautifulSoup(_embed_link(src, frame.get("title", "")), "html.parser"))

    for img in soup.find_all("img"):
        src = img.get("data-lazy-src") or img.get("data-src") or img.get("src") or ""
        if not src or src.startswith("data:"):
            img.decompose()
            continue
        src = urljoin(base_url, src)
        for attr in ("srcset", "sizes", "data-lazy-src", "data-src", "data-lazy-srcset",
                     "loading", "decoding", "class", "width", "height", "style"):
            img.attrs.pop(attr, None)
        if not (img.get("alt") or "").strip():
            out.images_without_alt += 1
        if _same_site(src, site_host):
            out.media.append(src)
            img["src"] = _local_path(src)
        else:
            img["src"] = src

    for link in soup.find_all("a"):
        href = link.get("href")
        if not href:
            continue
        absolute = urljoin(base_url, href)
        if link.get("data-embed"):
            if absolute not in out.embeds:
                out.embeds.append(absolute)
            continue
        if not link.get_text(strip=True) and not link.find("img"):
            # Verlinkte Kachel (z. B. Spectra): leerer Link liegt ueber dem ganzen Block.
            # Der Link wandert auf die Ueberschrift oder den ersten Text des Blocks.
            label_host = None
            parent = link.parent
            if parent is not None and parent.name != "[document]":
                candidates = [el for el in parent.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "span", "p", "strong"])
                              if el is not link and el.get_text(strip=True) and not el.find("a")
                              and link not in el.descendants]
                headings = [el for el in candidates if el.name.startswith("h")]
                label_host = (headings or candidates or [None])[0]
            if label_host is not None:
                link.extract()
                link.clear()
                for child in list(label_host.contents):
                    link.append(child.extract())
                label_host.append(link)
            else:
                label = (link.get("aria-label") or link.get("title") or urlparse(absolute).netloc).strip()
                if not label:
                    link.decompose()
                    continue
                link.string = label
            out.relinked.append(absolute)
        if absolute.startswith(("http://", "https://")) and _same_site(absolute, site_host):
            link["href"] = _local_path(absolute)
            if "/wp-content/uploads/" in absolute:
                out.media.append(absolute.split("#")[0].split("?")[0])

    # Spectra-Icon-Listen sind inhaltlich Aufzaehlungen.
    for wrap in soup.find_all(class_="uagb-icon-list__wrap"):
        wrap.name = "ul"
        for child in wrap.find_all(class_="wp-block-uagb-icon-list-child", recursive=False):
            child.name = "li"

    for cap in soup.find_all("figcaption"):
        cap.name = "p"
        em = soup.new_tag("em")
        for child in list(cap.contents):
            em.append(child.extract())
        cap.append(em)

    text = markdownify(str(soup), heading_style="ATX", bullets="-", strong_em_symbol="*",
                       escape_underscores=False)
    text = text.replace(" ", " ")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    out.h1_count = len(re.findall(r"^# ", text, flags=re.M))
    out.markdown = text
    out.shortcodes = sorted({m.group(1) for m in SHORTCODE_RE.finditer(text)})
    out.media = list(dict.fromkeys(out.media))
    return out


def html_to_text(html: str) -> str:
    return re.sub(r"\s+", " ", BeautifulSoup(html or "", "html.parser").get_text()).strip()


# --------------------------------------------------------------------------
# Dateien
# --------------------------------------------------------------------------

def read_frontmatter(path: Path) -> dict:
    if not path.exists():
        return {}
    match = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}


def write_markdown(path: Path, meta: dict, body: str) -> str:
    """Schreibt die Datei. Rueckgabe: 'frozen', 'unchanged', 'created' oder 'updated'."""
    if read_frontmatter(path).get("frozen"):
        return "frozen"
    front = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=1000).strip()
    content = f"---\n{front}\n---\n\n{body}"
    if path.exists():
        if path.read_text(encoding="utf-8") == content:
            return "unchanged"
        state = "updated"
    else:
        state = "created"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return state


def with_title(title: str, markdown: str) -> str:
    """Setzt den Titel als Hauptueberschrift. Wiederholt der Inhalt ihn gleich am Anfang, entfaellt die Dopplung."""
    first, _, rest = markdown.lstrip().partition("\n")
    match = re.match(r"^#{1,6}\s+(.*?)\s*$", first)
    if match and re.sub(r"[*_`]", "", match.group(1)).strip().lower() == title.strip().lower():
        markdown = rest.lstrip("\n")
    return f"# {title}\n\n{markdown}"


def add_excerpt_marker(markdown: str) -> str:
    """Setzt den Anreisser-Trenner nach dem ersten Absatz."""
    blocks = markdown.strip().split("\n\n")
    if len(blocks) < 3:
        return markdown
    return "\n\n".join([blocks[0], "<!-- more -->", *blocks[1:]]) + "\n"


def url_path(link: str) -> str:
    path = unquote(urlparse(link).path)
    return path if path.endswith("/") or "." in path.rsplit("/", 1)[-1] else path + "/"


def permalink_pattern(link: str, slug: str, date: str) -> str:
    """Erkennt die Permalink-Struktur eines Beitrags, z. B. /{yyyy}/{mm}/{slug}/."""
    path = url_path(link)
    year, month, day = date[0:4], date[5:7], date[8:10]
    pattern = path.replace(f"/{slug}/", "/{slug}/")
    pattern = pattern.replace(f"/{year}/{month}/{day}/", "/{yyyy}/{mm}/{dd}/")
    pattern = pattern.replace(f"/{year}/{month}/", "/{yyyy}/{mm}/")
    pattern = pattern.replace(f"/{year}/", "/{yyyy}/")
    return pattern


# --------------------------------------------------------------------------
# Export
# --------------------------------------------------------------------------

def category_slug(name: str) -> str:
    """Slug, unter dem Zensical eine Kategorie veroeffentlicht (/category/<slug>/)."""
    return re.sub(r"\s", "-", re.sub(r"[^\w\s-]", "", name.lower()))


def tag_slug(name: str) -> str:
    """Adresse einer Schlagwort-Seite (/tag/<slug>/): klein, Umlaute ausgeschrieben."""
    s = name.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9-]", "", s)


def load_tag_map(migration: Path) -> dict[str, str] | None:
    """Zuordnung alter Schlagworte zu neuen aus migration/schlagworte.csv.
    Schluessel klein geschrieben. None, wenn es keine Zuordnung gibt (dann bleibt alles, wie es ist)."""
    path = migration / "schlagworte.csv"
    if not path.exists():
        return None
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    return {row["alt"].strip().lower(): row["neu"].strip()
            for row in csv.DictReader(lines) if row.get("alt") and row.get("neu")}


def redirect_sources(migration: Path) -> set[str]:
    """Alte Pfade, fuer die in migration/redirects.map eine Weiterleitung steht."""
    path = migration / "redirects.map"
    if not path.exists():
        return set()
    rules = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if line:
            rules.add(line.split()[0].rstrip("/") or "/")
    return rules


class Export:
    def __init__(self, wp: WordPress, root: Path, args):
        self.wp = wp
        self.root = root
        self.docs = root / args.out
        self.migration = root / "migration"
        self.args = args
        self.stats = Counter()
        self.patterns = Counter()
        self.shortcodes = Counter()
        self.embeds = Counter()
        self.problems: list[str] = []
        self.notes: list[str] = []
        self.blocks = Counter()
        self.block_examples: dict[str, str] = {}
        self.empty_links: list[tuple[str, str]] = []
        self.images_without_alt = Counter()
        self.h1_pages = Counter()
        self.frozen_changed: list[str] = []
        self.unmapped_authors = Counter()
        self.url_map: list[dict] = []
        self.media: dict[str, None] = {}
        self.categories: dict[int, dict] = {}
        self.tags: dict[int, dict] = {}
        self.tag_map: dict[str, str] | None = None
        self.used_tags: set[str] = set()
        self.users: dict[int, dict] = {}

    # -- Inventar ----------------------------------------------------------

    def inventory(self) -> dict:
        resp = self.wp.get("")
        if resp.status_code != 200:
            raise RuntimeError(f"REST-API nicht erreichbar: HTTP {resp.status_code} ({self._error_code(resp)})")
        root = resp.json()
        inv = {
            "name": root.get("name"),
            "description": root.get("description"),
            "url": root.get("url"),
            "timezone": root.get("timezone_string"),
            "namespaces": root.get("namespaces", []),
            "generated": datetime.now().isoformat(timespec="seconds"),
            "types": {},
        }
        resp = self.wp.get("wp/v2/types")
        types = resp.json() if resp.status_code == 200 else {}
        if not types or not all(isinstance(v, dict) for v in types.values()):
            self.problems.append(
                f"Inhaltstypen nicht abrufbar (wp/v2/types: HTTP {resp.status_code}, "
                f"{self._error_code(resp)}) - es werden nur Beiträge und Seiten gezählt.")
            types = {"post": {"name": "Beiträge", "rest_base": "posts"},
                     "page": {"name": "Seiten", "rest_base": "pages"}}
        for key, info in sorted(types.items()):
            if key in CORE_TYPES_SKIP:
                continue
            base = info.get("rest_base") or key
            ns = info.get("rest_namespace") or "wp/v2"
            inv["types"][key] = {
                "name": info.get("name"),
                "route": f"{ns}/{base}",
                "count": self.wp.count(f"{ns}/{base}"),
            }
        for label, route in (("media", "wp/v2/media"), ("categories", "wp/v2/categories"),
                             ("tags", "wp/v2/tags"), ("users", "wp/v2/users"),
                             ("comments", "wp/v2/comments")):
            inv[label] = self.wp.count(route)
        try:
            counts = Counter(p.get("author") for p in self.wp.items("wp/v2/posts", {"_fields": "id,author"}))
            inv["posts_by_author_id"] = {str(k): v for k, v in counts.most_common()}
        except RuntimeError:
            pass
        if "tribe/events/v1" in inv["namespaces"]:
            resp = self.wp.get("tribe/events/v1/events", {"per_page": 1, "start_date": "2000-01-01"})
            if resp.status_code == 200:
                inv["events"] = resp.json().get("total")
        self.migration.mkdir(parents=True, exist_ok=True)
        (self.migration / "inventory.json").write_text(
            json.dumps(inv, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return inv

    @staticmethod
    def _error_code(resp) -> str:
        try:
            data = resp.json()
            return str(data.get("code", "ohne Fehlercode")) if isinstance(data, dict) else "unerwartete Antwort"
        except ValueError:
            return "keine JSON-Antwort"

    # -- Stammdaten --------------------------------------------------------

    def load_taxonomies(self):
        fields = "id,name,slug,description,link,count"
        self.categories = {c["id"]: c for c in self.wp.items("wp/v2/categories", {"_fields": fields})}
        self.tags = {t["id"]: t for t in self.wp.items("wp/v2/tags", {"_fields": fields})}
        for term in (*self.categories.values(), *self.tags.values()):
            term["name"] = html.unescape(term["name"])
        self.tag_map = load_tag_map(self.migration)
        try:
            self.users = {u["id"]: u for u in self.wp.items(
                "wp/v2/users", {"_fields": "id,name,slug,description,link"})}
        except RuntimeError as exc:
            self.users = {}
            self.notes.append(f"Benutzerliste nicht abrufbar ({exc}). Autoren kommen aus migration/autoren.yml.")
        # Zuordnung von Hand: WordPress-Benutzer-ID -> Autorenkuerzel. Hat Vorrang.
        mapping_file = self.migration / "autoren.yml"
        if mapping_file.exists():
            mapping = yaml.safe_load(mapping_file.read_text(encoding="utf-8")) or {}
            for user_id, slug in mapping.items():
                known = self.users.get(int(user_id), {})
                self.users[int(user_id)] = {"id": int(user_id), "slug": str(slug),
                                            "name": known.get("name", str(slug)),
                                            "description": known.get("description", "")}

    def write_taxonomy_lists(self):
        """Schlagwort- und Kategorienlisten mit Haeufigkeit - Grundlage fuer die Konsolidierung."""
        self.migration.mkdir(parents=True, exist_ok=True)
        for name, terms in (("tags", self.tags), ("categories", self.categories)):
            rows = sorted(terms.values(), key=lambda t: (-int(t.get("count") or 0), t["slug"]))
            with open(self.migration / f"{name}.csv", "w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                writer.writerow(["slug", "name", "count", "old_path"])
                for term in rows:
                    writer.writerow([term["slug"], term["name"], term.get("count") or 0,
                                     url_path(term.get("link") or "")])
            self.stats[f"{name}_total"] = len(rows)
            self.stats[f"{name}_used_once_or_never"] = sum(1 for t in rows if int(t.get("count") or 0) <= 1)
        self.write_category_redirects()

    def map_tags(self, names: list[str]) -> list[str]:
        """Alte Schlagworte eines Beitrags auf die neuen abbilden: zusammengefuehrte werden
        ersetzt, gestrichene fallen weg, Doppelte entfallen."""
        if self.tag_map is None:
            return names
        result = []
        for name in names:
            new = self.tag_map.get(name.lower())
            if new and new not in result:
                result.append(new)
        self.used_tags.update(result)
        return result

    def write_tag_redirects(self):
        """Alte Schlagwort-Adressen auf die neuen Schlagwort-Seiten, gestrichene auf die Blog-Uebersicht."""
        if self.tag_map is None:
            return
        lines = ["# Erzeugt von scripts/wp_export.py - nicht von Hand ändern.",
                 "# Alte Schlagwort-Adressen aus WordPress -> neue Schlagwort-Seite oder Blog."]
        for term in sorted(self.tags.values(), key=lambda t: t["slug"]):
            old = url_path(term.get("link") or f"/tag/{term['slug']}/")
            new_name = self.tag_map.get(term["name"].lower())
            # Nur Schlagworte, die an mindestens einem Beitrag haengen, bekommen eine Seite.
            new = f"/tag/{tag_slug(new_name)}/" if new_name in self.used_tags else "/blog/"
            if old.rstrip("/") + "/" != new:
                lines.append(f"{old.rstrip('/')} {new}")
        (self.migration / "redirects-schlagworte.map").write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.stats["tag_redirects"] = len(lines) - 2

    def write_category_redirects(self):
        """WordPress-Kategorien liegen unter ihrem Kurznamen (/category/kclo/), Zensical
        veroeffentlicht sie unter dem Titel. Fuer jede Abweichung entsteht eine Weiterleitung."""
        lines = ["# Erzeugt von scripts/wp_export.py - nicht von Hand ändern.",
                 "# Alte Kategorie-Adressen aus WordPress -> Adresse in Zensical."]
        for term in sorted(self.categories.values(), key=lambda t: t["slug"]):
            old = url_path(term.get("link") or f"/category/{term['slug']}/").rstrip("/")
            new = f"/category/{category_slug(term['name'])}/"
            if old and old + "/" != new:
                lines.append(f"{old} {new}")
        (self.migration / "redirects-kategorien.map").write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.stats["category_redirects"] = len(lines) - 2

    def write_authors(self):
        """Ergaenzt docs/.authors.yml um fehlende Autoren. Bestehende bleiben unveraendert."""
        path = self.docs / ".authors.yml"
        data = {"authors": {}}
        if path.exists():
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or data
            data.setdefault("authors", {})
        added = 0
        for user in self.users.values():
            if user["slug"] in data["authors"]:
                continue
            data["authors"][user["slug"]] = {
                "name": user["name"],
                "description": html_to_text(user.get("description", "")) or "Cogneon",
                "avatar": "/assets/authors/platzhalter.svg",
            }
            added += 1
        if added or not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=True), encoding="utf-8")
        self.stats["authors_added"] = added

    # -- Inhalte -----------------------------------------------------------

    def _convert(self, item: dict) -> Converted:
        conv = convert_html(item["content"]["rendered"], self.wp.base_url)
        path = url_path(item["link"])
        if self.args.raw:
            raw = self.migration / "raw" / (path.strip("/").replace("/", "_") or "startseite")
            raw.parent.mkdir(parents=True, exist_ok=True)
            raw.with_suffix(".html").write_text(item["content"]["rendered"], encoding="utf-8")
        for cls in conv.blocks:
            self.blocks[cls] += 1
            self.block_examples.setdefault(cls, path)
        for href in conv.relinked:
            self.empty_links.append((path, href))
        if conv.h1_count:
            self.h1_pages[path] = conv.h1_count
        if conv.headings_shifted:
            self.stats["pages_headings_shifted"] += 1
        for provider in conv.lost_embeds:
            self.problems.append(f"Einbettung ohne auffindbare Adresse ({provider}): {path}")
        if conv.images_without_alt:
            self.images_without_alt[path] = conv.images_without_alt
        for code in conv.shortcodes:
            self.shortcodes[code] += 1
        for src in conv.embeds:
            self.embeds[urlparse(src).netloc] += 1
        for url in conv.media:
            self.media[url] = None
        return conv

    def _record(self, kind: str, item: dict, target: Path, state: str):
        if state == "frozen":
            old = read_frontmatter(target)
            seen = str((old.get("wp") or {}).get("modified") or (old.get("date") or {}).get("updated") or "")
            if seen and item["modified"][:10] > seen[:10]:
                self.frozen_changed.append(
                    f"`{target.relative_to(self.root)}`: in WordPress geändert am {item['modified'][:10]}, "
                    f"im Repo Stand {seen[:10]}")
        self.stats[f"{kind}_{state}"] += 1
        self.url_map.append({
            "old_path": url_path(item["link"]),
            "type": kind,
            "wp_id": item["id"],
            "file": str(target.relative_to(self.root)),
            "state": state,
        })

    def export_posts(self):
        fields = ("id,date,modified,slug,link,title,content,excerpt,author,"
                  "categories,tags,featured_media,sticky")
        for post in self.wp.items("wp/v2/posts", {"_fields": fields, "orderby": "date",
                                                  "order": "desc"}, self.args.limit):
            self.patterns[permalink_pattern(post["link"], post["slug"], post["date"])] += 1
            conv = self._convert(post)
            author = self.users.get(post.get("author"), {})
            meta = {
                "title": html_to_text(post["title"]["rendered"]),
                "date": {"created": post["date"][:10], "updated": post["modified"][:10]},
                "slug": post["slug"],
            }
            if author:
                meta["authors"] = [author["slug"]]
            elif post.get("author"):
                self.unmapped_authors[post["author"]] += 1
            cats = [self.categories[c]["name"] for c in post.get("categories", []) if c in self.categories]
            if cats:
                meta["categories"] = cats
            tags = self.map_tags([self.tags[t]["name"] for t in post.get("tags", []) if t in self.tags])
            if tags:
                meta["tags"] = tags
            if post.get("sticky"):
                meta["pin"] = True
            body = with_title(meta["title"], add_excerpt_marker(conv.markdown))
            target = self.docs / "blog" / "posts" / post["date"][:4] / f"{post['slug']}.md"
            # Das Beitragsbild traegt resolve_featured_media() ein. Bleibt es dasselbe,
            # wird es hier uebernommen, damit ein zweiter Lauf nichts aendert.
            old = read_frontmatter(target)
            if post.get("featured_media") and (old.get("wp") or {}).get("featured_media") == post["featured_media"]:
                for key in ("bild", "bild_alt", "bild_im_text"):
                    if key in old:
                        meta[key] = old[key]
            meta["wp"] = {"id": post["id"], "link": post["link"],
                          "featured_media": post.get("featured_media") or None}
            self._record("post", post, target, write_markdown(target, meta, body))

    def export_pages(self):
        fields = "id,date,modified,slug,link,title,content,parent,menu_order,template"
        pages = list(self.wp.items("wp/v2/pages", {"_fields": fields, "orderby": "id",
                                                   "order": "asc"}, self.args.limit))
        paths = [url_path(p["link"]) for p in pages]
        redirected = redirect_sources(self.migration)
        for page in pages:
            path = url_path(page["link"])
            rel = path.strip("/")
            if (path.rstrip("/") or "/") in redirected:
                # Fuer diese Adresse gibt es eine Weiterleitung: keine Seite anlegen.
                self.stats["page_redirected"] += 1
                continue
            has_children = any(other != path and other.startswith(path) for other in paths)
            if not rel:
                target = self.docs / "index.md"
            elif has_children:
                target = self.docs / rel / "index.md"
                stale = self.docs / f"{rel}.md"
                if stale.exists() and not read_frontmatter(stale).get("frozen"):
                    stale.unlink()
            else:
                target = self.docs / f"{rel}.md"
                stale = self.docs / rel / "index.md"   # Ablage aus frueheren Laeufen
                if stale.exists() and not read_frontmatter(stale).get("frozen"):
                    stale.unlink()
            conv = self._convert(page)
            meta = {
                "title": html_to_text(page["title"]["rendered"]),
                "wp": {"id": page["id"], "link": page["link"],
                       "modified": page["modified"][:10]},
            }
            body = with_title(meta["title"], conv.markdown)
            self._record("page", page, target, write_markdown(target, meta, body))

    def resolve_featured_media(self):
        """Beitragsbilder: IDs gesammelt aufloesen, zur Medienliste hinzufuegen und den
        Pfad als 'bild' in den Kopf des Beitrags schreiben (fuer Blog-Uebersicht und Beitragskopf)."""
        files: dict[int, list[Path]] = {}
        for row in self.url_map:
            if row["type"] != "post":
                continue
            path = self.root / row["file"]
            wp = read_frontmatter(path).get("wp") or {}
            if wp.get("featured_media"):
                files.setdefault(int(wp["featured_media"]), []).append(path)
        ids = sorted(files)
        for start in range(0, len(ids), 100):
            chunk = ",".join(str(i) for i in ids[start:start + 100])
            for media in self.wp.items("wp/v2/media", {"include": chunk, "_fields": "id,source_url,alt_text"}):
                if not media.get("source_url"):
                    continue
                self.media[media["source_url"]] = None
                rel = unquote(urlparse(media["source_url"]).path).lstrip("/")
                if not rel.startswith("wp-content/"):
                    continue
                for path in files.get(media["id"], []):
                    self.set_post_image(path, rel, html.unescape(media.get("alt_text") or ""))

    def set_post_image(self, path: Path, image: str, alt: str):
        match = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
        if not match:
            return
        meta = yaml.safe_load(match.group(1)) or {}
        if meta.get("frozen"):
            return
        body = path.read_text(encoding="utf-8")[match.end():].lstrip("\n")
        meta["bild"] = image
        if alt:
            meta["bild_alt"] = alt
        # Steht das Bild schon im Text, zeigt die Vorlage es oben nicht noch einmal.
        stem = re.sub(r"-\d+x\d+$", "", Path(image).stem)
        if stem and stem in body:
            meta["bild_im_text"] = True
        wp = meta.pop("wp", None)        # 'wp' bleibt der letzte Eintrag
        if wp is not None:
            meta["wp"] = wp
        write_markdown(path, meta, body)
        self.stats["post_images"] += 1

    def download_media(self):
        for url in self.media:
            path = unquote(urlparse(url).path).lstrip("/")
            if not path.startswith("wp-content/"):
                continue
            target = self.docs / path
            if target.exists():
                self.stats["media_present"] += 1
                continue
            try:
                self.stats["media_bytes"] += self.wp.download(url, target)
                self.stats["media_downloaded"] += 1
            except RuntimeError as exc:
                self.stats["media_failed"] += 1
                self.problems.append(f"Medium nicht ladbar: {url} ({exc})")

    # -- Bericht -----------------------------------------------------------

    def write_reports(self, inv: dict | None):
        self.migration.mkdir(parents=True, exist_ok=True)
        if self.url_map:
            with open(self.migration / "url-map.csv", "w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=list(self.url_map[0]))
                writer.writeheader()
                writer.writerows(sorted(self.url_map, key=lambda r: r["old_path"]))
        lines = ["# Migrationsbericht", "",
                 f"Erzeugt: {datetime.now().isoformat(timespec='seconds')}",
                 f"Quelle: {self.wp.base_url}", ""]
        if inv:
            lines += ["## Inventar", "", f"- Site: {inv.get('name')}",
                      f"- Medien: {inv.get('media')}", f"- Kategorien: {inv.get('categories')}",
                      f"- Schlagwörter: {inv.get('tags')}", f"- Autoren: {inv.get('users')}",
                      f"- Kommentare: {inv.get('comments')}"]
            if "events" in inv:
                lines.append(f"- Veranstaltungen: {inv['events']}")
            if inv.get("posts_by_author_id"):
                lines += ["", "Beiträge je WordPress-Benutzer-ID: " + ", ".join(
                    f"{k}: {v}" for k, v in inv["posts_by_author_id"].items())]
            lines += ["", "| Inhaltstyp | Route | Anzahl |", "|---|---|---|"]
            lines += [f"| {k} | `{v['route']}` | {v['count']} |" for k, v in inv["types"].items()]
            lines += ["", "API-Namespaces: " + ", ".join(f"`{n}`" for n in inv["namespaces"]), ""]
        lines += ["## Export", ""]
        lines += [f"- {key}: {value}" for key, value in sorted(self.stats.items())] or ["- kein Export"]
        if self.patterns:
            lines += ["", "## Permalink-Struktur der Beiträge", ""]
            lines += [f"- `{p}`: {n}" for p, n in self.patterns.most_common()]
        if self.shortcodes:
            lines += ["", "## Shortcodes im Inhalt (brauchen Ersatz)", ""]
            lines += [f"- `[{c}]`: {n} Seiten" for c, n in self.shortcodes.most_common()]
        if self.embeds:
            lines += ["", "## Einbettungen nach Anbieter", ""]
            lines += [f"- {h}: {n}" for h, n in self.embeds.most_common()]
        if self.blocks:
            lines += ["", "## WordPress-Blöcke im Inhalt", "", "| Block | Seiten | Beispiel |", "|---|---|---|"]
            lines += [f"| `{b}` | {n} | {self.block_examples[b]} |" for b, n in self.blocks.most_common()]
        if self.empty_links:
            lines += ["", "## Verlinkte Kacheln", "",
                      "Der Link lag unsichtbar über dem ganzen Block. Der Export hängt ihn an die "
                      "Überschrift oder den ersten Text des Blocks.", ""]
            lines += [f"- {page}: {href}" for page, href in self.empty_links[:200]]
        if self.images_without_alt:
            total = sum(self.images_without_alt.values())
            lines += ["", f"## Bilder ohne Beschreibung: {total} auf {len(self.images_without_alt)} Seiten", ""]
            lines += [f"- {page}: {n}" for page, n in self.images_without_alt.most_common(50)]
        if self.h1_pages:
            lines += ["", f"## Überschriften der ersten Ebene im Inhalt: {len(self.h1_pages)} Seiten", "",
                      "Barrierefreiheit: Je Seite soll es nur eine Hauptüberschrift geben. "
                      "Diese Seiten brauchen eine Korrektur der Ebenen.", ""]
            lines += [f"- {page}: {n}" for page, n in self.h1_pages.most_common(50)]
        if self.frozen_changed:
            lines += ["", "## Eingefrorene Seiten mit Änderungen in WordPress", "",
                      "Diese Seiten wurden nicht überschrieben. Änderungen bei Bedarf von Hand nachziehen.", ""]
            lines += [f"- {entry}" for entry in self.frozen_changed]
        if self.stats.get("media_bytes"):
            lines += ["", f"Geladene Medien: {self.stats['media_bytes'] / 1e6:.1f} MB"]
        if self.unmapped_authors:
            lines += ["", "## Beiträge ohne Autoren-Zuordnung", "",
                      "Diese Benutzer-IDs fehlen in `migration/autoren.yml`:", ""]
            lines += [f"- ID {i}: {n} Beiträge" for i, n in self.unmapped_authors.most_common()]
        if self.notes:
            lines += ["", "## Hinweise", ""] + [f"- {n}" for n in self.notes]
        if self.problems:
            lines += ["", "## Probleme", ""] + [f"- {p}" for p in self.problems]
        (self.migration / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def run(self) -> int:
        inv = self.inventory()
        print(f"Inventar: {json.dumps({k: v['count'] for k, v in inv['types'].items()})}")
        if self.wp.get("wp/v2/posts", {"per_page": 1, "_fields": "id"}).status_code in (401, 403):
            hint = ("Die Anmeldung wurde abgelehnt - Benutzername und Anwendungspasswort prüfen."
                    if self.wp.authenticated else
                    "Die REST-API verlangt eine Anmeldung. WP_USER und WP_APP_PASSWORD setzen "
                    "(WordPress-Anwendungspasswort), siehe README.")
            self.problems.append(hint)
            self.write_reports(inv)
            print(f"FEHLER: {hint}")
            return 2
        if not self.args.inventory_only:
            self.load_taxonomies()
            self.write_taxonomy_lists()
            self.write_authors()
            if "posts" in self.args.types:
                self.export_posts()
                self.write_tag_redirects()
            if "pages" in self.args.types:
                self.export_pages()
            if "posts" in self.args.types:
                self.resolve_featured_media()
            if not self.args.no_media:
                self.download_media()
        self.write_reports(inv)
        print("Ergebnis:", dict(sorted(self.stats.items())))
        print(f"Bericht: {self.migration / 'report.md'}")
        # Einzelne Medien, die es in WordPress selbst nicht mehr gibt, stehen im Bericht
        # und brechen den Lauf nicht ab. Fehlt mehr als jedes zehnte, stimmt etwas nicht.
        failed, loaded = self.stats["media_failed"], self.stats["media_downloaded"] + self.stats["media_present"]
        if failed:
            print(f"WARNUNG: {failed} Medien nicht ladbar, siehe Bericht.")
        return 1 if failed > max(3, loaded // 10) else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--base-url", default="https://cogneon.de")
    parser.add_argument("--out", default="docs", help="Zielordner relativ zum Repo")
    parser.add_argument("--types", default="posts,pages",
                        type=lambda s: [t.strip() for t in s.split(",") if t.strip()])
    parser.add_argument("--limit", type=int, help="nur die ersten N Einträge je Typ (Pilot)")
    parser.add_argument("--no-media", action="store_true", help="keine Medien laden")
    parser.add_argument("--raw", action="store_true",
                        help="Original-HTML je Seite nach migration/raw/ schreiben (zur Fehlersuche)")
    parser.add_argument("--inventory-only", action="store_true", help="nur zählen, nichts schreiben")
    parser.add_argument("--delay", type=float, default=0.2, help="Pause zwischen Abrufen in Sekunden")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent,
                        help="Repo-Wurzel (Standard: Ordner über scripts/)")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    return Export(WordPress(args.base_url, args.delay), root, args).run()


if __name__ == "__main__":
    sys.exit(main())
