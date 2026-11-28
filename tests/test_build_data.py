import json
"""Tests für scripts/build_data.py (Daten der Startseite)."""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import build_data  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def test_termin_kategorie_adresse_festgelegt(tmp_path):
    write(tmp_path / "inhalte/termin-kategorien.yml", "lernOS Convention: loscon\n")
    write(tmp_path / "docs/event/a.md", "---\ntitle: A\nbeginn: 2026-01-10 10:00\n"
          "kategorien: [lernOS Convention]\nkategorie_slugs: [lernoscon]\n---\n")
    (e,) = build_data.all_events(tmp_path)
    assert e["kategorien"] == [("lernOS Convention", "loscon")]




def test_datum_spanne():
    d = lambda *a: dt.datetime(*a)
    assert build_data.datum_spanne(d(2026, 5, 20, 10), d(2026, 5, 20, 16)) == "20.05.2026"
    assert build_data.datum_spanne(d(2026, 5, 20, 10), d(2026, 5, 21, 16)) == "20.-21.05.2026"
    assert build_data.datum_spanne(d(2026, 5, 31, 10), d(2026, 6, 1, 16)) == "31.05.-01.06.2026"
    assert build_data.datum_spanne(d(2026, 12, 30, 10), d(2027, 1, 2, 16)) == "30.12.2026-02.01.2027"


def test_hashtags(tmp_path):
    write(tmp_path / "docs/event/lernos-convention-2027.md", "---\ntitle: L\nbeginn: 2027-06-01 10:00\nhashtag: '#loscon27'\n---\n")
    write(tmp_path / "docs/event/zwei.md", "---\ntitle: Z\nbeginn: 2027-06-02 10:00\nhashtag: loscon27\n---\n")
    write(tmp_path / "docs/akademie.md", "---\ntitle: A\nhashtag: [akademie, Ungültig!]\n---\n")
    write(tmp_path / "docs/blog/posts/2027/x.md", "---\ntitle: X\ndate: {created: 2027-01-05}\nslug: x\nhashtag: kclo27\n---\n")
    write(tmp_path / "migration/redirects.map", "/kclo27 /anderswo/\n")
    regeln, probleme = build_data.build_hashtags(tmp_path)
    assert ("/loscon27", "/event/lernos-convention-2027/") in regeln
    assert not any(a == "/kclo27" for a, _ in regeln)
    assert any("auch in" in p for p in probleme)                 # loscon27 doppelt
    assert any("schon eine Seite" in p for p in probleme)        # /akademie ist Seite
    assert any("a-z" in p for p in probleme)                     # ungültig
    assert any("redirects.map" in p for p in probleme)           # kclo27 manuell anders



def test_abgelaufene_eintraege_fallen_weg(tmp_path):
    write(tmp_path / "inhalte/aktuell.yml", """
highlights:
  - {titel: alt, link: a/, gueltig_bis: 2026-01-01}
  - {titel: neu, link: b/, gueltig_bis: 2026-12-31}
  - {titel: dauerhaft, link: c/}
termine:
  - {titel: vorbei, datum: 01.01.2026, tag: 2026-01-01, url: e/}
  - {titel: kommt, datum: 01.12.2026, tag: 2026-12-01, url: e/}
""")
    result = build_data.build(tmp_path, dt.date(2026, 11, 14))
    assert [h["titel"] for h in result["highlights"]] == ["neu", "dauerhaft"]
    assert "gueltig_bis" not in result["highlights"][0]
    assert [t["titel"] for t in result["termine"]] == ["kommt"]


def test_neueste_beitraege_mit_wordpress_url(tmp_path):
    for day, slug in [("2026-10-05", "a"), ("2026-10-12", "b"), ("2025-01-01", "c")]:
        write(tmp_path / f"docs/blog/posts/{day[:4]}/{slug}.md",
              f"---\ntitle: Titel {slug}\ndate:\n  created: '{day}'\nslug: {slug}\n---\nText\n")
    write(tmp_path / "docs/blog/posts/2026/entwurf.md",
          "---\ntitle: Entwurf\ndate: 2026-11-01\ndraft: true\n---\n")
    result = build_data.build(tmp_path, dt.date(2026, 11, 14), limit=2)
    assert result["blog"] == [
        {"titel": "Titel b", "datum": "12.10.2026", "url": "2026/10/12/b/"},
        {"titel": "Titel a", "datum": "05.10.2026", "url": "2026/10/05/a/"},
    ]


