#!/usr/bin/env python3
"""Render crisp, retina 1:1 Namaaz Reminder v1.6.2 screenshots for the Just Apps website.

Uses the real APK assets (`app/src/main/res/drawable-xxxhdpi/ic_app_icon.png` and
`app/src/main/res/drawable-nodpi/leather_black_tile.png`) and exact Compose theme
tokens from `Color.kt`, `NamazTopBar.kt`, `HeroCountdownCard.kt`, `PrayerTimeCard.kt`,
`CitySelectionSheet.kt`, and `SettingsSheet.kt`.

Outputs:
  - docs/assets/namaaz/today-{400,780}.webp + today.png
  - docs/assets/namaaz/cities-{400,780}.webp + cities.png
  - docs/assets/namaaz/settings-{400,780}.webp + settings.png
  - docs/assets/namaaz-preview.svg (self-contained high-DPI preview fallback)
"""

from __future__ import annotations

import base64
import io
import math
from pathlib import Path
from typing import Tuple

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
RES_DIR = ROOT / "app" / "src" / "main" / "res"
FONTS_DIR = ROOT / "docs" / "assets" / "fonts"
OUT_DIR = ROOT / "docs" / "assets" / "namaaz"

# Render at 3x of 390x844 (1170x2532), then downsample with LANCZOS to 780x1688 and 400x866
S = 3
W, H = 390 * S, 844 * S

# Exact Color.kt tokens
C_BG = (11, 13, 14, 255)             # #0B0D0E
C_SURFACE = (19, 22, 24, 255)        # #131618
C_SURFACE_VAR = (25, 30, 32, 255)    # #191E20
C_WELL = (9, 11, 12, 255)            # #090B0C
C_NEXT_CARD = (19, 29, 32, 255)      # #131D20
C_BORDER = (37, 43, 46, 255)         # #252B2E
C_TEXT_PRI = (245, 240, 230, 255)    # #F5F0E6
C_TEXT_SEC = (200, 185, 158, 255)    # #C8B99E
C_TEXT_TER = (138, 130, 117, 255)    # #8A8275
C_WARM = (216, 194, 160, 255)        # #D8C2A0
C_CYAN = (0, 188, 200, 255)          # #00BCC8
C_CYAN_SOFT = (122, 214, 220, 255)   # #7AD6DC
C_LIME = (208, 255, 0, 255)          # #D0FF00
C_COGNAC = (185, 87, 45, 255)        # #B9572D
C_CREAM_PILL = (237, 226, 206, 255)  # #EDE2CE
C_CREAM_INK = (23, 20, 17, 255)      # #171411


def px(dp: float) -> int:
    return int(round(dp * S))


def rgba(rgb: Tuple[int, int, int, int], alpha: float) -> Tuple[int, int, int, int]:
    return (rgb[0], rgb[1], rgb[2], int(round(255 * alpha)))


def rgba_draw(canvas: Image.Image) -> ImageDraw.ImageDraw:
    """Return an RGBA-blending draw context over an RGB canvas."""
    return ImageDraw.Draw(canvas, "RGBA")


def paste_rgba(canvas: Image.Image, layer: Image.Image, xy: Tuple[int, int]) -> None:
    canvas.paste(layer, xy, layer)


def font_sans(size_dp: float, weight: int = 500) -> ImageFont.FreeTypeFont:
    w_map = {
        400: "plus-jakarta-sans-latin-400-normal.woff2",
        500: "plus-jakarta-sans-latin-500-normal.woff2",
        600: "plus-jakarta-sans-latin-600-normal.woff2",
        700: "plus-jakarta-sans-latin-700-normal.woff2",
    }
    nearest = min(w_map.keys(), key=lambda k: abs(k - weight))
    return ImageFont.truetype(str(FONTS_DIR / w_map[nearest]), px(size_dp))


def font_mono(size_dp: float) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", px(size_dp))


def font_arabic(size_dp: float) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", px(size_dp))


def shape_ar(text: str) -> str:
    return get_display(arabic_reshaper.reshape(text))


def draw_tracked(
    draw: ImageDraw.ImageDraw,
    xy: Tuple[float, float],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: Tuple[int, int, int, int],
    tracking_dp: float = 0.0,
    anchor: str = "lt",
) -> float:
    t_px = tracking_dp * S
    if abs(t_px) < 0.05:
        draw.text(xy, text, font=font, fill=fill, anchor=anchor)
        bbox = draw.textbbox((0, 0), text, font=font)
        return float(bbox[2] - bbox[0])

    advances = [font.getlength(ch) for ch in text]
    total_w = sum(advances) + t_px * max(0, len(text) - 1)
    x, y = xy
    if anchor.startswith("r"):
        x -= total_w
    elif anchor.startswith("m"):
        x -= total_w / 2.0
    sub_anchor = "l" + anchor[1:]
    cx = x
    for idx, ch in enumerate(text):
        draw.text((cx, y), ch, font=font, fill=fill, anchor=sub_anchor)
        cx += advances[idx] + t_px
    return total_w


def make_leather_canvas() -> Image.Image:
    base = Image.new("RGBA", (W, H), C_BG)
    tile = Image.open(RES_DIR / "drawable-nodpi" / "leather_black_tile.png").convert("RGBA")
    tw, th = int(tile.width * 1.35), int(tile.height * 1.35)
    tile = tile.resize((tw, th), Image.Resampling.LANCZOS)

    grain_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for y in range(0, H, th):
        for x in range(0, W, tw):
            grain_layer.paste(tile, (x, y))

    alpha = grain_layer.split()[3].point(lambda p: int(p * 0.56))
    grain_layer.putalpha(alpha)
    base = Image.alpha_composite(base, grain_layer).convert("RGB")

    gd = rgba_draw(base)
    for y in range(H):
        t = y / max(1, H - 1)
        if t < 0.28:
            a = int(12 * (1.0 - t / 0.28))
            gd.line([(0, y), (W, y)], fill=(255, 250, 240, a))
        elif t > 0.72:
            a = int(40 * ((t - 0.72) / 0.28))
            gd.line([(0, y), (W, y)], fill=(0, 0, 0, a))
    return base


