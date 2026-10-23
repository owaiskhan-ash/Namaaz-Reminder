#!/usr/bin/env python3
"""Render crisp, retina 1:1 Subscription Tracker v1.2.0 screenshots for the Just Apps website.

Uses the authentic `ST.` icon (`design/source/ST-sub-icon.png`) and tactile suede/felt
textures (`design/source/subtracker_tex/*.jpg`) from `owaiskhan-ash/Subscription-Tracker`
v1.2.0 (`android/app/src/main/assets/www/index.html`).

Outputs in `docs/assets/subscriptions/`:
  - today-{400,780}.webp + today.png + today.svg
  - all-{400,780}.webp + all.png + all.svg
  - settings-{400,780}.webp + settings.png + settings.svg

Run:  python3 design/build_subtracker_screenshots.py
"""

from __future__ import annotations

import base64
import io
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ICON_PATH = ROOT / "design" / "source" / "ST-sub-icon.png"
TEX_DIR = ROOT / "design" / "source" / "subtracker_tex"
FONTS_DIR = ROOT / "docs" / "assets" / "fonts"
OUT_DIR = ROOT / "docs" / "assets" / "subscriptions"

# Render at 3x of 390x844 (1170x2532), then downsample with LANCZOS to 780x1688 and 400x866
S = 3
W, H = 390 * S, 844 * S

# Exact v1.2.0 CSS variables from Subscription-Tracker index.html
C_BG = (13, 16, 16, 255)             # #0D1010
C_BAR = (14, 17, 17, 245)            # rgba(14,17,17,.94)
C_INK = (239, 228, 208, 255)         # #EFE4D0 warm champagne-ivory
C_DARK_INK = (22, 20, 16, 255)       # #161410 ink on champagne pill/FAB
C_MUTED = (167, 158, 142, 255)       # #A79E8E
C_FAINT = (110, 104, 93, 255)        # #6E685D
C_PETROL_MUTED = (181, 198, 194, 255)# #B5C6C2
C_SIDE_TEAL = (107, 166, 166, 255)   # #6BA6A6
C_WARM_TRAIL = (196, 174, 136, 255)  # #C4AE88
C_LIME = (165, 195, 57, 255)         # #A5C339 ST. period botanical lime dot
C_SOON = (200, 222, 116, 255)        # #C8DE74 due soon highlight
C_HAIR = (239, 228, 208, 29)         # rgba(239,228,208,.11)
C_STITCH = (239, 224, 196, 62)       # rgba(239,224,196,.24)
C_STITCH_SOFT = (239, 224, 196, 42)  # rgba(239,224,196,.16)

# Card suede tone presets: (tex_file, base_rgb, tint_alpha, border_rgba)
SUEDE_STYLES: Dict[str, Tuple[str, Tuple[int, int, int], float, Tuple[int, int, int, int]]] = {
    "petrol": ("card-petrol.jpg", (32, 56, 54), 0.36, (110, 175, 172, 48)),
    "teal":   ("card-teal.jpg",   (31, 61, 62), 0.34, (74, 154, 154, 50)),
    "sand":   ("card-sand.jpg",   (56, 46, 33), 0.38, (196, 162, 114, 50)),
    "olive":  ("card-olive.jpg",  (48, 47, 29), 0.36, (154, 148, 92, 48)),
    "cognac": ("card-cognac.jpg", (60, 34, 24), 0.38, (186, 108, 78, 52)),
}

_TEX_CACHE: Dict[str, Image.Image] = {}


def px(dp: float) -> int:
    return int(round(dp * S))


def rgba(rgb: Tuple[int, int, int, int], alpha: float) -> Tuple[int, int, int, int]:
    return (rgb[0], rgb[1], rgb[2], int(round(255 * alpha)))


def rgba_draw(canvas: Image.Image) -> ImageDraw.ImageDraw:
    return ImageDraw.Draw(canvas, "RGBA")


def paste_rgba(canvas: Image.Image, layer: Image.Image, xy: Tuple[int, int]) -> None:
    canvas.paste(layer, xy, layer)


def get_tex(name: str, tile_dp: float = 220.0) -> Image.Image:
    key = f"{name}:{tile_dp}"
    if key not in _TEX_CACHE:
        sz = px(tile_dp)
        im = Image.open(TEX_DIR / name).convert("RGB").resize((sz, sz), Image.LANCZOS)
        _TEX_CACHE[key] = im
    return _TEX_CACHE[key]


def font_sans(size_dp: float, weight: int = 400) -> ImageFont.FreeTypeFont:
    w_map = {
        400: "plus-jakarta-sans-latin-400-normal.woff2",
        500: "plus-jakarta-sans-latin-500-normal.woff2",
        600: "plus-jakarta-sans-latin-600-normal.woff2",
        700: "plus-jakarta-sans-latin-700-normal.woff2",
    }
    nearest = min(w_map.keys(), key=lambda k: abs(k - weight))
    return ImageFont.truetype(str(FONTS_DIR / w_map[nearest]), px(size_dp))


def font_serif(size_dp: float, weight: int = 500) -> ImageFont.FreeTypeFont:
    fname = (
        "cormorant-garamond-latin-600-normal.woff2"
        if weight >= 600
        else "cormorant-garamond-latin-500-normal.woff2"
    )
    return ImageFont.truetype(str(FONTS_DIR / fname), px(size_dp))


def font_unicode_sym(size_dp: float) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", px(size_dp))


