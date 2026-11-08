"""Builds Luffy's hero sprite sheet (12x15 frames, one row per armor tier).

Usage: python3 tools/make_luffy_sprite.py <warrior.png> <luffy.png>

Luffy is drawn from scratch (round chibi face, straw hat, scar under the
eye, open vest, shorts, sandals). Only the death frames (8-12) are copied
from the warrior sheet, since they show the hero's remains.

Frame layout used by HeroSprite:
  0-1 idle, 2-7 run, 8-12 die, 13-15 attack, 16-17 operate, 18 fly, 19-20 read
"""
import sys
from PIL import Image

SRC, DST = sys.argv[1], sys.argv[2]
FW, FH = 12, 15
ROWS = 8

OUTLINE = (38, 22, 20)
BASE = {
    'Y': (250, 226, 132),  # straw light
    'y': (230, 190, 92),   # straw
    'd': (186, 144, 62),   # straw dark
    'R': (210, 36, 36),    # hat band
    'H': (28, 26, 36),     # hair
    'S': (246, 200, 160),  # skin
    's': (214, 160, 124),  # skin shadow
    'E': (20, 16, 22),     # eye
    'c': (206, 128, 108),  # scar
    'M': (96, 26, 34),     # mouth
    'B': (60, 98, 192),    # shorts
    'b': (40, 66, 146),    # shorts dark
    'F': (122, 78, 44),    # sandals
    'P': (236, 226, 196),  # paper (reading)
}

# vest (V light, v dark) per armor tier; covered = chest is covered too
ARMOR = [
    ((206, 34, 38), (150, 20, 28), False),   # 0 no armor: Luffy's red vest
    ((206, 34, 38), (150, 20, 28), False),   # 1 cloth
    ((150, 98, 54), (108, 68, 36), False),   # 2 leather
    ((156, 160, 172), (104, 108, 122), True),  # 3 mail
    ((70, 150, 136), (44, 104, 96), True),   # 4 scale
    ((212, 214, 224), (150, 154, 170), True),  # 5 plate
    ((232, 186, 64), (186, 40, 40), True),   # 6 class armor
    ((232, 186, 64), (186, 40, 40), True),   # 7 unused, same as class armor
]

HEAD = [
    "............",
    ".....YYY....",
    "....YyyyY...",
    "...RRRRRRR..",
    "..dyyyyyyyd.",
    "...HSSSSSH..",
    "..HSSESSESH.",
    "..HScSSSSS..",
    "...SSSMMS...",
]
HEAD_BLINK = HEAD[:6] + ["..HSSsSSsSH."] + HEAD[7:]

TORSO = {
    'idle':    ["..SVVSSVVS..", "..SvVSSVvS.."],
    'swing1':  [".S.VVSSVVS..", "...vVSSVvSS."],
    'swing2':  ["..SVVSSVV.S.", ".SSvVSSVv..."],
    'windup':  ["SSSVVSSVVS..", "...vVSSVvS.."],
    'punch':   ["...VVSSVVSSS", "...vVSSVvSSS"],
    'recover': ["...VVSSVVSS.", "..SvVSSVv..."],
    'op1':     ["...VVSSVVS..", "..SvVSSVvSS."],
    'op2':     ["...VVSSVVSS.", "..SvVSSVvS.."],
    'up':      [".S.VVSSVV.S.", "...vVSSVv..."],
    'read':    ["...VVSSVPPS.", "..SvVSSVPP.."],
}

LEGS = {
    'stand':   ["...BBBBBB...", "...Bb..bB...", "...SS..SS...", "...FF..FF..."],
    'spread':  ["...BBBBBB...", "..Bb....bB..", "..S......S..", ".FF......FF."],
    'mid':     ["...BBBBBB...", "...Bb..bB...", "...S....S...", "..FF....FF.."],
    'pass':    ["...BBBBBB...", "....BbbB....", ".....SS.....", ".....FFF...."],
    'tuck':    ["...BBBBBB...", "...BbbbbB...", "....SSSS....", "....FFFF...."],
}


def frame(head, torso, legs):
    return head + TORSO[torso] + LEGS[legs]


FRAMES = {
    0: frame(HEAD, 'idle', 'stand'),
    1: frame(HEAD_BLINK, 'idle', 'stand'),
    2: frame(HEAD, 'swing1', 'spread'),
    3: frame(HEAD, 'swing1', 'mid'),
    4: frame(HEAD, 'idle', 'pass'),
    5: frame(HEAD, 'swing2', 'spread'),
    6: frame(HEAD, 'swing2', 'mid'),
    7: frame(HEAD, 'idle', 'pass'),
    13: frame(HEAD, 'windup', 'spread'),
    14: frame(HEAD, 'punch', 'spread'),
    15: frame(HEAD, 'recover', 'mid'),
    16: frame(HEAD, 'op1', 'stand'),
    17: frame(HEAD, 'op2', 'stand'),
    18: frame(HEAD, 'up', 'tuck'),
    19: frame(HEAD, 'read', 'stand'),
    20: frame(HEAD_BLINK, 'read', 'stand'),
}
DIE_FRAMES = range(8, 13)


def draw(sheet, fx, fy, art, tier):
    vest, vest_d, covered = ARMOR[tier]
    pal = dict(BASE)
    pal['V'], pal['v'] = vest, vest_d
    ox, oy = fx * FW, fy * FH
    filled = set()
    for y, row in enumerate(art):
        assert len(row) == FW, (fx, y, row)
        for x, ch in enumerate(row):
            if ch == '.':
                continue
            col = pal[ch]
            # armor covers the chest (rows 9-10 between the vest halves)
            if covered and y in (9, 10) and ch == 'S' and 5 <= x <= 6:
                col = vest if y == 9 else vest_d
            sheet.putpixel((ox + x, oy + y), col + (255,))
            filled.add((x, y))
    for (x, y) in list(filled):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < FW and 0 <= ny < FH and (nx, ny) not in filled:
                sheet.putpixel((ox + nx, oy + ny), OUTLINE + (255,))


warrior = Image.open(SRC).convert('RGBA')
sheet = Image.new('RGBA', warrior.size, (0, 0, 0, 0))
for fy in range(ROWS):
    for f, art in FRAMES.items():
        draw(sheet, f, fy, art, fy)
    for f in DIE_FRAMES:
        box = (f * FW, fy * FH, (f + 1) * FW, (fy + 1) * FH)
        sheet.paste(warrior.crop(box), box[:2])
sheet.save(DST)
