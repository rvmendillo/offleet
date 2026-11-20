#!/usr/bin/env python3
"""Generate Offleet brand assets (app icon, launch logo, README banner).

The Offleet mark: two bracket-like arcs (the two pointers) around an amber
pill (the sliding window), forming a stylised "O". Pure PIL, no external files.

Usage: python3 scripts/brand/make_icons.py
"""
import json
import math
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, "Offleet", "Resources", "Assets.xcassets")
DOCS = os.path.join(ROOT, "docs", "brand")

# Brand palette (keep in sync with Offleet/Brand/Brand.swift)
VIOLET = (109, 40, 217)
INDIGO = (67, 56, 202)
CYAN = (8, 145, 178)
INK = (11, 16, 38)
WHITE = (255, 255, 255)
AQUA = (103, 232, 249)
AMBER = (251, 191, 36)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def gradient(w, h=None):
    """Diagonal violet -> indigo -> cyan gradient with a soft top-left glow."""
    h = h or w
    small = 256
    img = Image.new("RGB", (small, small))
    px = img.load()
    for y in range(small):
        for x in range(small):
            t = (x + y) / (2 * (small - 1))
            c = lerp(VIOLET, INDIGO, t / 0.55) if t < 0.55 else lerp(INDIGO, CYAN, (t - 0.55) / 0.45)
            px[x, y] = c
    img = img.resize((w, h), Image.BICUBIC)
    glow = Image.new("L", (w, h), 0)
    ImageDraw.Draw(glow).ellipse((-w * 0.25, -h * 0.35, w * 0.75, h * 0.55), fill=45)
    glow = glow.filter(ImageFilter.GaussianBlur(w * 0.12))
    img = Image.composite(Image.new("RGB", (w, h), (255, 255, 255)), img, glow)
    return img


def draw_mark(draw, cx, cy, s, left=WHITE, right=AQUA, pill=AMBER):
    """Draw the Offleet mark centred at (cx, cy); s = overall mark diameter."""
    r_out = s / 2
    w = s * 0.17
    r_mid = r_out - w / 2
    box = (cx - r_out, cy - r_out, cx + r_out, cy + r_out)

    def arc(start, end, color):
        draw.arc(box, start=start, end=end, fill=color, width=int(w))
        for ang in (start, end):
            a = math.radians(ang)
            x, y = cx + r_mid * math.cos(a), cy + r_mid * math.sin(a)
            draw.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=color)

    arc(118, 242, left)    # left pointer
    arc(-62, 62, right)    # right pointer
    pw, ph = s * 0.46, s * 0.16
    draw.rounded_rectangle((cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2), radius=ph / 2, fill=pill)


def app_icon(path, size=1024):
    scale = 4
    big = size * scale
    img = gradient(big, big)
    d = ImageDraw.Draw(img)
    draw_mark(d, big / 2, big / 2, big * 0.56)
    img = img.resize((size, size), Image.LANCZOS)
    img.save(path, "PNG")


def mark_png(path, px, bg=None):
    scale = 4
    big = px * scale
    img = Image.new("RGBA", (big, big), bg or (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    draw_mark(d, big / 2, big / 2, big * 0.92)
    img.resize((px, px), Image.LANCZOS).save(path, "PNG")


def banner(path):
    w, h = 1600, 640
    scale = 2
    img = gradient(w * scale, h * scale)
    d = ImageDraw.Draw(img)
    draw_mark(d, 330 * scale, h * scale / 2, 330 * scale)
    font_path = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
    sub_path = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
    try:
        f = ImageFont.truetype(font_path, 170 * scale)
        f2 = ImageFont.truetype(sub_path, 46 * scale)
    except OSError:
        f = f2 = ImageFont.load_default()
    d.text((560 * scale, 170 * scale), "offleet", font=f, fill=WHITE)
    d.text((566 * scale, 400 * scale), "Interview prep that works offline.", font=f2, fill=(224, 231, 255))
    img.resize((w, h), Image.LANCZOS).save(path, "PNG")


def write_json(path, obj):
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=2)
        fh.write("\n")


def main():
    os.makedirs(DOCS, exist_ok=True)
    # Asset catalog root
    os.makedirs(ASSETS, exist_ok=True)
    write_json(os.path.join(ASSETS, "Contents.json"), {"info": {"author": "xcode", "version": 1}})

    icon_dir = os.path.join(ASSETS, "AppIcon.appiconset")
    os.makedirs(icon_dir, exist_ok=True)
    app_icon(os.path.join(icon_dir, "AppIcon.png"))
    write_json(os.path.join(icon_dir, "Contents.json"), {
        "images": [{"filename": "AppIcon.png", "idiom": "universal", "platform": "ios", "size": "1024x1024"}],
        "info": {"author": "xcode", "version": 1},
    })

    logo_dir = os.path.join(ASSETS, "LaunchLogo.imageset")
    os.makedirs(logo_dir, exist_ok=True)
    imgs = []
    for sc in (1, 2, 3):
        name = f"LaunchLogo@{sc}x.png" if sc > 1 else "LaunchLogo.png"
        mark_png(os.path.join(logo_dir, name), 160 * sc)
        imgs.append({"filename": name, "idiom": "universal", "scale": f"{sc}x"})
    write_json(os.path.join(logo_dir, "Contents.json"), {"images": imgs, "info": {"author": "xcode", "version": 1}})

    art_dir = os.path.join(ASSETS, "Artwork.imageset")
    os.makedirs(art_dir, exist_ok=True)
    app_icon(os.path.join(art_dir, "Artwork.png"), size=600)
    write_json(os.path.join(art_dir, "Contents.json"), {
        "images": [{"filename": "Artwork.png", "idiom": "universal"}], "info": {"author": "xcode", "version": 1}})

    def color_set(name, light, dark):
        cdir = os.path.join(ASSETS, f"{name}.colorset")
        os.makedirs(cdir, exist_ok=True)

        def comp(c):
            return {"color-space": "srgb", "components": {
                "red": f"{c[0] / 255:.3f}", "green": f"{c[1] / 255:.3f}", "blue": f"{c[2] / 255:.3f}", "alpha": "1.000"}}
        write_json(os.path.join(cdir, "Contents.json"), {
            "colors": [
                {"idiom": "universal", "color": comp(light)},
                {"idiom": "universal", "appearances": [{"appearance": "luminosity", "value": "dark"}], "color": comp(dark)},
            ],
            "info": {"author": "xcode", "version": 1},
        })

    color_set("AccentColor", (79, 70, 229), (129, 140, 248))
    color_set("LaunchBackground", INK, INK)

    app_icon(os.path.join(DOCS, "icon-1024.png"))
    banner(os.path.join(DOCS, "banner.png"))
    print("Brand assets written to", ASSETS, "and", DOCS)


if __name__ == "__main__":
    main()