def _glyph_ink_metrics(
    text: str,
    f_hi: ImageFont.FreeTypeFont,
    base_y: int,
    anchor_y: str,
    tracking_px: float,
    space_px: float,
) -> Tuple[List[Tuple[str, float, float]], float]:
    probe = ImageDraw.Draw(Image.new("L", (4, 4), 0))
    items: List[Tuple[str, float, float]] = []
    for ch in text:
        if ch == " ":
            items.append((ch, 0.0, space_px))
        else:
            bb = probe.textbbox((0, base_y), ch, font=f_hi, anchor=anchor_y)
            items.append((ch, float(bb[0]), float(bb[2] - bb[0])))
    total = sum(w for _, _, w in items) + tracking_px * max(0, len(items) - 1)
    return items, total


def tracked_width(
    draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, tracking_dp: float
) -> float:
    if not text:
        return 0.0
    hs = 3
    f_hi = ImageFont.truetype(font.path, font.size * hs)
    t_hi = (tracking_dp + 0.50) * S * hs
    sp_hi = font.size * hs * 0.34
    _, total_hi = _glyph_ink_metrics(text, f_hi, 100, "la", t_hi, sp_hi)
    return total_hi / hs


def draw_tracked(
    draw: ImageDraw.ImageDraw,
    xy: Tuple[float, float],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: Tuple[int, int, int, int],
    tracking_dp: float = 1.6,
    align: str = "left",
    anchor_y: str = "la",
) -> float:
    if not text:
        return 0.0
    hs = 3
    f_hi = ImageFont.truetype(font.path, font.size * hs)
    t_hi = (tracking_dp + 0.50) * S * hs
    sp_hi = font.size * hs * 0.34
    pad_hi = font.size * hs
    lh = max(4, int(math.ceil(font.size * hs * 2.4)))
    base_y = lh // 2
    items, total_hi = _glyph_ink_metrics(text, f_hi, base_y, anchor_y, t_hi, sp_hi)
    lw = max(4, int(math.ceil(total_hi + pad_hi * 2)))
    mask_hi = Image.new("L", (lw, lh), 0)
    md = ImageDraw.Draw(mask_hi)
    cx = float(pad_hi)
    for ch, x_off, ink_w in items:
        if ch != " ":
            md.text((round(cx - x_off), base_y), ch, font=f_hi, fill=255, anchor=anchor_y)
        cx += ink_w + t_hi

    out_w = max(1, int(round(lw / hs)))
    out_h = max(1, int(round(lh / hs)))
    mask = mask_hi.resize((out_w, out_h), Image.LANCZOS)

    total_w = total_hi / hs
    x, y = xy
    if align == "right":
        x -= total_w
    elif align == "center":
        x -= total_w / 2.0
    px_x = int(round(x - pad_hi / hs))
    px_y = int(round(y - (base_y / hs)))

    if len(fill) == 4 and fill[3] < 255:
        mask = mask.point(lambda a: int(round(a * fill[3] / 255.0)))
    draw._image.paste(fill[:3], (px_x, px_y, px_x + out_w, px_y + out_h), mask)
    return total_w


def new_felt_screen() -> Image.Image:
    """Create 1170x2532 charcoal felt canvas matching `.phone-shell` in index.html."""
    canvas = Image.new("RGB", (W, H), C_BG[:3])
    tile = get_tex("felt-charcoal.jpg", 240.0)
    tw, th = tile.size
    for ty in range(0, H, th):
        for tx in range(0, W, tw):
            canvas.paste(tile, (tx, ty))

    # Overlay linear-gradient(180deg, rgba(32,56,54,.12) 0%, rgba(13,16,16,.88) 45%, rgba(13,16,16,.96) 100%)
    d = rgba_draw(canvas)
    bands = 48
    for i in range(bands):
        y0 = int(H * i / bands)
        y1 = int(H * (i + 1) / bands)
        t = i / (bands - 1)
        if t < 0.45:
            u = t / 0.45
            r = int(round(32 * (1 - u) + 13 * u))
            g = int(round(56 * (1 - u) + 16 * u))
            b = int(round(54 * (1 - u) + 16 * u))
            a = int(round(255 * (0.52 * (1 - u) + 0.88 * u)))
        else:
            u = (t - 0.45) / 0.55
            r, g, b = 13, 16, 16
            a = int(round(255 * (0.88 * (1 - u) + 0.95 * u)))
        d.rectangle((0, y0, W, y1), fill=(r, g, b, a))
    return canvas


def draw_status_bar(canvas: Image.Image) -> None:
    d = rgba_draw(canvas)
    d.rectangle((0, 0, W, px(28)), fill=(14, 17, 17, 235))
    f_time = font_sans(11.5, 600)
    d.text((px(24), px(8)), "9:41", font=f_time, fill=rgba(C_INK, 0.82))

    rx = W - px(24)
    bw, bh = px(18), px(9.5)
    bx, by = rx - bw, px(10)
    d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=px(2.2), outline=rgba(C_INK, 0.72), width=max(1, px(0.9)))
    d.rectangle((bx + px(2), by + px(2), bx + bw - px(4), by + bh - px(2)), fill=rgba(C_INK, 0.80))
    d.rectangle((bx + bw, by + px(2.8), bx + bw + px(1.6), by + bh - px(2.8)), fill=rgba(C_INK, 0.72))

    sx = bx - px(20)
    for i in range(4):
        bar_h = px(3.2 + i * 1.8)
        x0 = sx + i * px(3.6)
        y1 = by + bh
        d.rounded_rectangle(
            (x0, y1 - bar_h, x0 + px(2.2), y1),
            radius=px(0.8),
            fill=rgba(C_INK, 0.80 if i < 3 else 0.42),
        )


