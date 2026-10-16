# -*- coding: utf-8 -*-
"""Our Expertise + Org Structure slides from two screenshots -> two_slides.json + assets_two/"""
import os, json, sys
import cv2
import numpy as np
import gen_slides as G
from gen_slides import runs_of, fsize, T, esc, CW, CH



def fix_runs(ink, rr, need, x0, x1, ya, yb):
    """make the list of text rows exactly `need` long: merge the closest rows, or split a merged block into equal lines"""
    rr = [dict(r) for r in rr]
    while len(rr) > need:
        gaps = [rr[i + 1]["y0"] - rr[i]["y1"] for i in range(len(rr) - 1)]
        k = int(np.argmin(gaps))
        a, b = rr[k], rr.pop(k + 1)
        a["y1"] = b["y1"]; a["x0"] = min(a["x0"], b["x0"]); a["x1"] = max(a["x1"], b["x1"])
    return rr


def split_equal(ink, run, n, x0, x1):
    top, bot = run["y0"], run["y1"]
    h = (bot - top) / float(n)
    out = []
    for k in range(n):
        a, b = int(round(top + k * h)), int(round(top + (k + 1) * h))
        cols = np.where(ink[a:b, x0:x1].sum(axis=0) > 0)[0]
        out.append(dict(y0=a, y1=b, x0=int(cols.min()) + x0 if len(cols) else x0, x1=int(cols.max()) + x0 if len(cols) else x1))
    return out

IMGDIR = "../images"
OUT = "assets_two"
os.makedirs(OUT, exist_ok=True)
S = 1280 / 1600.0
res = {}


def save(name, im, q=92):
    cv2.imwrite(os.path.join(OUT, name), im, [cv2.IMWRITE_JPEG_QUALITY, q])
    return name