def paste_grain_clipped(
    canvas: Image.Image,
    box: Tuple[int, int, int, int],
    radius: int,
    fill_color: Tuple[int, int, int, int],
    grain_tile: Image.Image,
    grain_alpha: float = 0.28,
    drop_shadow: bool = True,
) -> None:
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0

    if drop_shadow:
        pad = px(14)
        sh = Image.new("RGBA", (bw + pad * 2, bh + pad * 2), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle(
            (pad, pad + px(4), pad + bw, pad + bh + px(4)),
            radius=radius,
            fill=(0, 0, 0, 120),
        )
        sh = sh.filter(ImageFilter.GaussianBlur(px(6)))
        paste_rgba(canvas, sh, (x0 - pad, y0 - pad))

    card = Image.new("RGBA", (bw, bh), fill_color)
    tw, th = grain_tile.size
    gl = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    for gy in range(0, bh, th):
        for gx in range(0, bw, tw):
            gl.paste(grain_tile, (gx, gy))
    ga = gl.split()[3].point(lambda p: int(p * grain_alpha))
    gl.putalpha(ga)
    card = Image.alpha_composite(card, gl).convert("RGB")

    shd = rgba_draw(card)
    for yy in range(bh):
        t = yy / max(1, bh - 1)
        if t < 0.35:
            shd.line([(0, yy), (bw, yy)], fill=(255, 255, 255, int(8 * (1 - t / 0.35))))
        elif t > 0.65:
            shd.line([(0, yy), (bw, yy)], fill=(0, 0, 0, int(26 * ((t - 0.65) / 0.35))))

    mask = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, bw - 1, bh - 1), radius=radius, fill=255)
    clipped = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    clipped.paste(card.convert("RGBA"), (0, 0), mask)
    paste_rgba(canvas, clipped, (x0, y0))


def draw_dashed_rounded_rect(
    draw: ImageDraw.ImageDraw,
    box: Tuple[int, int, int, int],
    radius: int,
    color: Tuple[int, int, int, int],
    width: int,
    dash: int,
    gap: int,
) -> None:
    x0, y0, x1, y1 = box
    pts = []
    steps_arc = 14
    corners = [
        (x1 - radius, y0 + radius, -math.pi / 2, 0),
        (x1 - radius, y1 - radius, 0, math.pi / 2),
        (x0 + radius, y1 - radius, math.pi / 2, math.pi),
        (x0 + radius, y0 + radius, math.pi, 3 * math.pi / 2),
    ]
    edges = [
        ((x0 + radius, y0), (x1 - radius, y0)),
        ((x1, y0 + radius), (x1, y1 - radius)),
        ((x1 - radius, y1), (x0 + radius, y1)),
        ((x0, y1 - radius), (x0, y0 + radius)),
    ]
    for i in range(4):
        pts.append(edges[i][0])
        pts.append(edges[i][1])
        cx, cy, a0, a1 = corners[i]
        for s in range(1, steps_arc):
            ang = a0 + (a1 - a0) * (s / steps_arc)
            pts.append((cx + radius * math.cos(ang), cy + radius * math.sin(ang)))
    pts.append(pts[0])

    dist_acc = 0.0
    cycle = dash + gap
    for i in range(len(pts) - 1):
        ax, ay = pts[i]
        bx, by = pts[i + 1]
        seg_len = math.hypot(bx - ax, by - ay)
        if seg_len < 0.5:
            continue
        pos = 0.0
        while pos < seg_len:
            rem_in_cycle = (dist_acc + pos) % cycle
            if rem_in_cycle < dash:
                d_end = min(seg_len, pos + (dash - rem_in_cycle))
                t0, t1 = pos / seg_len, d_end / seg_len
                draw.line(
                    [(ax + (bx - ax) * t0, ay + (by - ay) * t0),
                     (ax + (bx - ax) * t1, ay + (by - ay) * t1)],
                    fill=color,
                    width=width,
                )
                pos = d_end
            else:
                pos += cycle - rem_in_cycle
        dist_acc += seg_len


def draw_leather_card(
    canvas: Image.Image,
    grain_tile: Image.Image,
    box: Tuple[int, int, int, int],
    radius_dp: float,
    fill_color: Tuple[int, int, int, int] = C_SURFACE,
    border_color: Tuple[int, int, int, int] = C_BORDER,
    border_width_dp: float = 1.0,
    stitch_color: Tuple[int, int, int, int] | None = None,
    drop_shadow: bool = True,
) -> None:
    r = px(radius_dp)
    paste_grain_clipped(canvas, box, r, fill_color, grain_tile, drop_shadow=drop_shadow)
    d = rgba_draw(canvas)
    x0, y0, x1, y1 = box
    d.line([(x0 + r, y0 + px(1)), (x1 - r, y0 + px(1))], fill=(255, 255, 255, 14), width=max(1, px(0.8)))
    d.rounded_rectangle(box, radius=r, outline=border_color, width=max(1, px(border_width_dp)))
    if stitch_color is not None:
        inset = px(4.5)
        draw_dashed_rounded_rect(
            d,
            (x0 + inset, y0 + inset, x1 - inset, y1 - inset),
            max(px(4), r - inset),
            stitch_color,
            width=max(1, px(0.9)),
            dash=px(4.2),
            gap=px(3.4),
        )


def draw_leather_well(
    draw: ImageDraw.ImageDraw,
    box: Tuple[int, int, int, int],
    radius_dp: float = 9.0,
    border_color: Tuple[int, int, int, int] = C_BORDER,
    fill_color: Tuple[int, int, int, int] = C_WELL,
) -> None:
    r = px(radius_dp)
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=r, fill=fill_color)
    draw.line([(x0 + r, y0 + px(1.2)), (x1 - r, y0 + px(1.2))], fill=(0, 0, 0, 120), width=max(1, px(1.0)))
    draw.line([(x0 + r, y1 - px(1.0)), (x1 - r, y1 - px(1.0))], fill=(255, 255, 255, 11), width=max(1, px(0.8)))
    draw.rounded_rectangle(box, radius=r, outline=border_color, width=max(1, px(1.0)))


