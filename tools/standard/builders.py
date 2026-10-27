# -*- coding: utf-8 -*-
"""Slide builders for the Slide Standard + the patch step (see standard.py for tokens/base CSS).

Each builder reads the slide's ORIGINAL markup (kept in tools/standard/originals.json the
first time a slide is converted) only for its content and images, and returns new markup
that uses the standard classes only.

Run:  python tools/standard/builders.py [key ...]     (no keys = every slide with a builder)
"""
import importlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import standard as S  # noqa: E402
from standard import esc, slide  # noqa: E402

ROOT = S.ROOT
APP = S.APP


def snippets(s):
    a = s.find('id="all-snippets-data"')
    o = s.find(">", a) + 1
    e = s.find("</script>", o)
    return json.loads(s[o:e])


def urls(h, cls=None):
    """image URLs in reading order (background-image or <img src>)"""
    if cls:
        pat = r'class="[^"]*\b%s\b[^"]*"[^>]*?(?:background-image:url\(([^)]+)\)|src="([^"]+)")' % re.escape(cls)
    else:
        pat = r'(?:background-image:url\(([^)]+)\)|<img[^>]*src="([^"]+)")'
    return [a or b for a, b in re.findall(pat, h)]


def rich(t):
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(t))


# ------------------------------------------------------------------ About Us (reference-style slide)
def b_about_us(h, ctx):
    t = lambda pat: re.search(pat, h, re.S).group(1)
    eyebrow = t(r'class="block-kicker">([^<]+)<')
    head = t(r"<h2>([^<]+)</h2>")
    intro = t(r'block-about-us__body">([^<]+)<')
    m = re.search(r'block-about-us__map[^>]*><img src="([^"]+)" alt="([^"]*)"', h)
    mets = re.findall(r"<div><strong>([^<]+)</strong><span>([^<]+)</span></div>", h)
    inner = ['<h2 class="ss-h">%s</h2>' % head,
             '<p class="ss-body c-1-5 r-2">%s</p>' % intro,
             '<div class="ss-media is-contain ar-5-2 c-6-12 r-2"><img src="%s" alt="%s"></div>' % (m.group(1), m.group(2)),
             '<div class="ss-sub-grid g-4 c-1-12 r-3 sp-section">' +
             "".join('<div><p class="ss-sub is-accent">%s</p><p class="ss-detail is-caps sp-tight">%s</p></div>' % (a, b) for a, b in mets) + "</div>"]
    return slide("about_us", "about", inner, eyebrow=eyebrow, logo=ctx["logo"])


# ------------------------------------------------------------------ Journey
JOURNEY_MILESTONES = [
    ("2004", "Established **HTL Aircon** and executed 1st VRV project with Daikin"),
    ("2010", "Made inroads into mid-size **fit out projects**"),
    ("2017", "Reached the **100 CR turnover mark.** Won India’s Top 100 SME Award"),
    ("2018", "Started with **MEP Contracting** 10000 HP with Daikin."),
    ("2019", "Won **India’s Top 100 SME Award.** 400+ employees with 175 cr. Top line achieved"),
    ("2021", "Executed **50 MW of Data Centre**"),
    ("2026", "Executed **221 MW** of Data Centre"),
]
JOURNEY_STOPS = [("1996", "Year of commencement"), ("2010", "Pune branch"), ("2014", "Delhi branch"), ("2016", "Hyderabad branch"),
                 ("2020", "Data centre"), ("2023", "Expansion to Dubai"), ("2025", "HTL Biopharma")]