def draw_topbar(canvas: Image.Image, right_label: str = "4 SUBS") -> int:
    top_y = px(28)
    bar_h = px(54)
    d = rgba_draw(canvas)
    d.rectangle((0, top_y, W, top_y + bar_h), fill=C_BAR)

    cy = top_y + bar_h // 2
    logo_dp = 28
    lx = px(22)
    ly = cy - px(logo_dp) // 2
    logo = Image.open(ICON_PATH).convert("RGBA").resize((px(logo_dp), px(logo_dp)), Image.LANCZOS)
    paste_rgba(canvas, logo, (lx, ly))

    f_brand = font_sans(10.5, 500)
    draw_tracked(
        d,
        (lx + px(logo_dp + 10), cy),
        "SUBSCRIPTION TRACKER",
        f_brand,
        C_INK,
        tracking_dp=1.85,
        anchor_y="lm",
    )

    f_right = font_sans(9.8, 500)
    rx = W - px(22)
    rw = tracked_width(d, right_label, f_right, 1.55)
    draw_tracked(d, (rx, cy), right_label, f_right, C_MUTED, tracking_dp=1.55, align="right", anchor_y="lm")
    dot_r = px(2.7)
    dx = int(round(rx - rw - px(8)))
    d.ellipse((dx - dot_r, cy - dot_r, dx + dot_r, cy + dot_r), fill=C_LIME)

    bot_y = top_y + bar_h
    d.line([(0, bot_y), (W, bot_y)], fill=C_HAIR, width=max(1, px(0.9)))
    return bot_y


def draw_bottom_dock(canvas: Image.Image, active_tab: str) -> int:
    dock_h = px(64)
    dock_y = H - dock_h
    d = rgba_draw(canvas)
    d.rectangle((0, dock_y, W, H), fill=C_BAR)
    d.line([(0, dock_y), (W, dock_y)], fill=C_HAIR, width=max(1, px(0.9)))

    col_w = W / 4.0
    f_tab = font_sans(10.0, 500)
    f_tab_on = font_sans(10.0, 600)

    slots = [(0, "today", "TODAY"), (1, "all", "ALL"), (3, "settings", "SETTINGS")]
    for col_idx, key, label in slots:
        cx = col_w * col_idx + col_w / 2.0
        is_on = key == active_tab
        draw_tracked(
            d,
            (cx, dock_y + px(26)),
            label,
            f_tab_on if is_on else f_tab,
            C_INK if is_on else C_FAINT,
            tracking_dp=1.7,
            align="center",
            anchor_y="lm",
        )
        if is_on:
            r = px(2.1)
            d.ellipse((cx - r, dock_y + px(40) - r, cx + r, dock_y + px(40) + r), fill=C_LIME)

    # Column 2: 45dp warm champagne-ivory '+' FAB
    fab_cx = int(round(col_w * 2 + col_w / 2.0))
    fab_cy = dock_y + dock_h // 2
    fab_r = px(22.0)
    # Soft drop shadow
    sh = Image.new("RGBA", (fab_r * 4, fab_r * 4), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse(
        (fab_r, fab_r + px(3), fab_r * 3, fab_r * 3 + px(3)), fill=(0, 0, 0, 145)
    )
    sh = sh.filter(ImageFilter.GaussianBlur(px(5)))
    paste_rgba(canvas, sh, (fab_cx - fab_r * 2, fab_cy - fab_r * 2))

    d = rgba_draw(canvas)
    d.ellipse((fab_cx - fab_r, fab_cy - fab_r, fab_cx + fab_r, fab_cy + fab_r), fill=C_INK)
    arm = px(6.8)
    sw = max(2, px(1.6))
    d.line([(fab_cx - arm, fab_cy), (fab_cx + arm, fab_cy)], fill=C_DARK_INK, width=sw)
    d.line([(fab_cx, fab_cy - arm), (fab_cx, fab_cy + arm)], fill=C_DARK_INK, width=sw)
    return dock_y


def _rounded_rect_perimeter_points(
    x0: float, y0: float, x1: float, y1: float, r: float, step_px: float = 1.0
) -> List[Tuple[float, float]]:
    r = max(1.0, min(r, (x1 - x0) / 2.0, (y1 - y0) / 2.0))
    pts: List[Tuple[float, float]] = []

    def add_line(ax: float, ay: float, bx: float, by: float) -> None:
        dist = math.hypot(bx - ax, by - ay)
        n = max(1, int(round(dist / step_px)))
        for i in range(n):
            t = i / n
            pts.append((ax + (bx - ax) * t, ay + (by - ay) * t))

    def add_arc(cx: float, cy: float, a0_deg: float, a1_deg: float) -> None:
        arc_len = abs(math.radians(a1_deg - a0_deg)) * r
        n = max(4, int(round(arc_len / step_px)))
        for i in range(n):
            t = i / n
            ang = math.radians(a0_deg + (a1_deg - a0_deg) * t)
            pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))

    add_line(x0 + r, y0, x1 - r, y0)
    add_arc(x1 - r, y0 + r, -90, 0)
    add_line(x1, y0 + r, x1, y1 - r)
    add_arc(x1 - r, y1 - r, 0, 90)
    add_line(x1 - r, y1, x0 + r, y1)
    add_arc(x0 + r, y1 - r, 90, 180)
    add_line(x0, y1 - r, x0, y0 + r)
    add_arc(x0 + r, y0 + r, 180, 270)
    return pts


