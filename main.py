#!/usr/bin/env python3
"""THE WORLD IN ONE PICTURE: Wednesday 18 November 2026. Round 3.

A dense newspaper front page, 1024 by 1024 pixels, drawn with the
Python standard library only. It sums up 42 stories first reported
on Wednesday 18 November 2026: 13 illustrated lead cards, a world
map with numbered pins, 29 one-line briefs, a by-the-numbers strip,
region and field count bars, and a date-check footer naming stories
left out because they were first reported on 17 November.

Round 3 fixes the headlines round 2 got wrong: the Gulf drones
aimed at the US base at Ali Al Salem in Kuwait, the Salvadoran
helicopter strike on the gang boss's house in Canaan, the GTA VI
midnight rollout, the Bank of England rate warning, 4 dead in
Odesa (not 5), about 500 factories shut in Bangladesh (not 535),
and Cyclone Akvan gusts to 145 km/h (not 110). Every figure was
checked against reporting of the day. The illustrations are
detailed flat-vector scenes with gradients, shading and fine
detail; the map is a dotted world map with numbered pins.

The program is deterministic: no clock, no randomness, no network.
It writes entry.png to $MAKEFUN_OUTPUT_DIR when that is set, and
beside this script otherwise.
"""

import math
import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# Palette: name -> (red, green, blue).
PAL = {
    "cream": (253, 246, 227),
    "paper": (244, 234, 205),
    "ink": (18, 18, 18),
    "grey": (110, 108, 100),
    "dark": (70, 70, 68),
    "steel": (150, 158, 165),
    "sky": (178, 216, 240),
    "pale": (214, 232, 244),
    "sea": (38, 110, 180),
    "deep": (24, 80, 150),
    "night": (38, 52, 96),
    "night2": (70, 80, 140),
    "land": (196, 178, 130),
    "land2": (168, 158, 110),
    "green": (90, 140, 80),
    "leaf": (60, 160, 90),
    "red": (200, 40, 32),
    "orange": (240, 120, 20),
    "flame": (255, 176, 32),
    "gold": (255, 214, 90),
    "blue": (40, 80, 180),
    "white": (255, 255, 255),
    "moon": (240, 230, 200),
    "moonspot": (210, 200, 170),
    "hull": (120, 24, 20),
    "deck": (210, 210, 205),
    "deck2": (225, 225, 220),
    "tower": (40, 36, 52),
    "ground": (60, 50, 44),
    "table": (150, 110, 60),
    "box": (200, 170, 110),
    "skin": (250, 220, 190),
    "sun": (255, 220, 140),
    "window": (255, 220, 120),
    "dusk": (232, 150, 90),
    "dusk2": (120, 80, 130),
    "tan": (222, 196, 140),
    "pink": (232, 140, 160),
    "teal": (40, 140, 140),
    "cyan": (80, 190, 210),
    "purple": (120, 80, 160),
    "rust": (170, 80, 40),
    "olive": (120, 120, 70),
    "sand": (232, 214, 170),
}

