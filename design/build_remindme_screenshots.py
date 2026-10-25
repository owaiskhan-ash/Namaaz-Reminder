#!/usr/bin/env python3
"""
Generate the RemindME icon set and 3 Android screenshots for the landing page.

Outputs:
  docs/assets/remindme/
    icon.png
    icon-512.png, icon-256.png, icon-192.png, icon-128.png, icon-64.png
    home.png,     home-780.webp,     home-400.webp
    previous.png, previous-780.webp, previous-400.webp
    settings.png, settings-780.webp, settings-400.webp

Faithfully recreates the RemindME v1.0.5 native Android UI (dark theme by
default: surface #101512, card #19201C, preview #203126, sage #71917C,
sage_dark #C0DBC6, outline #2D3932, felt-leather RE badge, 3-item bottom dock
for Home / Previous / Settings).
"""

from __future__ import annotations

import base64
import io
import math
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

try:
    import freetype
    import numpy as np
    import uharfbuzz as hb

    HAS_HARFBUZZ = True
except ImportError:
    HAS_HARFBUZZ = False

# Pre-shaped RGBA label glyphs at 3x (42px) for non-Latin scripts so the
# generator produces identical output even without uharfbuzz / /tmp fonts.
_SHAPED_LABELS_B64 = {
    "devanagari": (
        "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"
    ),
    "arabic": (
        "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"
        "nQAAAABJRU5ErkJggg=="
    ),
    "han": (
        "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"
    ),
}

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "docs" / "assets" / "fonts"
SOURCE_ICON = ROOT / "design" / "source" / "RE-icon.png"
OUT_DIR = ROOT / "docs" / "assets" / "remindme"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 3x reference canvas -> downsampled to 780x1688 and 400x866
W, H = 1170, 2532

# RemindME v1.0.5 Dark Palette (values-night/colors.xml)
SURFACE = (16, 21, 18)           # #101512
CARD = (25, 32, 28)              # #19201C
CARD_COMPLETED = (21, 27, 23)    # #19201C blended at 0.68 alpha over #101512
PREVIEW = (32, 49, 38)           # #203126
INK = (240, 244, 238)            # #F0F4EE
INK_COMPLETED = (176, 181, 176)  # #F0F4EE at 0.68 alpha
INK_MUTED = (180, 189, 183)      # #B4BDB7
INK_HINT = (140, 150, 144)       # #8C9690
SAGE = (113, 145, 124)           # #71917C
SAGE_DARK = (192, 219, 198)      # #C0DBC6
SAGE_LIGHT = (41, 65, 52)        # #294134
DONE_BUTTON = (36, 56, 43)       # #24382B
OUTLINE = (45, 57, 50)           # #2D3932
DOCK_INACTIVE = (155, 166, 159)  # #9BA69F
DOCK_ACTIVE = (192, 219, 198)    # #C0DBC6
DOCK_ACTIVE_BG = (41, 67, 52)    # #294334
WHITE = (255, 255, 255)          # #FFFFFF
DANGER = (240, 154, 154)         # #F09A9A


# ---------------------------------------------------------------------------
# Font loading & HarfBuzz shaping for non-Latin scripts
# ---------------------------------------------------------------------------

_FONT_BYTES_CACHE: dict[str, bytes] = {}


def _load_ttf_bytes(path: Path) -> bytes:
    key = str(path)
    if key not in _FONT_BYTES_CACHE:
        if path.suffix.lower() == ".woff2":
            buf = io.BytesIO()
            tt = TTFont(str(path))
            tt.flavor = None
            tt.save(buf)
            _FONT_BYTES_CACHE[key] = buf.getvalue()
        else:
            _FONT_BYTES_CACHE[key] = path.read_bytes()
    return _FONT_BYTES_CACHE[key]


