# -*- coding: utf-8 -*-
"""Master Profile Deck: the project slides now follow the BIRA "PROJECT SLIDE" folder (28 slides in
four sections). Reads tools/bira_slides/{slides.json,assets,content.py} (built by gen_slides.py from the
screenshots), writes the photos to public/media and rewires src/frontend/app.html.

(tools/bira_slides/assets - the cut-out photos - is not kept in git: the same files live in public/media; rebuild them with build_assets.py + gen_slides.py from the screenshots.)

Retired from the picker / master list (their snippets stay in ALL_SNIPPETS so saved decks still open):
 project_slide_cre, project_slide_dc, recent_wins, major_projects_segment_{bfsi,industrial,mep,manufacturing,
 private_luxury,hospitality,edu}. Everything else stays as it was."""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "tools", "bira_slides")
sys.path.insert(0, BASE)
from content import SECTIONS  # noqa: E402

APP = os.path.join(ROOT, "src", "frontend", "app.html")
MEDIA = os.path.join(ROOT, "public", "media")
s = open(APP, encoding="utf-8").read()

RETIRED = ["project_slide_cre", "project_slide_dc", "recent_wins", "major_projects_segment_bfsi", "major_projects_segment_industrial",
           "major_projects_segment_mep", "major_projects_segment_manufacturing", "major_projects_segment_private_luxury",
           "major_projects_segment_hospitality", "major_projects_segment_edu"]

slides = json.load(open(os.path.join(BASE, "slides.json"), encoding="utf-8"))
LOGO = re.search(r'class=\\"kc-logo\\" src=\\"([^"\\]+)\\"', s).group(1)

# ---------------------------------------------------------------- media
_media = {}


def media(rel):
    if rel in _media:
        return _media[rel]
    raw = open(os.path.join(BASE, "assets", rel), "rb").read()
    ext = os.path.splitext(rel)[1]
    name = hashlib.sha1(raw).hexdigest()[:16] + ext
    p = os.path.join(MEDIA, name)
    if not os.path.exists(p):
        open(p, "wb").write(raw)
    _media[rel] = "/media/" + name
    return _media[rel]


# ---------------------------------------------------------------- class prefix (avoid clashes with the block library's CSS)
KEEP = {"pj", "pj-a", "pj-b", "pj-c"}


def pref(tok):
    return tok if (tok in KEEP or tok.startswith("pj-")) else "pj-" + tok


def fix_html(h):
    h = re.sub(r'class="([^"]*)"', lambda m: 'class="%s"' % " ".join(pref(t) for t in m.group(1).split()), h)
    h = h.replace("{{LOGO}}", LOGO)
    h = re.sub(r"\{\{IMG:([^}]+)\}\}", lambda m: media(m.group(1)), h)
    return h


SNIP = {}
for sid, h in slides.items():
    SNIP["pj_" + sid] = fix_html(h)
    assert "{{" not in SNIP["pj_" + sid]

# ---------------------------------------------------------------- CSS
sys.path.insert(0, BASE)
import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location("gen_slides_css", os.path.join(BASE, "gen_slides.py"))
src = open(os.path.join(BASE, "gen_slides.py"), encoding="utf-8").read()
CSS = re.search(r'CSS = r"""(.*?)"""', src, re.S).group(1)
CSS = re.sub(r"\.(?!real-scope\b|pj\b|pj-)([a-z][a-z-]*)", lambda m: ".pj-" + m.group(1), CSS)
CSS = CSS.replace(".real-scope .pj .", ".real-scope .pj .")  # (prefix already applied above)


def sw(o, n):
    global s
    assert s.count(o) == 1, (s.count(o), o[:100])
    s = s.replace(o, n)


def edit_json(marker, fn):
    global s
    a = s.find(marker)
    o = s.find(">", a) + 1
    e = s.find("</script>", o)
    orig = s[o:e]
    compact = '": "' not in orig[:400]
    data = json.loads(orig)
    data = fn(data) or data
    out = json.dumps(data, ensure_ascii=False, separators=(",", ":") if compact else None).replace("</script", "<\\/script")
    s = s[:o] + out + s[e:]


ALL = [sid for _, subs in SECTIONS for _, items in subs for sid, _ in items]
LABEL = {sid: lab for _, subs in SECTIONS for _, items in subs for sid, lab in items}


