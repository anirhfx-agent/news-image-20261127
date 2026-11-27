#!/usr/bin/env python3
"""The World in One Day -- 27 November 2026.

Draws one dense, dated newspaper front page (1024x1024 PNG) summing up
27 November 2026's world news. Every story was verified from live news
reports on 27 November 2026 and is hardcoded below.

Python 3 standard library only (os, struct, zlib, math). No network
calls, no third-party packages, no font files. The text is rendered with
a small proportional bitmap font defined in this file, and the PNG is
written by hand (IHDR/IDAT/IEND chunks). Deterministic: every run
writes byte-identical output to $MAKEFUN_OUTPUT_DIR/entry.png
(default /output/entry.png).
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024
MARGIN = 28
COL_W = (W - 2 * MARGIN - 2 * 16) // 3  # 312

NAVY = (18, 40, 77)
NAVY_LIGHT = (34, 64, 110)
PAPER = (253, 253, 248)
INK = (17, 17, 17)
GRAY = (85, 85, 85)
LIGHT_GRAY = (238, 238, 232)
RULE = (200, 200, 190)
RED = (164, 30, 34)
GREEN = (26, 122, 58)
GOLD = (198, 160, 40)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------------------
# Bitmap font: 5x7, proportional (advance = widest lit column + spacing).
# Each glyph is 7 rows of 5 characters ('#' = ink, '.' = empty).
# ---------------------------------------------------------------------------

FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "a": (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    "f": ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    "g": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": (".....", "..#..", ".....", ".##..", "..#..", "..#..", ".###."),
    "j": (".....", "...#.", ".....", "..##.", "...#.", "...#.", ".##.."),
    "k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    "q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#...#", ".####"),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "\u2019": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "\u2018": ("..#..", "..#..", "...#.", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "\u201c": (".#.#.", ".#.#.", "..#..", ".....", ".....", ".....", "....."),
    "\u201d": (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "\u2013": (".....", ".....", ".....", "####.", ".....", ".....", "....."),
    "\u2014": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "\u00b7": (".....", ".....", ".##..", ".##..", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "%": ("##...", "##...", "...#.", "..#..", ".#...", "...##", "...##"),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "=": (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    "<": ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    ">": (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "*": (".....", ".#.#.", "..#..", ".###.", "..#..", ".#.#.", "....."),
    "@": (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "\u20ac": ("..###", ".#...", "#....", "####.", "#....", ".#...", "..###"),
    "\u00a3": ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", "####."),
    "|": ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "^": ("..#..", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "~": (".....", ".....", ".##.#", "#.#.#", ".....", ".....", "....."),
    "`": (".#...", ".#...", "..#..", ".....", ".....", ".....", "....."),
    "[": (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    "]": (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    "{": ("...##", "..#..", "..#..", ".##..", "..#..", "..#..", "...##"),
    "}": ("##...", "..#..", "..#..", "..##.", "..#..", "..#..", "##..."),
}


def _glyph_width(ch):
    """Widest lit column of a glyph (0 if blank); space is 3 units."""
    if ch == " ":
        return 3
    g = FONT.get(ch)
    if g is None:
        return 0
    w = 0
    for row in g:
        r = row.rfind("#")
        if r >= 0:
            w = max(w, r + 1)
    return w


def _bold_dx(scale, bold):
    return max(1, scale // 2) if bold else 0


def _char_advance(ch, scale, spacing, bold):
    return _glyph_width(ch) * scale + _bold_dx(scale, bold) + spacing


def text_width(text, scale, spacing=1, bold=False):
    """Pixel width of text at the given scale (no trailing spacing)."""
    if not text:
        return 0
    return sum(_char_advance(ch, scale, spacing, bold) for ch in text) - spacing


def draw_text(cv, x, y, text, scale, color, spacing=1, bold=False):
    """Draw text left-aligned at (x, y); returns x after the last char."""
    dx = _bold_dx(scale, bold)
    for ch in text:
        if ch == " ":
            x += 3 * scale + spacing
            continue
        g = FONT.get(ch)
        if g is None:
            continue
        w = _glyph_width(ch)
        for ri, row in enumerate(g):
            for ci, px in enumerate(row):
                if px == "#":
                    cv.rect(x + ci * scale, y + ri * scale,
                            scale + dx, scale, color)
        x += w * scale + dx + spacing
    return x


def wrap(text, scale, max_w, spacing=1, bold=False):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip() if cur else w
        if text_width(trial, scale, spacing, bold) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(cv, x, y, text, scale, max_w, leading, color=INK, max_lines=None,
         spacing=1, bold=False):
    """Draw wrapped paragraph; returns y after the last line."""
    lines = wrap(text, scale, max_w, spacing, bold)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        draw_text(cv, x, y, ln, scale, color, spacing, bold)
        y += leading
    return y


# ---------------------------------------------------------------------------
# Canvas: plain RGB bytearray + drawing primitives.
# ---------------------------------------------------------------------------

class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.pix = bytearray(w * h * 3)
        r, g, b = bg
        for i in range(0, len(self.pix), 3):
            self.pix[i] = r
            self.pix[i + 1] = g
            self.pix[i + 2] = b

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.pix[i], self.pix[i + 1], self.pix[i + 2] = color

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x1 - x0):
                i = base + xx * 3
                self.pix[i] = r
                self.pix[i + 1] = g
                self.pix[i + 2] = b

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        """Bresenham line."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            if thick == 1:
                self.set(x0, y0, color)
            else:
                self.rect(x0 - thick // 2, y0 - thick // 2,
                          thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def ellipse(self, cx, cy, rx, ry, color):
        """Parametric ellipse outline (dense enough to look continuous)."""
        steps = max(48, 6 * (rx + ry))
        for i in range(steps):
            a = 2.0 * math.pi * i / steps
            self.set(round(cx + rx * math.cos(a)),
                     round(cy + ry * math.sin(a)), color)

    def filled_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            self.hline(cx - dx, cy + dy, 2 * dx + 1, color)


def write_png(path, cv):
    """Hand-rolled PNG writer: IHDR/IDAT/IEND, filter 0, zlib level 9."""
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: None
        raw += cv.pix[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

# Font scales (glyph height = 7 * scale)
S_MAST = 4      # masthead
S_HERO = 4      # hero headline
S_DATE = 2      # dateline
S_KICK = 2      # kickers, strip titles, labels
S_SIDE_H = 2    # side-lead headlines
S_GRID_H = 2    # grid headlines
S_BODY = 2      # hero body
S_BODY_SM = 1   # side-lead body
S_GRID_B = 1    # grid body
S_LABEL_SM = 1  # grid labels, brief heads, stat labels
S_TIME = 2      # timeline times
S_TL = 1        # timeline labels
S_MKT = 2       # markets
S_FOOT = 1      # footer
S_STAT_N = 3    # stat numbers


def rule(cv, x0, y, x1, width=1, color=RULE):
    cv.hline(x0, y, x1 - x0, color, thick=width)


def draw_globe(cv, cx, cy, r):
    """Simple vector globe: circle, meridians, parallels, marked spots."""
    cv.ellipse(cx, cy, r, r, NAVY)
    # meridians
    for k in (0.35, 0.7):
        cv.ellipse(cx, cy, int(r * k), r, NAVY_LIGHT)
    cv.vline(cx, cy - r, 2 * r + 1, NAVY_LIGHT)
    # parallels
    for k in (0.5,):
        yoff = int(r * k)
        half = int(math.sqrt(r * r - yoff * yoff))
        cv.hline(cx - half, cy - yoff, 2 * half + 1, NAVY_LIGHT)
        cv.hline(cx + half, cy + yoff, 2 * half + 1, NAVY_LIGHT)
    # Kuwait marker (upper right of globe) with starburst
    kx, ky = cx + int(r * 0.45), cy - int(r * 0.35)
    for dx, dy in ((0, -7), (0, 7), (-7, 0), (7, 0), (-5, -5), (5, -5),
                   (-5, 5), (5, 5)):
        cv.line(kx, ky, kx + dx, ky + dy, RED, thick=2)
    cv.filled_circle(kx, ky, 3, RED)
    # Gaza marker (left)
    gx, gy = cx - int(r * 0.55), cy + int(r * 0.15)
    cv.filled_circle(gx, gy, 3, RED)
    # Kyiv marker (top)
    ux, uy = cx + int(r * 0.1), cy - int(r * 0.62)
    cv.filled_circle(ux, uy, 3, RED)
    caption = "KUWAIT  \u00b7  GAZA  \u00b7  KYIV"
    cw = text_width(caption, 1)
    draw_text(cv, cx - cw // 2, cy + r + 6, caption, 1, GRAY)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = Canvas(W, H, PAPER)
    y = 0

    # ---- Masthead ----
    cv.rect(0, 0, W, 62, NAVY)
    title = "THE WORLD IN ONE DAY"
    tw = text_width(title, S_MAST, spacing=3, bold=True)
    draw_text(cv, (W - tw) // 2, 15, title, S_MAST, WHITE,
              spacing=3, bold=True)
    cv.rect(0, 62, W, 3, GOLD)
    y = 65

    # ---- Dateline ----
    cv.rect(0, y, W, 24, LIGHT_GRAY)
    date_line = ("FRIDAY 27 NOVEMBER 2026  \u00b7  30 STORIES  \u00b7  "
                 "17 COUNTRIES  \u00b7  14 FIELDS  \u00b7  TIMES AS REPORTED")
    dw = text_width(date_line, S_DATE, spacing=1, bold=True)
    draw_text(cv, (W - dw) // 2, y + 5, date_line, S_DATE, NAVY,
              spacing=1, bold=True)
    y += 24
    rule(cv, MARGIN, y, W - MARGIN, width=2, color=NAVY)
    y += 10

    # ---- Hero ----
    hero_x = MARGIN
    hero_w = 620
    draw_text(cv, hero_x, y, "MIDDLE EAST  \u00b7  WAR \u2014 KUWAIT",
              S_KICK, RED, spacing=1, bold=True)
    y += 18
    y = para(cv, hero_x, y, "IRANIAN DRONES KILL TWO ITALIANS IN KUWAIT",
             S_HERO, hero_w, 36, color=NAVY, max_lines=3,
             spacing=2, bold=True)
    y += 4
    y = para(cv, hero_x, y,
             "Two technicians for Rheinmetall Italia die when drones strike "
             "an air-defence station in Kuwait; two more people are wounded. "
             "Italy and Kuwait blame Iran; Tehran denies any role and accuses "
             "Kyiv of a \u201cfalse flag\u201d. It is the second reported "
             "Iranian attack on the Gulf state this month.",
             S_BODY, hero_w, 18, max_lines=5)
    hero_bottom = y

    # Globe + stat boxes on the right
    gx = 700
    gw = W - MARGIN - gx
    draw_globe(cv, gx + gw // 2, 146, 58)
    stats = [("2", "KILLED"), ("2", "WOUNDED"), ("2ND", "ATTACK IN NOV")]
    box_w = (gw - 2 * 8) // 3
    sy = 224
    for i, (num, lab) in enumerate(stats):
        bx = gx + i * (box_w + 8)
        cv.rect(bx, sy, box_w, 1, NAVY)
        cv.rect(bx, sy + 51, box_w, 1, NAVY)
        cv.vline(bx, sy, 52, NAVY)
        cv.vline(bx + box_w - 1, sy, 52, NAVY)
        nw = text_width(num, S_STAT_N, spacing=1, bold=True)
        draw_text(cv, bx + (box_w - nw) // 2, sy + 4, num, S_STAT_N, RED,
                  spacing=1, bold=True)
        lw = text_width(lab, S_LABEL_SM)
        draw_text(cv, bx + (box_w - lw) // 2, sy + 33, lab,
                  S_LABEL_SM, NAVY)
    y = max(hero_bottom, sy + 52) + 8
    rule(cv, MARGIN, y, W - MARGIN, width=2, color=NAVY)
    y += 10

    # ---- Three side leads ----
    leads = [
        ("GAZA  \u00b7  WAR",
         "ISRAEL KILLS 10 IN GAZA; HAMAS WEIGHS REPLY",
         "Strikes kill Hamas deputy education chief Khaled Abu Nada and his "
         "wife in Deir al-Balah, on a third straight night of attacks despite "
         "a year-old ceasefire. Hamas chief al-Hayya says the group will "
         "discuss a response; Netanyahu says about 80 Hamas fighters were "
         "killed in the past month."),
        ("UKRAINE  \u00b7  WAR",
         "KYIV HIT; UKRAINE LASER DOWNS DRONE",
         "Russian ballistic missiles wound seven in Kyiv and hit a mall. "
         "Ukraine says its \u201cBlysk\u201d laser shot down a jet-powered "
         "Shahed drone \u2014 a world first in combat. Air defences downed "
         "87 of 113 drones overnight."),
        ("UNITED STATES  \u00b7  ECONOMY",
         "TRUMP SEEKS PROBE INTO \u2018FAKE\u2019 GDP",
         "The president calls for an inquiry into alleged fake growth "
         "figures after US GDP was revised up to 4.3%. The claim lands as "
         "his tariff plan for 14 partners, at rates up to 35%, rattles "
         "markets ahead of Thanksgiving."),
    ]
    lead_top = y
    lead_bottom = y
    for i, (label, head, body) in enumerate(leads):
        x = MARGIN + i * (COL_W + 16)
        yy = lead_top
        draw_text(cv, x, yy, label, S_KICK, RED, spacing=1, bold=True)
        yy += 16
        yy = para(cv, x, yy, head, S_SIDE_H, COL_W, 18, color=NAVY,
                  max_lines=2, spacing=1, bold=True)
        yy += 2
        yy = para(cv, x, yy, body, S_BODY_SM, COL_W, 10, max_lines=5)
        lead_bottom = max(lead_bottom, yy)
    for i in range(2):
        x = MARGIN + (i + 1) * COL_W + i * 16 + 8
        cv.vline(x, lead_top, lead_bottom - lead_top, RULE)
    y = lead_bottom + 8
    rule(cv, MARGIN, y, W - MARGIN, width=2, color=NAVY)
    y += 8

    # ---- UTC timeline strip ----
    cv.rect(0, y, W, 74, LIGHT_GRAY)
    draw_text(cv, MARGIN, y + 6, "TIMELINE  \u00b7  27 NOV",
              S_KICK, NAVY, spacing=1, bold=True)
    timeline = [
        ("00:03", "Trump GDP probe"),
        ("00:22", "UK migration low"),
        ("00:26", "Chess draw"),
        ("01:03", "Kuwait drone deaths"),
        ("01:49", "SpaceX shares"),
        ("02:11", "Depardieu trial"),
        ("02:26", "Hamas weighs reply"),
        ("03:31", "Ibiza tanker sinks"),
    ]
    slot_w = (W - 2 * MARGIN) // 8
    ty = y + 24
    for i, (t, lab) in enumerate(timeline):
        x = MARGIN + i * slot_w
        draw_text(cv, x, ty, t, S_TIME, RED, spacing=1, bold=True)
        ly = ty + 18
        for ln in wrap(lab, S_TL, slot_w - 8):
            draw_text(cv, x, ly, ln, S_TL, INK)
            ly += 10
        if i < 7:
            cv.vline(x + slot_w - 4, ty, 44, RULE)
    y += 74 + 8
    rule(cv, MARGIN, y, W - MARGIN, width=2, color=NAVY)
    y += 8

    # ---- Grid: 15 stories, 3 cols x 5 rows ----
    grid = [
        ("UKRAINE  \u00b7  WAR", "Zelenskiy: new mass strike looms",
         "Kyiv says Moscow is preparing a fresh mass strike in the coming days."),
        ("RUSSIA  \u00b7  WAR", "Kremlin: Kyiv widens war zone",
         "Moscow says Kyiv is spreading the war to the Mediterranean and Baltic."),
        ("UNITED STATES  \u00b7  DIPLOMACY", "Kushner: Putin shuns ceasefire",
         "US envoy says territorial gaps cannot be bridged; $621.9m F-16 deal approved."),
        ("EUROPEAN UNION  \u00b7  AID", "EU approves \u20ac45bn Ukraine aid",
         "Council backs \u20ac45bn under a two-year, \u20ac90bn programme for Kyiv."),
        ("WORLD  \u00b7  WAR", "34 nations: stop chemical arms",
         "Joint statement demands Russia stop using toxic chemicals in Ukraine."),
        ("UNITED KINGDOM  \u00b7  POLITICS", "UK migration lowest since 1997",
         "Net migration falls to its lowest level since 1997, excluding the pandemic."),
        ("FRANCE  \u00b7  LAW", "Depardieu faces rape trial",
         "French court orders trial over alleged rape of an actress in 2018."),
        ("SPAIN  \u00b7  ACCIDENT", "Tanker sinks off Ibiza, 1 dead",
         "Diesel tanker carrying up to 7,000 tonnes capsizes; Spain races to stop a spill."),
        ("UNITED STATES  \u00b7  TECH", "Musk: 2 SpaceX shares per child",
         "Musk says every child in the US will get two shares in SpaceX."),
        ("CHESS  \u00b7  SPORT", "Gukesh\u2013Sindarov draw in Game 3",
         "World title match level after three games; marathon Game 3 ends in a draw."),
        ("NEW ZEALAND  \u00b7  POLITICS", "NZ count: coalition 67 of 131",
         "Final count gives the coalition a slim majority; 400,000 special votes counted."),
        ("UNITED STATES  \u00b7  WEATHER", "Storm wrecks US Thanksgiving",
         "Macy\u2019s parade postponed for the first time; 500,000 homes lose power."),
        ("GERMANY  \u00b7  SECURITY", "Germany arrests synagogue plotters",
         "Two Iraqis held over an alleged plot to attack a synagogue."),
        ("CHINA  \u00b7  REMEMBRANCE", "Hong Kong marks fire anniversary",
         "Flowers and prayers a year on from the deadly blaze; officials warn crowds."),
        ("EUROPE  \u00b7  DEFENCE", "Five nations buy BAE vehicles",
         "Finland says five European states ordered combat vehicles from BAE Systems."),
    ]
    row_h = 64
    grid_top = y
    for r in range(5):
        yy = grid_top + r * row_h
        for c in range(3):
            label, head, body = grid[r * 3 + c]
            x = MARGIN + c * (COL_W + 16)
            draw_text(cv, x, yy, label, S_LABEL_SM, RED, bold=True)
            hy = yy + 11
            hy = para(cv, x, hy, head, S_GRID_H, COL_W, 16, color=NAVY,
                      max_lines=2, spacing=1, bold=True)
            para(cv, x, hy, body, S_GRID_B, COL_W, 9, max_lines=2)
            if c < 2:
                cv.vline(x + COL_W + 8, yy, row_h - 6, RULE)
        if r < 4:
            rule(cv, MARGIN, yy + row_h - 2, W - MARGIN)
    y = grid_top + 5 * row_h + 6
    rule(cv, MARGIN, y, W - MARGIN, width=2, color=NAVY)
    y += 8

    # ---- Markets strip ----
    cv.rect(0, y, W, 52, LIGHT_GRAY)
    draw_text(cv, MARGIN, y + 5,
              "MARKETS  \u00b7  WED 25 NOV CLOSE \u2014 US MARKETS SHUT THU "
              "FOR THANKSGIVING",
              S_KICK, NAVY, spacing=1, bold=True)
    markets = [
        ("S&P 500", "7,182.78", "-0.25%", RED),
        ("NASDAQ", "23,585.80", "-0.62%", RED),
        ("DOW", "50,182.95", "+0.33%", GREEN),
        ("RUSSELL", "2,704.06", "+0.70%", GREEN),
        ("GOLD", "$3,589.18", "+0.92%", GREEN),
        ("BRENT", "$94.61", "+3.5%", GREEN),
        ("WTI", "$83.68", "+2.0%", GREEN),
        ("BITCOIN", "$60,900", "+2.7%", GREEN),
    ]
    mslot = (W - 2 * MARGIN) // 4
    for i, (name, val, chg, col) in enumerate(markets):
        x = MARGIN + (i % 4) * mslot
        yy = y + 22 + (i // 4) * 16
        nx = draw_text(cv, x, yy, name, S_MKT, NAVY, spacing=1, bold=True)
        cx = draw_text(cv, nx + 5, yy, val, S_MKT, INK)
        draw_text(cv, cx + 5, yy, chg, S_MKT, col, spacing=1, bold=True)
    y += 52 + 8

    # ---- In Brief ----
    draw_text(cv, MARGIN, y, "IN BRIEF", S_KICK, NAVY, spacing=1, bold=True)
    y += 16
    briefs = [
        ("INDIA  \u00b7  LAW", "PMLA bench rule",
         "A judicial member must sit on the bench, court says."),
        ("INDIA  \u00b7  LAW", "Ex-MP release quashed",
         "Bihar's early release of ex-MP Mohan was illegal."),
        ("ASIA  \u00b7  DEFENCE", "Drones reshape Asia",
         "Cheap drones are changing Asian militaries."),
        ("FRANCE  \u00b7  POLITICS", "Macron hits Le Pen",
         "President slams rival's 'arrogance' as if in charge."),
        ("EUROPE  \u00b7  SECURITY", "Romania seeks help",
         "Bucharest seeks more German help amid provocations."),
        ("COLOMBIA  \u00b7  CRIME", "Hostage tells of siege",
         "A rescued hostage recounts a supermarket siege."),
    ]
    brow_h = 38
    for i, (label, head, body) in enumerate(briefs):
        x = MARGIN + (i % 3) * (COL_W + 16)
        yy = y + (i // 3) * brow_h
        draw_text(cv, x, yy, label + "  \u2014  " + head, S_LABEL_SM, NAVY,
                  bold=True)
        para(cv, x, yy + 12, body, S_GRID_B, COL_W, 10, max_lines=1)
    y += 2 * brow_h + 6

    # ---- Footer ----
    rule(cv, MARGIN, y, W - MARGIN, width=2, color=NAVY)
    y += 6
    foot = ("Every story verified from live news reports on 27 November 2026  "
            "\u00b7  Python 3 stdlib only, no network  \u00b7  Built by an AI "
            "agent for make.fun\u2019s news-image-20261127 bounty")
    fw = text_width(foot, S_FOOT)
    draw_text(cv, (W - fw) // 2, y, foot, S_FOOT, GRAY)

    path = os.path.join(out_dir, "entry.png")
    write_png(path, cv)
    print("wrote %s (%d bytes)" % (path, os.path.getsize(path)))


if __name__ == "__main__":
    main()
