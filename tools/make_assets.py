#!/usr/bin/env python3
"""Generate Open Graph images and favicons with Pillow.

Usage:  pip install pillow   (once)
        python3 tools/make_assets.py

Writes:
  assets/og/default.jpg, assets/og/about.jpg, assets/og/<slug>.jpg  (1200x630)
  assets/favicon-32.png, assets/apple-touch-icon.png
(assets/favicon.svg is hand-written and not touched.)

Run it again after adding or renaming a project. build.py uses
assets/og/<slug>.jpg when it exists and falls back to default.jpg.
This is the only script that needs a third-party package; build.py and
check.py are standard library only.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "projects.json").read_text(encoding="utf-8"))
SITE = DATA["site"]
OUT = ROOT / "assets" / "og"
W, H = 1200, 630
ACCENT = (240, 162, 74)
TEXT = (242, 237, 229)
MUTED = (190, 184, 174)

SERIF_CANDIDATES = [
    ROOT / "assets/fonts/instrument-serif-regular.woff2",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/Library/Fonts/Georgia.ttf", "C:/Windows/Fonts/georgia.ttf",
]
SERIF_ITALIC_CANDIDATES = [ROOT / "assets/fonts/instrument-serif-italic.woff2"] + SERIF_CANDIDATES
SANS_CANDIDATES = [
    "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Helvetica.ttc", "C:/Windows/Fonts/segoeui.ttf",
]
MONO_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/System/Library/Fonts/Menlo.ttc", "C:/Windows/Fonts/consola.ttf",
]


def font(cands, size):
    for c in cands:
        try:
            return ImageFont.truetype(str(c), size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def background(pal, w=W, h=H):
    a, b = (hex_rgb(x) for x in pal[:2])
    img = Image.new("RGB", (w, h), (6, 6, 6))
    # vertical-ish base gradient from palette a to near black
    big = Image.linear_gradient("L").resize((w * 2, w * 2)).rotate(-25, resample=Image.BICUBIC)
    base = big.crop((w // 2, w - h // 2, w // 2 + w, w - h // 2 + h))
    dark = Image.new("RGB", (w, h), (6, 6, 6))
    img = Image.composite(dark, Image.new("RGB", (w, h), a), base)
    # glow from palette b, top right
    glow = Image.new("L", (w, h), 0)
    gd = ImageDraw.Draw(glow)
    gd.ellipse((int(w * 0.45), int(-h * 0.55), int(w * 1.35), int(h * 0.75)), fill=200)
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    img = Image.composite(Image.new("RGB", (w, h), b), img, glow)
    # grain
    noise = Image.effect_noise((w, h), 28).convert("L")
    img = Image.blend(img, Image.merge("RGB", (noise, noise, noise)), 0.05)
    # vignette
    vig = Image.new("L", (w, h), 0)
    ImageDraw.Draw(vig).rectangle((0, 0, w, h), fill=0)
    ImageDraw.Draw(vig).ellipse((-w * 0.25, -h * 0.4, w * 1.25, h * 1.4), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(120))
    img = Image.composite(img, Image.new("RGB", (w, h), (0, 0, 0)), vig)
    return img


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        test = (cur + " " + wd).strip()
        if draw.textlength(test, font=fnt) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def og(name, title, kicker, sub, pal, seed):
    img = background(pal)
    d = ImageDraw.Draw(img)
    mono = font(MONO_CANDIDATES, 20)
    sans = font(SANS_CANDIDATES, 28)
    x = 80
    # corner marks, like a camera frame guide
    for (cx, cy, dx, dy) in [(40, 40, 1, 1), (W - 40, H - 40, -1, -1)]:
        d.line((cx, cy, cx + 34 * dx, cy), fill=(242, 237, 229), width=2)
        d.line((cx, cy, cx, cy + 34 * dy), fill=(242, 237, 229), width=2)
    d.ellipse((x, 92, x + 12, 104), fill=ACCENT)
    d.text((x + 26, 87), kicker.upper(), font=mono, fill=MUTED)

    size = 96
    while size > 48:
        serif = font(SERIF_CANDIDATES, size)
        lines = wrap(d, title, serif, W - x * 2)
        if len(lines) <= 3:
            break
        size -= 6
    y = 160 if len(lines) == 3 else 190
    for ln in lines:
        d.text((x, y), ln, font=serif, fill=TEXT)
        y += int(size * 1.04)
    if sub:
        y += 24
        for ln in wrap(d, sub, sans, W - x * 2)[:2]:
            d.text((x, y), ln, font=sans, fill=MUTED)
            y += 40
    foot = f"{SITE['name']}  ·  {SITE['role']}  ·  {SITE['location']}"
    d.text((x, H - 92), foot, font=mono, fill=TEXT)
    d.text((W - 80 - d.textlength("somarawad.github.io", font=mono), H - 92), "somarawad.github.io", font=mono, fill=ACCENT)
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{name}.jpg"
    img.save(path, "JPEG", quality=84, optimize=True, progressive=True)
    print(f"  wrote {path.relative_to(ROOT)}")


def favicon():
    big = 512
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, big - 1, big - 1), radius=112, fill=(12, 11, 10, 255))
    serif = font(SERIF_ITALIC_CANDIDATES, 400)
    bbox = d.textbbox((0, 0), "S", font=serif)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((big - tw) / 2 - bbox[0], (big - th) / 2 - bbox[1] - 6), "S", font=serif, fill=(242, 237, 229, 255))
    d.ellipse((372, 84, 428, 140), fill=ACCENT + (255,))
    img.resize((32, 32), Image.LANCZOS).save(ROOT / "assets" / "favicon-32.png", optimize=True)
    apple = Image.new("RGB", (180, 180), (12, 11, 10))
    apple.paste(img.resize((180, 180), Image.LANCZOS), (0, 0), img.resize((180, 180), Image.LANCZOS))
    apple.save(ROOT / "assets" / "apple-touch-icon.png", optimize=True)
    print("  wrote assets/favicon-32.png, assets/apple-touch-icon.png")


def main():
    headline = SITE["headline"].replace("*", "")
    og("default", headline, "Portfolio", "", SITE.get("palette", ["#1a1410", "#5a3a1c"]), 0)
    og("about", "About Somar Awad", "About", SITE["about"]["intro"].split(". ", 1)[-1], SITE.get("palette"), 1)
    for i, p in enumerate(DATA["projects"]):
        kicker = " · ".join(x for x in [p.get("category"), p.get("year")] if x)
        og(p["slug"], p["title"], kicker, p.get("tagline", ""), p.get("palette", ["#161412", "#4a3a2a"]), i + 2)
    favicon()


if __name__ == "__main__":
    main()