def test_vorschau_nur_ohne_beitraege(tmp_path):
    write(tmp_path / "inhalte/aktuell.yml",
          "blog_vorschau:\n  - {titel: Vorschau, datum: 01.01.2026, url: blog/}\n")
    assert build_data.build(tmp_path, dt.date(2026, 11, 14))["blog"][0]["titel"] == "Vorschau"


def test_blog_uebersicht(tmp_path):
    write(tmp_path / "docs/blog/posts/2026/a.md",
          "---\ntitle: Neu\ndate:\n  created: '2026-10-12'\nslug: a\ncategories:\n- Keep Calm & Learn On\n---\n\n"
          "# Neu\n\nEin **Anriss** mit [Link](https://example.org) und ![Bild](/b.png).\n\n<!-- more -->\n\nRest.\n")
    write(tmp_path / "docs/blog/posts/2025/b.md",
          "---\ntitle: Alt\ndate:\n  created: '2025-01-01'\nslug: b\n---\n\nText\n")
    blog = build_data.build_blog(tmp_path)
    assert blog["neueste"][0] == {
        "titel": "Neu", "datum": "12.10.2026", "url": "2026/10/12/a/",
        "kategorie": "Keep Calm & Learn On", "auszug": "Ein Anriss mit Link und.",
    }
    assert blog["kategorien"] == [{"titel": "Keep Calm & Learn On", "anzahl": 1,
                                   "url": "category/keep-calm--learn-on/"}]
    assert [j["jahr"] for j in blog["archiv"]] == [2026, 2025]


def test_auszug_wird_an_wortgrenze_gekuerzt():
    text = "Wort " * 100
    result = build_data.excerpt(text, length=50)
    assert result.endswith(" …") and len(result) <= 52


def test_termine(tmp_path):
    kopf = "---\ntitle: {t}\ntemplate: termin.html\nbeginn: {b}\nende: {e}\n{x}---\n\nText\n"
    write(tmp_path / "docs/event/alt.md", kopf.format(t="Alt", b="2025-03-01 10:00", e="2025-03-01 12:00",
          x="kategorien: [Ausbildung]\nkategorie_slugs: [edmod]\n"))
    write(tmp_path / "docs/event/neu.md", kopf.format(t="Neu, mit Komma", b="2026-12-01 09:00", e="2026-12-02 17:00",
          x="ort:\n  name: Akademie\n  adresse: Bucherstr. 79a, 90419 Nürnberg\nkategorien: [Ausbildung]\nkategorie_slugs: [edmod]\n"))
    write(tmp_path / "docs/event/tag.md", kopf.format(t="Ganztags", b="2026-11-14 00:00", e="2026-11-14 23:59", x="ganztags: true\nonline: true\n"))
    (tmp_path / "overrides/partials").mkdir(parents=True)
    heute = dt.date(2026, 11, 14)

    info = build_data.build_events(tmp_path, heute)
    assert [e["titel"] for e in info["kommend"]] == ["Ganztags", "Neu, mit Komma"]     # heute zählt noch als kommend
    assert info["kommend"][1]["zeitraum"] == "Di, 01.12.2026, 09:00 Uhr - Mi, 02.12.2026, 17:00 Uhr"
    assert info["kommend"][0]["zeitraum"] == "Sa, 14.11.2026" and info["kommend"][0]["ort"] == "Online"

    ics = (tmp_path / "docs/events/cogneon.ics").read_bytes().decode("utf-8")
    assert "SUMMARY:Neu\\, mit Komma" in ics and "DTSTART:20261201T080000Z" in ics       # 9 Uhr Berlin = 8 Uhr UTC
    assert "DTSTART;VALUE=DATE:20261114" in ics and "DTEND;VALUE=DATE:20261115" in ics
    assert ics.count("BEGIN:VEVENT") == 3 and all(len(l.encode()) <= 75 for l in ics.split("\r\n"))

    kategorie = build_data.frontmatter(tmp_path / "docs/events/kategorie/edmod.md")
    assert [t["titel"] for t in kategorie["kommend"]] == ["Neu, mit Komma"]
    assert [t["titel"] for t in kategorie["vergangen"]] == ["Alt"]
    daten = (tmp_path / "overrides/partials/termine-daten.html").read_text(encoding="utf-8")
    je = json.loads(daten.split("{% set termine = ", 1)[1].rsplit(" %}", 1)[0])["kommend_je_kategorie"]
    assert [t["titel"] for t in je["edmod"]] == ["Neu, mit Komma"] and je["edmod"][0]["url"] == "event/neu/"
    assert build_data.build(tmp_path, heute)["termine"][0] == {"titel": "Ganztags", "datum": "14.11.2026", "url": "event/tag/"}


