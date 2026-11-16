#!/usr/bin/env python3
"""Erzeugt _data/aktuell.yml (Startseite) und overrides/partials/blog-daten.html (Blog-Übersicht).

Quellen:
  - inhalte/aktuell.yml   Highlights und Termine, von Hand gepflegt
  - docs/blog/posts/      die neuesten Blogbeiträge

Abgelaufene Highlights (gueltig_bis) und vergangene Termine (tag) fallen weg.
Aufruf vor jedem Build:  python scripts/build_data.py
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

import yaml


def as_date(value) -> dt.date | None:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        try:
            return dt.date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    try:
        return yaml.safe_load(text.split("---", 2)[1]) or {}
    except (IndexError, yaml.YAMLError):
        return {}


def category_slug(name: str) -> str:
    """Slug, unter dem Zensical eine Kategorie veröffentlicht (/category/<slug>/)."""
    return re.sub(r"\s", "-", re.sub(r"[^\w\s-]", "", name.lower()))


def excerpt(text: str, length: int = 220) -> str:
    """Anriss eines Beitrags: Text vor <!-- more -->, ohne Markdown, gekürzt an einer Wortgrenze."""
    body = text.split("---", 2)[2] if text.startswith("---") else text
    body = body.split("<!-- more -->")[0]
    body = re.sub(r"^#.*$", "", body, flags=re.M)                 # Überschriften
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)             # Bilder
    body = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", body)         # Links
    body = re.sub(r"<[^>]+>|\{[^}]*\}|[*_`>]", "", body)           # HTML, Attribute, Auszeichnung
    body = re.sub(r"\s+", " ", body).strip()
    body = re.sub(r"\s+([.,;:!?])", r"\1", body)
    if len(body) <= length:
        return body
    return body[:length].rsplit(" ", 1)[0].rstrip(".,;:- ") + " …"


def all_posts(post_dir: Path) -> list[dict]:
    """Alle veröffentlichten Beiträge, neueste zuerst."""
    posts = []
    for path in post_dir.rglob("*.md"):
        meta = frontmatter(path)
        if meta.get("draft"):
            continue
        date = meta.get("date")
        created = as_date(date.get("created") if isinstance(date, dict) else date)
        if not created or not meta.get("title"):
            continue
        slug = meta.get("slug") or path.stem
        posts.append({
            "titel": str(meta["title"]),
            "tag": created,
            "datum": created.strftime("%d.%m.%Y"),
            "url": f"{created:%Y/%m/%d}/{slug}/",
            "kategorien": [str(c) for c in meta.get("categories") or []],
            "schlagworte": [str(t) for t in meta.get("tags") or []],
            "bild": str(meta.get("bild") or ""),
            "bild_alt": str(meta.get("bild_alt") or ""),
            "pfad": path,
        })
    posts.sort(key=lambda p: (p["tag"], p["url"]), reverse=True)
    return posts


def build_blog(root: Path, newest: int = 10) -> dict:
    """Daten der Blog-Übersicht: neueste Beiträge mit Anriss, Kategorien, Archiv nach Jahren."""
    posts = all_posts(root / "docs" / "blog" / "posts")
    neueste = [{
        "titel": p["titel"], "datum": p["datum"], "url": p["url"],
        "kategorie": p["kategorien"][0] if p["kategorien"] else "",
        "auszug": excerpt(p["pfad"].read_text(encoding="utf-8")),
        # Bild nur, wenn die Datei im Repository liegt.
        **({"bild": p["bild"], "bild_alt": p["bild_alt"]}
           if p["bild"] and (root / "docs" / p["bild"]).is_file() else {}),
    } for p in posts[:newest]]
    counts: dict[str, int] = {}
    for p in posts:
        for name in p["kategorien"]:
            counts[name] = counts.get(name, 0) + 1
    kategorien = [{"titel": name, "anzahl": n, "url": f"category/{category_slug(name)}/"}
                  for name, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]
    archiv: list[dict] = []
    for p in posts:
        if not archiv or archiv[-1]["jahr"] != p["tag"].year:
            archiv.append({"jahr": p["tag"].year, "beitraege": []})
        archiv[-1]["beitraege"].append({"titel": p["titel"], "datum": p["datum"], "url": p["url"]})
    return {"neueste": neueste, "kategorien": kategorien, "archiv": archiv}


def tag_slug(name: str) -> str:
    """Adresse einer Schlagwort-Seite (/tag/<slug>/), wie in scripts/wp_export.py."""
    s = name.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9-]", "", s)


def build_tags(root: Path) -> int:
    """Eine Seite je Schlagwort unter docs/tag/<slug>.md und eine Übersicht docs/tag/index.md.
    Die Seiten werden bei jedem Lauf neu erzeugt und nicht ins Repository übernommen."""
    target = root / "docs" / "tag"
    if target.exists():
        for old in target.glob("*.md"):
            old.unlink()
    posts = all_posts(root / "docs" / "blog" / "posts")
    tags: dict[str, list[dict]] = {}
    for p in posts:
        for name in p["schlagworte"]:
            tags.setdefault(name, []).append({"titel": p["titel"], "datum": p["datum"],
                                              "url": "../../" + p["url"]})
    if not tags:
        return 0
    target.mkdir(parents=True, exist_ok=True)
    head = "<!-- Erzeugt von scripts/build_data.py - nicht von Hand ändern. -->\n"
    for name, items in tags.items():
        meta = {"title": name, "description": f"Beiträge zum Schlagwort {name}",
                "template": "schlagwort.html", "beitraege": items}
        (target / f"{tag_slug(name)}.md").write_text(
            "---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=1000)
            + "---\n" + head, encoding="utf-8")
    uebersicht = [{"titel": n, "anzahl": len(i), "url": f"{tag_slug(n)}/"}
                  for n, i in sorted(tags.items(), key=lambda kv: kv[0].lower())]
    meta = {"title": "Schlagworte", "description": "Alle Schlagworte im Blog von Cogneon",
            "template": "schlagwort.html", "schlagworte": uebersicht}
    (target / "index.md").write_text(
        "---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=1000)
        + "---\n" + head, encoding="utf-8")
    return len(tags)


def latest_posts(post_dir: Path, limit: int) -> list[dict]:
    posts = []
    for path in post_dir.rglob("*.md"):
        meta = frontmatter(path)
        if meta.get("draft"):
            continue
        date = meta.get("date")
        created = as_date(date.get("created") if isinstance(date, dict) else date)
        if not created or not meta.get("title"):
            continue
        slug = meta.get("slug") or path.stem
        posts.append({
            "titel": str(meta["title"]),
            "datum": created.strftime("%d.%m.%Y"),
            "url": f"{created:%Y/%m/%d}/{slug}/",
            "_tag": created,
        })
    posts.sort(key=lambda p: p["_tag"], reverse=True)
    return [{k: v for k, v in p.items() if k != "_tag"} for p in posts[:limit]]


def build(root: Path, today: dt.date, limit: int = 4) -> dict:
    source = root / "inhalte" / "aktuell.yml"
    data = yaml.safe_load(source.read_text(encoding="utf-8")) if source.exists() else {}
    data = data or {}

    highlights = []
    for item in data.get("highlights") or []:
        until = as_date(item.get("gueltig_bis"))
        if until and until < today:
            continue
        highlights.append({k: v for k, v in item.items() if k != "gueltig_bis"})

    termine = []
    for item in data.get("termine") or []:
        day = as_date(item.get("tag"))
        if day and day < today:
            continue
        termine.append({k: v for k, v in item.items() if k != "tag"})

    blog = latest_posts(root / "docs" / "blog" / "posts", limit)
    if not blog:
        blog = data.get("blog_vorschau") or []

    return {"highlights": highlights, "termine": termine, "blog": blog}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--heute", help="Stichtag JJJJ-MM-TT (Standard: heute)")
    args = parser.parse_args()
    today = as_date(args.heute) if args.heute else dt.date.today()
    if today is None:
        print("Ungültiges Datum für --heute", file=sys.stderr)
        return 2
    result = build(args.root, today)
    target = args.root / "_data" / "aktuell.yml"
    target.parent.mkdir(exist_ok=True)
    target.write_text(
        "# Erzeugt von scripts/build_data.py - nicht von Hand ändern.\n"
        + yaml.safe_dump(result, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    print(f"{target.relative_to(args.root)}: {len(result['highlights'])} Highlights, "
          f"{len(result['termine'])} Termine, {len(result['blog'])} Beiträge")
    # Die Blog-Daten gehen nicht nach _data/: Daten dort landen im Kontext jeder
    # Seite und bremsen den Build stark. Stattdessen entsteht eine Vorlagen-Datei,
    # die nur die Blog-Übersicht einbindet.
    blog = build_blog(args.root)
    target = args.root / "overrides" / "partials" / "blog-daten.html"
    target.write_text(
        "{#- Erzeugt von scripts/build_data.py - nicht von Hand ändern. -#}\n"
        "{% set blog = " + json.dumps(blog, ensure_ascii=False) + " %}\n",
        encoding="utf-8",
    )
    print(f"{target.relative_to(args.root)}: {sum(len(j['beitraege']) for j in blog['archiv'])} Beiträge, "
          f"{len(blog['kategorien'])} Kategorien")
    anzahl = build_tags(args.root)
    print(f"docs/tag/: {anzahl} Schlagwort-Seiten")
    return 0


if __name__ == "__main__":
    sys.exit(main())