# --- Crisp vector icons ---
def draw_icon_pin(draw: ImageDraw.ImageDraw, cx: float, cy: float, size_dp: float, color: Tuple[int, int, int, int], filled: bool = False) -> None:
    r = size_dp * S * 0.34
    top_y = cy - size_dp * S * 0.12
    bot_y = cy + size_dp * S * 0.44
    w = max(2, px(1.45))
    pts = []
    for i in range(25):
        ang = math.pi + math.pi * (i / 24.0)
        pts.append((cx + r * math.cos(ang), top_y + r * math.sin(ang)))
    pts.append((cx, bot_y))
    pts.append(pts[0])
    if filled:
        draw.polygon(pts, fill=color)
        draw.ellipse((cx - r * 0.38, top_y - r * 0.38, cx + r * 0.38, top_y + r * 0.38), fill=C_SURFACE)
    else:
        draw.line(pts, fill=color, width=w, joint="curve")
        ir = r * 0.36
        draw.ellipse((cx - ir, top_y - ir, cx + ir, top_y + ir), outline=color, width=max(2, px(1.25)))


def draw_icon_sun(draw: ImageDraw.ImageDraw, cx: float, cy: float, size_dp: float, color: Tuple[int, int, int, int]) -> None:
    r = size_dp * S * 0.22
    w = max(2, px(1.4))
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color, width=w)
    r1 = size_dp * S * 0.33
    r2 = size_dp * S * 0.46
    for i in range(8):
        ang = i * (math.pi / 4.0)
        draw.line(
            [(cx + r1 * math.cos(ang), cy + r1 * math.sin(ang)),
             (cx + r2 * math.cos(ang), cy + r2 * math.sin(ang))],
            fill=color,
            width=w,
        )


def draw_icon_gear(draw: ImageDraw.ImageDraw, cx: float, cy: float, size_dp: float, color: Tuple[int, int, int, int]) -> None:
    w = max(2, px(1.4))
    r_outer = size_dp * S * 0.33
    r_inner = size_dp * S * 0.15
    draw.ellipse((cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer), outline=color, width=w)
    draw.ellipse((cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner), outline=color, width=max(2, px(1.2)))
    for i in range(6):
        ang = i * (math.pi / 3.0)
        draw.line(
            [(cx + r_outer * 0.95 * math.cos(ang), cy + r_outer * 0.95 * math.sin(ang)),
             (cx + size_dp * S * 0.46 * math.cos(ang), cy + size_dp * S * 0.46 * math.sin(ang))],
            fill=color,
            width=max(2, px(1.6)),
        )


def draw_icon_bell(draw: ImageDraw.ImageDraw, cx: float, cy: float, size_dp: float, color: Tuple[int, int, int, int], muted: bool = False) -> None:
    s = size_dp * S
    r = s * 0.27
    top = cy - s * 0.30
    bell_pts = []
    for i in range(19):
        ang = math.pi + math.pi * (i / 18.0)
        bell_pts.append((cx + r * math.cos(ang), top + r + r * math.sin(ang)))
    bell_pts.append((cx + r * 1.28, cy + s * 0.18))
    bell_pts.append((cx - r * 1.28, cy + s * 0.18))
    draw.polygon(bell_pts, fill=color)
    cr = s * 0.09
    draw.pieslice((cx - cr, cy + s * 0.16, cx + cr, cy + s * 0.16 + cr * 2), 0, 180, fill=color)
    draw.ellipse((cx - s * 0.05, top - s * 0.05, cx + s * 0.05, top + s * 0.05), fill=color)
    if muted:
        draw.line(
            [(cx - s * 0.38, cy - s * 0.36), (cx + s * 0.38, cy + s * 0.36)],
            fill=color,
            width=max(2, px(1.6)),
        )


def draw_status_bar(draw: ImageDraw.ImageDraw) -> None:
    draw.text((px(22), px(15)), "9:41", font=font_sans(11.5, 600), fill=C_TEXT_PRI, anchor="lm")
    bx = px(316)
    by = px(19)
    for i, h_dp in enumerate([3.5, 5.5, 7.5, 9.5]):
        x = bx + i * px(3.6)
        draw.rounded_rectangle((x, by - px(h_dp), x + px(2.3), by), radius=px(0.8), fill=C_TEXT_PRI)
    wx, wy = px(338), px(18.5)
    draw.ellipse((wx - px(1.2), wy - px(1.2), wx + px(1.2), wy + px(1.2)), fill=C_TEXT_PRI)
    for r_dp in [4.0, 6.8]:
        r = px(r_dp)
        draw.arc((wx - r, wy - r, wx + r, wy + r), 220, 320, fill=C_TEXT_PRI, width=max(2, px(1.2)))
    bat_x, bat_y = px(350), px(11.2)
    draw.rounded_rectangle((bat_x, bat_y, bat_x + px(18), bat_y + px(9.2)), radius=px(2.2), outline=rgba(C_TEXT_PRI, 0.72), width=max(1, px(1.0)))
    draw.rounded_rectangle((bat_x + px(1.8), bat_y + px(1.8), bat_x + px(14.6), bat_y + px(7.4)), radius=px(1.2), fill=C_TEXT_PRI)
    draw.rounded_rectangle((bat_x + px(18.8), bat_y + px(2.8), bat_x + px(20.0), bat_y + px(6.4)), radius=px(0.8), fill=rgba(C_TEXT_PRI, 0.72))


