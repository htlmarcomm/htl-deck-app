# -*- coding: utf-8 -*-
"""All 28 project slides in ONE layout: the "Major MEP Projects" style
(photo panel with the title on the left, red-ruled label, cards = photo / name / location / rule / AREA-SCOPE lines),
on the Slide Standard (tokens, caption style for card text, footer).

Content comes from tools/bira_slides/content.py (text, in reading order) and the original slides in
tools/standard/originals.json (photos, panel photo, client-logo badges on cards).
Writes tools/standard/projects_result.json for apply.py."""
import importlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "bira_slides"))
C = importlib.import_module("content")
orig = json.load(open(os.path.join(HERE, "originals.json"), encoding="utf-8"))
app = open(os.path.join(ROOT, "src", "frontend", "app.html"), encoding="utf-8").read()
LOGO = re.search(r'class=\\"ss-logo\\" src=\\"([^"\\]+)\\"', app).group(1)

M = dict(l=72.0, r=1208.0, t=72.0, b=656.0)
PANEL_W = 314.0
X0 = M["l"] + 3 * (54.5 + 18) * 4 / 3          # column 4 = first column right of the panel (362 px)
GAP = 24.0
CAP = 12 * 1.3                                   # caption line height
LABEL_Y = M["t"]
RULE_Y = LABEL_Y + CAP + 6
GRID_Y = RULE_Y + 16


PLACEHOLDER = "data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='300'%3E%3Crect width='400' height='300' fill='%23e8e5df'/%3E%3Ctext x='200' y='158' font-family='Arial' font-size='22' fill='%23938c80' text-anchor='middle'%3EPoint here, then Change photo%3C/text%3E%3C/svg%3E"


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def f(v):
    return "%.1fpx" % v


# ---------------------------------------------------------------- text of each card -> (name, location, [(label, value)])
AREA = re.compile(r"(sq\.?\s*f|sqft|sq\s*ft|\bsq\b|\d\s*L\b|\dL\b|lakh)", re.I)
CAPY = re.compile(r"\b(MW|TR|HP)\b", re.I)
SCOPE = re.compile(r"^(scope\s*:\s*)?(hvac|mep|vrv|fitout|fit out|electrical|basebuild|fire|plumbing)", re.I)


def classify(line):
    s = line.strip().rstrip(",")
    m = re.match(r"^(AREA|SCOPE|VALUE|COMPLETION)\s*:\s*(.+)$", s, re.I)
    if m:
        return m.group(1).upper(), m.group(2).strip()
    if CAPY.search(s) and re.search(r"\d", s):
        return "CAPACITY", s
    if AREA.search(s) and re.search(r"\d", s):
        return "AREA", s
    if SCOPE.match(s):
        return "SCOPE", re.sub(r"^scope\s*:\s*", "", s, flags=re.I)
    return None, s


def from_A(c, named):
    name, loc, kv = "", [], []
    if "left" in c:
        kv = [(k.rstrip(":").upper(), v) for k, v in c["left"]]
        name = c.get("above") or " ".join(c.get("caption", [])).strip().rstrip(",")
        return name, "", kv
    lines = list(c["right"])
    if named and lines:
        name = lines.pop(0).strip().rstrip(",")
    for ln in lines:
        for part in [p for p in ln.split("|")]:
            k, v = classify(part)
            if k:
                kv.append((k, v))
            elif v:
                loc.append(v.strip().rstrip(","))
    if c.get("pilltext"):
        name = c["pilltext"]
    if c.get("topright"):
        loc.append(c["topright"])
    if c.get("caption") and not name:
        name = " ".join(c["caption"]).strip().rstrip(",")
    loc = ", ".join(x for x in loc if x)
    if not name:            # client is shown by the logo on the photo: the city leads
        name, loc = loc, ""
    return name, loc, kv


def cards_of(sid):
    if sid in C.Bs:
        d = C.Bs[sid]
        return [(n, l, [(k.rstrip(":").upper(), v) for k, v in kv]) for n, l, kv in d["cards"]]
    if sid in C.Cs:
        out = []
        for c in C.Cs[sid]["cards"]:
            if sid == "vrv":
                n, cap, typ = c
                out.append((n, "", [("CAPACITY", cap + " HP"), ("TYPE", typ)]))
            elif len(c) == 3:
                out.append((c[0], c[1], [("SCOPE", c[2])]))
            else:
                out.append((c[0], "", [("SCOPE", c[1])]))
        return out
    named = sid in ("bfsi2", "bfsi3", "res1")
    return [from_A(c, named) for c in C.A[sid]["cards"]]


def title_of(sid):
    """[(text, weight, red)] - weights kept from the original title"""
    if sid in C.Bs:
        return [(" ".join(C.Bs[sid]["panel"]), "b", False)]
    d = C.Cs.get(sid) or C.A[sid]
    segs = [(t, w, bool(red)) for line in d["title"] for (t, w, red) in line]
    out = []
    for t, w, red in segs:   # a bold word directly followed by a light word needs its space back ("MAJORPROJECTS")
        if out and out[-1][0] and t and out[-1][0][-1].isalnum() and t[0].isalnum():
            t = " " + t
        out.append((t, w, red))
    return out


def label_of(sid):
    d = C.A.get(sid)
    if sid == "dcmajor":
        return "PROJECTS  ·  120 MW EXECUTED  ·  156 MW UNDER EXECUTION"
    if d and d.get("pill"):
        return d["pill"]
    return "PROJECTS"


# ---------------------------------------------------------------- images from the original slide
DEGRADIENT = json.load(open(os.path.join(HERE, "degradient_map.json"), encoding="utf-8")) if os.path.exists(os.path.join(HERE, "degradient_map.json")) else {}


