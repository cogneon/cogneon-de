#!/usr/bin/env python3
"""Prüft die Links der gebauten Website (site/).

Intern:  Jeder Link und jedes Bild, das auf die eigene Website zeigt, muss als
         Datei im Build liegen oder in migration/redirects*.map stehen.
Extern:  Mit --extern wird jede fremde Adresse einmal abgerufen. Das braucht
         Netz und dauert, deshalb läuft es getrennt (wöchentlich).

Bericht: migration/link-check.md
Rückgabe 1, wenn interne Seitenlinks defekt sind (fehlende Medien und externe
Links zählen dafür nicht), mit --report-only immer 0.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import sys
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urldefrag, urljoin, urlsplit

OWN_HOSTS = {"cogneon.de", "www.cogneon.de"}
MEDIA_PREFIX = "/wp-content/"
SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "data:", "#")
# Vom Thema und vom Blog erzeugte Übersichten: ihre Links stehen auch auf den Beiträgen selbst.
SKIP_DIRS = ("category/", "author/", "tag/", "assets/")


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.found: list[tuple[str, str]] = []   # (Art, Adresse)
        self.ids: set[str] = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "a" and a.get("href"):
            self.found.append(("link", a["href"]))
        elif tag in ("img", "source", "video", "audio", "iframe") and a.get("src"):
            self.found.append(("bild" if tag == "img" else "medium", a["src"]))


def load_redirects(migration: Path) -> set[str]:
    rules = set()
    for path in sorted(migration.glob("redirects*.map")):
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.split("#")[0].strip()
            if line:
                rules.add(line.split()[0].rstrip("/") or "/")
    return rules


def exists(site: Path, path: str) -> bool:
    rel = unquote(path).lstrip("/")
    target = site / rel
    if target.is_file():
        return True
    return (target / "index.html").is_file()


def collect(site: Path):
    """Liefert interne und externe Verweise: Ziel -> Menge der Seiten, auf denen es vorkommt."""
    internal: dict[tuple[str, str], set[str]] = defaultdict(set)
    external: dict[str, set[str]] = defaultdict(set)
    for html_file in sorted(site.rglob("*.html")):
        rel = html_file.relative_to(site).as_posix()
        if rel.startswith(SKIP_DIRS) or rel == "404.html" or rel[:4].isdigit() and rel.count("/") == 1:
            continue
        page = "/" + rel.removesuffix("index.html")
        parser = Links()
        parser.feed(html_file.read_text(encoding="utf-8", errors="replace"))
        for kind, href in parser.found:
            href = href.strip()
            if not href or href.startswith(SKIP_SCHEMES):
                continue
            url, _ = urldefrag(urljoin("https://cogneon.de" + page, href))
            parts = urlsplit(url)
            if parts.scheme not in ("http", "https"):
                continue
            if parts.hostname in OWN_HOSTS:
                internal[(kind, parts.path or "/")].add(page)
            else:
                external[url].add(page)
    return internal, external


def check_internal(site: Path, internal, redirects: set[str]):
    pages, media = {}, {}
    for (kind, path), sources in internal.items():
        if exists(site, path) or (path.rstrip("/") or "/") in redirects:
            continue
        if path.startswith(MEDIA_PREFIX):
            media[path] = sources
        else:
            pages[path] = sources
    return pages, media


def fetch(url: str, timeout: float) -> str | None:
    """None, wenn erreichbar, sonst eine kurze Begründung."""
    import requests

    headers = {"User-Agent": "Mozilla/5.0 (compatible; cogneon-linkcheck; +https://cogneon.de)"}
    try:
        r = requests.head(url, allow_redirects=True, timeout=timeout, headers=headers)
        if r.status_code >= 400:
            r = requests.get(url, allow_redirects=True, timeout=timeout, headers=headers, stream=True)
        if r.status_code in (401, 403, 429, 999):
            return None      # Website sperrt Automaten aus, kein Hinweis auf einen defekten Link
        return None if r.status_code < 400 else f"HTTP {r.status_code}"
    except requests.exceptions.SSLError:
        return "Zertifikatsfehler"
    except requests.exceptions.Timeout:
        return "keine Antwort (Zeitüberschreitung)"
    except requests.exceptions.ConnectionError:
        return "nicht erreichbar"
    except requests.exceptions.RequestException as error:
        return type(error).__name__


def check_external(external, timeout: float, workers: int):
    broken = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        for url, reason in zip(external, pool.map(lambda u: fetch(u, timeout), external)):
            if reason:
                broken[url] = reason
    return broken


def section(title: str, hint: str, items: dict, reasons: dict | None = None, limit: int = 3) -> list[str]:
    lines = [f"## {title} ({len(items)})", "", hint, ""]
    for target in sorted(items):
        sources = sorted(items[target])
        where = ", ".join(f"`{s}`" for s in sources[:limit]) + (f" und {len(sources) - limit} weitere" if len(sources) > limit else "")
        reason = f" - {reasons[target]}" if reasons else ""
        lines.append(f"- `{target}`{reason}  \n  auf {where}")
    if not items:
        lines.append("Keine.")
    return lines + [""]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    root = Path(__file__).resolve().parent.parent
    parser.add_argument("--site", type=Path, default=root / "site")
    parser.add_argument("--migration", type=Path, default=root / "migration")
    parser.add_argument("--extern", action="store_true", help="auch fremde Adressen abrufen (braucht Netz)")
    parser.add_argument("--timeout", type=float, default=15)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args(argv)

    if not args.site.is_dir():
        print(f"FEHLER: {args.site} fehlt. Zuerst 'zensical build' ausführen.", file=sys.stderr)
        return 2
    internal, external = collect(args.site)
    pages, media = check_internal(args.site, internal, load_redirects(args.migration))

    report = ["# Linkprüfung", "",
              f"Geprüft: {len(internal)} interne Ziele, {len(external)} externe Adressen"
              + ("" if args.extern else " (extern nicht abgerufen)") + ".", ""]
    report += section("Defekte interne Links", "Diese Seiten gibt es auf der Website nicht. Link korrigieren oder Weiterleitung anlegen.", pages)
    broken = {}
    if args.extern:
        broken = check_external(external, args.timeout, args.workers)
        report += section("Defekte externe Links",
                          "Diese fremden Adressen antworten nicht oder mit einem Fehler. Vor dem Entfernen im Browser gegenprüfen.",
                          {u: external[u] for u in broken}, broken)
    report += section("Fehlende Medien", "Bilder und Dateien, die im Build fehlen.", media, limit=1)
    target = args.migration / "link-check.md"
    target.write_text("\n".join(report), encoding="utf-8")
    print(f"intern defekt {len(pages)}, Medien fehlen {len(media)}"
          + (f", extern defekt {len(broken)} von {len(external)}" if args.extern else f", extern nicht geprüft ({len(external)})"))
    print(f"Bericht: {target}")
    return 0 if args.report_only or not pages else 1


if __name__ == "__main__":
    sys.exit(main())