def draw_dashed_hline(
    draw: ImageDraw.ImageDraw, x0: int, x1: int, y: int, fill: Tuple[int, int, int, int]
) -> None:
    dash = px(3.5)
    gap = px(3.0)
    cx = x0
    w = max(1, px(0.9))
    while cx < x1:
        draw.line([(cx, y), (min(x1, cx + dash), y)], fill=fill, width=w)
        cx += dash + gap


def draw_suede_card(
    canvas: Image.Image,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    style: str = "petrol",
    radius_dp: float = 15.0,
    stitch_inset_dp: float = 5.0,
    strong_stitch: bool = False,
) -> None:
    tex_name, base_rgb, tint_a, border_rgba = SUEDE_STYLES[style]
    cw, ch = x1 - x0, y1 - y0
    rad = px(radius_dp)

    # Contact shadow
    sh_pad = px(12)
    sh = Image.new("RGBA", (cw + sh_pad * 2, ch + sh_pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(
        (sh_pad, sh_pad + px(4), sh_pad + cw, sh_pad + ch + px(4)),
        radius=rad,
        fill=(0, 0, 0, 128),
    )
    sh = sh.filter(ImageFilter.GaussianBlur(px(5.5)))
    paste_rgba(canvas, sh, (x0 - sh_pad, y0 - sh_pad))

    # Textured card surface
    tex_layer = Image.new("RGB", (cw, ch), base_rgb)
    tile = get_tex(tex_name, 220.0)
    tw, th = tile.size
    for ty in range(0, ch, th):
        for tx in range(0, cw, tw):
            tex_layer.paste(tile, (tx, ty))

    td = ImageDraw.Draw(tex_layer, "RGBA")
    # Blend base tone so text contrast is rich & hushed
    td.rectangle((0, 0, cw, ch), fill=(base_rgb[0], base_rgb[1], base_rgb[2], int(round(255 * tint_a))))
    # Subtle top-left sheen -> bottom-right falloff
    for i in range(12):
        by0 = int(ch * i / 12)
        by1 = int(ch * (i + 1) / 12)
        if i < 4:
            td.rectangle((0, by0, cw, by1), fill=(255, 255, 255, (4 - i) * 3))
        elif i > 8:
            td.rectangle((0, by0, cw, by1), fill=(0, 0, 0, (i - 8) * 6))

    card_rgba = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    mask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, cw - 1, ch - 1), radius=rad, fill=255)
    card_rgba.paste(tex_layer.convert("RGBA"), (0, 0), mask)

    cd = ImageDraw.Draw(card_rgba)
    cd.rounded_rectangle(
        (1, 1, cw - 2, ch - 2),
        radius=max(2, rad - 1),
        outline=border_rgba,
        width=max(1, px(0.95)),
    )
    paste_rgba(canvas, card_rgba, (x0, y0))

    # Inset warm champagne dashed stitching
    d = rgba_draw(canvas)
    inset = px(stitch_inset_dp)
    seam_r = max(px(4.0), rad - inset)
    pts = _rounded_rect_perimeter_points(x0 + inset, y0 + inset, x1 - inset, y1 - inset, seam_r)
    dash_len = max(3, px(3.3))
    gap_len = max(3, px(3.0))
    cycle = dash_len + gap_len
    stitch_col = C_STITCH if strong_stitch else C_STITCH_SOFT
    w_s = max(1, px(0.95))
    idx = 0
    n_pts = len(pts)
    while idx < n_pts:
        end = min(n_pts - 1, idx + dash_len)
        if end > idx + 1:
            seg = pts[idx : end + 1]
            seg_sh = [(p[0], p[1] + px(0.5)) for p in seg]
            d.line(seg_sh, fill=(0, 0, 0, 115), width=w_s)
            d.line(seg, fill=stitch_col, width=w_s)
        idx += cycle


def draw_editorial_header(
    canvas: Image.Image,
    y: int,
    left_meta: str,
    right_meta: str,
    title: str,
    side_status: str,
    subtitle_lines: List[str],
) -> int:
    d = rgba_draw(canvas)
    pad_x = px(22)
    f_meta = font_sans(9.6, 500)
    draw_tracked(d, (pad_x, y), left_meta, f_meta, C_MUTED, tracking_dp=1.6)
    draw_tracked(d, (W - pad_x, y), right_meta, f_meta, C_MUTED, tracking_dp=1.6, align="right")

    y += px(18)
    f_h1 = font_serif(46.0, 600)
    d.text((pad_x, y), title, font=f_h1, fill=C_INK)
    tw = d.textlength(title, font=f_h1)
    # Botanical lime period `.` right after title
    d.text((pad_x + tw + px(1), y), ".", font=f_h1, fill=C_LIME)

    if side_status:
        f_side = font_sans(9.8, 500)
        draw_tracked(
            d,
            (W - pad_x, y + px(34)),
            side_status,
            f_side,
            C_SIDE_TEAL,
            tracking_dp=1.55,
            align="right",
        )

    y += px(57)
    f_sub = font_sans(13.2, 400)
    for line in subtitle_lines:
        d.text((pad_x, y), line, font=f_sub, fill=C_MUTED)
        y += px(19.5)
    return y


