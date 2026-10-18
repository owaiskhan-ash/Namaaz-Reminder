#!/usr/bin/env python3
"""
Namaaz Reminder — "NR" debossed monogram generator.

The mark is built as geometry rather than typeset from a font: a heavy,
Adobe-style block monogram pressed into a black box. Outputs every Android
asset the app needs:

  * legacy launcher icons      mipmap-*dpi/ic_launcher(.png|_round.png)
  * adaptive-icon foreground   drawable/ic_launcher_foreground_mark.png
  * in-app header badge        drawable/ic_app_icon.png
  * vector path data           design/nr_monogram_path.txt

Run:  python3 design/nr_monogram.py
"""

from __future__ import annotations

import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter

# ---------------------------------------------------------------- palette ----
BOX_TOP = (30, 30, 30)        # #1E1E1E — the black box, top lit
BOX_BOTTOM = (18, 18, 18)     # #121212 — gentle falloff
LETTER = (0, 0, 0)            # recess floor: pure black, clearly below the box
WALL_TOP = (0, 0, 0, 200)     # the upper inner wall sits in shadow
WALL_BASE = (255, 255, 255, 0.16)  # light catches the lower inner wall
EDGE = (255, 255, 255, 0.10)  # hairline bevel on the tile edge

# --------------------------------------------------------------- geometry ----
S = 1024                      # master canvas
CAP = 428                     # cap height
STROKE = 80                   # stem weight (~19% of cap: heavy grotesque)
N_W = 266
R_W = 272
GAP = 60
BOWL_H = int(CAP * 0.655)     # R bowl height
LEG_W = 108                   # horizontal thickness of the R leg

X0 = (S - (N_W + GAP + R_W)) // 2
Y0 = (S - CAP) // 2
Y1 = Y0 + CAP


def _orient(pts, clockwise=True):
    """Wound clockwise (screen coords, y down) so overlaps union."""
    area = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        area += x1 * y2 - x2 * y1
    is_cw = area < 0
    return list(pts) if is_cw == clockwise else list(reversed(pts))


def _arc(cx, cy, r, steps=28):
    """Right-hand semicircle, top to bottom."""
    out = []
    for i in range(steps + 1):
        ang = -math.pi / 2 + math.pi * i / steps
        out.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return out


def n_shapes(x: int) -> list[list[tuple[float, float]]]:
    """N = left stem, right stem, and the classic corner-to-corner diagonal."""
    s, w = STROKE, N_W
    return [
        _orient([(x, Y0), (x + s, Y0), (x + s, Y1), (x, Y1)]),
        _orient([(x + w - s, Y0), (x + w, Y0), (x + w, Y1), (x + w - s, Y1)]),
        # Horizontal thickness equals the stroke, so the joints are seamless.
        _orient([(x, Y0), (x + s, Y0), (x + w, Y1), (x + w - s, Y1)]),
    ]


def r_outer_shapes(x: int) -> list[list[tuple[float, float]]]:
    """R silhouette as three overlapping shapes: stem, D-bowl, splayed leg."""
    s, w = STROKE, R_W
    r = BOWL_H / 2
    bowl_right = x + w * 0.94          # the bowl stops just inside the letter width
    cx = bowl_right - r
    yb = Y0 + BOWL_H

    stem = _orient([(x, Y0), (x + s, Y0), (x + s, Y1), (x, Y1)])
    bowl = _orient([(x, Y0), (cx, Y0)] + _arc(cx, Y0 + r, r) + [(x, yb)])

    # The leg leaves the bowl exactly at its widest point, where the outline is
    # already vertical, so the outer contour flows on without a notch.
    leg = _orient([
        (x + w * 0.40, Y0 + r * 1.16),  # inner edge, tucked under the bowl
        (cx + r, Y0 + r),               # outer edge: the bowl's equator
        (x + w, Y1),
        (x + w - LEG_W, Y1),
    ])
    return [stem, bowl, leg]


def r_counter(x: int) -> list[tuple[float, float]]:
    """Counter of the R bowl, wound the other way so it cuts a hole."""
    s, w = STROKE, R_W
    r = BOWL_H / 2
    bowl_right = x + w * 0.94
    cx = bowl_right - r
    ci = r - s
    pts = [
        (x + s, Y0 + s),
        (cx, Y0 + s),
    ] + _arc(cx, Y0 + r, ci) + [(x + s, Y0 + BOWL_H - s)]
    return _orient(pts, clockwise=False)


