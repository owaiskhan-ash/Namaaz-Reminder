#!/usr/bin/env python3
"""Render the 1200x630 Open Graph cards for the four newer app pages.

Water Reminder, Step Reminder, RemindME and Arabic Clock were added to the
site after the first four cards, which each have their own per-app icon
pipeline (build_site_icons.py, build_screentime_icons.py,
build_subtracker_icons.py and the vaccine assets). Rather than duplicate that
layout a fourth time, this script carries one copy of it and renders the four
cards the newer pages point at:

  docs/assets/og/og-water-reminder.png
  docs/assets/og/og-step-reminder.png
  docs/assets/og/og-remindme.png
  docs/assets/og/og-arabic-clock.png

The layout, type sizes, leather tile and footer line match the existing
cards, so a shared link looks like the rest of the collection.

    python3 design/build_app_og_cards.py
"""

import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "docs", "assets")
OG_DIR = os.path.join(ASSETS, "og")
FONTS_DIR = os.path.join(ASSETS, "fonts")

W, H = 1200, 630
ICON = 304
PAD = 46

# (output, icon source, eyebrow, accent, headline, two sub lines)
CARDS = [
    (
        "og-water-reminder.png",
        os.path.join(ASSETS, "water", "icon-512.png"),
        "JUST APPS  ·  05  ·  HYDRATION",
        (0, 188, 200),
        "Water Reminder",
        [
            "One reminder every two hours, aligned to your",
            "clock. No intake log, no account, no network.",
        ],
    ),
    (
        "og-step-reminder.png",
        os.path.join(ASSETS, "steps", "icon-512.png"),
        "JUST APPS  ·  06  ·  MOVEMENT",
        (216, 194, 160),
        "Step Reminder",
        [
            "A daily step goal, one plain-spoken reminder",
            "and a seven-day trail. Nothing leaves the phone.",
        ],
    ),
    (
        "og-remindme.png",
        os.path.join(ASSETS, "remindme", "icon-512.png"),
        "JUST APPS  ·  07  ·  REMINDERS",
        (126, 200, 160),
        "RemindME",
        [
            "Write a reminder the way you would say it, in one",
            "of seven languages. Alarm-stream loud, always.",
        ],
    ),
    (
        "og-arabic-clock.png",
        os.path.join(ASSETS, "arabic-clock", "icon-512.png"),
        "JUST APPS  ·  08  ·  HOME SCREEN",
        (233, 196, 106),
        "Arabic Clock",
        [
            "Arabic-Indic numerals on a clock widget that is",
            "100% transparent, in six bundled offline fonts.",
        ],
    ),
]


def _background():
    card = Image.new("RGBA", (W, H), (23, 27, 25, 255))
    tile = Image.open(os.path.join(ASSETS, "materials",
                                   "charcoal-leather.webp")).convert("RGB")
    tw, th = tile.size
    for y in range(0, H, th):
        for x in range(0, W, tw):
            card.paste(tile, (x, y))
    overlay = Image.new("RGBA", (W, H), (14, 18, 17, 178))
    return Image.alpha_composite(card, overlay)


def _paste_icon(card, icon_path):
    icon = Image.open(icon_path).convert("RGBA")
    x, y = W - 112 - ICON, (H - ICON) // 2
    scaled = icon.resize((ICON, ICON), Image.LANCZOS)

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer = Image.new("RGBA", (ICON, ICON), (0, 0, 0, 175))
    layer.putalpha(scaled.split()[3])
    shadow.paste(layer, (x, y + 14))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=16))
    card = Image.alpha_composite(card, shadow)
    card.paste(scaled, (x, y), scaled)
    return card


def build(out_name, icon_path, eyebrow, accent, headline, sub_lines):
    card = _background()

    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle(
        (PAD, PAD, W - PAD, H - PAD),
        radius=28,
        fill=(19, 25, 24, 165),
        outline=accent + (105,),
        width=2,
    )

    card = _paste_icon(card, icon_path)

    f_eyebrow = ImageFont.truetype(
        os.path.join(FONTS_DIR, "plus-jakarta-sans-latin-600-normal.woff2"), 17)
    f_head = ImageFont.truetype(
        os.path.join(FONTS_DIR, "instrument-serif-latin-400-normal.woff2"), 80)
    f_sub = ImageFont.truetype(
        os.path.join(FONTS_DIR, "plus-jakarta-sans-latin-400-normal.woff2"), 24)
    f_foot = ImageFont.truetype(
        os.path.join(FONTS_DIR, "plus-jakarta-sans-latin-600-normal.woff2"), 15)

    draw = ImageDraw.Draw(card)
    tx, text_limit = 104, (W - 112 - ICON) - 104 - 40
    assert draw.textlength(headline, font=f_head) <= text_limit, headline
    for line in sub_lines:
        assert draw.textlength(line, font=f_sub) <= text_limit, line

    draw.text((tx, 166), eyebrow, font=f_eyebrow, fill=accent + (255,))
    draw.text((tx, 218), headline, font=f_head, fill=(247, 242, 232, 255))
    for i, line in enumerate(sub_lines):
        draw.text((tx, 336 + i * 36), line, font=f_sub, fill=(216, 194, 160, 240))
    draw.line([(tx, 444), (tx + 590, 444)], fill=(216, 194, 160, 52), width=1)
    draw.text(
        (tx, 468),
        "FREE   ·   NO ADS   ·   NO TRACKING   ·   ON-DEVICE",
        font=f_foot,
        fill=(240, 227, 204, 190),
    )

    os.makedirs(OG_DIR, exist_ok=True)
    path = os.path.join(OG_DIR, out_name)
    card.convert("RGB").save(path, "PNG", optimize=True)
    print("wrote", os.path.relpath(path, ROOT))


def main():
    for spec in CARDS:
        build(*spec)


if __name__ == "__main__":
    main()
