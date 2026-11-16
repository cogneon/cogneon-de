"""Tests fuer den WordPress-Export. Laufen offline gegen einen nachgebauten API-Server."""

from __future__ import annotations

import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import check_urls  # noqa: E402
import wp_export  # noqa: E402

POST_HTML = """
<div class="wp-block-uagb-container uagb-block-1a2b">
<p>Erster Absatz mit <a href="{base}/angebote/">internem Link</a> und
<a href="https://example.org/extern">externem Link</a>.</p>
<h2 class="wp-block-heading">Zwischenüberschrift</h2>
<figure class="wp-block-image size-large"><img src="{base}/wp-content/uploads/2026/01/bild-1024x576.png"
 srcset="{base}/wp-content/uploads/2026/01/bild-300x169.png 300w" alt="Ein Bild" width="1024" height="576"/>
<figcaption>Bildunterschrift</figcaption></figure>
<ul><li>Punkt eins</li><li>Punkt zwei</li></ul>
<figure class="wp-block-embed"><iframe src="https://www.youtube.com/embed/abc123"></iframe></figure>
<p>[charta_unterschriften]</p>
<p>Download: <a href="{base}/wp-content/uploads/2026/01/handout.pdf">Handout</a></p>
<p>Vertreten durch:<br>Erika Muster<br />Registereintrag: HRB 1</p>
<div class="wp-block-uagb-info-box uagb-block-9f8e"><a class="uagb-infobox-link-wrap" href="https://partner.example/"></a>
<h3 class="uagb-ifb-title">Partner Eins</h3></div>
<script>alert("weg")</script>
</div>
"""


def make_site(base: str) -> dict:
    html = POST_HTML.format(base=base)
    return {
        "": {"name": "Testsite", "description": "", "url": base, "timezone_string": "Europe/Berlin",
             "namespaces": ["wp/v2", "tribe/events/v1"]},
        "wp/v2/types": {
            "post": {"name": "Beiträge", "rest_base": "posts", "rest_namespace": "wp/v2"},
            "page": {"name": "Seiten", "rest_base": "pages", "rest_namespace": "wp/v2"},
            "attachment": {"name": "Medien", "rest_base": "media", "rest_namespace": "wp/v2"},
        },
        "wp/v2/posts": [
            {"id": 11, "date": "2026-01-15T10:00:00", "modified": "2026-02-01T09:00:00",
             "slug": "erster-beitrag", "link": f"{base}/2026/01/15/erster-beitrag/",
             "title": {"rendered": "Erster Beitrag &#8211; Test"}, "content": {"rendered": html},
             "excerpt": {"rendered": ""}, "author": 1, "categories": [5], "tags": [7],
             "featured_media": 90, "sticky": False},
            {"id": 12, "date": "2025-11-03T08:00:00", "modified": "2025-11-03T08:00:00",
             "slug": "zweiter-beitrag", "link": f"{base}/2025/11/03/zweiter-beitrag/",
             "title": {"rendered": "Zweiter Beitrag"}, "content": {"rendered": "<p>Kurz.</p>"},
             "excerpt": {"rendered": ""}, "author": 1, "categories": [5], "tags": [],
             "featured_media": 0, "sticky": True},
        ],
        "wp/v2/pages": [
            {"id": 21, "date": "2024-01-01T00:00:00", "modified": "2026-01-01T00:00:00",
             "slug": "angebote", "link": f"{base}/angebote/", "title": {"rendered": "Angebote"},
             "content": {"rendered": "<p>Unsere Angebote.</p>"}, "parent": 0, "menu_order": 0,
             "template": ""},
            {"id": 22, "date": "2024-01-01T00:00:00", "modified": "2026-01-01T00:00:00",
             "slug": "wissenstransfer", "link": f"{base}/angebote/wissenstransfer/",
             "title": {"rendered": "Wissenstransfer"}, "content": {"rendered": "<p>Unterseite.</p>"},
             "parent": 21, "menu_order": 0, "template": ""},
            {"id": 23, "date": "2024-01-01T00:00:00", "modified": "2026-01-01T00:00:00",
             "slug": "startseite", "link": f"{base}/", "title": {"rendered": "Startseite"},
             "content": {"rendered": "<p>Alte Startseite.</p>"}, "parent": 0, "menu_order": 0,
             "template": ""},
        ],
        "wp/v2/categories": [{"id": 5, "name": "Künstliche Intelligenz &amp; Lernen", "slug": "ki",
                              "description": "", "link": f"{base}/category/ki/", "count": 2}],
        "wp/v2/tags": [{"id": 7, "name": "lernOS", "slug": "lernos", "description": "",
                        "link": f"{base}/tag/lernos/", "count": 1}],
        "wp/v2/users": [{"id": 1, "name": "Erika Muster", "slug": "erika.muster",
                         "description": "<p>Beraterin</p>", "link": f"{base}/author/erika.muster/"}],
        "wp/v2/media": [{"id": 90, "source_url": f"{base}/wp-content/uploads/2026/01/titel.jpg"}],
        "wp/v2/comments": [],
        "tribe/events/v1/events": {"total": 3, "events": []},
    }


