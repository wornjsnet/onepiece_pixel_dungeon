"""Builds a placeholder hero-select splash for Luffy (800x450 jpg).

Usage: python3 tools/make_luffy_splash.py <luffy.png> <luffy.jpg>
A sunset sea scene with Luffy's idle sprite frame scaled up.
"""
import sys, math, random
from PIL import Image

SRC, DST = sys.argv[1], sys.argv[2]
W, H = 800, 450
P = 5  # art pixel size, keeps a pixel-art look
w, h = W // P, H // P
random.seed(7)

img = Image.new('RGB', (w, h))
px = img.load()
horizon = int(h * 0.58)
for y in range(h):
    for x in range(w):
        if y < horizon:
            t = y / horizon
            c = (int(40 + 200 * t), int(30 + 90 * t), int(90 - 30 * t))
        else:
            t = (y - horizon) / (h - horizon)
            c = (int(20 + 10 * t), int(50 + 20 * t), int(100 + 30 * t))
            if (x + int(6 * math.sin(y * 0.9))) % 13 == 0 and random.random() < 0.6:
                c = (90, 130, 180)
        px[x, y] = c
# sun
sx, sy, r = int(w * 0.72), horizon - 4, 14
for y in range(sy - r, sy + 1):
    for x in range(sx - r, sx + r):
        if (x - sx) ** 2 + (y - sy) ** 2 <= r * r and 0 <= y < h:
            px[x, y] = (255, 200, 90)
# sun reflection
for y in range(horizon, min(h, horizon + 25)):
    half = max(1, r - (y - horizon) // 2)
    for x in range(sx - half, sx + half):
        if (x + y) % 2 == 0:
            px[x, y] = (230, 160, 80)

sheet = Image.open(SRC).convert('RGBA')
frame = sheet.crop((0, 0, 12, 15))
scale = 4
hero = frame.resize((12 * scale, 15 * scale), Image.NEAREST)
img = img.convert('RGBA')
hx, hy = (w - hero.width) // 2, horizon - hero.height + 18
img.alpha_composite(hero, (hx, hy))
img = img.convert('RGB').resize((W, H), Image.NEAREST)
img.save(DST, quality=92)
