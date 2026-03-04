#!/usr/bin/env python3
"""
Generate sumi-e style mnemonic images for Telugu characters.

Each image (1024 × 1024 px) features:
 - Warm washi-paper background with subtle grain
 - Soft radial watercolour wash accent
 - The Telugu character large in ink-brush style (centre)
 - A mnemonic keyword below the character in muted accent colour
 - A label strip at the bottom rendered with mixed fonts:
     [Telugu char]  (romaji) · Keyword  [red seal]

Output: public/mnemonics/te-{romaji}.png

Usage (from project root):
  python3 scripts/generate_telugu_mnemonics.py
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── Character data ───────────────────────────────────────────────────────────
# (char, romaji, keyword, accent_rgb)
CHARS = [
    # vowels
    ("అ",   "a",    "Artist",    (210, 140,  80)),
    ("ఆ",   "aa",   "Arms wide", (200, 120,  70)),
    ("ఇ",   "i",    "Flag",      (100, 160, 200)),
    ("ఈ",   "ii",   "Eel",       ( 80, 150, 200)),
    ("ఉ",   "u",    "Cup",       (160, 200, 140)),
    ("ఊ",   "uu",   "Moon",      (140, 180, 220)),
    ("ఋ",   "ru",   "Root",      (160, 120,  80)),
    ("ఎ",   "e",    "Ear",       (220, 160, 100)),
    ("ఏ",   "ee",   "Eel",       ( 80, 160, 210)),
    ("ఐ",   "ai",   "Slide",     (200, 180,  80)),
    ("ఒ",   "o",    "Wheel",     (200, 140,  60)),
    ("ఓ",   "oo",   "Ship",      ( 60, 130, 200)),
    ("ఔ",   "au",   "Boat",      ( 80, 160, 180)),
    # ka-varga
    ("క",   "ka",   "Kite",      (200,  80,  80)),
    ("ఖ",   "kha",  "Kha-lite",  (200, 100,  80)),
    ("గ",   "ga",   "Gallop",    ( 80, 160,  80)),
    ("ఘ",   "gha",  "Gong",      ( 80, 140,  60)),
    ("ఙ",   "nga",  "Hook",      (160,  80, 160)),
    # ca-varga
    ("చ",   "cha",  "Chai",      (200, 160,  60)),
    ("ఛ",   "chha", "Saucer",    (210, 170,  70)),
    ("జ",   "ja",   "Jug",       ( 60, 140, 200)),
    ("ఝ",   "jha",  "Cascade",   ( 40, 120, 200)),
    ("ఞ",   "nya",  "Knot",      (160,  60, 160)),
    # retroflex ta
    ("ట",   "tta",  "Drum",      (200,  80,  60)),
    ("ఠ",   "ttha", "Adorned",   (210,  90,  70)),
    ("డ",   "dda",  "Dolphin",   ( 60, 160, 200)),
    ("ఢ",   "ddha", "Deep dive", ( 40, 140, 200)),
    ("ణ",   "nna",  "Net",       (140, 100, 200)),
    # dental ta
    ("త",   "ta",   "Tent",      (160, 200, 120)),
    ("థ",   "tha",  "Wind",      (180, 220, 140)),
    ("ద",   "da",   "Dancer",    (200,  80, 140)),
    ("ధ",   "dha",  "Drum",      (200,  60, 120)),
    ("న",   "na",   "River",     ( 60, 140, 200)),
    # pa-varga
    ("ప",   "pa",   "Parrot",    ( 80, 200, 120)),
    ("ఫ",   "pha",  "Puffed",    (100, 210, 130)),
    ("బ",   "ba",   "Ball",      (200, 140,  60)),
    ("భ",   "bha",  "Bigger",    (210, 150,  70)),
    ("మ",   "ma",   "Mother",    (200,  80,  80)),
    # ya-row
    ("య",   "ya",   "Yak",       (140, 200,  80)),
    ("ర",   "ra",   "Rolling",   (200, 120,  60)),
    ("ల",   "la",   "Lotus",     ( 80, 200, 140)),
    ("వ",   "va",   "Waves",     ( 60, 140, 220)),
    # sha-row
    ("శ",   "sha",  "Star",      (220, 200,  60)),
    ("ష",   "ssa",  "Sharp",     (220, 180,  40)),
    ("స",   "sa",   "Swan",      (160, 200, 220)),
    ("హ",   "ha",   "Breath",    (180, 180, 220)),
    # special
    ("ళ",   "lla",  "Lotus",     ( 60, 180, 120)),
    ("క్ష", "ksha", "Key",       (200,  80, 140)),
    ("ఱ",   "rra",  "Roll",      (180,  90,  60)),
]

SIZE    = 1024
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "public", "mnemonics")

FONT_TELUGU = "/usr/share/fonts/truetype/noto/NotoSansTelugu-Bold.ttf"
FONT_SANS   = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO   = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


# ── Helpers ──────────────────────────────────────────────────────────────────

def washi_bg() -> Image.Image:
    """Warm washi-paper background with per-pixel grain."""
    import random
    rng = random.Random(7)
    img = Image.new("RGB", (SIZE, SIZE))
    px  = img.load()
    for y in range(SIZE):
        for x in range(SIZE):
            n = rng.randint(-8, 8)
            r = min(255, 238 + n + rng.randint(0, 8))
            g = min(255, 230 + n + rng.randint(-2, 4))
            b = min(255, 212 + n - rng.randint(0, 14))
            px[x, y] = (r, g, b)
    return img


def add_wash(img: Image.Image, cx: int, cy: int,
             radius: int, colour: tuple, strength: float = 0.22) -> Image.Image:
    """Soft radial watercolour wash, blurred."""
    layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    steps = 10
    for i in range(steps, 0, -1):
        r = radius * i // steps
        a = int(255 * strength * (1 - i / (steps + 1)))
        d.ellipse([(cx - r, cy - r), (cx + r, cy + r)],
                  fill=colour + (a,))
    layer = layer.filter(ImageFilter.GaussianBlur(radius // 5))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def render_char(img: Image.Image, char: str, fnt) -> tuple:
    """
    Render the character centred vertically in the upper 55 % of the canvas.
    Returns (img, char_bottom_y) where char_bottom_y is the actual bottom pixel.
    """
    # Measure
    probe = ImageDraw.Draw(img)
    bb    = probe.textbbox((0, 0), char, font=fnt)
    cw, ch = bb[2] - bb[0], bb[3] - bb[1]

    cx = (SIZE - cw) // 2 - bb[0]
    # Place character so its visible extent is centred in upper 55% of canvas
    top_margin = 60
    cy = top_margin + (int(0.55 * SIZE) - ch) // 2 - bb[1]

    # Ink shadow
    shadow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.text((cx + 5, cy + 8), char, font=fnt, fill=(20, 14, 30, 100))
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))

    # Glyph
    glyph = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glyph)
    gd.text((cx, cy), char, font=fnt, fill=(26, 20, 38, 255))
    glyph = glyph.filter(ImageFilter.GaussianBlur(1.0))  # ink spread

    base = Image.alpha_composite(img.convert("RGBA"), shadow)
    base = Image.alpha_composite(base, glyph).convert("RGB")

    # Return the actual bottom pixel of the rendered character
    return base, cy + bb[3]


def render_keyword(img: Image.Image, keyword: str,
                   char_bottom: int, accent: tuple, fnt) -> Image.Image:
    """Render the keyword in muted accent colour below the character."""
    layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d     = ImageDraw.Draw(layer)
    col   = tuple(max(30, c - 30) for c in accent) + (210,)
    bb    = d.textbbox((0, 0), keyword, font=fnt)
    kw, kh = bb[2] - bb[0], bb[3] - bb[1]
    kx = (SIZE - kw) // 2 - bb[0]
    ky = char_bottom + 30
    d.text((kx, ky), keyword, font=fnt, fill=col)
    layer = layer.filter(ImageFilter.GaussianBlur(0.6))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def render_label(img: Image.Image, char: str, romaji: str,
                 keyword: str, fnt_telugu, fnt_mono):
    """
    Bottom label strip with mixed fonts:
      [Telugu char in Telugu font]  (romaji) · Keyword  [red seal dot]
    """
    draw   = ImageDraw.Draw(img)
    rule_y = SIZE - 108

    # Rule
    draw.line([(60, rule_y), (SIZE - 60, rule_y)], fill=(170, 150, 130), width=1)

    # Measure parts
    part_romaji = f"  ({romaji})  ·  {keyword}"
    bb_ch  = draw.textbbox((0, 0), char,         font=fnt_telugu)
    bb_ro  = draw.textbbox((0, 0), part_romaji,  font=fnt_mono)

    total_w = (bb_ch[2] - bb_ch[0]) + (bb_ro[2] - bb_ro[0])
    x0 = (SIZE - total_w) // 2
    ly = rule_y + 22

    # Telugu char
    draw.text((x0 - bb_ch[0], ly - bb_ch[1]), char,
              font=fnt_telugu, fill=(80, 60, 45))

    # Romaji + keyword (mono)
    x1 = x0 + (bb_ch[2] - bb_ch[0])
    draw.text((x1 - bb_ro[0], ly - bb_ro[1] + (bb_ch[3] - bb_ch[1]) // 4),
              part_romaji, font=fnt_mono, fill=(90, 70, 55))

    # Red seal
    sx, sy = SIZE - 72, rule_y + 44
    draw.ellipse([(sx - 16, sy - 16), (sx + 16, sy + 16)], fill=(175, 45, 35))
    draw.ellipse([(sx - 10, sy - 10), (sx + 10, sy + 10)], fill=(210, 65, 48))


# ── Main ─────────────────────────────────────────────────────────────────────

def generate(char: str, romaji: str, keyword: str, accent: tuple, out_path: str):
    # Load fonts
    fnt_char  = ImageFont.truetype(FONT_TELUGU, 520)
    fnt_kw    = ImageFont.truetype(FONT_SANS,   62)
    fnt_label = ImageFont.truetype(FONT_TELUGU, 38)
    fnt_mono  = ImageFont.truetype(FONT_MONO,   34)

    # 1. Background
    img = washi_bg()

    # 2. Watercolour wash
    img = add_wash(img, SIZE // 2 - 40, SIZE // 2 - 80, 320, accent, 0.20)
    img = add_wash(img, SIZE // 2 + 90, SIZE // 2 + 50, 180, accent, 0.11)

    # 3. Character
    img, char_bottom = render_char(img, char, fnt_char)

    # 4. Keyword
    img = render_keyword(img, keyword, char_bottom, accent, fnt_kw)

    # 5. Bottom label
    render_label(img, char, romaji, keyword, fnt_label, fnt_mono)

    img.save(out_path, "PNG", optimize=True)
    print(f"  ✓  te-{romaji}.png   {char}  {keyword}")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Generating {len(CHARS)} Telugu mnemonic images → {OUT_DIR}/\n")
    for char, romaji, keyword, accent in CHARS:
        generate(char, romaji, keyword, accent,
                 os.path.join(OUT_DIR, f"te-{romaji}.png"))
    print(f"\n✓ Done — {len(CHARS)} images written.")
