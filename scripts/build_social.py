#!/usr/bin/env python3
"""Vorschaubilder (Social Cards) für LinkedIn, Mastodon & Co.

Erzeugt für jede Seite, jeden Blogbeitrag und jeden Termin ein Bild 1200x630
unter docs/assets/social/ und die Zuordnung Seite -> Bild in
overrides/partials/social-daten.html. main.html setzt daraus og:image.
Unveränderte Bilder werden nicht neu gezeichnet (Prüfsumme je Bild).

    python3 scripts/build_social.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import build_data  # noqa: E402

BREITE, HOEHE = 1200, 630
RAND = 80
DUNKEL = (35, 31, 32)
HELL = (255, 255, 255)
GRAU = (190, 186, 187)
ORANGE = (255, 102, 0)
VERSION = "1"  # erhöhen, wenn sich das Layout ändert: zeichnet alle Bilder neu
HIER = Path(__file__).parent / "social"


def schrift(groesse: int, gewicht: int) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(HIER / "inter.ttf"), groesse)
    try:
        font.set_variation_by_axes([gewicht])
    except OSError:
        pass
    return font


def umbrechen(text: str, font, breite: int) -> list[str]:
    zeilen, zeile = [], ""
    for wort in text.split():
        probe = f"{zeile} {wort}".strip()
        if font.getlength(probe) <= breite or not zeile:
            zeile = probe
        else:
            zeilen.append(zeile)
            zeile = wort
    if zeile:
        zeilen.append(zeile)
    return zeilen


def zeichnen(karte: dict, ziel: Path) -> None:
    bild = Image.new("RGB", (BREITE, HOEHE), DUNKEL)
    d = ImageDraw.Draw(bild)
    d.rectangle([0, HOEHE - 16, BREITE, HOEHE], fill=ORANGE)

    logo = Image.open(HIER / "logo-hell.png").convert("RGBA")
    logo = logo.resize((round(logo.width * 56 / logo.height), 56))
    bild.paste(logo, (RAND, RAND - 10), logo)

    y = RAND + 90
    if karte.get("art"):
        f = schrift(30, 700)
        d.text((RAND, y), karte["art"].upper(), font=f, fill=ORANGE)
        y += 56

    # Titel: größte Schrift, bei der er in höchstens vier Zeilen passt.
    platz = HOEHE - y - 150
    for groesse in (72, 64, 56, 50, 44, 40):
        f = schrift(groesse, 700)
        zeilen = umbrechen(karte["titel"], f, BREITE - 2 * RAND)
        hoehe = len(zeilen) * groesse * 1.18
        if len(zeilen) <= 4 and hoehe <= platz:
            break
    if len(zeilen) > 4:
        zeilen = zeilen[:4]
        zeilen[-1] = zeilen[-1].rstrip(".,;:- ") + " …"
    for z in zeilen:
        d.text((RAND, y), z, font=f, fill=HELL)
        y += round(groesse * 1.18)

    f = schrift(30, 400)
    unten = HOEHE - RAND - 30
    if karte.get("zeile"):
        text = karte["zeile"]
        while f.getlength(text) > BREITE - 2 * RAND - 260 and len(text) > 10:
            text = text[:-2].rstrip() + "…"
        d.text((RAND, unten), text, font=f, fill=GRAU)
    w = f.getlength("cogneon.de")
    d.text((BREITE - RAND - w, unten), "cogneon.de", font=f, fill=GRAU)
    ziel.parent.mkdir(parents=True, exist_ok=True)
    bild.save(ziel, "PNG", optimize=True)


def seiten_url(rel: Path) -> str:
    """docs-relativer Markdown-Pfad -> Seitenadresse wie in Zensical."""
    teile = list(rel.with_suffix("").parts)
    if teile[-1] == "index":
        teile = teile[:-1]
    return "/".join(teile) + "/" if teile else ""


def karten(root: Path) -> list[dict]:
    docs = root / "docs"
    liste = []
    for p in build_data.all_posts(docs / "blog" / "posts", auch_zukuenftige=True):
        liste.append({"url": p["url"], "art": "Blog", "titel": p["titel"], "zeile": p["datum"],
                      "text": build_data.excerpt(p["pfad"].read_text(encoding="utf-8"), 200)})
    for e in build_data.all_events(root):
        zeile = " · ".join(x for x in (e["datum"], e["ort"]) if x)
        liste.append({"url": e["url"], "art": "Termin", "titel": e["titel"], "zeile": zeile,
                      "text": f"{zeile}. {e['auszug']}".strip(". ")})
    for pfad in sorted(docs.rglob("*.md")):
        rel = pfad.relative_to(docs)
        if rel.parts[0] in ("blog", "event", "tag", "wp-content") or rel.parts[:2] == ("events", "kategorie"):
            continue
        meta = build_data.frontmatter(pfad)
        titel = str(meta.get("title") or "").strip()
        if not titel or meta.get("draft"):
            continue
        url = seiten_url(rel)
        if url in ("", "en/"):
            titel = "Cogneon - The Knowledge Company"
        untertitel = str(meta.get("untertitel") or "")
        liste.append({"url": url, "art": "", "titel": titel, "zeile": untertitel,
                      "text": str(meta.get("description") or untertitel
                                  or build_data.excerpt(pfad.read_text(encoding="utf-8"), 200))})
    return liste


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args(argv)
    root = args.root
    ausgabe = root / "docs" / "assets" / "social"
    stand_datei = ausgabe / ".stand.json"
    stand = json.loads(stand_datei.read_text()) if stand_datei.exists() else {}

    zuordnung, neu, alle = {}, 0, karten(root)
    for k in alle:
        name = (k["url"].strip("/") or "start").replace("/", "-") + ".png"
        ziel = ausgabe / name
        bildteile = {x: k.get(x) for x in ("art", "titel", "zeile")}
        pruef = hashlib.sha1(json.dumps([VERSION, bildteile], sort_keys=True).encode()).hexdigest()
        if stand.get(name) != pruef or not ziel.exists():
            zeichnen(k, ziel)
            stand[name] = pruef
            neu += 1
        zuordnung[k["url"]] = {"bild": f"assets/social/{name}", "text": k.get("text") or ""}
    # Bilder entfernter Seiten löschen.
    for alt in set(stand) - {Path(v["bild"]).name for v in zuordnung.values()}:
        (ausgabe / alt).unlink(missing_ok=True)
        stand.pop(alt)
    ausgabe.mkdir(parents=True, exist_ok=True)
    stand_datei.write_text(json.dumps(stand, sort_keys=True))
    ziel = root / "overrides" / "partials" / "social-daten.html"
    ziel.write_text(
        "{#- Erzeugt von scripts/build_social.py - nicht von Hand ändern. -#}\n"
        "{% set social = " + json.dumps(zuordnung, ensure_ascii=False) + " %}\n", encoding="utf-8")
    print(f"docs/assets/social/: {len(alle)} Vorschaubilder, davon {neu} neu gezeichnet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
