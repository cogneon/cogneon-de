"""Tests für scripts/build_htaccess.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import build_htaccess  # noqa: E402


def test_regeln(tmp_path):
    site, migration = tmp_path / "site", tmp_path / "migration"
    (site / "da").mkdir(parents=True)
    (site / "da/index.html").write_text("x")
    migration.mkdir()
    (migration / "redirects-kategorien.map").write_text(
        "# Kommentar\n/category/ki /category/künstliche-intelligenz/\n/ed /falsch/\n/da /woanders/\n", encoding="utf-8")
    (migration / "redirects.map").write_text(
        "/ed /expert-debriefing/\n/tag/f%c3%bchrung /tag/fuehrung/\n/feed/podcast https://podcasts.cogneon.io/@kclo/feed.xml\n",
        encoding="utf-8")
    assert build_htaccess.main(["--site", str(site), "--migration", str(migration)]) == 0
    text = (site / ".htaccess").read_text(encoding="utf-8")
    assert 'RewriteRule "^ed/?$" "/expert-debriefing/" [R=301,L,NE]' in text        # redirects.map gewinnt
    assert "/falsch/" not in text
    assert 'RewriteRule "^category/ki/?$" "/category/k\\%C3\\%BCnstliche-intelligenz/"' in text
    assert 'RewriteRule "^tag/führung/?$" "/tag/fuehrung/"' in text                 # Apache vergleicht entschlüsselt
    assert '"https://podcasts.cogneon.io/@kclo/feed.xml"' in text
    assert "woanders" not in text                                                   # echte Seite hat Vorrang
    assert text.index("RewriteRule ^feed/?$ /feed.xml") < text.index('"^feed/podcast/?$"')
