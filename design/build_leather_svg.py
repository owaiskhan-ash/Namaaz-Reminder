#!/usr/bin/env python3
"""Generate sculpted organic leather & suede SVG background stages for JUST APPS.

Produces HTML/SVG snippets in design/generated_stages.json with:
  - Smooth closed C1 cubic Bezier silhouettes (hand-cut leather & suede pads)
  - Per-flap rotated seamless WebP macro material patterns
  - Directional studio lighting & pillowed bevel shading
  - Burnished raw-hide cut-edge highlights & 3mm underside hide thickness
  - Mathematically exact inward-offset saddle stitching on selected leather flaps
  - Dual-stage ambient occlusion contact shadows + soft studio cast shadows
  - Semantic left/right/center groups for responsive tablet & mobile framing
"""

import json
import os
import numpy as np

OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_stages.json")


def catmull_rom_closed_svg_and_points(pts, samples_per_seg=44, tension=0.5):
    pts = np.array(pts, dtype=np.float64)
    n = len(pts)
    svg_cmds = []
    dense = []
    for i in range(n):
        p0 = pts[(i - 1) % n]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n]
        c1 = p1 + (p2 - p0) / (6.0 / (tension * 2.0))
        c2 = p2 - (p3 - p1) / (6.0 / (tension * 2.0))
        if i == 0:
            svg_cmds.append(f"M {p1[0]:.1f} {p1[1]:.1f}")
        svg_cmds.append(
            f"C {c1[0]:.1f} {c1[1]:.1f}, {c2[0]:.1f} {c2[1]:.1f}, {p2[0]:.1f} {p2[1]:.1f}"
        )
        t = np.linspace(0.0, 1.0, samples_per_seg, endpoint=False)[:, None]
        seg = (
            ((1 - t) ** 3) * p1
            + 3 * ((1 - t) ** 2) * t * c1
            + 3 * (1 - t) * (t ** 2) * c2
            + (t ** 3) * p2
        )
        dense.append(seg)
    svg_cmds.append("Z")
    return " ".join(svg_cmds), np.vstack(dense)


def signed_area(poly):
    x, y = poly[:, 0], poly[:, 1]
    return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)


def offset_closed_polyline_svg(dense_pts, inward_dist=13.5, subsample=18):
    sign = 1.0 if signed_area(dense_pts) > 0 else -1.0
    tang = np.roll(dense_pts, -1, axis=0) - np.roll(dense_pts, 1, axis=0)
    tang /= np.linalg.norm(tang, axis=1, keepdims=True) + 1e-8
    normals = sign * np.column_stack([-tang[:, 1], tang[:, 0]])
    off = dense_pts + inward_dist * normals
    for _ in range(5):
        off = 0.25 * np.roll(off, 1, axis=0) + 0.5 * off + 0.25 * np.roll(off, -1, axis=0)
    path_str, _ = catmull_rom_closed_svg_and_points(off[::subsample], samples_per_seg=6)
    return path_str


MATERIALS = {
    "teal-suede": {
        "file": "/assets/materials/teal-suede.webp",
        "fallback": "#064B4D",
        "edge_dark": "#032426",
        "bevel_tint": "#022224",
        "bevel_op": 0.46,
        "rim_light": "#55DCE6",
        "rim_opacity": 0.45,
        "stitch_light": "#8EE8F0",
        "key_light": "#2BE0EC",
        "key_opacity": 0.16,
    },
    "cyan-leather": {
        "file": "/assets/materials/cyan-leather.webp",
        "fallback": "#00BCC8",
        "edge_dark": "#044045",
        "bevel_tint": "#03383D",
        "bevel_op": 0.40,
        "rim_light": "#9EFAFF",
        "rim_opacity": 0.62,
        "stitch_light": "#D4F9FC",
        "key_light": "#A8FAFF",
        "key_opacity": 0.20,
    },
    "beige-suede": {
        "file": "/assets/materials/beige-suede.webp",
        "fallback": "#D8C2A0",
        "edge_dark": "#755F42",
        "bevel_tint": "#8F734F",
        "bevel_op": 0.28,
        "rim_light": "#FFF8EB",
        "rim_opacity": 0.80,
        "stitch_light": "#FFF9EE",
        "key_light": "#FFFDF7",
        "key_opacity": 0.22,
    },
    "cream-suede": {
        "file": "/assets/materials/cream-suede.webp",
        "fallback": "#F0E3CC",
        "edge_dark": "#857156",
        "bevel_tint": "#9E886B",
        "bevel_op": 0.24,
        "rim_light": "#FFFFFF",
        "rim_opacity": 0.84,
        "stitch_light": "#FFFFFF",
        "key_light": "#FFFFFF",
        "key_opacity": 0.20,
    },
    "rust-leather": {
        "file": "/assets/materials/rust-leather.webp",
        "fallback": "#B9572D",
        "edge_dark": "#551F0A",
        "bevel_tint": "#5C210B",
        "bevel_op": 0.42,
        "rim_light": "#F7AC85",
        "rim_opacity": 0.62,
        "stitch_light": "#EDD1B7",
        "key_light": "#FFC39E",
        "key_opacity": 0.20,
    },
    "olive-suede": {
        "file": "/assets/materials/olive-suede.webp",
        "fallback": "#62653A",
        "edge_dark": "#2D3018",
        "bevel_tint": "#2E3118",
        "bevel_op": 0.40,
        "rim_light": "#C7CD92",
        "rim_opacity": 0.54,
        "stitch_light": "#E1E3C5",
        "key_light": "#DCE2A6",
        "key_opacity": 0.18,
    },
    "brown-leather": {
        "file": "/assets/materials/brown-leather.webp",
        "fallback": "#38251E",
        "edge_dark": "#160D0A",
        "bevel_tint": "#140B08",
        "bevel_op": 0.48,
        "rim_light": "#845E50",
        "rim_opacity": 0.42,
        "stitch_light": "#BFA492",
        "key_light": "#9A6E5C",
        "key_opacity": 0.16,
    },
}


