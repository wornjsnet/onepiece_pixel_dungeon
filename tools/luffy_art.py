"""Draws all of Luffy's dedicated pixel art, in the original game's style.

Usage (from the repository root):
    python3 tools/luffy_art.py

Writes / updates:
  core/src/main/assets/sprites/luffy.png         hero sheet (12x15 frames, row per armor tier)
  core/src/main/assets/sprites/items.png         rubber fist icon      (item slot xy(1,13))
  core/src/main/assets/interfaces/talent_icons.png  Luffy talent icons (slots 192+)
  core/src/main/assets/effects/rubber_arm.png    Gum-Gum Pistol stretching arm (segment + fist)

Every sprite is defined below as text art, one character per pixel, so it can be
edited by hand. '.' is transparent; other characters map to the palettes.
"""
import os
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), '..', 'core', 'src', 'main', 'assets')

# ---------------------------------------------------------------- palette
P = {
    # straw hat
    'Y': (255, 238, 156), 'y': (238, 200, 104), 'd': (196, 154, 68), 'D': (150, 110, 44),
    'R': (214, 40, 40), 'r': (156, 24, 30),
    # hair
    'H': (34, 32, 42), 'h': (62, 60, 74),
    # skin (same tones the original heroes use)
    'S': (255, 218, 191), 's': (220, 180, 151), 'k': (184, 151, 120), 'o': (133, 89, 56),
    'E': (0, 0, 0), 'c': (204, 120, 100),
    # outfit (V/v vest, B/b shorts are swapped per armor tier)
    'F': (120, 76, 40), 'f': (86, 52, 26),
    # misc
    'W': (255, 255, 255), 'w': (200, 200, 200), 'g': (130, 130, 130),
    'M': (196, 72, 60), 'm': (140, 40, 36), 'n': (240, 220, 200),
    'G': (250, 210, 60), 'O': (255, 170, 40), 'Z': (90, 140, 210), 'z': (50, 90, 160),
    'P': (236, 226, 196), 'p': (200, 186, 150),
}

ARMOR = [
    # vest V, vest shade v, shorts B, shorts shade b, chest covered
    ((206, 36, 40), (150, 22, 30), (64, 104, 196), (40, 68, 150), False),   # 0 none
    ((206, 36, 40), (150, 22, 30), (64, 104, 196), (40, 68, 150), False),   # 1 cloth
    ((156, 104, 58), (110, 70, 38), (64, 104, 196), (40, 68, 150), False),  # 2 leather
    ((168, 172, 184), (112, 116, 130), (90, 92, 104), (62, 64, 74), True),  # 3 mail
    ((82, 160, 140), (50, 110, 98), (64, 104, 196), (40, 68, 150), True),   # 4 scale
    ((222, 224, 232), (156, 160, 176), (120, 124, 140), (84, 88, 104), True),  # 5 plate
    ((206, 36, 40), (150, 22, 30), (64, 104, 196), (40, 68, 150), False),   # 6 class armor (until Nika)
    ((206, 36, 40), (150, 22, 30), (64, 104, 196), (40, 68, 150), False),   # 7 unused
]

# ---------------------------------------------------------------- hero frames
# Head: hat brim sits over the forehead, black hair at the back, eyes face right.
HEAD = [
    "............",
    ".....yYYYy..",
    "....dyyyyyy.",
    "....rRRRRRr.",
    "..Ddyyyyyyyd",
    "...HHsSSSSk.",
    "...HsSESSEk.",
    "...HksSSSck.",
    "....okSSSk..",
]
HEAD_BLINK = HEAD[:6] + ["...HsSkSSkk."] + HEAD[7:]