def draw_sub_row(
    canvas: Image.Image,
    y: int,
    idx_str: str,
    name: str,
    sub_meta: str,
    amt: str,
    when_str: str,
    style: str,
    soon: bool = False,
) -> int:
    pad_x = px(22)
    rh = px(68)
    x0, x1 = pad_x, W - pad_x
    draw_suede_card(canvas, x0, y, x1, y + rh, style=style, radius_dp=14.0, stitch_inset_dp=4.5)

    d = rgba_draw(canvas)
    cy = y + rh // 2

    # Index badge `01`
    bsz = px(23)
    bx0, by0 = x0 + px(15), cy - bsz // 2
    d.rounded_rectangle(
        (bx0, by0, bx0 + bsz, by0 + bsz),
        radius=px(6),
        fill=(0, 0, 0, 68),
        outline=rgba(C_INK, 0.16),
        width=max(1, px(0.8)),
    )
    f_idx = font_sans(9.8, 600)
    d.text((bx0 + bsz / 2.0, cy), idx_str, font=f_idx, fill=rgba(C_INK, 0.78), anchor="mm")

    tx = bx0 + bsz + px(13)
    f_name = font_serif(19.0, 600)
    f_sub = font_sans(11.6, 400)
    d.text((tx, y + px(13)), name, font=f_name, fill=C_INK)
    d.text((tx, y + px(38)), sub_meta, font=f_sub, fill=rgba(C_INK, 0.70))

    rx = x1 - px(16)
    f_amt = font_serif(18.5, 600)
    f_when = font_sans(11.0, 600 if soon else 400)
    d.text((rx, y + px(14)), amt, font=f_amt, fill=C_INK, anchor="ra")
    d.text(
        (rx, y + px(39)),
        when_str,
        font=f_when,
        fill=C_SOON if soon else rgba(C_INK, 0.68),
        anchor="ra",
    )
    return y + rh


