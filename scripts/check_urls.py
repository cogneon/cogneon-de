#!/usr/bin/env python3
"""URL-Check: Bleiben alle alten URLs erreichbar? (Cool URLs don't change.)

Vergleicht eine Liste alter URLs mit dem gebauten Ordner site/. Jede alte URL
muss entweder als Seite existieren oder in der Redirect-Liste stehen.

Quellen fuer alte URLs (kombinierbar):
    --url-map migration/url-map.csv     aus dem Export
    --url-list migration/old-urls.txt   eine URL oder ein Pfad pro Zeile
    --sitemap https://cogneon.de/wp-sitemap.xml   live abrufen und speichern

Beispiel:
    zensical build && python scripts/check_urls.py --url-map migration/url-map.csv
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

LOC_RE = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>")


def to_path(url: str) -> str:
    return unquote(urlparse(url.strip()).path) or "/"


def from_sitemap(url: str, seen: set[str] | None = None) -> list[str]:
    import requests  # nur fuer diesen Modus noetig

    seen = seen if seen is not None else set()
    if url in seen:
        return []
    seen.add(url)
    text = requests.get(url, timeout=60, headers={"User-Agent": "cogneon-de-urlcheck/1.0"}).text
    locs = LOC_RE.findall(text)
    if "<sitemapindex" in text:
        return [u for loc in locs for u in from_sitemap(loc, seen)]
    return locs


def load_redirects(path: Path | None) -> set[str]:
    """Format: 'alter-pfad neues-ziel' pro Zeile, # fuer Kommentare."""
    if not path or not path.exists():
        return set()
    rules = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if line:
            rules.add(line.split()[0].rstrip("/") or "/")
    return rules


def exists(site: Path, path: str) -> bool:
    rel = path.strip("/")
    if not rel:
        return (site / "index.html").exists()
    candidate = site / rel
    return candidate.is_file() or (candidate / "index.html").is_file()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--site", type=Path, default=Path("site"))
    parser.add_argument("--url-map", type=Path)
    parser.add_argument("--url-list", type=Path)
    parser.add_argument("--sitemap")
    parser.add_argument("--save-list", type=Path, help="abgerufene Sitemap-URLs hier speichern")
    parser.add_argument("--redirects", type=Path, default=Path("migration/redirects.map"))
    parser.add_argument("--report", type=Path, default=Path("migration/url-check.md"))
    parser.add_argument("--report-only", action="store_true", help="nie mit Fehler beenden")
    args = parser.parse_args(argv)

    paths: set[str] = set()
    if args.url_map and args.url_map.exists():
        with open(args.url_map, encoding="utf-8") as fh:
            paths |= {row["old_path"] for row in csv.DictReader(fh)}
    if args.url_list and args.url_list.exists():
        paths |= {to_path(l) for l in args.url_list.read_text(encoding="utf-8").splitlines() if l.strip()}
    if args.sitemap:
        urls = from_sitemap(args.sitemap)
        if args.save_list:
            args.save_list.parent.mkdir(parents=True, exist_ok=True)
            args.save_list.write_text("\n".join(sorted(urls)) + "\n", encoding="utf-8")
        paths |= {to_path(u) for u in urls}
    if not paths:
        print("Keine alten URLs gefunden - nichts zu prüfen.")
        return 0

    redirects = load_redirects(args.redirects)
    ok, redirected, missing = [], [], []
    for path in sorted(paths):
        if exists(args.site, path):
            ok.append(path)
        elif (path.rstrip("/") or "/") in redirects:
            redirected.append(path)
        else:
            missing.append(path)

    lines = ["# URL-Check", "", f"- geprüft: {len(paths)}", f"- als Seite vorhanden: {len(ok)}",
             f"- per Redirect abgedeckt: {len(redirected)}", f"- fehlend: {len(missing)}", ""]
    if missing:
        lines += ["## Fehlende URLs", ""] + [f"- `{p}`" for p in missing]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"geprüft {len(paths)}, vorhanden {len(ok)}, Redirect {len(redirected)}, fehlend {len(missing)}")
    return 0 if args.report_only or not missing else 1


if __name__ == "__main__":
    sys.exit(main())
