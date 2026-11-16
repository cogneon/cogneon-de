"""Tests für scripts/build_data.py (Daten der Startseite)."""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import build_data  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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
    assert build_data.build(tmp_path, heute)["termine"][0] == {"titel": "Ganztags", "datum": "14.11.2026", "url": "event/tag/"}
