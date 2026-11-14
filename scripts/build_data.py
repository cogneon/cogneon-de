#!/usr/bin/env python3
"""Erzeugt _data/aktuell.yml für die Startseite.

Quellen:
  - inhalte/aktuell.yml   Highlights und Termine, von Hand gepflegt
  - docs/blog/posts/      die neuesten Blogbeiträge

Abgelaufene Highlights (gueltig_bis) und vergangene Termine (tag) fallen weg.
Aufruf vor jedem Build:  python scripts/build_data.py
"""
from __future__ import annotations

import argparse
import datetime as dt
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
