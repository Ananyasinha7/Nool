"""Draws the Doc2 section 3 logo (an N as one thread ending in a status dot) to PNG icons with Pillow.
Run: python scripts/make_icons.py  -> frontend/public/icons/{icon-192,icon-512,maskable-512}.png"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parents[1] / "frontend" / "public" / "icons"
INK, PAPER, GREEN = (20, 24, 31), (250, 250, 247), (46, 125, 91)
SS = 4  # supersampling for smooth edges


def draw(size: int, safe: float = 1.0, rounded: bool = True) -> Image.Image:
    """safe < 1 shrinks the mark into the central safe zone (maskable icons keep 80%)."""
    s = size * SS
    img = Image.new("RGB", (s, s), INK)
    d = ImageDraw.Draw(img)
    if rounded:  # transparent corners come from the rounded mask below
        pass
    k = s / 64 * safe
    off = (s - 64 * k) / 2
    p = lambda x, y: (off + x * k, off + y * k)  # noqa: E731
    w = int(5 * k)
    pts = [p(18, 46), p(18, 18), p(46, 46)]
    d.line(pts, fill=PAPER, width=w, joint="curve")
    for x, y in (pts[0], pts[2]):  # round caps
        d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=PAPER)
    cx, cy = p(46, 18)
    r = 4.5 * k
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GREEN)
    img = img.resize((size, size), Image.LANCZOS)
    if rounded:
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * 14 / 64), fill=255)
        out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        out.paste(img, (0, 0), mask)
        return out
    return img


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    draw(192).save(OUT / "icon-192.png")
    draw(512).save(OUT / "icon-512.png")
    draw(512, safe=0.8, rounded=False).save(OUT / "maskable-512.png")  # full-bleed, mark inside the 80% safe zone
    print("icons written")
