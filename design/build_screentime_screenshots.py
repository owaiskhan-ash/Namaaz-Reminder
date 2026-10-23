#!/usr/bin/env python3
"""Render crisp, retina 1:1 Screen Time Reminder v1.2.3 screenshots for the Just Apps website.

Matches `owaiskhan-ash/ScreenTime-Reminder` v1.2.3 (`Theme.kt`, `Materials.kt`,
`Components.kt`, `TodayScreen.kt`, `BreakOverlay.kt`, `InsightsScreen.kt`,
`SettingsScreen.kt`, and `preview/materials.css`):
  - Charcoal felt dark surface (#171B19) & subtle nav/suede (#282F29)
  - Transparent-base `ST` leather & suede icon (`design/source/ST-icon.png`)
  - Cyan leather Hero & 20·20·20 cards (#03B1C2) with 9dp-inset dark teal
    dashed stitching (#102C2C @ 68% over subtle black recess)
  - Cyan switches & segmented active states (#03B1C2 with #102C2C ink)

Outputs in `docs/assets/screentime/`:
  - today-{400,780}.webp + today.png
  - break-{400,780}.webp + break.png
  - week-{400,780}.webp + week.png
  - settings-{400,780}.webp + settings.png

Run:  python3 design/build_screentime_screenshots.py
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ST_LOGO_PATH = ROOT / "design" / "source" / "ST-icon.png"
FONTS_DIR = ROOT / "docs" / "assets" / "fonts"
OUT_DIR = ROOT / "docs" / "assets" / "screentime"

# Render at 3x of 390x844 (1170x2532), then downsample with LANCZOS to 780x1688 and 400x866
S = 3
W, H = 390 * S, 844 * S

# Exact v1.2.3 DarkPalette + IconBlue tokens (`Theme.kt` & `preview/materials.css`)
C_BG = (23, 27, 25, 255)             # #171B19 charcoal felt
C_SUBTLE = (40, 47, 41, 255)         # #282F29 bottom nav / break suede
C_FG = (247, 242, 232, 255)          # #F7F2E8 warm ivory ink
C_MUTED = (190, 183, 168, 255)       # #BEB7A8
C_FAINT = (157, 150, 136, 255)       # #9D9688
C_LINE = (247, 242, 232, 48)         # rgba(247,242,232,0.19)
C_CARD = (3, 177, 194, 255)          # #03B1C2 IconBlue cyan leather
C_CARD_TOP = (8, 186, 203, 255)      # subtle top-lit cyan leather sheen
C_CARD_BOT = (2, 166, 183, 255)      # subtle lower cyan leather falloff
C_CARD_FG = (16, 44, 44, 255)        # #102C2C deep teal ink
C_CARD_MUTED = (23, 61, 64, 255)     # #173D40
C_CARD_LINE = (16, 44, 44, 64)       # rgba(16,44,44,0.25)
C_STITCH_INK = (16, 44, 44, 174)     # #102C2C @ 68%
C_STITCH_GROOVE = (0, 0, 0, 96)      # recessed seam shadow


def px(dp: float) -> int:
    return int(round(dp * S))


def rgba(rgb: Tuple[int, int, int, int], alpha: float) -> Tuple[int, int, int, int]:
    return (rgb[0], rgb[1], rgb[2], int(round(255 * alpha)))


def rgba_draw(canvas: Image.Image) -> ImageDraw.ImageDraw:
    return ImageDraw.Draw(canvas, "RGBA")


def paste_rgba(canvas: Image.Image, layer: Image.Image, xy: Tuple[int, int]) -> None:
    canvas.paste(layer, xy, layer)


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


def font_mono(size_dp: float, bold: bool = False) -> ImageFont.FreeTypeFont:
    return font_sans(size_dp, 600 if bold else 400)


def _glyph_ink_metrics(
    text: str, f_hi: ImageFont.FreeTypeFont, base_y: int, anchor_y: str, tracking_px: float, space_px: float
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
    t_hi = (tracking_dp + 0.55) * S * hs
    sp_hi = font.size * hs * 0.34
    _, total_hi = _glyph_ink_metrics(text, f_hi, 100, "la", t_hi, sp_hi)
    return total_hi / hs


def draw_tracked(
    draw: ImageDraw.ImageDraw,
    xy: Tuple[float, float],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: Tuple[int, int, int, int],
    tracking_dp: float = 1.4,
    align: str = "left",
    anchor_y: str = "la",
) -> float:
    if not text:
        return 0.0
    hs = 3
    f_hi = ImageFont.truetype(font.path, font.size * hs)
    t_hi = (tracking_dp + 0.55) * S * hs
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
    """Create a 1170x2532 charcoal felt RGB canvas with subtle top-lit falloff."""
    canvas = Image.new("RGB", (W, H), C_BG[:3])
    d = rgba_draw(canvas)
    # Very gentle vertical ambient falloff (subtle, clean felt surface)
    for step in range(24):
        y0 = int(H * step / 24)
        y1 = int(H * (step + 1) / 24)
        if step < 8:
            a = int(round((8 - step) * 1.1))
            d.rectangle((0, y0, W, y1), fill=(255, 255, 255, a))
        elif step > 16:
            a = int(round((step - 16) * 1.6))
            d.rectangle((0, y0, W, y1), fill=(0, 0, 0, a))
    return canvas


def draw_status_bar(canvas: Image.Image) -> None:
    """Subtle Android status bar row (0..28dp)."""
    d = rgba_draw(canvas)
    f_time = font_sans(11.5, 600)
    d.text((px(24), px(9)), "8:42", font=f_time, fill=rgba(C_FG, 0.82))

    # Signal bars + wifi + battery on right
    rx = W - px(24)
    # Battery pill
    bw, bh = px(18), px(9.5)
    bx, by = rx - bw, px(11)
    d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=px(2.2), outline=rgba(C_FG, 0.72), width=max(1, px(0.9)))
    d.rectangle((bx + px(2), by + px(2), bx + bw - px(4), by + bh - px(2)), fill=rgba(C_FG, 0.80))
    d.rectangle((bx + bw, by + px(2.8), bx + bw + px(1.6), by + bh - px(2.8)), fill=rgba(C_FG, 0.72))

    # Cellular 4 bars
    sx = bx - px(20)
    for i in range(4):
        bar_h = px(3.2 + i * 1.8)
        x0 = sx + i * px(3.6)
        y1 = by + bh
        d.rounded_rectangle(
            (x0, y1 - bar_h, x0 + px(2.2), y1),
            radius=px(0.8),
            fill=rgba(C_FG, 0.80 if i < 3 else 0.42),
        )


def paste_st_logo(canvas: Image.Image, x: int, y: int, size_dp: float) -> None:
    sz = px(size_dp)
    logo = Image.open(ST_LOGO_PATH).convert("RGBA").resize((sz, sz), Image.LANCZOS)
    paste_rgba(canvas, logo, (x, y))


def draw_top_bar(canvas: Image.Image, status_text: str = "LIVE", live_dot: bool = True) -> int:
    """Draw Screen Time Reminder v1.2.3 TopBar; returns bottom y in px."""
    top_y = px(30)
    bar_h = px(52)
    cy = top_y + bar_h // 2

    logo_dp = 29
    lx = px(22)
    ly = cy - px(logo_dp) // 2
    paste_st_logo(canvas, lx, ly, logo_dp)

    d = rgba_draw(canvas)
    f_brand = font_sans(10.0, 600)
    draw_tracked(
        d,
        (lx + px(logo_dp + 10), cy),
        "SCREEN TIME REMINDER",
        f_brand,
        C_FG,
        tracking_dp=1.55,
        anchor_y="lm",
    )

    f_status = font_sans(9.8, 500)
    sw = tracked_width(d, status_text, f_status, 1.25)
    rx = W - px(22)
    draw_tracked(
        d,
        (rx, cy),
        status_text,
        f_status,
        C_MUTED,
        tracking_dp=1.25,
        align="right",
        anchor_y="lm",
    )
    if live_dot:
        dot_r = px(2.6)
        dx = int(round(rx - sw - px(8)))
        d.ellipse((dx - dot_r, cy - dot_r, dx + dot_r, cy + dot_r), fill=C_CARD)

    bot_y = top_y + bar_h
    d.line([(0, bot_y), (W, bot_y)], fill=C_LINE, width=max(1, px(0.8)))
    return bot_y


def draw_bottom_nav(canvas: Image.Image, active_tab: str) -> int:
    """Draw v1.2.3 3-tab BottomNav on #282F29 subtle felt; returns top y in px."""
    nav_h = px(58)
    nav_y = H - nav_h
    d = rgba_draw(canvas)
    d.rectangle((0, nav_y, W, H), fill=C_SUBTLE)
    d.line([(0, nav_y), (W, nav_y)], fill=C_LINE, width=max(1, px(0.8)))

    tabs = [("today", "TODAY"), ("week", "WEEK"), ("settings", "SETTINGS")]
    col_w = W / 3.0
    f_active = font_sans(10.2, 600)
    f_idle = font_sans(10.2, 500)

    for idx, (key, label) in enumerate(tabs):
        cx = col_w * idx + col_w / 2.0
        selected = key == active_tab
        ty = nav_y + px(24)
        draw_tracked(
            d,
            (cx, ty),
            label,
            f_active if selected else f_idle,
            C_FG if selected else C_FAINT,
            tracking_dp=1.45,
            align="center",
            anchor_y="lm",
        )
        dot_r = px(1.8)
        dy = nav_y + px(38)
        if selected:
            d.ellipse((cx - dot_r, dy - dot_r, cx + dot_r, dy + dot_r), fill=C_CARD)

    return nav_y


