#!/usr/bin/env python3
"""Erzeugt site/.htaccess für den Apache-Webserver (Ionos).

Inhalt:
  - Weiterleitungen aus migration/redirects*.map (alte Adressen aus WordPress)
  - Server-Regeln für Adressen, die WordPress dynamisch bedient hat:
    /feed/, das Kalender-Abo /events/?ical=1, Feeds je Kategorie
  - Fehlerseite, Zeichensatz, Dateitypen, Caching
  - Suchmaschinen-Sperre auf allen Adressen außer cogneon.de (Vorschau)

Aufruf nach dem Build:  python scripts/build_htaccess.py
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import quote, unquote

KOPF = """# Erzeugt von scripts/build_htaccess.py - nicht von Hand ändern.

AddDefaultCharset utf-8
AddType text/calendar .ics
AddType application/rss+xml .xml
ErrorDocument 404 /404.html
Options -Indexes

# Nur cogneon.de darf in Suchmaschinen erscheinen, Vorschau-Adressen nicht.
SetEnvIfNoCase Host "^(www\\.)?cogneon\\.de$" COGNEON_LIVE
<IfModule mod_headers.c>
  Header set X-Robots-Tag "noindex, nofollow" env=!COGNEON_LIVE
</IfModule>

# HTML, CSS und JavaScript: Der Browser fragt bei jedem Aufruf kurz nach, ob
# es eine neue Fassung gibt (sonst Antwort 304, ohne Download). So passen
# Seite und Stylesheet nach einem Veröffentlichen sofort zusammen.
<IfModule mod_headers.c>
  <FilesMatch "\\.(html|css|js)$">
    Header set Cache-Control "no-cache"
  </FilesMatch>
</IfModule>

<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType font/woff2 "access plus 1 year"
  ExpiresByType image/jpeg "access plus 1 month"
  ExpiresByType image/png "access plus 1 month"
  ExpiresByType image/svg+xml "access plus 1 month"
  ExpiresByType image/webp "access plus 1 month"
</IfModule>

RewriteEngine On

# www.cogneon.de -> cogneon.de (eine Adresse je Seite). http -> https stellt
# Ionos über die SSL-Einstellung der Domain sicher.
RewriteCond %{HTTP_HOST} ^www\\.cogneon\\.de$ [NC]
RewriteRule ^(.*)$ https://cogneon.de/$1 [R=301,L]

# Adressen, die WordPress dynamisch bedient hat
RewriteRule ^feed/?$ /feed.xml [L]
RewriteRule ^(category|tag|author)/.+/feed/?$ /feed/ [R=301,L]
RewriteRule ^comments/feed/?$ /feed/ [R=301,L]
RewriteCond %{QUERY_STRING} (^|&)ical=1(&|$)
RewriteRule ^events?(/.*)?$ /events/cogneon.ics? [R=302,L]
RewriteCond %{QUERY_STRING} (^|&)p=\\d+ [OR]
RewriteCond %{QUERY_STRING} (^|&)s=
RewriteRule ^$ /blog/? [R=302,L]

# Weiterleitungen alter Adressen
"""


def load_rules(migration: Path) -> list[tuple[str, str]]:
    rules: dict[str, str] = {}
    # redirects.map (von Hand gepflegt) zuletzt, damit es im Zweifel gewinnt.
    files = sorted(migration.glob("redirects-*.map")) + [migration / "redirects.map"]
    for path in files:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.split(" #")[0].strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) != 2 or not parts[0].startswith("/"):
                print(f"übersprungen ({path.name}): {line}", file=sys.stderr)
                continue
            rules[parts[0].rstrip("/") or "/"] = parts[1]
    return sorted(rules.items())


def rule(source: str, target: str) -> str | None:
    """Eine RewriteRule. Apache vergleicht mit der entschlüsselten Adresse ohne führenden
    Schrägstrich; ein Schrägstrich am Ende ist freigestellt."""
    path = unquote(source).strip("/")
    if not path or (target.rstrip("/") == source.rstrip("/")):
        return None                       # Startseite oder Weiterleitung auf sich selbst
    pattern = re.escape(path).replace("\\-", "-").replace("\\/", "/").replace("\\ ", " ")
    # Umlaute und Leerzeichen im Ziel kodieren. "%" leitet in Apache einen Rückbezug ein
    # und wird deshalb maskiert; NE verhindert, dass Apache ein zweites Mal kodiert.
    target = quote(target, safe=":/?#[]@!$&'()*+,;=%-._~").replace("%", "\\%")
    return f'RewriteRule "^{pattern}/?$" "{target}" [R=301,L,NE]'


def main(argv=None) -> int:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--site", type=Path, default=root / "site")
    parser.add_argument("--migration", type=Path, default=root / "migration")
    args = parser.parse_args(argv)
    if not args.site.is_dir():
        print(f"FEHLER: {args.site} fehlt. Zuerst 'zensical build' ausführen.", file=sys.stderr)
        return 2
    lines, skipped = [], 0
    for source, target in load_rules(args.migration):
        # Liegt unter der alten Adresse eine echte Seite, hat sie Vorrang.
        rel = unquote(source).strip("/")
        if (args.site / rel / "index.html").is_file() or (rel and (args.site / rel).is_file()):
            skipped += 1
            continue
        line = rule(source, target)
        if line:
            lines.append(line)
    (args.site / ".htaccess").write_text(KOPF + "\n".join(lines) + "\n", encoding="utf-8")
    print(f"site/.htaccess: {len(lines)} Weiterleitungen" + (f", {skipped} übergangen (Seite vorhanden)" if skipped else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