def render_today() -> Image.Image:
    canvas = new_felt_screen()
    draw_status_bar(canvas)
    y = draw_topbar(canvas, "4 SUBS") + px(20)

    y = draw_editorial_header(
        canvas,
        y,
        "FRI, 23 OCTOBER",
        "THIS PHONE",
        "Today",
        "1 DUE SOON",
        ["A quiet count of what renews, and when.", "Nothing more, nothing louder."],
    )
    y += px(12)

    # Deep Petrol Suede Hero Card (`#203836` + `card-petrol.jpg`)
    pad_x = px(22)
    hero_h = px(262)
    hx0, hy0, hx1, hy1 = pad_x, y, W - pad_x, y + hero_h
    draw_suede_card(
        canvas, hx0, hy0, hx1, hy1, style="petrol", radius_dp=16.0, stitch_inset_dp=5.5, strong_stitch=True
    )

    d = rgba_draw(canvas)
    ix0, ix1 = hx0 + px(22), hx1 - px(22)
    iy = hy0 + px(22)

    f_lbl = font_sans(9.6, 500)
    draw_tracked(d, (ix0, iy), "SPENDING THIS MONTH", f_lbl, C_PETROL_MUTED, tracking_dp=1.6)
    lw = tracked_width(d, "LIVE", f_lbl, 1.55)
    draw_tracked(d, (ix1, iy), "LIVE", f_lbl, C_INK, tracking_dp=1.55, align="right")
    dot_r = px(2.6)
    d.ellipse(
        (ix1 - lw - px(8) - dot_r, iy + px(5) - dot_r, ix1 - lw - px(8) + dot_r, iy + px(5) + dot_r),
        fill=C_LIME,
    )

    iy += px(18)
    f_big = font_serif(52.0, 600)
    d.text((ix0, iy), "$48.90", font=f_big, fill=C_INK)

    iy += px(58)
    f_gentle = font_sans(12.6, 400)
    d.text(
        (ix0, iy),
        "One renewal in the next seven days. The rest of the",
        font=f_gentle,
        fill=C_PETROL_MUTED,
    )
    d.text((ix0, iy + px(18)), "month is yours.", font=f_gentle, fill=C_PETROL_MUTED)

    iy += px(44)
    draw_dashed_hline(d, ix0, ix1, iy, rgba(C_INK, 0.20))

    iy += px(13)
    mid_x = (ix0 + ix1) // 2 + px(6)
    draw_tracked(d, (ix0, iy), "NEXT RENEWAL", f_lbl, C_PETROL_MUTED, tracking_dp=1.5)
    draw_tracked(d, (mid_x, iy), "DUE IN", f_lbl, C_PETROL_MUTED, tracking_dp=1.5)

    f_col_v = font_serif(20.5, 600)
    f_col_s = font_sans(11.8, 400)
    d.text((ix0, iy + px(16)), "Spotify", font=f_col_v, fill=C_INK)
    d.text((ix0, iy + px(40)), "Sun, 26 October", font=f_col_s, fill=C_PETROL_MUTED)

    d.text((mid_x, iy + px(16)), "3 days", font=f_col_v, fill=C_INK)
    d.text((mid_x, iy + px(40)), "$11.99 / month", font=f_col_s, fill=C_PETROL_MUTED)

    # Recessed sea-teal progress track
    ty = hy1 - px(38)
    th = px(6.5)
    d.rounded_rectangle((ix0, ty, ix1, ty + th), radius=th // 2, fill=(8, 16, 16, 155))
    fill_w = int(round((ix1 - ix0) * 0.65))
    d.rounded_rectangle((ix0, ty, ix0 + fill_w, ty + th), radius=th // 2, fill=(72, 160, 158, 255))

    draw_tracked(
        d, (ix0, ty + px(13)), "OF MONTHLY BUDGET", font_sans(9.2, 500), C_PETROL_MUTED, tracking_dp=1.45
    )
    draw_tracked(
        d, (ix1, ty + px(13)), "65% · $75", font_sans(9.2, 500), C_PETROL_MUTED, tracking_dp=1.35, align="right"
    )

    # 3 Suede Stat Trio Cards: Sea-Teal | Moss-Olive | Camel-Sand
    y = hy1 + px(13)
    gap = px(9)
    tw_card = int(round((W - pad_x * 2 - gap * 2) / 3.0))
    th_card = px(66)
    trio_items = [
        ("teal", "26 Oct", "NEXT RENEWAL"),
        ("olive", "4", "ACTIVE"),
        ("sand", "$586.80", "PER YEAR"),
    ]
    for i, (st_style, val_s, lbl_s) in enumerate(trio_items):
        cx0 = pad_x + i * (tw_card + gap)
        cx1 = (W - pad_x) if i == 2 else (cx0 + tw_card)
        draw_suede_card(canvas, cx0, y, cx1, y + th_card, style=st_style, radius_dp=13.0, stitch_inset_dp=4.0)
        d = rgba_draw(canvas)
        d.text((cx0 + px(11), y + px(12)), val_s, font=font_serif(19.5, 600), fill=C_INK)
        draw_tracked(
            d,
            (cx0 + px(11), y + px(41)),
            lbl_s,
            font_sans(8.4, 500),
            rgba(C_INK, 0.72),
            tracking_dp=1.15,
        )

    # UP NEXT · SOONEST FIRST
    y += th_card + px(22)
    d = rgba_draw(canvas)
    draw_tracked(d, (pad_x, y), "UP NEXT", font_sans(10.2, 500), C_INK, tracking_dp=1.8)
    draw_tracked(
        d, (W - pad_x, y), "SOONEST FIRST", font_sans(9.6, 500), C_WARM_TRAIL, tracking_dp=1.5, align="right"
    )
    draw_dashed_hline(d, pad_x, W - pad_x, y + px(18), rgba(C_INK, 0.16))

    y += px(28)
    y = draw_sub_row(
        canvas, y, "01", "Spotify", "Music · monthly", "$11.99", "in 3 days · 26 Oct", "teal", soon=True
    )
    y += px(9)
    y = draw_sub_row(
        canvas, y, "02", "Netflix", "Streaming · monthly", "$15.49", "in 12 days · 4 Nov", "sand", soon=False
    )

    draw_bottom_dock(canvas, "today")
    return canvas


def render_all() -> Image.Image:
    canvas = new_felt_screen()
    draw_status_bar(canvas)
    y = draw_topbar(canvas, "4 SUBS") + px(20)

    y = draw_editorial_header(
        canvas,
        y,
        "4 SUBSCRIPTIONS",
        "EVERYTHING",
        "All",
        "$48.90 / MO",
        ["Every recurring cost, in one calm list."],
    )
    y += px(12)

    pad_x = px(22)
    # Search box in petrol suede
    sh_h = px(44)
    draw_suede_card(canvas, pad_x, y, W - pad_x, y + sh_h, style="petrol", radius_dp=12.0, stitch_inset_dp=3.8)
    d = rgba_draw(canvas)
    d.text((pad_x + px(15), y + sh_h // 2), "Search…", font=font_sans(14.0, 400), fill=(141, 160, 157, 255), anchor="lm")

    # Filter pills: ALL (active champagne), ACTIVE, DUE SOON, PAUSED
    y += sh_h + px(12)
    fx = pad_x
    pills = [("ALL", True), ("ACTIVE", False), ("DUE SOON", False), ("PAUSED", False)]
    f_pill = font_sans(9.4, 600)
    for p_lbl, is_on in pills:
        pw = int(round(tracked_width(d, p_lbl, f_pill, 1.35) + px(24)))
        ph = px(30)
        if is_on:
            d.rounded_rectangle((fx, y, fx + pw, y + ph), radius=ph // 2, fill=C_INK)
            draw_tracked(
                d, (fx + pw / 2.0, y + ph / 2.0), p_lbl, f_pill, C_DARK_INK, tracking_dp=1.35, align="center", anchor_y="mm"
            )
        else:
            d.rounded_rectangle(
                (fx, y, fx + pw, y + ph),
                radius=ph // 2,
                fill=(27, 40, 40, 220),
                outline=C_STITCH_SOFT,
                width=max(1, px(0.9)),
            )
            draw_tracked(
                d, (fx + pw / 2.0, y + ph / 2.0), p_lbl, f_pill, C_MUTED, tracking_dp=1.35, align="center", anchor_y="mm"
            )
        fx += pw + px(8)

    # Stitched camel-sand totals card
    y += px(42)
    tot_h = px(82)
    draw_suede_card(canvas, pad_x, y, W - pad_x, y + tot_h, style="sand", radius_dp=14.0, stitch_inset_dp=4.5)
    d = rgba_draw(canvas)
    f_tk = font_sans(9.6, 500)
    f_tv = font_serif(18.0, 600)
    draw_tracked(d, (pad_x + px(16), y + px(22)), "MONTHLY TOTAL", f_tk, (200, 187, 165, 255), tracking_dp=1.45, anchor_y="lm")
    d.text((W - pad_x - px(16), y + px(22)), "$48.90", font=f_tv, fill=C_INK, anchor="rm")
    draw_dashed_hline(d, pad_x + px(16), W - pad_x - px(16), y + tot_h // 2, C_STITCH_SOFT)
    draw_tracked(d, (pad_x + px(16), y + px(60)), "YEARLY TOTAL", f_tk, (200, 187, 165, 255), tracking_dp=1.45, anchor_y="lm")
    d.text((W - pad_x - px(16), y + px(60)), "$586.80", font=f_tv, fill=C_INK, anchor="rm")

    # 4 Subscription cards cycling through all 4 ST. icon suede/leather tones
    y += tot_h + px(12)
    entries = [
        ("01", "Spotify", "Music · monthly", "$11.99", "in 3 days · 26 Oct", "teal", True),
        ("02", "Netflix", "Streaming · monthly", "$15.49", "in 12 days · 4 Nov", "sand", False),
        ("03", "iCloud+", "Cloud · monthly", "$2.99", "in 19 days · 11 Nov", "olive", False),
        ("04", "Home Wi-Fi", "Internet · monthly", "$18.43", "in 25 days · 17 Nov", "cognac", False),
    ]
    for idx_s, nm, sm, am, wh, st, sn in entries:
        y = draw_sub_row(canvas, y, idx_s, nm, sm, am, wh, st, soon=sn) + px(9)

    draw_bottom_dock(canvas, "all")
    return canvas


def render_settings() -> Image.Image:
    canvas = new_felt_screen()
    draw_status_bar(canvas)
    y = draw_topbar(canvas, "4 SUBS") + px(20)

    y = draw_editorial_header(
        canvas,
        y,
        "PREFERENCES",
        "VERSION 1.2",
        "Settings",
        "",
        ["A few quiet choices. Nothing else is asked of you."],
    )
    y += px(8)

    pad_x = px(22)
    f_k = font_sans(10.0, 600)
    f_d = font_sans(12.2, 400)
    f_seg = font_sans(11.4, 500)
    f_seg_on = font_sans(11.4, 600)

    # Card 1 (Petrol): CURRENCY
    c1_h = px(132)
    draw_suede_card(canvas, pad_x, y, W - pad_x, y + c1_h, style="petrol", radius_dp=14.0, stitch_inset_dp=4.5)
    d = rgba_draw(canvas)
    ix = pad_x + px(17)
    draw_tracked(d, (ix, y + px(17)), "CURRENCY", f_k, C_INK, tracking_dp=1.65)
    d.text((ix, y + px(37)), "Used across the whole app. Amounts keep their value;", font=f_d, fill=rgba(C_INK, 0.72))
    d.text((ix, y + px(55)), "only the symbol changes.", font=f_d, fill=rgba(C_INK, 0.72))

    # Currency pills: INR, USD (active), EUR, GBP
    cx = ix
    py = y + px(84)
    ph = px(32)
    f_sym = font_unicode_sym(11.4)
    for label, active in [("₹ INR", False), ("$ USD", True), ("€ EUR", False), ("£ GBP", False)]:
        # Use DejaVuSans for ₹/£/€ currency glyph coverage
        use_f = f_seg_on if active else f_sym
        pw = int(round(d.textlength(label, font=use_f) + px(24)))
        if active:
            d.rounded_rectangle((cx, py, cx + pw, py + ph), radius=ph // 2, fill=C_INK)
            d.text((cx + pw / 2.0, py + ph / 2.0), label, font=use_f, fill=C_DARK_INK, anchor="mm")
        else:
            d.rounded_rectangle(
                (cx, py, cx + pw, py + ph),
                radius=ph // 2,
                fill=(8, 12, 12, 115),
                outline=C_STITCH_SOFT,
                width=max(1, px(0.9)),
            )
            d.text((cx + pw / 2.0, py + ph / 2.0), label, font=use_f, fill=rgba(C_INK, 0.78), anchor="mm")
        cx += pw + px(7)

    # Card 2 (Sand): MONTHLY BUDGET
    y += c1_h + px(11)
    c2_h = px(136)
    draw_suede_card(canvas, pad_x, y, W - pad_x, y + c2_h, style="sand", radius_dp=14.0, stitch_inset_dp=4.5)
    d = rgba_draw(canvas)
    draw_tracked(d, (ix, y + px(17)), "MONTHLY BUDGET", f_k, C_INK, tracking_dp=1.65)
    d.text((ix, y + px(37)), "Optional. When set, the card on Today fills towards", font=f_d, fill=rgba(C_INK, 0.72))
    d.text((ix, y + px(55)), "it, quietly and without alarms.", font=f_d, fill=rgba(C_INK, 0.72))

    iy2 = y + px(84)
    ih = px(36)
    d.text((ix, iy2 + ih // 2), "$", font=font_serif(20.0, 600), fill=C_INK, anchor="lm")
    in_x0 = ix + px(20)
    save_w = px(74)
    in_x1 = W - pad_x - px(17) - save_w - px(10)
    d.rounded_rectangle(
        (in_x0, iy2, in_x1, iy2 + ih),
        radius=px(8),
        fill=(8, 12, 12, 125),
        outline=rgba(C_INK, 0.20),
        width=max(1, px(0.9)),
    )
    d.text((in_x0 + px(12), iy2 + ih // 2), "75", font=font_sans(15.0, 500), fill=C_INK, anchor="lm")

    sv_x0 = in_x1 + px(10)
    sv_x1 = W - pad_x - px(17)
    d.rounded_rectangle(
        (sv_x0, iy2, sv_x1, iy2 + ih),
        radius=px(9),
        fill=(12, 18, 18, 140),
        outline=C_STITCH,
        width=max(1, px(0.9)),
    )
    draw_tracked(
        d, ((sv_x0 + sv_x1) / 2.0, iy2 + ih / 2.0), "SAVE", font_sans(9.8, 600), C_INK, tracking_dp=1.5, align="center", anchor_y="mm"
    )

    # Card 3 (Olive): REMIND ME
    y += c2_h + px(11)
    c3_h = px(132)
    draw_suede_card(canvas, pad_x, y, W - pad_x, y + c3_h, style="olive", radius_dp=14.0, stitch_inset_dp=4.5)
    d = rgba_draw(canvas)
    draw_tracked(d, (ix, y + px(17)), "REMIND ME", f_k, C_INK, tracking_dp=1.65)
    d.text((ix, y + px(37)), "The usual reminder for new subscriptions, at 9 in", font=f_d, fill=rgba(C_INK, 0.72))
    d.text((ix, y + px(55)), "the morning. Each subscription can choose its own.", font=f_d, fill=rgba(C_INK, 0.72))

    rx = ix
    ry = y + px(84)
    for label, active in [("On the day", False), ("1 day before", False), ("3 days before", True)]:
        use_f = f_seg_on if active else f_seg
        pw = int(round(d.textlength(label, font=use_f) + px(24)))
        if active:
            d.rounded_rectangle((rx, ry, rx + pw, ry + ph), radius=ph // 2, fill=C_INK)
            d.text((rx + pw / 2.0, ry + ph / 2.0), label, font=use_f, fill=C_DARK_INK, anchor="mm")
        else:
            d.rounded_rectangle(
                (rx, ry, rx + pw, ry + ph),
                radius=ph // 2,
                fill=(8, 12, 12, 115),
                outline=C_STITCH_SOFT,
                width=max(1, px(0.9)),
            )
            d.text((rx + pw / 2.0, ry + ph / 2.0), label, font=use_f, fill=rgba(C_INK, 0.78), anchor="mm")
        rx += pw + px(7)

    # Card 4 (Teal): NOTIFICATIONS (visible before dock)
    y += c3_h + px(11)
    c4_h = px(112)
    if y + c4_h < H - px(68):
        draw_suede_card(canvas, pad_x, y, W - pad_x, y + c4_h, style="teal", radius_dp=14.0, stitch_inset_dp=4.5)
        d = rgba_draw(canvas)
        draw_tracked(d, (ix, y + px(17)), "NOTIFICATIONS", f_k, C_INK, tracking_dp=1.65)
        d.text((ix, y + px(37)), "One gentle reminder before each renewal at 9 AM.", font=f_d, fill=rgba(C_INK, 0.72))
        btn_y = y + px(64)
        btn_w = px(164)
        btn_h = px(34)
        d.rounded_rectangle(
            (ix, btn_y, ix + btn_w, btn_y + btn_h),
            radius=px(9),
            fill=(12, 18, 18, 140),
            outline=C_STITCH,
            width=max(1, px(0.9)),
        )
        draw_tracked(
            d,
            (ix + btn_w / 2.0, btn_y + btn_h / 2.0),
            "ENABLE REMINDERS",
            font_sans(9.4, 600),
            C_INK,
            tracking_dp=1.4,
            align="center",
            anchor_y="mm",
        )

    draw_bottom_dock(canvas, "settings")
    return canvas


def save_outputs(name: str, master: Image.Image) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    img_780 = master.resize((780, 1688), Image.LANCZOS)
    img_400 = master.resize((400, 866), Image.LANCZOS)

    p_png = OUT_DIR / f"{name}.png"
    p_780 = OUT_DIR / f"{name}-780.webp"
    p_400 = OUT_DIR / f"{name}-400.webp"
    p_svg = OUT_DIR / f"{name}.svg"

    img_780.save(p_png, "PNG", optimize=True)
    img_780.save(p_780, "WEBP", quality=92, method=6)
    img_400.save(p_400, "WEBP", quality=90, method=6)

    # Also update legacy .svg path with embedded 780w WebP so any cached .svg URL shows v1.2.0
    buf = io.BytesIO()
    img_780.save(buf, "WEBP", quality=90, method=6)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    svg_str = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="866" '
        'viewBox="0 0 780 1688" role="img">\n'
        f'  <image width="780" height="1688" href="data:image/webp;base64,{b64}"/>\n'
        "</svg>\n"
    )
    p_svg.write_text(svg_str, encoding="utf-8")

    print(f"wrote {p_png.relative_to(ROOT)}, {p_780.relative_to(ROOT)}, {p_400.relative_to(ROOT)}, {p_svg.relative_to(ROOT)}")


def main() -> None:
    save_outputs("today", render_today())
    save_outputs("all", render_all())
    save_outputs("settings", render_settings())


if __name__ == "__main__":
    main()