def test_rss_feed(tmp_path):
    import xml.etree.ElementTree as ET
    write(tmp_path / "docs/blog/posts/2026/a.md",
          "---\ntitle: Wissen & Lernen <neu>\ndate:\n  created: '2026-10-12'\nslug: a\ncategories:\n- News\ntags:\n- lernOS\n---\n\nAnriss & mehr.\n")
    assert build_data.build_feed(tmp_path) == 1
    channel = ET.parse(tmp_path / "docs/feed.xml").getroot().find("channel")
    item = channel.find("item")
    assert item.findtext("title") == "Wissen & Lernen <neu>"
    assert item.findtext("link") == "https://cogneon.de/2026/10/12/a/"
    assert item.findtext("pubDate") == "Mon, 12 Oct 2026 08:00:00 +0200"
    assert [c.text for c in item.findall("category")] == ["News", "lernOS"]


def test_save_the_date_und_schema(tmp_path):
    write(tmp_path / "docs/event/std.md",
          "---\ntitle: Camp 2027\ntemplate: termin.html\nbeginn: 2027-03-11 09:00\nende: 2027-03-12 17:00\n"
          "save_the_date: true\nort:\n  name: Akademie\n  adresse: Bucherstr. 79a, 90419 Nürnberg\n---\n")
    (tmp_path / "overrides/partials").mkdir(parents=True)
    heute = dt.date(2026, 11, 16)
    info = build_data.build_events(tmp_path, heute)
    assert info["kommend"][0]["save_the_date"] is True
    ics = (tmp_path / "docs/events/cogneon.ics").read_bytes().decode("utf-8")
    assert "SUMMARY:Save the Date: Camp 2027" in ics and "STATUS:TENTATIVE" in ics
    schema = build_data.event_jsonld(info["kommend"][0], "https://cogneon.de/")
    assert schema["@type"] == "Event" and schema["startDate"] == "2027-03-11T09:00:00+01:00"
    assert schema["location"] == {"@type": "Place", "name": "Akademie", "address": "Bucherstr. 79a, 90419 Nürnberg"}
    assert build_data.build(tmp_path, heute)["termine"][0]["save_the_date"] is True


ADVENT = """
jahr: 2026
themen:
  - {ab: 1, titel: Wissen sichern}
  - {ab: 6, titel: Wissen teilen}
tuerchen:
  - {tag: 1, typ: Video, titel: Eins, link: "https://a.example/", warum: Weil.}
  - {tag: 2, typ: Buch, titel: Zwei, link: "https://b.example/", warum: Darum.}
  - {tag: 3, titel: Drei, link: "https://c.example/"}
  - {tag: 6, titel: Sechs, link: "https://d.example/", warum: Geheim.}
"""


def test_advent_oeffnet_nur_faellige_und_fertige_tuerchen(tmp_path):
    write(tmp_path / "inhalte/advent.yml", ADVENT)
    a = build_data.build_advent(tmp_path, dt.date(2026, 12, 3))
    assert [i["tag"] for i in a["inhalte"]] == [2, 1]          # neuestes zuerst
    assert a["fehlen"] == [3]                                  # fällig, aber ohne warum
    offen = [t["tag"] for t in a["tueren"] if t["offen"]]
    assert offen == [1, 2]
    assert [t["tag"] for t in a["tueren"] if t["heute"]] == [3]
    assert len(a["tueren"]) == 24
    assert "Geheim" not in str(a)                              # Zukunft bleibt draußen
    assert a["inhalte"][0]["thema"] == "Wissen sichern"


def test_advent_vor_dem_start_alles_zu(tmp_path):
    write(tmp_path / "inhalte/advent.yml", ADVENT)
    a = build_data.build_advent(tmp_path, dt.date(2026, 11, 30))
    assert a["vor_start"] and not a["inhalte"] and not a["fehlen"]


def test_advent_thema_nach_woche(tmp_path):
    write(tmp_path / "inhalte/advent.yml", ADVENT)
    a = build_data.build_advent(tmp_path, dt.date(2026, 12, 6))
    assert a["inhalte"][0]["tag"] == 6 and a["inhalte"][0]["thema"] == "Wissen teilen"


HINWEISE = """
hinweise:
  - {text: Aktion, text_en: Action, link: advent/, art: aktion, ab: 2026-11-30, bis: 2026-12-24}
  - {text: Achtung, art: warnung, ab: 2026-12-10, bis: 2026-12-11}
  - {text: Später, art: hinweis, ab: 2027-01-01}
"""


