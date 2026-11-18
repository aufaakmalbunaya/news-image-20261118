#!/usr/bin/env python3
"""THE WORLD IN ONE PICTURE: Wednesday 18 November 2026.

A newspaper front page, 1024x1024, drawn with the Python standard
library only. Four stories from 18 November 2026: Iran strikes US
bases in Kuwait and Bahrain after the US hit Qeshm Island; Ukraine
hits the Kerch Bridge a second day; Xi and Putin meet in Shenzhen
ahead of the three-way summit with Trump; Mary Peltola wins Alaska
and Democrats take a 56-44 Senate majority.

Deterministic: no time, no randomness, no network. Writes entry.png
ONLY to $MAKEFUN_OUTPUT_DIR when set, else beside this script.
"""
import math
import os
import struct
import zlib

W = 1024
H = 1024

CREAM = (253, 246, 227)
INK = (18, 18, 18)
PAPER2 = (244, 234, 205)
SKY = (178, 216, 240)
NIGHT = (38, 52, 96)
NIGHT2 = (70, 80, 140)
SEA = (38, 110, 180)
DEEPSEA = (24, 80, 150)
GREY = (120, 120, 118)
DARKGREY = (70, 70, 68)
STEEL = (150, 158, 165)
ORANGE = (240, 120, 20)
FLAME = (255, 176, 32)
RED = (200, 40, 32)
BLUE = (40, 80, 180)
DUSK = (232, 150, 90)
DUSK2 = (120, 80, 130)
TAN = (222, 196, 140)
GOLD = (255, 214, 90)

# 5x7 bitmap font, each glyph is 7 rows of 5 bits ("1" = ink).
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "00000", "00100"),
    ",": ("00000", "00000", "00000", "00000", "00000", "00100", "01000"),
    "'": ("00000", "00100", "00100", "00000", "00000", "00000", "00000"),
    ":": ("00000", "00100", "00000", "00000", "00000", "00100", "00000"),
    ";": ("00000", "00100", "00000", "00000", "00000", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
}

PIX = bytearray(W * H * 3)