BODY = {  # rows 9-12: arms, open vest, shorts
    'idle':    ["..ksVVSVVsk.", "..ksvSSSvsk.", "..oBBBBBBBo.", "...BBbbbBB.."],
    'swing1':  ["..ksVVSVVs..", ".oksvSSSvs..", "...BBBBBBBo.", "...BBbbbBB.."],
    'swing2':  ["..ksVVSVVsk.", "..ksvSSSvsko", "..oBBBBBBB..", "...BBbbbBB.."],
    'windup':  [".kssVVSVVs..", ".o.svSSSvsk.", "...BBBBBBBo.", "...BBbbbBB.."],
    'punch':   ["..ksVVSVVsSk", "..ksvSSSvssS", "..oBBBBBBBk.", "...BBbbbBB.."],
    'recover': ["..ksVVSVVss.", "..ksvSSSv.k.", "..oBBBBBBB..", "...BBbbbBB.."],
    'op1':     ["..ksVVSVVs..", "..ksvSSSvsso", "..oBBBBBBB..", "...BBbbbBB.."],
    'op2':     ["..ksVVSVVsso", "..ksvSSSvk..", "..oBBBBBBB..", "...BBbbbBB.."],
    'up':      ["okssVVSVVsko", "...svSSSvs..", "...BBBBBBB..", "...BBbbbBB.."],
    'read':    ["..ksVVSVVPp.", "..ksvSSSvpPo", "..oBBBBBBB..", "...BBbbbBB.."],
}
LEGS = {  # rows 13-14
    'stand':  ["...ks..sk...", "..FFf..FFf.."],
    'spread': ["..ks....sk..", ".FFf....FFf."],
    'mid':    ["...ks...sk..", "..FFf..FFf.."],
    'pass':   ["....kssk....", "....FFFf...."],
    'tuck':   ["....kssk....", "....FFFF...."],
}

# arm ending in a fist for the punch, hands at the end of other poses are 'o'
FRAMES = {
    0: HEAD + BODY['idle'] + LEGS['stand'],
    1: HEAD_BLINK + BODY['idle'] + LEGS['stand'],
    2: HEAD + BODY['swing1'] + LEGS['spread'],
    3: HEAD + BODY['swing1'] + LEGS['mid'],
    4: HEAD + BODY['idle'] + LEGS['pass'],
    5: HEAD + BODY['swing2'] + LEGS['spread'],
    6: HEAD + BODY['swing2'] + LEGS['mid'],
    7: HEAD + BODY['idle'] + LEGS['pass'],
    13: HEAD + BODY['windup'] + LEGS['spread'],
    14: HEAD + BODY['punch'] + LEGS['spread'],
    15: HEAD + BODY['recover'] + LEGS['mid'],
    16: HEAD + BODY['op1'] + LEGS['stand'],
    17: HEAD + BODY['op2'] + LEGS['stand'],
    18: HEAD + BODY['up'] + LEGS['tuck'],
    19: HEAD + BODY['read'] + LEGS['stand'],
    20: HEAD_BLINK + BODY['read'] + LEGS['stand'],
}

# death: Luffy sinks down, then only his straw hat is left behind
HAT_ON_GROUND = [
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    ".....yYYy...",
    "....dyyyyyd.",
    "....rRRRRRr.",
    "..Ddyyyyyydd",
    "...DDddddDD.",
]


def sunk(art, rows):
    return ["............"] * rows + art[:len(art) - rows]


DIE = {
    8: sunk(FRAMES[0], 2),
    9: sunk(FRAMES[0], 5),
    10: sunk(FRAMES[0], 9)[:10] + HAT_ON_GROUND[10:],
    11: HAT_ON_GROUND,
    12: HAT_ON_GROUND,
}
FRAMES.update(DIE)


def hero_sheet():
    FW, FH = 12, 15
    sheet = Image.new('RGBA', (256, 128), (0, 0, 0, 0))
    for row, (V, v, B, b, covered) in enumerate(ARMOR):
        pal = dict(P, V=V, v=v, B=B, b=b)
        for f, art in FRAMES.items():
            assert len(art) == FH, (f, len(art))
            for y, line in enumerate(art):
                assert len(line) == FW, (f, y, line)
                for x, ch in enumerate(line):
                    if ch == '.':
                        continue
                    col = pal[ch]
                    if covered and ch in 'S' and 9 <= y <= 10:
                        col = V if y == 9 else v
                    sheet.putpixel((f * FW + x, row * FH + y), col + (255,))
    sheet.save(os.path.join(ROOT, 'sprites', 'luffy.png'))


