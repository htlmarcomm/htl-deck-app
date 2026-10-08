# -*- coding: utf-8 -*-
"""Adds Key Repeat Clients, Key Clients and Thank You to the Closing section of
the Master Profile Deck (Thank You replaces its "template not designed yet"
placeholder). Built from the supplied screenshots at their own widths
(SLIDE_LAYOUT_W). Edits src/frontend/app.html (kept for provenance)."""
import hashlib
import io
import json
import os
import re

import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, "src", "frontend", "app.html")
IMGDIR = r"C:\Users\anush\AppData\Local\Temp\claude\C--Users-anush-Downloads-htl-block-library--1-\e2e48ebc-294d-4beb-b54e-d94cd56a3cda\images"


def shot(n):
    return Image.open(os.path.join(IMGDIR, "%d.png" % n)).convert("RGB")


def store(im, q=93):
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q)
    raw = buf.getvalue()
    name = hashlib.sha1(raw).hexdigest()[:16] + ".jpg"
    open(os.path.join(ROOT, "public", "media", name), "wb").write(raw)
    return "/media/" + name


s = open(APP, encoding="utf-8").read()
LOGO = re.search(r'class=\\"tm-logo\\" src=\\"([^"\\]+)\\"', s).group(1)
lock = re.search(r'block-title-page__lockup\\"><img src=\\"([^"\\]+)\\" alt=\\"30th Anniversary\\"><span></span><img src=\\"([^"\\]+)\\"', s)
ANNIV, HTLLOGO = lock.group(1), lock.group(2)

SLIDES = []

# 1 ---- Key Repeat Clients
im = shot(48)
field = store(im.crop((60, 140, 980, 502)))
html1 = ('<section class="kr" data-block="key_repeat_clients">'
         '<div class="kr-title"><strong class="kr-red">Key Repeat</strong> <span class="kr-light">Clients</span></div>'
         '<div class="kr-logos" style="background-image:url(\'%s\')"></div></section>' % field)
SLIDES.append(("key_repeat_clients", "Key Repeat Clients", 1006, html1))

# 2 ---- Key Clients
im = shot(49)
grid = store(im.crop((98, 128, 910, 515)))
html2 = ('<section class="kc" data-block="key_clients">'
         '<i class="kc-line" style="left:77px;width:238px"></i><i class="kc-line" style="left:698px;width:232px"></i>'
         '<div class="kc-title"><strong class="kc-black">KEY</strong> <strong class="kc-red">CLIENTS</strong></div>'
         '<div class="kc-logos" style="background-image:url(\'%s\')"></div>'
         '<img class="kc-logo" src="%s" alt="HTL"></section>' % (grid, LOGO))
SLIDES.append(("key_clients", "Key Clients", 1002, html2))

# 3 ---- Thank You (building photo with the red lettering removed, so the text stays editable)
raw = cv2.imread(os.path.join(IMGDIR, "50.png"))
crop = raw[118:478, 55:953].copy()
b, g, r = [crop[:, :, i].astype(int) for i in range(3)]
mask = (np.maximum(r - g, r - b) > 22).astype(np.uint8) * 255
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)
clean = cv2.inpaint(crop, mask, 3, cv2.INPAINT_NS)
photo = store(Image.fromarray(cv2.cvtColor(clean, cv2.COLOR_BGR2RGB)), 92)
html3 = ('<section class="ty" data-block="thank_you">'
         '<div class="ty-lockup"><img src="%s" alt="30th Anniversary"><i></i><img src="%s" alt="HTL"></div>'
         '<div class="ty-photo" style="background-image:url(\'%s\')"></div>'
         '<strong class="ty-text">THANK YOU</strong><i class="ty-rule"></i>'
         '<span class="ty-cities">MUMBAI | PUNE | DELHI NCR | AMD | HYD | BLR | DUBAI | AFRICA</span></section>' % (ANNIV, HTLLOGO, photo))
SLIDES.append(("thank_you", "Thank You", 1003, html3))