def _rounded_rect_perimeter_points(
    x0: float, y0: float, x1: float, y1: float, r: float, step_px: float = 1.5
) -> List[Tuple[float, float]]:
    """Sample points evenly around a rounded rectangle perimeter."""
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


def draw_stitched_cyan_card(
    canvas: Image.Image, x0: int, y0: int, x1: int, y1: int, corner_dp: float = 22.0
) -> None:
    """Render #03B1C2 cyan leather card with soft top rim & 9dp-inset dark teal stitching."""
    cw, ch = x1 - x0, y1 - y0
    rad = px(corner_dp)

    # Soft external contact shadow
    sh_pad = px(14)
    sh = Image.new("RGBA", (cw + sh_pad * 2, ch + sh_pad * 2), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle(
        (sh_pad, sh_pad + px(4), sh_pad + cw, sh_pad + ch + px(4)),
        radius=rad,
        fill=(0, 0, 0, 108),
    )
    sh = sh.filter(ImageFilter.GaussianBlur(px(6)))
    paste_rgba(canvas, sh, (x0 - sh_pad, y0 - sh_pad))

    # Card body with smooth vertical top-lit leather ramp
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    mask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, cw - 1, ch - 1), radius=rad, fill=255)

    grad = Image.new("RGBA", (cw, ch), C_CARD)
    gd = ImageDraw.Draw(grad)
    for row in range(ch):
        t = row / max(1, ch - 1)
        r_c = int(round(C_CARD_TOP[0] * (1 - t) + C_CARD_BOT[0] * t))
        g_c = int(round(C_CARD_TOP[1] * (1 - t) + C_CARD_BOT[1] * t))
        b_c = int(round(C_CARD_TOP[2] * (1 - t) + C_CARD_BOT[2] * t))
        gd.line([(0, row), (cw, row)], fill=(r_c, g_c, b_c, 255))

    card.paste(grad, (0, 0), mask)

    # Outer rim highlight (`rgba(255,255,255,0.14)`)
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle(
        (1, 1, cw - 2, ch - 2),
        radius=max(2, rad - 1),
        outline=(255, 255, 255, 40),
        width=max(1, px(0.85)),
    )

    paste_rgba(canvas, card, (x0, y0))

    # 9dp-inset dashed dark teal stitched seam (`Materials.kt`: inset = 9.dp, 3dp dash / 3dp gap)
    d = rgba_draw(canvas)
    inset = px(9.0)
    seam_r = max(px(4.0), rad - inset)
    pts = _rounded_rect_perimeter_points(
        x0 + inset, y0 + inset, x1 - inset, y1 - inset, seam_r, step_px=1.0
    )
    dash_len = max(3, px(3.2))
    gap_len = max(3, px(3.0))
    cycle = dash_len + gap_len
    w_groove = max(1, px(0.95))
    w_thread = max(1, px(0.85))
    n_pts = len(pts)
    idx = 0
    while idx < n_pts:
        end = min(n_pts - 1, idx + dash_len)
        if end > idx + 1:
            seg = pts[idx : end + 1]
            seg_shadow = [(p[0], p[1] + px(0.45)) for p in seg]
            d.line(seg_shadow, fill=C_STITCH_GROOVE, width=w_groove)
            d.line(seg, fill=C_STITCH_INK, width=w_thread)
        idx += cycle


