# -*- coding: utf-8 -*-
"""Replaces the Journey master slide (htl_journey) with the user's new
"Stability & Longevity" design (pj_journey): Our Milestones cards + Expansion
timeline. Built by hand from the screenshot in tools/bira_slides/assets_journey/source.jpg
(1600x860, drawn here at 0.8 scale on the 1280x720 page). Illustrations are crops
of that screenshot. The old htl_journey snippet stays so saved decks still open."""
import hashlib
import json
import os
import re

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "tools", "bira_slides", "assets_journey")
APP = os.path.join(ROOT, "src", "frontend", "app.html")
s = open(APP, encoding="utf-8").read()

K = 0.8          # screenshot px -> slide px
OY = 16          # 860*0.8 = 688, centred on the 720 page

# ---- illustrations (crop boxes in screenshot px: x0, y0, x1, y1)
BOXES = {
    "trophy": (95, 699, 137, 747), "pune": (275, 689, 396, 752), "delhi": (479, 698, 609, 753),
    "hyderabad": (680, 709, 850, 756), "datacentre": (950, 688, 1005, 747), "dubai": (1084, 689, 1298, 756),
    "biopharma": (1414, 702, 1507, 722),
}
src = cv2.imread(os.path.join(ASSETS, "source.jpg"))


def crop(name):
    x0, y0, x1, y1 = BOXES[name]
    im = src[y0:y1, x0:x1].copy()
    m = (im.min(axis=2) < 240).astype(np.uint8)
    k, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    for i in range(1, k):  # drop stubs of the grey connector lines
        x, y, w, h, a = st[i]
        if h <= 5 and w >= 8 and a <= w * 4:
            im[lab == i] = 255
    im[im.min(axis=2) >= 244] = 255
    ok, buf = cv2.imencode(".png", im)
    raw = buf.tobytes()
    fn = hashlib.sha1(raw).hexdigest()[:16] + ".png"
    p = os.path.join(ROOT, "public", "media", fn)
    if not os.path.exists(p):
        open(p, "wb").write(raw)
    return "/media/" + fn


def px(v):
    return "%.1fpx" % v


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def T(x, cap_top, size, html, cls="", extra=""):
    """text whose capital letters start at screenshot y=cap_top"""
    top = cap_top * K + OY - 0.2 * size
    return '<span class="pj-t %s" style="left:%s;top:%s;font-size:%s;%s">%s</span>' % (cls, px(x * K), px(top), px(size), extra, html)


def line(x, cap_top, size, parts, color="#5b5b5b"):
    """one line made of regular + **bold** parts, each its own editable leaf"""
    top = cap_top * K + OY - 0.2 * size
    inner = "".join('<strong>%s</strong>' % esc(p[2:-2]) if p.startswith("**") else '<span>%s</span>' % esc(p) for p in parts)
    return '<p class="pj-t pj-jl" style="left:%s;top:%s;font-size:%s;color:%s;">%s</p>' % (px(x * K), px(top), px(size), color, inner)


out = ['<section class="pj pj-j" data-block="pj_journey">']
out.append('<div class="pj-ttl" style="left:%s;top:%s;font-size:51px;"><span class="pj-tb">STABILITY</span><span class="pj-tl"> &amp; LONGEVITY</span></div>' % (px(33 * K), px(32 * K + OY - 10)))
out.append(T(35, 198, 27, "OUR MILESTONES", "pj-jh"))

CARDS = [
    (34, "2004", 11.2, 17, [["Established ", "**HTL Aircon**"], ["and executed 1st VRV"], ["project with Daikin"]]),
    (251, "2010", 11.2, 17, [["Made inroads into mid-"], ["size ", "**fit out projects**"]]),
    (469, "2017", 12.3, 18.5, [["Reached the ", "**100 CR**"], ["**turnover mark.**"], ["Won India’s Top 100"], ["SME Award"]]),
    (686, "2018", 11.2, 17, [["Started with ", "**MEP**"], ["**Contracting**"], ["10000 HP with Daikin."]]),
    (904, "2019", 11.2, 17, [["Won ", "**India’s Top 100**"], ["**SME Award.**"], ["400+ employees with 175"], ["cr. Top line achieved"]]),
    (1121, "2021", 12.3, 18.5, [["Executed ", "**50 MW of**"], ["**Data Centre**"]]),
    (1338, "2026", 12.3, 18.5, [["Executed ", "**221 MW**"], ["of Data Centre"]]),
]
for x, year, fs, lh, lines in CARDS:
    out.append('<div class="pj-jcard" style="left:%s;top:%s;width:%s;height:%s;"></div>' % (px(x * K), px(250 * K + OY), px(199 * K), px(255 * K)))
    out.append(T(x + 27, 343, 43, year, "pj-jyear"))
    for i, parts in enumerate(lines):
        out.append(line(x + 23, 398 + i * lh, fs, parts))

