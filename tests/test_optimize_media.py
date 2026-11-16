"""Tests für scripts/optimize_media.py."""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import optimize_media  # noqa: E402


def test_grosse_bilder_werden_verkleinert_kleine_bleiben(tmp_path):
    gross, klein, pdf = tmp_path / "a/gross.jpg", tmp_path / "klein.png", tmp_path / "datei.pdf"
    gross.parent.mkdir()
    Image.effect_noise((4000, 3000), 60).convert("RGB").save(gross, "JPEG", quality=95)
    Image.new("RGB", (200, 100), "white").save(klein, "PNG", optimize=True)
    pdf.write_bytes(b"%PDF-1.4")
    before = {p: p.read_bytes() for p in (klein, pdf)}
    size = gross.stat().st_size

    assert optimize_media.main(["--dir", str(tmp_path)]) == 0
    with Image.open(gross) as img:
        assert img.size == (1920, 1440) and img.format == "JPEG"
    assert gross.stat().st_size < size
    assert all(p.read_bytes() == data for p, data in before.items())