def draw_eyebrow_and_headline(
    canvas: Image.Image,
    y: int,
    left_eyebrow: str,
    right_eyebrow: str,
    title: str,
    subtitle: str,
    title_dp: float = 38.0,
) -> int:
    d = rgba_draw(canvas)
    pad_x = px(22)
    f_eye = font_mono(9.6, bold=False)
    draw_tracked(d, (pad_x, y), left_eyebrow, f_eye, C_FAINT, tracking_dp=1.25)
    if right_eyebrow:
        draw_tracked(
            d, (W - pad_x, y), right_eyebrow, f_eye, C_FAINT, tracking_dp=1.25, align="right"
        )

    y += px(18)
    f_head = font_serif(title_dp, 600)
    d.text((pad_x, y), title, font=f_head, fill=C_FG)

    y += px(title_dp + 7)
    f_sub = font_sans(13.5, 400)
    # Wrap subtitle cleanly if multiline
    max_w = W - pad_x * 2
    words = subtitle.split()
    lines: List[str] = []
    cur = ""
    for w in words:
        cand = f"{cur} {w}".strip()
        if d.textlength(cand, font=f_sub) <= max_w:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)

    for line in lines:
        d.text((pad_x, y), line, font=f_sub, fill=C_MUTED)
        y += px(19.5)

    return y


def draw_section_header(canvas: Image.Image, y: int, title: str, trailing: str = "") -> int:
    d = rgba_draw(canvas)
    pad_x = px(22)
    f_sec = font_sans(10.0, 600)
    f_tr = font_mono(9.6, bold=False)
    draw_tracked(d, (pad_x, y), title, f_sec, C_MUTED, tracking_dp=1.5)
    if trailing:
        draw_tracked(d, (W - pad_x, y), trailing, f_tr, C_FAINT, tracking_dp=1.2, align="right")
    return y + px(22)


