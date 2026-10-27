# -*- coding: utf-8 -*-
"""'Sectors We Deliver Across' (major_projects_fixed) laid out by hand on the Slide Standard.
The original card grid sized itself from the browser window, so in small previews it re-flowed to
4 columns and ran off the slide. Now: fixed 1280 x 720, eyebrow in the top margin, heading at the
54/54 pt corner, 10 cards in two rows of five. Same look: warm background, white rounded cards,
red index number, dark sector name. Writes tools/standard/sectors_result.json for apply.py."""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
orig = json.load(open(os.path.join(HERE, "originals.json"), encoding="utf-8"))["major_projects_fixed"]
app = open(os.path.join(os.path.dirname(os.path.dirname(HERE)), "src", "frontend", "app.html"), encoding="utf-8").read()
LOGO = re.search(r'class=\\"ss-logo\\" src=\\"([^"\\]+)\\"', app).group(1)

eyebrow = re.search(r'class="eyebrow">([^<]+)<', orig).group(1)
head = re.search(r"<h2>([^<]+)</h2>", orig).group(1)
cards = re.findall(r'sector-card__index">(\d+)</span><h3>([^<]+)</h3>', orig)

L, R, T, B, GAP = 72.0, 1208.0, 72.0, 656.0, 24.0
HEAD_H = 66.667 * 1.05
top = T + HEAD_H + 40
per = 5
cw = (R - L - (per - 1) * GAP) / per
ch = (B - top - GAP) / 2      # two rows filling the space down to the bottom margin


def f(v):
    return "%.1fpx" % v


out = ['<section class="ss-sectors" data-block="major_projects_fixed">',
       '<p class="ss-sec-eyebrow t-caption is-b">%s</p>' % eyebrow,
       '<h2 class="ss-head">%s</h2>' % head]
for i, (n, name) in enumerate(cards):
    r, c = divmod(i, per)
    x, y = L + c * (cw + GAP), top + r * (ch + GAP)
    out.append('<div class="ss-sec-card" style="left:%s;top:%s;width:%s;height:%s;"><span class="t-caption is-b ss-sec-n">%s</span><h3 class="t-detail is-r ss-sec-name">%s</h3></div>' % (
        f(x), f(y), f(cw), f(ch), n, name.replace("&", "&amp;")))
out.append('<footer class="ss-foot"><span class="ss-pn"></span><img class="ss-logo" src="%s" alt="HTL"></footer>' % LOGO)
out.append("</section>")
bottom = top + 2 * ch + GAP
assert bottom <= B, bottom
json.dump({"major_projects_fixed": {"html": "".join(out), "flags": []}}, open(os.path.join(HERE, "sectors_result.json"), "w", encoding="utf-8"), ensure_ascii=False)
print("ok, %d cards, bottom %.0f" % (len(cards), bottom))
