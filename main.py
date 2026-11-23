#!/usr/bin/env python3
"""The World in One Day -- Sunday 22 November 2026.

Draws a one-page newspaper front page that sums up the world's news of
22 November 2026 and writes it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR).

Pure Python standard library. Deterministic: no clock, no randomness,
no network -- the same bytes come out of every run.
"""

import os
import struct
import sys
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (20, 24, 29)
MUTED = (96, 100, 104)
RED = (178, 34, 40)
NAVY = (16, 34, 58)
NAVY2 = (24, 52, 84)
SKY = (126, 178, 214)
SEA = (64, 116, 158)
GOLD = (206, 158, 44)
CREAM = (250, 247, 238)
PANEL = (255, 253, 246)
PANEL_ALT = (240, 236, 224)
FLAME = (232, 116, 36)
GREEN = (52, 122, 74)
GREYLINE = (196, 190, 172)

# ---------------------------------------------------------------- canvas
PX = bytearray(W * H * 3)


def put(x, y, rgb):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        PX[i] = rgb[0]
        PX[i + 1] = rgb[1]
        PX[i + 2] = rgb[2]


def rect(x, y, w, h, rgb):
    for yy in range(y, y + h):
        base = yy * W
        for xx in range(x, x + w):
            if 0 <= xx < W and 0 <= yy < H:
                i = (base + xx) * 3
                PX[i] = rgb[0]
                PX[i + 1] = rgb[1]
                PX[i + 2] = rgb[2]


def hline(x, y, w, rgb, t=1):
    rect(x, y, w, t, rgb)


def vline(x, y, h, rgb, t=1):
    rect(x, y, t, h, rgb)