def put(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        PIX[i], PIX[i + 1], PIX[i + 2] = color


def fill_rect(x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = yy * W * 3
        for xx in range(x0, x1):
            i = base + xx * 3
            PIX[i], PIX[i + 1], PIX[i + 2] = color


def hline(x, y, w, color, thick=1):
    fill_rect(x, y, w, thick, color)


def vline(x, y, h, color, thick=1):
    fill_rect(x, y, thick, h, color)


def circle(cx, cy, r, color):
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        for xx in range(cx - dx, cx + dx + 1):
            put(xx, cy + dy, color)


def line(x0, y0, x1, y1, color, thick=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        for t in range(thick):
            put(x0 + t, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def poly_fill(points, color):
    ys = [p[1] for p in points]
    for y in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            for xx in range(int(xs[k]), int(xs[k + 1]) + 1):
                put(xx, y, color)


def text_w(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(x, y, text, scale, color):
    for ci, ch in enumerate(text):
        glyph = FONT.get(ch, FONT[" "])
        ox = x + ci * 6 * scale
        for r in range(7):
            row = glyph[r]
            for c in range(5):
                if row[c] == "1":
                    fill_rect(ox + c * scale, y + r * scale, scale, scale, color)


def draw_centered(cx, y, text, scale, color):
    draw_text(cx - text_w(text, scale) // 2, y, text, scale, color)


def wrap(text, scale, max_w):
    max_chars = max(1, max_w // (6 * scale))
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(cx, y, text, scale, color, max_w, leading=4):
    lines = wrap(text, scale, max_w)
    for i, ln in enumerate(lines):
        draw_centered(cx, y + i * (7 * scale + leading), ln, scale, color)
    return len(lines) * (7 * scale + leading)


def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += PIX[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---- lead scene: drones over the Gulf at night ----
def scene_gulf(px, py, pw, ph):
    fill_rect(px, py, pw, ph, NIGHT)
    fill_rect(px, py + int(ph * 0.42), pw, ph - int(ph * 0.42), NIGHT2)
    # stars
    for sx, sy in ((30, 18), (90, 40), (150, 14), (220, 34), (300, 16),
                   (380, 38), (450, 20), (500, 44), (60, 66), (260, 62),
                   (410, 66), (520, 70)):
        put(px + sx, py + sy, GOLD)
        put(px + sx + 1, py + sy, GOLD)
    # low moon
    circle(px + pw - 70, py + 52, 26, (240, 230, 200))
    circle(px + pw - 78, py + 46, 6, (210, 200, 170))
    circle(px + pw - 62, py + 60, 4, (210, 200, 170))
    sea_y = py + int(ph * 0.60)
    fill_rect(px, sea_y, pw, ph - int(ph * 0.60), DEEPSEA)
    # moonlight path on the water
    for wx in range(px + pw - 110, px + pw - 30, 8):
        line(wx, sea_y + 18, wx + 34, sea_y + 18, (120, 150, 200), 2)
        line(wx + 8, sea_y + 44, wx + 28, sea_y + 44, (120, 150, 200), 2)
    # tanker: dark hull, lit deck houses, flames midship
    hull_y = sea_y - 26
    fill_rect(px + 40, hull_y, pw - 110, 40, (120, 24, 20))
    fill_rect(px + 40, hull_y + 40, pw - 110, 8, INK)
    fill_rect(px + 56, hull_y - 40, 64, 40, (210, 210, 205))
    fill_rect(px + pw - 150, hull_y - 58, 74, 58, (225, 225, 220))
    fill_rect(px + pw - 138, hull_y - 52, 12, 12, GOLD)
    fill_rect(px + pw - 118, hull_y - 52, 12, 12, GOLD)
    fill_rect(px + pw - 138, hull_y - 34, 12, 12, GOLD)
    # flames bursting from the deck
    for fx, fh in ((px + 190, 56), (px + 224, 76), (px + 258, 58),
                   (px + 292, 68), (px + 326, 50)):
        poly_fill([(fx - 18, hull_y), (fx, hull_y - fh), (fx + 18, hull_y)], ORANGE)
        poly_fill([(fx - 10, hull_y), (fx, hull_y - fh + 22), (fx + 10, hull_y)], FLAME)
    # black smoke rolling up
    circle(px + 230, hull_y - 66, 16, INK)
    circle(px + 258, hull_y - 84, 18, DARKGREY)
    circle(px + 228, hull_y - 96, 13, DARKGREY)
    circle(px + 262, hull_y - 108, 11, GREY)
    # two drones diving in from the sky, bright heads, dotted trails
    line(px + 60, py + 20, px + 170, py + 108, (255, 255, 255), 2)
    circle(px + 172, py + 110, 7, FLAME)
    line(px + 330, py + 14, px + 420, py + 96, (255, 255, 255), 2)
    circle(px + 422, py + 98, 7, FLAME)


# ---- scene: the Kerch Bridge, broken ----
def scene_kerch(px, py, pw, ph):
    fill_rect(px, py, pw, ph, SKY)
    water_y = py + int(ph * 0.62)
    fill_rect(px, water_y, pw, ph - int(ph * 0.62), SEA)
    circle(px + pw - 52, py + 34, 22, GOLD)
    deck_y = py + int(ph * 0.44)
    # left span stands, right span stands, the middle is gone
    fill_rect(px + 8, deck_y, pw // 2 - 52, 12, STEEL)
    fill_rect(px + pw // 2 + 40, deck_y, pw // 2 - 48, 12, STEEL)
    # arch over the left span
    line(px + 30, deck_y, px + pw // 4, deck_y - 64, DARKGREY, 4)
    line(px + pw // 4, deck_y - 64, px + pw // 2 - 52, deck_y, DARKGREY, 4)
    # right tower leaning after the blast
    line(px + pw - 96, deck_y, px + pw - 66, deck_y - 78, DARKGREY, 6)
    # deck slabs tumbling into the strait
    poly_fill([(px + pw // 2 - 44, deck_y), (px + pw // 2 - 12, deck_y),
               (px + pw // 2 - 22, deck_y + 42), (px + pw // 2 - 50, deck_y + 28)], STEEL)
    poly_fill([(px + pw // 2 + 6, deck_y + 8), (px + pw // 2 + 30, deck_y + 4),
               (px + pw // 2 + 22, deck_y + 34), (px + pw // 2 + 2, deck_y + 30)], DARKGREY)
    # smoke from the gap
    circle(px + pw // 2 - 6, deck_y - 20, 14, DARKGREY)
    circle(px + pw // 2 + 8, deck_y - 40, 16, GREY)
    circle(px + pw // 2 - 2, deck_y - 58, 12, GREY)
    # splash rings where the span fell
    for rx, ry, rr in ((pw // 2 - 18, water_y + 34, 22), (pw // 2 + 14, water_y + 52, 16)):
        for a in range(0, 360, 8):
            put(px + rx + int(rr * math.cos(math.radians(a))),
                py + ry + int(rr * 0.55 * math.sin(math.radians(a))),
                (255, 255, 255))
    # waves
    for wx in range(px + 8, px + pw - 8, 40):
        line(wx, water_y + 66, wx + 22, water_y + 66, (255, 255, 255), 2)


# ---- scene: three flags over the Shenzhen skyline ----
def scene_summit(px, py, pw, ph):
    fill_rect(px, py, pw, ph, DUSK)
    fill_rect(px, py + int(ph * 0.40), pw, ph - int(ph * 0.40), DUSK2)
    circle(px + pw - 56, py + 30, 18, (255, 220, 140))
    # skyline towers with lit windows
    towers = [(6, 96, 52, 100), (62, 66, 46, 130), (112, 104, 54, 92),
              (170, 56, 50, 140), (224, 88, 46, 108), (274, 70, 18, 126)]
    for tx, ty, tw, th in towers:
        base_y = py + ph - th - 46
        fill_rect(px + tx, base_y, tw, th, (40, 36, 52))
        for wy in range(base_y + 10, py + ph - 56, 20):
            for wx in range(px + tx + 7, px + tx + tw - 7, 16):
                fill_rect(wx, wy, 6, 8, (255, 220, 120))
    ground_y = py + ph - 46
    fill_rect(px, ground_y, pw, 46, (60, 50, 44))
    # three flags on poles: China red, US stripes, Russia white-blue-red
    flag_x = [px + 34, px + pw // 2 - 22, px + pw - 84]
    flag_cols = [(RED, RED, RED),
                 (RED, (255, 255, 255), BLUE),
                 ((255, 255, 255), BLUE, RED)]
    for fx, cols in zip(flag_x, flag_cols):
        vline(fx, py + 12, 62, INK, 3)
        for i, col in enumerate(cols):
            fill_rect(fx + 3, py + 12 + i * 11, 40, 11, col)
        # small stars on the red flag
        if cols[0] == RED and cols[1] == RED:
            for sx, sy in ((8, 16), (20, 20), (28, 28)):
                put(fx + 3 + sx, py + 12 + sy, GOLD)
    # three leaders seated at one table
    for fx in (px + 56, px + pw // 2 - 16, px + pw - 108):
        circle(fx + 18, ground_y + 6, 8, (250, 220, 190))
        fill_rect(fx + 7, ground_y + 15, 22, 24, INK)
    fill_rect(px + 40, ground_y + 32, pw - 80, 5, (150, 110, 60))


# ---- scene: the Senate count, 56 to 44 ----
def scene_senate(px, py, pw, ph):
    fill_rect(px, py, pw, ph, PAPER2)
    # ballot box with a big check
    box_x, box_y = px + pw // 2 - 52, py + 12
    fill_rect(box_x, box_y, 104, 64, (200, 170, 110))
    fill_rect(box_x - 10, box_y - 12, 124, 14, INK)
    fill_rect(box_x + 36, box_y - 12, 32, 4, CREAM)
    line(box_x + 22, box_y + 34, box_x + 44, box_y + 56, RED, 7)
    line(box_x + 44, box_y + 56, box_x + 84, box_y + 12, RED, 7)
    draw_centered(px + pw // 2, box_y + 82, "ALASKA DECIDES", 2, INK)
    # the tally bar: 56 blue, 44 red
    bar_y = py + ph - 58
    bar_w = pw - 40
    dem_w = int(bar_w * 56 / 100)
    fill_rect(px + 20, bar_y, dem_w, 30, BLUE)
    fill_rect(px + 20 + dem_w, bar_y, bar_w - dem_w, 30, RED)
    for t in range(2):
        hline(px + 20, bar_y + t, bar_w, INK)
        hline(px + 20, bar_y + 29 - t, bar_w, INK)
        vline(px + 20 + t, bar_y, 30, INK)
        vline(px + 20 + bar_w - 1 - t, bar_y, 30, INK)
    draw_text(px + 30, bar_y + 8, "DEM 56", 2, (255, 255, 255))
    draw_text(px + 20 + dem_w + 12, bar_y + 8, "GOP 44", 2, (255, 255, 255))


def lead_panel(px, py, pw, ph, scene, headline, caption):
    fill_rect(px, py, pw, ph, PAPER2)
    for t in range(3):
        vline(px + t, py, ph, INK)
        vline(px + pw - 1 - t, py, ph, INK)
        hline(px, py + t, pw, INK)
        hline(px, py + ph - 1 - t, pw, INK)
    scene(px + 6, py + 6, 540, ph - 12)
    tx = px + 540 + 24
    tw = pw - 540 - 36
    hy = py + 34
    draw_wrapped(tx + tw // 2, hy, headline, 3, INK, tw)
    cy = hy + 2 * (7 * 3 + 4) + 22
    draw_wrapped(tx + tw // 2, cy, caption, 2, INK, tw, leading=6)


def panel(px, py, pw, ph, scene, headline, caption):
    fill_rect(px, py, pw, ph, PAPER2)
    for t in range(3):
        vline(px + t, py, ph, INK)
        vline(px + pw - 1 - t, py, ph, INK)
        hline(px, py + t, pw, INK)
        hline(px, py + ph - 1 - t, pw, INK)
    scene_h = int(ph * 0.50)
    scene(px + 6, py + 6, pw - 12, scene_h)
    hy = py + 6 + scene_h + 14
    draw_wrapped(px + pw // 2, hy, headline, 3, INK, pw - 28)
    cy = hy + 2 * (7 * 3 + 4) + 12
    draw_wrapped(px + pw // 2, cy, caption, 2, INK, pw - 28, leading=5)


def masthead():
    draw_centered(W // 2, 28, "THE WORLD IN ONE PICTURE", 5, INK)
    hline(24, 94, W - 48, INK, 3)
    draw_centered(W // 2, 106, "WEDNESDAY 18 NOVEMBER 2026", 4, INK)
    hline(24, 150, W - 48, INK, 3)


def footer():
    y0 = 862
    hline(24, y0, W - 48, INK, 3)
    draw_centered(W // 2, y0 + 12, "ALSO IN THE NEWS", 3, INK)
    items = [
        "- EBOLA IN DR CONGO PASSES 11,000 CASES",
        "- US LOSES MEASLES-FREE STATUS AFTER 26 YEARS",
        "- RUSSIAN MILITARY PLANE CRASHES IN SIBERIA: 19 DEAD",
    ]
    for i, item in enumerate(items):
        draw_text(48, y0 + 52 + i * 26, item, 2, INK)


def main():
    fill_rect(0, 0, W, H, CREAM)
    for t in range(8):
        vline(t, 0, H, INK)
        vline(W - 1 - t, 0, H, INK)
        hline(0, t, W, INK)
        hline(0, H - 1 - t, W, INK)
    masthead()
    lead_panel(24, 166, 976, 312, scene_gulf,
               "IRAN STRIKES US BASES IN KUWAIT AND BAHRAIN",
               "TEHRAN SAYS IT TARGETED ALI AL SALEM AIR BASE "
               "AFTER US JETS HIT QESHM ISLAND.")
    panel(24, 494, 312, 352, scene_kerch, "KERCH BRIDGE HIT AGAIN",
          "UKRAINE STRIKES THE CRIMEA LINK FOR A SECOND DAY; "
          "PART OF THE ROAD SPAN FALLS.")
    panel(356, 494, 312, 352, scene_summit, "XI AND PUTIN MEET",
          "THE TWO LEADERS TALK IN SHENZHEN AHEAD OF THURSDAY'S "
          "THREE-WAY SUMMIT WITH TRUMP.")
    panel(688, 494, 312, 352, scene_senate, "DEMOCRATS TAKE SENATE",
          "MARY PELTOLA WINS ALASKA; DEMOCRATS HOLD A 56-44 "
          "MAJORITY IN THE SENATE.")
    footer()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if outdir:
        os.makedirs(outdir, exist_ok=True)
        write_png(os.path.join(outdir, "entry.png"))
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        write_png(os.path.join(here, "entry.png"))


if __name__ == "__main__":
    main()
