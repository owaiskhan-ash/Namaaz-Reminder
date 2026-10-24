#!/usr/bin/env python3
"""Build the SC Step Reminder website icons, responsive screenshots and social card.

The icon and screenshots come from the SC Step Reminder v1.1.0 source and running
app. Keep the 800 × 1732 PNG screenshots beside the generated WebP files as the
sources for future exports.

Run: python3 design/build_steps_assets.py
"""

from __future__ import annotations

import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "design", "source", "SC-step-icon.png")
ASSETS = os.path.join(ROOT, "docs", "assets")
OUT = os.path.join(ASSETS, "steps")
OG_OUT = os.path.join(ASSETS, "og", "og-step-reminder.png")
FONTS_DIR = os.path.join(ASSETS, "fonts")
SHOTS = ("today", "history", "settings")


def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(os.path.join(FONTS_DIR, name), size)


def _build_og_card(icon: Image.Image) -> None:
    """Render the 1200 × 630 Open Graph card in the Just Apps OG suite style."""
    width, height = 1200, 630
    bg_tile = Image.open(os.path.join(ASSETS, "materials", "charcoal-leather.webp")).convert("RGB")
    card = Image.new("RGBA", (width, height), (23, 27, 25, 255))
    tile_w, tile_h = bg_tile.size
    for y in range(0, height, tile_h):
        for x in range(0, width, tile_w):
            card.paste(bg_tile, (x, y))
    card = Image.alpha_composite(card, Image.new("RGBA", card.size, (14, 18, 17, 178)))

    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle(
        (46, 46, width - 46, height - 46),
        radius=28,
        fill=(19, 25, 24, 165),
        outline=(198, 155, 104, 135),
        width=2,
    )

    icon_size = 304
    icon_x, icon_y = width - 112 - icon_size, (height - icon_size) // 2
    resized = icon.resize((icon_size, icon_size), Image.LANCZOS)
    mask = Image.new("L", (icon_size, icon_size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, icon_size, icon_size), radius=66, fill=255)

    shadow = Image.new("RGBA", card.size, (0, 0, 0, 0))
    shadow_layer = Image.new("RGBA", (icon_size, icon_size), (0, 0, 0, 178))
    shadow_layer.putalpha(mask)
    shadow.paste(shadow_layer, (icon_x, icon_y + 14), shadow_layer)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=16))
    card = Image.alpha_composite(card, shadow)
    card.paste(resized, (icon_x, icon_y), mask)

    draw = ImageDraw.Draw(card)
    eyebrow = _font("plus-jakarta-sans-latin-600-normal.woff2", 17)
    headline = _font("instrument-serif-latin-400-normal.woff2", 78)
    body = _font("plus-jakarta-sans-latin-400-normal.woff2", 23)
    foot = _font("plus-jakarta-sans-latin-600-normal.woff2", 15)

    text_x = 104
    draw.text((text_x, 166), "JUST APPS  ·  05  ·  MOVEMENT", font=eyebrow, fill=(198, 155, 104, 255))
    draw.text((text_x, 218), "SC Step Reminder", font=headline, fill=(247, 242, 232, 255))
    draw.text((text_x, 336), "A daily step target, motion-sensor counting and", font=body, fill=(216, 194, 160, 240))
    draw.text((text_x, 372), "one local nudge at the hour you choose.", font=body, fill=(216, 194, 160, 240))
    draw.line([(text_x, 444), (text_x + 590, 444)], fill=(216, 194, 160, 52), width=1)
    draw.text(
        (text_x, 468),
        "FREE   ·   NO ADS   ·   NO ACCOUNT   ·   ON-DEVICE",
        font=foot,
        fill=(240, 227, 204, 190),
    )

    os.makedirs(os.path.dirname(OG_OUT), exist_ok=True)
    card.convert("RGB").save(OG_OUT, "PNG", optimize=True)
    print("wrote", os.path.relpath(OG_OUT, ROOT))


def _build_screenshots() -> None:
    for name in SHOTS:
        source = os.path.join(OUT, f"{name}.png")
        image = Image.open(source).convert("RGB")
        if image.size != (800, 1732):
            raise ValueError(f"{source}: expected an 800 × 1732 source screenshot, got {image.size}")
        for width, height in ((400, 866), (780, 1688)):
            output = os.path.join(OUT, f"{name}-{width}.webp")
            image.resize((width, height), Image.LANCZOS).save(
                output, "WEBP", quality=88, method=6
            )
            print("wrote", os.path.relpath(output, ROOT))


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    master = Image.open(SOURCE).convert("RGB")
    for size in (64, 128, 256, 512):
        output = os.path.join(OUT, f"icon-{size}.png")
        master.resize((size, size), Image.LANCZOS).save(output, "PNG", optimize=True)
        print("wrote", os.path.relpath(output, ROOT))
    _build_screenshots()
    _build_og_card(master)


if __name__ == "__main__":
    main()