def monogram_mask(size: int, scale: float = 1.0, ss: int = 2) -> Image.Image:
    """Raster mask (L) of the NR mark, supersampled for clean edges."""
    big = size * ss
    img = Image.new("L", (big, big), 0)
    d = ImageDraw.Draw(img)
    k = big / S * scale
    # Centred after scaling.
    ox = (big - S * k) / 2
    oy = (big - S * k) / 2

    def poly(pts, fill):
        d.polygon([(px * k + ox, py * k + oy) for px, py in pts], fill=fill)

    for p in n_shapes(X0):
        poly(p, 255)
    xr = X0 + N_W + GAP
    for p in r_outer_shapes(xr):
        poly(p, 255)
    poly(r_counter(xr), 0)
    return img.resize((size, size), Image.LANCZOS)


def rounded_rect_mask(size: int, radius_ratio: float, ss: int = 4) -> Image.Image:
    big = size * ss
    img = Image.new("L", (big, big), 0)
    ImageDraw.Draw(img).rounded_rectangle(
        [0, 0, big - 1, big - 1], radius=big * radius_ratio, fill=255
    )
    return img.resize((size, size), Image.LANCZOS)


def vertical_gradient(size: int, top, bottom) -> Image.Image:
    grad = Image.new("RGB", (1, size))
    px = grad.load()
    for y in range(size):
        t = y / max(size - 1, 1)
        px[0, y] = tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    # Repeat the exact rows sideways; a vertical-only resize keeps it smooth.
    return grad.resize((size, size), Image.BICUBIC)


def _tint(size: int, rgba, mask: Image.Image) -> Image.Image:
    """A flat colour image whose alpha is `rgba`'s alpha shaped by `mask`."""
    overlay = Image.new("RGBA", (size, size), rgba)
    overlay.putalpha(ImageChops.multiply(overlay.getchannel("A"), mask))
    return overlay


def _recess(size: int, letters: Image.Image) -> Image.Image:
    """Letters pressed into the surface: matte floor, shadowed top wall, lit base."""
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    band = max(1, round(size / 512))

    # 1. Recess floor.
    layer.alpha_composite(_tint(size, LETTER + (255,), letters))

    # 2. Upper inner wall, in shadow: a band just inside the top edge.
    shifted_down = ImageChops.offset(letters, 0, band)
    top_wall = ImageChops.subtract(letters, shifted_down)
    top_wall = top_wall.filter(ImageFilter.GaussianBlur(band * 0.30))
    layer.alpha_composite(_tint(size, WALL_TOP, top_wall))

    # 3. Lower inner wall, catching light: a band just inside the bottom edge.
    shifted_up = ImageChops.offset(letters, 0, -band)
    base_wall = ImageChops.subtract(letters, shifted_up)
    base_wall = base_wall.filter(ImageFilter.GaussianBlur(band * 0.30))
    layer.alpha_composite(_tint(size, WALL_BASE[:3] + (round(255 * WALL_BASE[3]),), base_wall))
    return layer


