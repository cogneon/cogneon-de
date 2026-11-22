#!/usr/bin/env python3
"""Link-Check vor dem Umzug: Wohin führt jede Adresse auf dem neuen Server?

Spielt die Weiterleitungen aus site/.htaccess (RewriteRule) gegen den gebauten
Ordner site/ durch, ohne Server. Geprüft werden

  - alle alten WordPress-Adressen (migration/old-urls.txt) und
  - alle internen Links in den gebauten Seiten.

Ergebnis je Adresse: vorhanden, per Weiterleitung erreichbar, extern
weitergeleitet (Ziel hier nicht prüfbar) oder fehlend (404).

Beispiel:
    python3 scripts/build_data.py && zensical build && python3 scripts/build_htaccess.py
    python3 scripts/check_links.py            # Bericht: migration/umzug-check.md
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

RULE_RE = re.compile(r'^RewriteRule\s+"?([^"\s]+)"?\s+"?([^"\s]+)"?(?:\s+\[([^\]]*)\])?')
HREF_RE = re.compile(r'<a\b[^>]*\bhref="([^"]+)"')
SKIP = ("mailto:", "tel:", "javascript:", "data:")


def load_rules(htaccess: Path) -> list[tuple[re.Pattern, str, bool]]:
    """RewriteRules ohne vorangestellte RewriteCond (die hängen an Query-Strings)."""
    rules, cond = [], False
    for line in htaccess.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("RewriteCond"):
            cond = True
            continue
        m = RULE_RE.match(line)
        if not m:
            continue
        if cond:
            cond = False
            continue
        muster, ziel, flags = m.group(1), m.group(2), m.group(3) or ""
        ziel = unquote(ziel.replace("\\%", "%"))
        rules.append((re.compile(muster), ziel, "R" in flags))
    return rules


def exists(site: Path, path: str) -> bool:
    p = site / path.lstrip("/")
    return p.is_file() or (p / "index.html").is_file()


def resolve(site: Path, rules, path: str) -> tuple[str, str]:
    """(status, endziel) mit status in vorhanden | weiterleitung | extern | fehlt."""
    seen, start = set(), path
    for _ in range(6):
        if exists(site, path):
            return ("vorhanden" if path == start else "weiterleitung"), path
        if path in seen:
            break
        seen.add(path)
        rel = path.lstrip("/")
        for muster, ziel, _ in rules:
            m = muster.search(rel)
            if m:
                ziel = m.expand(ziel.replace("$", "\\")) if "$" in ziel else ziel
                ziel = ziel.split("?")[0].split("#")[0] or "/"
                if ziel.startswith(("http://", "https://")):
                    return "extern", ziel
                path = ziel if ziel.startswith("/") else "/" + ziel
                break
        else:
            return "fehlt", path
    return "fehlt", path


def internal_links(site: Path) -> dict[str, set[str]]:
    links: dict[str, set[str]] = defaultdict(set)
    for f in site.rglob("*.html"):
        seite = "/" + str(f.relative_to(site)).removesuffix("index.html")
        for href in HREF_RE.findall(f.read_text(encoding="utf-8", errors="ignore")):
            if href.startswith(SKIP) or href.startswith("#"):
                continue
            u = urlparse(urljoin("https://cogneon.de" + seite, href))
            if u.netloc not in ("cogneon.de", "www.cogneon.de"):
                continue
            links[unquote(u.path) or "/"].add(seite)
    return links


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site", type=Path, default=Path("site"))
    ap.add_argument("--url-list", type=Path, default=Path("migration/old-urls.txt"))
    ap.add_argument("--report", type=Path, default=Path("migration/umzug-check.md"))
    args = ap.parse_args(argv)

    rules = load_rules(args.site / ".htaccess")
    alt = sorted({unquote(urlparse(u.strip()).path) or "/"
                  for u in args.url_list.read_text(encoding="utf-8").splitlines() if u.strip()})
    links = internal_links(args.site)

    out = ["# Umzugs-Check", "",
           "Erzeugt von scripts/check_umzug.py. Simuliert die Weiterleitungen aus "
           "site/.htaccess gegen den gebauten Ordner site/.", ""]
    fehler = 0
    for titel, pfade, quellen in (("Alte WordPress-Adressen", alt, None),
                                  ("Interne Links", sorted(links), links)):
        stand = defaultdict(list)
        for p in pfade:
            status, ziel = resolve(args.site, rules, p)
            stand[status].append((p, ziel))
        fehler += len(stand["fehlt"])
        out += [f"## {titel}", "",
                f"- geprüft: {len(pfade)}", f"- vorhanden: {len(stand['vorhanden'])}",
                f"- per Weiterleitung: {len(stand['weiterleitung'])}",
                f"- extern weitergeleitet: {len(stand['extern'])}",
                f"- fehlend (404): {len(stand['fehlt'])}", ""]
        if stand["fehlt"]:
            out += ["### Fehlend", ""]
            for p, _ in stand["fehlt"]:
                wo = f" - verlinkt auf {len(quellen[p])} Seite(n), z.B. {sorted(quellen[p])[0]}" if quellen else ""
                out.append(f"- `{p}`{wo}")
            out.append("")
        if stand["extern"]:
            out += ["### Extern weitergeleitet (Ziel von Hand prüfen)", ""]
            ziele = defaultdict(list)
            for p, z in stand["extern"]:
                ziele[urlparse(z).netloc].append(p)
            for host, ps in sorted(ziele.items(), key=lambda kv: -len(kv[1])):
                out.append(f"- {host}: {len(ps)}")
            out.append("")
        print(f"{titel}: {len(pfade)} geprüft, {len(stand['vorhanden'])} vorhanden, "
              f"{len(stand['weiterleitung'])} Weiterleitung, {len(stand['extern'])} extern, "
              f"{len(stand['fehlt'])} fehlend")
    args.report.write_text("\n".join(out), encoding="utf-8")
    print(f"Bericht: {args.report}")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