def test_hinweis_zeitraum_und_vorrang(tmp_path):
    write(tmp_path / "inhalte/hinweise.yml", HINWEISE)
    assert build_data.build_hinweis(tmp_path, dt.date(2026, 11, 29)) == {}
    h = build_data.build_hinweis(tmp_path, dt.date(2026, 12, 1))
    assert h["de"]["text"] == "Aktion" and h["en"]["text"] == "Action" and h["de"]["art"] == "aktion"
    w = build_data.build_hinweis(tmp_path, dt.date(2026, 12, 10))
    assert w["de"]["text"] == "Achtung" and "en" not in w


def test_termin_ohne_kategorie_slugs(tmp_path):
    write(tmp_path / "docs/event/alt.md", "---\ntitle: Alt\nbeginn: 2026-01-10 10:00\n"
          "kategorien: [Expert Debriefing Praxis-Ausbildung]\nkategorie_slugs: [edmod]\n---\n")
    write(tmp_path / "docs/event/neu.md", "---\ntype: termin\ntitle: Neu\n"
          "beginn: '2027-01-15T09:00:00.000Z'\nkategorien: [Expert Debriefing Praxis-Ausbildung, Neue Reihe Ä]\n---\n")
    events = {e["slug"]: e for e in build_data.all_events(tmp_path)}
    assert events["neu"]["kategorien"] == [("Expert Debriefing Praxis-Ausbildung", "edmod"), ("Neue Reihe Ä", "neue-reihe-ae")]
    assert events["neu"]["beginn"] == dt.datetime(2027, 1, 15, 10, 0)


def test_termin_hybrid(tmp_path):
    write(tmp_path / "docs/event/h.md", "---\ntitle: H\nbeginn: 2027-02-01 10:00\nonline: true\n"
          "ort: {name: Cogneon Akademie, adresse: Bucherstr. 79a}\n---\n")
    write(tmp_path / "docs/event/o.md", "---\ntitle: O\nbeginn: 2027-02-02 10:00\nonline: true\n---\n")
    ev = {e["slug"]: e for e in build_data.all_events(tmp_path)}
    assert ev["h"]["hybrid"] and ev["h"]["ort"] == "Cogneon Akademie"
    assert not ev["o"]["hybrid"] and ev["o"]["ort"] == "Online"
    assert build_data.event_jsonld(ev["h"], "https://cogneon.de/")["eventAttendanceMode"].endswith("MixedEventAttendanceMode")


def test_podcast_neueste_und_angepinnte_folgen(tmp_path):
    feed = (Path(__file__).parent / "daten" / "podcast-feed.xml").read_text(encoding="utf-8")
    write(tmp_path / "inhalte/podcast.yml", "anzahl: 2\nangepinnt: [folge-eins, gibt-es-nicht]\n")
    p = build_data.build_podcast(tmp_path, feed)
    assert [f["titel"] for f in p["folgen"]] == ["Folge eins", "Folge drei"]
    assert p["folgen"][0]["angepinnt"] and "angepinnt" not in p["folgen"][1]
    assert p["folgen"][1] == {"titel": "Folge drei", "url": "https://podcasts.cogneon.io/@kclo/episodes/folge-drei",
                              "datum": "11.10.2026", "nummer": "48", "minuten": 46}
    assert p["fehlend"] == ["gibt-es-nicht"]
    assert [(x["name"], x["url"]) for x in p["plattformen"]] == [
        ("Castopod", "https://podcasts.cogneon.io/@kclo"),
        ("Apple Podcasts", "https://podcasts.apple.com/de/podcast/keep-calm-learn-on/id714087020"),
        ("Spotify", "https://open.spotify.com/show/672J7qThg0wQq1P8jb4N1f")]
    assert build_data.podcast_dauer("00:48:58") == 49


def test_mastodon_ankuendigungen(tmp_path):
    import mastodon
    write(tmp_path / "zensical.toml", 'site_url = "https://cogneon.de/"\n')
    write(tmp_path / "docs/blog/posts/2026/neu.md", "---\ntitle: Neu\ndate: 2026-11-20\n---\nText\n")
    write(tmp_path / "docs/blog/posts/2026/alt.md", "---\ntitle: Alt\ndate: 2026-01-01\n---\nText\n")
    write(tmp_path / "docs/blog/posts/2026/entwurf.md", "---\ntitle: E\ndate: 2026-11-20\ndraft: true\n---\n")
    write(tmp_path / "docs/event/treff.md", "---\ntitle: Treff\nbeginn: 2026-12-03 10:00\nende: 2026-12-03 11:00\nonline: true\n---\nText\n")
    toots, hinweise = mastodon.ankuendigungen(tmp_path, [
        "docs/blog/posts/2026/neu.md", "docs/blog/posts/2026/alt.md",
        "docs/blog/posts/2026/entwurf.md", "docs/event/treff.md"], dt.date(2026, 11, 22))
    assert [t["url"] for t in toots] == ["https://cogneon.de/2026/11/20/neu/", "https://cogneon.de/event/treff/"]
    assert toots[0]["text"] == "Neuer Blog-Beitrag auf cogneon.de: Neu\n\nhttps://cogneon.de/2026/11/20/neu/"
    assert toots[1]["text"].startswith("Neuer Termin auf cogneon.de: Treff (")
    assert len(hinweise) == 2


