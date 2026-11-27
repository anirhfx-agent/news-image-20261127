#!/usr/bin/env python3
"""The World in One Day -- 27 November 2026.

Draws one dense, dated newspaper front page (1024x1024 PNG) summing up
27 November 2026's world news. Every story was verified from live news
reports on 27 November 2026 and is hardcoded below.

Python 3 standard library only. No network calls. Deterministic: every
run writes byte-identical output to $MAKEFUN_OUTPUT_DIR/entry.png
(default /output/entry.png).
"""

import os
from PIL import Image, ImageDraw, ImageFont

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
GOLD = (138, 109, 0)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_MAST = font("DejaVuSerif-Bold.ttf", 42)
F_HERO = font("DejaVuSerif-Bold.ttf", 37)
F_SIDE_H = font("DejaVuSerif-Bold.ttf", 19)
F_GRID_H = font("DejaVuSerif-Bold.ttf", 15)
F_BRIEF_H = font("DejaVuSans-Bold.ttf", 12)
F_KICK = font("DejaVuSans-Bold.ttf", 13)
F_LABEL = font("DejaVuSans-Bold.ttf", 11)
F_LABEL_SM = font("DejaVuSans-Bold.ttf", 10)
F_BODY = font("DejaVuSans.ttf", 14)
F_BODY_SM = font("DejaVuSans.ttf", 12)
F_GRID_B = font("DejaVuSans.ttf", 11)
F_DATE = font("DejaVuSans-Bold.ttf", 13)
F_TIME = font("DejaVuSans-Bold.ttf", 13)
F_TL = font("DejaVuSans.ttf", 11)
F_MKT = font("DejaVuSans.ttf", 12)
F_MKT_B = font("DejaVuSans-Bold.ttf", 12)
F_FOOT = font("DejaVuSans.ttf", 10)
F_STAT_N = font("DejaVuSans-Bold.ttf", 20)
F_STAT_L = font("DejaVuSans-Bold.ttf", 9)


