# -*- coding: utf-8 -*-
"""Adds four slides to the "Internal Systems & Processes" section (Master Profile
Deck), built from the supplied screenshots, each at its own reference width
(SLIDE_LAYOUT_W) and scaled to the 1180px slide:
  driving_projects_innovation  - Driving Projects with Innovation
  planning_erp_system          - Planning: ERP System
  project_dashboard_reporting  - Project Dashboard & Reporting
  innovation_in_designing      - Innovation in Designing
Edits src/frontend/app.html (kept for provenance)."""
import hashlib
import io
import json
import math
import os
import re

from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, "src", "frontend", "app.html")
IMGDIR = r"C:\Users\anush\AppData\Local\Temp\claude\C--Users-anush-Downloads-htl-block-library--1-\e2e48ebc-294d-4beb-b54e-d94cd56a3cda\images"


def shot(n):
    return Image.open(os.path.join(IMGDIR, "%d.png" % n)).convert("RGB")


def store(im, q=92):
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q)
    raw = buf.getvalue()
    name = hashlib.sha1(raw).hexdigest()[:16] + ".jpg"
    open(os.path.join(ROOT, "public", "media", name), "wb").write(raw)
    return "/media/" + name


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


s = open(APP, encoding="utf-8").read()
LOGO = re.search(r'class=\\"tm-logo\\" src=\\"([^"\\]+)\\"', s).group(1)
LOGO_IMG = '<img class="%s-logo" src="%s" alt="HTL">'

SLIDES = []  # (key, label, width, html)

# ------------------------------------------------------------ 1. Driving projects
im = shot(42)
photo = store(im.crop((77, 172, 445, 476)))
items = [("PLANNING", "MSP | ERP SYSTEM", 208), ("DESIGNING", "AUTO CAD | 3D & 4D BIM | AUTODESK", 310), ("PROJECT MANAGEMENT", "VIRTUAL PROJECT MANAGEMENT", 411)]
rows = ""
for head, sub, y in items:
    rows += ('<strong class="di-h" style="top:%dpx">%s</strong><i class="di-rule" style="top:%dpx"></i><span class="di-s" style="top:%dpx">%s</span>'
             % (y - 14, esc(head), y + 24, y + 33, esc(sub)))
html1 = ('<section class="di" data-block="driving_projects_innovation">'
         '<div class="di-title"><span class="di-light">DRIVING PROJECTS WITH</span> <strong class="di-bold">INNOVATION</strong></div>'
         '<div class="di-photo" style="background-image:url(\'%s\')"></div>%s%s</section>' % (photo, rows, LOGO_IMG % ("di", LOGO)))
SLIDES.append(("driving_projects_innovation", "Driving Projects with Innovation", 1008, html1))

# ------------------------------------------------------------ 2. Planning: ERP system
im = shot(43)
W, H = 248, 570
panel = Image.new("RGB", (W, H))
base = im.crop((0, 150, W, H))
panel.paste(base, (0, 150))
strip = im.crop((0, 152, W, 190)).resize((W, 150), Image.BICUBIC).filter(ImageFilter.GaussianBlur(6))
panel.paste(strip, (0, 0))
panel_url = store(panel)

# dots, traced from the screenshot
GRAY, PINK, RED, DARK = "#9a9a9a", "#f48a8a", "#ee2b33", "#2b2b2b"
dots = []
vy = [(257, DARK), (278, "#555"), (300, "#666"), (321, GRAY), (342, GRAY), (364, GRAY), (385, PINK), (407, RED), (428, RED)]
for y, c in vy:
    dots.append((329, y, c))
for i in range(27):
    x = 525 + 21.67 * (i - 8)
    if x >= 349:
        dots.append((round(x, 1), 300, GRAY))
by = [(321, GRAY), (343, GRAY), (364, GRAY), (386, PINK), (407, RED), (429, RED)]
for bx in (525, 720, 916):
    for y, c in by:
        dots.append((bx, y, c))
svg = '<svg class="pe-dots" viewBox="0 0 1010 570" aria-hidden="true">'
for x, y, c in dots:
    svg += '<circle cx="%s" cy="%s" r="2.7" fill="%s"/>' % (x, y, c)
for x, y in ((329, 230), (328, 455), (525, 455), (720, 455), (916, 456)):
    svg += '<circle cx="%d" cy="%d" r="9.5" fill="#dcdcdc"/><circle cx="%d" cy="%d" r="3.2" fill="%s"/>' % (x, y, x, y, RED)
svg += "</svg>"

