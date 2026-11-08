"""Draws Luffy's high-resolution (32x32) icons in the original game's style.

Usage (from the repository root):
    python3 tools/luffy_icons_hd.py

The game shows these at the same on-screen size as normal 16x16 icons (drawn at
half scale, see sprites/HDIcons.java), so they carry twice the detail. Outer
outlines are 2px so line weight on screen matches the original icons.

Writes:
  core/src/main/assets/sprites/luffy_items_hd.png       32x32 item icons
  core/src/main/assets/interfaces/luffy_talents_hd.png  32x32 talent icons
and prints the packed item sizes used in HDIcons.java.
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(__file__), '..', 'core', 'src', 'main', 'assets')
N = 32
OUTLINE = (0, 0, 0)


# ------------------------------------------------------------------ helpers
def mask():
    return Image.new('1', (N, N), 0)


def pts(m):
    return {(x, y) for x in range(N) for y in range(N) if m.getpixel((x, y))}


def shade(canvas, m, base, light, dark, mid_dark=None, light_w=1, dark_w=2):
    """Fills a shape with SPD style lighting: lit top-left edge, shadowed
    bottom-right edge, optional darker lower half."""
    p = pts(m)
    if not p:
        return p
    ys = [y for _, y in p]
    top, bottom = min(ys), max(ys)
    for (x, y) in p:
        c = base
        if mid_dark and y > top + (bottom - top) * 0.6:
            c = mid_dark
        if any((x + dx, y + dy) not in p for dx, dy in ((0, 1), (1, 0)) for _ in range(1)) or \
           any((x + dx * k, y + dy * k) not in p for dx, dy in ((0, 1), (1, 0)) for k in range(1, dark_w + 1)):
            c = dark
        if any((x - dx * k, y - dy * k) not in p for dx, dy in ((0, 1), (1, 0)) for k in range(1, light_w + 1)):
            c = light
        canvas.putpixel((x, y), c + (255,))
    return p


def outline(canvas, width=2, color=OUTLINE, inside=None):
    """Adds an outline of the given width around everything drawn so far
    (or around the given point set)."""
    filled = inside if inside is not None else {(x, y) for x in range(N) for y in range(N) if canvas.getpixel((x, y))[3]}
    ring = set()
    frontier = set(filled)
    for _ in range(width):
        nxt = set()
        for (x, y) in frontier:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if 0 <= n[0] < N and 0 <= n[1] < N and n not in filled and n not in ring:
                    nxt.add(n)
        ring |= nxt
        frontier = nxt
    for p in ring:
        canvas.putpixel(p, color + (255,))


def line(canvas, xy, color, width=1):
    ImageDraw.Draw(canvas).line(xy, fill=color + (255,), width=width)


def px(canvas, points, color):
    for p in points:
        canvas.putpixel(p, color + (255,))


def tile(color, border):
    """Rounded square talent tile, like the original talent icons."""
    t = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    d.rounded_rectangle((0, 0, N - 1, N - 1), radius=5, fill=border + (255,))
    d.rounded_rectangle((2, 2, N - 3, N - 3), radius=4, fill=color + (255,))
    return t


def object_layer():
    return Image.new('RGBA', (N, N), (0, 0, 0, 0))


def on_tile(t, obj, outline_w=2):
    outline(obj, outline_w)
    t.alpha_composite(obj)
    return t


# ------------------------------------------------------------------ palettes
SKIN = (255, 218, 191)
SKIN_L = (255, 236, 220)
SKIN_D = (220, 172, 140)
SKIN_DD = (176, 126, 96)

MEAT = (206, 72, 60)
MEAT_L = (240, 120, 100)
MEAT_D = (150, 40, 38)
FAT = (250, 214, 196)
BONE = (250, 246, 236)
BONE_D = (196, 188, 172)

BRASS = (240, 196, 72)
BRASS_L = (255, 236, 150)
BRASS_D = (178, 128, 38)
WOOD = (150, 96, 54)
WOOD_L = (190, 132, 80)
WOOD_D = (104, 62, 32)
GLASS = (170, 220, 255)

VEST = (210, 38, 42)
VEST_L = (240, 86, 80)
VEST_D = (146, 22, 30)
BUTTON = (250, 210, 80)

STRAW = (240, 200, 104)
STRAW_L = (255, 238, 160)
STRAW_D = (192, 148, 62)
BAND = (210, 38, 40)
BAND_D = (150, 22, 30)
HEART = (226, 58, 68)
HEART_L = (255, 130, 136)
HEART_D = (160, 28, 44)

GREEN, GREEN_B = (52, 168, 60), (24, 104, 34)
BLUE, BLUE_B = (40, 140, 230), (20, 84, 160)
WHITE, WHITE_B = (240, 240, 240), (150, 150, 150)


# ------------------------------------------------------------------ item: rubber fist
def rubber_fist():
    c = object_layer()
    d = ImageDraw.Draw

    # wrist
    m = mask(); d(m).rectangle((9, 21, 20, 29), fill=1)
    shade(c, m, SKIN_D, SKIN, SKIN_DD)
    # fingers block (side view, knuckles facing right)
    m = mask(); d(m).rounded_rectangle((5, 5, 27, 22), radius=5, fill=1)
    fingers = shade(c, m, SKIN, SKIN_L, SKIN_D, mid_dark=None)
    # finger creases
    for x in (11, 16, 21):
        line(c, [(x, 6), (x, 14)], SKIN_DD)
    # knuckle highlights
    for x in (8, 13, 18, 23):
        px(c, [(x, 7), (x + 1, 7), (x, 8)], SKIN_L)
    # thumb wrapping across the front
    m = mask(); d(m).rounded_rectangle((7, 14, 22, 20), radius=3, fill=1)
    thumb = shade(c, m, SKIN, SKIN_L, SKIN_D)
    line(c, [(8, 13), (21, 13)], SKIN_DD)   # top edge of thumb
    px(c, [(21, 15), (22, 15), (21, 16)], (214, 160, 150))  # thumbnail tint
    outline(c, 2)
    return c


# ------------------------------------------------------------------ talents
def big_eater():
    t = tile(GREEN, GREEN_B)
    o = object_layer()
    d = ImageDraw.Draw
    # bone sticking out both ends
    m = mask(); d(m).line([(6, 26), (25, 7)], fill=1, width=4)
    shade(o, m, BONE, (255, 255, 255), BONE_D)
    for (cx, cy) in ((5, 25), (7, 27), (24, 6), (26, 8)):
        m = mask(); d(m).ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=1)
        shade(o, m, BONE, (255, 255, 255), BONE_D)
    # meat chunk
    m = mask(); d(m).ellipse((8, 7, 24, 23), fill=1)
    shade(o, m, MEAT, MEAT_L, MEAT_D, mid_dark=(184, 58, 50))
    # fat streak and shine
    line(o, [(12, 12), (17, 9)], FAT)
    line(o, [(13, 17), (20, 12)], FAT)
    px(o, [(11, 10), (12, 9)], (255, 200, 190))
    return on_tile(t, o)


def pirates_senses():
    t = tile(BLUE, BLUE_B)
    o = object_layer()
    d = ImageDraw.Draw
    # leather grip
    m = mask(); d(m).line([(6, 26), (15, 17)], fill=1, width=5)
    shade(o, m, WOOD, WOOD_L, WOOD_D)
    # brass tube sections, wider towards the lens
    m = mask(); d(m).line([(14, 18), (21, 11)], fill=1, width=6)
    shade(o, m, BRASS, BRASS_L, BRASS_D)
    m = mask(); d(m).line([(20, 12), (25, 7)], fill=1, width=8)
    shade(o, m, BRASS, BRASS_L, BRASS_D)
    # rings
    line(o, [(13, 15), (17, 19)], BRASS_D)
    line(o, [(19, 9), (23, 13)], BRASS_D)
    # lens
    m = mask(); d(m).ellipse((23, 3, 29, 9), fill=1)
    shade(o, m, GLASS, (255, 255, 255), (90, 150, 210))
    return on_tile(t, o)


def captains_grit():
    t = tile(WHITE, WHITE_B)
    o = object_layer()
    d = ImageDraw.Draw
    # left and right vest halves (open in the middle)
    left = [(5, 9), (11, 5), (14, 7), (14, 27), (7, 27), (7, 15), (4, 17)]
    right = [(27, 9), (21, 5), (18, 7), (18, 27), (25, 27), (25, 15), (28, 17)]
    for poly in (left, right):
        m = mask(); d(m).polygon(poly, fill=1)
        shade(o, m, VEST, VEST_L, VEST_D)
    # collar fold
    line(o, [(11, 6), (13, 12)], VEST_D)
    line(o, [(21, 6), (19, 12)], VEST_D)
    # buttons
    for y in (13, 18, 23):
        px(o, [(13, y), (12, y), (13, y + 1), (12, y + 1)], BUTTON)
    return on_tile(t, o)


def captains_toughness():
    t = tile(WHITE, WHITE_B)
    o = object_layer()
    d = ImageDraw.Draw
    # heart
    m = mask()
    d(m).ellipse((4, 11, 16, 23), fill=1)
    d(m).ellipse((15, 11, 27, 23), fill=1)
    d(m).polygon([(5, 19), (26, 19), (16, 29)], fill=1)
    shade(o, m, HEART, HEART_L, HEART_D, mid_dark=(196, 44, 56))
    px(o, [(8, 14), (9, 13), (10, 13), (8, 15)], (255, 190, 194))
    # straw hat resting on top of the heart
    m = mask(); d(m).ellipse((3, 9, 28, 14), fill=1)      # brim
    shade(o, m, STRAW, STRAW_L, STRAW_D)
    m = mask(); d(m).rounded_rectangle((9, 2, 22, 11), radius=4, fill=1)   # crown
    shade(o, m, STRAW, STRAW_L, STRAW_D)
    m = mask(); d(m).rectangle((9, 8, 22, 10), fill=1)    # band
    shade(o, m, BAND, (240, 90, 86), BAND_D, light_w=1, dark_w=1)
    # straw weave
    for x in range(11, 21, 3):
        px(o, [(x, 4), (x + 1, 6)], STRAW_D)
    return on_tile(t, o)


# ------------------------------------------------------------------ output
def sheet(icons, path, cols=8):
    rows = (len(icons) + cols - 1) // cols
    img = Image.new('RGBA', (cols * N, max(1, rows) * N), (0, 0, 0, 0))
    sizes = []
    for i, ic in enumerate(icons):
        img.alpha_composite(ic, ((i % cols) * N, (i // cols) * N))
        sizes.append(ic.size)
    img.save(path)
    return sizes


def packed(icon):
    """Items are packed into the top-left of their cell, like the original sheet."""
    b = icon.getbbox()
    out = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    cropped = icon.crop(b)
    out.alpha_composite(cropped, (0, 0))
    return out, cropped.size


if __name__ == '__main__':
    fist, fist_size = packed(rubber_fist())
    sheet([fist], os.path.join(ROOT, 'sprites', 'luffy_items_hd.png'))
    print('RUBBER_FIST hd size:', fist_size)
    sheet([big_eater(), pirates_senses(), captains_grit(), captains_toughness()],
          os.path.join(ROOT, 'interfaces', 'luffy_talents_hd.png'))