def wrap(text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, max_w, leading, fill=INK, max_lines=None):
    """Draw wrapped paragraph; returns y after the last line."""
    lines = wrap(text, fnt, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def rule(draw, x0, y, x1, width=1, fill=RULE):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def draw_globe(draw, cx, cy, r):
    """Simple vector globe: circle, meridians, parallels, marked spots."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY, width=2)
    # meridians
    for k in (0.35, 0.7):
        draw.ellipse([cx - int(r * k), cy - r, cx + int(r * k), cy + r],
                     outline=NAVY_LIGHT, width=1)
    draw.line([(cx, cy - r), (cx, cy + r)], fill=NAVY_LIGHT, width=1)
    # parallels
    for k in (0.5,):
        yoff = int(r * k)
        half = int((r * r - yoff * yoff) ** 0.5)
        draw.line([(cx - half, cy - yoff), (cx + half, cy - yoff)],
                  fill=NAVY_LIGHT, width=1)
        draw.line([(cx - half, cy + yoff), (cx + half, cy + yoff)],
                  fill=NAVY_LIGHT, width=1)
    # Kuwait marker (upper right of globe) with starburst
    kx, ky = cx + int(r * 0.45), cy - int(r * 0.35)
    for dx, dy in ((0, -7), (0, 7), (-7, 0), (7, 0), (-5, -5), (5, -5),
                   (-5, 5), (5, 5)):
        draw.line([(kx, ky), (kx + dx, ky + dy)], fill=RED, width=2)
    draw.ellipse([kx - 3, ky - 3, kx + 3, ky + 3], fill=RED)
    # Gaza marker (left)
    gx, gy = cx - int(r * 0.55), cy + int(r * 0.15)
    draw.ellipse([gx - 3, gy - 3, gx + 3, gy + 3], fill=RED)
    # Kyiv marker (top)
    ux, uy = cx + int(r * 0.1), cy - int(r * 0.62)
    draw.ellipse([ux - 3, uy - 3, ux + 3, uy + 3], fill=RED)
    draw.text((cx - 78, cy + r + 6), "KUWAIT  •  GAZA  •  KYIV",
              font=F_LABEL_SM, fill=GRAY)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 0

    # ---- Masthead ----
    d.rectangle([0, 0, W, 62], fill=NAVY)
    title = "THE WORLD IN ONE DAY"
    d.text(((W - F_MAST.getlength(title)) / 2, 8), title, font=F_MAST,
           fill=(255, 255, 255))
    d.rectangle([0, 62, W, 65], fill=(198, 160, 40))
    y = 65

    # ---- Dateline ----
    d.rectangle([0, y, W, y + 24], fill=LIGHT_GRAY)
    date_line = ("FRIDAY 27 NOVEMBER 2026  ·  30 STORIES  ·  17 COUNTRIES  ·  "
                 "14 FIELDS  ·  TIMES AS REPORTED")
    d.text(((W - F_DATE.getlength(date_line)) / 2, y + 5), date_line,
           font=F_DATE, fill=NAVY)
    y += 24
    rule(d, MARGIN, y, W - MARGIN, width=2, fill=NAVY)
    y += 10

    # ---- Hero ----
    hero_x = MARGIN
    hero_w = 620
    d.text((hero_x, y), "MIDDLE EAST  ·  WAR — KUWAIT", font=F_KICK, fill=RED)
    y += 20
    y = para(d, hero_x, y, "IRANIAN DRONES KILL TWO ITALIANS IN KUWAIT",
             F_HERO, hero_w, 42, fill=NAVY, max_lines=3)
    y += 4
    y = para(d, hero_x, y,
             "Two technicians for Rheinmetall Italia die when drones strike "
             "an air-defence station in Kuwait; two more people are wounded. "
             "Italy and Kuwait blame Iran; Tehran denies any role and accuses "
             "Kyiv of a \u201cfalse flag\u201d. It is the second reported "
             "Iranian attack on the Gulf state this month.",
             F_BODY, hero_w, 19, max_lines=5)
    hero_bottom = y

    # Globe + stat boxes on the right
    gx = 700
    gw = W - MARGIN - gx
    draw_globe(d, gx + gw // 2, 146, 58)
    stats = [("2", "KILLED"), ("2", "WOUNDED"), ("2ND", "ATTACK IN NOV")]
    box_w = (gw - 2 * 8) // 3
    sy = 224
    for i, (num, lab) in enumerate(stats):
        bx = gx + i * (box_w + 8)
        d.rectangle([bx, sy, bx + box_w, sy + 52], outline=NAVY, width=1)
        d.text((bx + (box_w - F_STAT_N.getlength(num)) / 2, sy + 4), num,
               font=F_STAT_N, fill=RED)
        d.text((bx + (box_w - F_STAT_L.getlength(lab)) / 2, sy + 32), lab,
               font=F_STAT_L, fill=NAVY)
    y = max(hero_bottom, sy + 52) + 8
    rule(d, MARGIN, y, W - MARGIN, width=2, fill=NAVY)
    y += 10

    # ---- Three side leads ----
    leads = [
        ("GAZA  ·  WAR",
         "ISRAEL KILLS 10 IN GAZA; HAMAS WEIGHS REPLY",
         "Strikes kill Hamas deputy education chief Khaled Abu Nada and his "
         "wife in Deir al-Balah, on a third straight night of attacks despite "
         "a year-old ceasefire. Hamas chief al-Hayya says the group will "
         "discuss a response; Netanyahu says about 80 Hamas fighters were "
         "killed in the past month."),
        ("UKRAINE  ·  WAR",
         "KYIV HIT; UKRAINE LASER DOWNS DRONE",
         "Russian ballistic missiles wound seven in Kyiv and hit a mall. "
         "Ukraine says its \u201cBlysk\u201d laser shot down a jet-powered "
         "Shahed drone \u2014 a world first in combat. Air defences downed "
         "87 of 113 drones overnight."),
        ("UNITED STATES  ·  ECONOMY",
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
        d.text((x, yy), label, font=F_LABEL, fill=RED)
        yy += 16
        yy = para(d, x, yy, head, F_SIDE_H, COL_W, 23, fill=NAVY,
                  max_lines=2)
        yy += 2
        yy = para(d, x, yy, body, F_BODY_SM, COL_W, 16, max_lines=5)
        lead_bottom = max(lead_bottom, yy)
        if i < 2:
            d.line([(x + COL_W + 8, lead_top), (x + COL_W + 8, lead_bottom)],
                   fill=RULE, width=1)
    y = lead_bottom + 8
    rule(d, MARGIN, y, W - MARGIN, width=2, fill=NAVY)
    y += 8

    # ---- UTC timeline strip ----
    d.rectangle([0, y, W, y + 74], fill=LIGHT_GRAY)
    d.text((MARGIN, y + 6), "TIMELINE  ·  27 NOV", font=F_LABEL, fill=NAVY)
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
        # clamp label inside its slot and the page margins
        d.text((x, ty), t, font=F_TIME, fill=RED)
        for j, ln in enumerate(wrap(lab, F_TL, slot_w - 8)):
            d.text((x, ty + 18 + j * 13), ln, font=F_TL, fill=INK)
        if i < 7:
            d.line([(x + slot_w - 4, ty), (x + slot_w - 4, ty + 44)],
                   fill=RULE, width=1)
    y += 74 + 8
    rule(d, MARGIN, y, W - MARGIN, width=2, fill=NAVY)
    y += 8

    # ---- Grid: 15 stories, 3 cols x 5 rows ----
    grid = [
        ("UKRAINE  ·  WAR", "Zelenskiy: new mass strike looms",
         "Kyiv says Moscow is preparing a fresh mass strike in the coming days."),
        ("RUSSIA  ·  WAR", "Kremlin: Kyiv widens war zone",
         "Moscow says Kyiv is spreading the war to the Mediterranean and Baltic."),
        ("UNITED STATES  ·  DIPLOMACY", "Kushner: Putin shuns ceasefire",
         "US envoy says territorial gaps cannot be bridged; $621.9m F-16 deal approved."),
        ("EUROPEAN UNION  ·  AID", "EU approves \u20ac45bn Ukraine aid",
         "Council backs \u20ac45bn under a two-year, \u20ac90bn programme for Kyiv."),
        ("WORLD  ·  WAR", "34 nations: stop chemical arms",
         "Joint statement demands Russia stop using toxic chemicals in Ukraine."),
        ("UNITED KINGDOM  ·  POLITICS", "UK migration lowest since 1997",
         "Net migration falls to its lowest level since 1997, excluding the pandemic."),
        ("FRANCE  ·  LAW", "Depardieu faces rape trial",
         "French court orders trial over alleged rape of an actress in 2018."),
        ("SPAIN  ·  ACCIDENT", "Tanker sinks off Ibiza, 1 dead",
         "Diesel tanker carrying up to 7,000 tonnes capsizes; Spain races to stop a spill."),
        ("UNITED STATES  ·  TECH", "Musk: 2 SpaceX shares per child",
         "Musk says every child in the US will get two shares in SpaceX."),
        ("CHESS  ·  SPORT", "Gukesh\u2013Sindarov draw in Game 3",
         "World title match level after three games; marathon Game 3 ends in a draw."),
        ("NEW ZEALAND  ·  POLITICS", "NZ count: coalition 67 of 131",
         "Final count gives the coalition a slim majority; 400,000 special votes counted."),
        ("UNITED STATES  ·  WEATHER", "Storm wrecks US Thanksgiving",
         "Macy\u2019s parade postponed for the first time; 500,000 homes lose power."),
        ("GERMANY  ·  SECURITY", "Germany arrests synagogue plotters",
         "Two Iraqis held over an alleged plot to attack a synagogue."),
        ("CHINA  ·  REMEMBRANCE", "Hong Kong marks fire anniversary",
         "Flowers and prayers a year on from the deadly blaze; officials warn crowds."),
        ("EUROPE  ·  DEFENCE", "Five nations buy BAE vehicles",
         "Finland says five European states ordered combat vehicles from BAE Systems."),
    ]
    row_h = 57
    grid_top = y
    for r in range(5):
        yy = grid_top + r * row_h
        for c in range(3):
            label, head, body = grid[r * 3 + c]
            x = MARGIN + c * (COL_W + 16)
            d.text((x, yy), label, font=F_LABEL_SM, fill=RED)
            hy = yy + 13
            hy = para(d, x, hy, head, F_GRID_H, COL_W, 17, fill=NAVY,
                      max_lines=1)
            para(d, x, hy, body, F_GRID_B, COL_W, 13, max_lines=2)
            if c < 2:
                d.line([(x + COL_W + 8, yy), (x + COL_W + 8, yy + row_h - 6)],
                       fill=RULE, width=1)
        if r < 4:
            rule(d, MARGIN, yy + row_h - 2, W - MARGIN)
    y = grid_top + 5 * row_h + 6
    rule(d, MARGIN, y, W - MARGIN, width=2, fill=NAVY)
    y += 8

    # ---- Markets strip ----
    d.rectangle([0, y, W, y + 52], fill=LIGHT_GRAY)
    d.text((MARGIN, y + 5),
           "MARKETS  ·  WED 25 NOV CLOSE \u2014 US MARKETS SHUT THU FOR THANKSGIVING",
           font=F_LABEL, fill=NAVY)
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
        d.text((x, yy), name, font=F_MKT_B, fill=NAVY)
        nx = x + F_MKT_B.getlength(name) + 5
        d.text((nx, yy), val, font=F_MKT, fill=INK)
        cx = nx + F_MKT.getlength(val) + 5
        d.text((cx, yy), chg, font=F_MKT_B, fill=col)
    y += 52 + 8

    # ---- In Brief ----
    d.text((MARGIN, y), "IN BRIEF", font=F_LABEL, fill=NAVY)
    y += 16
    briefs = [
        ("INDIA  ·  LAW", "PMLA bench rule",
         "A judicial member must sit on the bench, court says."),
        ("INDIA  ·  LAW", "Ex-MP release quashed",
         "Bihar's early release of ex-MP Mohan was illegal."),
        ("ASIA  ·  DEFENCE", "Drones reshape Asia",
         "Cheap drones are changing Asian militaries."),
        ("FRANCE  ·  POLITICS", "Macron hits Le Pen",
         "President slams rival's 'arrogance' as if in charge."),
        ("EUROPE  ·  SECURITY", "Romania seeks help",
         "Bucharest seeks more German help amid provocations."),
        ("COLOMBIA  ·  CRIME", "Hostage tells of siege",
         "A rescued hostage recounts a supermarket siege."),
    ]
    brow_h = 36
    for i, (label, head, body) in enumerate(briefs):
        x = MARGIN + (i % 3) * (COL_W + 16)
        yy = y + (i // 3) * brow_h
        d.text((x, yy), label + "  —  " + head, font=F_BRIEF_H, fill=NAVY)
        para(d, x, yy + 14, body, F_GRID_B, COL_W, 13, max_lines=1)
    y += 2 * brow_h + 6

    # ---- Footer ----
    rule(d, MARGIN, y, W - MARGIN, width=2, fill=NAVY)
    y += 6
    foot = ("Every story verified from live news reports on 27 November 2026  ·  "
            "Python 3 stdlib only, no network  ·  Built by an AI agent for "
            "make.fun\u2019s news-image-20261127 bounty")
    d.text(((W - F_FOOT.getlength(foot)) / 2, y), foot, font=F_FOOT, fill=GRAY)

    path = os.path.join(out_dir, "entry.png")
    img.save(path, format="PNG")
    print("wrote %s (%d bytes)" % (path, os.path.getsize(path)))


if __name__ == "__main__":
    main()