def b_journey(h, ctx):
    icons = urls(h, "pj-jill")
    rows_m = "".join('<p class="ss-body is-bold is-accent">%s</p><p class="ss-detail">%s</p>' % (y, rich(d)) for y, d in JOURNEY_MILESTONES)
    rows_e = "".join('<div class="ss-media is-contain ss-icon"><img src="%s" alt=""></div>'
                     '<p class="ss-detail"><strong class="is-accent">%s</strong>&nbsp;&nbsp;%s</p>' % (icons[i], y, esc(lab).upper())
                     for i, (y, lab) in enumerate(JOURNEY_STOPS))
    inner = ['<h2 class="ss-h">Stability &amp; Longevity</h2>',
             '<div class="c-1-7 r-2"><p class="ss-sub is-caps">Our milestones</p><div class="ss-tl sp-sub">%s</div></div>' % rows_m,
             '<div class="c-8-12 r-2"><p class="ss-sub is-caps">Expansion</p><div class="ss-tl sp-sub">%s</div></div>' % rows_e]
    return slide("pj_journey", "journey", inner, logo=ctx["logo"])


# ------------------------------------------------------------------ Our Expertise
EXPERTISE = [
    ("01", "Electrical", ["HT/LT Power Distribution", "Lighting Communication & Security Systems"]),
    ("02", "Plumbing", ["Drainage & Vent Pipes", "Water supply, WTP & STP", "Hydro-pneumatic systems", "Sanitary wares"]),
    ("03", "Fire Fighting", ["Fire Alarm", "NOVEC VESDA Sprinkler & Suppression Systems"]),
    ("04", "HVAC", ["VRV Systems", "Chilled Water System", "Precision Air conditioning", "Base build & Fitout"]),
    ("05", "PHE", ["Drainage & vent pipes", "Water supply, sewage & drainage systems"]),
    ("06", "IBMS", ["Devices & energy-saving sensors", "Occupancy", "Environment control System backbone", "Integration GUI, monitoring & BMS services"]),
    ("07", "Low Voltage Solutions", ["CCTV, access control & intrusion detection", "Motion-based lighting", "Structured cabling & networking", "Public address systems"]),
]


def b_expertise(h, ctx):
    photos = urls(h, "pj-ph")
    cards = []
    for i, (n, title, lines) in enumerate(EXPERTISE):
        cards.append('<div><div class="ss-media ar-4-1"><img src="%s" alt=""></div>'
                     '<p class="ss-detail is-bold sp-sub"><span class="is-accent">%s</span>&nbsp;&nbsp;%s</p>'
                     '<p class="ss-detail">%s</p></div>' % (photos[i], n, esc(title).upper(), "<br>".join(esc(l) for l in lines)))
    inner = ['<h2 class="ss-h">Our Expertise</h2>',
             '<div class="ss-sub-grid g-4 c-1-12 r-2">%s</div>' % "".join(cards)]
    return slide("pj_expertise", "expertise", inner, logo=ctx["logo"])


# ------------------------------------------------------------------ project slides (one template for all 28)
DC_STATS = {"dcmajor": [("120 MW", "Executed"), ("156 MW", "Under Execution")]}
AR = [("ar-1-1", 1.0), ("ar-4-3", 4 / 3.), ("ar-3-2", 1.5), ("ar-2-1", 2.0), ("ar-5-2", 2.5), ("ar-3-1", 3.0), ("ar-4-1", 4.0)]
SAFE_W, SAFE_H, GUT = 1136.0, 584.0, 24.0
LINE_D = 18.6667 * 1.4      # one Detail line
HEAD_LH = 66.6667 * 1.05


def head_lines(text, width=SAFE_W):
    return 1 if len(text) * 0.70 * 66.6667 <= width else 2


