import sys
from PIL import Image

SRC, DST, PREVIEW = sys.argv[1], sys.argv[2], sys.argv[3]

FONT = {
 'O': [".###.","#...#","#...#","#...#","#...#","#...#",".###."],
 'N': ["#...#","##..#","#.#.#","#..##","#...#","#...#","#...#"],
 'E': ["#####","#....","#....","####.","#....","#....","#####"],
 'P': ["####.","#...#","#...#","####.","#....","#....","#...."],
 'I': ["###",".#.",".#.",".#.",".#.",".#.","###"],
 'C': [".###.","#...#","#....","#....","#....","#...#",".###."],
 'X': ["#...#","#...#",".#.#.","..#..",".#.#.","#...#","#...#"],
 'L': ["#....","#....","#....","#....","#....","#....","#####"],
 'D': ["####.","#...#","#...#","#...#","#...#","#...#","####."],
 'U': ["#...#","#...#","#...#","#...#","#...#","#...#",".###."],
 'G': [".###.","#...#","#....","#.###","#...#","#...#",".###."],
}

def text_mask(text, sx, sy, gap):
    """returns set of (x,y) filled pixels and width,height"""
    pts = set(); x = 0
    for ch in text:
        if ch == ' ':
            x += 3*sx; continue
        g = FONT[ch]
        for r, row in enumerate(g):
            for c, v in enumerate(row):
                if v == '#':
                    for dy in range(sy):
                        for dx in range(sx):
                            pts.add((x + c*sx + dx, r*sy + dy))
                            pts.add((x + c*sx + dx + 1, r*sy + dy))
        x += len(g[0])*sx + 1 + gap
    return pts, x - gap, 7*sy

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))

GOLD = ((255, 232, 120), (226, 132, 28))
GOLD_OUT = (74, 34, 8)
STONE = ((190, 200, 170), (92, 104, 82))
STONE_OUT = (30, 34, 26)
SHADOW = (0, 0, 0, 150)

def draw_text(img, glow, text, ox, oy, sx, sy, gap, pal, out, glowcol=None):
    pts, w, h = text_mask(text, sx, sy, gap)
    px = img.load()
    # drop shadow
    for (x, y) in pts:
        for d in [(1, 2), (2, 2), (1, 3)]:
            X, Y = ox+x+d[0], oy+y+d[1]
            if 0 <= X < img.width and 0 <= Y < img.height and px[X, Y][3] == 0:
                px[X, Y] = SHADOW
    # outline
    for (x, y) in pts:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (x+dx, y+dy) not in pts:
                    px[ox+x+dx, oy+y+dy] = out + (255,)
    # fill with vertical gradient and bevel
    for (x, y) in pts:
        t = y / max(1, h-1)
        c = lerp(pal[0], pal[1], t)
        if (x, y-1) not in pts:
            c = lerp(c, (255, 255, 255), 0.45)
        elif (x, y+1) not in pts:
            c = lerp(c, (0, 0, 0), 0.35)
        elif (x-1, y) not in pts:
            c = lerp(c, (255, 255, 255), 0.15)
        elif (x+1, y) not in pts:
            c = lerp(c, (0, 0, 0), 0.2)
        px[ox+x, oy+y] = c + (255,)
        if glow is not None and glowcol and (x, y-1) not in pts:
            glow.load()[ox+x, oy+y] = glowcol + (255,)
    return w, h

def draw_hat(img, glow, cx, top, scale=1):
    """straw hat with a red band, roughly 26 x 12"""
    px = img.load()
    straw = (238, 204, 104); straw_d = (198, 152, 62); straw_l = (255, 236, 160)
    band = (206, 36, 36); band_d = (140, 20, 24)
    out = (60, 34, 10)
    pts = {}
    # crown: half-dome 14 wide, 6 tall
    cw, ch = 8, 7
    for y in range(ch):
        yy = (ch - y - 0.5) / ch
        half = int(round(cw * (1 - yy*yy) ** 0.5)) if yy < 1 else 0
        for x in range(-half, half):
            col = straw if (x + y) % 3 else straw_d
            if y == 0 or x == -half: col = straw_l
            pts[(x, y)] = col
    # band 2 rows
    for y in (ch, ch+1):
        for x in range(-cw, cw):
            pts[(x, y)] = band if y == ch else band_d
    # brim: ellipse 26 wide, 3 tall
    bw = 15
    for y in range(3):
        w = bw - (1 if y == 2 else 0)
        for x in range(-w, w):
            col = straw if y < 2 else straw_d
            if y == 0 and abs(x) > cw - 1: col = straw_l
            pts[(x, ch+2+y)] = col
    for (x, y), c in list(pts.items()):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (x+dx, y+dy) not in pts:
                    X, Y = cx+x+dx, top+y+dy
                    if px[X, Y][3] != 255 or px[X, Y][:3] == (0, 0, 0):
                        px[X, Y] = out + (255,)
    for (x, y), c in pts.items():
        px[cx+x, top+y] = c + (255,)
        if glow is not None and c == straw_l:
            glow.load()[cx+x, top+y] = (255, 230, 140, 255)

def compose(W, H, layout):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    layout(img, glow)
    return img, glow

def centered(text, sx, gap, W):
    _, w, _ = text_mask(text, sx, 1, gap)
    return (W - w) // 2

def portrait(img, glow):
    W = img.width
    draw_hat(img, glow, W//2, 2)
    draw_text(img, glow, "ONE PIECE", centered("ONE PIECE", 2, 2, W), 20, 2, 3, 2, GOLD, GOLD_OUT, (255, 220, 110))
    draw_text(img, None, "PIXEL", centered("PIXEL", 2, 2, W), 46, 2, 2, 2, STONE, STONE_OUT)
    draw_text(img, None, "DUNGEON", centered("DUNGEON", 2, 2, W), 64, 2, 2, 2, STONE, STONE_OUT)
    # underline like the original
    y = 82
    for x in range(W//2 - 40, W//2 + 40):
        img.load()[x, y] = (170, 180, 150, 255)
        img.load()[x, y+1] = (40, 44, 34, 255)

def landscape(img, glow):
    W = img.width
    ox = centered("ONE PIECE", 2, 2, W)
    draw_hat(img, glow, W//2, 1)
    draw_text(img, glow, "ONE PIECE", ox, 15, 2, 3, 2, GOLD, GOLD_OUT, (255, 220, 110))
    draw_text(img, None, "PIXEL DUNGEON", centered("PIXEL DUNGEON", 2, 2, W), 40, 2, 2, 2, STONE, STONE_OUT)

banners = Image.open(SRC).convert('RGBA')
# clear the four title regions
for box in [(0, 0, 139, 100), (139, 0, 278, 100), (0, 100, 240, 157), (240, 100, 480, 157)]:
    banners.paste(Image.new('RGBA', (box[2]-box[0], box[3]-box[1]), (0, 0, 0, 0)), box[:2])

p, pg = compose(139, 100, portrait)
l, lg = compose(240, 57, landscape)
banners.paste(p, (0, 0)); banners.paste(pg, (139, 0))
banners.paste(l, (0, 100)); banners.paste(lg, (240, 100))
banners.save(DST)

bg = Image.new('RGBA', banners.size, (34, 34, 52, 255)); bg.alpha_composite(banners)
bg.resize((banners.width*3, banners.height*3), Image.NEAREST).save(PREVIEW)