labels = [(336, "DOCUMENT LIBRARY", "for All Technical Data Sheets"), (524, "MRN", "Material Request Note"),
          (720, "PO PREPARATION", "Draft & Final PO"), (916, "INDIVIDUAL DASHBOARD", "for All Departments")]
lab = ""
for x, a, b in labels:
    lab += ('<strong class="pe-lh" style="left:%dpx;top:484px">%s</strong><span class="pe-ls" style="left:%dpx;top:502px">%s</span>'
            % (x - 120, esc(a), x - 120, esc(b)))
html2 = ('<section class="pe" data-block="planning_erp_system">'
         '<div class="pe-left" style="background-image:url(\'%s\')"></div>'
         '<strong class="pe-t1">PLANNING</strong><span class="pe-t2" style="top:72px">ERP</span><span class="pe-t2" style="top:110px">SYSTEM</span>'
         '<i class="pe-vline"></i><span class="pe-pct">100%%</span>'
         '<span class="pe-note">Understanding project goals, BIM\nclash detection &amp; service co-\nordination before mobilisation</span>'
         '%s<strong class="pe-top" style="left:209px;top:169px">INTERNAL\nERP SYSTEM</strong>%s</section>' % (panel_url, svg, lab))
SLIDES.append(("planning_erp_system", "Planning \u2014 ERP System", 1010, html2))

# ------------------------------------------------------------ 3. Project dashboard & reporting
im = shot(44)
SHOTS = [(55, 117, 428, 324), (446, 117, 829, 326), (277, 333, 729, 542)]
shots = ""
for (l, t, r, b) in SHOTS:
    shots += ('<div class="pd-shot" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx;background-image:url(\'%s\')"></div>'
              % (l, t, r - l, b - t, store(im.crop((l, t, r, b)), 90)))
html3 = ('<section class="pd" data-block="project_dashboard_reporting">'
         '<div class="pd-title"><span class="pd-light">PROJECT</span> <strong class="pd-bold">DASHBOARD</strong> <strong class="pd-bold">&amp;</strong> <strong class="pd-bold">REPORTING</strong></div>'
         '%s%s</section>' % (shots, LOGO_IMG % ("pd", LOGO)))
SLIDES.append(("project_dashboard_reporting", "Project Dashboard & Reporting", 1007, html3))


