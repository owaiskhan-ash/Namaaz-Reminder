#!/usr/bin/env python3
"""Generates the Android launcher icon resources from the master artwork.

The master artwork is a dark plate with an engraved "NR" monogram. The relief
is very shallow, so the script first boosts it (unsharp mask) - otherwise the
monogram disappears at launcher sizes.

Usage:

    python3 scripts/generate_app_icons.py path/to/NR-icon.png

Produces:
  * mipmap-<density>/ic_launcher.png            legacy launcher icon
  * mipmap-<density>/ic_launcher_round.png      round launcher icon
  * mipmap-<density>/ic_launcher_foreground.png adaptive icon foreground
  * drawable/ic_app_icon.png                    logo used inside the app
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "app", "src", "main", "res")

# Legacy launcher icons are 48dp, adaptive icon layers are 108dp.
DENSITIES = {
    "mdpi": 48,
    "hdpi": 72,
    "xhdpi": 96,
    "xxhdpi": 144,
    "xxxhdpi": 192,
}
ADAPTIVE_SIZES = {
    "mdpi": 108,
    "hdpi": 162,
    "xhdpi": 216,
    "xxhdpi": 324,
    "xxxhdpi": 432,
}

# How much the engraved relief is boosted.
RELIEF_BOOST = 2.6
BLUR_RADIUS = 14


def save(image: Image.Image, *path: str) -> None:
    target = os.path.join(RES, *path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    image.save(target, "PNG", optimize=True)
    print(f"  + {os.path.relpath(target, ROOT)} ({image.size[0]}x{image.size[1]})")


def square(image: Image.Image) -> Image.Image:
    width, height = image.size
    side = min(width, height)
    return image.crop(
        ((width - side) // 2, (height - side) // 2, (width - side) // 2 + side, (height - side) // 2 + side)
    )


def boost_relief(image: Image.Image) -> Image.Image:
    """Makes the engraved monogram readable at small sizes."""
    grey = image.convert("L")
    pixels = grey.load()
    blurred = grey.filter(ImageFilter.GaussianBlur(BLUR_RADIUS)).load()
    width, height = grey.size

    boosted = Image.new("L", grey.size)
    out = boosted.load()
    for y in range(height):
        for x in range(width):
            value = pixels[x, y]
            detail = value - blurred[x, y]
            out[x, y] = max(0, min(255, int(value + detail * RELIEF_BOOST)))
    return boosted.convert("RGBA")


def circular_mask(size: int) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    return mask


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: generate_app_icons.py <master-icon.png>")
    source = sys.argv[1]
    if not os.path.exists(source):
        raise SystemExit(f"Master icon not found: {source}")

    master = square(Image.open(source).convert("RGBA"))
    artwork = boost_relief(master)
    # Keep the transparency of the original artwork.
    artwork.putalpha(master.getchannel("A"))
    print("Generated resources:")

    # 1) Legacy launcher icons.
    for density, size in DENSITIES.items():
        icon = artwork.resize((size, size), Image.LANCZOS)
        save(icon, f"mipmap-{density}", "ic_launcher.png")

        round_icon = icon.copy()
        round_icon.putalpha(
            Image.composite(icon.getchannel("A"), Image.new("L", (size, size), 0), circular_mask(size))
        )
        save(round_icon, f"mipmap-{density}", "ic_launcher_round.png")

    # 2) Adaptive icon foreground: the artwork inside the 66dp safe zone.
    for density, size in ADAPTIVE_SIZES.items():
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        inner = round(size * 66 / 108)
        art = artwork.resize((inner, inner), Image.LANCZOS)
        canvas.paste(art, ((size - inner) // 2, (size - inner) // 2), art)
        save(canvas, f"mipmap-{density}", "ic_launcher_foreground.png")

    # 3) The logo shown inside the app.
    save(artwork.resize((192, 192), Image.LANCZOS), "drawable", "ic_app_icon.png")

    # 4) The adaptive icon background is the flat colour of the plate.
    plate = artwork.convert("RGB").resize((32, 32), Image.LANCZOS).getpixel((16, 16))
    print(f"  = plate colour rgb{plate}")
    with open(os.path.join(RES, "values", "ic_launcher_colors.xml"), "w", encoding="utf-8") as handle:
        handle.write(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            "<resources>\n"
            f'    <color name="ic_launcher_background">#{plate[0]:02X}{plate[1]:02X}{plate[2]:02X}</color>\n'
            "</resources>\n"
        )
    print("  + values/ic_launcher_colors.xml")


if __name__ == "__main__":
    main()