def images_of(key):
    h = orig[key]
    panel = re.search(r'class="pj-panel"[^>]*background-image:url\(([^)]+)\)', h)
    photos, badges = [], []
    # photo cards (with their logo badge) and plain photos, in the order they appear
    for m in re.finditer(r'<div class="(pj-card|pj-ph[^"]*)"[^>]*background-image:url\(([^)]+)\)">', h):
        photos.append(DEGRADIENT.get(m.group(2), m.group(2)))   # caption gradient removed (degradient.py)
        badge = None
        if m.group(1) == "pj-card":
            end = h.find("</div>\n</div>", m.end())
            b = re.search(r'class="pj-pill-i" src="([^"]+)"', h[m.end():end])
            badge = b.group(1) if b else None
        badges.append(badge)
    return (panel.group(1) if panel else None), photos, badges


def rows_for(n):
    if n <= 4:
        return [n]
    if n <= 6:
        return [3, n - 3]
    if n <= 8:
        return [4, n - 4]
    return [4] * (n // 4) + ([n % 4] if n % 4 else [])


def build(key):
    sid = key[3:]
    cards = cards_of(sid)
    panel, photos, badges = images_of(key)
    flags = []
    dim = False
    if not panel:
        panel, dim = photos[0], True
    if len(photos) < len(cards):
        flags.append("fewer photos than cards (%d / %d)" % (len(photos), len(cards)))
    rows = rows_for(len(cards))
    per = max(rows)
    cw = (M["r"] - X0 - (per - 1) * GAP) / per
    kv_n = max([len(c[2]) for c in cards] + [1])
    has_loc = any(c[1] for c in cards)
    text_h = 8 + CAP * (1 + (1 if has_loc else 0)) + 6 + 1 + 6 + kv_n * CAP
    row_h = (M["b"] - GRID_Y - (len(rows) - 1) * GAP) / len(rows)
    # names can wrap to 2 lines: keep room for it
    long_name = any(len(c[0]) > cw / 6.6 for c in cards)
    if long_name:
        text_h += CAP
    ph = min(cw / 1.25, row_h - text_h)
    if ph < cw / 2.2:
        flags.append("%d cards: photos shortened to fit (%d px tall)" % (len(cards), ph))

    out = ['<section class="pj pj-b ss-proj" data-block="%s">' % key,
           '<div class="pj-panel%s" style="width:%s;background-image:url(%s)"></div>' % (" ss-dim" if dim else "", f(PANEL_W), panel)]
    segs = title_of(sid)
    t = "".join('<span class="%s%s">%s</span>' % ("is-b" if w == "b" else "is-l", " pj-red" if red else "", esc(x)) for x, w, red in segs)
    out.append('<h2 class="ss-head pj-ptitle ss-proj-title">%s</h2>' % t)
    out.append('<div class="ss-tb ss-proj-label" style="left:%s;top:%s;"><p class="t-caption is-b">%s</p></div>' % (f(X0), f(LABEL_Y), esc(label_of(sid))))
    out.append('<i class="pj-rule pj-red" style="left:%s;top:%s;width:%s;"></i>' % (f(X0), f(RULE_Y), f(M["r"] - X0)))
    # each card is ONE block (photo / logo badge / name + location / rule / AREA-SCOPE lines), so the editor can
    # add, remove and re-space cards (public/project-cards.js). Text rows have a shared height per slide (--ss-tx)
    # so the rules and value lines line up across a row.
    tx = CAP * (1 + (1 if has_loc else 0) + (1 if long_name else 0))
    i = 0
    y = GRID_Y
    for rc in rows:
        for j in range(rc):
            name, loc, kv = cards[i]
            x = X0 + j * (cw + GAP)
            photo = photos[i] if i < len(photos) else PLACEHOLDER
            badge = badges[i] if i < len(badges) else None
            out.append('<div class="ss-pcard" style="left:%s;top:%s;width:%s;--ss-ph:%s;--ss-tx:%s;">' % (f(x), f(y), f(cw), f(ph), f(tx)) +
                       '<div class="pj-ph ss-pc-ph" style="background-image:url(%s)"></div>' % photo +
                       ('<img class="ss-card-logo" src="%s" alt="">' % badge if badge else "") +
                       '<div class="ss-pc-text"><p class="t-caption is-b pj-nm">%s</p>%s</div>' % (esc(name), '<p class="t-caption is-r pj-lc">%s</p>' % esc(loc) if loc else "") +
                       '<i class="ss-pc-rule"></i>' +
                       '<div class="ss-pc-kv ss-kv">%s</div>' % "".join('<p class="t-caption"><span class="is-b ss-k">%s:</span><span class="is-r ss-v">%s</span></p>' % (esc(k), esc(v)) for k, v in kv) +
                       '</div>')
            i += 1
        y += row_h + GAP
    out.append('<footer class="ss-foot"><span class="ss-pn"></span><img class="ss-logo" src="%s" alt="HTL"></footer>' % LOGO)
    out.append("</section>")
    return {"html": "\n".join(out), "flags": flags}


KEYS = ["pj_" + s for s in ("bfsi1 bfsi2 bfsi3 cre1 cre2 dcnew dcmajor edu hosp1 hosp2 hosp3 hosp4 ind mfg res1 res2 "
                             "south1 south2 south3 south4 south5 pune1 pune3b pune3 mep1 mep2 vrv newwins").split()]
res = {k: build(k) for k in KEYS}
json.dump(res, open(os.path.join(HERE, "projects_result.json"), "w", encoding="utf-8"), ensure_ascii=False)
for k, r in res.items():
    print(k.ljust(12), "; ".join(r["flags"]) or "ok")