# 5x7 bitmap font. Each glyph is seven rows; each row is a 5-bit
# number, bit 4 (value 16) the leftmost pixel, bit 0 the rightmost.
GLYPHS = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04),
    ",": (0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x08),
    "'": (0x00, 0x04, 0x04, 0x00, 0x00, 0x00, 0x00),
    ":": (0x00, 0x04, 0x00, 0x00, 0x00, 0x04, 0x00),
    ";": (0x00, 0x04, 0x00, 0x00, 0x00, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x06, 0x04, 0x00, 0x04),
    "-": (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "%": (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    "=": (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "#": (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    "*": (0x00, 0x04, 0x15, 0x0E, 0x15, 0x04, 0x00),
    "@": (0x0E, 0x11, 0x16, 0x1A, 0x10, 0x10, 0x0E),
    '"': (0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00),
}
BLANK_GLYPH = (0, 0, 0, 0, 0, 0, 0)


def lerp_color(c1, c2, t):
    return (int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t))


class Canvas:
    """A plain RGB pixel buffer with small drawing helpers."""

    def __init__(self, width, height):
        self.w = width
        self.h = height
        self.buf = bytearray(width * height * 3)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = color

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = yy * self.w * 3
            for xx in range(x0, x1):
                i = base + xx * 3
                self.buf[i], self.buf[i + 1], self.buf[i + 2] = color

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def frame(self, x, y, w, h, color, thick=1):
        for t in range(thick):
            self.vline(x + t, y, h, color)
            self.vline(x + w - 1 - t, y, h, color)
            self.hline(x, y + t, w, color)
            self.hline(x, y + h - 1 - t, w, color)

    def disc(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            for xx in range(cx - dx, cx + dx + 1):
                self.set(xx, cy + dy, color)

    def ring(self, cx, cy, r, color):
        for a in range(0, 360, 4):
            rad = math.radians(a)
            self.set(cx + int(r * math.cos(rad)),
                     cy + int(r * math.sin(rad)), color)

    def segment(self, x0, y0, x1, y1, color, thick=1):
        """Bresenham line, thick pixels wide."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for t in range(thick):
                self.set(x0 + t, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def polygon(self, points, color):
        """Scanline fill of a simple polygon."""
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
                    self.set(xx, y, color)

    def vgrad(self, x, y, w, h, c_top, c_bot):
        """Vertical gradient fill, top colour to bottom colour."""
        for yy in range(h):
            t = yy / max(1, h - 1)
            self.rect(x, y + yy, w, 1, lerp_color(c_top, c_bot, t))

    def person(self, x, y, h, shirt, skin):
        """Tiny standing figure: head disc, body, legs."""
        hr = max(2, h // 6)
        self.disc(x, y + hr, hr, skin)
        self.rect(x - hr, y + 2 * hr, 2 * hr, h // 2, shirt)
        self.vline(x - hr + 1, y + 2 * hr + h // 2, h // 4,
                   PAL["ink"], 1)
        self.vline(x + hr - 2, y + 2 * hr + h // 2, h // 4,
                   PAL["ink"], 1)

    def text_width(self, text, scale):
        return len(text) * 6 * scale - scale

    def text(self, x, y, text, scale, color):
        for ci, ch in enumerate(text):
            glyph = GLYPHS.get(ch, BLANK_GLYPH)
            ox = x + ci * 6 * scale
            for r in range(7):
                row = glyph[r]
                for c in range(5):
                    if (row >> (4 - c)) & 1:
                        self.rect(ox + c * scale, y + r * scale,
                                  scale, scale, color)

    def centered(self, cx, y, text, scale, color):
        self.text(cx - self.text_width(text, scale) // 2, y, text,
                  scale, color)

    def wrap(self, text, scale, max_w):
        max_chars = max(1, max_w // (6 * scale))
        lines = []
        cur = ""
        for word in text.split(" "):
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

    def wrapped(self, cx, y, text, scale, color, max_w, leading=3,
                max_lines=None):
        """Draw word-wrapped centered text; return the height used."""
        lines = self.wrap(text, scale, max_w)
        if max_lines is not None:
            lines = lines[:max_lines]
        step = 7 * scale + leading
        for i, ln in enumerate(lines):
            self.centered(cx, y + i * step, ln, scale, color)
        return len(lines) * step


def png_chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(canvas, path):
    raw = bytearray()
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.buf[y * canvas.w * 3:(y + 1) * canvas.w * 3]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += png_chunk(b"IHDR", ihdr)
    png += png_chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += png_chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ---- Lead scenes: one detailed flat-vector illustration per card ----
# Each scene draws into the box (px, py, pw, ph) using fractions of
# its width and height, so it works in both card widths.


def scene_gulf(cv, px, py, pw, ph):
    """Night over the Gulf: drones, flares, an air base on the shore."""
    cv.vgrad(px, py, pw, ph, PAL["night"], PAL["night2"])
    sea_y = py + int(ph * 0.62)
    cv.vgrad(px, sea_y, pw, ph - int(ph * 0.62), PAL["deep"],
             PAL["sea"])
    for sx, sy in ((6, 5), (18, 12), (30, 4), (44, 10), (58, 6),
                   (70, 12), (92, 4), (96, 16)):
        cv.set(px + int(sx * pw / 100), py + int(sy * ph / 100),
               PAL["gold"])
    # moon with a pale glow ring and its reflection on the water
    mx, my = px + int(pw * 0.86), py + int(ph * 0.22)
    cv.ring(mx, my, max(4, ph // 5) + 2, PAL["moonspot"])
    cv.disc(mx, my, max(3, ph // 6), PAL["moon"])
    cv.disc(mx - 2, my - 1, 1, PAL["moonspot"])
    for i, w in enumerate((14, 10, 16)):
        cv.hline(mx - w // 2, sea_y + 4 + i * 3, w, PAL["gold"])
    # three drones diving in, bright heads and dotted trails
    for dx0, dx1, dy in ((0.10, 0.30, -4), (0.42, 0.62, -6),
                         (0.70, 0.84, -3)):
        cv.segment(px + int(pw * dx0), py + 2,
                   px + int(pw * dx1), sea_y + dy, PAL["white"], 1)
        cv.disc(px + int(pw * dx1), sea_y + dy, 3, PAL["flame"])
        cv.disc(px + int(pw * dx1), sea_y + dy, 1, PAL["white"])
    # interceptor bursts over the base
    for bx, by in ((0.48, -8), (0.66, -12)):
        cv.disc(px + int(pw * bx), sea_y + by, 4, PAL["orange"])
        cv.disc(px + int(pw * bx), sea_y + by, 2, PAL["flame"])
        cv.segment(px + int(pw * bx) - 6, sea_y + by,
                   px + int(pw * bx) + 6, sea_y + by, PAL["gold"], 1)
    # the air base on the shore: runway, hangar, tower, searchlight
    cv.rect(px, sea_y + 1, pw, 2, PAL["land"])
    cv.rect(px + int(pw * 0.05), sea_y + 3, int(pw * 0.9), 1,
            PAL["gold"])
    for i in range(6):
        cv.set(px + int(pw * (0.08 + i * 0.15)), sea_y + 3,
               PAL["white"])
    cv.rect(px + int(pw * 0.08), sea_y + 6, int(pw * 0.22),
            ph - int(ph * 0.62) - 8, PAL["deck"])
    cv.rect(px + int(pw * 0.12), sea_y + 8, int(pw * 0.06),
            ph - int(ph * 0.62) - 10, PAL["ink"])
    cv.rect(px + int(pw * 0.62), sea_y + 4, int(pw * 0.28),
            ph - int(ph * 0.62) - 6, PAL["steel"])
    for i in range(3):
        cv.rect(px + int(pw * (0.65 + i * 0.08)), sea_y + 7, 3, 3,
                PAL["window"])
    tx = px + int(pw * 0.42)
    cv.rect(tx, sea_y - 2, 4, ph - int(ph * 0.62), PAL["tower"])
    cv.rect(tx - 2, sea_y - 6, 8, 4, PAL["tower"])
    cv.rect(tx - 1, sea_y - 5, 6, 2, PAL["window"])
    cv.segment(tx + 2, sea_y - 6, tx + 22, py + 2, PAL["pale"], 1)
    # a small patrol boat on the water
    bx = px + int(pw * 0.20)
    cv.polygon([(bx, sea_y + 6), (bx + 16, sea_y + 6),
                (bx + 13, sea_y + 10), (bx + 3, sea_y + 10)],
               PAL["hull"])
    cv.vline(bx + 8, sea_y + 1, 5, PAL["ink"], 1)


def scene_summit(cv, px, py, pw, ph):
    """Three flags over the Shenzhen skyline at dusk."""
    cv.vgrad(px, py, pw, ph, PAL["dusk"], PAL["dusk2"])
    cv.disc(px + int(pw * 0.88), py + int(ph * 0.2),
            max(3, ph // 7), PAL["sun"])
    cv.ring(px + int(pw * 0.88), py + int(ph * 0.2),
            max(3, ph // 7) + 2, PAL["gold"])
    # skyline towers with lit windows in two rows
    for i in range(7):
        tx = px + int(pw * (0.02 + i * 0.14))
        tw = int(pw * 0.11)
        th = int(ph * (0.30 + (i % 3) * 0.13))
        base_y = py + ph - th - int(ph * 0.18)
        cv.rect(tx, base_y, tw, th, PAL["tower"])
        cv.rect(tx + 2, base_y + 3, 3, 3, PAL["window"])
        cv.rect(tx + tw - 5, base_y + th // 2, 3, 3, PAL["window"])
        if i % 2 == 0:
            cv.rect(tx + 2, base_y + th - 6, 3, 3, PAL["gold"])
    # the tallest tower, with a spire and a red beacon
    tx = px + int(pw * 0.46)
    cv.rect(tx, py + int(ph * 0.10), int(pw * 0.10),
            int(ph * 0.72), PAL["ink"])
    cv.vline(tx + int(pw * 0.05), py + 2, int(ph * 0.10),
             PAL["ink"], 1)
    cv.disc(tx + int(pw * 0.05), py + 2, 2, PAL["red"])
    ground_y = py + ph - int(ph * 0.18)
    cv.rect(px, ground_y, pw, int(ph * 0.18), PAL["ground"])
    cv.rect(px, ground_y, pw, 2, PAL["gold"])
    # a road with two cars on the pavement
    cv.rect(px, ground_y + int(ph * 0.07), pw, 3, PAL["ink"])
    for cx in (0.15, 0.68):
        bx = px + int(pw * cx)
        cv.rect(bx, ground_y + int(ph * 0.03), 12, 4, PAL["red"])
        cv.rect(bx + 2, ground_y + int(ph * 0.01), 8, 3, PAL["sky"])
    # three flags: China red with stars, US stripes, Russia tricolour
    flag_cols = [(PAL["red"], PAL["red"], PAL["red"]),
                 (PAL["red"], PAL["white"], PAL["blue"]),
                 (PAL["white"], PAL["blue"], PAL["red"])]
    for j, cols in enumerate(flag_cols):
        fx = px + int(pw * (0.10 + j * 0.30))
        cv.vline(fx, py + 2, int(ph * 0.42), PAL["ink"], 2)
        for i, col in enumerate(cols):
            cv.rect(fx + 2, py + 2 + i * 4, int(pw * 0.12), 4, col)
        if j == 0:
            for sx, sy in ((4, 4), (9, 5), (9, 9), (5, 10)):
                cv.set(fx + sx, py + sy, PAL["gold"])
        if j == 1:
            cv.rect(fx + 2, py + 2, 5, 5, PAL["blue"])
    # delegates stand on the pavement, inside the scene box
    for j, shirt in enumerate((PAL["blue"], PAL["red"],
                               PAL["teal"])):
        cv.person(px + int(pw * (0.38 + j * 0.07)),
                  ground_y - 10, 8, shirt, PAL["skin"])


def scene_cop(cv, px, py, pw, ph):
    """A globe, a smoking stack, a leaf and a turbine: the split."""
    cv.vgrad(px, py, pw, ph, PAL["sky"], PAL["pale"])
    cv.disc(px + int(pw * 0.90), py + int(ph * 0.18),
            max(3, ph // 7), PAL["sun"])
    # the globe, with continents, cloud streaks and a ring
    cx, cy = px + int(pw * 0.26), py + ph // 2
    r = int(ph * 0.36)
    cv.disc(cx, cy, r, PAL["sea"])
    cv.disc(cx - r // 3, cy - r // 4, r // 3, PAL["green"])
    cv.disc(cx + r // 3, cy + r // 4, r // 4, PAL["green"])
    cv.disc(cx + r // 5, cy - r // 2, r // 5, PAL["leaf"])
    cv.hline(cx - r + 2, cy - r // 3, r, PAL["white"])
    cv.hline(cx - r // 2, cy + r // 2, r, PAL["white"])
    cv.ring(cx, cy, r, PAL["ink"])
    cv.segment(cx - r, cy, cx + r, cy, PAL["steel"], 1)
    # factory with three stacks, smoke and lit windows
    bx = px + int(pw * 0.52)
    cv.rect(bx, py + int(ph * 0.45), int(pw * 0.44), int(ph * 0.55),
            PAL["dark"])
    cv.rect(bx, py + int(ph * 0.45), int(pw * 0.44), 2, PAL["steel"])
    for i in range(3):
        cv.rect(bx + int(pw * (0.05 + i * 0.13)),
                py + int(ph * 0.55), int(pw * 0.05),
                int(ph * 0.16), PAL["gold"])
    for j, (sx, sw, sh) in enumerate(((0.05, 0.07, 0.25),
                                      (0.20, 0.07, 0.15),
                                      (0.33, 0.06, 0.30))):
        cv.rect(bx + int(pw * sx), py + int(ph * (0.45 - sh)),
                int(pw * sw), int(ph * sh), PAL["steel"])
    for dx, dy, dr in ((0.08, 0.16, 4), (0.13, 0.10, 3),
                       (0.24, 0.20, 3), (0.36, 0.12, 4)):
        cv.disc(bx + int(pw * dx), py + int(ph * dy), dr, PAL["grey"])
    # a green leaf and a wind turbine rising above the smoke
    lx, ly = px + int(pw * 0.84), py + int(ph * 0.20)
    cv.polygon([(lx, ly - 7), (lx + 8, ly), (lx, ly + 7),
                (lx - 8, ly)], PAL["leaf"])
    cv.segment(lx, ly - 7, lx, ly + 9, PAL["green"], 1)
    tx = px + int(pw * 0.68)
    cv.vline(tx, py + int(ph * 0.30), int(ph * 0.55), PAL["white"],
             2)
    for a in (90, 210, 330):
        rad = math.radians(a)
        cv.segment(tx, py + int(ph * 0.30),
                   tx + int(9 * math.cos(rad)),
                   py + int(ph * 0.30) + int(9 * math.sin(rad)),
                   PAL["white"], 1)
    cv.disc(tx, py + int(ph * 0.30), 2, PAL["ink"])


def scene_gaza(cv, px, py, pw, ph):
    """A white flag on a broken wall, dusk over Gaza."""
    cv.vgrad(px, py, pw, ph, PAL["dusk"], PAL["dusk2"])
    cv.disc(px + int(pw * 0.85), py + int(ph * 0.25),
            max(3, ph // 7), PAL["sun"])
    cv.ring(px + int(pw * 0.85), py + int(ph * 0.25),
            max(3, ph // 7) + 2, PAL["gold"])
    # two tents and a minaret behind the wall
    tx = px + int(pw * 0.08)
    cv.polygon([(tx, py + int(ph * 0.55)), (tx + 9, py + int(ph * 0.38)),
                (tx + 18, py + int(ph * 0.55))], PAL["sand"])
    cv.rect(px + int(pw * 0.90), py + int(ph * 0.20), 4,
            int(ph * 0.35), PAL["tower"])
    cv.disc(px + int(pw * 0.90) + 2, py + int(ph * 0.20), 3,
            PAL["gold"])
    # broken wall: staggered blocks at two heights, with cracks
    wy = py + int(ph * 0.55)
    for i in range(7):
        bw = int(pw * 0.13)
        bx = px + i * bw
        bh = int(ph * (0.30 + (0.15 if i % 2 else 0.0)))
        cv.rect(bx, wy + int(ph * 0.45) - bh, bw - 2, bh, PAL["tan"])
        cv.rect(bx, wy + int(ph * 0.45) - bh, bw - 2, 2, PAL["sand"])
        if i % 2:
            cv.segment(bx + bw // 2, wy + int(ph * 0.45) - bh + 2,
                       bx + bw // 2 + 2, wy + int(ph * 0.45) - bh + 8,
                       PAL["dark"], 1)
    cv.rect(px, wy + int(ph * 0.45), pw, 3, PAL["ink"])
    # rubble at the foot of the wall
    for rx, rr in ((0.15, 3), (0.30, 2), (0.72, 3), (0.86, 2)):
        cv.disc(px + int(pw * rx), wy + int(ph * 0.45) + 4, rr,
                PAL["grey"])
    # white flag on a pole above the wall, with its shadow
    fx = px + int(pw * 0.5)
    cv.vline(fx, py + int(ph * 0.12), int(ph * 0.45), PAL["ink"], 2)
    cv.rect(fx + 2, py + int(ph * 0.12), int(pw * 0.16),
            int(ph * 0.2), PAL["white"])
    cv.rect(fx + 2, py + int(ph * 0.12) + int(ph * 0.2) - 2,
            int(pw * 0.16), 2, PAL["steel"])
    cv.segment(fx, py + int(ph * 0.57), fx + 10, py + int(ph * 0.60),
               PAL["grey"], 1)
    # a dove and an olive branch above the flag
    dx, dy = px + int(pw * 0.2), py + int(ph * 0.2)
    cv.disc(dx, dy, 3, PAL["white"])
    cv.segment(dx - 8, dy - 2, dx - 2, dy, PAL["white"], 2)
    cv.segment(dx + 2, dy, dx + 8, dy - 3, PAL["white"], 2)
    bx, by = px + int(pw * 0.68), py + int(ph * 0.16)
    cv.segment(bx, by, bx + 12, by + 4, PAL["leaf"], 1)
    for ox, oy in ((3, 1), (7, 2), (10, 4)):
        cv.disc(bx + ox, by + oy, 2, PAL["leaf"])


def scene_bangladesh(cv, px, py, pw, ph):
    """Garment workers, a factory and a wage banner."""
    cv.rect(px, py, pw, ph, PAL["paper"])
    cv.disc(px + int(pw * 0.90), py + int(ph * 0.14),
            max(3, ph // 7), PAL["sun"])
    cv.disc(px + int(pw * 0.06), py + int(ph * 0.10), 5, PAL["white"])
    cv.disc(px + int(pw * 0.11), py + int(ph * 0.08), 4, PAL["white"])
    # factory block with chimneys, smoke and lit windows
    cv.rect(px + int(pw * 0.55), py + int(ph * 0.35), int(pw * 0.42),
            int(ph * 0.65), PAL["red"])
    cv.rect(px + int(pw * 0.55), py + int(ph * 0.35), int(pw * 0.42),
            2, PAL["rust"])
    cv.rect(px + int(pw * 0.6), py + int(ph * 0.1), int(pw * 0.06),
            int(ph * 0.25), PAL["steel"])
    cv.rect(px + int(pw * 0.75), py + int(ph * 0.18), int(pw * 0.06),
            int(ph * 0.17), PAL["steel"])
    cv.disc(px + int(pw * 0.63), py + int(ph * 0.05), 3, PAL["grey"])
    cv.disc(px + int(pw * 0.78), py + int(ph * 0.12), 3, PAL["grey"])
    for r in range(2):
        for i in range(3):
            cv.rect(px + int(pw * (0.60 + i * 0.12)),
                    py + int(ph * (0.52 + r * 0.18)), int(pw * 0.06),
                    int(ph * 0.12), PAL["gold"])
    # the wage banner, held high by the march
    by = py + int(ph * 0.40)
    cv.rect(px + int(pw * 0.04), by, int(pw * 0.44), int(ph * 0.24),
            PAL["white"])
    cv.frame(px + int(pw * 0.04), by, int(pw * 0.44), int(ph * 0.24),
             PAL["ink"], 1)
    cv.text(px + int(pw * 0.07), by + 2, "TK30,000", 1, PAL["red"])
    # four workers with raised arms, and a crowd behind them
    for i in range(4):
        fx = px + int(pw * (0.08 + i * 0.11))
        cv.disc(fx, by + int(ph * 0.38), 3, PAL["skin"])
        cv.rect(fx - 3, by + int(ph * 0.42), 6, int(ph * 0.22),
                (PAL["blue"], PAL["teal"], PAL["red"],
                 PAL["gold"])[i])
        cv.segment(fx + 2, by + int(ph * 0.42), fx + 4,
                   by + int(ph * 0.30), PAL["skin"], 1)
    for i in range(3):
        hx = px + int(pw * (0.05 + i * 0.16))
        cv.disc(hx, by + int(ph * 0.30), 2, PAL["skin"])
    cv.rect(px, py + ph - 3, pw, 3, PAL["ground"])


def scene_voyager(cv, px, py, pw, ph):
    """Voyager 1 in deep space, one light-day out."""
    cv.rect(px, py, pw, ph, PAL["ink"])
    # a faint purple nebula behind the stars
    cv.disc(px + int(pw * 0.20), py + int(ph * 0.25), 10,
            PAL["night2"])
    cv.disc(px + int(pw * 0.78), py + int(ph * 0.70), 8,
            PAL["purple"])
    for sx, sy, big in ((6, 8, 0), (18, 20, 1), (32, 6, 0),
                        (48, 16, 0), (64, 8, 1), (80, 22, 0),
                        (92, 10, 0), (12, 70, 0), (40, 80, 1),
                        (70, 72, 0), (26, 40, 0), (56, 55, 0),
                        (88, 45, 1), (36, 88, 0)):
        x = px + int(sx * pw / 100)
        y = py + int(sy * ph / 100)
        if big:
            cv.rect(x, y, 2, 2, PAL["white"])
        else:
            cv.set(x, y, PAL["white"])
    # the probe: gold body with foil lines, big dish, long boom
    cx, cy = px + int(pw * 0.5), py + ph // 2
    cv.rect(cx - 12, cy - 5, 24, 10, PAL["gold"])
    cv.hline(cx - 12, cy - 2, 24, PAL["orange"])
    cv.hline(cx - 12, cy + 2, 24, PAL["orange"])
    cv.polygon([(cx - 12, cy - 8), (cx - 12, cy + 8),
                (cx - 30, cy + 2), (cx - 30, cy - 2)], PAL["deck"])
    cv.segment(cx - 12, cy, cx - 30, cy - 10, PAL["steel"], 2)
    cv.disc(cx - 30, cy - 10, 3, PAL["white"])
    cv.segment(cx + 12, cy, cx + 34, cy + 8, PAL["white"], 1)
    cv.disc(cx + 34, cy + 8, 2, PAL["flame"])
    for i in range(3):
        cv.segment(cx + 12 + i * 4, cy - 5, cx + 14 + i * 4, cy + 5,
                   PAL["rust"], 1)
    # signal rings travelling home toward a small Earth
    for r in (4, 7, 10):
        cv.ring(cx - 30, cy - 10, r, PAL["sky"])
    ex, ey = px + int(pw * 0.06), py + int(ph * 0.82)
    cv.ring(ex, ey, 6, PAL["cyan"])
    cv.disc(ex, ey, 4, PAL["sea"])
    cv.disc(ex - 1, ey - 1, 2, PAL["green"])
    cv.hline(ex - 3, ey - 2, 6, PAL["white"])


def scene_haiti(cv, px, py, pw, ph):
    """Helicopters over a hillside mansion in Canaan, Haiti."""
    cv.vgrad(px, py, pw, ph, PAL["sky"], PAL["pale"])
    cv.disc(px + int(pw * 0.90), py + int(ph * 0.16),
            max(3, ph // 7), PAL["sun"])
    # two layered hills and a road at the foot
    hy = py + int(ph * 0.62)
    cv.polygon([(px, py + ph), (px, hy - 2),
                (px + int(pw * 0.4), hy - 12),
                (px + int(pw * 0.7), hy - 4),
                (px + pw, hy + 2), (px + pw, py + ph)],
               PAL["olive"])
    cv.polygon([(px, py + ph), (px, hy + 8),
                (px + int(pw * 0.5), hy - 6),
                (px + pw, hy + 4), (px + pw, py + ph)], PAL["green"])
    cv.rect(px, py + ph - 4, pw, 4, PAL["ground"])
    # the mansion on the hill, with a pool and a palm
    hx = px + int(pw * 0.55)
    cv.rect(hx, hy - 12, int(pw * 0.3), 12, PAL["white"])
    cv.polygon([(hx - 2, hy - 12), (hx + int(pw * 0.15), hy - 18),
                (hx + int(pw * 0.3) + 2, hy - 12)], PAL["red"])
    cv.rect(hx + int(pw * 0.08), hy - 7, 5, 7, PAL["blue"])
    cv.rect(hx + int(pw * 0.2), hy - 7, 5, 7, PAL["blue"])
    cv.rect(hx + int(pw * 0.13), hy - 7, 5, 7, PAL["ink"])
    cv.rect(hx + int(pw * 0.02), hy - 2, int(pw * 0.10), 3,
            PAL["cyan"])
    cv.rect(hx + int(pw * 0.02), hy - 2, int(pw * 0.10), 1,
            PAL["white"])
    px0 = px + int(pw * 0.46)
    cv.segment(px0, hy - 2, px0 + 2, hy - 12, PAL["rust"], 1)
    for a in (200, 240, 280, 320):
        rad = math.radians(a)
        cv.segment(px0 + 2, hy - 12,
                   px0 + 2 + int(7 * math.cos(rad)),
                   hy - 12 + int(5 * math.sin(rad)), PAL["leaf"], 1)
    # smoke drifting right from the mansion roof, inside the box
    for sx, sy, sr in ((0.70, -14, 4), (0.75, -18, 4),
                       (0.80, -22, 3), (0.85, -16, 3)):
        cv.disc(px + int(pw * sx), hy + sy, sr, PAL["grey"])
    cv.disc(px + int(pw * 0.82), hy - 24, 2, PAL["white"])
    # two helicopters above, rotors spinning, one searchlight on
    for hx2, hy2, s in ((0.20, 0.24, 1.0), (0.38, 0.30, 0.7)):
        cx = px + int(pw * hx2)
        cy = py + int(ph * hy2)
        k = s
        cv.rect(cx - int(12 * k), cy - 4, int(24 * k), 8, PAL["dark"])
        cv.rect(cx - int(12 * k), cy - 4, int(24 * k), 2, PAL["deck"])
        cv.segment(cx - int(18 * k), cy - 7, cx + int(18 * k), cy - 7,
                   PAL["ink"], 2)
        cv.segment(cx + int(12 * k), cy, cx + int(20 * k), cy + 6,
                   PAL["ink"], 2)
        cv.disc(cx - int(8 * k), cy - 1, 2, PAL["sky"])
        if s > 0.9:
            cv.polygon([(cx - 4, cy + 4), (cx + 4, cy + 4),
                        (cx + 14, hy - 2), (cx + 2, hy - 2)],
                       PAL["pale"])

def scene_odesa(cv, px, py, pw, ph):
    """Odesa at night: skyline, a blast, and interceptors."""
    cv.vgrad(px, py, pw, ph, PAL["night"], PAL["night2"])
    for sx, sy in ((8, 6), (20, 12), (36, 5), (52, 10), (68, 6),
                   (84, 12), (94, 5)):
        cv.set(px + int(sx * pw / 100), py + int(sy * ph / 100),
               PAL["gold"])
    mx, my = px + int(pw * 0.90), py + int(ph * 0.18)
    cv.disc(mx, my, 3, PAL["moon"])
    # skyline with lit windows and a church dome
    gy = py + int(ph * 0.72)
    for i in range(6):
        bx = px + int(pw * (0.02 + i * 0.16))
        bw = int(pw * 0.13)
        bh = int(ph * (0.24 + (i % 3) * 0.09))
        cv.rect(bx, gy - bh, bw, bh, PAL["tower"])
        cv.rect(bx + 3, gy - bh + 4, 3, 3, PAL["window"])
        cv.rect(bx + bw - 6, gy - bh + 9, 3, 3, PAL["window"])
        if i % 2 == 0:
            cv.rect(bx + 3, gy - 5, 3, 3, PAL["gold"])
    dx = px + int(pw * 0.50)
    cv.disc(dx, gy - int(ph * 0.34), 5, PAL["gold"])
    cv.vline(dx, gy - int(ph * 0.34) - 7, 5, PAL["gold"], 1)
    cv.hline(dx - 2, gy - int(ph * 0.34) - 5, 5, PAL["gold"])
    # the sea at the foot of the city, with reflections
    cv.rect(px, gy, pw, ph - int(ph * 0.72), PAL["deep"])
    cv.hline(px + int(pw * 0.10), gy + 3, 18, PAL["gold"])
    cv.hline(px + int(pw * 0.60), gy + 6, 22, PAL["gold"])
    # blast over the city, layered fire and smoke
    bx, by = px + int(pw * 0.68), py + int(ph * 0.30)
    cv.disc(bx, by, 8, PAL["orange"])
    cv.disc(bx, by, 5, PAL["flame"])
    cv.disc(bx, by, 2, PAL["white"])
    for ox, oy, r in ((-12, 8, 4), (12, -6, 3), (-8, -8, 3),
                      (14, 6, 4)):
        cv.disc(bx + ox, by + oy, r, PAL["grey"])
    for ox, oy in ((-16, 12), (18, -10), (0, 14)):
        cv.set(bx + ox, by + oy, PAL["flame"])
    # interceptor streaks crossing the sky
    for x0, y0, x1, y1 in ((0.05, 0.15, 0.30, 0.40),
                           (0.35, 0.08, 0.55, 0.35),
                           (0.10, 0.45, 0.32, 0.22)):
        cv.segment(px + int(pw * x0), py + int(ph * y0),
                   px + int(pw * x1), py + int(ph * y1),
                   PAL["white"], 1)
        cv.disc(px + int(pw * x1), py + int(ph * y1), 2, PAL["flame"])


def scene_badme(cv, px, py, pw, ph):
    """Two armies face off across a dry border valley."""
    cv.vgrad(px, py, pw, ph, PAL["sand"], PAL["tan"])
    cv.disc(px + int(pw * 0.85), py + int(ph * 0.2),
            max(3, ph // 7), PAL["sun"])
    cv.disc(px + int(pw * 0.12), py + int(ph * 0.12), 4, PAL["white"])
    cv.disc(px + int(pw * 0.18), py + int(ph * 0.09), 3, PAL["white"])
    # two mountain ranges, the far one with snow caps
    cv.polygon([(px, py + int(ph * 0.42)), (px + int(pw * 0.20),
                py + int(ph * 0.14)), (px + int(pw * 0.40),
                py + int(ph * 0.42))], PAL["steel"])
    cv.polygon([(px + int(pw * 0.14), py + int(ph * 0.22)),
                (px + int(pw * 0.20), py + int(ph * 0.14)),
                (px + int(pw * 0.26), py + int(ph * 0.22))],
               PAL["white"])
    cv.polygon([(px + int(pw * 0.60), py + int(ph * 0.42)),
                (px + int(pw * 0.78), py + int(ph * 0.18)),
                (px + pw, py + int(ph * 0.42))], PAL["dark"])
    cv.polygon([(px + int(pw * 0.72), py + int(ph * 0.26)),
                (px + int(pw * 0.78), py + int(ph * 0.18)),
                (px + int(pw * 0.84), py + int(ph * 0.26))],
               PAL["white"])
    # the valley floor, a dry river and an acacia tree
    vy = py + int(ph * 0.55)
    cv.rect(px, vy, pw, ph - int(ph * 0.55), PAL["land2"])
    cv.polygon([(px, vy + 8), (px + int(pw * 0.5), vy + 4),
                (px + pw, vy + 8), (px + pw, vy + 12),
                (px + int(pw * 0.5), vy + 8), (px, vy + 12)],
               PAL["sand"])
    ax = px + int(pw * 0.12)
    cv.segment(ax, vy + 4, ax + 2, vy - 8, PAL["rust"], 2)
    cv.polygon([(ax - 10, vy - 8), (ax + 12, vy - 8),
                (ax + 2, vy - 13)], PAL["olive"])
    # the border line down the middle, with posts
    cv.vline(px + pw // 2, vy, int(ph * 0.45), PAL["red"], 2)
    for i in range(4):
        cv.set(px + pw // 2, vy + i * 6, PAL["white"])
    for j, col in enumerate((PAL["green"], PAL["red"])):
        fx = px + int(pw * (0.30 + j * 0.32))
        cv.vline(fx, vy - 2, int(ph * 0.28), PAL["ink"], 2)
        for i, c in enumerate((col, PAL["gold"], PAL["red"])
                              if j == 0 else
                              (PAL["green"], PAL["red"],
                               PAL["blue"])):
            cv.rect(fx + 2, vy - 2 + i * 4, int(pw * 0.09), 4, c)
    # tents and soldiers at the foot of the valley
    for i in range(4):
        tx = px + int(pw * (0.06 + i * 0.12))
        cv.polygon([(tx, py + ph - 3), (tx + 8, py + int(ph * 0.78)),
                    (tx + 16, py + ph - 3)], PAL["white"])
        cv.rect(tx + 6, py + ph - 6, 4, 3, PAL["ink"])
    for j, shirt in enumerate((PAL["green"], PAL["blue"])):
        cv.person(px + int(pw * (0.62 + j * 0.10)), vy + 6, 12,
                  shirt, PAL["skin"])


def scene_gta(cv, px, py, pw, ph):
    """Neon city night: the GTA VI launch."""
    cv.vgrad(px, py, pw, ph, PAL["night"], PAL["purple"])
    for sx, sy in ((5, 6), (25, 10), (45, 5), (65, 9), (85, 6),
                   (95, 12)):
        cv.set(px + int(sx * pw / 100), py + int(sy * ph / 100),
               PAL["white"])
    # neon skyline with coloured windows and an antenna
    for i in range(7):
        bx = px + int(pw * (0.02 + i * 0.14))
        bw = int(pw * 0.11)
        bh = int(ph * (0.34 + (i % 3) * 0.12))
        cv.rect(bx, py + ph - bh - int(ph * 0.14), bw, bh,
                PAL["tower"])
        win = PAL["pink"] if i % 3 == 0 else (
            PAL["gold"] if i % 3 == 1 else PAL["cyan"])
        cv.rect(bx + 2, py + ph - bh - int(ph * 0.14) + 4, 3, 4, win)
        cv.rect(bx + bw - 5, py + ph - bh - int(ph * 0.14) + 10, 3,
                4, win)
        if i == 3:
            cv.vline(bx + bw // 2, py + ph - bh - int(ph * 0.14) - 6,
                     6, PAL["ink"], 1)
            cv.disc(bx + bw // 2, py + ph - bh - int(ph * 0.14) - 7,
                    2, PAL["red"])
    # the road, a car, and two palm trees
    cv.rect(px, py + ph - int(ph * 0.14), pw, int(ph * 0.14),
            PAL["ground"])
    for i in range(5):
        cv.rect(px + int(pw * (0.05 + i * 0.19)),
                py + ph - int(ph * 0.07), 8, 2, PAL["gold"])
    cx = px + int(pw * 0.70)
    cv.rect(cx, py + ph - 10, 22, 5, PAL["red"])
    cv.rect(cx + 4, py + ph - 14, 13, 4, PAL["red"])
    cv.rect(cx + 6, py + ph - 13, 9, 3, PAL["sky"])
    cv.disc(cx + 4, py + ph - 5, 2, PAL["ink"])
    cv.disc(cx + 18, py + ph - 5, 2, PAL["ink"])
    cv.disc(cx + 23, py + ph - 8, 1, PAL["gold"])
    for tx in (0.06, 0.92):
        bx = px + int(pw * tx)
        cv.segment(bx, py + ph - int(ph * 0.14), bx + 1,
                   py + ph - int(ph * 0.32), PAL["rust"], 2)
        for a in (200, 250, 290, 340):
            rad = math.radians(a)
            cv.segment(bx + 1, py + ph - int(ph * 0.32),
                       bx + 1 + int(8 * math.cos(rad)),
                       py + ph - int(ph * 0.32) +
                       int(5 * math.sin(rad)), PAL["leaf"], 1)
    # big neon VI in the sky, glowing over a dark sign
    vx = px + int(pw * 0.36)
    vy = py + int(ph * 0.10)
    cv.rect(vx - 6, vy - 4, 48, 22, PAL["ink"])
    for col, th in ((PAL["pink"], 3), (PAL["white"], 1)):
        cv.segment(vx, vy, vx + 8, vy + 14, col, th)
        cv.segment(vx + 8, vy + 14, vx + 16, vy, col, th)
        cv.segment(vx + 24, vy, vx + 24, vy + 14, col, th)
    # a game controller below the sign
    gx, gy = px + int(pw * 0.5), py + int(ph * 0.62)
    cv.rect(gx - 16, gy - 4, 32, 10, PAL["white"])
    cv.rect(gx - 16, gy - 4, 32, 3, PAL["deck2"])
    cv.disc(gx - 8, gy + 2, 3, PAL["red"])
    cv.disc(gx + 8, gy + 2, 3, PAL["blue"])
    cv.disc(gx - 2, gy - 1, 1, PAL["gold"])
    cv.disc(gx + 2, gy - 1, 1, PAL["gold"])


def scene_bank(cv, px, py, pw, ph):
    """A bank with columns and a rising rate chart."""
    cv.rect(px, py, pw, ph, PAL["paper"])
    cv.disc(px + int(pw * 0.92), py + int(ph * 0.14),
            max(3, ph // 7), PAL["sun"])
    # bank front: pediment, five columns, steps and a door
    bx = px + int(pw * 0.06)
    bw = int(pw * 0.48)
    cv.polygon([(bx, py + int(ph * 0.25)), (bx + bw // 2, py + 4),
                (bx + bw, py + int(ph * 0.25))], PAL["dark"])
    cv.polygon([(bx + 4, py + int(ph * 0.25)),
                (bx + bw // 2, py + 8),
                (bx + bw - 4, py + int(ph * 0.25))], PAL["steel"])
    for i in range(5):
        cx = bx + int(bw * (0.06 + i * 0.19))
        cv.rect(cx, py + int(ph * 0.28), 5, int(ph * 0.46),
                PAL["ink"])
        cv.rect(cx - 1, py + int(ph * 0.28), 7, 2, PAL["ink"])
        cv.rect(cx - 1, py + int(ph * 0.72), 7, 2, PAL["ink"])
    cv.rect(bx + bw // 2 - 6, py + int(ph * 0.52), 12,
            int(ph * 0.22), PAL["ink"])
    cv.rect(bx + bw // 2 - 4, py + int(ph * 0.54), 8,
            int(ph * 0.20), PAL["gold"])
    for i in range(3):
        cv.rect(bx - 4, py + int(ph * (0.78 + i * 0.05)), bw + 8, 3,
                PAL["dark"])
    # a gold coin on the pediment
    cv.disc(bx + bw // 2, py + int(ph * 0.14), 5, PAL["gold"])
    cv.ring(bx + bw // 2, py + int(ph * 0.14), 5, PAL["ink"])
    cv.disc(bx + bw // 2, py + int(ph * 0.14), 2, PAL["orange"])
    # the rate chart: axes, grid, a flat line and a rising one
    ox = px + int(pw * 0.62)
    oy = py + int(ph * 0.78)
    for gy in (0.18, 0.36):
        cv.hline(ox, oy - int(ph * gy), int(pw * 0.32), PAL["steel"])
    cv.segment(ox, oy, ox, oy - int(ph * 0.5), PAL["ink"], 1)
    cv.segment(ox, oy, ox + int(pw * 0.32), oy, PAL["ink"], 1)
    cv.segment(ox, oy - int(ph * 0.06),
               ox + int(pw * 0.30), oy - int(ph * 0.10), PAL["blue"],
               2)
    pts = [(ox, oy), (ox + int(pw * 0.08), oy - int(ph * 0.16)),
           (ox + int(pw * 0.16), oy - int(ph * 0.20)),
           (ox + int(pw * 0.28), oy - int(ph * 0.46))]
    for i in range(3):
        cv.segment(pts[i][0], pts[i][1], pts[i + 1][0],
                   pts[i + 1][1], PAL["red"], 2)
    for p in pts[1:]:
        cv.disc(p[0], p[1], 3, PAL["red"])
        cv.disc(p[0], p[1], 1, PAL["white"])
    cv.text(ox + int(pw * 0.20), oy - int(ph * 0.58), "4%", 1,
            PAL["red"])


def scene_sanctions(cv, px, py, pw, ph):
    """Australia stamped: sanctions over settlements."""
    cv.vgrad(px, py, pw, ph, PAL["sky"], PAL["pale"])
    # simplified Australia, with state lines and a capital dot
    ax, ay = px + int(pw * 0.26), py + int(ph * 0.08)
    cv.polygon([(ax, ay + 7), (ax + 10, ay), (ax + 34, ay + 2),
                (ax + 44, ay + 9), (ax + 38, ay + 17),
                (ax + 20, ay + 20), (ax + 4, ay + 15)], PAL["tan"])
    cv.frame(ax - 2, ay - 2, 50, 24, PAL["ink"], 1)
    cv.segment(ax + 12, ay + 2, ax + 12, ay + 21, PAL["rust"], 1)
    cv.segment(ax + 2, ay + 12, ax + 46, ay + 12, PAL["rust"], 1)
    cv.disc(ax + 36, ay + 15, 2, PAL["red"])
    # the scales of justice on the left
    sx = px + int(pw * 0.06)
    sy = py + int(ph * 0.18)
    cv.vline(sx + 10, sy, 22, PAL["ink"], 2)
    cv.segment(sx, sy + 2, sx + 20, sy + 2, PAL["ink"], 2)
    for j in (0, 20):
        cv.segment(sx + j, sy + 2, sx + j - 4, sy + 10, PAL["ink"],
                   1)
        cv.segment(sx + j, sy + 2, sx + j + 4, sy + 10, PAL["ink"],
                   1)
        cv.polygon([(sx + j - 6, sy + 10), (sx + j + 6, sy + 10),
                    (sx + j, sy + 14)], PAL["gold"])
    # a red stamp across the lower half, and a gavel
    sx = px + int(pw * 0.12)
    sy = py + int(ph * 0.62)
    cv.frame(sx, sy, int(pw * 0.76), int(ph * 0.3), PAL["red"], 2)
    cv.text(sx + 4, sy + 3, "SANCTIONED", 1, PAL["red"])
    gx, gy = px + int(pw * 0.74), py + int(ph * 0.10)
    cv.rect(gx, gy, 14, 5, PAL["table"])
    cv.rect(gx, gy, 14, 2, PAL["box"])
    cv.segment(gx + 7, gy + 5, gx + 7, gy + 16, PAL["table"], 2)
    cv.rect(gx + 2, gy + 16, 10, 3, PAL["table"])
    # a sealed document above the stamp
    cv.rect(px + int(pw * 0.52), py + int(ph * 0.36), 16, 10,
            PAL["white"])
    cv.frame(px + int(pw * 0.52), py + int(ph * 0.36), 16, 10,
             PAL["ink"], 1)
    cv.hline(px + int(pw * 0.52) + 2, py + int(ph * 0.36) + 3, 12,
             PAL["grey"])
    cv.disc(px + int(pw * 0.52) + 12, py + int(ph * 0.36) + 7, 2,
            PAL["red"])


def scene_cyclone(cv, px, py, pw, ph):
    """Cyclone Akvan spiralling over the Bay of Bengal."""
    cv.vgrad(px, py, pw, ph, PAL["sea"], PAL["deep"])
    cv.disc(px + int(pw * 0.10), py + int(ph * 0.10), 5, PAL["white"])
    cv.disc(px + int(pw * 0.16), py + int(ph * 0.08), 4, PAL["white"])
    cx, cy = px + int(pw * 0.5), py + int(ph * 0.48)
    # spiral arms, tightening toward the eye
    for r in (5, 9, 13, 17, 21):
        for a in range(0, 300, 5):
            rad = math.radians(a + r * 9)
            cv.set(cx + int(r * math.cos(rad)),
                   cy + int(r * 0.8 * math.sin(rad)), PAL["white"])
    cv.disc(cx, cy, 5, PAL["gold"])
    cv.ring(cx, cy, 5, PAL["white"])
    cv.disc(cx, cy, 2, PAL["orange"])
    # rain bands sweeping in from the sides
    for i in range(8):
        rx = px + int(pw * (0.06 + i * 0.12))
        cv.segment(rx, py + int(ph * 0.52), rx - 3,
                   py + int(ph * 0.66), PAL["sky"], 1)
    # the coast at the bottom: land, palms, houses, a boat
    cv.polygon([(px, py + ph), (px, py + int(ph * 0.82)),
                (px + int(pw * 0.3), py + int(ph * 0.86)),
                (px + int(pw * 0.6), py + int(ph * 0.82)),
                (px + pw, py + int(ph * 0.88)), (px + pw, py + ph)],
               PAL["land"])
    for tx in (0.10, 0.78):
        bx = px + int(pw * tx)
        cv.segment(bx, py + int(ph * 0.97), bx + 1,
                   py + int(ph * 0.86), PAL["rust"], 1)
        for a in (200, 250, 290, 340):
            rad = math.radians(a)
            cv.segment(bx + 1, py + int(ph * 0.86),
                       bx + 1 + int(6 * math.cos(rad)),
                       py + int(ph * 0.86) +
                       int(4 * math.sin(rad)), PAL["leaf"], 1)
    for hx in (0.30, 0.55):
        bx = px + int(pw * hx)
        cv.rect(bx, py + int(ph * 0.90), 10, 6, PAL["white"])
        cv.polygon([(bx - 1, py + int(ph * 0.90)),
                    (bx + 5, py + int(ph * 0.84)),
                    (bx + 11, py + int(ph * 0.90))], PAL["red"])
    bx = px + int(pw * 0.88)
    cv.polygon([(bx, py + int(ph * 0.78)), (bx + 12, py + int(ph * 0.78)),
                (bx + 10, py + int(ph * 0.81)),
                (bx + 2, py + int(ph * 0.81))], PAL["hull"])
    # warning triangle with the gust figure
    tx, ty = px + int(pw * 0.05), py + int(ph * 0.06)
    cv.polygon([(tx, ty + 12), (tx + 7, ty), (tx + 14, ty + 12)],
               PAL["gold"])
    cv.frame(tx, ty, 15, 13, PAL["ink"], 1)
    cv.text(tx + 5, ty + 4, "!", 1, PAL["ink"])

# ---- World map: dotted continents in lon/lat, pins for the leads ----
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80),
     (-85, 70), (-75, 62), (-60, 55), (-55, 47), (-70, 42),
     (-75, 35), (-80, 26), (-84, 30), (-85, 20), (-90, 15),
     (-95, 18), (-105, 22), (-115, 28), (-125, 40), (-125, 50),
     (-140, 60), (-155, 58), (-165, 60)],
    # South America
    [(-80, 10), (-75, 5), (-60, 5), (-50, 0), (-40, -5), (-35, -10),
     (-40, -20), (-48, -28), (-55, -35), (-65, -40), (-70, -50),
     (-73, -40), (-70, -30), (-75, -18), (-80, -5)],
    # Africa
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (32, 31),
     (35, 28), (40, 15), (48, 11), (51, 10), (45, 0), (40, -10),
     (35, -20), (30, -30), (20, -35), (15, -25), (12, -15), (8, 4),
     (-8, 5), (-15, 10)],
    # Madagascar
    [(47, -15), (50, -17), (48, -22), (45, -25), (43, -20)],
    # Eurasia, with Arabia and India drawn in
    [(-10, 36), (-5, 43), (0, 48), (5, 55), (10, 58), (18, 56),
     (21, 60), (25, 65), (30, 70), (45, 68), (60, 70), (75, 73),
     (90, 75), (110, 76), (130, 72), (150, 70), (170, 67), (178, 65),
     (170, 60), (160, 55), (150, 45), (140, 40), (130, 35),
     (122, 30), (115, 22), (108, 12), (103, 8), (100, 8), (95, 15),
     (90, 22), (85, 20), (80, 10), (75, 8), (72, 20), (66, 25),
     (58, 25), (55, 17), (48, 14), (43, 12), (40, 15), (38, 22),
     (35, 28), (35, 36), (30, 36), (25, 38), (20, 40), (15, 44),
     (10, 44), (5, 43), (0, 40), (-5, 36), (-10, 36)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -27),
     (150, -22), (146, -19), (142, -11), (137, -12), (132, -11),
     (126, -14), (122, -17), (118, -20)],
    # Greenland
    [(-55, 60), (-45, 60), (-35, 65), (-25, 70), (-30, 75),
     (-45, 76), (-55, 72)],
    # New Zealand
    [(167, -45), (174, -41), (178, -38), (174, -35), (170, -40)],
    # Japan
    [(130, 31), (133, 34), (137, 35), (140, 38), (142, 42),
     (141, 45), (138, 40), (134, 35), (131, 33)],
    # Britain
    [(-5, 50), (-2, 53), (0, 53), (1, 51), (-3, 50)],
]

# (number, lon, lat) for the 13 lead stories.
PINS = [
    (1, 48.0, 29.3), (2, 114.1, 22.5), (3, 30.7, 36.9),
    (4, 34.5, 31.5), (5, 90.4, 23.8), (6, -118.2, 34.2),
    (7, -72.3, 18.5), (8, 30.7, 46.5), (9, 37.9, 14.7),
    (10, 174.8, -36.8), (11, -0.1, 51.5), (12, 149.1, -35.3),
    (13, 80.3, 16.5),
]


def point_in_poly(x, y, poly):
    """Ray-casting point-in-polygon test in lon/lat space."""
    inside = False
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        if (y0 > y) != (y1 > y):
            xin = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            if x < xin:
                inside = not inside
    return inside


def draw_map(cv, x, y, w, h):
    """Dotted world map with numbered pins for the 13 leads."""
    cv.rect(x, y, w, h, PAL["sky"])
    cv.frame(x, y, w, h, PAL["ink"], 2)

    def proj(lon, lat):
        px = x + int((lon + 170) / 360.0 * w)
        py = y + int((80 - lat) / 140.0 * h)
        return (px, py)

    bboxes = []
    for poly in CONTINENTS:
        lons = [p[0] for p in poly]
        lats = [p[1] for p in poly]
        bboxes.append((min(lons), max(lons), min(lats), max(lats)))
    for gy in range(y + 2, y + h - 2, 4):
        lat = 80 - (gy - y) / h * 140.0
        for gx in range(x + 2, x + w - 2, 4):
            lon = (gx - x) / w * 360.0 - 170
            for k, poly in enumerate(CONTINENTS):
                lo0, lo1, la0, la1 = bboxes[k]
                if not (lo0 <= lon <= lo1 and la0 <= lat <= la1):
                    continue
                if point_in_poly(lon, lat, poly):
                    col = (PAL["land"] if
                           ((gx // 4 + gy // 4) % 2 == 0) else
                           PAL["land2"])
                    cv.rect(gx, gy, 2, 2, col)
                    break
    cv.text(x + int(w * 0.05), y + int(h * 0.55), "N. AMERICA", 1,
            PAL["dark"])
    cv.text(x + int(w * 0.24), y + int(h * 0.72), "S. AMERICA", 1,
            PAL["dark"])
    cv.text(x + int(w * 0.47), y + int(h * 0.55), "AFRICA", 1,
            PAL["dark"])
    cv.text(x + int(w * 0.40), y + int(h * 0.10), "EUROPE", 1,
            PAL["dark"])
    cv.text(x + int(w * 0.72), y + int(h * 0.20), "ASIA", 1,
            PAL["dark"])
    cv.text(x + int(w * 0.80), y + int(h * 0.62), "OCEANIA", 1,
            PAL["dark"])
    # Pins 3, 4 and 8 sit on top of each other around Turkiye and
    # the Levant, so they are fanned out with leader lines to
    # their true positions.
    offsets = {3: (-16, 10), 4: (16, -8), 8: (-20, -8)}
    for num, lon, lat in PINS:
        px, py = proj(lon, lat)
        dx, dy = offsets.get(num, (0, 0))
        if dx or dy:
            cv.segment(px, py, px + dx, py + dy, PAL["ink"], 1)
            px, py = px + dx, py + dy
        cv.disc(px, py, 7, PAL["red"])
        cv.ring(px, py, 7, PAL["ink"])
        label = str(num)
        cv.text(px - (3 if num < 10 else 6), py - 3, label, 1,
                PAL["white"])


# ---- The 42 stories: 13 illustrated leads, 29 briefs ----
# Lead: (number, region, field, tag, scene, headline, deck)
LEADS = [
    (1, "MIDDLE EAST", "WAR", "MIDDLE EAST - WAR", scene_gulf,
     "IRAN DRONES TARGET US BASE IN KUWAIT",
     "KUWAIT AND BAHRAIN SAY DEFENCES SHOT THEM DOWN. "
     "IRAN SAYS IT AIMED AT ALI AL SALEM."),
    (2, "ASIA", "POLITICS", "ASIA - DIPLOMACY", scene_summit,
     "XI GREETS TRUMP AS APEC OPENS",
     "SHENZHEN HOSTS THE SUMMIT. XI URGES FREE TRADE. "
     "THE TRILATERAL MEETS THURSDAY."),
    (3, "WORLD", "CLIMATE", "CLIMATE", scene_cop,
     "COP31 SPLIT ON FOSSIL FUELS",
     "INDONESIA: PHASE DOWN TO 2060, NOT PHASE OUT. "
     "DRAFT DEAL STILL UNAGREED."),
    (4, "MIDDLE EAST", "WAR", "MIDDLE EAST - TRUCE", scene_gaza,
     "GAZA TRUCE MAY COLLAPSE, BOARD WARNS",
     "A CEASEFIRE THAT DELIVERS NOTHING VISIBLE CANNOT LAST, "
     "THE BOARD TELLS THE UN."),
    (5, "ASIA", "ECONOMY", "ASIA - LABOUR", scene_bangladesh,
     "BANGLADESH WAGE PROTESTS SHUT 500 FACTORIES",
     "WORKERS WANT TK30,000 A MONTH, UP FROM TK12,500. "
     "NEARLY 300 ARRESTED."),
    (6, "WORLD", "CLIMATE", "SCIENCE - SPACE", scene_voyager,
     "VOYAGER 1, ONE LIGHT-DAY FROM EARTH",
     "25.9BN KM OUT, THE FIRST HUMAN OBJECT A LIGHT-DAY AWAY. "
     "A SIGNAL TAKES A FULL DAY."),
    (7, "AMERICAS", "WAR", "AMERICAS - SECURITY", scene_haiti,
     "SALVADOR TROOPS HIT GANG BOSS HOME IN HAITI",
     "HELICOPTERS DESTROY JEFF LAROSE'S CANAAN HOUSE. "
     "BUKELE HAILS IT AS A VERTIERES GIFT."),
    (8, "EUROPE", "WAR", "EUROPE - WAR", scene_odesa,
     "RUSSIA HITS ODESA: 4 DEAD",
     "4 DEAD, 13 HURT IN CENTRAL ODESA. UKRAINE SHOT DOWN "
     "126 OF 141 DRONES OVERNIGHT."),
    (9, "AFRICA", "WAR", "AFRICA - SECURITY", scene_badme,
     "ETHIOPIA AND ERITREA MASS TROOPS",
     "ARMIES FACE OFF NEAR BADME. MONITORS FEAR OUTRIGHT "
     "WAR IN THE HORN OF AFRICA."),
    (10, "WORLD", "SOCIETY", "CULTURE - GAMES", scene_gta,
     "GTA VI ROLLS OUT AT MIDNIGHT",
     "NZ PLAYS FIRST AT MIDNIGHT. CRITICS GIVE 99/100. "
     "NO PC VERSION."),
    (11, "EUROPE", "ECONOMY", "ECONOMY", scene_bank,
     "BAILEY: LONG WAR MEANS HIGHER RATES",
     "BAILEY: WAR LENGTH DECIDES THE RATE PATH. "
     "UK INFLATION 3.6%."),
    (12, "OCEANIA", "POLITICS", "OCEANIA - DIPLOMACY",
     scene_sanctions,
     "AUSTRALIA SANCTIONS WEISS",
     "3 PEOPLE, 4 GROUPS BLACKLISTED OVER "
     "WEST BANK SETTLEMENTS."),
    (13, "ASIA", "DISASTERS", "ASIA - WEATHER", scene_cyclone,
     "CYCLONE AKVAN NEARS INDIA",
     "ODISHA SHUTS SCHOOLS. LANDFALL FRIDAY, "
     "GUSTS TO 145 KM/H."),
]

# Brief: (region, field, text) — stories 14 to 42.
BRIEFS = [
    ("MIDDLE EAST", "WAR",
     "YEMEN: GULF STATES ALSO SHOT DOWN MISSILES AND DRONES FROM HOUTHI ALLIES."),
    ("MIDDLE EAST", "POLITICS",
     "WEST BANK: BRITAIN SANCTIONED 8 SETTLEMENT FIRMS ON TUESDAY."),
    ("MIDDLE EAST", "WAR",
     "GAZA: ISRAEL'S KATZ SAYS NO WITHDRAWAL UNTIL HAMAS IS DISMANTLED."),
    ("ASIA", "JUSTICE",
     "MYANMAR: WORLD COURT RULES THURSDAY ON THE ROHINGYA GENOCIDE CASE."),
    ("AMERICAS", "POLITICS",
     "USA: HOUSE DEMOCRATS NOMINATE JEFFRIES FOR SPEAKER, 251-11."),
    ("AMERICAS", "TECH",
     "USA: GAO SAYS 4 TOP AI MODELS DREW UP MASS-CASUALTY ATTACK PLANS."),
    ("AMERICAS", "TECH",
     "USA: SENATORS INTRODUCE BILL TO FORCE STEALTH BOTS TO IDENTIFY."),
    ("AMERICAS", "TECH",
     "USA: OUTAGE WAVE REACHES THE NSA AFTER APPLE, BANKS, AIRLINES."),
    ("AMERICAS", "ECONOMY",
     "USA: LA AND LONG BEACH PORT TALKS STALL; 250 WATCHMEN MAY STRIKE."),
    ("AMERICAS", "DISASTERS",
     "USA: BLAST AT CLEAN HARBORS WASTE PLANT NEAR HOUSTON; 1 IN HOSPITAL."),
    ("AMERICAS", "POLITICS",
     "USA: PEW: TWO-THIRDS DISAPPROVE OF TRUMP ON THE RUSSIA-UKRAINE WAR."),
    ("WORLD", "SOCIETY",
     "RELIGION: PEW: MUSLIMS TO PASS CHRISTIANS AS TOP FAITH BY 2035."),
    ("EUROPE", "WAR",
     "UKRAINE: 1,000+ RUSSIAN ATTACKS ON ENERGY SITES SINCE SEPTEMBER."),
    ("EUROPE", "ECONOMY",
     "UK: INFLATION HIT 3.6% IN OCTOBER, HIGHEST IN A YEAR."),
    ("WORLD", "POLITICS",
     "COP31: DRAFT SPLITS ON PHASE-OUT V PHASE-DOWN."),
    ("WORLD", "POLITICS",
     "COP31: TALKS CLOSE FRIDAY 20 NOV IN ANTALYA, TURKIYE."),
    ("ASIA", "POLITICS",
     "APEC: PUTIN EXPECTS BIG BENEFIT FROM THURSDAY'S TRILATERAL."),
    ("ASIA", "POLITICS",
     "APEC: XI URGES FREE TRADE AND HITS OUT AT PROTECTIONISM."),
    ("MIDDLE EAST", "WAR",
     "GULF: FIRST IRANIAN ATTACK ON KUWAIT SINCE SEPTEMBER."),
    ("ASIA", "ECONOMY",
     "BANGLADESH: WAGE BOARD MEETS AGAIN ON 23 NOV."),
    ("ASIA", "JUSTICE",
     "BANGLADESH: NEARLY 300 ARRESTED, 24 CASES FILED."),
    ("AFRICA", "POLITICS",
     "ETHIOPIA: ERITREA DENIES CROSSING INTO TIGRAY."),
    ("AMERICAS", "SOCIETY",
     "HAITI: 223RD ANNIVERSARY OF THE BATTLE OF VERTIERES."),
    ("AMERICAS", "POLITICS",
     "HAITI: UN-BACKED FORCE SAYS IT TOOK NO PART IN THE STRIKE."),
    ("AMERICAS", "SOCIETY",
     "GTA VI: US UNLOCKS AT MIDNIGHT EASTERN; NO PC VERSION AT LAUNCH."),
    ("WORLD", "ECONOMY",
     "GTA VI: LEAVE REQUESTS UP 32% AROUND 19 NOV, SAYS REMOTE."),
    ("ASIA", "DISASTERS",
     "CYCLONE: LANDFALL DUE FRIDAY NOON, GUSTS TO 145 KM/H."),
    ("ASIA", "DISASTERS",
     "CYCLONE: 7 ANDHRA DISTRICTS ON RED ALERT."),
    ("WORLD", "CLIMATE",
     "SPACE: A RADIO SIGNAL TO VOYAGER 1 NOW TAKES A FULL DAY EACH WAY."),
]

# The day in numbers: (big numeral, label). All four figures were
# reported on 18 November itself.
NUMBERS = [
    ("126", "DRONES UKRAINE SHOT DOWN OF 141 OVERNIGHT"),
    ("99/100", "GTA VI METACRITIC SCORE FROM 100+ CRITICS"),
    ("145 KM/H", "CYCLONE AKVAN FORECAST GUSTS AT LANDFALL"),
    ("200,000", "PEOPLE ODISHA PLANS TO MOVE INLAND"),
]

REGION_ORDER = ["MIDDLE EAST", "ASIA", "EUROPE", "AFRICA",
                "AMERICAS", "OCEANIA", "WORLD"]
REGION_COLORS = {"MIDDLE EAST": PAL["red"], "ASIA": PAL["blue"],
                 "EUROPE": PAL["gold"], "AFRICA": PAL["green"],
                 "AMERICAS": PAL["teal"], "OCEANIA": PAL["orange"],
                 "WORLD": PAL["steel"]}
FIELD_ORDER = ["WAR", "POLITICS", "ECONOMY", "SOCIETY", "DISASTERS",
               "TECH", "CLIMATE", "JUSTICE"]
FIELD_COLORS = {"WAR": PAL["red"], "POLITICS": PAL["blue"],
                "ECONOMY": PAL["gold"], "SOCIETY": PAL["pink"],
                "DISASTERS": PAL["orange"], "TECH": PAL["teal"],
                "CLIMATE": PAL["green"], "JUSTICE": PAL["purple"]}


def count_stories():
    """Count the 42 stories by region and by field."""
    regions = {name: 0 for name in REGION_ORDER}
    fields = {name: 0 for name in FIELD_ORDER}
    for _num, region, field, _tag, _sc, _h, _d in LEADS:
        regions[region] += 1
        fields[field] += 1
    for region, field, _text in BRIEFS:
        regions[region] += 1
        fields[field] += 1
    assert sum(regions.values()) == 42
    assert sum(fields.values()) == 42
    return regions, fields


def lead_card(cv, x, y, w, h, num, tag, scene, headline, deck):
    ink = PAL["ink"]
    cv.rect(x, y, w, h, PAL["paper"])
    cv.frame(x, y, w, h, ink, 2)
    cv.text(x + 8, y + 5, str(num) + " " + tag, 1, PAL["red"])
    scene(cv, x + 6, y + 14, w - 12, 42)
    hy = y + 60
    used = cv.wrapped(x + w // 2, hy, headline, 2, ink, w - 16,
                      leading=2, max_lines=2)
    cv.wrapped(x + w // 2, hy + used + 4, deck, 1, PAL["dark"],
               w - 16, leading=2, max_lines=2)


def draw_chips(cv, y, label, order, counts, colors, bar_scale):
    """One row: a label, then NAME n plus a bar per item."""
    cv.text(24, y, label, 1, PAL["red"])
    x = 100
    for name in order:
        count = counts[name]
        txt = name + " " + str(count)
        cv.text(x, y, txt, 1, PAL["ink"])
        x += cv.text_width(txt, 1) + 6
        bw = count * bar_scale
        cv.rect(x, y, bw, 7, colors[name])
        cv.frame(x, y, bw, 7, PAL["ink"], 1)
        x += bw + 12


def draw_numbers(cv, y, h):
    """The by-the-numbers strip: four big numerals with labels."""
    cv.rect(24, y, WIDTH - 48, h, PAL["paper"])
    cv.frame(24, y, WIDTH - 48, h, PAL["ink"], 2)
    cv.centered(WIDTH // 2, y + 2, "BY THE NUMBERS", 1, PAL["red"])
    cw = (WIDTH - 48) // 4
    for i, (num, label) in enumerate(NUMBERS):
        x0 = 24 + i * cw
        if i:
            cv.vline(x0, y, h, PAL["ink"], 1)
        cv.centered(x0 + cw // 2, y + 11, num, 3, PAL["red"])
        cv.wrapped(x0 + cw // 2, y + 34, label, 1, PAL["dark"],
                   cw - 16, leading=2, max_lines=2)


def main():
    cv = Canvas(WIDTH, HEIGHT)
    ink = PAL["ink"]
    cv.rect(0, 0, WIDTH, HEIGHT, PAL["cream"])
    cv.frame(0, 0, WIDTH, HEIGHT, ink, 8)

    # Masthead.
    cv.centered(WIDTH // 2, 16, "THE WORLD IN ONE PICTURE", 4, ink)
    cv.hline(24, 52, WIDTH - 48, ink, 2)
    cv.centered(WIDTH // 2, 60, "WEDNESDAY 18 NOVEMBER 2026", 3, ink)
    cv.hline(24, 88, WIDTH - 48, ink, 2)

    # Counts band.
    cv.rect(24, 94, WIDTH - 48, 20, ink)
    cv.centered(WIDTH // 2, 99,
                "42 STORIES - 7 REGIONS - 8 FIELDS - 13 ILLUSTRATED",
                2, PAL["cream"])

    # Region and field count bars, counted from the stories.
    regions, fields = count_stories()
    draw_chips(cv, 120, "REGIONS", REGION_ORDER, regions,
               REGION_COLORS, 8)
    draw_chips(cv, 134, "FIELDS", FIELD_ORDER, fields,
               FIELD_COLORS, 7)

    # By-the-numbers strip.
    draw_numbers(cv, 148, 56)

    # Lead cards: three rows of three, then a row of four.
    rows = [(210, 325, LEADS[0:3]), (330, 325, LEADS[3:6]),
            (450, 325, LEADS[6:9]), (570, 242, LEADS[9:13])]
    for ry, cw, cards in rows:
        x = 16
        for num, _region, _field, tag, scene, headline, deck in cards:
            lead_card(cv, x, ry, cw, 116, num, tag, scene, headline,
                      deck)
            x += cw + 8

    # World map with numbered pins.
    cv.centered(WIDTH // 2, 692,
                "WHERE IT HAPPENED - RED NUMBERS ARE THE 13 LEADS, "
                "DOTS MARK LAND", 1, ink)
    draw_map(cv, 24, 702, WIDTH - 48, 94)

    # Briefs 14-42 in two columns.
    cv.centered(WIDTH // 2, 802, "ALSO ON WEDNESDAY 18 NOVEMBER", 2,
                ink)
    cv.hline(24, 820, WIDTH - 48, ink, 1)
    left = BRIEFS[:15]
    right = BRIEFS[15:]
    for i, (_region, _field, brief) in enumerate(left):
        cv.text(24, 826 + i * 9, str(14 + i) + ". " + brief, 1, ink)
    for i, (_region, _field, brief) in enumerate(right):
        cv.text(524, 826 + i * 9, str(29 + i) + ". " + brief, 1, ink)

    # Footer: date check and sources.
    cv.hline(24, 966, WIDTH - 48, ink, 2)
    cv.wrapped(WIDTH // 2, 972,
               "DATE CHECK - LEFT OUT BECAUSE FIRST REPORTED 17 NOV: "
               "PELTOLA WINS ALASKA SENATE SEAT; NVIDIA'S $115.8BN "
               "QUARTER; PRAGUE TRAIN CRASH; MONGOLIA'S PRESIDENT "
               "RESIGNS; UKRAINE HITS THE KERCH BRIDGE.",
               1, PAL["red"], WIDTH - 48, leading=2, max_lines=2)
    cv.centered(WIDTH // 2, 1000,
                "SOURCES: REUTERS, AP, AFP, AL JAZEERA, BLOOMBERG, "
                "BBC, NASA, IMD, PEW RESEARCH CENTER.", 1, PAL["dark"])

    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if outdir:
        os.makedirs(outdir, exist_ok=True)
        write_png(cv, os.path.join(outdir, "entry.png"))
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        write_png(cv, os.path.join(here, "entry.png"))


if __name__ == "__main__":
    main()
