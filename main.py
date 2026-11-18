#!/usr/bin/env python3
"""THE WORLD IN ONE PICTURE: Wednesday 18 November 2026.

A newspaper front page, 1024 by 1024 pixels, drawn with the Python
standard library only. Four stories from Wednesday 18 November 2026:

  * Iran strikes US bases in Kuwait and Bahrain, after the US hit
    Qeshm Island.
  * Ukraine hits the Kerch Bridge for a second day.
  * Xi and Putin meet in Shenzhen ahead of the three-way summit
    with Trump.
  * Mary Peltola wins Alaska and the Democrats take a 56-44
    Senate majority.

Plus a footer with three more items from the day. The program is
deterministic: no clock, no randomness, no network. It writes
entry.png to $MAKEFUN_OUTPUT_DIR when that is set, and beside this
script otherwise.
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
    "sky": (178, 216, 240),
    "night": (38, 52, 96),
    "night2": (70, 80, 140),
    "sea": (38, 110, 180),
    "deep": (24, 80, 150),
    "grey": (120, 120, 118),
    "dark": (70, 70, 68),
    "steel": (150, 158, 165),
    "orange": (240, 120, 20),
    "flame": (255, 176, 32),
    "red": (200, 40, 32),
    "blue": (40, 80, 180),
    "dusk": (232, 150, 90),
    "dusk2": (120, 80, 130),
    "tan": (222, 196, 140),
    "gold": (255, 214, 90),
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
    "white": (255, 255, 255),
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

    def wrapped(self, cx, y, text, scale, color, max_w, leading=4):
        """Draw word-wrapped centered text; return the height used."""
        lines = self.wrap(text, scale, max_w)
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


# ---- Lead scene: drones over the Gulf at night ----
def scene_gulf(cv, px, py, pw, ph):
    ink = PAL["ink"]
    cv.rect(px, py, pw, ph, PAL["night"])
    horizon = py + int(ph * 0.42)
    cv.rect(px, horizon, pw, ph - int(ph * 0.42), PAL["night2"])
    # stars
    for sx, sy in ((30, 18), (90, 40), (150, 14), (220, 34), (300, 16),
                   (380, 38), (450, 20), (500, 44), (60, 66), (260, 62),
                   (410, 66), (520, 70)):
        cv.set(px + sx, py + sy, PAL["gold"])
        cv.set(px + sx + 1, py + sy, PAL["gold"])
    # low moon with craters
    cv.disc(px + pw - 70, py + 52, 26, PAL["moon"])
    cv.disc(px + pw - 78, py + 46, 6, PAL["moonspot"])
    cv.disc(px + pw - 62, py + 60, 4, PAL["moonspot"])
    sea_y = py + int(ph * 0.60)
    cv.rect(px, sea_y, pw, ph - int(ph * 0.60), PAL["deep"])
    # moonlight path on the water
    for wx in range(px + pw - 110, px + pw - 30, 8):
        cv.segment(wx, sea_y + 18, wx + 34, sea_y + 18,
                   (120, 150, 200), 2)
        cv.segment(wx + 8, sea_y + 44, wx + 28, sea_y + 44,
                   (120, 150, 200), 2)
    # tanker: dark hull, lit deck houses, flames midship
    hull_y = sea_y - 26
    cv.rect(px + 40, hull_y, pw - 110, 40, PAL["hull"])
    cv.rect(px + 40, hull_y + 40, pw - 110, 8, ink)
    cv.rect(px + 56, hull_y - 40, 64, 40, PAL["deck"])
    cv.rect(px + pw - 150, hull_y - 58, 74, 58, PAL["deck2"])
    cv.rect(px + pw - 138, hull_y - 52, 12, 12, PAL["gold"])
    cv.rect(px + pw - 118, hull_y - 52, 12, 12, PAL["gold"])
    cv.rect(px + pw - 138, hull_y - 34, 12, 12, PAL["gold"])
    # flames bursting from the deck
    for fx, fh in ((px + 190, 56), (px + 224, 76), (px + 258, 58),
                   (px + 292, 68), (px + 326, 50)):
        cv.polygon([(fx - 18, hull_y), (fx, hull_y - fh),
                    (fx + 18, hull_y)], PAL["orange"])
        cv.polygon([(fx - 10, hull_y), (fx, hull_y - fh + 22),
                    (fx + 10, hull_y)], PAL["flame"])
    # black smoke rolling up
    cv.disc(px + 230, hull_y - 66, 16, ink)
    cv.disc(px + 258, hull_y - 84, 18, PAL["dark"])
    cv.disc(px + 228, hull_y - 96, 13, PAL["dark"])
    cv.disc(px + 262, hull_y - 108, 11, PAL["grey"])
    # two drones diving in from the sky, bright heads, dotted trails
    cv.segment(px + 60, py + 20, px + 170, py + 108, PAL["white"], 2)
    cv.disc(px + 172, py + 110, 7, PAL["flame"])
    cv.segment(px + 330, py + 14, px + 420, py + 96, PAL["white"], 2)
    cv.disc(px + 422, py + 98, 7, PAL["flame"])


# ---- Scene: the Kerch Bridge, broken ----
def scene_kerch(cv, px, py, pw, ph):
    cv.rect(px, py, pw, ph, PAL["sky"])
    water_y = py + int(ph * 0.62)
    cv.rect(px, water_y, pw, ph - int(ph * 0.62), PAL["sea"])
    cv.disc(px + pw - 52, py + 34, 22, PAL["gold"])
    deck_y = py + int(ph * 0.44)
    # left span stands, right span stands, the middle is gone
    cv.rect(px + 8, deck_y, pw // 2 - 52, 12, PAL["steel"])
    cv.rect(px + pw // 2 + 40, deck_y, pw // 2 - 48, 12, PAL["steel"])
    # arch over the left span
    cv.segment(px + 30, deck_y, px + pw // 4, deck_y - 64,
               PAL["dark"], 4)
    cv.segment(px + pw // 4, deck_y - 64, px + pw // 2 - 52, deck_y,
               PAL["dark"], 4)
    # right tower leaning after the blast
    cv.segment(px + pw - 96, deck_y, px + pw - 66, deck_y - 78,
               PAL["dark"], 6)
    # deck slabs tumbling into the strait
    cv.polygon([(px + pw // 2 - 44, deck_y), (px + pw // 2 - 12, deck_y),
                (px + pw // 2 - 22, deck_y + 42),
                (px + pw // 2 - 50, deck_y + 28)], PAL["steel"])
    cv.polygon([(px + pw // 2 + 6, deck_y + 8), (px + pw // 2 + 30, deck_y + 4),
                (px + pw // 2 + 22, deck_y + 34),
                (px + pw // 2 + 2, deck_y + 30)], PAL["dark"])
    # smoke from the gap
    cv.disc(px + pw // 2 - 6, deck_y - 20, 14, PAL["dark"])
    cv.disc(px + pw // 2 + 8, deck_y - 40, 16, PAL["grey"])
    cv.disc(px + pw // 2 - 2, deck_y - 58, 12, PAL["grey"])
    # splash rings where the span fell
    for rx, ry, rr in ((pw // 2 - 18, water_y + 34, 22),
                       (pw // 2 + 14, water_y + 52, 16)):
        for a in range(0, 360, 8):
            cv.set(px + rx + int(rr * math.cos(math.radians(a))),
                   py + ry + int(rr * 0.55 * math.sin(math.radians(a))),
                   PAL["white"])
    # waves
    for wx in range(px + 8, px + pw - 8, 40):
        cv.segment(wx, water_y + 66, wx + 22, water_y + 66,
                   PAL["white"], 2)


# ---- Scene: three flags over the Shenzhen skyline ----
def scene_summit(cv, px, py, pw, ph):
    ink = PAL["ink"]
    cv.rect(px, py, pw, ph, PAL["dusk"])
    cv.rect(px, py + int(ph * 0.40), pw, ph - int(ph * 0.40),
            PAL["dusk2"])
    cv.disc(px + pw - 56, py + 30, 18, PAL["sun"])
    # skyline towers with lit windows
    towers = [(6, 96, 52, 100), (62, 66, 46, 130), (112, 104, 54, 92),
              (170, 56, 50, 140), (224, 88, 46, 108), (274, 70, 18, 126)]
    for tx, ty, tw, th in towers:
        base_y = py + ph - th - 46
        cv.rect(px + tx, base_y, tw, th, PAL["tower"])
        for wy in range(base_y + 10, py + ph - 56, 20):
            for wx in range(px + tx + 7, px + tx + tw - 7, 16):
                cv.rect(wx, wy, 6, 8, PAL["window"])
    ground_y = py + ph - 46
    cv.rect(px, ground_y, pw, 46, PAL["ground"])
    # three flags on poles: China red, US stripes, Russia white-blue-red
    flag_x = [px + 34, px + pw // 2 - 22, px + pw - 84]
    flag_cols = [(PAL["red"], PAL["red"], PAL["red"]),
                 (PAL["red"], PAL["white"], PAL["blue"]),
                 (PAL["white"], PAL["blue"], PAL["red"])]
    for fx, cols in zip(flag_x, flag_cols):
        cv.vline(fx, py + 12, 62, ink, 3)
        for i, col in enumerate(cols):
            cv.rect(fx + 3, py + 12 + i * 11, 40, 11, col)
        # small stars on the all-red flag
        if cols[0] == PAL["red"] and cols[1] == PAL["red"]:
            for sx, sy in ((8, 16), (20, 20), (28, 28)):
                cv.set(fx + 3 + sx, py + 12 + sy, PAL["gold"])
    # three leaders seated at one table
    for fx in (px + 56, px + pw // 2 - 16, px + pw - 108):
        cv.disc(fx + 18, ground_y + 6, 8, PAL["skin"])
        cv.rect(fx + 7, ground_y + 15, 22, 24, ink)
    cv.rect(px + 40, ground_y + 32, pw - 80, 5, PAL["table"])


# ---- Scene: the Senate count, 56 to 44 ----
def scene_senate(cv, px, py, pw, ph):
    ink = PAL["ink"]
    cv.rect(px, py, pw, ph, PAL["paper"])
    # ballot box with a big check
    box_x, box_y = px + pw // 2 - 52, py + 12
    cv.rect(box_x, box_y, 104, 64, PAL["box"])
    cv.rect(box_x - 10, box_y - 12, 124, 14, ink)
    cv.rect(box_x + 36, box_y - 12, 32, 4, PAL["cream"])
    cv.segment(box_x + 22, box_y + 34, box_x + 44, box_y + 56,
               PAL["red"], 7)
    cv.segment(box_x + 44, box_y + 56, box_x + 84, box_y + 12,
               PAL["red"], 7)
    cv.centered(px + pw // 2, box_y + 82, "ALASKA DECIDES", 2, ink)
    # the tally bar: 56 blue, 44 red
    bar_y = py + ph - 58
    bar_w = pw - 40
    dem_w = int(bar_w * 56 / 100)
    cv.rect(px + 20, bar_y, dem_w, 30, PAL["blue"])
    cv.rect(px + 20 + dem_w, bar_y, bar_w - dem_w, 30, PAL["red"])
    for t in range(2):
        cv.hline(px + 20, bar_y + t, bar_w, ink)
        cv.hline(px + 20, bar_y + 29 - t, bar_w, ink)
        cv.vline(px + 20 + t, bar_y, 30, ink)
        cv.vline(px + 20 + bar_w - 1 - t, bar_y, 30, ink)
    cv.text(px + 30, bar_y + 8, "DEM 56", 2, PAL["white"])
    cv.text(px + 20 + dem_w + 12, bar_y + 8, "GOP 44", 2, PAL["white"])


def lead_panel(cv, px, py, pw, ph, scene, headline, caption):
    """Wide panel: picture on the left, headline and caption right."""
    ink = PAL["ink"]
    cv.rect(px, py, pw, ph, PAL["paper"])
    cv.frame(px, py, pw, ph, ink, 3)
    scene(cv, px + 6, py + 6, 540, ph - 12)
    tx = px + 540 + 24
    tw = pw - 540 - 36
    hy = py + 34
    used = cv.wrapped(tx + tw // 2, hy, headline, 3, ink, tw)
    cv.wrapped(tx + tw // 2, hy + used + 22, caption, 2, ink, tw,
               leading=6)


def panel(cv, px, py, pw, ph, scene, headline, caption):
    """Square panel: picture on top, headline and caption below."""
    ink = PAL["ink"]
    cv.rect(px, py, pw, ph, PAL["paper"])
    cv.frame(px, py, pw, ph, ink, 3)
    scene_h = int(ph * 0.50)
    scene(cv, px + 6, py + 6, pw - 12, scene_h)
    hy = py + 6 + scene_h + 14
    used = cv.wrapped(px + pw // 2, hy, headline, 3, ink, pw - 28)
    cv.wrapped(px + pw // 2, hy + used + 12, caption, 2, ink,
               pw - 28, leading=5)


def masthead(cv):
    ink = PAL["ink"]
    cv.centered(WIDTH // 2, 28, "THE WORLD IN ONE PICTURE", 5, ink)
    cv.hline(24, 94, WIDTH - 48, ink, 3)
    cv.centered(WIDTH // 2, 106, "WEDNESDAY 18 NOVEMBER 2026", 4, ink)
    cv.hline(24, 150, WIDTH - 48, ink, 3)


def footer(cv):
    ink = PAL["ink"]
    y0 = 862
    cv.hline(24, y0, WIDTH - 48, ink, 3)
    cv.centered(WIDTH // 2, y0 + 12, "ALSO IN THE NEWS", 3, ink)
    items = [
        "- EBOLA IN DR CONGO PASSES 11,000 CASES",
        "- US LOSES MEASLES-FREE STATUS AFTER 26 YEARS",
        "- RUSSIAN MILITARY PLANE CRASHES IN SIBERIA: 19 DEAD",
    ]
    for i, item in enumerate(items):
        cv.text(48, y0 + 52 + i * 26, item, 2, ink)


def main():
    cv = Canvas(WIDTH, HEIGHT)
    ink = PAL["ink"]
    cv.rect(0, 0, WIDTH, HEIGHT, PAL["cream"])
    cv.frame(0, 0, WIDTH, HEIGHT, ink, 8)
    masthead(cv)
    lead_panel(cv, 24, 166, 976, 312, scene_gulf,
               "IRAN STRIKES US BASES IN KUWAIT AND BAHRAIN",
               "TEHRAN SAYS IT TARGETED ALI AL SALEM AIR BASE "
               "AFTER US JETS HIT QESHM ISLAND.")
    panel(cv, 24, 494, 312, 352, scene_kerch, "KERCH BRIDGE HIT AGAIN",
          "UKRAINE STRIKES THE CRIMEA LINK FOR A SECOND DAY; "
          "PART OF THE ROAD SPAN FALLS.")
    panel(cv, 356, 494, 312, 352, scene_summit, "XI AND PUTIN MEET",
          "THE TWO LEADERS TALK IN SHENZHEN AHEAD OF THURSDAY'S "
          "THREE-WAY SUMMIT WITH TRUMP.")
    panel(cv, 688, 494, 312, 352, scene_senate, "DEMOCRATS TAKE SENATE",
          "MARY PELTOLA WINS ALASKA; DEMOCRATS HOLD A 56-44 "
          "MAJORITY IN THE SENATE.")
    footer(cv)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if outdir:
        os.makedirs(outdir, exist_ok=True)
        write_png(cv, os.path.join(outdir, "entry.png"))
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        write_png(cv, os.path.join(here, "entry.png"))


if __name__ == "__main__":
    main()
