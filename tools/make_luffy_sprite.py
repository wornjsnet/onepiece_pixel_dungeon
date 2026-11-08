"""Builds a placeholder Luffy hero sprite sheet from the Warrior's sheet.

Usage: python3 tools/make_luffy_sprite.py <warrior.png> <luffy.png>

Recolors per 12x15 frame: orange hair -> black hair, beard removed,
straw hat with a red band drawn over the top of the head, and for the
unarmored row a red open vest and blue shorts.
"""
import sys
from PIL import Image

SRC, DST = sys.argv[1], sys.argv[2]
FW, FH = 12, 15

HAIR = {
    (190, 57, 12): (52, 50, 58),
    (151, 49, 13): (24, 22, 30),
    (220, 121, 55): (44, 42, 52),
    (117, 43, 14): (18, 16, 22),
    (173, 105, 60): (34, 32, 40),
    (196, 112, 58): (30, 28, 36),
}
SKIN = (220, 180, 151)
SKIN_SHADOW = (184, 151, 120)
SKIN_LIGHT = (255, 218, 191)
SKINS = {SKIN, SKIN_SHADOW, SKIN_LIGHT, (190, 127, 89), (255, 186, 143)}

STRAW_L = (246, 222, 128)
STRAW = (226, 188, 90)
STRAW_D = (186, 146, 60)
BAND = (206, 34, 34)
HAT_OUT = (92, 60, 22)

VEST = (196, 30, 30)
VEST_D = (140, 18, 22)
SHORTS = {
    (126, 126, 126): (36, 62, 140),
    (204, 204, 204): (64, 104, 196),
    (255, 255, 255): (90, 132, 220),
    (163, 163, 163): (46, 80, 164),
    (179, 179, 179): (54, 92, 180),
}

im = Image.open(SRC).convert('RGBA')
px = im.load()
W, H = im.size


def rgb(p):
    return p[:3]


for fy in range(H // FH):
    for fx in range(W // FW):
        ox, oy = fx * FW, fy * FH
        # skip empty frames
        if all(px[ox + x, oy + y][3] == 0 for x in range(FW) for y in range(FH)):
            continue
        hair_cols = [x for x in range(FW) for y in range(0, 4)
                     if px[ox + x, oy + y][3] and rgb(px[ox + x, oy + y]) in HAIR]
        if not hair_cols:
            continue  # not a hero frame (e.g. death/skull frames)

        # beard (hair colours below the eyes) -> skin
        for y in range(6, 9):
            for x in range(FW):
                p = px[ox + x, oy + y]
                if p[3] and rgb(p) in HAIR:
                    px[ox + x, oy + y] = (SKIN_SHADOW if y == 6 else SKIN) + (255,)

        # hair -> black
        for y in range(0, 8):
            for x in range(FW):
                p = px[ox + x, oy + y]
                if p[3] and rgb(p) in HAIR:
                    px[ox + x, oy + y] = HAIR[rgb(p)] + (255,)

        # straw hat over rows 0-2, brim on row 3
        left, right = min(hair_cols), max(hair_cols)
        for y, col in ((0, STRAW_L), (1, STRAW), (2, BAND)):
            for x in range(FW):
                p = px[ox + x, oy + y]
                if p[3]:
                    c = col
                    if y < 2 and (x + y) % 3 == 0:
                        c = STRAW_D
                    px[ox + x, oy + y] = c + (255,)
        for x in range(max(0, left - 1), min(FW, right + 2)):
            p = px[ox + x, oy + 3]
            if p[3] == 0 or rgb(p) in HAIR.values():
                px[ox + x, oy + 3] = STRAW_D + (255,)

        # unarmored row: open red vest and blue shorts
        if fy == 0:
            for y in range(8, 11):
                body = [x for x in range(FW) if px[ox + x, oy + y][3] and rgb(px[ox + x, oy + y]) in SKINS]
                if not body:
                    continue
                l, r = min(body), max(body)
                for x in body:
                    if x in (l + 1, l + 2, r - 1, r - 2):
                        px[ox + x, oy + y] = (VEST if y < 10 else VEST_D) + (255,)
            for y in range(11, FH):
                for x in range(FW):
                    p = px[ox + x, oy + y]
                    if p[3] and rgb(p) in SHORTS:
                        px[ox + x, oy + y] = SHORTS[rgb(p)] + (255,)

im.save(DST)
