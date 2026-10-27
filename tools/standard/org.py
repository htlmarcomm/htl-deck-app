# -*- coding: utf-8 -*-
"""Org Structure on the Slide Standard, laid out by hand (too dense for the generic normaliser).
Same design: bold/light heading, leadership pair, grey department bar, 2 rows of people under it,
names + titles centred under their photo. Seven equal person columns across the safe area, so no
caption can run into its neighbour; photos keep their original proportions.
Writes tools/standard/org_result.json for apply.py."""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
orig = json.load(open(os.path.join(HERE, "originals.json"), encoding="utf-8"))["pj_orgstructure"]
app = open(os.path.join(os.path.dirname(os.path.dirname(HERE)), "src", "frontend", "app.html"), encoding="utf-8").read()
LOGO = re.search(r'class=\\"ss-logo\\" src=\\"([^"\\]+)\\"', app).group(1)

# people from the original slide: photo, then its name + title lines, in order
items = re.findall(r'<(div|span) class="([^"]*)" style="([^"]*)">(.*?)</\1>', orig)
people, cur = [], None
for tag, cls, style, inner in items:
    if "pj-ph" in cls:
        cur = {"img": re.search(r"url\(([^)]+)\)", style).group(1), "lines": []}
        people.append(cur)
    elif "pj-t" in cls and cur is not None:
        txt = re.sub(r"<[^>]+>", "", inner).strip()
        if txt.isupper() and len(txt) > 6 and not cur["lines"]:
            continue  # a department label, not a caption
        cur["lines"].append(txt)
by_name = {p["lines"][0]: p for p in people}


def person(name):
    p = by_name[name]
    return p["img"], name, " ".join(p["lines"][1:])


M = dict(l=72.0, r=1208.0, t=72.0, b=656.0)
GAP = 24.0
P = (M["r"] - M["l"] - 6 * GAP) / 7            # one person column
PW, PH = 115.0, 90.0                            # photo, original proportion (~1.25:1)
CAP = 12 * 1.3                                  # caption line
pcx = lambda i: M["l"] + i * (P + GAP)


def f(v):
    return "%.1fpx" % v


out = ['<section class="pj pj-org ss-org" data-block="pj_orgstructure">',
       '<h2 class="ss-head"><span class="is-b">ORG</span><span class="is-l"> STRUCTURE</span></h2>']


def card(x, y, name):
    img, n, title = person(name)
    out.append('<div class="pj-ph pj-rnd2" style="left:%s;top:%s;width:%s;height:%s;background-image:url(%s)"></div>' % (f(x + (P - PW) / 2), f(y), f(PW), f(PH), img))
    out.append('<div class="ss-tb ss-tb--under" style="left:%s;top:%s;width:%s;"><p class="t-caption is-b">%s</p><p class="t-caption is-r">%s</p></div>' % (f(x), f(y + PH + 8), f(P), n, title))


# leadership pair, top right beside the heading
lx2 = M["r"] - P
lx1 = lx2 - P - GAP
out.append('<div class="ss-tb ss-tb--under" style="left:%s;top:%s;width:%s;"><p class="t-caption is-b">LEADERSHIP</p></div>' % (f(lx1), f(M["t"]), f(2 * P + GAP)))
card(lx1, M["t"] + CAP + 8, "Lavinder Duggal")
card(lx2, M["t"] + CAP + 8, "Bhupinder Duggal")
lead_bottom = M["t"] + CAP + 8 + PH + 8 + 2 * CAP

# department bar
bar_top = max(M["t"] + 66.667 * 1.05 + 40, lead_bottom + 16)
BAR_H = 28.0
out.append('<i class="pj-obar" style="left:%s;top:%s;width:%s;height:%s;"></i>' % (f(M["l"]), f(bar_top), f(M["r"] - M["l"]), f(BAR_H)))
for i, lab in ((0, "DIRECTORS"), (1, "STRATEGY &amp; SALES"), (3, "DIVISIONAL LEADERSHIP"), (5, "MEP LEADERSHIP")):
    out.append('<div class="ss-tb" style="left:%s;top:%s;"><p class="t-caption is-b">%s</p></div>' % (f(pcx(i) + 8), f(bar_top + (BAR_H - CAP) / 2), lab))

row1 = bar_top + BAR_H + 16
row_h = PH + 8 + CAP + 3 * CAP + 16
row2 = row1 + row_h
for col, row, name in ((0, 1, "Vishal Jadhav"), (0, 2, "Ashok Nayak"),
                       (1, 1, "Jasraj Chauhan"), (2, 1, "Harkirat Duggal"), (1, 2, "Anuj Nigam"),
                       (3, 1, "Lalita P."), (4, 1, "Kunal P."), (3, 2, "Shiv Kumar"), (4, 2, "Sanjay Panchal"),
                       (5, 1, "Sachin Baraskar"), (6, 1, "Dharmendra Tambe"), (5, 2, "Vigeshvar Durairaj"), (6, 2, "Syam Das")):
    card(pcx(col), row1 if row == 1 else row2, name)
bottom = row2 + PH + 8 + CAP + 3 * CAP
for i in (1, 3, 5):   # rules between the department groups
    out.append('<i class="pj-ovline" style="left:%s;top:%s;height:%s;"></i>' % (f(pcx(i) - GAP / 2), f(bar_top + BAR_H), f(bottom - bar_top - BAR_H)))
out.append('<footer class="ss-foot"><span class="ss-pn"></span><img class="ss-logo" src="%s" alt="HTL"></footer>' % LOGO)
out.append("</section>")
html = "\n".join(out)
assert bottom <= M["b"] + 0.5, ("does not fit", bottom)
json.dump({"pj_orgstructure": {"html": html, "flags": ["laid out by hand: 7 equal person columns (7 does not divide the 12-column grid; the groups and the bar span the full safe area)"]}},
          open(os.path.join(HERE, "org_result.json"), "w", encoding="utf-8"), ensure_ascii=False)
print("ok: %d people, bottom %.0f px (limit %.0f)" % (len(people), bottom, M["b"]))