def font(family: str, weight: int, size: int) -> ImageFont.FreeTypeFont:
    table = {
        ("sans", 400): "plus-jakarta-sans-latin-400-normal.woff2",
        ("sans", 500): "plus-jakarta-sans-latin-500-normal.woff2",
        ("sans", 600): "plus-jakarta-sans-latin-600-normal.woff2",
        ("sans", 700): "plus-jakarta-sans-latin-700-normal.woff2",
        ("display", 600): "plus-jakarta-sans-latin-600-normal.woff2",
        ("display", 700): "plus-jakarta-sans-latin-700-normal.woff2",
        ("mono", 500): "plus-jakarta-sans-latin-500-normal.woff2",
    }
    fname = table.get((family, weight), "plus-jakarta-sans-latin-500-normal.woff2")
    raw = _load_ttf_bytes(FONT_DIR / fname)
    return ImageFont.truetype(io.BytesIO(raw), size=size)


def render_hb_text(
    ttf_bytes: bytes,
    text: str,
    px_size: int,
    color_rgba: tuple[int, int, int, int],
    direction: str = "ltr",
) -> Image.Image:
    hb_blob = hb.Blob(ttf_bytes)
    hb_face = hb.Face(hb_blob)
    hb_font = hb.Font(hb_face)
    upem = hb_face.upem

    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    if direction:
        buf.direction = direction
    hb.shape(hb_font, buf)

    infos = buf.glyph_infos
    positions = buf.glyph_positions

    ft_face = freetype.Face(io.BytesIO(ttf_bytes))
    ft_face.set_pixel_sizes(0, px_size)
    scale = px_size / float(upem)

    pen_x, pen_y = 0.0, 0.0
    glyphs = []
    min_x, min_y, max_x, max_y = 10000, 10000, -10000, -10000
    for info, pos in zip(infos, positions):
        ft_face.load_glyph(
            info.codepoint,
            freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_NORMAL,
        )
        bmp = ft_face.glyph.bitmap
        gx = int(round(pen_x + (pos.x_offset * scale) + ft_face.glyph.bitmap_left))
        gy = int(round(pen_y - (pos.y_offset * scale) - ft_face.glyph.bitmap_top))
        w, h = bmp.width, bmp.rows
        if w > 0 and h > 0:
            arr = np.array(bmp.buffer, dtype=np.uint8).reshape((h, w))
            glyphs.append((gx, gy, w, h, arr))
            min_x = min(min_x, gx)
            min_y = min(min_y, gy)
            max_x = max(max_x, gx + w)
            max_y = max(max_y, gy + h)
        pen_x += pos.x_advance * scale
        pen_y -= pos.y_advance * scale

    if not glyphs:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))

    out_w = max_x - min_x + 4
    out_h = max_y - min_y + 4
    alpha = np.zeros((out_h, out_w), dtype=np.uint16)
    for gx, gy, w, h, arr in glyphs:
        x0 = gx - min_x + 2
        y0 = gy - min_y + 2
        alpha[y0 : y0 + h, x0 : x0 + w] = np.clip(
            alpha[y0 : y0 + h, x0 : x0 + w] + arr, 0, 255
        )

    rgba = np.zeros((out_h, out_w, 4), dtype=np.uint8)
    rgba[..., 0] = color_rgba[0]
    rgba[..., 1] = color_rgba[1]
    rgba[..., 2] = color_rgba[2]
    rgba[..., 3] = (alpha * (color_rgba[3] / 255.0)).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


# ---------------------------------------------------------------------------
# Icon generation
# ---------------------------------------------------------------------------

