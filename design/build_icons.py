#!/usr/bin/env python3
"""
Namaaz Reminder — icon pipeline built from the original brand artwork.

Source of truth: design/source/NR-icon.png (the rendered NR tile). Everything
below is derived from it, so the app icon and the in-app header always match
the artwork exactly:

  * mipmap-*/ic_launcher.png          the artwork, tight-cropped
  * mipmap-*/ic_launcher_round.png    circular crop of the artwork
  * drawable/ic_app_icon.png          header badge
  * drawable/ic_launcher_foreground_mark.png
                                      adaptive foreground, mark kept inside the
                                      66dp safe zone of the 108dp canvas
  * drawable/ic_launcher_monochrome.xml
                                      themed-icon silhouette (system tinted),
                                      drawn from geometry because the artwork's
                                      3D shading cannot be tinted
  * drawable/ic_launcher_background.xml
                                      adaptive background matching the plate

Run:  python3 design/build_icons.py
"""

from __future__ import annotations

import math
import os

from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "app", "src", "main", "res")
SRC = os.path.join(ROOT, "design", "source", "NR-icon.png")
PREVIEW = os.path.join(ROOT, "design", "preview")

DENSITIES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}

# Fractions of the source artwork, measured from the file.
MARK_W_FRAC = 838 / 1099      # monogram width / plate width
SAFE_MARK_DP = 58.0           # monogram width; its shadows still fit the 66dp safe circle
CANVAS_DP = 108.0


