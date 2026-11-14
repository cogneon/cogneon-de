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
             "slug": "erster-beitrag", "link": f"{base}/2026/01/erster-beitrag/",
             "title": {"rendered": "Erster Beitrag &#8211; Test"}, "content": {"rendered": html},
             "excerpt": {"rendered": ""}, "author": 1, "categories": [5], "tags": [7],
             "featured_media": 90, "sticky": False},
            {"id": 12, "date": "2025-11-03T08:00:00", "modified": "2025-11-03T08:00:00",
             "slug": "zweiter-beitrag", "link": f"{base}/2025/11/zweiter-beitrag/",
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
        "wp/v2/categories": [{"id": 5, "name": "Künstliche Intelligenz", "slug": "ki",
                              "description": "", "link": f"{base}/category/ki/"}],
        "wp/v2/tags": [{"id": 7, "name": "lernOS", "slug": "lernos", "description": "",
                        "link": f"{base}/tag/lernos/"}],
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
    assert "Eingebetteter Inhalt: www.youtube.com" in md
    assert conv.shortcodes == ["charta_unterschriften"]
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
    assert meta["categories"] == ["Künstliche Intelligenz"]
    assert meta["tags"] == ["lernOS"]
    assert str(meta["date"]["created"]) == "2026-01-15"
    assert "<!-- more -->" in post.read_text(encoding="utf-8")
    assert wp_export.read_frontmatter(tmp_path / "docs/blog/posts/2025/zweiter-beitrag.md")["pin"] is True

    assert (tmp_path / "docs/angebote/index.md").exists()
    assert (tmp_path / "docs/angebote/wissenstransfer/index.md").exists()
    assert "Handgebaut" in home.read_text(encoding="utf-8"), "frozen-Seite wurde überschrieben"

    for name in ("bild-1024x576.png", "handout.pdf", "titel.jpg"):
        assert (tmp_path / "docs/wp-content/uploads/2026/01" / name).exists(), name

    authors = yaml.safe_load((tmp_path / "docs/blog/.authors.yml").read_text(encoding="utf-8"))
    assert authors["authors"]["erika.muster"]["description"] == "Beraterin"

    report = (tmp_path / "migration/report.md").read_text(encoding="utf-8")
    assert "`/{yyyy}/{mm}/{slug}/`: 2" in report
    assert "[charta_unterschriften]" in report
    assert "www.youtube.com: 1" in report
    assert "Veranstaltungen: 3" in report
    url_map = (tmp_path / "migration/url-map.csv").read_text(encoding="utf-8")
    assert "/2026/01/erster-beitrag/,post,11" in url_map
    assert ",frozen" in url_map

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