def build_icons() -> Image.Image:
    src = Image.open(SOURCE_ICON).convert("RGBA")
    alpha = src.split()[3]
    bbox = alpha.getbbox() or (0, 0, src.width, src.height)
    cropped = src.crop(bbox)

    # Fit cleanly inside 512x512 with 1.5% breathing room (matches nr-mark-512)
    master_size = 512
    pad = int(round(master_size * 0.015))
    inner = master_size - pad * 2
    scale = min(inner / cropped.width, inner / cropped.height)
    new_w = int(round(cropped.width * scale))
    new_h = int(round(cropped.height * scale))
    resized = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)

    master = Image.new("RGBA", (master_size, master_size), (0, 0, 0, 0))
    master.paste(
        resized,
        ((master_size - new_w) // 2, (master_size - new_h) // 2),
        resized,
    )

    for s in (512, 256, 192, 128, 64):
        out = (
            master
            if s == master_size
            else master.resize((s, s), Image.Resampling.LANCZOS)
        )
        out.save(OUT_DIR / f"icon-{s}.png", optimize=True)
        if s == 512:
            out.save(OUT_DIR / "icon.png", optimize=True)
        print(f"  wrote icon-{s}.png")

    return master


# ---------------------------------------------------------------------------
# Shared UI helpers
# ---------------------------------------------------------------------------

def new_canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), SURFACE)
    draw = ImageDraw.Draw(img, "RGBA")
    return img, draw


def draw_status_bar(draw: ImageDraw.ImageDraw) -> None:
    f_time = font("sans", 600, 38)
    draw.text((76, 44), "8:42", font=f_time, fill=INK)
    # Signal bars
    bx = W - 220
    by = 54
    for i, bh in enumerate((12, 17, 22, 27)):
        x0 = bx + i * 13
        draw.rounded_rectangle(
            (x0, by + 27 - bh, x0 + 8, by + 27), radius=2, fill=INK
        )
    # Wi-Fi dot + arc hint
    # Battery
    bat_x, bat_y = W - 134, 52
    draw.rounded_rectangle(
        (bat_x, bat_y, bat_x + 56, bat_y + 28),
        radius=6,
        outline=INK_MUTED,
        width=2,
    )
    draw.rounded_rectangle(
        (bat_x + 5, bat_y + 5, bat_x + 45, bat_y + 23), radius=3, fill=INK
    )
    draw.rounded_rectangle(
        (bat_x + 58, bat_y + 9, bat_x + 62, bat_y + 19),
        radius=1,
        fill=INK_MUTED,
    )


def draw_card(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    radius: int = 48,
    fill: tuple[int, int, int] = CARD,
    outline: tuple[int, int, int] | None = OUTLINE,
    width: int = 3,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill)
    if outline:
        draw.rounded_rectangle(box, radius=radius, outline=outline, width=width)


