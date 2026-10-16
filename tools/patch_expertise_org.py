# -*- coding: utf-8 -*-
"""Replaces two master slides with the user's new designs:
   "Our Project Scope" (project_scope)  -> "Our Expertise"  (pj_expertise)
   "Organisation Chart" (org_chart)     -> "Org Structure"  (pj_orgstructure), now included by default
Built from two screenshots by tools/bira_slides/gen_two.py (photos in tools/bira_slides/assets_two)."""
import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "tools", "bira_slides")
APP = os.path.join(ROOT, "src", "frontend", "app.html")
s = open(APP, encoding="utf-8").read()
slides = json.load(open(os.path.join(BASE, "two_slides.json"), encoding="utf-8"))
LOGO = re.search(r'class=\\"kc-logo\\" src=\\"([^"\\]+)\\"', s).group(1)

PAIRS = [("project_scope", "pj_expertise", "expertise", "Our Expertise"), ("org_chart", "pj_orgstructure", "orgstructure", "Org Structure")]


def media(rel):
    raw = open(os.path.join(BASE, "assets_two", rel), "rb").read()
    name = hashlib.sha1(raw).hexdigest()[:16] + os.path.splitext(rel)[1]
    p = os.path.join(ROOT, "public", "media", name)
    if not os.path.exists(p):
        open(p, "wb").write(raw)
    return "/media/" + name


def pref(t):
    return t if t.startswith("pj") else "pj-" + t


def fix(h):
    h = re.sub(r'class="([^"]*)"', lambda m: 'class="%s"' % " ".join(pref(t) for t in m.group(1).split()), h)
    h = h.replace("{{LOGO}}", LOGO)
    return re.sub(r"\{\{IMG:two/([^}]+)\}\}", lambda m: media(m.group(1)), h)


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
    data = fn(json.loads(orig)) or None
    out = json.dumps(data, ensure_ascii=False, separators=(",", ":") if compact else None).replace("</script", "<\\/script")
    s = s[:o] + out + s[e:]


def snip(d):
    for old, new, key, lab in PAIRS:
        d[new] = fix(slides[key])
        assert "{{" not in d[new]
    return d


edit_json('id="all-snippets-data"', snip)


def seed(d):
    out = []
    for x in d:
        hit = [p for p in PAIRS if p[0] == x["key"]]
        out.append({"key": hit[0][1], "label": hit[0][3], "kind": "static", "slots": []} if hit else x)
    return out


edit_json('id="workspace-data"', seed)

# css: reuse the project-slide styles (already in the page) + the two layout widths
sw("    thank_you: 1003,\n", "    thank_you: 1003,\n    pj_expertise: 1280,\n    pj_orgstructure: 1280,\n")
EXTRA = """
  .real-scope .pj-e{background:#f4f3f5;}
  .real-scope .pj .pj-ecard{position:absolute; background:#fff; display:block;}
  .real-scope .pj .pj-enum{font-weight:300; color:#111;} .real-scope .pj .pj-etitle{font-weight:400; color:#111; letter-spacing:-.005em;}
  .real-scope .pj .pj-edesc{font-weight:400;}
  .real-scope .pj .pj-tl{font-weight:300;}
  .real-scope .pj .pj-ph.pj-rnd2{border-radius:10px;}
  .real-scope .pj .pj-obar{position:absolute; background:#d9d9d9; display:block;}
  .real-scope .pj .pj-ovline{position:absolute; width:1px; background:#d8d8d8; display:block;}
"""
sw("  .ws-card-remove{position:absolute; top:6px; right:6px;", EXTRA + "\n  .ws-card-remove{position:absolute; top:6px; right:6px;")

# picker cards
EYE = "\U0001F441"
sw('<div class="thumb-card"><div class="thumb-stage-wrap"><div class="thumb-stage real-scope" data-key="project_scope"></div></div><div class="thumb-card__order">6</div><div class="thumb-card__label">Our Project Scope</div>',
   '<div class="thumb-card"><div class="thumb-stage-wrap"><div class="thumb-stage real-scope" data-key="pj_expertise"></div></div><div class="thumb-card__order">6</div><div class="thumb-card__label">Our Expertise</div>')
m = re.search(r'<div class="thumb-card excluded"><div class="thumb-stage-wrap"><div class="thumb-stage real-scope" data-key="org_chart"></div></div><div class="thumb-card__label">Organisation Chart</div>.*?</button></div>', s, re.S)
assert m
s = s.replace(m.group(0), '<div class="thumb-card"><div class="thumb-stage-wrap"><div class="thumb-stage real-scope" data-key="pj_orgstructure"></div></div>'
              '<div class="thumb-card__order">5</div><div class="thumb-card__label">Org Structure</div><button class="thumb-card__toggle" aria-label="Hide slide">%s</button></div>' % EYE)

# master list
mm = re.search(r'var PROFILE_DECK_KEYS = \[(.*?)\];', s)
keys = json.loads("[" + mm.group(1) + "]")
keys = ["pj_expertise" if k == "project_scope" else k for k in keys]
i = keys.index("htl_journey")
keys.insert(i + 1, "pj_orgstructure")
s = s[:mm.start()] + "var PROFILE_DECK_KEYS = " + json.dumps(keys, separators=(",", ":")) + ";" + s[mm.end():]
open(APP, "w", encoding="utf-8").write(s)
print("ok")
