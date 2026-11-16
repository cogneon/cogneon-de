#!/usr/bin/env python3
"""Verkleinert übernommene Bilder unter docs/wp-content/.

Fotos aus WordPress sind oft mehrere tausend Pixel breit. Für die Website
reichen 1920 Pixel an der langen Kante. Dateinamen und Formate bleiben gleich,
damit alle Bild-Adressen weiter stimmen. Ein Bild wird nur ersetzt, wenn die
neue Datei wirklich kleiner ist. Animierte Bilder, SVG und andere Dateien
(PDF, Audio) bleiben unberührt.

Aufruf:  python scripts/optimize_media.py [--max 1920] [--quality 82]
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

from PIL import Image, ImageOps

FORMATS = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WEBP"}


def optimize(path: Path, max_edge: int, quality: int) -> int:
    """Gibt die eingesparten Bytes zurück (0, wenn die Datei bleibt, wie sie ist)."""
    fmt = FORMATS.get(path.suffix.lower())
    if not fmt:
        return 0
    before = path.stat().st_size
    try:
        with Image.open(path) as img:
            if getattr(img, "is_animated", False):
                return 0
            img = ImageOps.exif_transpose(img)      # Drehung aus den Kameradaten anwenden
            resized = max(img.size) > max_edge
            if resized:
                img.thumbnail((max_edge, max_edge), Image.LANCZOS)
            if fmt == "JPEG" and before < 300_000 and not resized:
                return 0                             # kleine JPEGs nicht erneut komprimieren
            out = io.BytesIO()
            if fmt == "JPEG":
                img.convert("RGB").save(out, "JPEG", quality=quality, optimize=True, progressive=True)
            elif fmt == "PNG":
                img.save(out, "PNG", optimize=True)
            else:
                img.save(out, "WEBP", quality=quality, method=6)
    except (OSError, ValueError) as error:
        print(f"übersprungen: {path} ({error})", file=sys.stderr)
        return 0
    data = out.getvalue()
    if len(data) >= before * 0.95:
        return 0
    path.write_bytes(data)
    return before - len(data)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dir", type=Path, default=Path(__file__).resolve().parent.parent / "docs" / "wp-content")
    parser.add_argument("--max", type=int, default=1920, help="längste Kante in Pixeln")
    parser.add_argument("--quality", type=int, default=82)
    args = parser.parse_args(argv)
    if not args.dir.is_dir():
        print(f"{args.dir} fehlt, nichts zu tun.")
        return 0
    files = [p for p in sorted(args.dir.rglob("*")) if p.is_file()]
    total = sum(p.stat().st_size for p in files)
    saved = changed = 0
    for path in files:
        gain = optimize(path, args.max, args.quality)
        if gain:
            saved += gain
            changed += 1
    print(f"{len(files)} Dateien, {changed} verkleinert: {total / 1e6:.0f} MB -> {(total - saved) / 1e6:.0f} MB")
    for path in sorted(files, key=lambda p: p.stat().st_size, reverse=True)[:10]:
        print(f"  {path.stat().st_size / 1e6:6.1f} MB  {path.relative_to(args.dir)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