def line(x0, y0, x1, y1, rgb, t=1):
    """Bresenham line with a square brush of thickness t."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    off = t // 2
    while True:
        rect(x - off, y - off, t, t, rgb)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def circle(cx, cy, r, rgb, fill=True):
    if fill:
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5)
            hline(cx - dx, yy, 2 * dx + 1, rgb)
    else:
        steps = max(24, r * 4)
        for i in range(steps):
            a = 2 * 3.141592653589793 * i / steps
            put(int(cx + r * _cos(a)), int(cy + r * _sin(a)), rgb)


def _sin(a):
    return __import__("math").sin(a)


def _cos(a):
    return __import__("math").cos(a)


def poly(points, rgb):
    """Filled polygon via scanline even-odd fill."""
    ys = [p[1] for p in points]
    for yy in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= yy < y1) or (y1 <= yy < y0):
                xs.append(x0 + (yy - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            hline(int(xs[i]), yy, int(xs[i + 1]) - int(xs[i]) + 1, rgb)


def outline(points, rgb, t=2):
    n = len(points)
    for i in range(n):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) % n]
        line(x0, y0, x1, y1, rgb, t)


# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, each row a 5-bit mask (bit 4 = leftmost pixel).
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1C, 0x12, 0x11, 0x11, 0x11, 0x12, 0x1C),
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
    "X": (0x11, 0x0A, 0x04, 0x04, 0x04, 0x0A, 0x11),
    "Y": (0x11, 0x0A, 0x04, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    "-": (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "%": (0x18, 0x19, 0x02, 0x04, 0x08, 0x13, 0x03),
    '"': (0x0A, 0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00),
}


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, rgb, bold=False):
    s = s.upper()
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    rect(cx + col * scale, y + row * scale, scale, scale, rgb)
                    if bold:
                        rect(cx + col * scale + max(1, scale // 3),
                             y + row * scale, scale, scale, rgb)
        cx += 6 * scale
    return cx


def draw_centered(y, s, scale, rgb, bold=False):
    draw_text((W - text_w(s, scale)) // 2, y, s, scale, rgb, bold)


def wrap(s, scale, max_w):
    words = s.upper().split()
    lines, cur = [], ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_w(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(x, y, s, scale, rgb, max_w, leading, bold=False):
    for ln in wrap(s, scale, max_w):
        draw_text(x, y, ln, scale, rgb, bold)
        y += leading
    return y


# ---------------------------------------------------------------- icons
def icon_ship(x, y, s, hull, accent):
    """Warship silhouette with a sea-drone arc above it."""
    poly([(x, y + 34 * s // 4), (x + 60 * s // 4, y + 34 * s // 4),
          (x + 52 * s // 4, y + 44 * s // 4), (x + 8 * s // 4, y + 44 * s // 4)], hull)
    rect(x + 18 * s // 4, y + 26 * s // 4, 22 * s // 4, 8 * s // 4, hull)
    rect(x + 40 * s // 4, y + 18 * s // 4, 4 * s // 4, 16 * s // 4, hull)
    line(x + 42 * s // 4, y + 18 * s // 4, x + 56 * s // 4, y + 12 * s // 4, accent, max(1, s // 2))
    for i in range(3):  # waves
        yy = y + (50 + i * 5) * s // 4
        for xx in range(x, x + 60 * s // 4, 10 * s // 4):
            line(xx, yy, xx + 5 * s // 4, yy - 2 * s // 4, SEA, max(1, s // 2))


def icon_scales(x, y, s, ink):
    cx = x + 22 * s // 4
    vline(cx, y + 6 * s // 4, 34 * s // 4, ink, max(1, s // 2))
    hline(x + 2 * s // 4, y + 8 * s // 4, 40 * s // 4, ink, max(1, s // 2))
    hline(x + 12 * s // 4, y + 44 * s // 4, 20 * s // 4, ink, max(1, s // 2))
    for px in (x + 4 * s // 4, x + 34 * s // 4):
        line(px + 6 * s // 4, y + 8 * s // 4, px, y + 22 * s // 4, ink, max(1, s // 2))
        line(px + 6 * s // 4, y + 8 * s // 4, px + 12 * s // 4, y + 22 * s // 4, ink, max(1, s // 2))
        poly([(px - 2 * s // 4, y + 22 * s // 4), (px + 14 * s // 4, y + 22 * s // 4),
              (px + 6 * s // 4, y + 30 * s // 4)], ink)


def icon_shield(x, y, s, ink, accent):
    pts = [(x + 22 * s // 4, y), (x + 42 * s // 4, y + 6 * s // 4),
           (x + 42 * s // 4, y + 26 * s // 4), (x + 22 * s // 4, y + 46 * s // 4),
           (x + 2 * s // 4, y + 26 * s // 4), (x + 2 * s // 4, y + 6 * s // 4)]
    poly(pts, ink)
    cx, cy = x + 22 * s // 4, y + 20 * s // 4
    for dx, dy in ((0, -9), (7, -3), (-7, -3), (5, 6), (-5, 6)):
        circle(cx + dx * s // 4, cy + dy * s // 4, max(2, 3 * s // 4), accent)


def icon_tanker(x, y, s, ink):
    poly([(x, y + 30 * s // 4), (x + 62 * s // 4, y + 30 * s // 4),
          (x + 54 * s // 4, y + 42 * s // 4), (x + 8 * s // 4, y + 42 * s // 4)], ink)
    for i in range(3):
        rect(x + (10 + i * 14) * s // 4, y + 20 * s // 4, 11 * s // 4, 10 * s // 4,
             (SEA if i % 2 else GOLD))
    # flame above the middle container
    fx, fy = x + 31 * s // 4, y + 16 * s // 4
    poly([(fx - 6 * s // 4, fy + 6 * s // 4), (fx, fy - 10 * s // 4),
          (fx + 6 * s // 4, fy + 6 * s // 4), (fx, fy + 2 * s // 4)], FLAME)


def icon_house_flame(x, y, s, ink):
    poly([(x + 4 * s // 4, y + 22 * s // 4), (x + 24 * s // 4, y + 4 * s // 4),
          (x + 44 * s // 4, y + 22 * s // 4)], ink)
    rect(x + 10 * s // 4, y + 22 * s // 4, 28 * s // 4, 20 * s // 4, ink)
    rect(x + 20 * s // 4, y + 30 * s // 4, 8 * s // 4, 12 * s // 4, PAPER)
    fx, fy = x + 40 * s // 4, y + 12 * s // 4
    poly([(fx - 7 * s // 4, fy + 10 * s // 4), (fx + 1 * s // 4, fy - 8 * s // 4),
          (fx + 8 * s // 4, fy + 10 * s // 4), (fx + 1 * s // 4, fy + 3 * s // 4)], FLAME)


def icon_ball(x, y, s, ink):
    cx, cy, r = x + 24 * s // 4, y + 24 * s // 4, 22 * s // 4
    circle(cx, cy, r, (198, 216, 90))
    circle(cx, cy, r, ink, fill=False)
    import math
    # two curved seams hugging the left and right edges, tennis-ball style
    for side in (-1, 1):
        pts = []
        for i in range(17):
            a = -1.15 + 2.3 * i / 16
            px = cx + side * int(r * 0.92 * math.cos(a * 0.42))
            py = cy + int(r * math.sin(a))
            pts.append((px, py))
        for i in range(len(pts) - 1):
            line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], ink, max(1, s // 2))


def hero_globe(cx, cy, r):
    """A globe split by a jagged crack, over a rising thermometer."""
    circle(cx, cy, r, SKY)
    circle(cx, cy, r, NAVY, fill=False)
    import math
    # meridians
    for frac in (-0.55, 0.0, 0.55):
        pts = []
        for i in range(25):
            a = -math.pi / 2 + math.pi * i / 24
            pts.append((int(cx + frac * r * math.cos(a) * 1.6), int(cy + r * math.sin(a))))
        for i in range(len(pts) - 1):
            line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], NAVY2, 2)
    # parallels
    for frac in (-0.45, 0.0, 0.45):
        yy = int(cy + frac * r)
        half = int(r * (1 - frac * frac) ** 0.5)
        hline(cx - half, yy, 2 * half, NAVY2, 2)
    # continent blobs
    for bx, by, br in ((-40, -38, 26), (28, -18, 20), (-8, 34, 24), (52, 30, 13)):
        circle(cx + bx * r // 100, cy + by * r // 100, br * r // 100, GREEN)
    # the crack
    crack = [(cx - 6, cy - r + 8), (cx + 14, cy - r // 2), (cx - 10, cy - 6),
             (cx + 16, cy + r // 3), (cx - 2, cy + r - 10)]
    for i in range(len(crack) - 1):
        line(crack[i][0], crack[i][1], crack[i + 1][0], crack[i + 1][1], RED, 7)
    # thermometer at the side
    tx = cx + r + 26
    rect(tx, cy - r + 10, 16, 2 * r - 52, CREAM)
    outline([(tx, cy - r + 10), (tx + 16, cy - r + 10), (tx + 16, cy + r - 42),
             (tx, cy + r - 42)], NAVY, 2)
    rect(tx + 4, cy - r // 3, 8, r // 3 + r - 46, RED)
    circle(tx + 8, cy + r - 30, 15, RED)
    circle(tx + 8, cy + r - 30, 15, NAVY, fill=False)


# ---------------------------------------------------------------- page
def masthead():
    rect(0, 0, W, H, PAPER)
    hline(0, 10, W, RED, 6)
    draw_centered(26, "THE WORLD IN ONE DAY", 3, RED, bold=True)
    draw_centered(56, "SUNDAY 22 NOVEMBER 2026", 6, INK, bold=True)
    hline(40, 108, W - 80, INK, 3)
    hline(40, 114, W - 80, INK, 1)


def hero():
    y0, hh = 126, 280
    rect(24, y0, W - 48, hh, NAVY)
    hero_globe(196, y0 + hh // 2, 100)
    tx = 372
    draw_text(tx, y0 + 26, "ANTALYA, TURKIYE - CLIMATE SUMMIT", 2, GOLD, bold=True)
    y = draw_wrapped(tx, y0 + 56, "COP31 CLIMATE TALKS COLLAPSE WITHOUT A DEAL",
                     4, CREAM, W - tx - 48, 34, bold=True)
    hline(tx, y + 4, 120, RED, 4)
    draw_wrapped(tx, y + 18,
                 "NEARLY 200 NATIONS END THE SUMMIT WITH NO AGREEMENT AFTER THE "
                 "EU AND OTHERS REJECT THE FINAL DRAFT. FOSSIL FUELS GO "
                 "UNMENTIONED, AND UN CHIEF GUTERRES SAYS HE IS DEEPLY "
                 "DISAPPOINTED.", 2, (214, 224, 236), W - tx - 48, 19)


PANELS = [
    ("LIBYA - WAR AT SEA", "UKRAINE DRONES SINK RUSSIAN WARSHIP",
     "ZELENSKYY CONFIRMS THE STRIKE ON THE VESSEL AT BENGHAZI PORT",
     icon_ship, SEA),
    ("THE HAGUE - ICJ RULING", "WORLD COURT: MYANMAR COMMITTED GENOCIDE",
     "REFUGEES WELCOME THE UN COURT RULING ON THE 2017 CRACKDOWN",
     icon_scales, GOLD),
    ("MEXICO - CARTEL LEADER", "'EL CHAPO ISIDRO' CAPTURED IN MEXICO",
     "THE FBI TOP-10 FUGITIVE IS TAKEN IN A SINALOA FIREFIGHT THAT KILLS 11",
     icon_shield, RED),
    ("STRAIT OF HORMUZ", "IRAN STRIKES THREE TANKERS AT THE STRAIT",
     "BAHRAIN SAYS IRAN HIT A CIVILIAN PLANT; TEHRAN SHOWS A 'MISSILE CITY'",
     icon_tanker, FLAME),
    ("WEST BANK - OVERNIGHT RAIDS", "SETTLERS TORCH HOMES AND CARS IN VILLAGES",
     "12 VEHICLES BURNED NEAR RAMALLAH; EISENKOT CALLS THE RAIDS TERRORISM",
     icon_house_flame, FLAME),
    ("TURIN - TENNIS", "ALCARAZ BEATS ZVEREV, WINS ATP FINALS",
     "A 6-2 7-6 WIN OVER THE WORLD NO.1 SEALS HIS MAIDEN TITLE",
     icon_ball, GREEN),
]


def panel(x, y, w, h, kicker, head, body, icon, accent, alt):
    rect(x, y, w, h, PANEL_ALT if alt else PANEL)
    hline(x, y, w, accent, 5)
    icon(x + 16, y + 34, 4, INK, accent) if icon in (icon_ship, icon_shield) \
        else icon(x + 16, y + 34, 4, INK)
    tx = x + 92
    draw_text(tx, y + 12, kicker, 2, accent, bold=True)
    y2 = draw_wrapped(tx, y + 32, head, 3, INK, x + w - tx - 12, 25, bold=True)
    draw_wrapped(tx, y2 + 4, body, 2, (52, 56, 60), x + w - tx - 12, 16)


def grid():
    draw_text(24, 420, "AROUND THE WORLD - SIX MORE STORIES OF THE DAY", 2, RED, bold=True)
    hline(24, 442, W - 48, GREYLINE, 2)
    pw, ph, gap = 488, 140, 16
    for i, (kick, head, body, icon, accent) in enumerate(PANELS):
        x = 24 + (i % 2) * (pw + gap)
        y = 452 + (i // 2) * (ph + 8)
        panel(x, y, pw, ph, kick, head, body, icon, accent, i % 2 == 1)


MINI = [
    ("KYIV, UKRAINE", "RUSSIAN DRONES HIT AN APARTMENT BLOCK: 3 KILLED, 14 MISSING"),
    ("LONDON - BRUSSELS", "UK AND EU SIGN POST-BREXIT DEALS ON TRADE AND TRAVEL"),
    ("SEOUL, SOUTH KOREA", "EDUCATION MINISTER QUITS OVER AI CHEATING ROW IN EXAM RULES"),
]


def mini_strip():
    y = 896
    hline(24, y - 8, W - 48, GREYLINE, 2)
    colw = (W - 48 - 24) // 3
    for i, (kick, head) in enumerate(MINI):
        x = 24 + i * (colw + 12)
        draw_text(x, y, kick, 2, RED, bold=True)
        draw_wrapped(x, y + 20, head, 2, INK, colw, 17, bold=True)


def ticker():
    y = 990
    rect(0, 972, W, H - 972, INK)
    draw_text(24, y,
              "NIGERIA: 24 DIE AS BOAT CAPSIZES  +++  US SEEKS NVIDIA "
              "ANSWERS ON CHINA CHIPS", 2, CREAM)


# ---------------------------------------------------------------- png out
def png_bytes():
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += PX[yy * W * 3:(yy + 1) * W * 3]

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def check_png(data):
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "bad signature"
    assert len(data) <= 1048576, "image over 1 MiB"
    pos = 8
    w = h = None
    while pos < len(data):
        ln, = struct.unpack(">I", data[pos:pos + 4])
        tag = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + ln]
        crc, = struct.unpack(">I", data[pos + 8 + ln:pos + 12 + ln])
        assert crc == zlib.crc32(tag + body) & 0xFFFFFFFF, "bad CRC"
        if tag == b"IHDR":
            w, h = struct.unpack(">II", body[:8])
        pos += 12 + ln
    assert (w, h) == (W, H), "wrong dimensions"
    return True


def main():
    masthead()
    hero()
    grid()
    mini_strip()
    ticker()
    data = png_bytes()
    check_png(data)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (path, len(data), W, H))
    return 0


if __name__ == "__main__":
    sys.exit(main())
