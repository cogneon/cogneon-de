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