def test_social_seiten_url():
    import build_social
    assert build_social.seiten_url(Path("index.md")) == ""
    assert build_social.seiten_url(Path("en/index.md")) == "en/"
    assert build_social.seiten_url(Path("edmod.md")) == "edmod/"
    assert build_social.seiten_url(Path("en/services.md")) == "en/services/"


def test_kommentare_zuordnung(tmp_path):
    write(tmp_path / "docs/blog/posts/2026/a.md", "---\ntitle: A\ndate: 2026-11-20\n---\nText\n")
    write(tmp_path / "docs/blog/posts/2026/b.md",
          "---\ntitle: B\ndate: 2026-11-21\nmastodon: https://social.cologne/@cogneon/11345\n---\nText\n")
    write(tmp_path / ".daten/mastodon.json",
          '{"2026/11/20/a/": "https://mastodon.social/@cogneon/999", "2026/11/21/b/": "https://x.y/@z/1",'
          ' "2026/11/19/c/": "keine Adresse"}')
    write(tmp_path / "inhalte/kommentare.yml", "ausblenden: [https://a.b/@c/5]\n")
    write(tmp_path / ".daten/bluesky.json", '{"2026/11/20/a/": "https://bsky.app/profile/did:plc:abc/post/3kxyz"}')
    k, probleme = build_data.build_kommentare(tmp_path)
    assert k["beitraege"]["2026/11/20/a/"]["mastodon"] == {"toot": "https://mastodon.social/@cogneon/999",
                                                          "instanz": "https://mastodon.social", "id": "999"}
    assert k["beitraege"]["2026/11/20/a/"]["bluesky"] == {
        "post": "https://bsky.app/profile/did:plc:abc/post/3kxyz", "autor": "did:plc:abc", "rkey": "3kxyz"}
    assert k["beitraege"]["2026/11/21/b/"]["mastodon"]["instanz"] == "https://social.cologne"   # Front Matter gewinnt
    assert "bluesky" not in k["beitraege"]["2026/11/21/b/"]
    assert build_data.bsky_teile("at://cogneon.eurosky.social/app.bsky.feed.post/3abc")["autor"] == "cogneon.eurosky.social"
    assert k["ausblenden"] == ["https://a.b/@c/5"] and len(probleme) == 1
    assert build_data.toot_teile("https://h.de/users/x/statuses/42")["id"] == "42"
    assert build_data.toot_teile("javascript:alert(1)") is None


def test_bluesky_post_text_mit_link_facette():
    import bluesky
    url = "https://cogneon.de/2026/11/30/neue-website/"
    text, facetten = bluesky.post_text({"url": url, "text": f"Neuer Blog-Beitrag auf cogneon.de: Neue Website\n\n{url}"})
    roh = text.encode("utf-8")
    f = facetten[0]["index"]
    assert roh[f["byteStart"]:f["byteEnd"]].decode() == url
    lang = bluesky.post_text({"url": url, "text": "Neuer Termin auf cogneon.de: " + "Ä" * 400 + f"\n\n{url}"})[0]
    assert len(lang) <= bluesky.MAX_ZEICHEN and lang.endswith(url) and "…" in lang


def test_feed_behaelt_wordpress_kennung(tmp_path):
    write(tmp_path / "docs/blog/posts/2026/alt.md", "---\ntitle: Alt\ndate: 2026-11-01\nwp:\n  id: 4711\n---\nText\n")
    write(tmp_path / "docs/blog/posts/2026/neu.md", "---\ntitle: Neu\ndate: 2026-11-02\n---\nText\n")
    build_data.build_feed(tmp_path)
    xml = (tmp_path / "docs/feed.xml").read_text(encoding="utf-8")
    assert '<guid isPermaLink="false">https://cogneon.de/?p=4711</guid>' in xml
    assert '<guid isPermaLink="true">https://cogneon.de/2026/11/02/neu/</guid>' in xml