def load_artwork() -> Image.Image:
    """The artwork, tightly cropped to its opaque plate (outer glow dropped)."""
    im = Image.open(SRC).convert("RGBA")
    box = im.getbbox()                      # alpha > 0, includes the soft glow
    alpha = im.getchannel("A")
    # Use the solid plate instead of the faint outer glow.
    solid = alpha.point(lambda v: 255 if v >= 250 else 0)
    x0, y0, x1, y1 = solid.getbbox()
    del box
    tile = im.crop((x0, y0, x1, y1))

    # Pad to a square without distorting, so every icon keeps the true shape.
    side = max(tile.size)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.paste(tile, ((side - tile.width) // 2, (side - tile.height) // 2))
    return square


def round_circle(art: Image.Image, size: int) -> Image.Image:
    """Circular icon: the plate's inscribed circle, antialiased at 4x."""
    ss = 4
    big = art.resize((size * ss, size * ss), Image.LANCZOS)
    mask = Image.new("L", (size * ss, size * ss), 0)
    from PIL import ImageDraw

    ImageDraw.Draw(mask).ellipse([0, 0, size * ss - 1, size * ss - 1], fill=255)
    out = Image.new("RGBA", (size * ss, size * ss), (0, 0, 0, 0))
    out.paste(big, (0, 0), mask)
    return out.resize((size, size), Image.LANCZOS)


def fit_plate(art: Image.Image, size: int) -> Image.Image:
    """
    A smooth full-bleed plate that reproduces the artwork's lighting.

    A low-order surface is fitted to the plate pixels only (the monogram and
    the plate's own rounded rim are excluded), so the result has no ghost rim
    and can be cut by any launcher mask.
    """
    import numpy as np

    a = np.array(art.convert("RGB")).astype(np.float32)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]

    # Keep clear of the plate rim and of the monogram.
    inset = 0.10 * w
    inner = (xx > inset) & (xx < w - inset) & (yy > inset) & (yy < h - inset)
    mx0, mx1 = 217 - inset * 0.9, 1054 + inset * 0.9
    my0, my1 = 399 - inset * 0.9, 843 + inset * 0.9
    mark = (xx > mx0) & (xx < mx1) & (yy > my0) & (yy < my1)
    sel = inner & ~mark
    sel[::2, :] = sel[::2, :] & (np.arange(w)[None, :] % 2 == 0)
    sel = sel & (yy % 2 == 0)

    nx = xx / w - 0.5
    ny = yy / h - 0.5
    # Quadratic basis: vertical falloff, horizontal falloff, and a vignette.
    basis = np.stack([np.ones_like(nx), ny, nx, ny * ny, nx * nx, (nx * nx + ny * ny)], -1)
    design = basis[sel]
    out = np.zeros((size, size, 3), np.float32)

    sy = np.linspace(-0.5, 0.5, size)
    sx = np.linspace(-0.5, 0.5, size)
    NX, NY = np.meshgrid(sx, sy)
    gbasis = np.stack(
        [np.ones_like(NX), NY, NX, NY * NY, NX * NX, (NX * NX + NY * NY)], -1
    )

    for c in range(3):
        vals = a[..., c][sel]
        coef, *_ = np.linalg.lstsq(design, vals, rcond=None)
        out[..., c] = gbasis @ coef

    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


def extend_plate(art: Image.Image, size: int) -> Image.Image:
    """
    Adaptive foreground: the artwork itself, full-bleed.

    The launcher mask always cuts a shape inside the 108dp canvas, so it crops
    the plate's own rounded rim exactly where a mask would cut anyway. The
    monogram's furthest corner sits at ~47% of the tile, well inside every mask,
    so nothing important is ever clipped.
    """
    return art.resize((size, size), Image.LANCZOS)


def adaptive_background(art: Image.Image, size: int) -> Image.Image:
    """
    Adaptive background: the plate edge tone, so the margin around the
    foreground (where a mask is wider than the artwork) stays consistent.
    """
    import numpy as np

    a = np.array(art.convert("RGB")).astype(np.float32)
    h, w = a.shape[:2]
    band = int(min(h, w) * 0.06)
    edge = np.concatenate([
        a[band:band + 8].reshape(-1, 3),
        a[h - band - 8:h - band].reshape(-1, 3),
        a[:, band:band + 8].reshape(-1, 3),
        a[:, w - band - 8:w - band].reshape(-1, 3),
    ])
    tone = tuple(int(v) for v in np.median(edge, axis=0))
    return Image.new("RGB", (size, size), tone)


# ------------------------------------------------------- monogram geometry ----
# The themed icon is a flat silhouette: the artwork's deboss cannot be tinted,
# so the mark is rebuilt from geometry with the artwork's proportions.
S = 1024
CAP = int(S * (445 / 838))            # cap height, as a share of the mark width
MARK_W = int(S * 0.90)                # mark width in master units
STROKE = int(CAP * 0.185)
GAP = int(MARK_W * 0.078)
N_W = int(MARK_W * 0.585)
R_W = MARK_W - GAP - N_W
BOWL_H = int(CAP * 0.66)
LEG_W = int(STROKE * 1.35)
X0 = (S - MARK_W) // 2
Y0 = (S - CAP) // 2
Y1 = Y0 + CAP


def _orient(pts, clockwise=True):
    area = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        area += x1 * y2 - x2 * y1
    is_cw = area < 0
    return list(pts) if is_cw == clockwise else list(reversed(pts))


def _arc(cx, cy, r, steps=28):
    return [
        (cx + r * math.cos(-math.pi / 2 + math.pi * i / steps),
         cy + r * math.sin(-math.pi / 2 + math.pi * i / steps))
        for i in range(steps + 1)
    ]


def n_shapes(x):
    s, w = STROKE, N_W
    return [
        _orient([(x, Y0), (x + s, Y0), (x + s, Y1), (x, Y1)]),
        _orient([(x + w - s, Y0), (x + w, Y0), (x + w, Y1), (x + w - s, Y1)]),
        _orient([(x, Y0), (x + s, Y0), (x + w, Y1), (x + w - s, Y1)]),
    ]


def r_shapes(x):
    s, w, r = STROKE, R_W, BOWL_H / 2
    cx = x + w - r
    stem = _orient([(x, Y0), (x + s, Y0), (x + s, Y1), (x, Y1)])
    bowl = _orient([(x, Y0), (cx, Y0)] + _arc(cx, Y0 + r, r) + [(x, Y0 + 2 * r)])
    leg = _orient([(x + w * 0.40, Y0 + r * 1.16), (cx + r, Y0 + r), (x + w, Y1), (x + w - LEG_W, Y1)])
    return [stem, bowl, leg]


def r_counter(x):
    s, w, r = STROKE, R_W, BOWL_H / 2
    cx = x + w - r
    ci = r - s
    return _orient(
        [(x + s, Y0 + s), (cx, Y0 + s)] + _arc(cx, Y0 + r, ci) + [(x + s, Y0 + 2 * r - s)],
        clockwise=False,
    )


def _path(pts, k, cx):
    def tx(p):
        return ((p[0] - S / 2) * k + cx, (p[1] - S / 2) * k + cx)

    return "M" + " L".join(f"{tx(p)[0]:.2f},{tx(p)[1]:.2f}" for p in pts) + " Z"


def monochrome_xml(safe_frac: float = 0.585) -> str:
    """Themed icon: solid NR silhouette, sized into the 108dp safe zone."""
    cx = 54.0
    k = (safe_frac * CANVAS_DP) / MARK_W
    xr = X0 + N_W + GAP
    parts = [_path(p, k, cx) for p in n_shapes(X0)]
    parts += [_path(p, k, cx) for p in r_shapes(xr)]
    parts.append(_path(r_counter(xr), k, cx))
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!--
    Monochrome (themed icon) layer: the NR monogram as a flat silhouette.
    The launcher tints this layer, so the artwork's deboss shading cannot be
    used here. Generated by design/build_icons.py - do not edit by hand.
-->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#FFFFFFFF"
        android:fillType="nonZero"
        android:pathData="{' '.join(parts)}" />
</vector>
"""


def background_xml(art: Image.Image) -> str:
    """Adaptive background: two sampled plate tones, top to bottom."""
    px = art.convert("RGB").load()
    w, h = art.size
    top = tuple(sum(px[x, int(h * 0.06)][i] for x in range(int(w * .3), int(w * .7))) // int(w * .4) for i in range(3))
    bottom = tuple(sum(px[x, int(h * 0.94)][i] for x in range(int(w * .3), int(w * .7))) // int(w * .4) for i in range(3))
    hexc = lambda c: "#FF%02X%02X%02X" % c
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!--
    Adaptive-icon background: the artwork's plate lighting. The foreground uses
    the real tile, so this only shows in the narrow margin around it.
    Tones sampled from design/source/NR-icon.png by design/build_icons.py.
-->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:aapt="http://schemas.android.com/aapt"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path android:pathData="M0,0h108v108h-108z">
        <aapt:attr name="android:fillColor">
            <gradient
                android:type="linear"
                android:startX="0"
                android:startY="0"
                android:endX="0"
                android:endY="108"
                android:startColor="{hexc(top)}"
                android:endColor="{hexc(bottom)}" />
        </aapt:attr>
    </path>
</vector>
"""


def main() -> None:
    os.makedirs(PREVIEW, exist_ok=True)
    art = load_artwork()
    print("artwork:", art.size)

    for dpi, px in DENSITIES.items():
        out = os.path.join(RES, f"mipmap-{dpi}")
        os.makedirs(out, exist_ok=True)
        art.resize((px, px), Image.LANCZOS).save(os.path.join(out, "ic_launcher.png"))
        round_circle(art, px).save(os.path.join(out, "ic_launcher_round.png"))

    # Bitmaps live in a density bucket, never in the densityless drawable/
    # folder: there they would be treated as mdpi and decoded far larger than
    # needed. 34dp header badge at xxxhdpi is 136px; 192px keeps it crisp.
    xxxhdpi = os.path.join(RES, "drawable-xxxhdpi")
    os.makedirs(xxxhdpi, exist_ok=True)
    art.resize((192, 192), Image.LANCZOS).save(os.path.join(xxxhdpi, "ic_app_icon.png"))
    # Adaptive foreground is 108dp: 432px at xxxhdpi.
    extend_plate(art, 432).save(
        os.path.join(xxxhdpi, "ic_launcher_foreground_mark.png")
    )
    with open(os.path.join(RES, "drawable", "ic_launcher_monochrome.xml"), "w") as fh:
        fh.write(monochrome_xml())
    with open(os.path.join(RES, "drawable", "ic_launcher_background.xml"), "w") as fh:
        fh.write(background_xml(art))

    art.resize((1024, 1024), Image.LANCZOS).save(os.path.join(PREVIEW, "icon-1024.png"))
    adaptive_background(art, 432).save(os.path.join(PREVIEW, "adaptive-background.png"))
    print("wrote assets +", os.path.join(PREVIEW, "icon-1024.png"))


if __name__ == "__main__":
    main()