def build_stage_svg(stage_id, width, height, flaps, extra_class=""):
    defs = [
        f"""
    <filter id="sh-{stage_id}" x="-14%" y="-14%" width="132%" height="136%" color-interpolation-filters="sRGB">
      <feDropShadow dx="9" dy="20" stdDeviation="16" flood-color="#020505" flood-opacity="0.58"/>
      <feDropShadow dx="2" dy="3.5" stdDeviation="2.4" flood-color="#010303" flood-opacity="0.84"/>
    </filter>
    <filter id="bv-{stage_id}" x="-8%" y="-8%" width="116%" height="116%">
      <feGaussianBlur stdDeviation="7.5"/>
    </filter>"""
    ]

    groups = {"center": [], "left": [], "right": []}

    for f in flaps:
        fid = f"{stage_id}-{f['id']}"
        m = MATERIALS[f["mat"]]
        path_d, dense_pts = catmull_rom_closed_svg_and_points(f["pts"], samples_per_seg=42)
        xmin, ymin = dense_pts.min(axis=0)
        xmax, ymax = dense_pts.max(axis=0)

        defs.append(
            f"""
    <path id="p-{fid}" d="{path_d}"/>
    <pattern id="pat-{fid}" patternUnits="userSpaceOnUse" width="512" height="512" patternTransform="rotate({f['rot']})">
      <rect width="512" height="512" fill="{m['fallback']}"/>
      <image href="{m['file']}" x="0" y="0" width="512" height="512" preserveAspectRatio="none"/>
    </pattern>
    <clipPath id="clip-{fid}">
      <use href="#p-{fid}"/>
    </clipPath>
    <linearGradient id="lt-{fid}" gradientUnits="userSpaceOnUse" x1="{xmin:.0f}" y1="{ymin:.0f}" x2="{xmax:.0f}" y2="{ymax:.0f}">
      <stop offset="0%" stop-color="{m['key_light']}" stop-opacity="{m['key_opacity']}"/>
      <stop offset="48%" stop-color="#000000" stop-opacity="0"/>
      <stop offset="100%" stop-color="#030606" stop-opacity="0.34"/>
    </linearGradient>"""
        )

        stitch_markup = ""
        if f.get("stitch"):
            stitch_d = offset_closed_polyline_svg(dense_pts, inward_dist=13.5, subsample=18)
            defs.append(f'\n    <path id="st-{fid}" d="{stitch_d}"/>')
            stitch_markup = f"""
        <use href="#st-{fid}" fill="none" stroke="#050404" stroke-opacity="0.30" stroke-width="1.9"/>
        <use href="#st-{fid}" transform="translate(0.5, 0.7)" fill="none" stroke="#040303" stroke-opacity="0.52" stroke-width="1.2" stroke-dasharray="5.8 4.4" stroke-linecap="round"/>
        <use href="#st-{fid}" fill="none" stroke="{m['stitch_light']}" stroke-opacity="0.48" stroke-width="1.05" stroke-dasharray="5.8 4.4" stroke-linecap="round"/>"""

        side = f.get("side", "center")
        if side == "center":
            depth_cls = "flap-depth-base"
        elif f.get("stitch") or len(groups[side]) % 2 == 1:
            depth_cls = "flap-depth-over"
        else:
            depth_cls = "flap-depth-under"

        cls = f"{f.get('cls', '')} {depth_cls}".strip()
        cls_attr = f' class="{cls}"' if cls else ""
        flap_svg = f"""
      <g{cls_attr}>
        <use href="#p-{fid}" fill="{m['edge_dark']}" filter="url(#sh-{stage_id})"/>
        <use href="#p-{fid}" transform="translate(2.2, 3.2)" fill="{m['edge_dark']}"/>
        <g clip-path="url(#clip-{fid})">
          <use href="#p-{fid}" fill="url(#pat-{fid})"/>
          <use href="#p-{fid}" fill="url(#lt-{fid})"/>
          <use href="#p-{fid}" fill="none" stroke="{m['bevel_tint']}" stroke-opacity="{m['bevel_op']}" stroke-width="22" filter="url(#bv-{stage_id})"/>
          <use href="#p-{fid}" transform="translate(1.6, 2.0)" fill="none" stroke="{m['rim_light']}" stroke-opacity="{m['rim_opacity']}" stroke-width="2.1"/>
          <use href="#p-{fid}" transform="translate(-1.4, -1.6)" fill="none" stroke="{m['edge_dark']}" stroke-opacity="0.52" stroke-width="2.2"/>{stitch_markup}
        </g>
      </g>"""

        groups[f.get("side", "center")].append(flap_svg)

    center_block = f'\n    <g class="flaps-center">{"".join(groups["center"])}\n    </g>' if groups["center"] else ""
    left_block = f'\n    <g class="flaps-left">{"".join(groups["left"])}\n    </g>' if groups["left"] else ""
    right_block = f'\n    <g class="flaps-right">{"".join(groups["right"])}\n    </g>' if groups["right"] else ""

    cls_svg = f"leather-svg {extra_class}".strip()
    return (
        f'<svg class="{cls_svg}" viewBox="0 0 {width} {height}" '
        f'preserveAspectRatio="xMidYMin slice" aria-hidden="true" focusable="false">'
        f"\n  <defs>{''.join(defs)}\n  </defs>"
        f"{center_block}{left_block}{right_block}\n</svg>"
    )


