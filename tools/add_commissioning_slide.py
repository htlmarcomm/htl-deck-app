# -*- coding: utf-8 -*-
"""Adds the "Internal Systems & Processes" section (Master Profile Deck) with its
first slide, "From Commissioning to Asset Management", built from the supplied
screenshot at its own 1005px width (SLIDE_LAYOUT_W) and scaled to the slide.
Edits src/frontend/app.html (kept for provenance)."""
import hashlib
import json
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, "src", "frontend", "app.html")
IMG = r"C:\Users\anush\AppData\Local\Temp\claude\C--Users-anush-Downloads-htl-block-library--1-\e2e48ebc-294d-4beb-b54e-d94cd56a3cda\images\41.png"
KEY = "commissioning_asset_management"
LABEL = "From Commissioning to Asset Management"
SECTION = "Internal Systems &amp; Processes"

ref = Image.open(IMG).convert("RGB")


def media(box):
    im = ref.crop(box)
    import io
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=92)
    raw = buf.getvalue()
    name = hashlib.sha1(raw).hexdigest()[:16] + ".jpg"
    open(os.path.join(ROOT, "public", "media", name), "wb").write(raw)
    return "/media/" + name


# the four photos, at their own places on the 1005x566 frame (the two on the
# bottom row run off the bottom edge, as in the design)
PHOTOS = [
    (49, 243, 198, 443),
    (205, 243, 354, 361),
    (204, 368, 354, 566),
    (49, 449, 198, 566),
]
photos = "".join(
    '<div class="ca-photo" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx;background-image:url(\'%s\')"></div>'
    % (l, t, r - l, b - t, media((l, t, r, b)))
    for (l, t, r, b) in PHOTOS
)

# (side, dot_y, heading, description)
STEPS = [
    ("l", 84, "01 \u2013 VALIDATE",
     "Understanding project goals, BIM clash\ndetection & service\nco-ordination before mobilisation"),
    ("r", 181, "02 \u2013 INSTALL",
     "Quality controlled execution to PMC\nbenchmarking"),
    ("l", 278, "03 \u2013TEST &\nCOMMISSION",
     "System-wise testing, balancing & integrated\ncommissioning to ensure performance\nreadiness"),
    ("r", 375, "04 \u2013HANDOVER",
     "Complete documentation, asset\nhandover & operational readiness for a\nseamless transition"),
    ("l", 475, "05 \u2013 SERVICE",
     "Proactive preventive maintenance and\nresponsive service support throughout\nthe asset lifecycle"),
]


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


steps_html = ""
for side, y, head, desc in STEPS:
    x = 434 if side == "l" else 792
    if head.startswith("05"):
        x = 445
    two = "\n" in head
    head_top = y - 11 if not two else y - 12
    desc_top = y + (21 if not two else 38) - 6
    if side == "l":
        line = '<i class="ca-conn" style="left:609px;top:%dpx;width:81px"></i>' % y
    else:
        line = '<i class="ca-conn" style="left:690px;top:%dpx;width:80px"></i>' % y
    steps_html += (
        '<div class="ca-step">%s<i class="ca-dot" style="top:%dpx"></i>'
        '<strong class="ca-head" style="left:%dpx;top:%dpx">%s</strong>'
        '<span class="ca-desc" style="left:%dpx;top:%dpx">%s</span></div>'
        % (line, y, x, head_top, esc(head), x + 1, desc_top, esc(desc))
    )

html = (
    '<section class="ca" data-block="%s">' % KEY
    + '<i class="ca-vline"></i>'
    + '<div class="ca-title"><span class="ca-l ca-l--light">FROM</span><span class="ca-l ca-l--bold">COMMISSIONING</span>'
      '<div class="ca-l-row"><span class="ca-l ca-l--light">TO</span> <span class="ca-l ca-l--bold">ASSET</span></div>'
      '<span class="ca-l ca-l--bold">MANAGEMENT</span></div>'
    + photos
    + steps_html
    + "</section>"
)

CSS = """
  /* ---- From Commissioning to Asset Management: the supplied slide at its own
     1005px width (SLIDE_LAYOUT_W), scaled to the 1180px slide by fitSlideStage().
     Absolute pixel layout, ca-* classes only; text is plain <strong>/<span>
     leaves (click-to-edit) with literal newlines + white-space:pre-line; the four
     photos are background-image slots ("Change photo"). ---- */
  .real-scope .ca{position:relative; height:566px; background:#fff; overflow:hidden; color:#1a1a1a;}
  .real-scope .ca .ca-vline{position:absolute; left:690px; top:0; bottom:0; width:1px; background:#c9c9c9; display:block;}
  .real-scope .ca .ca-title{position:absolute; left:50px; top:76px; width:330px;}
  .real-scope .ca .ca-l{display:inline-block; font-size:35px; line-height:32.5px; letter-spacing:-.005em; color:#111;}
  .real-scope .ca .ca-title > .ca-l{display:block;}
  .real-scope .ca .ca-l--light{font-weight:300;}
  .real-scope .ca .ca-l--bold{font-weight:800;}
  .real-scope .ca .ca-l-row{display:block; height:32.5px; white-space:nowrap;}
  .real-scope .ca .ca-l-row .ca-l--bold{margin-left:10px;}
  .real-scope .ca .ca-photo{position:absolute; background-size:cover; background-position:center; background-color:#e6e6e6;}
  .real-scope .ca .ca-dot{position:absolute; left:687px; width:6px; height:6px; margin-top:-3px; border-radius:50%; background:#111; display:block;}
  .real-scope .ca .ca-conn{position:absolute; height:1px; background:#c4c4c4; display:block;}
  .real-scope .ca .ca-head{position:absolute; font-size:17px; line-height:19.5px; font-weight:700; letter-spacing:.01em; color:#1a1a1a; white-space:pre-line;}
  .real-scope .ca .ca-desc{position:absolute; font-size:11px; line-height:12.6px; color:#444; white-space:pre-line;}
"""

s = open(APP, encoding="utf-8").read()


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
    assert KEY not in d
    d[KEY] = html


edit_json('id="all-snippets-data"', snip)


def seed(d):
    assert not any(x["key"] == KEY for x in d)
    d.append({"key": KEY, "label": LABEL, "kind": "static", "slots": []})


edit_json('id="workspace-data"', seed)

sw("  .ws-card-remove{position:absolute; top:6px; right:6px;", CSS + "\n  .ws-card-remove{position:absolute; top:6px; right:6px;")
sw("    client_testimonials: 1010\n", "    client_testimonials: 1010,\n    %s: 1005\n" % KEY)
sw("    client_testimonials: ['stagger', '.tm-card']\n", "    client_testimonials: ['stagger', '.tm-card'],\n    %s: ['stagger', '.ca-step, .ca-photo']\n" % KEY)
sw('"why_htl_mep","client_testimonials"];', '"why_htl_mep","client_testimonials","%s"];' % KEY)

# picker: a new section before "Closing"
closing = '<div class="section-group"><div class="section-group__title">Closing</div>'
card = ('<div class="section-group"><div class="section-group__title">%s</div><div class="thumb-grid">'
        '<div class="thumb-card"><div class="thumb-stage-wrap"><div class="thumb-stage real-scope" data-key="%s"></div></div>'
        '<div class="thumb-card__order">1</div><div class="thumb-card__label">%s</div>'
        '<button class="thumb-card__toggle" aria-label="Hide slide">\U0001F441</button></div></div></div>\n' % (SECTION, KEY, LABEL))
sw(closing, card + closing)

open(APP, "w", encoding="utf-8").write(s)
print("ok", len(html), "chars of slide markup")