def badge(size: int, shape: str = "squircle") -> Image.Image:
    """Full badge: a black box with the NR mark debossed into it."""
    # Work at a fixed high resolution, then downscale, so the 1px deboss
    # light stays clean even in the 48px legacy icon.
    big = max(size * 2, 1024)
    radius = 0.225

    if shape == "circle":
        mask = Image.new("L", (big, big), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, big - 1, big - 1], fill=255)
    else:
        mask = Image.new("L", (big, big), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            [0, 0, big - 1, big - 1], radius=big * radius, fill=255
        )

    tile = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    tile.paste(vertical_gradient(big, BOX_TOP, BOX_BOTTOM).convert("RGBA"), (0, 0), mask)
    tile.alpha_composite(_recess(big, monogram_mask(big, ss=1)))

    # Hairline bevel around the tile, inside the rounded edge.
    edge = Image.new("L", (big, big), 0)
    ImageDraw.Draw(edge).rounded_rectangle(
        [0, 0, big - 1, big - 1],
        radius=big * radius,
        outline=255,
        width=max(1, big // 512),
    )
    edge = ImageChops.multiply(edge, mask)
    tile.alpha_composite(_tint(big, EDGE[:3] + (round(255 * EDGE[3]),), edge))

    return tile.resize((size, size), Image.LANCZOS)


# Fraction of the 108dp adaptive layer the monogram's cap height should span;
# 0.44 keeps the whole mark inside the 72dp safe zone of every launcher mask.
SAFE_CAP = 0.44


def foreground(size: int) -> Image.Image:
    """Adaptive-icon foreground: transparent, mark inside the safe zone."""
    big = max(size * 2, 1024)
    letters = monogram_mask(big, scale=SAFE_CAP / (CAP / S), ss=1)
    canvas = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    canvas.alpha_composite(_recess(big, letters))
    return canvas.resize((size, size), Image.LANCZOS)


# ------------------------------------------------------------ vector path ----
def _path(pts, k: float = 1.0, cx: float = 0.0) -> str:
    """Sub-path in master units, optionally scaled about the canvas centre."""
    def tx(p):
        return ((p[0] - S / 2) * k + cx, (p[1] - S / 2) * k + cx)

    return "M" + " L".join(f"{tx(p)[0]:.2f},{tx(p)[1]:.2f}" for p in pts) + " Z"


def monogram_path_data(k: float = 1.0, cx: float = S / 2) -> str:
    """NR as one path string: clockwise sub-paths union, the counter cuts out."""
    parts = [_path(p, k, cx) for p in n_shapes(X0)]
    xr = X0 + N_W + GAP
    parts += [_path(p, k, cx) for p in r_outer_shapes(xr)]
    parts.append(_path(r_counter(xr), k, cx))
    return " ".join(parts)


def monochrome_xml() -> str:
    """Themed-icon layer: a solid silhouette in a 108dp viewport."""
    cx = 54.0
    k = (SAFE_CAP * 108) / (S * (CAP / S)) / 108 * (108 / S) * (S / 108)
    k = (SAFE_CAP * 108) / CAP * (1.0) / 1.0
    # k scales master units so the cap becomes SAFE_CAP * 108 dp.
    k = (SAFE_CAP * 108) / CAP
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!--
    Monochrome (themed icon) layer: the NR monogram as a solid silhouette.
    Generated by design/nr_monogram.py - do not edit by hand.
-->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <!-- All outer sub-paths run clockwise and the R counter runs the other
         way, so nonZero unions the letterforms and cuts the bowl. -->
    <path
        android:fillColor="#FFFFFFFF"
        android:fillType="nonZero"
        android:pathData="{monogram_path_data(k, cx)}" />
</vector>
"""


# ----------------------------------------------------------------- output ----
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "app", "src", "main", "res")
PREVIEW = os.path.join(ROOT, "design", "preview")

DENSITIES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}


def main() -> None:
    os.makedirs(PREVIEW, exist_ok=True)

    for dpi, px in DENSITIES.items():
        out = os.path.join(RES, f"mipmap-{dpi}")
        os.makedirs(out, exist_ok=True)
        badge(px, "squircle").save(os.path.join(out, "ic_launcher.png"))
        badge(px, "circle").save(os.path.join(out, "ic_launcher_round.png"))

    badge(512, "squircle").save(os.path.join(RES, "drawable", "ic_app_icon.png"))
    foreground(864).save(os.path.join(RES, "drawable", "ic_launcher_foreground_mark.png"))

    # Review sheet: large mark, then real sizes on a light and a dark surface.
    badge(1024, "squircle").save(os.path.join(PREVIEW, "icon-1024.png"))

    W, H = 1240, 700
    sheet = Image.new("RGB", (W, H), (246, 246, 246))
    d = ImageDraw.Draw(sheet)
    big_icon = badge(300, "squircle")
    sheet.paste(big_icon, (40, 60), big_icon)
    d.rectangle([370, 60, W - 40, 60 + 300], fill=(10, 10, 10))
    x = 400
    for px in (192, 144, 96, 48):
        art = badge(px, "squircle")
        sheet.paste(art, (x, 60 + (300 - px) // 2), art)
        x += px + 44
    d.rectangle([370, 60, W - 40, 60 + 300], outline=(200, 200, 200), width=1)
    d.text((40, 400), "light surface", fill=(60, 60, 60))
    x = 40
    for px in (192, 144, 96, 48):
        art = badge(px, "squircle")
        sheet.paste(art, (x, 430), art)
        x += px + 34
    d.text((40, 640), "minimum launcher size: 48dp", fill=(90, 90, 90))
    sheet.save(os.path.join(PREVIEW, "sheet.png"))

    with open(os.path.join(RES, "drawable", "ic_launcher_monochrome.xml"), "w") as fh:
        fh.write(monochrome_xml())
    print("wrote", os.path.join(PREVIEW, "sheet.png"))


if __name__ == "__main__":
    main()