# ---------------------------------------------------------------- item icon
# Drawn like the original item icons: translucent black outline ('A'),
# four or five tones per material, light from the top-left.
ICON_PAL = {
    'A': (0, 0, 0, 102),
    'S': (255, 224, 200, 255), 's': (238, 194, 160, 255), 'k': (204, 156, 122, 255),
    'd': (160, 112, 82, 255), 'D': (120, 78, 54, 255),
}
RUBBER_FIST = [
    "...AAAAAAAA..",
    "..ASSkSSkSSA.",
    ".ASSSkSSkSSsA",
    "ASSSskSskSssA",
    "AsSsssssssskA",
    "AsssssssssskA",
    "AkSSSSSSSsskA",
    "AksssssssskdA",
    ".AkkkkkkkkdA.",
    "..AkssssskA..",
    "..AksssskdA..",
    "..AkkkkkddA..",
    "..AAAAAAAAA..",
]
ITEM_SLOT = 12 * 16 + 0  # xy(1, 13)


def item_icon():
    """Packed into the top-left of its slot like the original sheet.
    Returns its size, used by ItemSpriteSheet.assignItemRect."""
    path = os.path.join(ROOT, 'sprites', 'items.png')
    sheet = Image.open(path).convert('RGBA')
    ox, oy = (ITEM_SLOT % 16) * 16, (ITEM_SLOT // 16) * 16
    sheet.paste(Image.new('RGBA', (16, 16), (0, 0, 0, 0)), (ox, oy))
    for y, line in enumerate(RUBBER_FIST):
        for x, ch in enumerate(line):
            if ch != '.':
                sheet.putpixel((ox + x, oy + y), ICON_PAL[ch])
    sheet.save(path)
    return len(RUBBER_FIST[0]), len(RUBBER_FIST)


# ---------------------------------------------------------------- talent icons
# Flat style like the original talent icons: a solid colored tile (corners
# transparent), a few bold colors and 1px black outlines.
#   green tile = food talents, blue = identification, white = combat/defense
TALENT_PAL = {
    'g': (0, 179, 0), 'b': (0, 160, 255), 'w': (255, 255, 255),
    'E': (0, 0, 0),
    'B': (242, 228, 218), 'C': (179, 168, 161),            # bone
    'K': (224, 73, 73), 'L': (240, 160, 150), 'N': (165, 40, 40),  # meat / red
    'Y': (255, 220, 60), 'O': (214, 150, 0), 'T': (128, 81, 35),   # brass / wood
    'G': (200, 240, 255),                                   # lens
    'R': (230, 30, 30), 'r': (160, 10, 20),                # vest / heart
    'H': (255, 230, 120), 'h': (220, 170, 60),             # straw
}
TALENTS = {
    192: [  # big eater: meat on the bone
        ".gggggggggggggg.",
        "ggggggggggggEEgg",
        "gggggEEEEEEEBBEg",
        "ggggEKKKKKKEBCEg",
        "gggEKLLKKKKKEEgg",
        "ggEKLKKKKKKKNEgg",
        "ggEKKKKKKKKKNEgg",
        "ggEKKKKKKKKNNEgg",
        "ggEKKKKKKKNNEggg",
        "ggEEKKKKNNNEEggg",
        "gEBEENNNNEEggggg",
        "EBBBEEEEEggggggg",
        "EBCBEggggggggggg",
        "gEEBCEgggggggggg",
        "ggEBCEgggggggggg",
        ".ggEEgggggggggg.",
    ],
    193: [  # pirate's senses: spyglass
        ".bbbbbbbbbbbbbb.",
        "bbbbbbbbbbbEEEbb",
        "bbbbbbbbbbEGGGEb",
        "bbbbbbbbbEYGGGEb",
        "bbbbbbbbEYYEGEbb",
        "bbbbbbbEYYOOEbbb",
        "bbbbbbEYYOEEbbbb",
        "bbbbbEEOOEbbbbbb",
        "bbbbEYEEEbbbbbbb",
        "bbbEYYOEbbbbbbbb",
        "bbETTOEbbbbbbbbb",
        "bETTTEbbbbbbbbbb",
        "ETTTEbbbbbbbbbbb",
        "ETTEbbbbbbbbbbbb",
        "bEEbbbbbbbbbbbbb",
        ".bbbbbbbbbbbbbb.",
    ],
    194: [  # captain's grit: Luffy's open red vest
        ".wwwwwwwwwwwwww.",
        "wwwwwwwwwwwwwwww",
        "wwwwEEEwwEEEwwww",
        "wwwERRREwERRREww",
        "wwERRRREwERRRREw",
        "wERRRRRREERRRRRE",
        "wERRERRYEERRERRE",
        "wEEEERRREERRREEE",
        "wwwwERRYEERRREww",
        "wwwwERRREERRREww",
        "wwwwERRYEERRREww",
        "wwwwERRREERRREww",
        "wwwwErrrEErrrEww",
        "wwwwEEEEwwEEEEww",
        "wwwwwwwwwwwwwwww",
        ".wwwwwwwwwwwwww.",
    ],
    195: [  # captain's toughness: straw hat on a heart
        ".wwwwwwwwwwwwww.",
        "wwwwwwEEEEwwwwww",
        "wwwwwEHHHHEwwwww",
        "wwwwwEHHHhEwwwww",
        "wwwwwERRRREwwwww",
        "wwwEEEhhhhEEEwww",
        "wwEHHHHHHHHHhEww",
        "wwwEEERRRREEEwww",
        "wwERREKKKKERRRww",
        "wERLRRRRRRRRRREw",
        "wERRRRRRRRRRRrEw",
        "wwERRRRRRRRRrEww",
        "wwwERRRRRRRrEwww",
        "wwwwERRRRRrEwwww",
        "wwwwwERRRrEwwwww",
        ".wwwwwEEEEwwwww.",
    ],
}


def talent_icons():
    path = os.path.join(ROOT, 'interfaces', 'talent_icons.png')
    sheet = Image.open(path).convert('RGBA')
    per_row = sheet.width // 16
    for slot, art in TALENTS.items():
        assert len(art) == 16, slot
        ox, oy = (slot % per_row) * 16, (slot // per_row) * 16
        sheet.paste(Image.new('RGBA', (16, 16), (0, 0, 0, 0)), (ox, oy))
        for y, line in enumerate(art):
            assert len(line) == 16, (slot, y, line)
            for x, ch in enumerate(line):
                if ch != '.':
                    sheet.putpixel((ox + x, oy + y), TALENT_PAL[ch] + (255,))
    sheet.save(path)


# ---------------------------------------------------------------- stretching arm effect
# left 4x6: arm segment (repeated along the stretch), right 8x8: fist at the tip
ARM_SEGMENT = [
    "kkkk",
    "SSSS",
    "SSSS",
    "ssss",
    "ssss",
    "kkkk",
]
ARM_FIST = [
    "..kkkk..",
    ".kSSSSk.",
    "kSSsSSsk",
    "kSSSSSsk",
    "kSSSSSsk",
    "ksSSSssk",
    ".ksssk..",
    "..kkk...",
]


def arm_effect():
    img = Image.new('RGBA', (12, 8), (0, 0, 0, 0))
    for y, line in enumerate(ARM_SEGMENT):
        for x, ch in enumerate(line):
            img.putpixel((x, y + 1), P[ch] + (255,))
    for y, line in enumerate(ARM_FIST):
        for x, ch in enumerate(line):
            if ch != '.':
                img.putpixel((4 + x, y), P[ch] + (255,))
    os.makedirs(os.path.join(ROOT, 'effects'), exist_ok=True)
    img.save(os.path.join(ROOT, 'effects', 'rubber_arm.png'))


if __name__ == '__main__':
    hero_sheet()
    print('rubber fist icon size (for assignItemRect):', item_icon())
    talent_icons()
    arm_effect()
