#!/usr/bin/env python3
"""
Just Apps — site icon pipeline.

The older site icons were rendered from a 3D "debossed" artwork: at the 30px
header size the bevel and drop shadow collapse into a grey mush that reads as a
broken/blurry PNG. These marks are drawn instead:

  * flat, high-contrast monogram on the dark Nodes Mono plate,
  * geometry rendered from real font outlines, so it stays crisp at 16px,
  * one true vector SVG (glyph outlines, not an embedded bitmap) for the
    favicon and any HiDPI use.

Outputs (docs/assets):
  just-apps-icon-{32,64,128,256,512}.png   favicon, header logo, apple-touch, logo
  just-apps-icon.svg                   vector favicon / schema logo
  nr-mark-header-{64,128}.png          Namaaz Reminder page header
  nr-mark-header.svg                   vector mark for that page

The app-card artwork (nr-mark-*.png) is the real launcher artwork and is
deliberately left alone.

Run:  python3 design/build_site_icons.py
"""

from __future__ import annotations

import os

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "docs", "assets")

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Nodes Mono palette
PLATE_TOP = (26, 26, 30)      # #1A1A1E
PLATE_BOTTOM = (10, 10, 10)   # #0A0A0A
MARK = (238, 238, 240)        # #EEEEF0
RIM = (238, 238, 240, 36)     # off-white at ~14%

MASTER = 4096
RADIUS_FRAC = 0.225           # squircle-ish plate corner
CAP_FRAC = 0.430              # cap height / plate size
TRACK_FRAC = -0.035           # letter spacing, as a share of cap height

MARKS = [
    ("JA", "just-apps-icon", [32, 64, 128, 256, 512]),
    ("NR", "nr-mark-header", [64, 128]),
]


def _font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size)


def _cap_height(font: ImageFont.FreeTypeFont) -> int:
    top, bottom = font.getbbox("H")[1], font.getbbox("H")[3]
    return bottom - top


def _text_metrics(font: ImageFont.FreeTypeFont, text: str):
    """Width and x-offset of the monogram, including tracking."""
    cap = _cap_height(font)
    track = TRACK_FRAC * cap
    widths = [font.getlength(ch) for ch in text]
    total = sum(widths) + track * (len(text) - 1)
    return total, track, widths