out.append(T(40, 585, 27, "EXPANSION", "pj-jh"))
STOPS = [  # centre x, label lines, label cap top, illustration, year, year cap top
    (115, ["YEAR OF", "COMMENCEMENT"], 638, "trophy", "1996", 768),
    (329, ["PUNE", "BRANCH"], 638, "pune", "2010", 768),
    (543, ["DELHI", "BRANCH"], 638, "delhi", "2014", 768),
    (763, ["HYDERABAD", "BRANCH"], 638, "hyderabad", "2016", 768),
    (977, ["DATA", "CENTRE"], 638, "datacentre", "2020", 768),
    (1177, ["EXPANSION", "TO DUBAI"], 638, "dubai", "2023", 768),
    (1460, ["HTL", "BIOPHARMA"], 634, "biopharma", "2025", 764),
]
C = "transform:translateX(-50%);text-align:center;"
for cx, lab, lt, ill, yr, yt in STOPS:
    for i, t in enumerate(lab):
        out.append(T(cx, lt + i * 20.5, 11.2, esc(t), "pj-jlab", C))
    x0, y0, x1, y1 = BOXES[ill]
    out.append('<div class="pj-ph pj-jill" style="left:%s;top:%s;width:%s;height:%s;background-image:url(%s)"></div>' % (
        px(x0 * K), px(y0 * K + OY), px((x1 - x0) * K), px((y1 - y0) * K), crop(ill)))
    out.append(T(cx, yt, 22.4, yr, "pj-jyr", C))
for x0, x1, y in [(175, 236, 722), (388, 448, 719), (627, 688, 716), (813, 875, 713), (1020, 1082, 713), (1300, 1361, 710)]:
    out.append('<i class="pj-jline" style="left:%s;top:%s;width:%s;"></i>' % (px(x0 * K), px(y * K + OY), px((x1 - x0) * K)))
out.append("</section>")
SNIP = "\n".join(out)


def sw(o, n):
    global s
    assert s.count(o) == 1, (s.count(o), o[:90])
    s = s.replace(o, n)


def edit_json(marker, fn):
    global s
    a = s.find(marker)
    o = s.find(">", a) + 1
    e = s.find("</script>", o)
    orig = s[o:e]
    compact = '": "' not in orig[:400]
    data = fn(json.loads(orig))
    out_ = json.dumps(data, ensure_ascii=False, separators=(",", ":") if compact else None).replace("</script", "<\\/script")
    s = s[:o] + out_ + s[e:]


def snip(d):
    d["pj_journey"] = SNIP
    return d


edit_json('id="all-snippets-data"', snip)
edit_json('id="workspace-data"', lambda d: [{"key": "pj_journey", "label": "Journey", "kind": "static", "slots": []} if x["key"] == "htl_journey" else x for x in d])

sw("    htl_journey: 1248,\n", "    htl_journey: 1248,\n    pj_journey: 1280,\n")
sw("    htl_journey: ['stagger', '.journey-milestone'],\n", "    htl_journey: ['stagger', '.journey-milestone'],\n    pj_journey: ['stagger', '.pj-jcard'],\n")
CSS = """
  .real-scope .pj .pj-jcard{position:absolute; background:#f3f3f3; border-radius:11px; display:block;}
  .real-scope .pj .pj-jh{font-weight:400; color:#111; letter-spacing:.005em;}
  .real-scope .pj .pj-jyear{font-weight:700; color:#e3262c; letter-spacing:-.01em;}
  .real-scope .pj .pj-jl{line-height:1.15;} .real-scope .pj .pj-jl strong{font-weight:700; color:#3a3a3a;}
  .real-scope .pj .pj-jlab{font-weight:400; color:#5b5b5b; letter-spacing:.02em;}
  .real-scope .pj .pj-jyr{font-weight:300; color:#555;}
  .real-scope .pj .pj-jill{background-color:transparent; background-size:contain; background-repeat:no-repeat;}
  .real-scope .pj .pj-jline{position:absolute; height:1px; background:#bdbdbd; display:block;}
"""
sw("  .ws-card-remove{position:absolute; top:6px; right:6px;", CSS + "\n  .ws-card-remove{position:absolute; top:6px; right:6px;")
sw('<div class="thumb-stage real-scope" data-key="htl_journey"></div>', '<div class="thumb-stage real-scope" data-key="pj_journey"></div>')

mm = re.search(r'var PROFILE_DECK_KEYS = \[(.*?)\];', s)
keys = ["pj_journey" if k == "htl_journey" else k for k in json.loads("[" + mm.group(1) + "]")]
s = s[:mm.start()] + "var PROFILE_DECK_KEYS = " + json.dumps(keys, separators=(",", ":")) + ";" + s[mm.end():]
open(APP, "w", encoding="utf-8").write(s)
print("ok", len(SNIP))