# ------------------------------------------------------------ 4. Innovation in designing
def catmull(points, steps_tension=0.5):
    """cubic bezier path through points (Catmull-Rom)."""
    d = "M%g %g" % points[0]
    pts = [points[0]] + points + [points[-1]]
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += " C%.1f %.1f %.1f %.1f %g %g" % (c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    return d


curve_pts = [(51, 502), (300, 502), (487, 502), (600, 497), (705, 474), (810, 421), (893, 341), (935, 235), (950, 109), (946, 40), (944, 0)]
path = catmull(curve_pts)
dots_red = [(129, 502), (311, 502), (487, 502), (705, 474), (893, 341), (950, 109)]
bubbles = [(135, 398, "3-D BIM\nServices", "#fddede"), (313, 397, "3-D As-Built\nDocumentation", "#fcd6d6"),
           (488, 397, "4-D Construction\nScheduling & Site\nLogistics", "#fbc9c9"), (670, 358, "5-D Cost\nMonitoring &\nProcurement\nManagement", "#fcd3d3"),
           (812, 258, "Quantity Take\noffs Revit\nFamily\nCreation", "#fbc6c6"), (833, 93, "Clash\nDetection &\nRisk Mitigation", "#fcdada")]
svg = '<svg class="ib-curve" viewBox="0 0 1008 566" aria-hidden="true"><path d="%s" fill="none" stroke="#d7d5e3" stroke-width="3" stroke-linecap="round"/>' % path
for x, y in dots_red:
    svg += '<circle cx="%d" cy="%d" r="7.5" fill="#e30613"/>' % (x, y)
svg += "</svg>"
bub = ""
for x, y, t, col in bubbles:
    bub += ('<div class="ib-bub" style="left:%dpx;top:%dpx"><i class="ib-in" style="background:%s"><span>%s</span></i></div>' % (x - 71, y - 71, col, esc(t)))
html4 = ('<section class="ib" data-block="innovation_in_designing">'
         '<div class="ib-title"><strong class="ib-bold">INNOVATION</strong> <span class="ib-light">IN DESIGNING</span></div>'
         '<div class="ib-sub"><strong>Auto CAD &amp; BIM</strong> <span>- Design Solutions</span></div>'
         '<strong class="ib-kick">BIM MODELLING</strong>'
         '<ul class="ib-list"><li>Accuracy upto LOD 450</li><li>Structural coordination</li><li>Fit-up drawings</li><li>3D &amp; 4D BIM execution</li></ul>'
         '%s%s%s</section>' % (svg, bub, LOGO_IMG % ("ib", LOGO)))
SLIDES.append(("innovation_in_designing", "Innovation in Designing", 1008, html4))

CSS = """
  /* ---- Internal Systems & Processes: slides built from the supplied
     screenshots, each laid out at its own reference width (SLIDE_LAYOUT_W) and
     scaled to the 1180px slide by fitSlideStage(). Absolute pixel layout with
     per-slide class prefixes (di- pe- pd- ib-); text is plain <strong>/<span>
     leaves (click-to-edit, newlines via white-space:pre-line); photos and
     dashboard shots are background-image slots ("Change photo"). ---- */
  .real-scope .di, .real-scope .pe, .real-scope .pd, .real-scope .ib{position:relative; background:#fff; overflow:hidden; color:#111;}
  .real-scope .di{height:562px;} .real-scope .pe{height:570px;} .real-scope .pd{height:562px;} .real-scope .ib{height:566px;}
  .real-scope .di *, .real-scope .pe *, .real-scope .pd *, .real-scope .ib *{box-sizing:border-box;}
  .real-scope .di .di-logo, .real-scope .pd .pd-logo, .real-scope .ib .ib-logo{position:absolute; left:929px; top:513px; width:49px; height:auto; max-width:none;}
  /* 1 - Driving projects with innovation */
  .real-scope .di .di-title{position:absolute; left:58px; top:53px; font-size:36px; line-height:44px; white-space:nowrap; letter-spacing:-.003em;}
  .real-scope .di .di-light{font-weight:300;} .real-scope .di .di-bold{font-weight:800;}
  .real-scope .di .di-photo{position:absolute; left:75px; top:170px; width:372px; height:308px; border-radius:15px; background-size:cover; background-position:center; background-color:#222;}
  .real-scope .di .di-h{position:absolute; left:506px; font-size:21px; line-height:28px; font-weight:800; letter-spacing:.01em; white-space:nowrap;}
  .real-scope .di .di-rule{position:absolute; left:506px; width:307px; height:1.5px; background:#e30613; display:block;}
  .real-scope .di .di-s{position:absolute; left:506px; font-size:15px; line-height:20px; font-weight:300; letter-spacing:.01em; white-space:nowrap;}
  /* 2 - Planning: ERP system */
  .real-scope .pe .pe-left{position:absolute; left:0; top:0; width:248px; height:570px; background-size:cover; background-position:center; background-color:#344;}
  .real-scope .pe .pe-t1{position:absolute; left:34px; top:34px; font-size:36px; line-height:40px; font-weight:800; color:#fff; white-space:nowrap;}
  .real-scope .pe .pe-t2{position:absolute; left:34px; font-size:36px; line-height:40px; font-weight:300; color:#fff; white-space:nowrap;}
  .real-scope .pe .pe-vline{position:absolute; left:785px; top:33px; width:2px; height:122px; background:#111; display:block;}
  .real-scope .pe .pe-pct{position:absolute; left:803px; top:44px; font-size:46px; line-height:52px; font-weight:300; white-space:nowrap;}
  .real-scope .pe .pe-note{position:absolute; left:804px; top:98px; font-size:10px; line-height:13px; color:#333; white-space:pre-line;}
  .real-scope .pe .pe-dots{position:absolute; left:0; top:0; width:1010px; height:570px; display:block; max-width:none;}
  .real-scope .pe .pe-top{position:absolute; width:240px; text-align:center; font-size:12px; line-height:15px; font-weight:800; white-space:pre-line;}
  .real-scope .pe .pe-lh{position:absolute; width:240px; text-align:center; font-size:12px; line-height:16px; font-weight:800; white-space:nowrap;}
  .real-scope .pe .pe-ls{position:absolute; width:240px; text-align:center; font-size:9px; line-height:12px; color:#222; white-space:nowrap;}
  /* 3 - Project dashboard & reporting */
  .real-scope .pd .pd-title{position:absolute; left:58px; top:53px; font-size:36px; line-height:44px; white-space:nowrap; letter-spacing:-.003em;}
  .real-scope .pd .pd-light{font-weight:300;} .real-scope .pd .pd-bold{font-weight:800;}
  .real-scope .pd .pd-shot{position:absolute; background-size:100% 100%; background-color:#f3f3f3; box-shadow:0 2px 8px rgba(0,0,0,.18);}
  /* 4 - Innovation in designing */
  .real-scope .ib .ib-title{position:absolute; left:48px; top:66px; font-size:36px; line-height:44px; white-space:nowrap; letter-spacing:-.003em;}
  .real-scope .ib .ib-bold{font-weight:800;} .real-scope .ib .ib-light{font-weight:300;}
  .real-scope .ib .ib-sub{position:absolute; left:57px; top:144px; font-size:24px; line-height:32px; white-space:nowrap; color:#222;}
  .real-scope .ib .ib-sub strong{font-weight:800;} .real-scope .ib .ib-sub span{font-weight:300;}
  .real-scope .ib .ib-kick{position:absolute; left:57px; top:175px; font-size:14px; line-height:18px; font-weight:800; color:#e30613; letter-spacing:.01em; white-space:nowrap;}
  .real-scope .ib .ib-list{position:absolute; left:57px; top:198px; margin:0; padding:0 0 0 19px; list-style:disc; font-size:16px; line-height:20px; font-weight:400; color:#111;}
  .real-scope .ib .ib-list li{margin:0; padding:0;}
  .real-scope .ib .ib-curve{position:absolute; left:0; top:0; width:1008px; height:566px; display:block; max-width:none;}
  .real-scope .ib .ib-bub{position:absolute; width:142px; height:142px; border-radius:50%; background:#fff0f0; display:flex; align-items:center; justify-content:center;}
  .real-scope .ib .ib-in{display:flex; align-items:center; justify-content:center; width:102px; height:102px; border-radius:50%; text-align:center; padding:6px;}
  .real-scope .ib .ib-in span{display:block; font-size:9.5px; line-height:11px; color:#222; white-space:pre-line;}
"""


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
    data = json.loads(orig)
    fn(data)
    out = json.dumps(data, ensure_ascii=False, separators=(",", ":") if compact else None).replace("</script", "<\\/script")
    s = s[:o] + out + s[e:]


def snip(d):
    for key, label, w, html in SLIDES:
        assert key not in d
        d[key] = html


edit_json('id="all-snippets-data"', snip)


def seed(d):
    for key, label, w, html in SLIDES:
        assert not any(x["key"] == key for x in d)
        d.append({"key": key, "label": label, "kind": "static", "slots": []})


edit_json('id="workspace-data"', seed)

sw("  .ws-card-remove{position:absolute; top:6px; right:6px;", CSS + "\n  .ws-card-remove{position:absolute; top:6px; right:6px;")
widths = ",\n".join("    %s: %d" % (k, w) for k, _, w, _ in SLIDES)
sw("    commissioning_asset_management: 1005\n", "    commissioning_asset_management: 1005,\n" + widths + "\n")
reveal = {"driving_projects_innovation": "['stagger', '.di-h, .di-s, .di-photo']", "planning_erp_system": "['stagger', '.pe-lh, .pe-ls, .pe-top']",
          "project_dashboard_reporting": "['stagger', '.pd-shot']", "innovation_in_designing": "['stagger', '.ib-bub, .ib-list']"}
sw("    commissioning_asset_management: ['stagger', '.ca-step, .ca-photo']\n",
   "    commissioning_asset_management: ['stagger', '.ca-step, .ca-photo'],\n" + ",\n".join("    %s: %s" % (k, v) for k, v in reveal.items()) + "\n")
keys = "".join(',"%s"' % k for k, _, _, _ in SLIDES)
sw('"client_testimonials","commissioning_asset_management"];', '"client_testimonials","commissioning_asset_management"%s];' % keys)

# picker: four more cards in the Internal Systems & Processes section, after the first
first = ('<div class="thumb-card__order">1</div><div class="thumb-card__label">From Commissioning to Asset Management</div>'
         '<button class="thumb-card__toggle" aria-label="Hide slide">\U0001F441</button></div>')
cards = "".join('<div class="thumb-card"><div class="thumb-stage-wrap"><div class="thumb-stage real-scope" data-key="%s"></div></div>'
                '<div class="thumb-card__order">%d</div><div class="thumb-card__label">%s</div>'
                '<button class="thumb-card__toggle" aria-label="Hide slide">\U0001F441</button></div>' % (k, i + 2, esc(l))
                for i, (k, l, _, _) in enumerate(SLIDES))
sw(first, first + cards)

open(APP, "w", encoding="utf-8").write(s)
print("ok", [(k, len(h)) for k, _, _, h in SLIDES])