def project_cards(h, key):
    sys.path.insert(0, os.path.join(ROOT, "tools", "bira_slides"))
    C = importlib.import_module("content")
    sid = key[3:]
    photos = urls(h, "pj-ph") or urls(h, "pj-card")
    panel = (urls(h, "pj-panel") or [None])[0]
    cards, title, eyebrow = [], "", None
    if sid in C.Bs:
        d = C.Bs[sid]
        title = " ".join(d["panel"])
        for name, loc, kv in d["cards"]:
            cards.append((name, [loc], ["%s %s" % (k.rstrip(":").title() + ":", v) for k, v in kv]))
    elif sid in C.Cs:
        d = C.Cs[sid]
        title = " ".join("".join(seg[0] for seg in line) for line in d["title"])
        for c in d["cards"]:
            name, rest = c[0], list(c[1:])
            if len(rest) == 1:
                rest = ["Scope: " + rest[0]]
            elif sid == "vrv" and len(rest) == 2:
                rest = ["%s HP" % rest[0], rest[1]]
            cards.append((name, [], rest))
    elif sid in C.A:
        d = C.A[sid]
        title = " ".join("".join(seg[0] for seg in line) for line in d["title"])
        eyebrow = d.get("pill")
        for c in d["cards"]:
            lines = []
            if c.get("pilltext"):
                lines.append(c["pilltext"])
            lines += [" ".join(c["caption"]).replace(", ", ", ").strip()] if c.get("caption") else []
            lines += c.get("right", [])
            lines += ["%s %s" % (k.rstrip(":").title() + ":", v) for k, v in c.get("left", [])]
            cards.append((lines[0] if lines else "", [], lines[1:]))
    return re.sub(r"\s+", " ", title).strip(), eyebrow, cards, photos, panel


def grid_for(n):
    """cards per row - always 2, 3, 4 or 6 so every card starts and ends on a column edge"""
    if n <= 4:
        return max(n, 2)
    if n <= 6:
        return 3
    if n <= 8:
        return 4
    return 6 if n <= 12 else 4


def pick_ar(card_w, img_h):
    """the tallest standard photo shape that still fits"""
    for cls, r in AR:
        if card_w / r <= img_h:
            return cls, False
    return AR[-1][0], True


FLAGS = {}


