#!/usr/bin/env python3
"""Neue Blogbeiträge und Termine auf Mastodon ankündigen.

Läuft in .github/workflows/deploy.yml nach dem Hochladen, nur bei einem Merge
nach main. Bekommt die in diesem Merge neu hinzugefügten Dateien und postet je
neuem Beitrag oder Termin einen Toot:

    Neuer Blog-Beitrag auf cogneon.de: <Titel>
    <Link>

Sicherungen:
  - ohne Secrets MASTODON_INSTANZ und MASTODON_TOKEN passiert nichts
  - Entwürfe, Beiträge mit Datum in der Zukunft oder älter als 14 Tage und
    vergangene Termine werden übersprungen
  - mehr als 3 neue Einträge auf einmal (z.B. ein Import): nichts posten
  - steht der Link schon in einem der letzten 40 eigenen Toots: nicht nochmal

Mit --zuordnung schreibt es für Blogbeiträge Beitrag -> Toot in eine JSON-Datei.
Daraus zeigt die Beitragsseite den Kommentarbereich (Antworten auf den Toot).

    git diff --name-only --diff-filter=A <vorher> HEAD | python3 scripts/mastodon.py
    ... | python3 scripts/mastodon.py --probe     # nur anzeigen, nichts posten
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_data  # noqa: E402

HOECHSTENS = 3
MAX_ALTER_TAGE = 14


def site_url(root: Path) -> str:
    for zeile in (root / "zensical.toml").read_text(encoding="utf-8").splitlines():
        if zeile.startswith("site_url"):
            return zeile.split("=", 1)[1].strip().strip('"').rstrip("/") + "/"
    return "https://cogneon.de/"


def ankuendigungen(root: Path, neue_dateien: list[str], heute: dt.date) -> tuple[list[dict], list[str]]:
    basis = site_url(root)
    neu = {Path(d).as_posix() for d in neue_dateien}
    toots, hinweise = [], []
    for p in build_data.all_posts(root / "docs" / "blog" / "posts", auch_zukuenftige=True):
        rel = p["pfad"].relative_to(root).as_posix()
        if rel not in neu:
            continue
        if p["tag"] > heute or (heute - p["tag"]).days > MAX_ALTER_TAGE:
            hinweise.append(f"übersprungen (Datum {p['datum']}): {rel}")
            continue
        toots.append({"url": basis + p["url"], "seite": p["url"],
                      "text": f"Neuer Blog-Beitrag auf cogneon.de: {p['titel']}\n\n{basis + p['url']}"})
    for e in build_data.all_events(root):
        rel = f"docs/event/{e['slug']}.md"
        if rel not in neu:
            continue
        if e["ende"].date() < heute:
            hinweise.append(f"übersprungen (vorbei): {rel}")
            continue
        wann = " · ".join(x for x in (e["datum"], e["ort"]) if x)
        toots.append({"url": basis + e["url"],
                      "text": f"Neuer Termin auf cogneon.de: {e['titel']} ({wann})\n\n{basis + e['url']}"})
    # Entwürfe und Dateien ohne Titel tauchen oben nicht auf.
    bekannt = {t["url"] for t in toots}
    for d in sorted(neu):
        if d.startswith(("docs/blog/posts/", "docs/event/")) and d.endswith(".md") \
                and not any(Path(d).stem in u for u in bekannt) \
                and not any(Path(d).name in h for h in hinweise):
            hinweise.append(f"übersprungen (Entwurf oder ohne Titel/Datum): {d}")
    return toots, hinweise


def faellige_dateien(root: Path, heute: dt.date, zuordnung: Path | None) -> list[str]:
    """Vordatierte Blogbeiträge, deren Tag heute oder gestern war (falls ein Lauf
    ausfiel) und die noch keinen Post haben - für den morgendlichen Lauf."""
    import json
    bekannt = json.loads(zuordnung.read_text(encoding="utf-8")) if zuordnung and zuordnung.exists() else {}
    return [p["pfad"].relative_to(root).as_posix()
            for p in build_data.all_posts(root / "docs" / "blog" / "posts", auch_zukuenftige=True)
            if heute - dt.timedelta(days=1) <= p["tag"] <= heute and p["url"] not in bekannt]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--probe", action="store_true", help="nur anzeigen, nichts posten")
    ap.add_argument("--heute", help="Stichtag JJJJ-MM-TT (zum Testen)")
    ap.add_argument("--faellig", action="store_true",
                    help="statt neuer Dateien von stdin: vordatierte Beiträge, die heute erscheinen")
    ap.add_argument("--zuordnung", type=Path,
                    help="JSON-Datei Beitrag -> Toot, wird um die geposteten Blogbeiträge ergänzt")
    args = ap.parse_args(argv)
    heute = build_data.as_date(args.heute) if args.heute else build_data.stichtag()
    build_data.STICHTAG = heute

    if args.faellig:
        dateien = faellige_dateien(args.root, heute, args.zuordnung)
    else:
        dateien = [z.strip() for z in sys.stdin.read().splitlines() if z.strip()]
    toots, hinweise = ankuendigungen(args.root, dateien, heute)
    for h in hinweise:
        print(h)
    if not toots:
        print("Nichts anzukündigen.")
        return 0
    if len(toots) > HOECHSTENS:
        print(f"{len(toots)} neue Einträge auf einmal - vermutlich ein Import. Nichts gepostet:")
        for t in toots:
            print(f"  {t['url']}")
        return 0

    instanz = os.environ.get("MASTODON_INSTANZ", "").rstrip("/")
    token = os.environ.get("MASTODON_TOKEN", "")
    if args.probe or not (instanz and token):
        print("Nur Probe, nichts gepostet." if args.probe else
              "MASTODON_INSTANZ oder MASTODON_TOKEN fehlt, nichts gepostet.")
        for t in toots:
            print("---\n" + t["text"])
        return 0

    import requests
    kopf = {"Authorization": f"Bearer {token}"}
    ich = requests.get(f"{instanz}/api/v1/accounts/verify_credentials", headers=kopf, timeout=20)
    ich.raise_for_status()
    letzte = requests.get(f"{instanz}/api/v1/accounts/{ich.json()['id']}/statuses",
                          params={"limit": 40}, headers=kopf, timeout=20)
    letzte.raise_for_status()
    zuordnung = {}
    for t in toots:
        frueher = next((s for s in letzte.json() if t["url"] in s.get("content", "")), None)
        if frueher:
            print(f"schon gepostet: {t['url']}")
            toot = frueher
        else:
            antwort = requests.post(
                f"{instanz}/api/v1/statuses",
                headers={**kopf, "Idempotency-Key": hashlib.sha1(t["url"].encode()).hexdigest()},
                data={"status": t["text"], "language": "de", "visibility": "public"}, timeout=30)
            antwort.raise_for_status()
            toot = antwort.json()
            print(f"gepostet: {toot.get('url')}")
        if t.get("seite") and toot.get("url"):
            zuordnung[t["seite"]] = toot["url"]
    if args.zuordnung and zuordnung:
        import json
        bisher = json.loads(args.zuordnung.read_text(encoding="utf-8")) if args.zuordnung.exists() else {}
        args.zuordnung.write_text(json.dumps({**bisher, **zuordnung}, ensure_ascii=False, indent=1,
                                             sort_keys=True) + "\n", encoding="utf-8")
        print(f"Kommentare: {len(zuordnung)} Beitrag/Beiträge mit Toot verknüpft")
    return 0


if __name__ == "__main__":
    sys.exit(main())