def snip(d):
    for k, v in SNIP.items():
        d[k] = v
    return d


edit_json('id="all-snippets-data"', snip)


def seed(d):
    d = [x for x in d if x["key"] not in RETIRED]
    out = []
    for x in d:
        out.append(x)
        if x["key"] == "major_projects_segment_hospitals":
            for sid in ALL:
                out.append({"key": "pj_" + sid, "label": LABEL[sid], "kind": "static", "slots": []})
    assert any(x["key"] == "pj_bfsi1" for x in out)
    return out


edit_json('id="workspace-data"', seed)

CSS += """
  .sub-group{margin:0 0 22px;}
  .sub-group__title{display:flex; align-items:center; gap:10px; font-size:.95rem; font-weight:700; color:#1f2937; letter-spacing:0; text-transform:none; margin:4px 0 12px; padding-left:12px; border-left:3px solid #dc2626;}
  .sub-count{font-size:.8rem; font-weight:500; color:#9ca3af;}
  .sub-select{appearance:none; margin-left:auto; border:1px solid var(--line-strong); background:var(--surface); color:#374151; font:inherit; font-size:.8rem; font-weight:600; padding:5px 13px; border-radius:8px; cursor:pointer; white-space:nowrap;}
  .sub-select:hover{background:var(--accent-wash); color:#b91c1c; border-color:#fecaca;}
"""
# ---------------------------------------------------------------- CSS + widths + reveal
sw("  .ws-card-remove{position:absolute; top:6px; right:6px;", CSS + "\n  .ws-card-remove{position:absolute; top:6px; right:6px;")
sw("    thank_you: 1003,\n", "    thank_you: 1003,\n" + "".join("    pj_%s: 1280,\n" % sid for sid in ALL))
sw("    if(key && key.indexOf('major_projects_segment_') === 0) return ['stagger', '.bp-card'];\n    return null;",
   "    if(key && key.indexOf('major_projects_segment_') === 0) return ['stagger', '.bp-card'];\n    if(key && key.indexOf('pj_') === 0) return ['fade-up'];\n    return null;")

# ---------------------------------------------------------------- picker
OPEN = '<div class="section-group"><div class="section-group__title">'
a = s.index(OPEN + "Projects & Sectors</div>")
b = s.index(OPEN + "Internal Systems &amp; Processes</div>")
blk = s[a:b]
for key in RETIRED:
    pat = re.compile(r'<div class="thumb-card[^"]*"><div class="thumb-stage-wrap"><div class="thumb-stage real-scope" data-key="%s"></div></div>.*?</button></div>' % re.escape(key), re.S)
    blk, n = pat.subn("", blk)
    assert n == 1, (key, n)
EYE = "\U0001F441"


def card(sid):
    return ('<div class="thumb-card"><div class="thumb-stage-wrap"><div class="thumb-stage real-scope" data-key="pj_%s"></div></div>'
            '<div class="thumb-card__order">0</div><div class="thumb-card__label">%s</div>'
            '<button class="thumb-card__toggle" aria-label="Hide slide">%s</button></div>' % (sid, LABEL[sid].replace("&", "&amp;"), EYE))


new = ""
for title, subs in SECTIONS:
    new += OPEN + title.replace("&", "&amp;") + "</div>"
    for sub, items in subs:
        grid = '<div class="thumb-grid">' + "".join(card(sid) for sid, _ in items) + "</div>"
        if sub:
            new += '<div class="sub-group"><div class="sub-group__title">' + sub.replace("&", "&amp;") + "</div>" + grid + "</div>"
        else:
            new += grid
    new += "</div>"
s = s[:a] + blk + new + s[b:]

# ---------------------------------------------------------------- master list (download / upload of the Profile deck)
m = re.search(r'var PROFILE_DECK_KEYS = \[(.*?)\];', s)
keys = json.loads("[" + m.group(1) + "]")
keys = [k for k in keys if k not in RETIRED]
i = keys.index("major_projects_segment_hospitals")
keys = keys[: i + 1] + ["pj_" + sid for sid in ALL] + keys[i + 1:]
s = s[: m.start()] + "var PROFILE_DECK_KEYS = " + json.dumps(keys, separators=(",", ":")) + ";" + s[m.end():]

open(APP, "w", encoding="utf-8").write(s)
print("ok", len(SNIP), "slides,", len(_media), "images")
