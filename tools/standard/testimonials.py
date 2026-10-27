# -*- coding: utf-8 -*-
"""Client Testimonials laid out by hand on the Slide Standard: heading at the 54/54 pt corner, the three
letters at one shared height, as large as the safe-area width allows (edge to edge, 24 px gutters),
top-aligned under the heading. Writes tools/standard/testimonials_result.json for apply.py.
(The letter images are ~300 px screenshots; this is ~1.25x, about the most before they blur.)"""
import json
import os
import re

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
orig = json.load(open(os.path.join(HERE, "originals.json"), encoding="utf-8"))["client_testimonials"]
app = open(os.path.join(ROOT, "src", "frontend", "app.html"), encoding="utf-8").read()
LOGO = re.search(r'class=\\"ss-logo\\" src=\\"([^"\\]+)\\"', app).group(1)

imgs = re.findall(r"background-image:url\('?([^')]+)'?\)", orig)
aspect = [Image.open(os.path.join(ROOT, "public", u.lstrip("/"))).size for u in imgs]
aspect = [w / h for w, h in aspect]
L, R, T, GAP = 72.0, 1208.0, 72.0, 24.0
H = (R - L - GAP * (len(imgs) - 1)) / sum(aspect)
top0 = T + 66.667 * 1.05 + 40
# centred in the space between the heading and the bottom margin, so the slide is evenly balanced
top = top0 + max(0.0, (656.0 - top0 - H) / 2)


def f(v):
    return "%.1fpx" % v


out = ['<section class="tm ss-tm" data-block="client_testimonials">',
       '<h2 class="ss-head"><span class="is-b">CLIENT</span><span class="is-l"> TESTIMONIALS</span></h2>']
x = L
for u, a in zip(imgs, aspect):
    out.append('<div class="tm-card" style="left:%s;top:%s;width:%s;height:%s;background-image:url(\'%s\')"></div>' % (f(x), f(top), f(H * a), f(H), u))
    x += H * a + GAP
out.append('<footer class="ss-foot"><span class="ss-pn"></span><img class="ss-logo" src="%s" alt="HTL"></footer>' % LOGO)
out.append("</section>")
json.dump({"client_testimonials": {"html": "".join(out), "flags": []}}, open(os.path.join(HERE, "testimonials_result.json"), "w", encoding="utf-8"), ensure_ascii=False)
print("ok: cards %.0f px tall, %.2fx the image size, bottom %.0f" % (H, H / 209, top + H))
