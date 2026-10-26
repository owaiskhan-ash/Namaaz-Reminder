#!/usr/bin/env python3
"""
Screen Time Reminder: web icon & Open Graph social card pipeline.

Derives all website icon sizes and the Open Graph card directly from the
approved leather, felt & suede `ST` artwork at `design/source/ST-icon.png`
(`online.justsimpleapps.screentime` v1.2.3).

Outputs:
  * docs/assets/screentime/icon-64.png               small mark
  * docs/assets/screentime/icon-128.png              app card (1x)
  * docs/assets/screentime/icon-256.png              retina app card (2x)
  * docs/assets/screentime/icon-512.png              schema / 3x mark
  * docs/assets/og/og-screen-time-reminder.png       1200x630 Open Graph card

Run:  python3 design/build_screentime_icons.py
"""

from __future__ import annotations

import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "design", "source", "ST-icon.png")
ASSETS = os.path.join(ROOT, "docs", "assets")
OUT = os.path.join(ASSETS, "screentime")
OG_OUT = os.path.join(ASSETS, "og", "og-screen-time-reminder.png")
FONTS_DIR = os.path.join(ASSETS, "fonts")


def _build_og_card(st_icon_512: Image.Image) -> None:
    """Render docs/assets/og/og-screen-time-reminder.png (1200x630) matching og-namaaz-reminder.png."""
    w, h = 1200, 630
    bg_tile = Image.open(os.path.join(ASSETS, "materials", "charcoal-leather.webp")).convert("RGB")
    card = Image.new("RGBA", (w, h), (23, 27, 25, 255))
    tw, th = bg_tile.size
    for y in range(0, h, th):
        for x in range(0, w, tw):
            card.paste(bg_tile, (x, y))

    ov = Image.new("RGBA", (w, h), (14, 18, 17, 178))
    card = Image.alpha_composite(card, ov)

    draw = ImageDraw.Draw(card)
    pad = 46
    draw.rounded_rectangle(
        (pad, pad, w - pad, h - pad),
        radius=28,
        fill=(19, 25, 24, 165),
        outline=(3, 177, 194, 105),
        width=2,
    )

    icon_sz = 304
    icon_x, icon_y = w - 112 - icon_sz, (h - icon_sz) // 2
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh_alpha = st_icon_512.resize((icon_sz, icon_sz), Image.LANCZOS).split()[3]
    sh_layer = Image.new("RGBA", (icon_sz, icon_sz), (0, 0, 0, 175))
    sh_layer.putalpha(sh_alpha)
    shadow.paste(sh_layer, (icon_x, icon_y + 14))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=16))
    card = Image.alpha_composite(card, shadow)

    st_resized = st_icon_512.resize((icon_sz, icon_sz), Image.LANCZOS)
    card.paste(st_resized, (icon_x, icon_y), st_resized)

    draw = ImageDraw.Draw(card)
    f_eyebrow = ImageFont.truetype(os.path.join(FONTS_DIR, "plus-jakarta-sans-latin-600-normal.woff2"), 17)
    f_head = ImageFont.truetype(os.path.join(FONTS_DIR, "instrument-serif-latin-400-normal.woff2"), 80)
    f_sub = ImageFont.truetype(os.path.join(FONTS_DIR, "plus-jakarta-sans-latin-400-normal.woff2"), 24)
    f_foot = ImageFont.truetype(os.path.join(FONTS_DIR, "plus-jakarta-sans-latin-600-normal.woff2"), 15)

    tx = 104
    draw.text((tx, 166), "JUST APPS  ·  02  ·  WELLBEING", font=f_eyebrow, fill=(3, 177, 194, 255))
    draw.text((tx, 218), "Screen Time Reminder", font=f_head, fill=(247, 242, 232, 255))
    draw.text((tx, 336), "Counts continuous screen time and sends one", font=f_sub, fill=(216, 194, 160, 240))
    draw.text((tx, 372), "calm reminder when it is time to look up.", font=f_sub, fill=(216, 194, 160, 240))
    draw.line([(tx, 444), (tx + 590, 444)], fill=(216, 194, 160, 52), width=1)
    draw.text(
        (tx, 468),
        "FREE   ·   NO ADS   ·   NO TRACKING   ·   ON-DEVICE",
        font=f_foot,
        fill=(240, 227, 204, 190),
    )

    os.makedirs(os.path.dirname(OG_OUT), exist_ok=True)
    card.convert("RGB").save(OG_OUT, "PNG", optimize=True)
    print("wrote", os.path.relpath(OG_OUT, ROOT))


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    master = Image.open(SOURCE).convert("RGBA")
    rendered = {}
    for size in (64, 128, 256, 512):
        img = master.resize((size, size), Image.LANCZOS)
        rendered[size] = img
        path = os.path.join(OUT, f"icon-{size}.png")
        img.save(path, "PNG", optimize=True)
        print("wrote", os.path.relpath(path, ROOT))

    _build_og_card(rendered[512])


if __name__ == "__main__":
    main()
