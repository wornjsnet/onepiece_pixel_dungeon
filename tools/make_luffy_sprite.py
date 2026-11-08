"""Builds Luffy's hero sprite sheet in the original game's art style.

Usage: python3 tools/make_luffy_sprite.py <rogue.png> <luffy.png>

Uses the rogue's frames as the body/animation base (short hair, no beard,
same proportions and shading as every other hero), then:
  - hair -> black
  - a shaded straw hat with a red band over the top of the head
  - a small scar under the eye
  - unarmored & cloth rows: open red vest and blue shorts
Frame layout (HeroSprite): 0-1 idle, 2-7 run, 8-12 die, 13-15 attack,
16-17 operate, 18 fly, 19-20 read. One row per armor tier.
"""
import sys
from PIL import Image

SRC, DST = sys.argv[1], sys.argv[2]
FW, FH = 12, 15

HAIR = {
    (133, 73, 12): (40, 38, 48),
    (171, 94, 16): (58, 56, 68),
    (98, 55, 9): (22, 20, 28),
    (184, 136, 55): (50, 48, 60),
    (209, 155, 63): (66, 64, 78),
}
SKIN = {(220, 180, 151), (255, 218, 191), (184, 151, 120), (190, 127, 89), (255, 186, 143)}
EYE = (0, 0, 0)

STRAW_HI = (255, 236, 150)
STRAW = (236, 198, 100)
STRAW_MID = (214, 172, 78)
STRAW_SH = (170, 128, 52)
BAND = (206, 36, 36)
BAND_SH = (150, 22, 28)
SCAR = (196, 112, 96)

VEST = (204, 36, 40)
VEST_SH = (150, 22, 30)
SHORTS = {
    (126, 126, 126): (34, 60, 138),
    (204, 204, 204): (62, 102, 194),
    (255, 255, 255): (88, 130, 220),
    (163, 163, 163): (46, 78, 162),
}

src = Image.open(SRC).convert('RGBA')
W, H = src.size
sheet = src.copy()

# Luffy wears his own outfit until he puts on real armor: the cloth armor row
# uses the unarmored body, which then gets the vest and shorts below
sheet.paste(src.crop((0, 0, W, FH)), (0, FH))
# class armor row too (shown on the hero select screen), until Nika gets its own look
sheet.paste(src.crop((0, 0, W, FH)), (0, 6 * FH))

# every armor row uses the unarmored head (e.g. no rogue mask on class armor)
for fy in range(2, H // FH):
    for fx in range(W // FW):
        box = (fx * FW, 0, (fx + 1) * FW, 8)
        if src.crop(box).getbbox() and src.crop((fx * FW, fy * FH, (fx + 1) * FW, fy * FH + 8)).getbbox():
            sheet.paste(src.crop(box), (fx * FW, fy * FH))

px = sheet.load()

# remove any leftover of the rogue's class armor mask below the head
mask_cols = set()
for fx in range(W // FW):
    for y in range(4, 9):
        for x in range(FW):
            m = src.getpixel((fx * FW + x, 6 * FH + y))
            u = src.getpixel((fx * FW + x, y))
            if m[3] and m != u:
                mask_cols.add(m[:3])
for fy in range(2, H // FH):
    for fx in range(W // FW):
        for y in range(8, 10):
            for x in range(FW):
                p = px[fx * FW + x, fy * FH + y]
                if p[3] and p[:3] in mask_cols and p[2] > p[1] + 40 and p[0] > p[1] + 40:
                    px[fx * FW + x, fy * FH + y] = src.getpixel((fx * FW + x, y))


def rgb(p):
    return p[:3]


def opaque(x, y):
    return px[x, y][3] != 0


for fy in range(H // FH):
    for fx in range(W // FW):
        ox, oy = fx * FW, fy * FH
        hair = [(x, y) for y in range(0, 4) for x in range(FW)
                if opaque(ox + x, oy + y) and rgb(px[ox + x, oy + y]) in HAIR]
        if not hair:
            continue  # death frames etc.

        top = min(y for _, y in hair)
        left = min(x for x, _ in hair)
        right = max(x for x, _ in hair)

        # hair -> black (anywhere on the head)
        for y in range(0, 9):
            for x in range(FW):
                p = px[ox + x, oy + y]
                if p[3] and rgb(p) in HAIR:
                    px[ox + x, oy + y] = HAIR[rgb(p)] + (255,)

        # scar under the front eye
        eyes = [x for x in range(FW) if opaque(ox + x, oy + top + 3) and rgb(px[ox + x, oy + top + 3]) == EYE]
        if eyes:
            ex = max(eyes)
            sy = oy + top + 4
            if rgb(px[ox + ex, sy]) in SKIN:
                px[ox + ex, sy] = SCAR + (255,)

        # straw hat: crown, band, wide brim (brim sits where the forehead was)
        def put(x, y, c):
            if 0 <= x < FW and 0 <= y - oy < FH:
                px[ox + x, y] = c + (255,)

        crown_top = oy + top - 1
        for x in range(left + 1, right):
            put(x, crown_top, STRAW_HI if x < right - 1 else STRAW)
        for x in range(left, right + 1):
            put(x, crown_top + 1, STRAW if x < right - 1 else STRAW_MID)
        for x in range(left, right + 1):
            put(x, crown_top + 2, BAND if x < right else BAND_SH)
        for x in range(left - 1, right + 2):
            put(x, crown_top + 3, STRAW_MID if left <= x <= right else STRAW_SH)

        # black hair showing below the brim at the back of the head
        HAIR_DARK, HAIR_MID = (22, 20, 28), (44, 42, 54)
        for dy, col in ((3, HAIR_MID), (4, HAIR_DARK)):
            y = oy + top + dy
            if opaque(ox + left, y):
                px[ox + left, y] = col + (255,)
        if left - 1 >= 0 and not opaque(ox + left - 1, oy + top + 3):
            px[ox + left - 1, oy + top + 3] = HAIR_DARK + (255,)

        # outfit for the unarmored, cloth and class armor rows
        if fy in (0, 1, 6):
            for y in range(8, 11):
                row = [x for x in range(FW) if opaque(ox + x, oy + y) and rgb(px[ox + x, oy + y]) in SKIN]
                if len(row) < 4:
                    continue
                l, r = min(row), max(row)
                for x in row:
                    if x in (l + 1, l + 2, r - 2, r - 1):
                        px[ox + x, oy + y] = (VEST if y < 10 else VEST_SH) + (255,)
            for y in range(11, FH):
                for x in range(FW):
                    p = px[ox + x, oy + y]
                    if p[3] and rgb(p) in SHORTS:
                        px[ox + x, oy + y] = SHORTS[rgb(p)] + (255,)

sheet.save(DST)