def draw_top_bar(canvas: Image.Image) -> int:
    """Draws exact v1.6.2 NamazTopBar (34dp transparent NR logo + 32dp spaced leather wells)."""
    y_top = px(36)
    cy = y_top + px(17)

    nr_icon = Image.open(RES_DIR / "drawable-xxxhdpi" / "ic_app_icon.png").convert("RGBA")
    icon_sz = px(34)
    nr_icon = nr_icon.resize((icon_sz, icon_sz), Image.Resampling.LANCZOS)
    paste_rgba(canvas, nr_icon, (px(16), y_top))

    draw = rgba_draw(canvas)
    tx = px(16 + 34 + 11)
    draw_tracked(draw, (tx, y_top + px(4.5)), "NAMAAZ REMINDER", font_sans(13.2, 700), C_TEXT_PRI, tracking_dp=0.85, anchor="lt")
    dot_y = y_top + px(25.5)
    dr = px(2.25)
    draw.ellipse((tx, dot_y - dr, tx + dr * 2, dot_y + dr), fill=rgba(C_COGNAC, 0.88))
    draw_tracked(draw, (tx + px(9.5), dot_y), "MUMBAI, INDIA", font_sans(9.8, 600), C_TEXT_SEC, tracking_dp=0.5, anchor="lm")

    btn_sz = px(32)
    gap = px(10)
    right_edge = W - px(16)
    b3_x0 = right_edge - btn_sz
    b2_x0 = b3_x0 - gap - btn_sz
    b1_x0 = b2_x0 - gap - btn_sz
    by0 = cy - btn_sz // 2

    for bx0, draw_fn in [
        (b1_x0, lambda d, x, y: draw_icon_pin(d, x, y, 15.0, C_TEXT_SEC, filled=False)),
        (b2_x0, lambda d, x, y: draw_icon_sun(d, x, y, 15.0, C_TEXT_SEC)),
        (b3_x0, lambda d, x, y: draw_icon_gear(d, x, y, 15.0, C_TEXT_SEC)),
    ]:
        draw_leather_well(draw, (bx0, by0, bx0 + btn_sz, by0 + btn_sz), radius_dp=9.0, border_color=C_BORDER)
        draw_fn(draw, bx0 + btn_sz / 2.0, by0 + btn_sz / 2.0)

    return y_top + icon_sz + px(10)