def render_png(text: str, size: int) -> Image.Image:
    """Flat plate + monogram, supersampled then downsampled for clean edges."""
    s = MASTER
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))

    # Plate: vertical gradient, clipped by a rounded square.
    gradient = Image.new("RGBA", (s, s))
    gd = ImageDraw.Draw(gradient)
    for y in range(s):
        t = y / (s - 1)
        # ease the ramp so the plate stays dark at the bottom (Nodes Mono)
        t = t * t * (3 - 2 * t) * 0.85 + t * 0.15
        colour = tuple(
            round(PLATE_TOP[i] + (PLATE_BOTTOM[i] - PLATE_TOP[i]) * t) for i in range(3)
        )
        gd.line([(0, y), (s, y)], fill=colour + (255,))

    radius = round(s * RADIUS_FRAC)
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, s - 1, s - 1], radius=radius, fill=255)
    img.paste(gradient, (0, 0), mask)

    # Hairline rim so the plate separates from a dark page background.
    rim = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(rim).rounded_rectangle(
        [1, 1, s - 2, s - 2], radius=radius - 1, outline=RIM, width=max(2, s // 400)
    )
    rim.putalpha(Image.composite(rim.getchannel("A"), Image.new("L", (s, s), 0), mask))
    img.alpha_composite(rim)

    # Monogram on its own layer, then centred on its true ink bounds so the
    # mark sits optically centred whatever the glyph's descender.
    probe = _font(1000)
    cap = _cap_height(probe)
    font = _font(round(1000 * (s * CAP_FRAC) / cap))
    _, track, widths = _text_metrics(font, text)
    total, _, _ = _text_metrics(font, text)

    layer = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    baseline = round(s * 0.62)
    x = (s - total) / 2
    for i, ch in enumerate(text):
        draw.text((round(x), baseline), ch, font=font, fill=MARK + (255,), anchor="ls")
        x += widths[i] + track

    ink = layer.getchannel("A").getbbox()
    if ink:
        glyphs = layer.crop(ink)
        img.alpha_composite(
            glyphs,
            (
                (s - glyphs.width) // 2,
                (s - glyphs.height) // 2,
            ),
        )

    return img.resize((size, size), Image.LANCZOS)


def render_svg(text: str, size: int = 512) -> str:
    """Same plate and monogram as real vector outlines (no embedded bitmap)."""
    font = TTFont(FONT_PATH)
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    upem = font["head"].unitsPerEm
    glyph_margin = font["hmtx"]

    cap = getattr(font["OS/2"], "sCapHeight", None) or round(upem * 0.729)
    track = TRACK_FRAC * cap

    widths = [glyph_margin[cmap[ord(ch)]][0] for ch in text]
    total = sum(widths) + track * (len(text) - 1)
    scale = (size * CAP_FRAC) / cap

    # Ink bounds in font units, with the tracking applied, so the mark can be
    # centred on what is actually drawn rather than on advance widths.
    bounds = None
    x = 0.0
    for i, ch in enumerate(text):
        p = BoundsPen(glyphs)
        glyphs[cmap[ord(ch)]].draw(TransformPen(p, (1, 0, 0, -1, x, 0)))
        if p.bounds:
            b = p.bounds
            bounds = b if bounds is None else (
                min(bounds[0], b[0]), min(bounds[1], b[1]),
                max(bounds[2], b[2]), max(bounds[3], b[3]),
            )
        x += widths[i] + track

    tx = size / 2 - (bounds[0] + bounds[2]) / 2 * scale
    ty = size / 2 - (bounds[1] + bounds[3]) / 2 * scale

    parts = []
    x = 0.0
    for i, ch in enumerate(text):
        name = cmap[ord(ch)]
        pen = SVGPathPen(glyphs)
        # font units: x right, y up. Flip into SVG space and centre the ink.
        tpen = TransformPen(pen, (scale, 0, 0, -scale, tx + x * scale, ty))
        glyphs[name].draw(tpen)
        parts.append(pen.getCommands())
        x += widths[i] + track

    radius = round(size * RADIUS_FRAC, 2)
    rim_w = round(size / 400, 2)
    inset = rim_w / 2
    cap_ids = "".join(f'<path d="{d}"/>' for d in parts)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" \
width="{size}" height="{size}" role="img" aria-label="Just Apps">
  <defs>
    <linearGradient id="plate" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#{PLATE_TOP[0]:02X}{PLATE_TOP[1]:02X}{PLATE_TOP[2]:02X}"/>
      <stop offset="1" stop-color="#{PLATE_BOTTOM[0]:02X}{PLATE_BOTTOM[1]:02X}{PLATE_BOTTOM[2]:02X}"/>
    </linearGradient>
  </defs>
  <rect width="{size}" height="{size}" rx="{radius}" fill="url(#plate)"/>
  <rect x="{inset}" y="{inset}" width="{size - rim_w}" height="{size - rim_w}" \
rx="{radius - inset}" fill="none" stroke="#{MARK[0]:02X}{MARK[1]:02X}{MARK[2]:02X}" \
stroke-opacity="0.14" stroke-width="{rim_w}"/>
  <g fill="#{MARK[0]:02X}{MARK[1]:02X}{MARK[2]:02X}">{cap_ids}</g>
</svg>
"""


def main() -> None:
    os.makedirs(ASSETS, exist_ok=True)
    for text, prefix, sizes in MARKS:
        for size in sizes:
            path = os.path.join(ASSETS, f"{prefix}-{size}.png")
            render_png(text, size).save(path, "PNG", optimize=True)
            print("wrote", os.path.relpath(path, ROOT))
        svg_path = os.path.join(ASSETS, f"{prefix}.svg" if prefix == "just-apps-icon" else f"{prefix}.svg")
        with open(svg_path, "w") as fh:
            fh.write(render_svg(text))
        print("wrote", os.path.relpath(svg_path, ROOT))


if __name__ == "__main__":
    main()