# ================================================================== OUR EXPERTISE
im = cv2.imread(os.path.join(IMGDIR, "57.jpg"))
H, W = im.shape[:2]
CARDS = [
    ("01", ["ELECTRICAL"], ["HT/LT Power Distribution", "Lighting Communication &", "Security Systems"]),
    ("02", ["PLUMBING"], ["Drainage & Vent Pipes", "Water supply, WTP & STP", "Hydro-pneumatic systems", "Sanitary wares"]),
    ("03", ["FIRE FIGHTING"], ["Fire Alarm", "NOVEC VESDA Sprinkler &", "Suppression Systems"]),
    ("04", ["HVAC"], ["VRV Systems", "Chilled Water System", "Precision Air conditioning", "Base build & Fitout"]),
    ("05", ["PHE"], ["Drainage & vent pipes", "Water supply, sewage &", "drainage systems"]),
    ("06", ["IBMS"], ["Devices & energy-saving sensors", "Occupancy", "Environment control System backbone", "Integration GUI, monitoring & BMS services"]),
    ("07", ["LOW VOLTAGE", "SOLUTIONS"], ["CCTV, access control & intrusion", "detection", "Motion-based lighting", "Structured cabling & networking", "Public address systems"]),
]
white = (im.min(axis=2) >= 249).astype(np.uint8)
white = cv2.morphologyEx(white, cv2.MORPH_CLOSE, np.ones((21, 21), np.uint8))
white = cv2.morphologyEx(white, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(white)
boxes = []
for i in range(1, n):
    x, y, bw, bh, a = st[i]
    if bw > 200 and bh > 300:
        boxes.append([x, y, x + bw, y + bh])
boxes.sort(key=lambda b: (round(b[1] / 200), b[0]))
print("cards", len(boxes))
ink = (im.min(axis=2) < 150).astype(np.uint8)
out = ['<section class="pj pj-e" data-block="pj_expertise">']
# heading
hr = [r for r in runs_of(ink, 20, 640, 20, 300) if r["y1"] - r["y0"] > 20]
size = np.median([(r["y1"] - r["y0"]) / 0.72 for r in hr]) * S
out.append(G.title_html([[("OUR", "l", 0)], [("EXPERTISE", "b", 0)]], hr[0]["x0"] * S, [(r["y0"] + r["y1"]) / 2 * S for r in hr], size))
for (num, tl, desc), b in zip(CARDS, boxes):
    x0, y0, x1, y1 = b
    out.append('<div class="ecard" style="left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;"></div>' % (x0 * S, y0 * S, (x1 - x0) * S, (y1 - y0) * S))
    # photo = the non-white block in the lower part of the card
    sub = im[y0:y1, x0:x1]
    nonw = (sub.min(axis=2) < 235).astype(np.uint8)
    nonw[: int(0.5 * (y1 - y0)), :] = 0
    nonw = cv2.morphologyEx(nonw, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    rowfrac = nonw.mean(axis=1)
    good = (rowfrac > 0.55).astype(np.uint8)
    # photo = the longest run of full-width rows (text lines are only a few px tall)
    best, cur, st0 = (0, 0), 0, 0
    for k, v in enumerate(good):
        if v:
            if cur == 0: st0 = k
            cur += 1
            if cur > best[0]: best = (cur, st0)
        else: cur = 0
    ys = np.arange(best[1], best[1] + best[0])
    cols = np.where(nonw[ys.min():ys.max() + 1].mean(axis=0) > 0.5)[0]
    px0, py0, px1, py1 = cols.min() + x0, ys.min() + y0, cols.max() + x0 + 1, ys.max() + y0 + 1
    pname = save("exp_%s.jpg" % num, im[py0:py1, px0:px1])
    out.append('<div class="ph" style="left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;background-image:url({{IMG:%s}})"></div>' % (px0 * S, py0 * S, (px1 - px0) * S, (py1 - py0) * S, "two/" + pname))
    rr = [r for r in runs_of(ink, x0 + 6, x1 - 6, y0 + 6, py0 - 4, merge_gap=1) if r["y1"] - r["y0"] >= 5]
    need = 1 + len(tl) + len(desc)
    if len(rr) != need:
        # number + titles are separate rows; the description lines (tight spacing) may be merged -> split evenly
        head = rr[: 1 + len(tl)]
        tail = rr[1 + len(tl):]
        if tail:
            blk = dict(y0=tail[0]["y0"], y1=tail[-1]["y1"])
            tail = split_equal(ink, blk, len(desc), x0 + 6, x1 - 6)
        rr = head + tail
        print("  card", num, "split ->", len(rr), "rows (need %d)" % need)
    nr = rr[0]
    out.append(T(num, nr["x0"] * S, (nr["y0"] + nr["y1"]) / 2 * S, (nr["y1"] - nr["y0"]) / 0.72 * S, "l", None, cls="enum"))
    for t, r in zip(tl, rr[1:1 + len(tl)]):
        out.append(T(t, r["x0"] * S, (r["y0"] + r["y1"]) / 2 * S, (r["y1"] - r["y0"]) / 0.72 * S, "r", None, cls="etitle"))
    tail0 = [r for r in rr[1 + len(tl):]]
    y_first = tail0[0]["y0"]
    xl = min(r["x0"] for r in tail0)
    for k, t in enumerate(desc):
        out.append(T(t, xl * S, (y_first + 7 + 15 * k) * S, 9.7, "r", "#222", cls="edesc"))
out.append("</section>")
res["expertise"] = "\n".join(out)

# ================================================================== ORG STRUCTURE
im = cv2.imread(os.path.join(IMGDIR, "58.jpg"))
H, W = im.shape[:2]
PEOPLE = [
    ("Lavinder Duggal", ["Founder & MD"]), ("Bhupinder Duggal", ["President"]),
    ("Vishal Jadhav", ["National Director"]), ("Jasraj Chauhan", ["VP - Sales & key accounts"]), ("Harkirat Duggal", ["Business Strategist & Int.", "Markets"]),
    ("Lalita P.", ["Head Procurement"]), ("Kunal P.", ["Head  Technology"]), ("Sachin Baraskar", ["National MEP Head"]), ("Dharmendra Tambe", ["General Manager", "ELV & BMS"]),
    ("Ashok Nayak", ["Director"]), ("Anuj Nigam", ["CGO"]), ("Shiv Kumar", ["Head Service"]), ("Sanjay Panchal", ["AGM - Design"]),
    ("Vigeshvar Durairaj", ["Regional Head - South,", "Projects & Operations"]), ("Syam Das", ["Head - Testing &", "Commissioning"]),
]
m = (im.min(axis=2) < 238).astype(np.uint8)
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((17, 17), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(m)
photos, bar = [], None
for i in range(1, n):
    x, y, bw, bh, a = st[i]
    if bw > 800 and 15 < bh < 60:
        bar = [x, y, x + bw, y + bh]
    elif 110 <= bw <= 175 and 85 <= bh <= 150:
        if bh > 125 and y > 330: bh = 111
        photos.append([x, y, x + bw, y + bh])
print("photos", len(photos), "bar", bar)
lead = sorted([p for p in photos if p[1] < 330], key=lambda p: p[0])
rest = [p for p in photos if p[1] >= 330]
row1 = sorted([p for p in rest if p[1] < 600], key=lambda p: p[0])
row2 = sorted([p for p in rest if p[1] >= 600], key=lambda p: p[0])
order = lead + row1 + row2
assert len(order) == 15, len(order)
# vertical dividers (thin, tall) -> removed from the ink mask, drawn as rules
ink = (im.min(axis=2) < 150).astype(np.uint8)
light = (im.min(axis=2) < 235).astype(np.uint8)
vlines = []
for x in range(W):
    col = light[bar[3] + 5: bar[3] + 380, x]
    if col.mean() > 0.9: vlines.append(x)
vx = []
for x in vlines:
    if not vx or x - vx[-1][-1] > 2: vx.append([x])
    else: vx[-1].append(x)
vx = [int(np.mean(v)) for v in vx]
vx = [365, 722, 1088]
for v in vx:
    ink[:, v - 3:v + 4] = 0
out = ['<section class="pj pj-o" data-block="pj_orgstructure">']
tr = [r for r in runs_of(ink, 20, 560, 20, 190) if r["y1"] - r["y0"] > 20]
size = np.median([(r["y1"] - r["y0"]) / 0.72 for r in tr]) * S
out.append(G.title_html([[("ORG", "b", 0)], [("STRUCTURE", "l", 0)]], tr[0]["x0"] * S, [(r["y0"] + r["y1"]) / 2 * S for r in tr], size))
# LEADERSHIP label
lr = [r for r in runs_of(ink, 400, 1200, 140, 185) if r["y1"] - r["y0"] > 8]
r = lr[0]
out.append(T("LEADERSHIP", (r["x0"] + r["x1"]) / 2 * S, (r["y0"] + r["y1"]) / 2 * S, (r["y1"] - r["y0"]) / 0.72 * S, "b", None, align="c"))
# bar + labels
out.append('<i class="obar" style="left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;"></i>' % (bar[0] * S, bar[1] * S, (bar[2] - bar[0]) * S, (bar[3] - bar[1]) * S))
dark = (im.min(axis=2) < 120).astype(np.uint8)
br = runs_of(dark, bar[0] + 3, bar[2] - 3, bar[1] + 2, bar[3] - 2, merge_gap=3)
labels = ["DIRECTORS", "STRATEGY & SALES", "DIVISIONAL LEADERSHIP", "MEP LEADERSHIP"]
# one run holds all four labels: split by wide gaps
if br:
    gs = br[0]["groups"]
    # merge groups closer than 60px (words of one label)
    merged = []
    for a, b in gs:
        if merged and a - merged[-1][1] < 55: merged[-1][1] = b
        else: merged.append([a, b])
    cyb = (br[0]["y0"] + br[0]["y1"]) / 2
    fs = (br[0]["y1"] - br[0]["y0"]) / 0.72 * S
    print("labels", len(merged))
    for lab_, (a, b) in zip(labels, merged):
        out.append(T(lab_, a * S, cyb * S, fs, "b", "#2a2a2a"))
for v in vx:
    out.append('<i class="ovline" style="left:%.1fpx;top:%.1fpx;height:%.1fpx;"></i>' % (v * S, bar[3] * S, (803 - bar[3]) * S))
# people
for i, ((name, roles), b) in enumerate(zip(PEOPLE, order)):
    x0, y0, x1, y1 = b
    pn = save("org_%02d.jpg" % i, im[y0:y1, x0:x1])
    out.append('<div class="ph rnd2" style="left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;background-image:url({{IMG:%s}})"></div>' % (x0 * S, y0 * S, (x1 - x0) * S, (y1 - y0) * S, "two/" + pn))
    if i < 2:  # the two leaders: fixed text rows (names / roles at the same sizes as the rest)
        cx = (x0 + x1) / 2
        out.append(T(name, cx * S, 331 * S, 10.0, "b", None, align="c"))
        out.append(T(roles[0], cx * S, 348 * S, 7.0, "r", "#333", align="c"))
        continue
    below = [q[1] for q in order if q[1] > y1 + 5 and not (q[2] < x0 - 10 or q[0] > x1 + 10)]
    by1 = min(below) - 4 if below else (bar[1] - 6 if y0 < 330 else 805)
    rr = [r for r in runs_of(ink, x0 - 25, x1 + 25, y1 + 3, by1, merge_gap=1) if r["y1"] - r["y0"] >= 5]
    need = 1 + len(roles)
    if len(rr) > need:
        rr = fix_runs(ink, rr, need, x0, x1, y1, by1)
    if len(rr) != need:
        print("  !! person", name, len(rr), "expected", need)
        cx = (x0 + x1) / 2
        rr = [dict(y0=y1 + 8 + k * 14, y1=y1 + 20 + k * 14, x0=cx - 40, x1=cx + 40) for k in range(need)]
    cx0 = (x0 + x1) / 2
    for k, (tx, r) in enumerate(zip([name] + roles, rr)):
        cx = (r["x0"] + r["x1"]) / 2
        out.append(T(tx, cx * S, (r["y0"] + r["y1"]) / 2 * S, fsize(r["y1"] - r["y0"], tx) * S, "b" if k == 0 else "r", None if k == 0 else "#333", align="c"))
out.append(G.logo_html(im, S, []))
out.append("</section>")
res["orgstructure"] = "\n".join(out)
json.dump(res, open("two_slides.json", "w"))
print("ok")