@pytest.fixture()
def server():
    state = {}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # still
            pass

        def do_GET(self):
            parts = urlparse(self.path)
            if parts.path.startswith("/wp-content/"):
                body = b"BINARY-" + parts.path.encode()
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            route = parts.path.removeprefix("/wp-json/").strip("/")
            data = state["site"].get(route)
            if data is None:
                self.send_response(404)
                self.end_headers()
                return
            headers = {}
            if isinstance(data, list):
                query = parse_qs(parts.query)
                if "include" in query:
                    wanted = {int(i) for i in query["include"][0].split(",")}
                    data = [d for d in data if d["id"] in wanted]
                per_page = int(query.get("per_page", ["10"])[0])
                page = int(query.get("page", ["1"])[0])
                total = len(data)
                headers = {"X-WP-Total": str(total),
                           "X-WP-TotalPages": str(max(1, -(-total // per_page)))}
                data = data[(page - 1) * per_page: page * per_page]
            body = json.dumps(data).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            for key, value in headers.items():
                self.send_header(key, value)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    base = f"http://127.0.0.1:{httpd.server_port}"
    state["site"] = make_site(base)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield base
    httpd.shutdown()


def run_export(base: str, root: Path, *extra: str) -> int:
    return wp_export.main(["--base-url", base, "--root", str(root), "--delay", "0", *extra])


def test_convert_html_rewrites_links_and_media():
    base = "https://cogneon.de"
    conv = wp_export.convert_html(POST_HTML.format(base=base), base)
    md = conv.markdown
    assert "[internem Link](/angebote/)" in md
    assert "[externem Link](https://example.org/extern)" in md
    assert "## Zwischenüberschrift" in md
    assert "![Ein Bild](/wp-content/uploads/2026/01/bild-1024x576.png)" in md
    assert "*Bildunterschrift*" in md
    assert "- Punkt eins" in md
    assert "alert" not in md and "srcset" not in md
    assert conv.embeds == ["https://www.youtube.com/embed/abc123"]
    assert "[Eingebetteter Inhalt: youtube.com](https://www.youtube.com/embed/abc123){ .embed }" in md
    assert conv.shortcodes == ["charta_unterschriften"]
    assert "Vertreten durch:<br>\nErika Muster<br>\nRegistereintrag: HRB 1" in md
    assert "\\" not in md
    assert conv.relinked == ["https://partner.example/"]
    assert "### [Partner Eins](https://partner.example/)" in md
    assert "wp-block-uagb-info-box" in conv.blocks and "wp-block-uagb-container" in conv.blocks
    assert conv.images_without_alt == 0
    assert f"{base}/wp-content/uploads/2026/01/handout.pdf" in conv.media


def test_permalink_pattern():
    assert wp_export.permalink_pattern("https://x.de/2026/01/hallo/", "hallo", "2026-01-15T10:00:00") \
        == "/{yyyy}/{mm}/{slug}/"
    assert wp_export.permalink_pattern("https://x.de/hallo/", "hallo", "2026-01-15T10:00:00") == "/{slug}/"


def test_full_export_is_repeatable_and_respects_frozen(server, tmp_path):
    home = tmp_path / "docs" / "index.md"
    home.parent.mkdir(parents=True)
    home.write_text("---\ntitle: Start\nfrozen: true\n---\n\n# Handgebaut\n", encoding="utf-8")

    assert run_export(server, tmp_path) == 0

    post = tmp_path / "docs/blog/posts/2026/erster-beitrag.md"
    meta = wp_export.read_frontmatter(post)
    assert meta["title"] == "Erster Beitrag – Test"
    assert meta["slug"] == "erster-beitrag"
    assert meta["authors"] == ["erika.muster"]
    assert meta["categories"] == ["Künstliche Intelligenz & Lernen"]
    assert meta["tags"] == ["lernOS"]
    assert str(meta["date"]["created"]) == "2026-01-15"
    assert "<!-- more -->" in post.read_text(encoding="utf-8")
    assert wp_export.read_frontmatter(tmp_path / "docs/blog/posts/2025/zweiter-beitrag.md")["pin"] is True

    assert (tmp_path / "docs/angebote/index.md").exists()
    assert (tmp_path / "docs/angebote/wissenstransfer.md").exists()
    assert "Handgebaut" in home.read_text(encoding="utf-8"), "frozen-Seite wurde überschrieben"

    for name in ("bild-1024x576.png", "handout.pdf", "titel.jpg"):
        assert (tmp_path / "docs/wp-content/uploads/2026/01" / name).exists(), name

    authors = yaml.safe_load((tmp_path / "docs/.authors.yml").read_text(encoding="utf-8"))
    assert authors["authors"]["erika.muster"]["description"] == "Beraterin"

    report = (tmp_path / "migration/report.md").read_text(encoding="utf-8")
    assert "`/{yyyy}/{mm}/{dd}/{slug}/`: 2" in report
    assert "[charta_unterschriften]" in report
    assert "www.youtube.com: 1" in report
    assert "Veranstaltungen: 3" in report
    url_map = (tmp_path / "migration/url-map.csv").read_text(encoding="utf-8")
    assert "/2026/01/15/erster-beitrag/,post,11" in url_map
    assert ",frozen" in url_map

    assert "| `wp-block-uagb-info-box` | 1 |" in report
    assert "## Verlinkte Kacheln" in report and "https://partner.example/" in report
    tags = (tmp_path / "migration/tags.csv").read_text(encoding="utf-8")
    assert "lernos,lernOS,1,/tag/lernos/" in tags
    assert "ki,Künstliche Intelligenz & Lernen,2,/category/ki/" in (tmp_path / "migration/categories.csv").read_text(encoding="utf-8")

    # Zweiter Lauf: nichts aendert sich, nichts wird erneut geladen.
    before = post.read_text(encoding="utf-8")
    assert run_export(server, tmp_path) == 0
    assert post.read_text(encoding="utf-8") == before
    report = (tmp_path / "migration/report.md").read_text(encoding="utf-8")
    assert "post_unchanged: 2" in report and "media_present: 3" in report


def test_inventory_only_writes_no_content(server, tmp_path):
    assert run_export(server, tmp_path, "--inventory-only") == 0
    inv = json.loads((tmp_path / "migration/inventory.json").read_text(encoding="utf-8"))
    assert inv["types"]["post"]["count"] == 2 and inv["types"]["page"]["count"] == 3
    assert "attachment" not in inv["types"]
    assert not (tmp_path / "docs").exists()


def test_check_urls(tmp_path):
    site = tmp_path / "site"
    (site / "angebote").mkdir(parents=True)
    (site / "index.html").write_text("x")
    (site / "angebote/index.html").write_text("x")
    urls = tmp_path / "old.txt"
    urls.write_text("https://cogneon.de/\nhttps://cogneon.de/angebote/\n"
                    "https://cogneon.de/feed/podcast/\nhttps://cogneon.de/weg/\n")
    redirects = tmp_path / "redirects.map"
    redirects.write_text("# alt neu\n/feed/podcast https://podcasts.cogneon.io/@kclo/feed.xml\n")
    args = ["--site", str(site), "--url-list", str(urls), "--redirects", str(redirects),
            "--report", str(tmp_path / "check.md")]
    assert check_urls.main(args) == 1
    report = (tmp_path / "check.md").read_text()
    assert "fehlend: 1" in report and "`/weg/`" in report and "per Redirect abgedeckt: 1" in report
    assert check_urls.main([*args, "--report-only"]) == 0


def test_blocked_endpoints_do_not_abort_export(server, tmp_path, monkeypatch):
    """Sicherheits-Plugins sperren oft die Typ- und Benutzerliste."""
    original = wp_export.WordPress.get

    def blocked(self, route, params=None):
        if route.strip("/") in ("wp/v2/types", "wp/v2/users"):
            class Resp:
                status_code = 401
                headers = {}

                @staticmethod
                def json():
                    return {"code": "rest_forbidden", "message": "nein", "data": {"status": 401}}
            return Resp()
        return original(self, route, params)

    monkeypatch.setattr(wp_export.WordPress, "get", blocked)
    assert run_export(server, tmp_path) == 0
    meta = wp_export.read_frontmatter(tmp_path / "docs/blog/posts/2026/erster-beitrag.md")
    assert "authors" not in meta
    report = (tmp_path / "migration/report.md").read_text(encoding="utf-8")
    assert "rest_forbidden" in report and "Benutzerliste nicht abrufbar" in report
    assert "ID 1: 2 Beiträge" in report

    # Mit Zuordnungsdatei bekommen die Beitraege ihren Autor.
    (tmp_path / "migration/autoren.yml").write_text("1: erika.muster\n", encoding="utf-8")
    assert run_export(server, tmp_path) == 0
    meta = wp_export.read_frontmatter(tmp_path / "docs/blog/posts/2026/erster-beitrag.md")
    assert meta["authors"] == ["erika.muster"]
    authors = yaml.safe_load((tmp_path / "docs/.authors.yml").read_text(encoding="utf-8"))
    assert "erika.muster" in authors["authors"]


def test_locked_api_gives_clear_message(server, tmp_path, monkeypatch, capsys):
    """cogneon.de liefert wp/v2 nur an angemeldete Benutzer aus."""
    original = wp_export.WordPress.get

    def locked(self, route, params=None):
        if route.strip("/").startswith("wp/v2/"):
            class Resp:
                status_code = 401
                headers = {}

                @staticmethod
                def json():
                    return {"code": "rest_not_logged_in", "message": "nein", "data": {"status": 401}}
            return Resp()
        return original(self, route, params)

    monkeypatch.setattr(wp_export.WordPress, "get", locked)
    monkeypatch.delenv("WP_USER", raising=False)
    monkeypatch.delenv("WP_APP_PASSWORD", raising=False)
    assert run_export(server, tmp_path) == 2
    assert "WP_APP_PASSWORD" in capsys.readouterr().out
    assert "verlangt eine Anmeldung" in (tmp_path / "migration/report.md").read_text(encoding="utf-8")
    assert not (tmp_path / "docs").exists()


def test_credentials_come_from_environment_only(monkeypatch):
    monkeypatch.setenv("WP_USER", "export")
    monkeypatch.setenv("WP_APP_PASSWORD", "test-wert")
    wp = wp_export.WordPress("https://cogneon.de")
    assert wp.authenticated and wp.session.auth == ("export", "test-wert")


def test_frozen_page_changed_in_wordpress_is_reported(server, tmp_path):
    page = tmp_path / "docs/angebote/index.md"
    page.parent.mkdir(parents=True)
    page.write_text("---\ntitle: Angebote\nfrozen: true\nwp:\n  id: 21\n  modified: '2025-06-01'\n---\n\n# Neu gebaut\n",
                    encoding="utf-8")
    assert run_export(server, tmp_path, "--raw") == 0
    assert "Neu gebaut" in page.read_text(encoding="utf-8")
    report = (tmp_path / "migration/report.md").read_text(encoding="utf-8")
    assert "in WordPress geändert am 2026-01-01, im Repo Stand 2025-06-01" in report
    assert (tmp_path / "migration/raw/angebote.html").exists()


def test_spectra_icon_list_link_moves_to_label():
    html = ('<div class="uagb-icon-list__wrap"><div class="wp-block-uagb-icon-list-child">'
            '<a aria-label="GfWM" href="https://gfwm.de"> </a>'
            '<span class="uagb-icon-list__source-wrap"><svg><path d="M0 0"/></svg></span>'
            '<span class="uagb-icon-list__label">Gesellschaft für Wissensmanagement e.V.</span></div></div>')
    md = wp_export.convert_html(html, "https://cogneon.de").markdown
    assert md.strip() == "- [Gesellschaft für Wissensmanagement e.V.](https://gfwm.de)"


def test_title_is_not_repeated():
    assert wp_export.with_title("Über uns", "## Über uns\n\nText\n") == "# Über uns\n\nText\n"
    assert wp_export.with_title("Über uns", "Text\n") == "# Über uns\n\nText\n"


EMBED_PRIVACY = """<figure class="wp-block-embed wp-block-embed-youtube"><div class="wp-block-embed__wrapper">
<div class="embed-privacy-container is-disabled embed-youtube" data-embed-provider="youtube">
<button type="button" class="embed-privacy-enable screen-reader-text">Video anzeigen</button>
<div class="embed-privacy-overlay"><div class="embed-privacy-inner"><p>Hier klicken, um den Inhalt von YouTube anzuzeigen.
<noscript>Bitte aktiviere JavaScript.</noscript></p></div>
<div class="embed-privacy-footer"><span class="embed-privacy-url"><a href="https://www.youtube.com/watch?v=ddO9idmax0o">„Twitter in Plain English“ direkt öffnen</a></span></div></div>
<div class="embed-privacy-content"><script>var _oembed_1 = '{\\"embed\\":\\"&lt;iframe title=&quot;Twitter in Plain English&quot; src=&quot;https:\\\\/\\\\/www.youtube-nocookie.com\\\\/embed\\\\/ddO9idmax0o?feature=oembed&quot;&gt;&lt;\\\\/iframe&gt;\\"}';</script></div>
</div></div></figure>"""


def test_embed_privacy_placeholder_becomes_embed_link():
    conv = wp_export.convert_html(EMBED_PRIVACY, "https://cogneon.de")
    assert conv.markdown.strip() == "[YouTube: Twitter in Plain English](https://www.youtube.com/watch?v=ddO9idmax0o){ .embed }"
    assert conv.embeds == ["https://www.youtube.com/watch?v=ddO9idmax0o"] and not conv.lost_embeds


def test_embed_privacy_without_direct_link_uses_script():
    html = ('<div class="embed-privacy-container" data-embed-provider="vimeo"><div class="embed-privacy-content">'
            "<script>var _oembed_2 = '{\\\"embed\\\":\\\"&lt;iframe title=&quot;Film&quot; "
            "src=&quot;https:\\\\/\\\\/player.vimeo.com\\\\/video\\\\/123456&quot;&gt;&lt;\\\\/iframe&gt;\\\"}';</script></div></div>")
    conv = wp_export.convert_html(html, "https://cogneon.de")
    assert conv.markdown.strip() == "[Vimeo: Film](https://player.vimeo.com/video/123456){ .embed }"


def test_legacy_shortcodes():
    html = ("<p>[av_video src=&#8217;https://www.youtube.com/watch?v=d7f_GZsQMpA&#8216; format=&#8217;16-9&#8242; av_uid=&#8217;av-1&#8242;]</p>"
            "<p>[av_button label=&#8217;Zum Jam anmelden&#8216; link=&#8217;manually,https://example.org/tickets&#8242; size=&#8217;small&#8216;]</p>"
            "<p>[bctt tweet=&#8220;HR wird Teil eines Netzwerks. <a href=\"https://cogneon.de/tag/hr/\">#hr</a>&#8243; username=&#8220;cogneon&#8220;]</p>"
            "<p>[vimeo 108251676 w=500 h=281]</p>"
            "<p>[pdf-embedder url=&#8220;https://cogneon.de/wp-content/uploads/2018/04/folien.pdf&#8220; width=&#8220;500&#8243;]</p>")
    conv = wp_export.convert_html(html, "https://cogneon.de")
    md = conv.markdown
    assert "[Eingebetteter Inhalt: youtube.com](https://www.youtube.com/watch?v=d7f_GZsQMpA){ .embed }" in md
    assert "[Zum Jam anmelden](https://example.org/tickets)" in md
    assert "> HR wird Teil eines Netzwerks. [#hr](/tag/hr/)" in md
    assert "[Eingebetteter Inhalt: Vimeo](https://vimeo.com/108251676){ .embed }" in md
    assert "[PDF: folien.pdf](/wp-content/uploads/2018/04/folien.pdf)" in md
    assert conv.shortcodes == []
    assert "https://cogneon.de/wp-content/uploads/2018/04/folien.pdf" in conv.media


def test_headings_shift_down_when_content_has_h1():
    conv = wp_export.convert_html("<h1>Erster Tag</h1><h2>Vormittag</h2><p>Text</p>", "https://cogneon.de")
    assert "## Erster Tag" in conv.markdown and "### Vormittag" in conv.markdown
    assert conv.h1_count == 0 and conv.headings_shifted
    untouched = wp_export.convert_html("<h2>Abschnitt</h2>", "https://cogneon.de")
    assert "## Abschnitt" in untouched.markdown and not untouched.headings_shifted


def test_page_with_redirect_is_not_exported(server, tmp_path):
    (tmp_path / "migration").mkdir()
    (tmp_path / "migration/redirects.map").write_text(
        "# Kommentar\n/angebote/wissenstransfer /wissenstransfer/\n", encoding="utf-8")
    assert run_export(server, tmp_path) == 0
    assert not (tmp_path / "docs/angebote/wissenstransfer.md").exists()
    # ohne Unterseite liegt "Angebote" als einfache Datei vor - oder als Ordner, beides ist in Ordnung
    assert (tmp_path / "docs/angebote.md").exists() or (tmp_path / "docs/angebote/index.md").exists()


def test_category_redirects_follow_zensical_slug(server, tmp_path):
    assert wp_export.category_slug("Keep Calm & Learn On") == "keep-calm--learn-on"
    assert wp_export.category_slug("Führung und Kultur") == "führung-und-kultur"
    assert wp_export.category_slug("IT und Enterprise 2.0") == "it-und-enterprise-20"
    assert run_export(server, tmp_path) == 0
    rules = (tmp_path / "migration/redirects-kategorien.map").read_text(encoding="utf-8")
    assert "/category/ki /category/künstliche-intelligenz--lernen/" in rules


def test_tag_slug():
    assert wp_export.tag_slug("PersönlichesWissensmanagement") == "persoenlicheswissensmanagement"
    assert wp_export.tag_slug("lernOS") == "lernos"
    assert wp_export.tag_slug("4010km") == "4010km"


def test_tags_follow_mapping(server, tmp_path):
    (tmp_path / "migration").mkdir()
    (tmp_path / "migration/schlagworte.csv").write_text(
        "# Kommentar\nalt,neu\nLERNOS,lernOS\n", encoding="utf-8")
    assert run_export(server, tmp_path) == 0
    rules = (tmp_path / "migration/redirects-schlagworte.map").read_text(encoding="utf-8")
    assert "/tag/lernos " not in rules          # Adresse bleibt gleich, keine Weiterleitung
    meta = wp_export.read_frontmatter(tmp_path / "docs/blog/posts/2026/erster-beitrag.md")
    assert meta["tags"] == ["lernOS"]


def test_dropped_tags_redirect_to_blog(server, tmp_path):
    (tmp_path / "migration").mkdir()
    (tmp_path / "migration/schlagworte.csv").write_text("alt,neu\n", encoding="utf-8")
    assert run_export(server, tmp_path) == 0
    rules = (tmp_path / "migration/redirects-schlagworte.map").read_text(encoding="utf-8")
    assert "/tag/lernos /blog/" in rules
    posts = list((tmp_path / "docs/blog/posts").rglob("*.md"))
    assert posts and all("tags:" not in p.read_text(encoding="utf-8") for p in posts)


def test_featured_image_lands_in_frontmatter(server, tmp_path):
    assert run_export(server, tmp_path, "--no-media") == 0
    posts = [wp_export.read_frontmatter(p) for p in (tmp_path / "docs/blog/posts").rglob("*.md")]
    with_image = [m for m in posts if m.get("bild")]
    assert len(with_image) == 1
    assert with_image[0]["bild"] == "wp-content/uploads/2026/01/titel.jpg"
    assert list(with_image[0])[-1] == "wp"
    # zweiter Lauf ändert nichts mehr
    assert run_export(server, tmp_path, "--no-media") == 0


def test_calendar_markup_is_removed():
    source = ('<div class="tribe-events-schedule tribe-clearfix"><p>@</p></div><p>Text bleibt.</p>'
              '<div class="tribe-block tribe-block__events-link"><button>Zum Kalender hinzufügen</button></div>')
    cleaned = wp_export.Export.strip_calendar_markup(source)
    assert "Text bleibt." in cleaned and "Kalender" not in cleaned and "@" not in cleaned


def test_wordpress_buttons_stay_buttons():
    source = ('<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="/edmod">Mehr</a></div>'
              '<p><a class="wp-block-button__link uagb-text-link" href="/a">weiter</a> <a href="/b">normal</a></p>')
    markdown = wp_export.convert_html(source, "https://cogneon.de").markdown
    assert "[Mehr](/edmod){ .cg-button }" in markdown
    assert "[weiter](/a)" in markdown and "[weiter](/a){" not in markdown and "[normal](/b){" not in markdown


def test_nested_lists_use_four_spaces():
    source = ("<ol><li><strong>Ziele:</strong> Text<ul><li>Unterpunkt A<ul><li>tief</li></ul></li><li>Unterpunkt B</li></ul></li>"
              "<li>Zweitens</li></ol><p>Absatz</p><ul><li>eins<ul><li>zwei</li></ul></li></ul>")
    lines = wp_export.convert_html(source, "https://cogneon.de").markdown.splitlines()
    assert "1. **Ziele:** Text" in lines and "    - Unterpunkt A" in lines and "        - tief" in lines
    assert "    - Unterpunkt B" in lines and "2. Zweitens" in lines
    assert "- eins" in lines and "    - zwei" in lines


def test_escaped_characters_and_multiline_buttons():
    source = ('<p>Modul u0022PKE 101u0022 mit Copilot u0026amp; Co.</p>'
              '<div class="wp-block-button"><a class="wp-block-button__link" href="https://pretix.eu/x/">'
              '<div>Zur Lernreise anmelden</div><p>Alleine oder im Tandem</p></a></div>')
    markdown = wp_export.convert_html(source, "https://cogneon.de").markdown
    assert 'Modul "PKE 101" mit Copilot & Co.' in markdown
    assert "[Zur Lernreise anmelden - Alleine oder im Tandem](https://pretix.eu/x/){ .cg-button }" in markdown