def draw_bottom_dock(draw: ImageDraw.ImageDraw, active_tab: str) -> None:
    """
    Matches activity_main.xml bottom_dock:
    72dp height (216px at 3x) + navigation bar inset below.
    3 equal tabs: Home, Previous, Settings.
    """
    dock_top = H - 266
    dock_bottom = H - 50
    draw.rectangle((0, dock_top, W, H), fill=CARD)
    draw.line((0, dock_top, W, dock_top), fill=OUTLINE, width=3)

    tabs = [
        ("home", "Home"),
        ("previous", "Previous"),
        ("settings", "Settings"),
    ]
    pad_x = 36
    pad_y = 21
    tab_w = (W - pad_x * 2) // 3
    f_active = font("sans", 600, 33)
    f_inactive = font("sans", 500, 33)

    for idx, (key, label) in enumerate(tabs):
        x0 = pad_x + idx * tab_w
        x1 = x0 + tab_w
        y0 = dock_top + pad_y
        y1 = dock_bottom - pad_y
        cx = (x0 + x1) // 2
        is_active = key == active_tab

        if is_active:
            draw.rounded_rectangle(
                (x0 + 6, y0, x1 - 6, y1), radius=42, fill=DOCK_ACTIVE_BG
            )

        color = DOCK_ACTIVE if is_active else DOCK_INACTIVE
        icon_cy = y0 + 56

        if key == "home":
            # ic_nav_home: house roof + body
            pts = [
                (cx - 26, icon_cy + 2),
                (cx, icon_cy - 22),
                (cx + 26, icon_cy + 2),
            ]
            draw.line(pts, fill=color, width=5, joint="curve")
            draw.line(
                [
                    (cx - 18, icon_cy - 3),
                    (cx - 18, icon_cy + 20),
                    (cx + 18, icon_cy + 20),
                    (cx + 18, icon_cy - 3),
                ],
                fill=color,
                width=5,
                joint="curve",
            )
        elif key == "previous":
            # ic_nav_history: circle + clock hands
            r = 23
            draw.ellipse(
                (cx - r, icon_cy - r, cx + r, icon_cy + r),
                outline=color,
                width=5,
            )
            draw.line(
                [(cx, icon_cy - 12), (cx, icon_cy), (cx + 10, icon_cy + 6)],
                fill=color,
                width=5,
                joint="curve",
            )
        elif key == "settings":
            # ic_nav_settings: gear circle + 8 teeth + inner circle
            r_outer = 16
            r_inner = 7
            draw.ellipse(
                (cx - r_outer, icon_cy - r_outer, cx + r_outer, icon_cy + r_outer),
                outline=color,
                width=5,
            )
            for a_deg in range(0, 360, 45):
                ang = math.radians(a_deg)
                x_s = cx + math.cos(ang) * 16
                y_s = icon_cy + math.sin(ang) * 16
                x_e = cx + math.cos(ang) * 24
                y_e = icon_cy + math.sin(ang) * 24
                draw.line([(x_s, y_s), (x_e, y_e)], fill=color, width=5)
            draw.ellipse(
                (cx - r_inner, icon_cy - r_inner, cx + r_inner, icon_cy + r_inner),
                outline=color,
                width=4,
            )

        f_lbl = f_active if is_active else f_inactive
        tw = draw.textlength(label, font=f_lbl)
        draw.text((cx - tw / 2, y0 + 96), label, font=f_lbl, fill=color)

    # Android gesture pill
    pill_w = 340
    draw.rounded_rectangle(
        ((W - pill_w) // 2, H - 30, (W + pill_w) // 2, H - 18),
        radius=6,
        fill=(92, 102, 96),
    )


def save_screen(img: Image.Image, name: str) -> None:
    s780 = img.resize((780, 1688), Image.Resampling.LANCZOS)
    s400 = img.resize((400, 866), Image.Resampling.LANCZOS)
    s780.save(OUT_DIR / f"{name}.png", format="PNG", optimize=True)
    s780.save(OUT_DIR / f"{name}-780.webp", format="WEBP", quality=88, method=6)
    s400.save(OUT_DIR / f"{name}-400.webp", format="WEBP", quality=86, method=6)
    print(f"  wrote {name}.png, {name}-780.webp, {name}-400.webp")


# ---------------------------------------------------------------------------
# Screen 1: Home (Conversational capture + Smart Parse + Upcoming)
# ---------------------------------------------------------------------------

def build_home_screen(master_icon: Image.Image) -> None:
    img, draw = new_canvas()
    draw_status_bar(draw)

    pad = 66  # 22dp * 3
    y = 148

    # Brand header row (re_felt_leather_icon 54dp = 162px)
    icon_px = 162
    badge = master_icon.resize((icon_px, icon_px), Image.Resampling.LANCZOS)
    img.paste(badge, (pad, y), badge)

    f_brand = font("display", 700, 72)
    f_tag = font("sans", 400, 39)
    draw.text((pad + icon_px + 39, y + 18), "RemindME", font=f_brand, fill=INK)
    draw.text(
        (pad + icon_px + 39, y + 104),
        "A clear nudge, at the right moment.",
        font=f_tag,
        fill=INK_MUTED,
    )

    y += icon_px + 78

    # Main conversational prompt
    f_h1 = font("display", 700, 76)
    draw.text((pad, y), "What do you want to", font=f_h1, fill=INK)
    y += 88
    draw.text((pad, y), "remember?", font=f_h1, fill=INK)
    y += 106

    f_sub = font("sans", 400, 42)
    draw.text(
        (pad, y),
        "Write it naturally. Include a date and time",
        font=f_sub,
        fill=INK_MUTED,
    )
    y += 54
    draw.text(
        (pad, y),
        "so your alarm can be scheduled.",
        font=f_sub,
        fill=INK_MUTED,
    )
    y += 82

    # Natural language input box (bg_input: #19201C, 1dp #2D3932, 16dp radius)
    input_h = 310
    draw_card(draw, (pad, y, W - pad, y + input_h), radius=48, fill=CARD, outline=OUTLINE)
    f_input = font("sans", 500, 48)
    draw.text(
        (pad + 51, y + 48),
        "Tomorrow at 9 AM - check in with",
        font=f_input,
        fill=INK,
    )
    line2 = "Abdullah about homework"
    draw.text((pad + 51, y + 116), line2, font=f_input, fill=INK)
    # Subtle cursor at end of line2
    cur_x = pad + 51 + int(draw.textlength(line2, font=f_input)) + 6
    draw.rounded_rectangle(
        (cur_x, y + 118, cur_x + 5, y + 170), radius=2, fill=SAGE_DARK
    )

    y += input_h + 33

    # Smart Parse preview card (bg_preview: #203126, 14dp radius = 42px)
    prev_h = 236
    draw_card(
        draw, (pad, y, W - pad, y + prev_h), radius=42, fill=PREVIEW, outline=None
    )
    f_kicker = font("sans", 700, 30)
    f_prev_title = font("sans", 600, 41)
    f_prev_meta = font("sans", 400, 36)
    draw.text((pad + 42, y + 36), "SMART PARSE", font=f_kicker, fill=SAGE_DARK)
    draw.text(
        (pad + 42, y + 86),
        "Check in with Abdullah about homework",
        font=f_prev_title,
        fill=INK,
    )
    draw.text(
        (pad + 42, y + 138),
        "Tomorrow at 9:00 AM  ·  Ready to schedule.",
        font=f_prev_meta,
        fill=INK_MUTED,
    )

    y += prev_h + 42

    # Primary button: Set reminder (bg_primary_button: #71917C, 15dp radius = 45px, 52dp = 156px)
    btn_h = 156
    draw_card(
        draw, (pad, y, W - pad, y + btn_h), radius=45, fill=SAGE, outline=None
    )
    f_btn = font("sans", 600, 45)
    btn_lbl = "Set reminder"
    bw = draw.textlength(btn_lbl, font=f_btn)
    draw.text(
        ((W - bw) / 2, y + 50),
        btn_lbl,
        font=f_btn,
        fill=WHITE,
    )

    y += btn_h + 52

    # Notification / Alarm stream status card
    notif_h = 196
    draw_card(draw, (pad, y, W - pad, y + notif_h), radius=48, fill=CARD, outline=OUTLINE)
    f_notif = font("sans", 400, 37)
    draw.text(
        (pad + 45, y + 36),
        "Alarm alerts are ready. They use the",
        font=f_notif,
        fill=INK_MUTED,
    )
    draw.text(
        (pad + 45, y + 84),
        "Android alarm stream, so silent mode",
        font=f_notif,
        fill=INK_MUTED,
    )
    draw.text(
        (pad + 45, y + 132),
        "will not mute them.",
        font=f_notif,
        fill=INK_MUTED,
    )
    # "On" badge button (bg_secondary_button: #294134, 12dp radius = 36px)
    pill_w, pill_h = 148, 114
    px0 = W - pad - 45 - pill_w
    py0 = y + (notif_h - pill_h) // 2
    draw_card(
        draw,
        (px0, py0, px0 + pill_w, py0 + pill_h),
        radius=36,
        fill=SAGE_LIGHT,
        outline=None,
    )
    f_pill = font("sans", 600, 36)
    on_w = draw.textlength("On", font=f_pill)
    draw.text(
        (px0 + (pill_w - on_w) / 2, py0 + 34),
        "On",
        font=f_pill,
        fill=SAGE_DARK,
    )

    y += notif_h + 62

    # Upcoming section
    f_sec = font("display", 700, 56)
    draw.text((pad, y), "Upcoming", font=f_sec, fill=INK)
    y += 82

    # Upcoming reminder card (matches ReminderItemViewFactory.create)
    up_h = 278
    draw_card(draw, (pad, y, W - pad, y + up_h), radius=48, fill=CARD, outline=OUTLINE)
    f_rem_title = font("sans", 600, 46)
    f_rem_sub = font("sans", 400, 36)
    draw.text(
        (pad + 48, y + 40),
        "Call Ammi before evening walk",
        font=f_rem_title,
        fill=INK,
    )
    draw.text(
        (pad + 48, y + 102),
        "Today at 6:30 PM",
        font=f_rem_sub,
        fill=INK_MUTED,
    )

    # Actions row (right aligned: Mark done + Delete)
    f_act = font("sans", 600, 36)
    del_lbl = "Delete"
    del_w = draw.textlength(del_lbl, font=f_act)
    del_x = W - pad - 54 - del_w
    act_y = y + 156
    draw.text((del_x, act_y + 28), del_lbl, font=f_act, fill=DANGER)

    done_lbl = "Mark done"
    done_tw = draw.textlength(done_lbl, font=f_act)
    done_bw = int(done_tw + 72)
    done_bh = 98
    done_x = int(del_x - 36 - done_bw)
    draw_card(
        draw,
        (done_x, act_y, done_x + done_bw, act_y + done_bh),
        radius=30,
        fill=DONE_BUTTON,
        outline=None,
    )
    draw.text(
        (done_x + 36, act_y + 26),
        done_lbl,
        font=f_act,
        fill=SAGE_DARK,
    )

    draw_bottom_dock(draw, "home")
    save_screen(img, "home")


# ---------------------------------------------------------------------------
# Screen 2: Previous (Completed reminders history + Clear completed)
# ---------------------------------------------------------------------------

def build_previous_screen() -> None:
    img, draw = new_canvas()
    draw_status_bar(draw)

    pad = 66
    y = 156

    f_h1 = font("display", 700, 76)
    draw.text((pad, y), "Previous reminders", font=f_h1, fill=INK)
    y += 104

    f_sub = font("sans", 400, 42)
    draw.text(
        (pad, y),
        "Completed reminders live here, out of your way.",
        font=f_sub,
        fill=INK_MUTED,
    )
    y += 86

    # Clear completed button (bg_secondary_button: #294134, 12dp radius = 36px, 40dp = 120px)
    f_btn = font("sans", 600, 36)
    clr_lbl = "Clear completed"
    clr_tw = draw.textlength(clr_lbl, font=f_btn)
    clr_w = int(clr_tw + 84)
    clr_h = 120
    draw_card(
        draw,
        (pad, y, pad + clr_w, y + clr_h),
        radius=36,
        fill=SAGE_LIGHT,
        outline=None,
    )
    draw.text((pad + 42, y + 38), clr_lbl, font=f_btn, fill=SAGE_DARK)

    y += clr_h + 54

    completed_items = [
        "Check in with Abdullah about homework",
        "Pick up prescription from medical store",
        "Send signed rent receipt to landlord",
        "Water the balcony plants before work",
        "Submit electricity bill reading",
    ]

    f_rem_title = font("sans", 600, 45)
    f_rem_sub = font("sans", 400, 36)
    f_act = font("sans", 600, 36)

    for title in completed_items:
        card_h = 264
        draw_card(
            draw,
            (pad, y, W - pad, y + card_h),
            radius=48,
            fill=CARD_COMPLETED,
            outline=OUTLINE,
        )
        tx = pad + 48
        ty = y + 42
        draw.text((tx, ty), title, font=f_rem_title, fill=INK_COMPLETED)
        # Strikethrough line matching Paint.STRIKE_THRU_TEXT_FLAG
        tw = draw.textlength(title, font=f_rem_title)
        strike_y = ty + 28
        draw.line(
            ((tx, strike_y), (tx + tw, strike_y)),
            fill=INK_COMPLETED,
            width=4,
        )

        draw.text(
            (tx, y + 106),
            "Completed",
            font=f_rem_sub,
            fill=INK_MUTED,
        )

        del_lbl = "Delete"
        del_w = draw.textlength(del_lbl, font=f_act)
        draw.text(
            (W - pad - 54 - del_w, y + 174),
            del_lbl,
            font=f_act,
            fill=DANGER,
        )

        y += card_h + 33

    draw_bottom_dock(draw, "previous")
    save_screen(img, "previous")


# ---------------------------------------------------------------------------
# Screen 3: Settings (7 Languages, Alarm Sound, Dark Mode)
# ---------------------------------------------------------------------------

def build_settings_screen() -> None:
    img, draw = new_canvas()
    draw_status_bar(draw)

    pad = 66
    y = 148

    f_h1 = font("display", 700, 76)
    draw.text((pad, y), "Settings", font=f_h1, fill=INK)
    y += 96

    f_sub = font("sans", 400, 41)
    draw.text(
        (pad, y),
        "Keep your reminders reliable and your space calm.",
        font=f_sub,
        fill=INK_MUTED,
    )
    y += 74

    # Card 1: Language (7 radio options)
    lang_card_h = 842
    draw_card(
        draw,
        (pad, y, W - pad, y + lang_card_h),
        radius=48,
        fill=CARD,
        outline=OUTLINE,
    )
    f_card_title = font("display", 700, 48)
    f_card_sub = font("sans", 400, 34)
    f_radio = font("sans", 400, 41)

    draw.text((pad + 51, y + 40), "Language", font=f_card_title, fill=INK)
    draw.text(
        (pad + 51, y + 104),
        "Choose the language for RemindME and its alarm actions.",
        font=f_card_sub,
        fill=INK_MUTED,
    )

    def _get_shaped_label(script: str, label: str, direction: str) -> Image.Image:
        font_paths = {
            "devanagari": Path("/tmp/fonts/noto-sans-devanagari-devanagari-400-normal.woff2"),
            "han": Path("/tmp/fonts/noto-sans-sc-chinese-simplified-400-normal.woff2"),
            "arabic": Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        }
        fp = font_paths.get(script)
        if HAS_HARFBUZZ and fp and fp.exists():
            ttf = _load_ttf_bytes(fp)
            return render_hb_text(ttf, label, 42, (*INK, 255), direction=direction)
        raw_png = base64.b64decode(_SHAPED_LABELS_B64[script])
        return Image.open(io.BytesIO(raw_png)).convert("RGBA")

    languages = [
        ("English", True, "latin"),
        ("Bahasa Indonesia", False, "latin"),
        ("Español", False, "latin"),
        ("Português", False, "latin"),
        ("हिन्दी", False, "devanagari"),
        ("العربية", False, "arabic"),
        ("简体中文", False, "han"),
    ]

    ry = y + 184
    row_step = 90
    for label, checked, script in languages:
        rcx = pad + 81
        rcy = ry + 26
        r_outer = 24
        if checked:
            draw.ellipse(
                (rcx - r_outer, rcy - r_outer, rcx + r_outer, rcy + r_outer),
                outline=SAGE,
                width=5,
            )
            r_inner = 12
            draw.ellipse(
                (rcx - r_inner, rcy - r_inner, rcx + r_inner, rcy + r_inner),
                fill=SAGE,
            )
        else:
            draw.ellipse(
                (rcx - r_outer, rcy - r_outer, rcx + r_outer, rcy + r_outer),
                outline=INK_HINT,
                width=4,
            )

        tx = pad + 135
        if script == "latin":
            draw.text((tx, ry), label, font=f_radio, fill=INK)
        elif script == "devanagari":
            glyph_img = _get_shaped_label("devanagari", label, "ltr")
            img.paste(glyph_img, (tx, ry + 2), glyph_img)
        elif script == "arabic":
            glyph_img = _get_shaped_label("arabic", label, "rtl")
            img.paste(glyph_img, (tx, ry + 2), glyph_img)
        elif script == "han":
            glyph_img = _get_shaped_label("han", label, "ltr")
            img.paste(glyph_img, (tx, ry + 4), glyph_img)

        ry += row_step

    y += lang_card_h + 38

    # Card 2: Alarm sound
    sound_card_h = 488
    draw_card(
        draw,
        (pad, y, W - pad, y + sound_card_h),
        radius=48,
        fill=CARD,
        outline=OUTLINE,
    )
    draw.text((pad + 51, y + 40), "Alarm sound", font=f_card_title, fill=INK)
    draw.text(
        (pad + 51, y + 104),
        "Your device alarm remains the default.",
        font=f_card_sub,
        fill=INK_MUTED,
    )

    sound_opts = [
        ("Device alarm sound (default)", True),
        ("RemindME alarm sound", False),
    ]
    sry = y + 178
    for label, checked in sound_opts:
        rcx = pad + 81
        rcy = sry + 26
        r_outer = 24
        if checked:
            draw.ellipse(
                (rcx - r_outer, rcy - r_outer, rcx + r_outer, rcy + r_outer),
                outline=SAGE,
                width=5,
            )
            r_inner = 12
            draw.ellipse(
                (rcx - r_inner, rcy - r_inner, rcx + r_inner, rcy + r_inner),
                fill=SAGE,
            )
        else:
            draw.ellipse(
                (rcx - r_outer, rcy - r_outer, rcx + r_outer, rcy + r_outer),
                outline=INK_HINT,
                width=4,
            )
        draw.text((pad + 135, sry), label, font=f_radio, fill=INK)
        sry += 88

    f_note = font("sans", 400, 33)
    draw.text(
        (pad + 51, y + 368),
        "Both options play on the Android alarm stream, not",
        font=f_note,
        fill=INK_HINT,
    )
    draw.text(
        (pad + 51, y + 412),
        "the silent-ringer stream.",
        font=f_note,
        fill=INK_HINT,
    )

    y += sound_card_h + 34

    # Card 3: Dark mode
    dark_card_h = 200
    draw_card(
        draw,
        (pad, y, W - pad, y + dark_card_h),
        radius=48,
        fill=CARD,
        outline=OUTLINE,
    )
    draw.text((pad + 51, y + 42), "Dark mode", font=f_card_title, fill=INK)
    draw.text(
        (pad + 51, y + 108),
        "Use a darker, softer reminder space.",
        font=f_card_sub,
        fill=INK_MUTED,
    )

    # Checked switch on right
    sw_w, sw_h = 136, 76
    sw_x = W - pad - 51 - sw_w
    sw_y = y + (dark_card_h - sw_h) // 2
    draw.rounded_rectangle(
        (sw_x, sw_y, sw_x + sw_w, sw_y + sw_h), radius=38, fill=SAGE_LIGHT
    )
    draw.rounded_rectangle(
        (sw_x, sw_y, sw_x + sw_w, sw_y + sw_h),
        radius=38,
        outline=SAGE,
        width=3,
    )
    thumb_r = 28
    tcx = sw_x + sw_w - 38
    tcy = sw_y + sw_h // 2
    draw.ellipse(
        (tcx - thumb_r, tcy - thumb_r, tcx + thumb_r, tcy + thumb_r),
        fill=SAGE_DARK,
    )

    y += dark_card_h + 38

    # Privacy note at bottom
    f_priv = font("sans", 400, 33)
    priv_txt = "Settings are stored only on this device."
    pw = draw.textlength(priv_txt, font=f_priv)
    draw.text(((W - pw) / 2, y), priv_txt, font=f_priv, fill=INK_HINT)

    draw_bottom_dock(draw, "settings")
    save_screen(img, "settings")


def main() -> None:
    print("Building RemindME icons...")
    master_icon = build_icons()
    print("Building RemindME screenshots...")
    build_home_screen(master_icon)
    build_previous_screen()
    build_settings_screen()
    print("Done.")


if __name__ == "__main__":
    main()
