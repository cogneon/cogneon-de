#!/usr/bin/env python3
"""Neue Blogbeiträge und Termine auf Bluesky (AT-Protokoll) ankündigen.

Gegenstück zu scripts/mastodon.py, gleiche Auswahl und Sicherungen (keine
Entwürfe, keine alten oder zukünftigen Beiträge, keine vergangenen Termine,
nichts bei mehr als 3 neuen Einträgen, keine Doppelposts). Funktioniert mit
jedem AT-Protokoll-Konto, auch auf eurosky.social: Der Server des Kontos (PDS)
wird aus dem Handle ermittelt.

Der Post enthält den Text, einen anklickbaren Link und eine Link-Karte mit dem
Vorschaubild aus site/assets/social/ (falls gebaut).

Secrets: BLUESKY_HANDLE (z.B. cogneon.eurosky.social) und BLUESKY_APP_PASSWORD
(App-Passwort, nicht das Konto-Passwort).

    git diff --name-only --diff-filter=A <vorher> HEAD | python3 scripts/bluesky.py
    ... | python3 scripts/bluesky.py --probe       # nur anzeigen, nichts posten
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_data  # noqa: E402
from mastodon import HOECHSTENS, ankuendigungen, faellige_dateien, site_url  # noqa: E402

OEFFENTLICH = "https://public.api.bsky.app"
MAX_ZEICHEN = 300


def kuerzen(titel: str, rest: str) -> str:
    """Titel so kürzen, dass Titel + Rest höchstens MAX_ZEICHEN Zeichen haben."""
    frei = MAX_ZEICHEN - len(rest)
    return titel if len(titel) <= frei else titel[: max(10, frei - 1)].rstrip() + "…"


def post_text(t: dict) -> tuple[str, list[dict]]:
    """Text (Kopf + Link) und die Facette, die den Link anklickbar macht."""
    kopf, link = t["text"].split("\n\n", 1)
    praefix, titel = kopf.split(": ", 1)
    text_ohne = f"{praefix}: " + "{}" + f"\n\n{link}"
    text = text_ohne.format(kuerzen(titel, text_ohne.format("")))
    start = len(text.encode("utf-8")) - len(link.encode("utf-8"))
    facette = {"index": {"byteStart": start, "byteEnd": start + len(link.encode("utf-8"))},
               "features": [{"$type": "app.bsky.richtext.facet#link", "uri": link}]}
    return text, [facette]


def bild_fuer(root: Path, basis: str, url: str) -> Path | None:
    rel = url.removeprefix(basis)
    datei = root / "site" / "assets" / "social" / ((rel.strip("/") or "start").replace("/", "-") + ".png")
    return datei if datei.exists() else None


def web_adresse(handle_oder_did: str, at_uri: str) -> str:
    rkey = at_uri.rsplit("/", 1)[1]
    return f"https://bsky.app/profile/{handle_oder_did}/post/{rkey}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--probe", action="store_true", help="nur anzeigen, nichts posten")
    ap.add_argument("--heute", help="Stichtag JJJJ-MM-TT (zum Testen)")
    ap.add_argument("--faellig", action="store_true",
                    help="statt neuer Dateien von stdin: vordatierte Beiträge, die heute erscheinen")
    ap.add_argument("--zuordnung", type=Path, help="JSON-Datei Beitrag -> Bluesky-Post, wird ergänzt")
    args = ap.parse_args(argv)
    heute = build_data.as_date(args.heute) if args.heute else build_data.stichtag()
    build_data.STICHTAG = heute

    if args.faellig:
        dateien = faellige_dateien(args.root, heute, args.zuordnung)
    else:
        dateien = [z.strip() for z in sys.stdin.read().splitlines() if z.strip()]
    posts, hinweise = ankuendigungen(args.root, dateien, heute)
    for h in hinweise:
        print(h)
    if not posts:
        print("Nichts anzukündigen.")
        return 0
    if len(posts) > HOECHSTENS:
        print(f"{len(posts)} neue Einträge auf einmal - vermutlich ein Import. Nichts gepostet.")
        return 0

    handle = os.environ.get("BLUESKY_HANDLE", "").strip().lstrip("@")
    passwort = os.environ.get("BLUESKY_APP_PASSWORD", "")
    if args.probe or not (handle and passwort):
        print("Nur Probe, nichts gepostet." if args.probe else
              "BLUESKY_HANDLE oder BLUESKY_APP_PASSWORD fehlt, nichts gepostet.")
        for t in posts:
            print("---\n" + post_text(t)[0])
        return 0

    import requests
    # Handle -> DID -> Server des Kontos (PDS)
    did = requests.get(f"{OEFFENTLICH}/xrpc/com.atproto.identity.resolveHandle",
                       params={"handle": handle}, timeout=20).json()["did"]
    if did.startswith("did:plc:"):
        doc = requests.get(f"https://plc.directory/{did}", timeout=20).json()
    else:  # did:web
        doc = requests.get(f"https://{did.removeprefix('did:web:')}/.well-known/did.json", timeout=20).json()
    pds = next(s["serviceEndpoint"] for s in doc["service"] if s["id"].endswith("#atproto_pds")).rstrip("/")

    sitzung = requests.post(f"{pds}/xrpc/com.atproto.server.createSession",
                            json={"identifier": handle, "password": passwort}, timeout=20)
    sitzung.raise_for_status()
    kopf = {"Authorization": f"Bearer {sitzung.json()['accessJwt']}"}

    # Letzte eigene Posts: schon angekündigte Links nicht noch einmal posten.
    letzte = requests.get(f"{pds}/xrpc/com.atproto.repo.listRecords", headers=kopf, timeout=20,
                          params={"repo": did, "collection": "app.bsky.feed.post", "limit": 50}).json()
    frueher = {}
    for r in letzte.get("records", []):
        inhalt = json.dumps(r.get("value", {}))
        for t in posts:
            if t["url"] in inhalt:
                frueher.setdefault(t["url"], r["uri"])

    basis = site_url(args.root)
    zuordnung = {}
    for t in posts:
        if t["url"] in frueher:
            print(f"schon gepostet: {t['url']}")
            uri = frueher[t["url"]]
        else:
            text, facetten = post_text(t)
            titel = t["text"].split("\n\n", 1)[0].split(": ", 1)[1]
            karte = {"uri": t["url"], "title": titel, "description": "cogneon.de"}
            bild = bild_fuer(args.root, basis, t["url"])
            if bild and bild.stat().st_size < 950_000:
                blob = requests.post(f"{pds}/xrpc/com.atproto.repo.uploadBlob", data=bild.read_bytes(),
                                     headers={**kopf, "Content-Type": "image/png"}, timeout=30)
                if blob.ok:
                    karte["thumb"] = blob.json()["blob"]
            datensatz = {"$type": "app.bsky.feed.post", "text": text, "facets": facetten, "langs": ["de"],
                         "createdAt": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
                         "embed": {"$type": "app.bsky.embed.external", "external": karte}}
            antwort = requests.post(f"{pds}/xrpc/com.atproto.repo.createRecord", headers=kopf, timeout=30,
                                    json={"repo": did, "collection": "app.bsky.feed.post", "record": datensatz})
            antwort.raise_for_status()
            uri = antwort.json()["uri"]
            print(f"gepostet: {web_adresse(handle, uri)}")
        if t.get("seite"):
            zuordnung[t["seite"]] = web_adresse(did, uri)
    if args.zuordnung and zuordnung:
        bisher = json.loads(args.zuordnung.read_text(encoding="utf-8")) if args.zuordnung.exists() else {}
        args.zuordnung.write_text(json.dumps({**bisher, **zuordnung}, ensure_ascii=False, indent=1,
                                             sort_keys=True) + "\n", encoding="utf-8")
        print(f"Kommentare: {len(zuordnung)} Beitrag/Beiträge mit Bluesky-Post verknüpft")
    return 0


if __name__ == "__main__":
    sys.exit(main())