# ---------------------------------------------------------------------------
# Stage 1: Header + Hero + Hero-to-Collection Transition + Collection Header
# ViewBox: 1600 x 1260 (extra headroom at bottom so all shadows settle naturally!)
# ---------------------------------------------------------------------------
STAGE_TOP_FLAPS = [
    # Broad asymmetric Dark Chocolate Espresso hide behind Hero, curving down right above Collection divider
    {
        "id": "hero-espresso",
        "side": "center",
        "cls": "flap-espresso-hero",
        "mat": "brown-leather",
        "rot": -11,
        "stitch": False,
        "pts": [
            (-220, -160), (680, -170), (1410, -140),
            (1325, 175), (1240, 382), (985, 512),
            (635, 540), (305, 488), (-230, 340),
        ],
    },
    # Left earthy Olive Moss Suede tucked beneath Beige Suede
    {
        "id": "left-olive",
        "side": "left",
        "cls": "flap-mobile-soft",
        "mat": "olive-suede",
        "rot": 26,
        "stitch": False,
        "pts": [
            (-240, 225), (85, 240), (262, 335),
            (338, 495), (248, 645), (55, 720), (-240, 755),
        ],
    },
    # Upper-Left S-Curved Warm Sandy Beige Suede (starts just below 66px header so nav stays ultra-crisp!)
    {
        "id": "upper-left-beige",
        "side": "left",
        "mat": "beige-suede",
        "rot": -18,
        "stitch": False,
        "pts": [
            (-230, 70), (155, 74), (332, 142),
            (296, 268), (212, 372), (132, 460),
            (-45, 518), (-240, 480),
        ],
    },
    # Left-to-Collection Stitched Cyan-Teal Brand Leather Fold (crossing Hero -> Collection boundary!)
    {
        "id": "lower-left-cyan",
        "side": "left",
        "mat": "cyan-leather",
        "rot": -31,
        "stitch": True,
        "pts": [
            (-240, 512), (98, 518), (318, 592),
            (342, 720), (198, 848), (28, 912), (-250, 932),
        ],
    },
    # Lower-Left Light Cream Suede Flap (framing the Collection heading & top-left of App Gallery!)
    {
        "id": "lower-left-cream",
        "side": "left",
        "cls": "flap-mobile-soft",
        "mat": "cream-suede",
        "rot": 15,
        "stitch": False,
        "pts": [
            (-250, 735), (55, 752), (225, 858),
            (252, 1015), (112, 1138), (-250, 1168),
        ],
    },
    # Upper-Right Stitched S-Curved Cyan-Teal Brand Leather Tongue
    {
        "id": "upper-right-cyan",
        "side": "right",
        "mat": "cyan-leather",
        "rot": 22,
        "stitch": True,
        "pts": [
            (1215, -130), (1790, -120), (1830, 485),
            (1525, 502), (1345, 392), (1295, 255),
            (1235, 115),
        ],
    },
    # Upper-Right Warm Sand Suede Corner Overlap (positioned past x=1435 at top so nav icons stay high-contrast!)
    {
        "id": "top-right-sand",
        "side": "right",
        "cls": "flap-mobile-soft",
        "mat": "beige-suede",
        "rot": 34,
        "stitch": False,
        "pts": [
            (1445, -120), (1830, -110), (1840, 305),
            (1615, 275), (1485, 155), (1438, 18),
        ],
    },
    # Right Sweeping Pebbled Burnt-Orange Leather Flap (stitched, crossing Hero -> Collection boundary!)
    {
        "id": "right-rust",
        "side": "right",
        "mat": "rust-leather",
        "rot": -24,
        "stitch": True,
        "pts": [
            (1545, 242), (1840, 265), (1850, 855),
            (1515, 872), (1308, 752), (1218, 590),
            (1252, 432), (1380, 305),
        ],
    },
    # Lower-Right Earthy Olive Suede Flap (tucked beside Collection opening)
    {
        "id": "lower-right-olive",
        "side": "right",
        "cls": "flap-mobile-soft",
        "mat": "olive-suede",
        "rot": 29,
        "stitch": False,
        "pts": [
            (1485, 738), (1840, 755), (1840, 1165),
            (1415, 1155), (1298, 1012), (1342, 852),
        ],
    },
]

