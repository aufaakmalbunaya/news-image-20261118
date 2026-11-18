#!/usr/bin/env python3
"""THE WORLD IN ONE PICTURE: Wednesday 18 November 2026. Round 2.

A dense newspaper front page, 1024 by 1024 pixels, drawn with the
Python standard library only. It sums up 42 stories first reported
on Wednesday 18 November 2026: 13 illustrated lead cards, a world
map with numbered pins, 29 one-line briefs, a day-in-numbers strip
and a date-check footer naming stories left out because they were
first reported on 17 November.

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
    "sea": (38, 110, 180),
    "deep": (24, 80, 150),
    "night": (38, 52, 96),
    "night2": (70, 80, 140),
    "land": (196, 178, 130),
    "land2": (168, 158, 110),
    "green": (90, 140, 80),
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


# ---- Lead scenes: one small original illustration per card ----
# Each scene draws into the box (px, py, pw, ph) using fractions of
# its width and height, so it works in both card widths.


def scene_gulf(cv, px, py, pw, ph):
    """Night over the Gulf: drones, flares, a base on the shore."""
    cv.rect(px, py, pw, ph, PAL["night"])
    sea_y = py + int(ph * 0.62)
    cv.rect(px, sea_y, pw, ph - int(ph * 0.62), PAL["deep"])
    for sx, sy in ((8, 6), (30, 14), (55, 5), (78, 12), (92, 4)):
        cv.set(px + int(sx * pw / 100), py + int(sy * ph / 100),
               PAL["gold"])
    cv.disc(px + int(pw * 0.86), py + int(ph * 0.22),
            max(3, ph // 6), PAL["moon"])
    # two drones diving in, bright heads and dotted trails
    cv.segment(px + int(pw * 0.12), py + 2,
               px + int(pw * 0.38), sea_y - 4, PAL["white"], 1)
    cv.disc(px + int(pw * 0.38), sea_y - 4, 3, PAL["flame"])
    cv.segment(px + int(pw * 0.62), py + 2,
               px + int(pw * 0.78), sea_y - 6, PAL["white"], 1)
    cv.disc(px + int(pw * 0.78), sea_y - 6, 3, PAL["flame"])
    # air base on the shore: runway lights and a hangar
    cv.rect(px + int(pw * 0.05), sea_y + 2, int(pw * 0.9), 2, PAL["gold"])
    cv.rect(px + int(pw * 0.08), sea_y + 6, int(pw * 0.24),
            ph - int(ph * 0.62) - 8, PAL["deck"])
    cv.rect(px + int(pw * 0.62), sea_y + 4, int(pw * 0.30),
            ph - int(ph * 0.62) - 6, PAL["steel"])
    # interceptor burst over the base
    cv.disc(px + int(pw * 0.5), sea_y - 8, 4, PAL["orange"])
    cv.disc(px + int(pw * 0.5), sea_y - 8, 2, PAL["flame"])


def scene_summit(cv, px, py, pw, ph):
    """Three flags over the Shenzhen skyline at dusk."""
    cv.rect(px, py, pw, ph, PAL["dusk"])
    cv.rect(px, py + int(ph * 0.45), pw, ph - int(ph * 0.45),
            PAL["dusk2"])
    cv.disc(px + int(pw * 0.88), py + int(ph * 0.2),
            max(3, ph // 7), PAL["sun"])
    # skyline towers with lit windows
    for i in range(6):
        tx = px + int(pw * (0.02 + i * 0.16))
        tw = int(pw * 0.12)
        th = int(ph * (0.35 + (i % 3) * 0.12))
        base_y = py + ph - th - int(ph * 0.18)
        cv.rect(tx, base_y, tw, th, PAL["tower"])
        cv.rect(tx + 2, base_y + 4, 3, 4, PAL["window"])
        cv.rect(tx + tw - 5, base_y + th // 2, 3, 4, PAL["window"])
    ground_y = py + ph - int(ph * 0.18)
    cv.rect(px, ground_y, pw, int(ph * 0.18), PAL["ground"])
    # three flags: China red, US stripes, Russia white-blue-red
    flag_cols = [(PAL["red"], PAL["red"], PAL["red"]),
                 (PAL["red"], PAL["white"], PAL["blue"]),
                 (PAL["white"], PAL["blue"], PAL["red"])]
    for j, cols in enumerate(flag_cols):
        fx = px + int(pw * (0.12 + j * 0.32))
        cv.vline(fx, py + 2, int(ph * 0.42), PAL["ink"], 2)
        for i, col in enumerate(cols):
            cv.rect(fx + 2, py + 2 + i * 4, int(pw * 0.13), 4, col)


def scene_cop(cv, px, py, pw, ph):
    """A globe, a smoking stack and a green leaf: the climate split."""
    cv.rect(px, py, pw, ph, PAL["sky"])
    cx, cy = px + int(pw * 0.26), py + ph // 2
    r = int(ph * 0.36)
    cv.disc(cx, cy, r, PAL["sea"])
    cv.disc(cx - r // 3, cy - r // 4, r // 3, PAL["green"])
    cv.disc(cx + r // 3, cy + r // 4, r // 4, PAL["green"])
    cv.ring(cx, cy, r, PAL["ink"])
    # factory with two stacks on the right
    bx = px + int(pw * 0.55)
    cv.rect(bx, py + int(ph * 0.45), int(pw * 0.4), int(ph * 0.55),
            PAL["dark"])
    cv.rect(bx + int(pw * 0.06), py + int(ph * 0.2),
            int(pw * 0.07), int(ph * 0.25), PAL["steel"])
    cv.rect(bx + int(pw * 0.22), py + int(ph * 0.3),
            int(pw * 0.07), int(ph * 0.15), PAL["steel"])
    cv.disc(bx + int(pw * 0.09), py + int(ph * 0.12), 4, PAL["grey"])
    cv.disc(bx + int(pw * 0.13), py + int(ph * 0.06), 3, PAL["grey"])
    # a green leaf rising above the smoke
    lx, ly = px + int(pw * 0.82), py + int(ph * 0.14)
    cv.polygon([(lx, ly - 6), (lx + 7, ly), (lx, ly + 6), (lx - 7, ly)],
               PAL["green"])
    cv.segment(lx, ly - 6, lx, ly + 8, PAL["green"], 1)


def scene_gaza(cv, px, py, pw, ph):
    """A white flag on a broken wall, dusk over Gaza."""
    cv.rect(px, py, pw, ph, PAL["dusk"])
    cv.disc(px + int(pw * 0.85), py + int(ph * 0.25),
            max(3, ph // 7), PAL["sun"])
    # broken wall: blocks at two heights
    wy = py + int(ph * 0.55)
    for i in range(7):
        bw = int(pw * 0.13)
        bx = px + i * bw
        bh = int(ph * (0.30 + (0.15 if i % 2 else 0.0)))
        cv.rect(bx, wy + int(ph * 0.45) - bh, bw - 2, bh, PAL["tan"])
    cv.rect(px, wy + int(ph * 0.45), pw, 3, PAL["ink"])
    # white flag on a pole above the wall
    fx = px + int(pw * 0.5)
    cv.vline(fx, py + int(ph * 0.12), int(ph * 0.45), PAL["ink"], 2)
    cv.rect(fx + 2, py + int(ph * 0.12), int(pw * 0.16),
            int(ph * 0.2), PAL["white"])
    # a small dove above the flag
    dx, dy = px + int(pw * 0.2), py + int(ph * 0.2)
    cv.disc(dx, dy, 3, PAL["white"])
    cv.segment(dx - 8, dy - 2, dx - 2, dy, PAL["white"], 2)
    cv.segment(dx + 2, dy, dx + 8, dy - 3, PAL["white"], 2)


def scene_bangladesh(cv, px, py, pw, ph):
    """Garment workers, a factory and a wage banner."""
    cv.rect(px, py, pw, ph, PAL["paper"])
    # factory block with chimneys
    cv.rect(px + int(pw * 0.55), py + int(ph * 0.35), int(pw * 0.42),
            int(ph * 0.65), PAL["red"])
    cv.rect(px + int(pw * 0.6), py + int(ph * 0.1), int(pw * 0.06),
            int(ph * 0.25), PAL["steel"])
    cv.rect(px + int(pw * 0.75), py + int(ph * 0.18), int(pw * 0.06),
            int(ph * 0.17), PAL["steel"])
    for i in range(3):
        cv.rect(px + int(pw * (0.6 + i * 0.12)), py + int(ph * 0.55),
                int(pw * 0.06), int(ph * 0.18), PAL["gold"])
    # three workers holding a banner
    by = py + int(ph * 0.40)
    cv.rect(px + int(pw * 0.04), by, int(pw * 0.44), int(ph * 0.24),
            PAL["white"])
    cv.frame(px + int(pw * 0.04), by, int(pw * 0.44), int(ph * 0.24),
             PAL["ink"], 1)
    cv.text(px + int(pw * 0.07), by + 2, "TK30,000", 1, PAL["red"])
    for i in range(3):
        fx = px + int(pw * (0.08 + i * 0.14))
        cv.disc(fx, by + int(ph * 0.38), 3, PAL["skin"])
        cv.rect(fx - 3, by + int(ph * 0.42), 6, int(ph * 0.22),
                PAL["blue"] if i % 2 == 0 else PAL["teal"])


def scene_voyager(cv, px, py, pw, ph):
    """Voyager 1 in deep space, one light-day out."""
    cv.rect(px, py, pw, ph, PAL["ink"])
    for sx, sy in ((6, 8), (18, 20), (32, 6), (48, 16), (64, 8),
                   (80, 22), (92, 10), (12, 70), (40, 80), (70, 72)):
        cv.set(px + int(sx * pw / 100), py + int(sy * ph / 100),
               PAL["white"])
    # the probe: gold body, big dish, long boom
    cx, cy = px + int(pw * 0.5), py + ph // 2
    cv.rect(cx - 12, cy - 5, 24, 10, PAL["gold"])
    cv.segment(cx - 12, cy, cx - 30, cy - 10, PAL["steel"], 2)
    cv.disc(cx - 30, cy - 10, 3, PAL["white"])
    cv.segment(cx + 12, cy, cx + 34, cy + 8, PAL["white"], 1)
    cv.disc(cx + 34, cy + 8, 2, PAL["flame"])
    # signal rings travelling home
    for r in (10, 16, 22):
        cv.ring(cx - 34, cy - 12, r, PAL["sky"])
    # a small Earth, far behind
    cv.disc(px + int(pw * 0.06), py + int(ph * 0.82), 4, PAL["sea"])
    cv.disc(px + int(pw * 0.06) - 1, py + int(ph * 0.82) - 1, 2,
            PAL["green"])


def scene_haiti(cv, px, py, pw, ph):
    """A helicopter over a hillside mansion in Haiti."""
    cv.rect(px, py, pw, ph, PAL["sky"])
    # green hill
    hy = py + int(ph * 0.55)
    cv.polygon([(px, py + ph), (px, hy + 8),
                (px + int(pw * 0.5), hy - 6),
                (px + pw, hy + 4), (px + pw, py + ph)], PAL["green"])
    # the mansion on the hill
    hx = px + int(pw * 0.55)
    cv.rect(hx, hy - 14, int(pw * 0.3), 14, PAL["white"])
    cv.rect(hx + 2, hy - 20, int(pw * 0.12), 6, PAL["red"])
    cv.rect(hx + int(pw * 0.08), hy - 8, 5, 8, PAL["blue"])
    cv.rect(hx + int(pw * 0.2), hy - 8, 5, 8, PAL["blue"])
    # helicopter above, rotor spinning
    cx, cy = px + int(pw * 0.22), py + int(ph * 0.22)
    cv.rect(cx - 12, cy - 4, 24, 8, PAL["dark"])
    cv.segment(cx - 18, cy - 7, cx + 18, cy - 7, PAL["ink"], 2)
    cv.segment(cx + 12, cy, cx + 20, cy + 6, PAL["ink"], 2)
    # smoke rising from the mansion
    cv.disc(hx + int(pw * 0.15), hy - 26, 5, PAL["grey"])
    cv.disc(hx + int(pw * 0.2), hy - 34, 4, PAL["grey"])
    cv.disc(hx + int(pw * 0.12), hy - 40, 3, PAL["white"])


def scene_odesa(cv, px, py, pw, ph):
    """Odesa at night: skyline, a blast, and a shield of interceptors."""
    cv.rect(px, py, pw, ph, PAL["night"])
    for sx, sy in ((10, 6), (28, 12), (50, 5), (72, 10), (90, 6)):
        cv.set(px + int(sx * pw / 100), py + int(sy * ph / 100),
               PAL["gold"])
    # skyline with lit windows
    gy = py + int(ph * 0.72)
    for i in range(5):
        bx = px + int(pw * (0.04 + i * 0.19))
        bw = int(pw * 0.15)
        bh = int(ph * (0.28 + (i % 3) * 0.08))
        cv.rect(bx, gy - bh, bw, bh, PAL["tower"])
        cv.rect(bx + 3, gy - bh + 4, 3, 4, PAL["window"])
    cv.rect(px, gy, pw, ph - int(ph * 0.72), PAL["ground"])
    # blast over the city
    bx, by = px + int(pw * 0.68), py + int(ph * 0.3)
    cv.disc(bx, by, 6, PAL["orange"])
    cv.disc(bx, by, 3, PAL["flame"])
    cv.disc(bx - 10, by + 8, 4, PAL["grey"])
    cv.disc(bx + 10, by - 6, 3, PAL["grey"])
    # interceptor streaks crossing the sky
    cv.segment(px + int(pw * 0.05), py + int(ph * 0.15),
               px + int(pw * 0.3), py + int(ph * 0.4), PAL["white"], 1)
    cv.segment(px + int(pw * 0.35), py + int(ph * 0.08),
               px + int(pw * 0.55), py + int(ph * 0.35), PAL["white"], 1)


def scene_badme(cv, px, py, pw, ph):
    """Two armies face off across a dry border valley."""
    cv.rect(px, py, pw, ph, PAL["tan"])
    cv.disc(px + int(pw * 0.85), py + int(ph * 0.2),
            max(3, ph // 7), PAL["sun"])
    # mountains on both sides
    cv.polygon([(px, py + int(ph * 0.5)), (px + int(pw * 0.25),
                py + int(ph * 0.18)), (px + int(pw * 0.5),
                py + int(ph * 0.5))], PAL["dark"])
    cv.polygon([(px + int(pw * 0.5), py + int(ph * 0.5)),
                (px + int(pw * 0.75), py + int(ph * 0.22)),
                (px + pw, py + int(ph * 0.5))], PAL["dark"])
    # the border line down the middle
    cv.vline(px + pw // 2, py + int(ph * 0.5), int(ph * 0.5),
             PAL["red"], 2)
    # two flags facing each other
    for j, col in enumerate((PAL["green"], PAL["red"])):
        fx = px + int(pw * (0.3 + j * 0.32))
        cv.vline(fx, py + int(ph * 0.52), int(ph * 0.3), PAL["ink"], 2)
        cv.rect(fx + 2, py + int(ph * 0.52), int(pw * 0.1),
                int(ph * 0.12), col)
    # tents at the foot of the valley
    for i in range(3):
        tx = px + int(pw * (0.08 + i * 0.12))
        cv.polygon([(tx, py + ph - 4), (tx + 8, py + int(ph * 0.78)),
                    (tx + 16, py + ph - 4)], PAL["white"])


def scene_gta(cv, px, py, pw, ph):
    """Neon city night: the GTA VI launch."""
    cv.rect(px, py, pw, ph, PAL["night"])
    # neon skyline
    for i in range(6):
        bx = px + int(pw * (0.02 + i * 0.16))
        bw = int(pw * 0.12)
        bh = int(ph * (0.4 + (i % 3) * 0.12))
        cv.rect(bx, py + ph - bh - int(ph * 0.14), bw, bh,
                PAL["tower"])
        cv.rect(bx + 2, py + ph - bh - int(ph * 0.14) + 4, 3, 4,
                PAL["pink"] if i % 2 else PAL["gold"])
    cv.rect(px, py + ph - int(ph * 0.14), pw, int(ph * 0.14),
            PAL["ground"])
    # big neon VI in the sky
    vx = px + int(pw * 0.38)
    vy = py + int(ph * 0.12)
    cv.segment(vx, vy, vx + 8, vy + 14, PAL["pink"], 3)
    cv.segment(vx + 8, vy + 14, vx + 16, vy, PAL["pink"], 3)
    cv.segment(vx + 24, vy, vx + 24, vy + 14, PAL["pink"], 3)
    # a game controller below the sign
    cx, cy = px + int(pw * 0.5), py + int(ph * 0.68)
    cv.rect(cx - 16, cy - 4, 32, 10, PAL["white"])
    cv.disc(cx - 8, cy + 2, 3, PAL["red"])
    cv.disc(cx + 8, cy + 2, 3, PAL["blue"])


def scene_bank(cv, px, py, pw, ph):
    """A bank with columns and a rising rate chart."""
    cv.rect(px, py, pw, ph, PAL["paper"])
    # bank front: pediment and four columns
    bx = px + int(pw * 0.08)
    bw = int(pw * 0.5)
    cv.polygon([(bx, py + int(ph * 0.25)), (bx + bw // 2, py + 4),
                (bx + bw, py + int(ph * 0.25))], PAL["dark"])
    for i in range(4):
        cx = bx + int(bw * (0.08 + i * 0.24))
        cv.rect(cx, py + int(ph * 0.28), 5, int(ph * 0.5), PAL["ink"])
    cv.rect(bx, py + int(ph * 0.78), bw, 4, PAL["ink"])
    # pound sign on the pediment: a gold coin
    cv.disc(bx + bw // 2, py + int(ph * 0.14), 5, PAL["gold"])
    cv.ring(bx + bw // 2, py + int(ph * 0.14), 5, PAL["ink"])
    # rising chart on the right
    ox = px + int(pw * 0.66)
    oy = py + int(ph * 0.7)
    cv.segment(ox, oy, ox + int(pw * 0.08), oy - int(ph * 0.18),
               PAL["red"], 2)
    cv.segment(ox + int(pw * 0.08), oy - int(ph * 0.18),
               ox + int(pw * 0.16), oy - int(ph * 0.22), PAL["red"], 2)
    cv.segment(ox + int(pw * 0.16), oy - int(ph * 0.22),
               ox + int(pw * 0.28), oy - int(ph * 0.45), PAL["red"], 2)
    cv.disc(ox + int(pw * 0.28), oy - int(ph * 0.45), 3, PAL["red"])


def scene_sanctions(cv, px, py, pw, ph):
    """Australia stamped on a map: sanctions over settlements."""
    cv.rect(px, py, pw, ph, PAL["sky"])
    # simplified Australia
    ax, ay = px + int(pw * 0.28), py + int(ph * 0.18)
    cv.polygon([(ax, ay + 8), (ax + 10, ay), (ax + 34, ay + 2),
                (ax + 44, ay + 10), (ax + 38, ay + 20),
                (ax + 20, ay + 24), (ax + 4, ay + 18)], PAL["tan"])
    cv.frame(ax - 2, ay - 2, 50, 30, PAL["ink"], 1)
    # a red stamp across the lower half
    sx = px + int(pw * 0.12)
    sy = py + int(ph * 0.62)
    cv.frame(sx, sy, int(pw * 0.76), int(ph * 0.3), PAL["red"], 2)
    cv.text(sx + 4, sy + 3, "SANCTIONED", 1, PAL["red"])
    # a gavel above
    gx, gy = px + int(pw * 0.72), py + int(ph * 0.12)
    cv.rect(gx, gy, 14, 5, PAL["table"])
    cv.segment(gx + 7, gy + 5, gx + 7, gy + 16, PAL["table"], 2)


def scene_cyclone(cv, px, py, pw, ph):
    """Cyclone Akvan spiralling over the Bay of Bengal."""
    cv.rect(px, py, pw, ph, PAL["sea"])
    cx, cy = px + int(pw * 0.5), py + int(ph * 0.45)
    # spiral arms
    for r in (6, 12, 18, 24):
        for a in range(0, 270, 6):
            rad = math.radians(a + r * 8)
            cv.set(cx + int(r * math.cos(rad)),
                   cy + int(r * 0.8 * math.sin(rad)), PAL["white"])
    cv.disc(cx, cy, 4, PAL["gold"])
    # coastline at the bottom with rain
    cv.rect(px, py + int(ph * 0.82), pw, int(ph * 0.18), PAL["land"])
    for i in range(6):
        rx = px + int(pw * (0.08 + i * 0.15))
        cv.segment(rx, py + int(ph * 0.55), rx - 3,
                   py + int(ph * 0.68), PAL["sky"], 1)
    # warning triangle
    tx, ty = px + int(pw * 0.06), py + int(ph * 0.08)
    cv.polygon([(tx, ty + 12), (tx + 7, ty), (tx + 14, ty + 12)],
               PAL["gold"])
    cv.text(tx + 5, ty + 4, "!", 1, PAL["ink"])


# ---- World map: coarse continents in lon/lat, pins for the leads ----
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80),
     (-85, 70), (-75, 62), (-60, 55), (-55, 47), (-70, 42),
     (-75, 35), (-80, 26), (-85, 20), (-90, 15), (-95, 18),
     (-105, 22), (-115, 28), (-125, 40), (-125, 50), (-140, 60),
     (-155, 58), (-165, 60)],
    # South America
    [(-80, 10), (-75, 5), (-60, 5), (-50, 0), (-40, -5), (-35, -10),
     (-40, -20), (-48, -28), (-55, -35), (-65, -40), (-70, -50),
     (-73, -40), (-70, -30), (-75, -18), (-80, -5)],
    # Africa
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (32, 31),
     (35, 28), (40, 15), (48, 11), (51, 10), (45, 0), (40, -10),
     (35, -20), (30, -30), (20, -35), (15, -25), (12, -15), (8, 4),
     (-8, 5), (-15, 10)],
    # Eurasia
    [(-10, 36), (-5, 43), (0, 48), (5, 55), (10, 58), (18, 56),
     (21, 60), (25, 65), (30, 70), (45, 68), (60, 70), (75, 73),
     (90, 75), (110, 76), (130, 72), (150, 70), (170, 67), (178, 65),
     (170, 60), (160, 55), (150, 45), (140, 40), (130, 35),
     (122, 30), (115, 22), (108, 12), (103, 8), (100, 8), (95, 15),
     (90, 22), (85, 20), (80, 10), (75, 8), (70, 20), (65, 25),
     (58, 25), (52, 27), (48, 30), (43, 35), (35, 36), (30, 36),
     (25, 38), (20, 40), (15, 44), (10, 44), (5, 43), (0, 40),
     (-5, 36), (-10, 36)],
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


def draw_map(cv, x, y, w, h):
    """Stylised world map with numbered pins for the 13 leads."""
    cv.rect(x, y, w, h, PAL["sky"])
    cv.frame(x, y, w, h, PAL["ink"], 2)

    def proj(lon, lat):
        px = x + int((lon + 170) / 360.0 * w)
        py = y + int((80 - lat) / 140.0 * h)
        return (px, py)

    for poly in CONTINENTS:
        cv.polygon([proj(lon, lat) for lon, lat in poly], PAL["land"])
    cv.text(x + int(w * 0.05), y + int(h * 0.55), "N. AMERICA", 1,
            PAL["dark"])
    cv.text(x + int(w * 0.24), y + int(h * 0.72), "S. AMERICA", 1,
            PAL["dark"])
    cv.text(x + int(w * 0.47), y + int(h * 0.55), "AFRICA", 1,
            PAL["dark"])
    cv.text(x + int(w * 0.46), y + int(h * 0.12), "EUROPE", 1,
            PAL["dark"])
    cv.text(x + int(w * 0.68), y + int(h * 0.32), "ASIA", 1,
            PAL["dark"])
    cv.text(x + int(w * 0.82), y + int(h * 0.72), "OCEANIA", 1,
            PAL["dark"])
    for num, lon, lat in PINS:
        px, py = proj(lon, lat)
        cv.disc(px, py, 7, PAL["red"])
        cv.ring(px, py, 7, PAL["ink"])
        label = str(num)
        cv.text(px - (3 if num < 10 else 6), py - 3, label, 1,
                PAL["white"])


# ---- The 42 stories: 13 illustrated leads, 29 briefs ----
# (number, region/field tag, scene, headline, deck)
LEADS = [
    (1, "MIDDLE EAST - WAR", scene_gulf,
     "IRAN DRONES HIT US BASES IN THE GULF",
     "KUWAIT AND BAHRAIN SAY DEFENCES SHOT THE DRONES DOWN. "
     "NO CASUALTIES REPORTED."),
    (2, "ASIA - DIPLOMACY", scene_summit,
     "XI GREETS TRUMP AS APEC OPENS",
     "SHENZHEN HOSTS THE SUMMIT. PUTIN IS THERE TOO. "
     "THE FIRST TRILATERAL MEETS THURSDAY."),
    (3, "CLIMATE", scene_cop,
     "COP31 SPLIT ON FOSSIL FUELS",
     "INDONESIA SAYS PHASE DOWN, NOT PHASE OUT, TO 2060. "
     "THE DRAFT DEAL IS STILL UNAGREED."),
    (4, "MIDDLE EAST - TRUCE", scene_gaza,
     "GAZA TRUCE MAY COLLAPSE, BOARD WARNS",
     "A CEASEFIRE THAT DELIVERS NOTHING VISIBLE CANNOT LAST, "
     "THE BOARD TELLS THE UN."),
    (5, "ASIA - LABOUR", scene_bangladesh,
     "BANGLADESH WAGE PROTESTS SHUT 535 FACTORIES",
     "WORKERS WANT TK30,000 A MONTH, UP FROM TK12,500. "
     "300 ARRESTED IN TWO DAYS."),
    (6, "SCIENCE - SPACE", scene_voyager,
     "VOYAGER 1, ONE LIGHT-DAY FROM EARTH",
     "25.9BN KM OUT, THE PROBE IS THE FIRST HUMAN OBJECT "
     "A LIGHT-DAY AWAY. SIGNALS TAKE A DAY."),
    (7, "AMERICAS - SECURITY", scene_haiti,
     "BUKELE BLASTS GANG BOSS MANSION",
     "HELICOPTERS HIT JEFF LAROSE'S HILLSIDE HOME IN HAITI "
     "ON THE VERTIERES ANNIVERSARY."),
    (8, "EUROPE - WAR", scene_odesa,
     "RUSSIAN STRIKES KILL AT LEAST 5 IN UKRAINE",
     "ODESA HIT: 4 DEAD, 13 HURT. UKRAINE SHOT DOWN "
     "126 OF 141 DRONES OVERNIGHT."),
    (9, "AFRICA - SECURITY", scene_badme,
     "ETHIOPIA AND ERITREA MASS TROOPS",
     "ARMIES FACE OFF NEAR BADME. MONITORS FEAR OUTRIGHT "
     "WAR IN THE HORN OF AFRICA."),
    (10, "CULTURE - GAMES", scene_gta,
     "GTA VI IS OUT AFTER 13 YEARS",
     "NZ PLAYS FIRST AT MIDNIGHT. CRITICS GIVE 99/100. "
     "NO PC VERSION."),
    (11, "ECONOMY", scene_bank,
     "WAR LENGTH TO SET BANK RATES",
     "BAILEY: A LONG IRAN WAR MEANS HIGHER RATES. "
     "UK INFLATION 3.6%."),
    (12, "OCEANIA - DIPLOMACY", scene_sanctions,
     "AUSTRALIA SANCTIONS SETTLER LEADER WEISS",
     "3 PEOPLE, 4 GROUPS BLACKLISTED OVER "
     "WEST BANK SETTLEMENTS."),
    (13, "ASIA - WEATHER", scene_cyclone,
     "CYCLONE AKVAN NEARS INDIA'S EAST COAST",
     "ODISHA SHUTS SCHOOLS. LANDFALL FRIDAY, "
     "WINDS TO 110 KM/H."),
]

BRIEFS = [
    "YEMEN: GULF STATES ALSO SHOT DOWN MISSILES AND DRONES FROM HOUTHI ALLIES.",
    "WEST BANK: BRITAIN SANCTIONED 8 SETTLEMENT FIRMS ON TUESDAY.",
    "GAZA: ISRAEL'S KATZ SAYS NO WITHDRAWAL UNTIL HAMAS IS DISMANTLED.",
    "MYANMAR: WORLD COURT RULES THURSDAY ON THE ROHINGYA GENOCIDE CASE.",
    "USA: HOUSE DEMOCRATS NOMINATE JEFFRIES FOR SPEAKER, 251-11.",
    "USA: GAO SAYS 4 TOP AI MODELS DREW UP MASS-CASUALTY ATTACK PLANS.",
    "USA: SENATORS INTRODUCE BILL TO FORCE STEALTH BOTS TO IDENTIFY.",
    "USA: OUTAGE WAVE REACHES THE NSA AFTER APPLE, BANKS, AIRLINES.",
    "USA: LA AND LONG BEACH PORT TALKS STALL; 250 WATCHMEN MAY STRIKE.",
    "USA: BLAST AT CLEAN HARBORS WASTE PLANT NEAR HOUSTON; 1 IN HOSPITAL.",
    "USA: PEW: TWO-THIRDS DISAPPROVE OF TRUMP ON THE RUSSIA-UKRAINE WAR.",
    "RELIGION: PEW: MUSLIMS TO PASS CHRISTIANS AS TOP FAITH BY 2035.",
    "UKRAINE: 1,000+ RUSSIAN ATTACKS ON ENERGY SITES SINCE SEPTEMBER.",
    "UK: INFLATION HIT 3.6% IN OCTOBER, HIGHEST IN A YEAR.",
    "COP31: 11 COUNTRIES UNVEIL FOSSIL-FUEL PHASE-OUT ROADMAPS.",
    "COP31: TALKS CLOSE FRIDAY 20 NOV IN ANTALYA, TURKIYE.",
    "APEC: PUTIN EXPECTS BIG BENEFIT FROM THURSDAY'S TRILATERAL.",
    "APEC: XI URGES FREE TRADE AND HITS OUT AT PROTECTIONISM.",
    "GULF: FIRST IRANIAN ATTACK ON KUWAIT SINCE SEPTEMBER.",
    "BANGLADESH: WAGE BOARD MEETS AGAIN ON 23 NOV.",
    "BANGLADESH: 300 ARRESTED AS PROTESTS TURN VIOLENT.",
    "ETHIOPIA: ERITREA DENIES CROSSING INTO TIGRAY.",
    "HAITI: 223RD ANNIVERSARY OF THE BATTLE OF VERTIERES.",
    "HAITI: UN-BACKED FORCE SAYS IT TOOK NO PART IN THE RAID.",
    "GTA VI: US UNLOCKS AT MIDNIGHT EASTERN; NO PC VERSION AT LAUNCH.",
    "GTA VI: LEAVE REQUESTS UP 32% AROUND 19 NOV, SAYS REMOTE.",
    "CYCLONE: LANDFALL DUE FRIDAY NOON, WINDS TO 110 KM/H.",
    "CYCLONE: ANDHRA ON RED ALERT FOR 19-20 NOV.",
    "SPACE: A RADIO SIGNAL TO VOYAGER 1 NOW TAKES A FULL DAY EACH WAY.",
]


def lead_card(cv, x, y, w, h, num, tag, scene, headline, deck):
    ink = PAL["ink"]
    cv.rect(x, y, w, h, PAL["paper"])
    cv.frame(x, y, w, h, ink, 2)
    cv.text(x + 8, y + 5, str(num) + " " + tag, 1, PAL["red"])
    scene(cv, x + 6, y + 14, w - 12, 46)
    hy = y + 64
    used = cv.wrapped(x + w // 2, hy, headline, 2, ink, w - 16,
                      leading=2, max_lines=2)
    cv.wrapped(x + w // 2, hy + used + 4, deck, 1, PAL["dark"],
               w - 16, leading=2, max_lines=2)


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
    cv.rect(24, 94, WIDTH - 48, 22, ink)
    cv.centered(WIDTH // 2, 100,
                "42 STORIES - 7 REGIONS - 8 FIELDS - 13 ILLUSTRATED",
                2, PAL["cream"])

    # Region strip and day-in-numbers strip.
    cv.centered(WIDTH // 2, 122,
                "MIDDLE EAST - ASIA - EUROPE - AFRICA - "
                "N. AMERICA - CARIBBEAN - OCEANIA", 1, PAL["dark"])
    cv.centered(WIDTH // 2, 138,
                "5 KILLED IN ODESA - 535 FACTORIES SHUT - 25.9BN KM - "
                "141 DRONES - 99/100 - 3.6% - 251-11", 1, ink)

    # Lead cards: three rows of three, then a row of four.
    rows = [(156, 325, LEADS[0:3]), (284, 325, LEADS[3:6]),
            (412, 325, LEADS[6:9]), (540, 242, LEADS[9:13])]
    for ry, cw, cards in rows:
        gap = 8 if len(cards) == 3 else 8
        x = 16
        for num, tag, scene, headline, deck in cards:
            lead_card(cv, x, ry, cw, 124, num, tag, scene, headline,
                      deck)
            x += cw + gap

    # World map with numbered pins.
    cv.centered(WIDTH // 2, 668, "WHERE IT HAPPENED - 13 LEADS PINNED",
                1, ink)
    draw_map(cv, 24, 680, WIDTH - 48, 116)

    # Briefs 14-42 in two columns.
    cv.centered(WIDTH // 2, 802, "ALSO ON WEDNESDAY 18 NOVEMBER", 2,
                ink)
    cv.hline(24, 822, WIDTH - 48, ink, 1)
    left = BRIEFS[:15]
    right = BRIEFS[15:]
    for i, brief in enumerate(left):
        cv.text(24, 830 + i * 10, str(14 + i) + ". " + brief, 1, ink)
    for i, brief in enumerate(right):
        cv.text(524, 830 + i * 10, str(29 + i) + ". " + brief, 1, ink)

    # Footer: date check and sources.
    cv.hline(24, 976, WIDTH - 48, ink, 2)
    cv.wrapped(WIDTH // 2, 982,
               "DATE CHECK - LEFT OUT BECAUSE FIRST REPORTED 17 NOV: "
               "PELTOLA WINS ALASKA SENATE SEAT; NVIDIA'S $115.8BN "
               "QUARTER; PRAGUE TRAIN CRASH; MONGOLIA'S PRESIDENT "
               "RESIGNS; UKRAINE HITS THE KERCH BRIDGE.",
               1, PAL["red"], WIDTH - 48, leading=2, max_lines=2)
    cv.centered(WIDTH // 2, 1004,
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