def draw_toggle_switch(canvas: Image.Image, right_x: int, cy: int, checked: bool) -> None:
    """Draw v1.2.3 44x26dp #03B1C2 toggle switch with 20dp #F7F2E8 thumb."""
    d = rgba_draw(canvas)
    sw, sh = px(44), px(26)
    x0 = right_x - sw
    y0 = cy - sh // 2
    track_fill = C_CARD if checked else C_SUBTLE
    d.rounded_rectangle((x0, y0, x0 + sw, y0 + sh), radius=sh // 2, fill=track_fill)
    if not checked:
        d.rounded_rectangle(
            (x0, y0, x0 + sw, y0 + sh), radius=sh // 2, outline=C_LINE, width=max(1, px(0.9))
        )
    thumb_d = px(20)
    inset = px(3)
    tx = (x0 + sw - inset - thumb_d) if checked else (x0 + inset)
    ty = y0 + inset
    # Soft thumb shadow
    d.ellipse((tx, ty + px(1), tx + thumb_d, ty + thumb_d + px(1)), fill=(0, 0, 0, 55))
    d.ellipse((tx, ty, tx + thumb_d, ty + thumb_d), fill=C_FG)


def render_today() -> Image.Image:
    canvas = new_felt_screen()
    draw_status_bar(canvas)
    y = draw_top_bar(canvas, "LIVE", live_dot=True) + px(20)

    y = draw_eyebrow_and_headline(
        canvas,
        y,
        "FRI, 23 OCTOBER",
        "THIS PHONE",
        "Today",
        "A live count of the time you spend looking.",
    )
    y += px(14)

    # Stitched #03B1C2 Cyan Leather Hero Card
    pad_x = px(22)
    card_h = px(244)
    cx0, cy0, cx1, cy1 = pad_x, y, W - pad_x, y + card_h
    draw_stitched_cyan_card(canvas, cx0, cy0, cx1, cy1, corner_dp=22.0)

    d = rgba_draw(canvas)
    ix0, ix1 = cx0 + px(24), cx1 - px(24)
    iy = cy0 + px(23)

    f_card_lbl = font_sans(9.8, 600)
    draw_tracked(d, (ix0, iy), "TIME ON SCREEN TODAY", f_card_lbl, C_CARD_MUTED, tracking_dp=1.45)

    # LIVE pill dot inside card
    live_w = tracked_width(d, "LIVE", f_card_lbl, 1.35)
    draw_tracked(d, (ix1, iy), "LIVE", f_card_lbl, C_CARD_MUTED, tracking_dp=1.35, align="right")
    dot_r = px(2.5)
    dot_cx = int(round(ix1 - live_w - px(7.5)))
    dot_cy = iy + px(5.5)
    d.ellipse((dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r), fill=C_CARD_FG)

    # Big hero timer
    iy += px(20)
    f_hero_num = font_mono(40.0, bold=False)
    d.text((ix0 - px(1), iy), "2:44:37", font=f_hero_num, fill=C_CARD_FG)

    iy += px(50)
    f_card_sub = font_sans(12.8, 500)
    d.text((ix0, iy), "Since midnight, across every app.", font=f_card_sub, fill=C_CARD_MUTED)

    iy += px(26)
    d.line([(ix0, iy), (ix1, iy)], fill=C_CARD_LINE, width=max(1, px(0.9)))

    # CONTINUOUS | NEXT NUDGE IN
    iy += px(14)
    mid_x = (ix0 + ix1) // 2 + px(6)
    draw_tracked(d, (ix0, iy), "CONTINUOUS", f_card_lbl, C_CARD_MUTED, tracking_dp=1.35)
    draw_tracked(d, (mid_x, iy), "NEXT NUDGE IN", f_card_lbl, C_CARD_MUTED, tracking_dp=1.35)

    iy += px(18)
    f_sub_timer = font_mono(17.5, bold=False)
    d.text((ix0, iy), "00:44:16", font=f_sub_timer, fill=C_CARD_FG)
    d.text((mid_x, iy), "00:00:44", font=f_sub_timer, fill=C_CARD_FG)

    # Daily limit progress bar
    iy += px(32)
    bar_h = max(2, px(2.2))
    d.rounded_rectangle((ix0, iy, ix1, iy + bar_h), radius=bar_h // 2, fill=C_CARD_LINE)
    fill_x = ix0 + int(round((ix1 - ix0) * 0.55))
    d.rounded_rectangle((ix0, iy, fill_x, iy + bar_h), radius=bar_h // 2, fill=C_CARD_FG)

    iy += px(9)
    f_lim = font_mono(9.4, bold=False)
    draw_tracked(d, (ix0, iy), "5H DAILY LIMIT", f_lim, C_CARD_MUTED, tracking_dp=1.15)
    draw_tracked(d, (ix1, iy), "55%", f_lim, C_CARD_MUTED, tracking_dp=1.0, align="right")

    # 3-column StatRow: 6:40 AM | 42 | 2
    y = cy1 + px(22)
    col_w = (W - pad_x * 2) / 3.0
    stats = [("6:40 AM", "FIRST UNLOCK"), ("42", "UNLOCKS"), ("2", "BREAKS")]
    f_stat_v = font_mono(16.5, bold=False)
    f_stat_l = font_sans(9.5, 500)
    for i, (val, lbl) in enumerate(stats):
        sx = pad_x + int(round(col_w * i))
        if i > 0:
            d.line(
                [(sx - px(10), y + px(2)), (sx - px(10), y + px(38))],
                fill=C_LINE,
                width=max(1, px(0.8)),
            )
        d.text((sx, y), val, font=f_stat_v, fill=C_FG)
        draw_tracked(d, (sx, y + px(25)), lbl, f_stat_l, C_FAINT, tracking_dp=1.25)

    # YOUR RHYTHM · 24 HOURS
    y += px(56)
    y = draw_section_header(canvas, y, "YOUR RHYTHM", "24 HOURS")

    hours = [0, 0, 0, 0, 0, 1, 3, 8, 13, 10, 8, 11, 7, 5, 8, 12, 10, 7, 11, 20, 30, 0, 0, 0]
    chart_h = px(74)
    chart_bottom = y + chart_h
    avail_w = W - pad_x * 2
    gap = px(3.0)
    bw = (avail_w - gap * 23) / 24.0
    max_v = 30.0
    for hr, mins in enumerate(hours):
        bx0 = pad_x + hr * (bw + gap)
        bx1 = bx0 + bw
        bh = max(px(2.0), int(round((mins / max_v) * chart_h)))
        by0 = chart_bottom - bh
        if hr == 20:
            col = C_CARD
        elif mins > 0:
            col = rgba(C_CARD, 0.35)
        else:
            col = C_LINE
        d.rounded_rectangle((bx0, by0, bx1, chart_bottom), radius=px(1.5), fill=col)

    y = chart_bottom + px(7)
    f_tick = font_mono(9.2, bold=False)
    ticks = [("00", 0.0), ("06", 0.25), ("12", 0.50), ("18", 0.75), ("24", 1.0)]
    for t_lbl, frac in ticks:
        tx = pad_x + avail_w * frac
        al = "left" if frac == 0 else ("right" if frac == 1.0 else "center")
        draw_tracked(d, (tx, y), t_lbl, f_tick, C_FAINT, tracking_dp=0.6, align=al)

    y += px(18)
    f_cap = font_sans(11.8, 400)
    d.text((pad_x, y), "Screen-on minutes by hour, since midnight.", font=f_cap, fill=C_MUTED)

    # TOP APPS · TODAY
    y += px(30)
    y = draw_section_header(canvas, y, "TOP APPS", "TODAY")
    f_rank = font_mono(10.0, bold=False)
    f_app = font_sans(14.0, 500)
    f_dur = font_mono(11.8, bold=False)
    d.text((pad_x, y + px(2)), "01", font=f_rank, fill=C_FAINT)
    ax0 = pad_x + px(28)
    d.text((ax0, y - px(1)), "Instagram", font=f_app, fill=C_FG)
    d.text((W - pad_x, y + px(1)), "48m", font=f_dur, fill=C_MUTED, anchor="ra")
    bar_y = y + px(23)
    d.rounded_rectangle((ax0, bar_y, W - pad_x, bar_y + px(2)), radius=px(1), fill=C_CARD)

    draw_bottom_nav(canvas, "today")
    return canvas


def render_break() -> Image.Image:
    canvas = new_felt_screen()
    draw_status_bar(canvas)
    d = rgba_draw(canvas)

    pad_x = px(22)
    top_y = px(38)
    cy = top_y + px(18)

    # Top row: ST logo + BREAK | 36dp circle close button
    paste_st_logo(canvas, pad_x, cy - px(14), 28)
    f_lbl = font_sans(10.0, 600)
    draw_tracked(
        d, (pad_x + px(38), cy), "BREAK", f_lbl, C_MUTED, tracking_dp=1.6, anchor_y="lm"
    )

    close_r = px(18)
    ccx = W - pad_x - close_r
    d.ellipse(
        (ccx - close_r, cy - close_r, ccx + close_r, cy + close_r),
        fill=rgba(C_SUBTLE, 0.55),
        outline=C_LINE,
        width=max(1, px(0.9)),
    )
    cr = px(4.6)
    d.line([(ccx - cr, cy - cr), (ccx + cr, cy + cr)], fill=C_FG, width=max(2, px(1.4)))
    d.line([(ccx + cr, cy - cr), (ccx - cr, cy + cr)], fill=C_FG, width=max(2, px(1.4)))

    y = top_y + px(54)
    y = draw_eyebrow_and_headline(
        canvas,
        y,
        "STEP AWAY",
        "",
        "Look up.",
        "You have been on screen for 44m. Give your eyes five minutes of distance.",
        title_dp=44.0,
    )

    # 204dp circular break timer ring
    ring_y = y + px(24)
    ring_d = px(202)
    rcx = W // 2
    rcy = ring_y + ring_d // 2
    rr = ring_d // 2
    d.ellipse(
        (rcx - rr, rcy - rr, rcx + rr, rcy + rr),
        outline=C_LINE,
        width=max(2, px(1.6)),
    )
    # Subtle cyan ready indicator dot at 12 o'clock on the ring
    dot_r = px(3.0)
    d.ellipse((rcx - dot_r, rcy - rr - dot_r, rcx + dot_r, rcy - rr + dot_r), fill=C_CARD)

    f_timer = font_mono(34.0, bold=False)
    d.text((rcx, rcy - px(6)), "05:00", font=f_timer, fill=C_FG, anchor="mm")
    f_min = font_sans(9.6, 500)
    draw_tracked(
        d, (rcx, rcy + px(24)), "5 MINUTES", f_min, C_FAINT, tracking_dp=1.5, align="center", anchor_y="mm"
    )

    # Primary cyan button: START A 5-MIN BREAK
    by = ring_y + ring_d + px(28)
    btn_h = px(52)
    btn_r = px(12)
    d.rounded_rectangle((pad_x, by, W - pad_x, by + btn_h), radius=btn_r, fill=C_CARD)
    f_btn_pri = font_sans(11.0, 700)
    draw_tracked(
        d,
        (W / 2.0, by + btn_h / 2.0),
        "START A 5-MIN BREAK",
        f_btn_pri,
        C_CARD_FG,
        tracking_dp=1.45,
        align="center",
        anchor_y="mm",
    )

    # Ghost button: SNOOZE 15 MINUTES
    by2 = by + btn_h + px(10)
    d.rounded_rectangle(
        (pad_x, by2, W - pad_x, by2 + btn_h),
        radius=btn_r,
        outline=C_LINE,
        width=max(1, px(1.0)),
    )
    f_btn_gh = font_sans(11.0, 500)
    draw_tracked(
        d,
        (W / 2.0, by2 + btn_h / 2.0),
        "SNOOZE 15 MINUTES",
        f_btn_gh,
        C_FG,
        tracking_dp=1.45,
        align="center",
        anchor_y="mm",
    )

    # Stitched #03B1C2 20·20·20 leather card (`BreakOverlay.kt`)
    cy0 = by2 + btn_h + px(22)
    cy1 = cy0 + px(78)
    draw_stitched_cyan_card(canvas, pad_x, cy0, W - pad_x, cy1, corner_dp=20.0)
    d = rgba_draw(canvas)
    f_20 = font_mono(13.5, bold=True)
    d.text((pad_x + px(20), (cy0 + cy1) // 2), "20·20·20", font=f_20, fill=C_CARD_FG, anchor="lm")
    f_rule = font_sans(12.2, 500)
    rx0 = pad_x + px(102)
    d.text((rx0, cy0 + px(21)), "Every 20 minutes, look 20 feet away", font=f_rule, fill=C_CARD_MUTED)
    d.text((rx0, cy0 + px(40)), "for 20 seconds.", font=f_rule, fill=C_CARD_MUTED)

    # Footer note
    f_foot = font_sans(9.4, 500)
    draw_tracked(
        d,
        (W / 2.0, H - px(28)),
        "2 BREAKS TODAY · NOTHING LEAVES THIS PHONE",
        f_foot,
        C_FAINT,
        tracking_dp=1.25,
        align="center",
        anchor_y="mm",
    )
    return canvas


def render_week() -> Image.Image:
    canvas = new_felt_screen()
    draw_status_bar(canvas)
    y = draw_top_bar(canvas, "LIVE", live_dot=True) + px(20)

    y = draw_eyebrow_and_headline(
        canvas,
        y,
        "YOUR WEEK",
        "LAST 7 DAYS",
        "Seven days.",
        "The same record, looked at from further back.",
    )
    y += px(14)

    d = rgba_draw(canvas)
    pad_x = px(22)
    f_lbl = font_sans(9.8, 500)
    draw_tracked(d, (pad_x, y), "DAILY AVERAGE", f_lbl, C_FAINT, tracking_dp=1.35)
    draw_tracked(
        d, (W - pad_x, y + px(10)), "DAYS TRACKED", f_lbl, C_FAINT, tracking_dp=1.35, align="right"
    )

    f_avg = font_mono(28.0, bold=False)
    f_days = font_mono(18.0, bold=False)
    d.text((pad_x, y + px(18)), "3h 18m", font=f_avg, fill=C_FG)
    d.text((W - pad_x, y + px(29)), "7/7", font=f_days, fill=C_FG, anchor="ra")

    # 7-day weekly bar chart
    y += px(72)
    week_days = [
        ("SAT", "3:18", 198, False),
        ("SUN", "2:56", 176, False),
        ("MON", "3:34", 214, False),
        ("TUE", "3:09", 189, False),
        ("WED", "4:03", 243, False),
        ("THU", "3:25", 205, False),
        ("FRI", "2:44", 164, True),
    ]
    max_m = 243.0
    avail_w = W - pad_x * 2
    gap = px(8.0)
    bw = (avail_w - gap * 6) / 7.0
    bar_max_h = px(112)
    bar_bot = y + px(20) + bar_max_h

    f_val = font_mono(9.6, bold=False)
    f_val_b = font_mono(9.6, bold=True)
    f_day = font_sans(9.6, 500)
    f_day_b = font_sans(9.6, 700)

    for idx, (day_lbl, dur_lbl, mins, is_today) in enumerate(week_days):
        bx0 = pad_x + idx * (bw + gap)
        bx1 = bx0 + bw
        bcx = (bx0 + bx1) / 2.0
        d.text(
            (bcx, y),
            dur_lbl,
            font=f_val_b if is_today else f_val,
            fill=C_FG if is_today else C_FAINT,
            anchor="ma",
        )
        bh = int(round((mins / max_m) * bar_max_h))
        by0 = bar_bot - bh
        d.rounded_rectangle(
            (bx0, by0, bx1, bar_bot),
            radius=px(4.0),
            fill=C_CARD if is_today else rgba(C_CARD, 0.28),
        )
        draw_tracked(
            d,
            (bcx, bar_bot + px(9)),
            day_lbl,
            f_day_b if is_today else f_day,
            C_FG if is_today else C_FAINT,
            tracking_dp=1.0,
            align="center",
        )

    # DAY BY DAY list
    y = bar_bot + px(38)
    y = draw_section_header(canvas, y, "DAY BY DAY")
    d.line([(pad_x, y - px(6)), (W - pad_x, y - px(6))], fill=C_LINE, width=max(1, px(0.8)))

    rows = [
        ("FRI", "23", "2h 44m", 164, True),
        ("THU", "22", "3h 25m", 205, False),
        ("WED", "21", "4h 3m", 243, False),
        ("TUE", "20", "3h 9m", 189, False),
        ("MON", "19", "3h 34m", 214, False),
        ("SUN", "18", "2h 56m", 176, False),
    ]
    f_rday = font_sans(10.0, 600)
    f_rnum = font_sans(13.5, 500)
    f_rdur = font_mono(12.2, bold=False)
    f_rtoday = font_mono(9.2, bold=False)

    ry = y + px(4)
    for wday, dnum, dur, mins, is_today in rows:
        if ry > H - px(82):
            break
        draw_tracked(
            d,
            (pad_x, ry + px(2)),
            wday,
            f_rday,
            C_FG if is_today else C_FAINT,
            tracking_dp=1.1,
        )
        d.text((pad_x + px(36), ry - px(1)), dnum, font=f_rnum, fill=C_FG)

        if is_today:
            tw = tracked_width(d, "TODAY", f_rtoday, 0.9)
            draw_tracked(
                d, (W - pad_x, ry + px(3)), "TODAY", f_rtoday, C_CARD, tracking_dp=0.9, align="right"
            )
            d.text((W - pad_x - tw - px(9), ry), dur, font=f_rdur, fill=C_FG, anchor="ra")
        else:
            d.text((W - pad_x, ry), dur, font=f_rdur, fill=C_MUTED, anchor="ra")

        pby = ry + px(24)
        d.line([(pad_x, pby), (W - pad_x, pby)], fill=C_LINE, width=max(1, px(1.2)))
        fill_w = int(round((W - pad_x * 2) * (mins / max_m)))
        d.line(
            [(pad_x, pby), (pad_x + fill_w, pby)],
            fill=C_CARD if is_today else rgba(C_CARD, 0.48),
            width=max(2, px(1.8)),
        )
        d.line([(pad_x, ry + px(35)), (W - pad_x, ry + px(35))], fill=rgba(C_FG, 0.08), width=1)
        ry += px(45)

    draw_bottom_nav(canvas, "week")
    return canvas


def draw_segmented_picker(
    canvas: Image.Image, y: int, options: List[str], selected_idx: int
) -> int:
    d = rgba_draw(canvas)
    pad_x = px(22)
    h = px(40)
    x0, x1 = pad_x, W - pad_x
    rad = px(10)

    d.rounded_rectangle((x0, y, x1, y + h), radius=rad, fill=rgba(C_SUBTLE, 0.45), outline=C_LINE, width=max(1, px(0.9)))
    n = len(options)
    cw = (x1 - x0) / n

    # Selected cell highlight
    sx0 = int(round(x0 + cw * selected_idx))
    sx1 = int(round(x0 + cw * (selected_idx + 1)))
    if selected_idx == 0:
        d.rounded_rectangle((sx0, y, sx1 + rad, y + h), radius=rad, fill=C_CARD)
        d.rectangle((sx1, y, sx1 + rad, y + h), fill=C_CARD)
    elif selected_idx == n - 1:
        d.rounded_rectangle((sx0 - rad, y, sx1, y + h), radius=rad, fill=C_CARD)
        d.rectangle((sx0 - rad, y, sx0, y + h), fill=C_CARD)
    else:
        d.rectangle((sx0, y, sx1, y + h), fill=C_CARD)

    f_sel = font_mono(10.5, bold=True)
    f_unsel = font_mono(10.5, bold=False)
    for i, opt in enumerate(options):
        if i > 0 and i != selected_idx and i - 1 != selected_idx:
            lx = int(round(x0 + cw * i))
            d.line([(lx, y + px(6)), (lx, y + h - px(6))], fill=C_LINE, width=max(1, px(0.8)))
        cx = x0 + cw * i + cw / 2.0
        is_sel = i == selected_idx
        draw_tracked(
            d,
            (cx, y + h / 2.0),
            opt,
            f_sel if is_sel else f_unsel,
            C_CARD_FG if is_sel else C_MUTED,
            tracking_dp=0.9,
            align="center",
            anchor_y="mm",
        )
    return y + h


def render_settings() -> Image.Image:
    canvas = new_felt_screen()
    draw_status_bar(canvas)
    y = draw_top_bar(canvas, "LIVE", live_dot=True) + px(20)

    y = draw_eyebrow_and_headline(
        canvas,
        y,
        "PREFERENCES",
        "1.2.3",
        "Settings",
        "A few switches. Nothing buried, nothing extra.",
    )
    y += px(14)

    d = rgba_draw(canvas)
    pad_x = px(22)
    f_title = font_sans(14.5, 500)
    f_desc = font_sans(12.2, 400)
    f_meta = font_mono(9.8, bold=False)

    # SESSIONS & REMINDERS
    y = draw_section_header(canvas, y, "SESSIONS & REMINDERS")
    d.line([(pad_x, y - px(6)), (W - pad_x, y - px(6))], fill=C_LINE, width=max(1, px(0.8)))

    # Row 1: Reminders
    ry = y + px(6)
    d.text((pad_x, ry), "Reminders", font=f_title, fill=C_FG)
    d.text((pad_x, ry + px(22)), "A calm nudge when a screen session runs long.", font=f_desc, fill=C_MUTED)
    draw_toggle_switch(canvas, W - pad_x, ry + px(19), True)
    ry += px(52)
    d.line([(pad_x, ry), (W - pad_x, ry)], fill=C_LINE, width=max(1, px(0.8)))

    # Row 2: Reminder after (30M | 45M | 60M | 90M)
    ry += px(14)
    d.text((pad_x, ry), "Reminder after", font=f_title, fill=C_FG)
    draw_tracked(d, (W - pad_x, ry + px(4)), "45 MIN", f_meta, C_FAINT, tracking_dp=1.0, align="right")
    ry = draw_segmented_picker(canvas, ry + px(28), ["30M", "45M", "60M", "90M"], 1) + px(14)
    d.line([(pad_x, ry), (W - pad_x, ry)], fill=C_LINE, width=max(1, px(0.8)))

    # Row 3: Repeat while still on screen
    ry += px(14)
    d.text((pad_x, ry), "Repeat while still on screen", font=f_title, fill=C_FG)
    d.text((pad_x, ry + px(22)), "Nudge again every 45 minutes if still active.", font=f_desc, fill=C_MUTED)
    draw_toggle_switch(canvas, W - pad_x, ry + px(19), True)
    ry += px(52)
    d.line([(pad_x, ry), (W - pad_x, ry)], fill=C_LINE, width=max(1, px(0.8)))

    # Row 4: Vibrate on reminder
    ry += px(14)
    d.text((pad_x, ry), "Vibrate on reminder", font=f_title, fill=C_FG)
    d.text((pad_x, ry + px(22)), "Sound comes from your notification settings.", font=f_desc, fill=C_MUTED)
    draw_toggle_switch(canvas, W - pad_x, ry + px(19), True)
    ry += px(52)
    d.line([(pad_x, ry), (W - pad_x, ry)], fill=C_LINE, width=max(1, px(0.8)))

    # DAILY LIMIT
    ry += px(22)
    ry = draw_section_header(canvas, ry, "DAILY LIMIT")
    d.line([(pad_x, ry - px(6)), (W - pad_x, ry - px(6))], fill=C_LINE, width=max(1, px(0.8)))

    ry += px(6)
    d.text((pad_x, ry), "Stop nudging me after", font=f_title, fill=C_FG)
    d.text(
        (pad_x, ry + px(22)),
        "A second, firmer reminder when the day passes this line.",
        font=f_desc,
        fill=C_MUTED,
    )
    ry = draw_segmented_picker(canvas, ry + px(48), ["2H", "3H", "5H", "6H", "OFF"], 2) + px(10)
    draw_tracked(d, (pad_x, ry), "TODAY 2H 44M OF 5H", f_meta, C_FAINT, tracking_dp=1.0)

    # APPEARANCE (visible near bottom before BottomNav)
    ry += px(28)
    if ry < H - px(96):
        ry = draw_section_header(canvas, ry, "APPEARANCE")
        d.line([(pad_x, ry - px(6)), (W - pad_x, ry - px(6))], fill=C_LINE, width=max(1, px(0.8)))
        if ry + px(24) < H - px(64):
            d.text((pad_x, ry + px(6)), "Theme", font=f_title, fill=C_FG)
            draw_tracked(
                d, (W - pad_x, ry + px(10)), "DARK", f_meta, C_CARD, tracking_dp=1.0, align="right"
            )

    draw_bottom_nav(canvas, "settings")
    return canvas


def save_outputs(name: str, master: Image.Image) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    img_780 = master.resize((780, 1688), Image.LANCZOS)
    img_400 = master.resize((400, 866), Image.LANCZOS)

    p_png = OUT_DIR / f"{name}.png"
    p_780 = OUT_DIR / f"{name}-780.webp"
    p_400 = OUT_DIR / f"{name}-400.webp"

    img_780.save(p_png, "PNG", optimize=True)
    img_780.save(p_780, "WEBP", quality=92, method=6)
    img_400.save(p_400, "WEBP", quality=90, method=6)
    print(f"wrote {p_png.relative_to(ROOT)}, {p_780.relative_to(ROOT)}, {p_400.relative_to(ROOT)}")


def main() -> None:
    save_outputs("today", render_today())
    save_outputs("break", render_break())
    save_outputs("week", render_week())
    save_outputs("settings", render_settings())


if __name__ == "__main__":
    main()
