"""Placeholder photos drawn with Pillow: plain colour swatches with a label (no real imagery)."""
from __future__ import annotations

import io

from PIL import Image, ImageDraw


def make_swatch(label: str, colour: tuple[int, int, int]) -> bytes:
    img = Image.new("RGB", (480, 360), colour)
    ImageDraw.Draw(img).text((16, 16), label, fill=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=70)
    return buf.getvalue()