# ---------------------------------------------------------------------------
# Stage 2: Lower Collection Gallery -> Our Approach (#features) -> Studio (#about)
# ViewBox: 1600 x 1360
# ---------------------------------------------------------------------------
STAGE_MID_FLAPS = [
    # Left Olive Moss Suede under-pad
    {
        "id": "mid-left-olive",
        "side": "left",
        "cls": "flap-mobile-soft",
        "mat": "olive-suede",
        "rot": -22,
        "stitch": False,
        "pts": [
            (-240, 90), (45, 110), (198, 225),
            (215, 395), (75, 520), (-240, 555),
        ],
    },
    # Left Pebbled Burnt-Orange Leather crossing Collection -> Our Approach
    {
        "id": "mid-left-rust",
        "side": "left",
        "mat": "rust-leather",
        "rot": 19,
        "stitch": True,
        "pts": [
            (-240, 310), (72, 332), (228, 455),
            (205, 635), (58, 760), (-240, 795),
        ],
    },
    # Lower-Mid Left Cyan-Teal Brand Leather bridging Our Approach -> Studio
    {
        "id": "mid-left-cyan",
        "side": "left",
        "mat": "cyan-leather",
        "rot": -16,
        "stitch": False,
        "pts": [
            (-240, 780), (48, 800), (188, 918),
            (172, 1085), (32, 1195), (-240, 1225),
        ],
    },
    # Right Dark Chocolate Leather under-flap
    {
        "id": "mid-right-brown",
        "side": "right",
        "cls": "flap-mobile-soft",
        "mat": "brown-leather",
        "rot": 14,
        "stitch": False,
        "pts": [
            (1520, 130), (1840, 145), (1840, 620),
            (1495, 605), (1378, 465), (1395, 285),
        ],
    },
    # Right Warm Sandy Beige Suede crossing Collection -> Our Approach
    {
        "id": "mid-right-beige",
        "side": "right",
        "mat": "beige-suede",
        "rot": -27,
        "stitch": False,
        "pts": [
            (1540, 365), (1840, 385), (1840, 860),
            (1515, 845), (1385, 705), (1402, 520),
        ],
    },
    # Right Stitched Cyan-Teal Brand Leather beside Studio section
    {
        "id": "mid-right-cyan",
        "side": "right",
        "mat": "cyan-leather",
        "rot": 24,
        "stitch": True,
        "pts": [
            (1535, 815), (1840, 830), (1840, 1255),
            (1505, 1240), (1392, 1105), (1412, 945),
        ],
    },
]