def b_project(key):
    def build(h, ctx):
        title, eyebrow, cards, photos, panel = project_cards(h, key)
        n = len(cards)
        k = grid_for(n)
        rows = -(-n // k)
        stats = DC_STATS.get(key[3:])
        hl = head_lines(title, SAFE_W if not stats else 8 * 72.667 + 7 * 24)
        avail = SAFE_H - hl * HEAD_LH - 40
        row_h = (avail - GUT * (rows - 1)) / rows
        card_w = (SAFE_W - GUT * (k - 1)) / k
        cpl = max(8, int(card_w / (18.6667 * 0.56)))   # characters per Detail line in one card

        def nlines(cs):
            return max(sum(-(-max(1, len(t)) // cpl) for t in [nm] + sb + kv) for nm, sb, kv in cs)
        max_lines = nlines(cards)
        ar, tight = pick_ar(card_w, row_h - 16 - max_lines * LINE_D)
        if tight or card_w / dict(AR)[ar] > row_h - 16 - max_lines * LINE_D:
            # two short facts per line ("Area: 88k  ·  Scope: MEP") before giving up
            merged = [(nm, sb, ["  ·  ".join(kv[i:i + 2]) for i in range(0, len(kv), 2)]) for nm, sb, kv in cards]
            ml2 = nlines(merged)
            ar2, tight2 = pick_ar(card_w, row_h - 16 - ml2 * LINE_D)
            if ml2 < max_lines:
                cards, max_lines, ar, tight = merged, ml2, ar2, tight2
        if tight:
            FLAGS[key] = "%d cards with up to %d text lines do not fit at Detail size; photos are at the flattest standard shape (4:1)" % (n, max_lines)
        if len(photos) != n:
            FLAGS[key] = (FLAGS.get(key, "") + " photos %d vs cards %d" % (len(photos), n)).strip()
        out = []
        for i, (name, sub, kv) in enumerate(cards):
            img = photos[i] if i < len(photos) else ""
            out.append('<div><div class="ss-media %s"><img src="%s" alt=""></div><p class="ss-detail is-bold sp-sub">%s</p>%s%s</div>' % (
                ar, img, esc(name), "".join('<p class="ss-detail is-muted">%s</p>' % esc(x) for x in sub),
                "".join('<p class="ss-detail">%s</p>' % esc(x) for x in kv)))
        inner = ['<h2 class="ss-h%s">%s</h2>' % (" c-1-8 r-1" if stats else "", esc(title))]
        if stats:
            inner.append('<div class="ss-sub-grid g-2 c-9-12 r-1">%s</div>' % "".join(
                '<div><p class="ss-sub is-accent">%s</p><p class="ss-detail is-caps sp-tight">%s</p></div>' % (a, esc(b)) for a, b in stats))
        inner.append('<div class="ss-sub-grid g-%d c-1-12 r-2">%s</div>' % (k, "".join(out)))
        return slide(key, "projects", inner, eyebrow=eyebrow, bleed=panel, logo=ctx["logo"])
    return build


def project_keys():
    sys.path.insert(0, os.path.join(ROOT, "tools", "bira_slides"))
    C = importlib.import_module("content")
    return ["pj_" + sid for _, groups in C.SECTIONS for _, items in groups for sid, _ in items]


BUILDERS = {
    "about_us": b_about_us,
    "pj_journey": b_journey,
    "pj_expertise": b_expertise,
}
for _k in project_keys():
    BUILDERS[_k] = b_project(_k)
import builders2 as B2  # noqa: E402
BUILDERS.update(B2.BUILDERS2)

EXTRA_CSS = """
.ss .ss-tl{display:grid; grid-template-columns:calc(2 * var(--col-w) + var(--gutter)) minmax(0, 1fr); column-gap:var(--gutter); row-gap:var(--sp-tight); align-items:center;}
.ss .ss-tl .ss-icon{height:calc(var(--fs-body) * var(--lh-body));}
"""

FONT_LINK = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Raleway:wght@400;500;600;700&amp;display=swap" id="ss-font">'


def patch(keys):
    s = open(APP, encoding="utf-8").read()
    snip = snippets(s)
    ctx = {"logo": "/media/a18705566cb26d29.jpg"}  # the HTL logo used in every slide footer
    op = os.path.join(HERE, "originals.json")
    orig = json.load(open(op, encoding="utf-8")) if os.path.exists(op) else {}
    report = {}
    for k in keys:
        if k not in orig:
            orig[k] = snip[k]
        snip[k] = BUILDERS[k](orig[k], ctx)
        report[k] = len(snip[k])
    json.dump(orig, open(op, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    a = s.find('id="all-snippets-data"')
    o = s.find(">", a) + 1
    e = s.find("</script>", o)
    compact = '": "' not in s[o:o + 400]
    s = s[:o] + json.dumps(snip, ensure_ascii=False, separators=(",", ":") if compact else None).replace("</script", "<\\/script") + s[e:]
    s = re.sub(r'<style id="slide-standard">.*?</style>\n?', "", s, flags=re.S)
    s = s.replace("</head>", '<style id="slide-standard">' + S.CSS + EXTRA_CSS + B2.CSS2 + "</style>\n</head>", 1)
    if 'id="ss-font"' not in s:
        s = s.replace("</head>", FONT_LINK + "\n</head>", 1)
    for k in keys:  # every standard slide is laid out at 1280 px
        m = re.search(r"\n    %s: \d+,\n" % re.escape(k), s)
        if m:
            s = s[:m.start()] + "\n    %s: 1280,\n" % k + s[m.end():]
        else:
            s = s.replace("    thank_you: 1003,\n", "    thank_you: 1003,\n    %s: 1280,\n" % k, 1)
    open(APP, "w", encoding="utf-8").write(s)
    return report


if __name__ == "__main__":
    print(patch(sys.argv[1:] or list(BUILDERS)))
    FLAGS.update(B2.FLAGS)
    print("FLAGS", json.dumps(FLAGS, indent=1, ensure_ascii=False))
