# -*- coding: utf-8 -*-
"""Slide Standard for the "add slide" templates: new blank / table / text slides start on the grid.
Positions are in the custom-slide canvas, which the app lays out at 1280 x 720 (1 pt = 4/3 px):
  heading at 54/54 pt, first body block 30 pt under the heading, text boxes 5 columns wide,
  tables 12 columns wide; footer (page number + logo) in the bottom margin.
Run once (asserts on exact strings)."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = 1280 / 960.0
ML = round(54 * P, 1)                                  # 72
TOP = round(54 * P, 1)                                 # heading top
BODY_Y = round((54 + 50 * 1.05 + 30) * P, 1)           # first body block under a one-line heading
W5 = round((5 * 54.5 + 4 * 18) * P, 1)                 # 5 columns
W12 = round((12 * 54.5 + 11 * 18) * P, 1)              # full width


def patch(path, pairs):
    p = os.path.join(ROOT, path)
    s = open(p, encoding="utf-8").read()
    for a, b in pairs:
        assert s.count(a) == 1, (path, s.count(a), a[:70])
        s = s.replace(a, b)
    open(p, "w", encoding="utf-8").write(s)


app = os.path.join(ROOT, "src", "frontend", "app.html")
logo = re.search(r'class=\\"ss-logo\\" src=\\"([^"\\]+)\\"', open(app, encoding="utf-8").read()).group(1)

patch("src/frontend/app.html", [
    ("var CS_DEFAULT_BOX = { text: {w: 420, h: 90}, image: {w: 380, h: 260}, graph: {w: 460, h: 260}, table: {w: 1060, h: 0} };",
     "var CS_DEFAULT_BOX = { text: {w: %s, h: 90}, image: {w: 380, h: 260}, graph: {w: 460, h: 260}, table: {w: %s, h: 0} };" % (W5, W12)),
    ("    return { x: 90 + (n % 6) * 36, y: 90 + (n % 6) * 36 };",
     "    // Slide Standard: first box on the left margin, under the heading area; later ones cascade\n"
     "    return { x: %s + (n %% 6) * 36, y: %s + (n %% 6) * 36 };" % (ML, BODY_Y)),
    ("    return '<div class=\"cs-slide-canvas\">' + body + '</div>';",
     "    body += '<footer class=\"ss-foot\"><span class=\"ss-pn\"></span><img class=\"ss-logo\" src=\"%s\" alt=\"HTL\"></footer>';\n"
     "    return '<div class=\"cs-slide-canvas\">' + body + '</div>';" % logo),
])
patch("public/table-slide.js", [
    ('{ id: csNewId(), type: "text", text: title, x: 60, y: 34, w: 1060, size: "header" },',
     '{ id: csNewId(), type: "text", text: title, x: %s, y: %s, w: %s, size: "header" },' % (ML, TOP, W12)),
    ('{ id: csNewId(), type: "table", x: 60, y: 128, w: 1060,',
     '{ id: csNewId(), type: "table", x: %s, y: %s, w: %s,' % (ML, BODY_Y, W12)),
])
patch("public/sources.js", [
    ('s.elements.push({ id: csNewId(), type: "text", text: body, x: pos.x, y: pos.y, w: 760, size: "body" });',
     's.elements.push({ id: csNewId(), type: "text", text: body, x: pos.x, y: pos.y, w: %s, size: "body" });' % W5),
    ('elements: [{ id: csNewId(), type: "text", text: body, x: 60, y: 60, w: 1000',
     'elements: [{ id: csNewId(), type: "text", text: body, x: %s, y: %s, w: %s' % (ML, BODY_Y, W5)),
])
print("templates patched", ML, TOP, BODY_Y, W5, W12)
