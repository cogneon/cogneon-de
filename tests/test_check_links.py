"""Tests für scripts/check_links.py (Linkprüfung der gebauten Website)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import check_links  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_interne_links_medien_und_weiterleitungen(tmp_path):
    site, migration = tmp_path / "site", tmp_path / "migration"
    write(site / "index.html", """
        <a href="da/">ok</a> <a href="/weg/">defekt</a> <a href="https://cogneon.de/alt">Weiterleitung</a>
        <a href="https://example.org/x#teil">extern</a> <a href="mailto:a@b.de">Mail</a> <a href="#oben">Anker</a>
        <img src="/wp-content/uploads/fehlt.png"> <img src="bild.png">""")
    write(site / "da/index.html", "<a href='../'>zurück</a>")
    write(site / "bild.png", "")
    write(migration / "redirects.map", "/alt /da/\n")

    internal, external = check_links.collect(site)
    pages, media = check_links.check_internal(site, internal, check_links.load_redirects(migration))
    assert list(pages) == ["/weg/"] and pages["/weg/"] == {"/"}
    assert list(media) == ["/wp-content/uploads/fehlt.png"]
    assert list(external) == ["https://example.org/x"]


def test_rueckgabe_und_bericht(tmp_path):
    site, migration = tmp_path / "site", tmp_path / "migration"
    write(site / "index.html", '<a href="/weg/">defekt</a>')
    migration.mkdir()
    args = ["--site", str(site), "--migration", str(migration)]
    assert check_links.main(args) == 1
    assert check_links.main(args + ["--report-only"]) == 0
    assert "`/weg/`" in (migration / "link-check.md").read_text(encoding="utf-8")
