#!/usr/bin/env python3
"""Erzeugt _data/aktuell.yml (Startseite) und overrides/partials/blog-daten.html (Blog-Übersicht).

Quellen:
  - inhalte/aktuell.yml   Highlights und Termine, von Hand gepflegt
  - docs/blog/posts/      die neuesten Blogbeiträge
  - inhalte/advent.yml    Adventskalender (overrides/partials/advent-daten.html)

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
from zoneinfo import ZoneInfo

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


WOCHENTAGE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def as_datetime(value) -> dt.datetime | None:
    if isinstance(value, dt.datetime):
        return value
    if isinstance(value, dt.date):
        return dt.datetime.combine(value, dt.time())
    if isinstance(value, str):
        try:
            wert = dt.datetime.fromisoformat(value.strip().replace(" ", "T"))
        except ValueError:
            return None
        # Mit Zeitzone (z.B. "2027-01-15T09:00:00.000Z" aus einem Editor):
        # in Berliner Zeit umrechnen und ohne Zone weiterführen wie alle anderen.
        if wert.tzinfo is not None:
            wert = wert.astimezone(ZoneInfo("Europe/Berlin")).replace(tzinfo=None)
        return wert
    return None


def zeitraum(start: dt.datetime, end: dt.datetime, all_day: bool) -> str:
    """Lesbarer Zeitraum: 'Do, 24.09.2020, 11:45 - 15:30 Uhr' oder über mehrere Tage."""
    tag = lambda d: f"{WOCHENTAGE[d.weekday()]}, {d:%d.%m.%Y}"   # noqa: E731
    if start.date() == end.date():
        return tag(start) if all_day else f"{tag(start)}, {start:%H:%M} - {end:%H:%M} Uhr"
    if all_day:
        return f"{tag(start)} - {tag(end)}"
    return f"{tag(start)}, {start:%H:%M} Uhr - {tag(end)}, {end:%H:%M} Uhr"


def termin_slug(name: str) -> str:
    """Adresse einer Terminkategorie (/events/kategorie/<slug>/) für neue Kategorien."""
    s = name.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def kategorie_paare(meta: dict, bekannt: dict[str, str]) -> list[tuple[str, str]]:
    """(Name, Slug) je Kategorie eines Termins. Aus WordPress übernommene Termine
    bringen kategorie_slugs mit; neue Termine (z.B. aus Front Matter CMS) nur
    Namen: dann den Slug eines anderen Termins mit gleichem Namen nehmen, sonst
    einen aus dem Namen bilden."""
    namen = [str(k) for k in meta.get("kategorien") or []]
    slugs = list(meta.get("kategorie_slugs") or [])
    return [(n, str(slugs[i]) if i < len(slugs) and slugs[i] else bekannt.get(n) or termin_slug(n))
            for i, n in enumerate(namen)]


def all_events(root: Path) -> list[dict]:
    """Alle Termine aus docs/event/*.md, nach Beginn sortiert."""
    events = []
    pfade = sorted((root / "docs" / "event").glob("*.md"))
    festgelegt = {}
    quelle = root / "inhalte" / "termin-kategorien.yml"
    if quelle.exists():
        festgelegt = {str(k): str(v) for k, v in (yaml.safe_load(quelle.read_text(encoding="utf-8")) or {}).items()}
    bekannt: dict[str, str] = {}
    for path in pfade:
        m = frontmatter(path)
        for n, sl in zip(m.get("kategorien") or [], m.get("kategorie_slugs") or []):
            bekannt.setdefault(str(n), str(sl))
    for path in pfade:
        meta = frontmatter(path)
        start = as_datetime(meta.get("beginn"))
        if not start or not meta.get("title"):
            continue
        end = as_datetime(meta.get("ende")) or start
        all_day = bool(meta.get("ganztags"))
        ort = meta.get("ort") or {}
        events.append({
            "titel": str(meta["title"]), "slug": path.stem, "url": f"event/{path.stem}/",
            "beginn": start, "ende": end, "ganztags": all_day,
            "datum": f"{start:%d.%m.%Y}", "zeitraum": zeitraum(start, end, all_day),
            "ort": "Online" if meta.get("online") and not ort else str(ort.get("name") or ""),
            "adresse": str(ort.get("adresse") or ""),
            "kategorien": [(n, festgelegt.get(n, sl)) for n, sl in kategorie_paare(meta, bekannt)],
            "anmeldung": str(meta.get("anmeldung") or ""),
            "online": bool(meta.get("online")),
            "bild": str(meta.get("bild") or "") if (root / "docs" / str(meta.get("bild") or "-")).is_file() else "",
            "auszug": excerpt(path.read_text(encoding="utf-8"), 180),
            # Termin steht fest, Beschreibung und Anmeldung folgen noch.
            "save_the_date": bool(meta.get("save_the_date")),
        })
    events.sort(key=lambda e: e["beginn"])
    return events


def ics_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def ics_fold(line: str) -> str:
    """Zeilen nach 75 Bytes umbrechen, wie es das Kalenderformat verlangt."""
    out, current = [], ""
    for char in line:
        if len((current + char).encode("utf-8")) > 74:
            out.append(current)
            current = " "
        current += char
    return "\r\n".join(out + [current])


def build_ics(events: list[dict], site_url: str, stamp: dt.datetime) -> str:
    from zoneinfo import ZoneInfo

    berlin, utc = ZoneInfo("Europe/Berlin"), ZoneInfo("UTC")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Cogneon//cogneon.de//DE",
             "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "X-WR-CALNAME:Cogneon Termine", "X-WR-TIMEZONE:Europe/Berlin"]
    for e in events:
        lines += ["BEGIN:VEVENT", f"UID:{e['slug']}@cogneon.de", f"DTSTAMP:{stamp:%Y%m%dT%H%M%SZ}"]
        if e["ganztags"]:
            lines += [f"DTSTART;VALUE=DATE:{e['beginn']:%Y%m%d}",
                      f"DTEND;VALUE=DATE:{e['ende'].date() + dt.timedelta(days=1):%Y%m%d}"]
        else:
            for key, moment in (("DTSTART", e["beginn"]), ("DTEND", e["ende"])):
                lines.append(f"{key}:{moment.replace(tzinfo=berlin).astimezone(utc):%Y%m%dT%H%M%SZ}")
        if e["save_the_date"]:
            lines.append("STATUS:TENTATIVE")
        lines.append("SUMMARY:" + ics_text(("Save the Date: " if e["save_the_date"] else "") + e["titel"]))
        place = ", ".join(x for x in (e["ort"], e["adresse"]) if x)
        if place:
            lines.append("LOCATION:" + ics_text(place))
        lines += [f"URL:{site_url}{e['url']}", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    return "\r\n".join(ics_fold(l) for l in lines) + "\r\n"


def event_jsonld(e: dict, site_url: str) -> dict:
    """Angaben eines Termins nach schema.org (Event). Suchmaschinen und andere Programme
    lesen sie aus der Terminseite."""
    from zoneinfo import ZoneInfo

    berlin = ZoneInfo("Europe/Berlin")
    moment = lambda d: d.date().isoformat() if e["ganztags"] else d.replace(tzinfo=berlin).isoformat()   # noqa: E731
    data = {"@context": "https://schema.org", "@type": "Event", "name": e["titel"],
            "startDate": moment(e["beginn"]), "endDate": moment(e["ende"]),
            "url": site_url + e["url"], "eventStatus": "https://schema.org/EventScheduled",
            "organizer": {"@type": "Organization", "name": "Cogneon GmbH", "url": site_url}}
    place = {"@type": "Place", "name": e["ort"], **({"address": e["adresse"]} if e["adresse"] else {})}
    virtual = {"@type": "VirtualLocation", "url": site_url + e["url"]}
    if e["online"] and e["ort"] and e["ort"] != "Online":
        data["eventAttendanceMode"] = "https://schema.org/MixedEventAttendanceMode"
        data["location"] = [place, virtual]
    elif e["online"] or e["ort"] == "Online":
        data["eventAttendanceMode"] = "https://schema.org/OnlineEventAttendanceMode"
        data["location"] = virtual
    elif e["ort"]:
        data["eventAttendanceMode"] = "https://schema.org/OfflineEventAttendanceMode"
        data["location"] = place
    if e["anmeldung"]:
        data["offers"] = {"@type": "Offer", "url": e["anmeldung"]}
    return data


def build_events(root: Path, today: dt.date, site_url: str = "https://cogneon.de/") -> dict:
    """Erzeugt alles rund um Termine: Daten für die Übersicht /events/, eine Seite je
    Kategorie unter /events/kategorie/<slug>/ und die Kalenderdatei /events/cogneon.ics."""
    events = all_events(root)
    MONATE = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
    kurz = lambda e: {"titel": e["titel"], "zeitraum": e["zeitraum"], "datum": e["datum"],   # noqa: E731
                      "ort": e["ort"], "url": e["url"], **({"save_the_date": True} if e["save_the_date"] else {})}
    # Kommende Termine zeigen zusätzlich Bild, Anriss und das Datum als Kachel.
    lang = lambda e: {**kurz(e), "bild": e["bild"], "auszug": e["auszug"],   # noqa: E731
                      "tag": f"{e['beginn']:%d}", "monat": f"{MONATE[e['beginn'].month - 1]} {e['beginn']:%Y}"}
    kommend = [e for e in events if e["ende"].date() >= today]
    vergangen = [e for e in reversed(events) if e["ende"].date() < today]
    archiv: list[dict] = []
    for e in vergangen:
        if not archiv or archiv[-1]["jahr"] != e["beginn"].year:
            archiv.append({"jahr": e["beginn"].year, "termine": []})
        archiv[-1]["termine"].append(kurz(e))
    kategorien: dict[str, dict] = {}
    for e in events:
        for name, slug in e["kategorien"]:
            kategorien.setdefault(slug, {"titel": name, "termine": []})["termine"].append(e)

    target = root / "docs" / "events"
    cat_dir = target / "kategorie"
    if cat_dir.exists():
        for old in cat_dir.glob("*.md"):
            old.unlink()
    head = "<!-- Erzeugt von scripts/build_data.py - nicht von Hand ändern. -->\n"
    for slug, cat in kategorien.items():
        cat_dir.mkdir(parents=True, exist_ok=True)
        meta = {"title": cat["titel"], "description": f"Termine: {cat['titel']}", "template": "termine.html",
                "kommend": [{**lang(e), "url": "../../../" + e["url"]} for e in cat["termine"] if e["ende"].date() >= today],
                "vergangen": [{**kurz(e), "url": "../../../" + e["url"]} for e in reversed(cat["termine"]) if e["ende"].date() < today]}
        (cat_dir / f"{slug}.md").write_text(
            "---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=1000) + "---\n" + head,
            encoding="utf-8")
    if events:
        target.mkdir(parents=True, exist_ok=True)
        stamp = dt.datetime.combine(today, dt.time())
        (target / "cogneon.ics").write_text(build_ics(events, site_url, stamp), encoding="utf-8", newline="")
    daten = {"kommend": [lang(e) for e in kommend], "archiv": archiv,
             "zeiten": {e["url"]: e["zeitraum"] for e in events},
             "kategorien_je_termin": {e["url"]: [list(k) for k in e["kategorien"]] for e in events},
             "schema": {e["url"]: event_jsonld(e, site_url) for e in events},
             "kategorien": [{"titel": c["titel"], "url": f"events/kategorie/{s}/", "anzahl": len(c["termine"])}
                            for s, c in sorted(kategorien.items(), key=lambda kv: kv[1]["titel"].lower())]}
    (root / "overrides" / "partials" / "termine-daten.html").write_text(
        "{#- Erzeugt von scripts/build_data.py - nicht von Hand ändern. -#}\n"
        "{% set termine = " + json.dumps(daten, ensure_ascii=False) + " %}\n", encoding="utf-8")
    return {"kommend": kommend, "gesamt": len(events), "kategorien": len(kategorien)}


def build_feed(root: Path, site_url: str = "https://cogneon.de/", limit: int = 20) -> int:
    """RSS-Feed der neuesten Beiträge als docs/feed.xml. Der Server liefert ihn auch
    unter der alten WordPress-Adresse /feed/ aus."""
    from email.utils import format_datetime
    from xml.sax.saxutils import escape
    from zoneinfo import ZoneInfo

    posts = all_posts(root / "docs" / "blog" / "posts")[:limit]
    if not posts:
        return 0
    berlin = ZoneInfo("Europe/Berlin")
    stamp = lambda day: format_datetime(dt.datetime.combine(day, dt.time(8), tzinfo=berlin))   # noqa: E731
    items = []
    for p in posts:
        link = site_url + p["url"]
        cats = "".join(f"\n      <category>{escape(c)}</category>" for c in p["kategorien"] + p["schlagworte"])
        items.append(f"""    <item>
      <title>{escape(p['titel'])}</title>
      <link>{escape(link)}</link>
      <guid isPermaLink="true">{escape(link)}</guid>
      <pubDate>{stamp(p['tag'])}</pubDate>
      <description>{escape(excerpt(p['pfad'].read_text(encoding='utf-8'), 400))}</description>{cats}
    </item>""")
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Cogneon - The Knowledge Company</title>
    <link>{site_url}blog/</link>
    <description>Beiträge von Cogneon zu Wissensmanagement, Wissenstransfer und Lernenden Organisationen.</description>
    <language>de-DE</language>
    <lastBuildDate>{stamp(posts[0]['tag'])}</lastBuildDate>
    <atom:link href="{site_url}feed/" rel="self" type="application/rss+xml"/>
{chr(10).join(items)}
  </channel>
</rss>
"""
    (root / "docs" / "feed.xml").write_text(xml, encoding="utf-8")
    return len(posts)


ADVENT_VORLAUF = 6  # Stunden


def build_advent(root: Path, today: dt.date) -> dict | None:
    """Daten für den Adventskalender /advent/ aus inhalte/advent.yml.

    Ein Türchen ist offen, wenn sein Tag erreicht ist und titel, link und warum
    ausgefüllt sind. Inhalte geschlossener Türchen gelangen nicht in die Seite."""
    source = root / "inhalte" / "advent.yml"
    if not source.exists():
        return None
    data = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
    jahr = int(data.get("jahr") or today.year)
    themen = sorted(data.get("themen") or [], key=lambda t: int(t["ab"]))
    eintraege = {int(t["tag"]): t for t in data.get("tuerchen") or [] if t.get("tag")}

    def thema(tag: int) -> str:
        titel = ""
        for t in themen:
            if tag >= int(t["ab"]):
                titel = t["titel"]
        return titel

    tueren, inhalte, fehlen = [], [], []
    for tag in range(1, 25):
        datum = dt.date(jahr, 12, tag)
        e = eintraege.get(tag) or {}
        fertig = all(str(e.get(f) or "").strip() for f in ("titel", "link", "warum"))
        faellig = datum <= today
        offen = faellig and fertig
        if faellig and not fertig:
            fehlen.append(tag)
        tueren.append({"tag": tag, "offen": offen, "heute": datum == today})
        if offen:
            inhalte.append({"tag": tag, "datum": f"{tag}. Dezember", "thema": thema(tag),
                            **{f: str(e.get(f) or "").strip() for f in
                               ("typ", "titel", "link", "von", "warum", "impuls")}})
    inhalte.reverse()   # neuestes Türchen zuerst
    return {"jahr": jahr, "tueren": tueren, "inhalte": inhalte, "fehlen": fehlen,
            "vor_start": today < dt.date(jahr, 12, 1),
            "nach_ende": today > dt.date(jahr, 12, 24)}


def md_url(rel: str) -> str:
    """Pfad einer Markdown-Datei relativ zu docs/ -> URL wie im Build (ohne führenden /)."""
    rel = rel.replace("\\", "/")
    if rel.endswith("index.md"):
        return rel[: -len("index.md")]
    return rel[: -len(".md")] + "/"


def quell_hash(path: Path) -> str:
    """Kurzer Prüfwert einer Quelldatei, um veraltete Übersetzungen zu erkennen."""
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def build_sprachen(root: Path) -> dict:
    """Zuordnung deutscher und englischer Seiten aus docs/en/**.md.

    Jede englische Seite nennt im Front Matter ihre Vorlage (quelle: kontakt.md)
    und deren Prüfwert beim Übersetzen (quelle_hash). Weicht der Prüfwert ab,
    hat sich die deutsche Seite seither geändert."""
    docs = root / "docs"
    de_zu_en, en_zu_de, veraltet, fehlt = {}, {}, [], []
    for en in sorted((docs / "en").rglob("*.md")) if (docs / "en").exists() else []:
        meta = frontmatter(en)
        quelle = meta.get("quelle")
        if not quelle:
            continue
        de = docs / quelle
        en_url = md_url(str(en.relative_to(docs)))
        if not de.exists():
            fehlt.append(f"{en.relative_to(docs)} -> {quelle}")
            continue
        de_url = md_url(quelle)
        de_zu_en[de_url] = en_url
        en_zu_de[en_url] = de_url
        if not meta.get("frozen") and str(meta.get("quelle_hash") or "") != quell_hash(de):
            veraltet.append(f"{en.relative_to(docs)} (Vorlage {quelle} geändert)")
    return {"de_zu_en": de_zu_en, "en_zu_de": en_zu_de, "veraltet": veraltet, "fehlt": fehlt}


HINWEIS_ARTEN = ("warnung", "hinweis", "aktion")


def build_hinweis(root: Path, today: dt.date) -> dict:
    """Die heute gültige Meldung für die Hinweisleiste je Sprache (oder keine)."""
    source = root / "inhalte" / "hinweise.yml"
    if not source.exists():
        return {}
    data = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
    gueltig = []
    for i, h in enumerate(data.get("hinweise") or []):
        ab, bis = as_date(h.get("ab")), as_date(h.get("bis"))
        if (ab and today < ab) or (bis and today > bis) or not str(h.get("text") or "").strip():
            continue
        art = h.get("art") if h.get("art") in HINWEIS_ARTEN else "hinweis"
        gueltig.append((0 if art == "warnung" else 1, i, art, h))
    if not gueltig:
        return {}
    _, _, art, h = sorted(gueltig)[0]
    ergebnis = {"de": {"text": str(h["text"]).strip(), "link": h.get("link") or "", "art": art}}
    if str(h.get("text_en") or "").strip():
        ergebnis["en"] = {"text": str(h["text_en"]).strip(), "link": h.get("link_en") or h.get("link") or "", "art": art}
    return ergebnis


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

    # Termine kommen aus docs/event/. Einträge in inhalte/aktuell.yml kommen dazu
    # (zum Beispiel fremde Veranstaltungen ohne eigene Seite).
    termine = [{"titel": e["titel"], "datum": e["datum"], "url": e["url"],
                **({"save_the_date": True} if e["save_the_date"] else {})}
               for e in all_events(root) if e["ende"].date() >= today][:5]
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
    today = as_date(args.heute) if args.heute else dt.datetime.now(ZoneInfo("Europe/Berlin")).date()
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
    info = build_events(args.root, today)
    print(f"docs/events/: {info['gesamt']} Termine, davon {len(info['kommend'])} kommend, {info['kategorien']} Kategorien")
    print(f"docs/feed.xml: {build_feed(args.root)} Beiträge")
    karte = args.root / "inhalte" / "karte.yml"
    if karte.exists():
        orte = yaml.safe_load(karte.read_text(encoding="utf-8")) or {}
        ziel = args.root / "docs" / "assets" / "karte" / "orte.json"
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_text(json.dumps(orte, ensure_ascii=False), encoding="utf-8")
        print(f"docs/assets/karte/orte.json: {len(orte.get('orte') or [])} Orte")
    # Der Adventskalender öffnet das nächste Türchen schon am Vorabend: Ab
    # ADVENT_VORLAUF Stunden vor Mitternacht (Berliner Zeit) gilt der Folgetag.
    # So reicht der abendliche Lauf, auch wenn GitHub ihn stundenlang verzögert.
    advent_tag = as_date(args.heute) if args.heute else (
        dt.datetime.now(ZoneInfo("Europe/Berlin")) + dt.timedelta(hours=ADVENT_VORLAUF)).date()
    advent = build_advent(args.root, advent_tag)
    if advent is not None:
        target = args.root / "overrides" / "partials" / "advent-daten.html"
        target.write_text(
            "{#- Erzeugt von scripts/build_data.py - nicht von Hand ändern. -#}\n"
            "{% set advent = " + json.dumps(advent, ensure_ascii=False) + " %}\n",
            encoding="utf-8",
        )
        print(f"{target.relative_to(args.root)}: {len(advent['inhalte'])} Türchen offen")
        if advent["fehlen"]:
            print(f"Warnung: Adventskalender-Türchen ohne titel/link/warum bleiben zu: "
                  f"{', '.join(map(str, advent['fehlen']))}", file=sys.stderr)
    hinweis = build_hinweis(args.root, today)
    target = args.root / "overrides" / "partials" / "hinweis-daten.html"
    target.write_text(
        "{#- Erzeugt von scripts/build_data.py - nicht von Hand ändern. -#}\n"
        "{% set hinweis = " + json.dumps(hinweis, ensure_ascii=False) + " %}\n",
        encoding="utf-8",
    )
    print(f"{target.relative_to(args.root)}: {'Meldung aktiv' if hinweis else 'keine Meldung'}")
    sprachen = build_sprachen(args.root)
    target = args.root / "overrides" / "partials" / "sprachen-daten.html"
    target.write_text(
        "{#- Erzeugt von scripts/build_data.py - nicht von Hand ändern. -#}\n"
        "{% set sprachen = " + json.dumps({k: sprachen[k] for k in ("de_zu_en", "en_zu_de")},
                                         ensure_ascii=False) + " %}\n",
        encoding="utf-8",
    )
    print(f"{target.relative_to(args.root)}: {len(sprachen['de_zu_en'])} englische Seiten")
    for zeile in sprachen["veraltet"]:
        print(f"Warnung: Übersetzung veraltet: {zeile}", file=sys.stderr)
    for zeile in sprachen["fehlt"]:
        print(f"Warnung: Vorlage fehlt: {zeile}", file=sys.stderr)
    anzahl = build_tags(args.root)
    print(f"docs/tag/: {anzahl} Schlagwort-Seiten")
    return 0


if __name__ == "__main__":
    sys.exit(main())