CSS = """
  /* ---- Closing section: Key Repeat Clients, Key Clients, Thank You - built from
     the supplied screenshots at their own widths (SLIDE_LAYOUT_W), scaled to the
     slide by fitSlideStage(). kr- kc- ty- classes; headings are click-to-edit
     text, the logo fields and the building photo are image slots. ---- */
  .real-scope .kr, .real-scope .kc, .real-scope .ty{position:relative; background:#fff; overflow:hidden; color:#111;}
  .real-scope .kr{height:560px;} .real-scope .kc{height:560px;} .real-scope .ty{height:557px;}
  .real-scope .kr *, .real-scope .kc *, .real-scope .ty *{box-sizing:border-box;}
  .real-scope .kr .kr-title{position:absolute; left:58px; top:66px; font-size:40px; line-height:52px; white-space:nowrap; letter-spacing:-.005em;}
  .real-scope .kr .kr-red{font-weight:800; color:#ff2d2d;} .real-scope .kr .kr-light{font-weight:300; color:#333;}
  .real-scope .kr .kr-logos{position:absolute; left:60px; top:140px; width:920px; height:362px; background-size:100% 100%; background-position:center;}
  .real-scope .kc .kc-line{position:absolute; top:79px; height:2px; background:#111; display:block;}
  .real-scope .kc .kc-title{position:absolute; left:313px; width:400px; top:56px; text-align:center; font-size:42px; line-height:52px; letter-spacing:.01em; white-space:nowrap;}
  .real-scope .kc .kc-black{font-weight:800; color:#111;} .real-scope .kc .kc-red{font-weight:800; color:#f00000;}
  .real-scope .kc .kc-logos{position:absolute; left:98px; top:128px; width:812px; height:387px; background-size:100% 100%; background-position:center;}
  .real-scope .kc .kc-logo{position:absolute; left:927px; top:513px; width:49px; height:auto; max-width:none;}
  .real-scope .ty .ty-lockup{position:absolute; left:671px; top:52px; height:50px; display:flex; align-items:center; gap:22px;}
  .real-scope .ty .ty-lockup img{display:block; height:auto; max-width:none;}
  .real-scope .ty .ty-lockup img:first-child{width:126px;} .real-scope .ty .ty-lockup img:last-child{width:113px;}
  .real-scope .ty .ty-lockup i{display:block; width:1px; height:48px; background:#b8a08c;}
  .real-scope .ty .ty-photo{position:absolute; left:55px; top:118px; width:898px; height:360px; background-size:cover; background-position:center; background-color:#777;}
  .real-scope .ty .ty-text{position:absolute; left:55px; width:898px; top:268px; text-align:center; font-size:70px; line-height:84px; font-weight:300; letter-spacing:.125em; color:#ff2d2d; white-space:nowrap; text-indent:.13em;}
  .real-scope .ty .ty-rule{position:absolute; left:54px; top:508px; width:898px; height:1px; background:#111; display:block;}
  .real-scope .ty .ty-cities{position:absolute; left:54px; width:898px; top:520px; text-align:center; font-size:15.5px; line-height:22px; font-weight:300; letter-spacing:.2em; color:#222; white-space:nowrap;}
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
sw("    innovation_in_designing: 1008\n", "    innovation_in_designing: 1008,\n" + ",\n".join("    %s: %d" % (k, w) for k, _, w, _ in SLIDES) + "\n")
sw("    innovation_in_designing: ['stagger', '.ib-bub, .ib-list']\n",
   "    innovation_in_designing: ['stagger', '.ib-bub, .ib-list'],\n    key_repeat_clients: ['fade-up'],\n    key_clients: ['fade-up'],\n    thank_you: ['fade-up']\n")
sw('"innovation_in_designing"];', '"innovation_in_designing"%s];' % "".join(',"%s"' % k for k, _, _, _ in SLIDES))

# Closing section: the three slides (replacing the Thank You placeholder)
pend = '<div class="thumb-card pending" data-pending-key="thank_you"><div class="thumb-stage-wrap"></div><div class="thumb-card__label">Thank You Page</div></div>'
assert s.count(pend) == 1
eye = "👁"
cards = "".join('<div class="thumb-card"><div class="thumb-stage-wrap"><div class="thumb-stage real-scope" data-key="%s"></div></div>'
                '<div class="thumb-card__order">%d</div><div class="thumb-card__label">%s</div>'
                '<button class="thumb-card__toggle" aria-label="Hide slide">%s</button></div>' % (k, i + 1, l, eye)
                for i, (k, l, _, _) in enumerate(SLIDES))
s = s.replace(pend, cards)

open(APP, "w", encoding="utf-8").write(s)
print("ok", [(k, len(h)) for k, _, _, h in SLIDES])