# ---------------------------------------------------------------------------
# Stage 3: FAQ (#faq) -> Espresso Leather Footer Apron
# ViewBox: 1600 x 960
# ---------------------------------------------------------------------------
STAGE_BOT_FLAPS = [
    # Bottom Espresso Dark Chocolate Leather Footer Apron (curves up gently behind Footer!)
    {
        "id": "footer-espresso",
        "side": "center",
        "mat": "brown-leather",
        "rot": 9,
        "stitch": False,
        "pts": [
            (-220, 745), (360, 705), (840, 692),
            (1290, 720), (1820, 760), (1820, 1080),
            (-220, 1080),
        ],
    },
    # Left Warm Sandy Beige Suede beside FAQ
    {
        "id": "bot-left-beige",
        "side": "left",
        "mat": "beige-suede",
        "rot": 21,
        "stitch": False,
        "pts": [
            (-240, 140), (52, 162), (205, 285),
            (188, 465), (42, 590), (-240, 625),
        ],
    },
    # Left Olive Moss Suede overlapping into Footer corner
    {
        "id": "bot-left-olive",
        "side": "left",
        "cls": "flap-mobile-soft",
        "mat": "olive-suede",
        "rot": -19,
        "stitch": False,
        "pts": [
            (-240, 495), (38, 520), (178, 645),
            (155, 815), (-10, 920), (-240, 945),
        ],
    },
    # Right Stitched Pebbled Burnt-Orange Leather beside FAQ
    {
        "id": "bot-right-rust",
        "side": "right",
        "mat": "rust-leather",
        "rot": -17,
        "stitch": True,
        "pts": [
            (1535, 175), (1840, 195), (1840, 665),
            (1510, 648), (1388, 515), (1408, 330),
        ],
    },
    # Right Cyan-Teal Brand Leather overlapping Footer corner
    {
        "id": "bot-right-cyan",
        "side": "right",
        "cls": "flap-mobile-soft",
        "mat": "cyan-leather",
        "rot": 28,
        "stitch": False,
        "pts": [
            (1545, 540), (1840, 560), (1840, 945),
            (1495, 930), (1398, 795), (1422, 645),
        ],
    },
]

# ---------------------------------------------------------------------------
# Subpage Stage: Compact Atelier Header/Hero Frame for App Detail & Privacy Pages
# ViewBox: 1600 x 680
# ---------------------------------------------------------------------------
STAGE_SUB_FLAPS = [
    {
        "id": "sub-espresso",
        "side": "center",
        "mat": "brown-leather",
        "rot": -9,
        "stitch": False,
        "pts": [
            (-220, -140), (740, -150), (1420, -130),
            (1310, 155), (1180, 315), (860, 392),
            (480, 382), (180, 310), (-230, 195),
        ],
    },
    {
        "id": "sub-left-beige",
        "side": "left",
        "mat": "beige-suede",
        "rot": -18,
        "stitch": False,
        "pts": [
            (-230, 68), (95, 76), (228, 158),
            (205, 295), (72, 405), (-230, 445),
        ],
    },
    {
        "id": "sub-left-cyan",
        "side": "left",
        "cls": "flap-mobile-soft",
        "mat": "cyan-leather",
        "rot": 24,
        "stitch": True,
        "pts": [
            (-240, 325), (58, 345), (185, 442),
            (155, 565), (-20, 635), (-240, 650),
        ],
    },
    {
        "id": "sub-right-cyan",
        "side": "right",
        "mat": "cyan-leather",
        "rot": 20,
        "stitch": True,
        "pts": [
            (1285, -120), (1820, -110), (1830, 365),
            (1535, 375), (1375, 265), (1315, 110),
        ],
    },
    {
        "id": "sub-right-rust",
        "side": "right",
        "cls": "flap-mobile-soft",
        "mat": "rust-leather",
        "rot": -23,
        "stitch": True,
        "pts": [
            (1550, 210), (1840, 230), (1840, 635),
            (1515, 620), (1395, 495), (1420, 335),
        ],
    },
]


def main():
    stages = {
        "top": build_stage_svg("s1", 1600, 1260, STAGE_TOP_FLAPS, "leather-svg-top"),
        "mid": build_stage_svg("s2", 1600, 1360, STAGE_MID_FLAPS, "leather-svg-mid"),
        "bot": build_stage_svg("s3", 1600, 960, STAGE_BOT_FLAPS, "leather-svg-bot"),
        "sub": build_stage_svg("ss", 1600, 680, STAGE_SUB_FLAPS, "leather-svg-sub"),
    }
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(stages, fh, indent=2)
    for k, v in stages.items():
        print(f"Stage '{k}': {len(v)} chars")


if __name__ == "__main__":
    main()
