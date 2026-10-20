#!/usr/bin/env python3
"""
Just Apps — site icon pipeline.

The Just Apps "JA" mark is drawn in exactly the style of the Namaaz Reminder
app icon (design/source/NR-icon.png): the same rounded-squircle plate, the
same dark plate lighting with a lit top rim, and the same *engraved* monogram
— a recessed letter whose floor is lighter than the plate, with a black
contact shadow under the top edges and a bright chamfer along the bottom.

Every value below is measured from that artwork (plate tones, squircle
exponent, rim height, monogram cap height and tracking), so "JA" reads as the
sibling of "NR" rather than a different icon family.

Outputs (docs/assets):
  just-apps-icon-{32,64,128,256,512}.png   favicon, header logo, apple-touch
  just-apps-icon.svg                       favicon / schema logo
  nr-mark-header-{64,128}.png, .svg        the privacy page header mark

Run:  python3 design/build_site_icons.py
"""

from __future__ import annotations

import base64
import io
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "docs", "assets")

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

MASTER = 1024

# ---------------------------------------------------------------- artwork ---
# Measured from design/source/NR-icon.png.
SQUIRCLE_N = 4.3          # plate silhouette: |x|^n + |y|^n = 1
PLATE_TOP = 105.0         # tone just under the lit rim
PLATE_MID = 62.0
PLATE_LOW = 37.0
PLATE_BOTTOM = 12.0
RIM_LIGHT = 148.0         # the bright top rim (specular edge)
RIM_FRAC = 0.019          # how far the rim highlight reaches inward
EDGE_DARK = 0.55          # edges fall off away from the lit rim
CAP_FRAC = 0.452          # monogram cap height / plate side
GLYPH_XSCALE = 1.075      # NR sets its monogram almost edge to edge
TRACK_FRAC = -0.030       # letter spacing, share of cap height
BLUE_TINT = 2.0           # the artwork is neutral with a ~2/255 blue lift

MARKS = [
    ("JA", "just-apps-icon", [32, 64, 128, 256, 512]),
    ("NR", "nr-mark-header", [64, 128]),
]


# ------------------------------------------------------------------ utils ---
def _superellipse(size: int, n: float = SQUIRCLE_N) -> Image.Image:
    """Antialiased squircle mask, drawn 4x and downsampled."""
    ss = 4
    s = size * ss
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    u = (xx + 0.5) / s * 2 - 1
    v = (yy + 0.5) / s * 2 - 1
    d = np.abs(u) ** n + np.abs(v) ** n
    a = np.clip((1 - d) * (s / 6), 0, 1)          # cheap antialias ramp
    out = Image.fromarray((a * 255).astype(np.uint8), "L")
    return out.resize((size, size), Image.LANCZOS)


def _distance(mask: np.ndarray, steps: int) -> np.ndarray:
    """Inward distance from the silhouette edge, in pixels (erosion count)."""
    dist = np.zeros(mask.shape, np.float32)
    cur = (mask > 127)
    for _ in range(steps):
        cur = np.array(
            Image.fromarray((cur * 255).astype(np.uint8), "L").filter(ImageFilter.MinFilter(3))
        ) > 127
        dist += cur
    return dist


def _plate(size: int) -> np.ndarray:
    """The lit plate: vertical ramp, darker edges, specular top rim."""
    s = size
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    t = yy / (s - 1)

    # Row profile measured from design/source/NR-icon.png (512px scale).
    key_y = np.array([0.00, 0.03, 0.08, 0.14, 0.20, 0.30, 0.40, 0.50,
                      0.60, 0.70, 0.80, 0.90, 1.00])
    key_v = np.array([108.0, 96.0, 78.0, 68.0, 62.0, 50.0, 42.0, 36.0,
                      29.0, 24.0, 21.0, 16.0, 13.0])
    base = np.interp(t, key_y, key_v)

    # The light falls from the top centre: edges sit darker than the middle.
    u = (xx / (s - 1) - 0.5) * 2
    v = (yy / (s - 1) - 0.5) * 2
    radial = 1.0 - 0.20 * np.clip(np.abs(u) / 0.98, 0, 1) ** 2.6
    radial *= 1.0 - 0.10 * np.clip(np.abs(v), 0, 1) ** 3.0
    base = base * radial

    # Specular rim: a thin bright band just inside the silhouette, strongest
    # at the top and fading out by the bottom edge.
    mask_arr = np.array(_superellipse(size))
    steps = max(4, int(round(RIM_FRAC * s)) + 2)
    dist = _distance(mask_arr, steps)
    band = np.clip(1.0 - dist / max(1.0, RIM_FRAC * s), 0, 1)
    core = np.clip(1.0 - dist / max(1.0, RIM_FRAC * s * 0.35), 0, 1)
    rim = 0.40 * band ** 2.0 + 0.80 * core ** 1.4
    rim *= np.clip(1.30 - t * 2.6, 0, 1)
    base = base + (RIM_LIGHT - base) * np.clip(rim, 0, 1)

    return base