def build_base_home_screen() -> Tuple[Image.Image, Image.Image]:
    canvas = make_leather_canvas()
    grain_tile = Image.open(RES_DIR / "drawable-nodpi" / "leather_black_tile.png").convert("RGBA")
    grain_tile = grain_tile.resize((int(grain_tile.width * 1.25), int(grain_tile.height * 1.25)), Image.Resampling.LANCZOS)

    d = rgba_draw(canvas)
    draw_status_bar(d)
    y = draw_top_bar(canvas)

    # 1. DateHeader card
    dh_top = y + px(4)
    dh_bot = dh_top + px(62)
    draw_leather_card(canvas, grain_tile, (px(16), dh_top, W - px(16), dh_bot), radius_dp=14.0)
    d = rgba_draw(canvas)
    draw_icon_pin(d, px(36), dh_top + px(21), 15.0, C_WARM, filled=True)
    draw_tracked(d, (px(48), dh_top + px(21)), "MUMBAI, INDIA", font_sans(13.0, 700), C_TEXT_PRI, tracking_dp=0.65, anchor="lm")
    d.text((W - px(31), dh_top + px(21)), "10 Jumada al-Ula 1448", font=font_sans(10.5, 500), fill=C_TEXT_SEC, anchor="rm")
    d.text((px(31), dh_top + px(43)), "Friday, 23 October 2026", font=font_sans(11.0, 400), fill=C_TEXT_SEC, anchor="lm")
    d.text((W - px(31), dh_top + px(43)), "Univ. of Islamic Sciences", font=font_sans(10.5, 400), fill=rgba(C_TEXT_SEC, 0.72), anchor="rm")

    # 2. HeroCountdownCard (subtle 28% cyan border + faint 14% warm sand stitch matching HeroCountdownCard.kt)
    hc_top = dh_bot + px(12)
    hc_bot = hc_top + px(206)
    draw_leather_card(
        canvas,
        grain_tile,
        (px(16), hc_top, W - px(16), hc_bot),
        radius_dp=20.0,
        fill_color=C_SURFACE,
        border_color=rgba(C_CYAN, 0.30),
        border_width_dp=1.1,
        stitch_color=rgba(C_WARM, 0.16),
    )
    d = rgba_draw(canvas)

    pill_y0 = hc_top + px(20)
    pill_h = px(23)
    np_w = px(98)
    d.rounded_rectangle((px(38), pill_y0, px(38) + np_w, pill_y0 + pill_h), radius=pill_h // 2, fill=C_CREAM_PILL)
    draw_tracked(d, (px(38) + np_w / 2, pill_y0 + pill_h / 2), "NEXT PRAYER", font_sans(9.5, 700), C_CREAM_INK, tracking_dp=0.95, anchor="mm")

    city_w = px(70)
    cx1 = W - px(38)
    d.rounded_rectangle((cx1 - city_w, pill_y0, cx1, pill_y0 + pill_h), radius=pill_h // 2, outline=C_BORDER, width=max(1, px(1.0)))
    draw_tracked(d, (cx1 - city_w / 2, pill_y0 + pill_h / 2), "MUMBAI", font_sans(9.5, 600), C_TEXT_SEC, tracking_dp=0.8, anchor="mm")

    draw_tracked(d, (px(38), hc_top + px(60)), "ASR", font_sans(34.0, 700), C_TEXT_PRI, tracking_dp=1.0, anchor="lt")
    d.text((px(38), hc_top + px(103)), "Starts at 4:48 PM", font=font_sans(12.5, 500), fill=C_TEXT_SEC, anchor="lt")
    d.text((W - px(38), hc_top + px(95)), shape_ar("العصر"), font=font_arabic(26.0), fill=C_TEXT_SEC, anchor="rb")

    well_top = hc_top + px(133)
    well_bot = hc_bot - px(18)
    draw_leather_well(d, (px(36), well_top, W - px(36), well_bot), radius_dp=13.0, border_color=C_BORDER)
    draw_tracked(d, (px(51), well_top + px(11)), "TIME REMAINING", font_sans(9.0, 700), C_TEXT_SEC, tracking_dp=0.95, anchor="lt")
    draw_tracked(d, (px(51), well_top + px(25)), "01:07:52", font_mono(21.0), C_TEXT_PRI, tracking_dp=0.7, anchor="lt")

    rc_w, rc_h = px(94), px(30)
    rc_x1 = W - px(50)
    rc_x0 = rc_x1 - rc_w
    rc_y0 = (well_top + well_bot - rc_h) // 2
    d.rounded_rectangle(
        (rc_x0, rc_y0, rc_x1, rc_y0 + rc_h),
        radius=rc_h // 2,
        fill=rgba(C_CREAM_PILL, 0.11),
        outline=rgba(C_WARM, 0.36),
        width=max(1, px(1.0)),
    )
    draw_icon_bell(d, rc_x0 + px(18), rc_y0 + rc_h / 2, 13.5, C_WARM)
    d.text((rc_x0 + px(30), rc_y0 + rc_h / 2), "5m after", font=font_sans(10.5, 600), fill=C_TEXT_PRI, anchor="lm")

    # 3. Section header: TODAY'S PRAYERS + 12-Hour AM/PM
    sec_y = hc_bot + px(20)
    draw_tracked(d, (px(20), sec_y), "TODAY'S PRAYERS", font_sans(11.0, 700), C_TEXT_PRI, tracking_dp=1.05, anchor="lm")
    d.text((W - px(20), sec_y), "12-Hour AM/PM", font=font_sans(10.5, 500), fill=C_TEXT_SEC, anchor="rm")

    # 4. Five PrayerTimeCard rows
    prayers = [
        ("Fajr", "الفجر", "5:22 AM", "passed", True),
        ("Dhuhr", "الظهر", "12:28 PM", "passed", True),
        ("Asr", "العصر", "4:48 PM", "next", True),
        ("Maghrib", "المغرب", "6:08 PM", "upcoming", True),
        ("Isha", "العشاء", "7:22 PM", "upcoming", True),
    ]
    row_y = sec_y + px(14)
    row_h = px(62)
    row_gap = px(8)

    for name, ar, time_s, state, notif_on in prayers:
        is_next = state == "next"
        is_passed = state == "passed"
        fill_c = C_NEXT_CARD if is_next else C_SURFACE
        bord_c = rgba(C_CYAN, 0.46) if is_next else C_BORDER
        stitch_c = rgba(C_CYAN, 0.17) if is_next else None
        draw_leather_card(
            canvas,
            grain_tile,
            (px(16), row_y, W - px(16), row_y + row_h),
            radius_dp=14.0,
            fill_color=fill_c,
            border_color=bord_c,
            border_width_dp=1.2 if is_next else 1.0,
            stitch_color=stitch_c,
            drop_shadow=not is_passed,
        )
        d = rgba_draw(canvas)
        cy = row_y + row_h / 2.0

        if is_next:
            dot_c = C_LIME
        elif is_passed:
            dot_c = rgba(C_WARM, 0.32)
        else:
            dot_c = rgba(C_COGNAC, 0.62)
        dr = px(3.5)
        dx = px(33)
        d.ellipse((dx - dr, cy - dr, dx + dr, cy + dr), fill=dot_c)

        txt_alpha = 0.48 if is_passed else 1.0
        tx = px(49)
        name_font = font_sans(15.0, 700 if is_next else 600)
        d.text((tx, row_y + px(12)), name, font=name_font, fill=rgba(C_TEXT_PRI, txt_alpha), anchor="lt")
        nb = d.textbbox((tx, row_y + px(12)), name, font=name_font)

        if is_next:
            bx0 = nb[2] + px(8)
            by0 = row_y + px(13)
            bw, bh = px(38), px(17)
            d.rounded_rectangle(
                (bx0, by0, bx0 + bw, by0 + bh),
                radius=px(4),
                fill=rgba(C_CYAN, 0.18),
                outline=rgba(C_CYAN, 0.42),
                width=max(1, px(0.9)),
            )
            draw_tracked(d, (bx0 + bw / 2, by0 + bh / 2), "NEXT", font_sans(8.5, 700), C_CYAN_SOFT, tracking_dp=0.7, anchor="mm")
        elif is_passed:
            d.text((nb[2] + px(8), row_y + px(15)), "Done", font=font_sans(10.0, 500), fill=rgba(C_TEXT_SEC, 0.56), anchor="lt")

        d.text((tx, row_y + px(35)), shape_ar(ar), font=font_arabic(12.0), fill=rgba(C_TEXT_SEC, txt_alpha), anchor="lt")

        bell_sz = px(34)
        bell_x1 = W - px(30)
        bell_x0 = bell_x1 - bell_sz
        bell_y0 = int(cy - bell_sz / 2)
        bell_bord = rgba(C_CYAN, 0.42) if is_next else (rgba(C_WARM, 0.22) if notif_on else C_BORDER)
        draw_leather_well(d, (bell_x0, bell_y0, bell_x1, bell_y0 + bell_sz), radius_dp=9.0, border_color=bell_bord)
        bell_tint = C_CYAN_SOFT if is_next else (rgba(C_WARM, 0.48 if is_passed else 0.90) if notif_on else rgba(C_TEXT_SEC, 0.36))
        draw_icon_bell(d, (bell_x0 + bell_x1) / 2, cy, 15.0, bell_tint, muted=not notif_on)

        d.text(
            (bell_x0 - px(12), cy),
            time_s,
            font=font_sans(16.0, 700 if is_next else 600),
            fill=rgba(C_TEXT_PRI, txt_alpha),
            anchor="rm",
        )
        row_y += row_h + row_gap

    # 5. Astronomical Times collapsed footer bar
    astro_top = row_y + px(6)
    astro_bot = astro_top + px(42)
    if astro_bot < H - px(14):
        draw_leather_card(canvas, grain_tile, (px(16), astro_top, W - px(16), astro_bot), radius_dp=12.0, drop_shadow=False)
        d = rgba_draw(canvas)
        acy = (astro_top + astro_bot) / 2.0
        draw_icon_sun(d, px(36), acy, 14.0, C_WARM)
        draw_tracked(d, (px(50), acy), "ASTRONOMICAL TIMES (SUNRISE & SUNSET)", font_sans(9.2, 700), C_TEXT_PRI, tracking_dp=0.65, anchor="lm")
        chx = W - px(34)
        d.line([(chx - px(4.5), acy - px(2)), (chx, acy + px(2.5)), (chx + px(4.5), acy - px(2))], fill=C_TEXT_SEC, width=max(2, px(1.5)), joint="curve")

    d = rgba_draw(canvas)
    gw = px(108)
    d.rounded_rectangle(((W - gw) // 2, H - px(11), (W + gw) // 2, H - px(7)), radius=px(2), fill=rgba(C_TEXT_PRI, 0.26))

    return canvas, grain_tile


def build_scrim_sheet_base(base_home: Image.Image, grain_tile: Image.Image, sheet_top_dp: float) -> Tuple[Image.Image, int]:
    canvas = base_home.copy()
    d = rgba_draw(canvas)
    d.rectangle((0, 0, W, H), fill=(4, 6, 7, 166))

    sheet_y0 = px(sheet_top_dp)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((0, sheet_y0 - px(6), W, H + px(30)), radius=px(26), fill=(0, 0, 0, 195))
    sh = sh.filter(ImageFilter.GaussianBlur(px(12)))
    paste_rgba(canvas, sh, (0, 0))

    paste_grain_clipped(
        canvas,
        (0, sheet_y0, W, H + px(28)),
        radius=px(26),
        fill_color=C_SURFACE,
        grain_tile=grain_tile,
        grain_alpha=0.34,
        drop_shadow=False,
    )
    d = rgba_draw(canvas)
    d.rounded_rectangle((0, sheet_y0, W - 1, H + px(28)), radius=px(26), outline=C_BORDER, width=max(1, px(1.1)))
    hw = px(36)
    d.rounded_rectangle(((W - hw) // 2, sheet_y0 + px(11), (W + hw) // 2, sheet_y0 + px(15)), radius=px(2), fill=rgba(C_TEXT_SEC, 0.38))
    return canvas, sheet_y0


def build_cities_screen(base_home: Image.Image, grain_tile: Image.Image) -> Image.Image:
    canvas, sy = build_scrim_sheet_base(base_home, grain_tile, sheet_top_dp=168)
    d = rgba_draw(canvas)

    hy = sy + px(38)
    draw_icon_pin(d, px(28), hy, 17.0, C_WARM, filled=True)
    draw_tracked(d, (px(43), hy), "SELECT CITY IN INDIA", font_sans(14.0, 700), C_TEXT_PRI, tracking_dp=0.9, anchor="lm")

    cb_sz = px(32)
    cb_x0 = W - px(20) - cb_sz
    cb_y0 = hy - cb_sz // 2
    draw_leather_well(d, (cb_x0, cb_y0, cb_x0 + cb_sz, cb_y0 + cb_sz), radius_dp=9.0)
    cx, cy = cb_x0 + cb_sz / 2, cb_y0 + cb_sz / 2
    d.line([(cx - px(4.5), cy - px(4.5)), (cx + px(4.5), cy + px(4.5))], fill=C_TEXT_SEC, width=max(2, px(1.5)))
    d.line([(cx + px(4.5), cy - px(4.5)), (cx - px(4.5), cy + px(4.5))], fill=C_TEXT_SEC, width=max(2, px(1.5)))

    sf_y0 = hy + px(24)
    sf_y1 = sf_y0 + px(48)
    draw_leather_well(d, (px(20), sf_y0, W - px(20), sf_y1), radius_dp=12.0, border_color=rgba(C_CYAN, 0.34))
    scy = (sf_y0 + sf_y1) / 2.0
    mx, my = px(38), scy - px(1)
    mr = px(5.5)
    d.ellipse((mx - mr, my - mr, mx + mr, my + mr), outline=C_CYAN_SOFT, width=max(2, px(1.5)))
    d.line([(mx + mr * 0.72, my + mr * 0.72), (mx + px(8.5), my + px(8.5))], fill=C_CYAN_SOFT, width=max(2, px(1.5)))
    d.text((px(54), scy), "Search any city in India…", font=font_sans(12.5, 400), fill=C_TEXT_TER, anchor="lm")

    ly = sf_y1 + px(24)
    draw_tracked(d, (px(20), ly), "POPULAR CITIES", font_sans(10.5, 700), C_TEXT_SEC, tracking_dp=1.0, anchor="lm")
    d.text((px(20), ly + px(18)), "No GPS permission: timings are fetched by city name only.", font=font_sans(11.0, 400), fill=C_TEXT_TER, anchor="lt")

    cities = [
        ("Mumbai", True), ("Delhi", False), ("Hyderabad", False),
        ("Bengaluru", False), ("Chennai", False), ("Kolkata", False),
        ("Lucknow", False), ("Ahmedabad", False), ("Pune", False),
        ("Srinagar", False), ("Kozhikode", False), ("Bhopal", False),
        ("Jaipur", False), ("Patna", False), ("Surat", False),
        ("Indore", False), ("Nagpur", False), ("Kochi", False),
    ]
    chip_x = px(20)
    chip_y = ly + px(44)
    chip_h = px(38)
    max_x = W - px(20)
    f_chip = font_sans(12.5, 600)

    for city_name, selected in cities:
        tb = d.textbbox((0, 0), city_name, font=f_chip)
        tw = tb[2] - tb[0]
        extra = px(38) if selected else px(26)
        cw = tw + extra
        if chip_x + cw > max_x:
            chip_x = px(20)
            chip_y += chip_h + px(10)
        if selected:
            d.rounded_rectangle((chip_x, chip_y, chip_x + cw, chip_y + chip_h), radius=px(11), fill=C_CREAM_PILL)
            ckx = chip_x + px(15)
            cky = chip_y + chip_h / 2
            d.line(
                [(ckx - px(4), cky), (ckx - px(1), cky + px(3.5)), (ckx + px(5), cky - px(3.5))],
                fill=C_CREAM_INK,
                width=max(2, px(1.8)),
                joint="curve",
            )
            d.text((chip_x + px(27), chip_y + chip_h / 2), city_name, font=font_sans(12.5, 700), fill=C_CREAM_INK, anchor="lm")
        else:
            draw_leather_well(d, (chip_x, chip_y, chip_x + cw, chip_y + chip_h), radius_dp=11.0, border_color=C_BORDER)
            d.text((chip_x + cw / 2, chip_y + chip_h / 2), city_name, font=f_chip, fill=C_TEXT_PRI, anchor="mm")
        chip_x += cw + px(9)

    info_y0 = chip_y + chip_h + px(24)
    info_y1 = info_y0 + px(88)
    draw_leather_card(
        canvas,
        grain_tile,
        (px(20), info_y0, W - px(20), info_y1),
        radius_dp=15.0,
        fill_color=C_SURFACE_VAR,
        border_color=rgba(C_WARM, 0.24),
        stitch_color=rgba(C_WARM, 0.14),
        drop_shadow=False,
    )
    d = rgba_draw(canvas)
    draw_tracked(d, (px(36), info_y0 + px(22)), "PRIVATE & OFFLINE READY", font_sans(9.5, 700), C_WARM, tracking_dp=0.95, anchor="lm")
    d.text((px(36), info_y0 + px(42)), "Only your chosen city name is sent to fetch timings.", font=font_sans(11.5, 500), fill=C_TEXT_PRI, anchor="lt")
    d.text((px(36), info_y0 + px(60)), "The last schedule stays cached on your phone offline.", font=font_sans(11.0, 400), fill=C_TEXT_SEC, anchor="lt")

    gw = px(108)
    d.rounded_rectangle(((W - gw) // 2, H - px(11), (W + gw) // 2, H - px(7)), radius=px(2), fill=rgba(C_TEXT_PRI, 0.26))
    return canvas


def draw_switch(draw: ImageDraw.ImageDraw, x1: int, cy: float, on: bool) -> None:
    sw, sh = px(44), px(25)
    x0 = x1 - sw
    y0 = int(cy - sh / 2)
    if on:
        draw.rounded_rectangle((x0, y0, x1, y0 + sh), radius=sh // 2, fill=rgba(C_CYAN, 0.30), outline=rgba(C_CYAN, 0.62), width=max(1, px(1.0)))
        kr = px(9.2)
        kx = x1 - px(12.5)
        draw.ellipse((kx - kr, cy - kr, kx + kr, cy + kr), fill=C_CREAM_PILL)
    else:
        draw_leather_well(draw, (x0, y0, x1, y0 + sh), radius_dp=12.5, border_color=C_BORDER)
        kr = px(8.0)
        kx = x0 + px(12.5)
        draw.ellipse((kx - kr, cy - kr, kx + kr, cy + kr), fill=C_TEXT_TER)


def build_settings_screen(base_home: Image.Image, grain_tile: Image.Image) -> Image.Image:
    canvas, sy = build_scrim_sheet_base(base_home, grain_tile, sheet_top_dp=132)
    d = rgba_draw(canvas)

    hy = sy + px(36)
    draw_tracked(d, (px(20), hy), "SETTINGS", font_sans(15.0, 700), C_TEXT_PRI, tracking_dp=1.0, anchor="lm")
    cb_sz = px(32)
    cb_x0 = W - px(20) - cb_sz
    cb_y0 = hy - cb_sz // 2
    draw_leather_well(d, (cb_x0, cb_y0, cb_x0 + cb_sz, cb_y0 + cb_sz), radius_dp=9.0)
    cx, cy = cb_x0 + cb_sz / 2, cb_y0 + cb_sz / 2
    d.line([(cx - px(4.5), cy - px(4.5)), (cx + px(4.5), cy + px(4.5))], fill=C_TEXT_SEC, width=max(2, px(1.5)))
    d.line([(cx + px(4.5), cy - px(4.5)), (cx - px(4.5), cy + px(4.5))], fill=C_TEXT_SEC, width=max(2, px(1.5)))

    y = hy + px(26)
    draw_tracked(d, (px(20), y), "CALCULATION METHOD", font_sans(9.8, 700), C_TEXT_SEC, tracking_dp=0.95, anchor="lm")
    m_y0 = y + px(14)
    m_y1 = m_y0 + px(58)
    draw_leather_well(d, (px(20), m_y0, W - px(20), m_y1), radius_dp=12.0, border_color=C_BORDER)
    d.text((px(34), m_y0 + px(14)), "Univ. of Islamic Sciences, Karachi", font=font_sans(12.5, 600), fill=C_TEXT_PRI, anchor="lt")
    d.text((px(34), m_y0 + px(34)), "Method 1 · Standard across India", font=font_sans(10.5, 400), fill=C_TEXT_SEC, anchor="lt")
    chx, chy = W - px(38), (m_y0 + m_y1) / 2
    d.line([(chx - px(4.5), chy - px(2)), (chx, chy + px(2.5)), (chx + px(4.5), chy - px(2))], fill=C_TEXT_SEC, width=max(2, px(1.5)), joint="curve")

    y = m_y1 + px(22)
    draw_tracked(d, (px(20), y), "PRAYER REMINDERS", font_sans(9.8, 700), C_TEXT_SEC, tracking_dp=0.95, anchor="lm")

    r1_y = y + px(26)
    d.text((px(20), r1_y - px(7)), "Prayer Notifications", font=font_sans(13.0, 600), fill=C_TEXT_PRI, anchor="lm")
    d.text((px(20), r1_y + px(11)), "Exact on-device alarms, re-armed on reboot", font=font_sans(10.5, 400), fill=C_TEXT_SEC, anchor="lm")
    draw_switch(d, W - px(20), r1_y + px(1), True)

    oy = r1_y + px(34)
    d.text((px(20), oy), "Reminder Offset", font=font_sans(11.5, 600), fill=C_TEXT_SEC, anchor="lm")
    offsets = [("At Adhan", False), ("5m after", True), ("10m after", False), ("15m after", False)]
    ox = px(20)
    chip_top = oy + px(14)
    chip_w = (W - px(40) - px(8) * 3) // 4
    chip_h = px(34)
    for label, sel in offsets:
        if sel:
            d.rounded_rectangle((ox, chip_top, ox + chip_w, chip_top + chip_h), radius=px(9), fill=C_CREAM_PILL)
            d.text((ox + chip_w / 2, chip_top + chip_h / 2), label, font=font_sans(11.0, 700), fill=C_CREAM_INK, anchor="mm")
        else:
            draw_leather_well(d, (ox, chip_top, ox + chip_w, chip_top + chip_h), radius_dp=9.0)
            d.text((ox + chip_w / 2, chip_top + chip_h / 2), label, font=font_sans(11.0, 500), fill=C_TEXT_PRI, anchor="mm")
        ox += chip_w + px(8)

    az_y0 = chip_top + chip_h + px(18)
    az_y1 = az_y0 + px(126)
    draw_leather_card(
        canvas,
        grain_tile,
        (px(20), az_y0, W - px(20), az_y1),
        radius_dp=15.0,
        fill_color=C_NEXT_CARD,
        border_color=rgba(C_CYAN, 0.42),
        stitch_color=rgba(C_CYAN, 0.16),
        drop_shadow=False,
    )
    d = rgba_draw(canvas)
    draw_tracked(d, (px(34), az_y0 + px(20)), "AZAAN AUDIO", font_sans(9.5, 700), C_CYAN_SOFT, tracking_dp=0.95, anchor="lm")

    rad1_y = az_y0 + px(48)
    rx = px(42)
    d.ellipse((rx - px(7.5), rad1_y - px(7.5), rx + px(7.5), rad1_y + px(7.5)), outline=C_LIME, width=max(2, px(1.5)))
    d.ellipse((rx - px(3.8), rad1_y - px(3.8), rx + px(3.8), rad1_y + px(3.8)), fill=C_LIME)
    d.text((px(57), rad1_y - px(7)), "Madinah Azaan (Bundled)", font=font_sans(12.8, 700), fill=C_TEXT_PRI, anchor="lm")
    d.text((px(57), rad1_y + px(10)), "Plays in Silent mode via Android Alarm stream", font=font_sans(10.3, 400), fill=C_TEXT_SEC, anchor="lm")

    rad2_y = az_y0 + px(95)
    d.ellipse((rx - px(7.5), rad2_y - px(7.5), rx + px(7.5), rad2_y + px(7.5)), outline=C_TEXT_TER, width=max(2, px(1.4)))
    d.text((px(57), rad2_y), "System notification or custom audio file…", font=font_sans(11.5, 500), fill=C_TEXT_SEC, anchor="lm")

    sv_y = az_y1 + px(24)
    d.text((px(20), sv_y), "Play Adhan Sound", font=font_sans(12.5, 600), fill=C_TEXT_PRI, anchor="lm")
    draw_switch(d, W - px(20), sv_y, True)

    vv_y = sv_y + px(38)
    d.text((px(20), vv_y), "Vibrate at Reminder", font=font_sans(12.5, 600), fill=C_TEXT_PRI, anchor="lm")
    draw_switch(d, W - px(20), vv_y, True)

    ty = vv_y + px(36)
    draw_tracked(d, (px(20), ty), "APPEARANCE & CLOCK", font_sans(9.8, 700), C_TEXT_SEC, tracking_dp=0.95, anchor="lm")

    th_top = ty + px(16)
    th_h = px(36)
    th_w = (W - px(40) - px(8) * 2) // 3
    tx = px(20)
    for label, sel in [("System", False), ("Cream Light", False), ("Black Leather", True)]:
        if sel:
            d.rounded_rectangle((tx, th_top, tx + th_w, th_top + th_h), radius=px(10), fill=C_CREAM_PILL)
            d.text((tx + th_w / 2, th_top + th_h / 2), label, font=font_sans(11.0, 700), fill=C_CREAM_INK, anchor="mm")
        else:
            draw_leather_well(d, (tx, th_top, tx + th_w, th_top + th_h), radius_dp=10.0)
            d.text((tx + th_w / 2, th_top + th_h / 2), label, font=font_sans(11.0, 500), fill=C_TEXT_PRI, anchor="mm")
        tx += th_w + px(8)

    c24_y = th_top + th_h + px(26)
    d.text((px(20), c24_y), "24-Hour Clock Format", font=font_sans(12.5, 600), fill=C_TEXT_PRI, anchor="lm")
    draw_switch(d, W - px(20), c24_y, False)

    gw = px(108)
    d.rounded_rectangle(((W - gw) // 2, H - px(11), (W + gw) // 2, H - px(7)), radius=px(2), fill=rgba(C_TEXT_PRI, 0.26))
    return canvas


def save_variants(img_3x: Image.Image, stem: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rgb = img_3x.convert("RGB")

    im_780 = rgb.resize((780, 1688), Image.Resampling.LANCZOS)
    im_780 = ImageEnhance.Sharpness(im_780).enhance(1.06)
    im_780.save(OUT_DIR / f"{stem}-780.webp", "WEBP", quality=90, method=6)
    im_780.save(OUT_DIR / f"{stem}.png", "PNG", optimize=True)

    im_400 = rgb.resize((400, 866), Image.Resampling.LANCZOS)
    im_400 = ImageEnhance.Sharpness(im_400).enhance(1.08)
    im_400.save(OUT_DIR / f"{stem}-400.webp", "WEBP", quality=90, method=6)
    print(f"wrote {stem}: -400.webp ({(OUT_DIR / f'{stem}-400.webp').stat().st_size // 1024} KB), "
          f"-780.webp ({(OUT_DIR / f'{stem}-780.webp').stat().st_size // 1024} KB)")


def write_svg_fallback(today_3x: Image.Image) -> None:
    """Keep /assets/namaaz-preview.svg updated with the new UI so no stale grey/white SVG remains."""
    im = today_3x.convert("RGB").resize((585, 1266), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=88, method=6)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="390" height="844" viewBox="0 0 390 844" fill="none">\n'
        '  <defs><clipPath id="r"><rect width="390" height="844" rx="24"/></clipPath></defs>\n'
        f'  <image href="data:image/webp;base64,{b64}" width="390" height="844" clip-path="url(#r)" preserveAspectRatio="xMidYMid slice"/>\n'
        '  <rect x="0.75" y="0.75" width="388.5" height="842.5" rx="23.25" stroke="#252B2E" stroke-width="1.5"/>\n'
        '</svg>\n'
    )
    svg_path = ROOT / "docs" / "assets" / "namaaz-preview.svg"
    svg_path.write_text(svg, encoding="utf-8")
    print(f"updated {svg_path.relative_to(ROOT)} ({len(svg) // 1024} KB)")


def main() -> None:
    today_3x, grain_tile = build_base_home_screen()
    cities_3x = build_cities_screen(today_3x, grain_tile)
    settings_3x = build_settings_screen(today_3x, grain_tile)

    save_variants(today_3x, "today")
    save_variants(cities_3x, "cities")
    save_variants(settings_3x, "settings")
    write_svg_fallback(today_3x)


if __name__ == "__main__":
    main()