def _glyph_layer(text: str, size: int) -> np.ndarray:
    """Monogram mask, centred on its ink bounds (matches the artwork)."""
    s = size * 2                      # supersampled work canvas
    probe = ImageFont.truetype(FONT_PATH, 400)
    cap = probe.getbbox("H")[3] - probe.getbbox("H")[1]
    font = ImageFont.truetype(FONT_PATH, round(400 * (s * CAP_FRAC) / cap))
    track = TRACK_FRAC * (font.getbbox("H")[3] - font.getbbox("H")[1])

    widths = [font.getlength(ch) for ch in text]
    total = sum(widths) + track * (len(text) - 1)

    layer = Image.new("L", (s, s), 0)
    draw = ImageDraw.Draw(layer)
    x = (s - total) / 2
    baseline = s * 0.62
    for i, ch in enumerate(text):
        draw.text((round(x), baseline), ch, font=font, fill=255, anchor="ls")
        x += widths[i] + track

    ink = layer.getbbox()
    glyph = Image.new("L", (s, s), 0)
    glyph.paste(layer.crop(ink), ((s - (ink[2] - ink[0])) // 2,
                                  (s - (ink[3] - ink[1])) // 2))

    # NR's monogram runs almost the full plate width; a hint of horizontal
    # stretch lands "JA" on the same optical width without bending the letters.
    wide = int(round(s * GLYPH_XSCALE))
    stretched = glyph.resize((wide, s), Image.LANCZOS)
    off = (wide - s) // 2
    stretched = stretched.crop((off, 0, off + s, s))

    return np.array(stretched.resize((size, size), Image.LANCZOS)).astype(np.float32) / 255.0


def _blur(a: np.ndarray, sigma: float) -> np.ndarray:
    im = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8), "L")
    return np.array(im.filter(ImageFilter.GaussianBlur(sigma))).astype(np.float32) / 255.0


def _shift(a: np.ndarray, dy: float, dx: float = 0.0) -> np.ndarray:
    im = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8), "L")
    return np.array(
        im.transform(im.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy), resample=Image.BICUBIC)
    ).astype(np.float32) / 255.0


# ----------------------------------------------------------------- render ---
def render(text: str, size: int) -> Image.Image:
    # Below ~96px the engraving's subtle contrast disappears when downsampled,
    # so small sizes get a proportional contrast lift. The style is unchanged;
    # it just survives a 16-32px favicon slot.
    boost = 1.0 + max(0.0, (96 - size) / 96.0) * 1.05

    s = MASTER
    plate_l = _plate(s)
    glyph = _glyph_layer(text, s)

    px = s / 512.0                     # every effect scales with the plate
    yy = np.mgrid[0:s, 0:s][0].astype(np.float32) / (s - 1)

    # Recess floor: its own light curve (measured), brightest across the
    # middle of the letters and falling away at the bottom of the plate.
    # The recess floor follows the plate's own lighting, lifted a little, so
    # the letters read as part of the plate rather than as bright stickers.
    floor = plate_l * 1.70 + 17.0

    # Black contact shadow under the top edges of the recess.
    inner = _blur(_shift(1.0 - glyph, -1.5 * px), 0.85 * px)
    shadow_top = np.clip((inner - 0.16) / 0.84, 0, 1) ** 1.5
    tone = floor * (1 - 0.95 * shadow_top)

    # Bright chamfer along the bottom edges, and a softer one down the sides.
    lower = _blur(_shift(1.0 - glyph, 1.05 * px), 0.55 * px)
    bevel = np.clip((lower - 0.20) / 0.80, 0, 1) ** 1.9
    tone = tone + (178.0 - tone).clip(0) * bevel * 0.92

    # Soft shadow cast on the plate just outside the recess.
    cast = _blur(_shift(glyph, -1.8 * px, 0.5 * px), 1.4 * px)
    cast = np.clip((cast - 0.10) / 0.90, 0, 1) * (1 - glyph)
    plate_l = plate_l * (1 - 0.45 * cast)

    # Thin dark line hugging the monogram.
    ring = np.clip(_blur(glyph, 0.8 * px) - glyph, 0, 1)
    plate_l = plate_l - plate_l * ring * 0.55

    # Contrast lift for small sizes, applied around each letter's local plate.
    tone = plate_l + (tone - plate_l) * boost

    lum = plate_l * (1 - glyph) + tone * glyph
    lum = np.clip(lum, 0, 255)

    rgb = np.stack([lum, lum, np.clip(lum + BLUE_TINT, 0, 255)], axis=-1)

    # Clip to the plate silhouette.
    mask = np.array(_superellipse(s)).astype(np.float32) / 255.0
    out = np.zeros((s, s, 4), np.float32)
    out[..., :3] = rgb
    out[..., 3] = mask * 255

    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")
    return img.resize((size, size), Image.LANCZOS)


def svg(embedded_png: bytes, size: int) -> str:
    """Favicon SVG: the rendered mark, embedded so it matches the PNG exactly."""
    b64 = base64.b64encode(embedded_png).decode("ascii")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}" role="img" aria-label="Just Apps">\n'
        f'  <image width="{size}" height="{size}" '
        f'href="data:image/png;base64,{b64}"/>\n'
        f"</svg>\n"
    )


def main() -> None:
    os.makedirs(ASSETS, exist_ok=True)
    for text, prefix, sizes in MARKS:
        rendered = {size: render(text, size) for size in sizes}
        for size, img in rendered.items():
            path = os.path.join(ASSETS, f"{prefix}-{size}.png")
            img.save(path, "PNG", optimize=True)
            print("wrote", os.path.relpath(path, ROOT))

        buf = io.BytesIO()
        rendered[max(sizes)].save(buf, "PNG", optimize=True)
        svg_path = os.path.join(ASSETS, f"{prefix}.svg")
        with open(svg_path, "w") as fh:
            fh.write(svg(buf.getvalue(), max(sizes)))
        print("wrote", os.path.relpath(svg_path, ROOT))


if __name__ == "__main__":
    main()
