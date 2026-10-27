# -*- coding: utf-8 -*-
"""Slide Standard builders for the remaining Profile slides (title, values, sectors, testimonials,
process / systems slides, client walls, thank you, org chart and the two picker-driven project slides).
Content and images come from each slide's original markup; layout uses the standard classes only."""
import html as H
import re

from standard import esc, slide


def U(h):
    """image URLs in reading order, any notation"""
    return [m.strip("'\"") for m in re.findall(r"""(?:src=["']|url\()(['"]?/media/[^"')]+)""", h)]


def T(h, pat, flags=re.S):
    m = re.search(pat, h, flags)
    return H.unescape(m.group(1)).strip() if m else ""


def one(t):
    """join a hand-broken line ("A\nB") back into running text"""
    return re.sub(r"\s*\n\s*", " ", t).strip()


def e(t):
    return esc(H.unescape(t))


FLAGS = {}


# ------------------------------------------------------------------ cover
def b_title(h, ctx):
    u = U(h)
    building, anniv, htl = u[0], u[1], u[2]
    return ('<section class="ss ss-cover" data-block="title_page">'
            '<div class="ss-cover-band"></div>'
            '<div class="ss-cover-photo"><img src="%s" alt=""></div>'
            '<div class="ss-safe">'
            '<h1 class="ss-h is-inverse">HTL Profile</h1>'
            '<div class="ss-lockup c-1-5"><img src="%s" alt="30th Anniversary"><i></i><img src="%s" alt="HTL"></div>'
            '</div></section>') % (building, anniv, htl)


# ------------------------------------------------------------------ vision / mission / values
def b_mvv(h, ctx):
    arts = re.findall(r"<article><span>([^<]+)</span><h2>([^<]+)</h2><p>([^<]+)</p></article>", h)
    cols = "".join('<div><p class="ss-detail is-caps is-bold is-accent">%s</p><p class="ss-sub sp-sub">%s</p>'
                   '<p class="ss-detail sp-sub">%s</p></div>' % (e(a), e(b), e(c)) for a, b, c in arts)
    FLAGS["mission_vision_values"] = "the slide had no heading; it now uses its own three labels as the heading (Vision · Mission · Values)"
    inner = ['<h2 class="ss-h">Vision · Mission · Values</h2>',
             '<div class="ss-sub-grid g-3 c-1-12 r-2">%s</div>' % cols]
    return slide("mission_vision_values", "mvv", inner, logo=ctx["logo"])


# ------------------------------------------------------------------ sectors
def b_sectors(h, ctx):
    cards = re.findall(r'sector-card__index">([^<]+)</span><h3>([^<]+)</h3>', h)
    out = "".join('<div class="ss-card"><p class="ss-detail is-bold is-accent">%s</p><p class="ss-body sp-tight">%s</p></div>' % (a, e(b)) for a, b in cards)
    inner = ['<h2 class="ss-h">%s</h2>' % e(T(h, r"<h2>([^<]+)</h2>")),
             '<div class="ss-sub-grid g-4 c-1-12 r-2">%s</div>' % out]
    return slide("major_projects_fixed", "sectors", inner, eyebrow=T(h, r'class="eyebrow">([^<]+)<'), logo=ctx["logo"])


# ------------------------------------------------------------------ testimonials
def b_testimonials(h, ctx):
    letters = [x for x in U(h) if x != ctx["logo"]]
    out = "".join('<div class="ss-media ar-4-3 is-letter"><img src="%s" alt="Client letter"></div>' % x for x in letters)
    inner = ['<h2 class="ss-h">Client Testimonials</h2>', '<div class="ss-sub-grid g-%d c-1-12 r-2">%s</div>' % (len(letters), out)]
    return slide("client_testimonials", "testimonials", inner, logo=ctx["logo"])


# ------------------------------------------------------------------ commissioning -> asset management
def b_commissioning(h, ctx):
    photos = U(h)
    steps = re.findall(r'class="ca-head"[^>]*>([^<]+)</strong><span class="ca-desc"[^>]*>([^<]+)</span>', h)
    ph = "".join('<div class="ss-media ar-1-1"><img src="%s" alt=""></div>' % p for p in photos)
    st = "".join('<div><p class="ss-detail is-bold is-accent is-caps">%s</p><p class="ss-detail sp-tight">%s</p></div>'
                 % (e(re.sub(r"\s*–\s*", " – ", one(a))), e(one(b))) for a, b in steps)
    inner = ['<h2 class="ss-h">From Commissioning to Asset Management</h2>',
             '<div class="ss-sub-grid g-2 c-1-4 r-2">%s</div>' % ph,
             '<div class="ss-sub-grid g-2 c-5-12 r-2">%s</div>' % st]
    return slide("commissioning_asset_management", "process", inner, logo=ctx["logo"])


# ------------------------------------------------------------------ driving projects with innovation
def b_driving(h, ctx):
    photo = [x for x in U(h) if x != ctx["logo"]][0]
    items = re.findall(r'class="di-h"[^>]*>([^<]+)</strong>.*?class="di-s"[^>]*>([^<]+)</span>', h)
    blocks = "".join('<div class="%s"><p class="ss-sub">%s</p><hr class="ss-rule sp-sub"><p class="ss-detail is-caps sp-sub">%s</p></div>'
                     % ("" if i == 0 else "sp-section", e(a).title(), e(b)) for i, (a, b) in enumerate(items))
    inner = ['<h2 class="ss-h">Driving Projects with Innovation</h2>',
             '<div class="ss-media ar-4-3 c-1-5 r-2"><img src="%s" alt=""></div>' % photo,
             '<div class="c-7-12 r-2">%s</div>' % blocks]
    return slide("driving_projects_innovation", "driving", inner, logo=ctx["logo"])


# ------------------------------------------------------------------ planning ERP
def b_erp(h, ctx):
    photo = U(h)[0]
    note = one(T(h, r'class="pe-note">([^<]+)<'))
    top = one(T(h, r'class="pe-top"[^>]*>([^<]+)<'))
    nodes = re.findall(r'class="pe-lh"[^>]*>([^<]+)</strong><span class="pe-ls"[^>]*>([^<]+)</span>', h)
    nd = "".join('<div><hr class="ss-rule is-accent"><p class="ss-detail is-bold is-caps sp-sub">%s</p><p class="ss-detail">%s</p></div>' % (e(a), e(b)) for a, b in nodes)
    FLAGS["planning_erp_system"] = "the dotted connector diagram is replaced by a rule above each of the four modules (it could not sit on the column grid)"
    inner = ['<h2 class="ss-h">Planning ERP System</h2>',
             '<div class="ss-media ar-1-1 c-1-4 r-2"><img src="%s" alt=""></div>' % photo,
             '<div class="c-5-12 r-2"><p class="ss-sub is-accent">%s</p><p class="ss-body sp-tight">%s</p>'
             '<p class="ss-sub sp-section">%s</p><div class="ss-sub-grid g-4 sp-sub">%s</div></div>' % (e(T(h, r'class="pe-pct">([^<]+)<')), e(note), e(top).title().replace("Erp", "ERP"), nd)]
    return slide("planning_erp_system", "erp", inner, logo=ctx["logo"])


# ------------------------------------------------------------------ project dashboard
def b_dashboard(h, ctx):
    shots = [x for x in U(h) if x != ctx["logo"]]
    out = "".join('<div class="ss-media ar-16-9 is-shot"><img src="%s" alt="Dashboard"></div>' % x for x in shots)
    inner = ['<h2 class="ss-h">Project Dashboard &amp; Reporting</h2>', '<div class="ss-sub-grid g-%d c-1-12 r-2">%s</div>' % (len(shots), out)]
    return slide("project_dashboard_reporting", "dashboard", inner, logo=ctx["logo"])


# ------------------------------------------------------------------ innovation in designing
def b_innovation(h, ctx):
    lis = re.findall(r"<li>([^<]+)</li>", h)
    bubs = re.findall(r'class="ib-in" style="background:(#[0-9a-f]+)"><span>([^<]+)</span>', h)
    tiles = "".join('<div class="ss-card is-tint"><p class="ss-detail is-bold">%s</p></div>' % e(one(t)) for _, t in bubs)
    inner = ['<h2 class="ss-h">Innovation in Designing</h2>',
             '<div class="c-1-5 r-2"><p class="ss-sub">Auto CAD &amp; BIM <span class="is-muted">- Design Solutions</span></p>'
             '<p class="ss-detail is-bold is-caps is-accent sp-section">%s</p>%s</div>' % (e(T(h, r'class="ib-kick">([^<]+)<')),
                                                                                         "".join('<p class="ss-body%s">%s</p>' % (" sp-tight" if i else " sp-sub", e(x)) for i, x in enumerate(lis))),
             '<div class="ss-sub-grid g-3 c-6-12 r-2">%s</div>' % tiles]
    return slide("innovation_in_designing", "innovation", inner, logo=ctx["logo"])


# ------------------------------------------------------------------ safety
def b_safety(h, ctx):
    groups = re.findall(r"<h3><img src=\"([^\"]+)\" alt=\"\"><span>([^<]+)</span></h3><div>(.*?)</div></section>", h, re.S)
    cols = []
    spans = ["c-1-3", "c-4-6", "c-7-12"]
    for gi, (icon, name, body) in enumerate(groups):
        items = re.findall(r'<img src="([^"]+)" alt=""><p>([^<]+)</p>', body)
        lst = "".join('<p class="ss-detail ss-with-icon"><img src="%s" alt="">%s</p>' % (ic, e(t)) for ic, t in items)
        two = len(items) > 6
        cols.append('<div class="%s r-3 sp-section"><p class="ss-sub ss-with-icon"><img src="%s" alt="">%s</p><div class="ss-list%s sp-sub">%s</div></div>'
                    % (spans[gi], icon, e(name), " is-2col" if two else "", lst))
    head = H.unescape(re.sub(r"<[^>]+>", "", T(h, r"<h2>(.*?)</h2>")))
    inner = ['<h2 class="ss-h">%s</h2>' % e(head),
             '<p class="ss-body c-1-8 r-2">%s</p>' % e(T(h, r"</h2><p>([^<]+)</p>")),
             "".join(cols)]
    return slide("safety_practices_hse_policy", "safety", inner, eyebrow=T(h, r'class="block-kicker">([^<]+)<'), logo=ctx["logo"])


# ------------------------------------------------------------------ quality policy
def b_quality(h, ctx):
    items = re.findall(r'<i class="qp-icon">(<svg.*?</svg>)</i><strong class="qp-item-title">([^<]+)</strong><span class="qp-item-text">([^<]+)</span>', h, re.S)
    its = "".join('<div class="ss-iconrow"><i class="ss-disc">%s</i><div><p class="ss-detail is-bold is-caps">%s</p><p class="ss-detail sp-tight">%s</p></div></div>'
                  % (svg, e(a), e(one(b))) for svg, a, b in items)
    quote = one(T(h, r'class="qp-quote">([^<]+)<'))
    by = one(T(h, r'class="qp-by">([^<]+)<'))
    inner = ['<h2 class="ss-h">Quality Policy</h2>',
             '<div class="ss-sub-grid g-2 c-1-8 r-2">%s</div>' % its,
             '<div class="ss-card c-9-12 r-2"><p class="ss-sub">%s</p><p class="ss-detail is-muted sp-sub">%s</p></div>' % (e(quote), e(by))]
    return slide("quality_checklist", "quality", inner, logo=ctx["logo"])


# ------------------------------------------------------------------ service implementation process
SIP_COLOURS = {"#ff3a3a": "sip-c1", "#e60000": "sip-c2", "#d3281f": "sip-c3", "#d90000": "sip-c4"}


def b_service(h, ctx):
    cards = re.findall(r'<i class="sip-badge"[^>]*>(<svg.*?</svg>)</i><div class="sip-red" style="background:(#[0-9a-f]+)"><span class="sip-text">([^<]+)</span><i class="sip-notch"></i><strong class="sip-num">([^<]+)</strong>', h, re.S)
    cards.sort(key=lambda c: c[3])
    cs = "".join('<div class="ss-card is-red %s"><div class="ss-cardtop"><p class="ss-sub">%s</p><i class="ss-badge">%s</i></div><p class="ss-detail sp-sub">%s</p></div>'
                 % (SIP_COLOURS.get(col, "sip-c2"), n, svg, e(one(t))) for svg, col, t, n in cards)
    stats = re.findall(r'class="sip-label">([^<]+)</span><span class="sip-value"[^>]*>([^<]+)</span>', h)
    st = "".join('<div><p class="ss-detail is-caps is-muted">%s</p><p class="ss-body is-bold is-accent">%s</p></div>' % (e(a), e(b).replace("&amp;P", "&amp; P")) for a, b in stats)
    inner = ['<h2 class="ss-h">Service Implementation Process</h2>',
             '<div class="ss-sub-grid g-6 c-1-12 r-2">%s</div>' % cs,
             '<div class="ss-sub-grid g-3 c-1-12 r-3 sp-para">%s</div>' % st]
    return slide("service_implementation_process", "service", inner, logo=ctx["logo"])


# ------------------------------------------------------------------ why HTL
WH_COLOURS = {"#f50000": "wh-c1", "#d9261c": "wh-c2", "#9b1a10": "wh-c3", "#6b0f0f": "wh-c4", "#e06666": "wh-c5"}


def b_why(h, ctx):
    items = re.findall(r'class="wh-num"[^>]*>([^<]+)</strong><strong class="wh-head[^"]*"[^>]*>([^<]+)</strong><span class="wh-text[^"]*"[^>]*>([^<]+)</span>', h)
    discs = re.findall(r'<i class="wh-disc" style="background:(#[0-9a-f]+)">(<svg.*?</svg>)</i>', h, re.S)
    rows = []
    for i, (n, hd, tx) in enumerate(items):
        col, svg = discs[i] if i < len(discs) else ("#f50000", "")
        rows.append('<div class="ss-iconrow"><i class="ss-disc %s">%s</i><div><p class="ss-detail is-bold"><span class="is-accent">%s</span>&nbsp;&nbsp;%s</p><p class="ss-detail sp-tight">%s</p></div></div>'
                    % (WH_COLOURS.get(col, "wh-c1"), svg, n, e(hd).upper(), e(one(tx))))
    FLAGS["why_htl_mep"] = "the curved connector lines between the five icons are left out (they could not sit on the column grid); each icon now sits beside its point"
    inner = ['<h2 class="ss-h">Why HTL for MEP</h2>',
             '<div class="c-1-6 r-2 ss-stack">%s</div>' % "".join(rows[:3]),
             '<div class="c-7-12 r-2 ss-stack">%s</div>' % "".join(rows[3:])]
    return slide("why_htl_mep", "why", inner, logo=ctx["logo"])


# ------------------------------------------------------------------ client walls
def b_wall(key, title):
    def build(h, ctx):
        img = [x for x in U(h) if x != ctx["logo"]][0]
        inner = ['<h2 class="ss-h">%s</h2>' % title, '<div class="ss-media is-contain ar-5-2 c-1-12 r-2"><img src="%s" alt="Client logos"></div>' % img]
        return slide(key, "wall", inner, logo=ctx["logo"])
    return build


# ------------------------------------------------------------------ thank you
def b_thanks(h, ctx):
    u = U(h)
    anniv, htl, photo = u[0], u[1], u[2]
    inner = ['<h2 class="ss-h c-1-8 r-1">Thank You</h2>',
             '<div class="ss-lockup is-small c-9-12 r-1"><img src="%s" alt="30th Anniversary"><i></i><img src="%s" alt="HTL"></div>' % (anniv, htl),
             '<div class="ss-media ar-3-1 c-1-12 r-2"><img src="%s" alt=""></div>' % photo,
             '<p class="ss-detail is-caps is-bold c-1-12 r-3 sp-sub">%s</p>' % e(T(h, r'class="ty-cities">([^<]+)<'))]
    return slide("thank_you", "thanks", inner)


# ------------------------------------------------------------------ org structure
def b_org(h, ctx):
    # people in reading order: photo, name, role lines (role may be split over two spans)
    photos = [x for x in U(h) if "pj-logo" not in x]
    texts = [H.unescape(t) for t in re.findall(r'class="pj-t[^"]*"[^>]*>([^<]+)<', h)]
    heads = ["LEADERSHIP", "DIRECTORS", "STRATEGY & SALES", "DIVISIONAL LEADERSHIP", "MEP LEADERSHIP"]
    body = [t for t in texts if t not in heads and t not in ("ORG", "STRUCTURE")]
    PEOPLE = [("Lavinder Duggal", "Founder & MD"), ("Bhupinder Duggal", "President"), ("Vishal Jadhav", "National Director"),
              ("Jasraj Chauhan", "VP - Sales & key accounts"), ("Harkirat Duggal", "Business Strategist & Int. Markets"), ("Lalita P.", "Head Procurement"),
              ("Kunal P.", "Head Technology"), ("Sachin Baraskar", "National MEP Head"), ("Dharmendra Tambe", "General Manager ELV & BMS"),
              ("Ashok Nayak", "Director"), ("Anuj Nigam", "CGO"), ("Shiv Kumar", "Head Service"), ("Sanjay Panchal", "AGM - Design"),
              ("Vigeshvar Durairaj", "Regional Head - South, Projects & Operations"), ("Syam Das", "Head - Testing & Commissioning")]
    pic = dict(zip([p[0] for p in PEOPLE], photos))
    GROUPS = [("Leadership", ["Lavinder Duggal", "Bhupinder Duggal"]), ("Directors", ["Vishal Jadhav", "Ashok Nayak"]),
              ("Strategy & Sales", ["Jasraj Chauhan", "Harkirat Duggal", "Anuj Nigam"]),
              ("Divisional Leadership", ["Lalita P.", "Kunal P.", "Shiv Kumar", "Sanjay Panchal"]),
              ("MEP Leadership", ["Sachin Baraskar", "Dharmendra Tambe", "Vigeshvar Durairaj", "Syam Das"])]
    role = dict(PEOPLE)

    def person(n):
        return ('<div class="ss-person"><div class="ss-media ar-1-1 is-portrait"><img src="%s" alt=""></div>'
                '<div><p class="ss-detail is-bold">%s</p><p class="ss-detail is-muted">%s</p></div></div>' % (pic[n], e(n), e(role[n])))

    def group(name, people, extra=""):
        return '<div class="%s"><p class="ss-detail is-bold is-caps is-accent">%s</p><div class="ss-list sp-sub">%s</div></div>' % (extra, e(name), "".join(person(p) for p in people))
    cols = [group(*GROUPS[0]) + group(*GROUPS[1], "sp-para"), group(*GROUPS[2]), group(*GROUPS[3]), group(*GROUPS[4])]
    FLAGS.pop("pj_orgstructure", None)
    inner = ['<h2 class="ss-h">Org Structure</h2>'] + ['<div class="c-%d-%d r-2">%s</div>' % (1 + 3 * i, 3 + 3 * i, c) for i, c in enumerate(cols)]
    return slide("pj_orgstructure", "org", inner, logo=ctx["logo"])


# ------------------------------------------------------------------ picker-driven project slides (cards are rebuilt by the app's project picker)
def b_bp(key):
    def build(h, ctx):
        side = U(h)[0]
        t = [H.unescape(x) for x in re.findall(r'class="bp-t[13]">([^<]+)<|<strong class="bp-t2"[^>]*><span>([^<]+)</span>', h) for x in x if x]
        title = " ".join(t)
        grid = re.search(r'(<div class="bp-grid".*?</article></div>)</div>', h, re.S).group(1)
        grid = grid.replace('<div class="bp-grid"', '<div class="bp-grid c-1-12 r-2"', 1)
        inner = ['<h2 class="ss-h">%s</h2>' % e(title).title().replace("Hospital ", "Hospital "), grid]
        return slide(key, "bp", inner, eyebrow="Projects", bleed=side, logo=ctx["logo"])
    return build


BUILDERS2 = {
    "title_page": b_title,
    "mission_vision_values": b_mvv,
    "major_projects_fixed": b_sectors,
    "client_testimonials": b_testimonials,
    "commissioning_asset_management": b_commissioning,
    "driving_projects_innovation": b_driving,
    "planning_erp_system": b_erp,
    "project_dashboard_reporting": b_dashboard,
    "innovation_in_designing": b_innovation,
    "safety_practices_hse_policy": b_safety,
    "quality_checklist": b_quality,
    "service_implementation_process": b_service,
    "why_htl_mep": b_why,
    "key_repeat_clients": b_wall("key_repeat_clients", "Key Repeat Clients"),
    "key_clients": b_wall("key_clients", "Key Clients"),
    "thank_you": b_thanks,
    "pj_orgstructure": b_org,
    "major_projects_customisable": b_bp("major_projects_customisable"),
    "major_projects_segment_hospitals": b_bp("major_projects_segment_hospitals"),
}

CSS2 = """
/* cover: red band + building bleed off the right/bottom edge; heading on the margin like every slide */
.ss-cover .ss-cover-band{position:absolute; left:0; right:0; top:0; height:calc(var(--m-top) + var(--fs-heading) * var(--lh-heading) + var(--sp-section)); background:#e3262c;}
.ss-cover .ss-cover-photo{position:absolute; right:0; bottom:0; left:calc(var(--m-left) + 5 * var(--pitch)); top:calc(var(--m-top) + var(--fs-heading) * var(--lh-heading) + var(--sp-section));}
.ss-cover .ss-cover-photo > img{width:100%; height:100%; object-fit:cover; object-position:left top; display:block; max-width:none;}
.ss-cover .ss-safe{grid-template-rows:min-content 1fr; align-content:stretch;}
.ss .ss-h.is-inverse{color:#fff;}
.ss .ss-lockup{display:flex; align-items:center; gap:var(--sp-paragraph); align-self:end; grid-row:2;}
.ss .ss-lockup > img{height:calc(var(--fs-heading) * .8); width:auto; display:block; max-width:none;}
.ss .ss-lockup > i{width:1px; align-self:stretch; background:var(--c-rule);}
.ss .ss-lockup.is-small{grid-row:1; align-self:start; justify-content:flex-end;}
.ss .ss-lockup.is-small > img{height:calc(var(--fs-sub) * 1.2);}
/* shared bits */
.ss .ar-3-4{aspect-ratio:3/4;}
.ss .ss-media.is-letter, .ss .ss-media.is-shot{box-shadow:0 2px 8px rgba(0,0,0,.18);}
.ss .ss-media.is-shot > img{object-fit:fill;}
.ss .ss-media.is-portrait > img{object-position:center top;}
.ss .ss-rule.is-accent{border-top-color:var(--c-accent); border-top-width:2px;}
.ss .ss-card.is-tint{background:#fde3e3;}
.ss .ss-card.is-red{color:#fff;} .ss .ss-card.is-red .ss-sub, .ss .ss-card.is-red .ss-detail{color:#fff;}
.ss .sip-c1{background:#ff3a3a;} .ss .sip-c2{background:#e60000;} .ss .sip-c3{background:#d3281f;} .ss .sip-c4{background:#d90000;}
.ss .ss-cardtop{display:flex; align-items:center; justify-content:space-between;}
.ss .ss-badge{width:calc(var(--fs-sub) * 1.2); height:calc(var(--fs-sub) * 1.2); border-radius:50%; background:#fff; display:grid; place-items:center;}
.ss .ss-badge svg{width:70%; height:70%;}
.ss .ss-with-icon{display:flex; align-items:center; gap:var(--sp-tight);}
.ss .ss-with-icon > img{height:1.2em; width:auto; flex:none; display:block; max-width:none;}
.ss .ss-iconrow{display:grid; grid-template-columns:var(--col-w) minmax(0, 1fr); column-gap:var(--gutter); align-items:start;}
.ss .ss-list{display:grid; row-gap:var(--sp-tight);} .ss .ss-list.is-2col{grid-template-columns:repeat(2, minmax(0, 1fr)); column-gap:var(--gutter);}
.ss .ss-person{display:grid; grid-template-columns:var(--col-w) minmax(0, 1fr); column-gap:var(--sp-paragraph); align-items:start;}
.ss .ss-stack{display:grid; row-gap:var(--sp-paragraph); align-content:start;}
.ss .ss-sub-grid > .ss-iconrow{align-self:start;}
.ss .ss-disc{width:var(--col-w); height:var(--col-w); border-radius:50%; background:var(--c-accent); display:grid; place-items:center;}
.ss .ss-disc svg{width:58%; height:58%;}
.ss .wh-c1{background:#f50000;} .ss .wh-c2{background:#d9261c;} .ss .wh-c3{background:#9b1a10;} .ss .wh-c4{background:#6b0f0f;} .ss .wh-c5{background:#e06666;}
/* picker-driven project grid: the app sets each card's column span (3, 4, 6 or 12) */
.ss .bp-grid{position:relative; display:grid; grid-template-columns:repeat(12, minmax(0, 1fr)); column-gap:var(--gutter); row-gap:var(--sp-paragraph);
  height:calc(var(--slide-h) - var(--m-top) - var(--m-bottom) - var(--fs-heading) * var(--lh-heading) - var(--sp-heading-body)); grid-template-rows:repeat(2, minmax(0, 1fr));}
.ss .bp-grid[data-rows="1"]{grid-template-rows:minmax(0, 1fr);} .ss .bp-grid[data-rows="3"]{grid-template-rows:repeat(3, minmax(0, 1fr));}
.ss .bp-card{position:relative; display:flex; flex-direction:column; min-width:0; min-height:0;}
.ss .bp-card__img{flex:1 1 0; min-height:var(--col-w); background-color:#e4e1da; background-size:cover; background-position:center; position:relative;}
.ss .bp-card__img--empty{display:grid; place-items:center;}
.ss .bp-card__img--empty span{font-size:var(--fs-detail); color:#8d887c;}
.ss .bp-card h3{margin:var(--sp-sub-content) 0 0; font-size:var(--fs-detail); line-height:var(--lh-detail); font-weight:700; color:var(--c-ink);}
.ss .bp-loc{margin:0; font-size:var(--fs-detail); line-height:var(--lh-detail); color:var(--c-muted);}
.ss .bp-meta{margin:0; display:grid; grid-template-columns:auto 1fr; column-gap:var(--sp-tight); font-size:var(--fs-detail); line-height:var(--lh-detail);}
.ss .bp-meta > div{display:contents;} .ss .bp-meta dt{margin:0; font-weight:400;} .ss .bp-meta dd{margin:0;}
.ss .bp-grid > .ws-ghost-card{position:absolute; top:calc(-1 * var(--sp-heading-body) - var(--fs-detail)); right:0; width:auto; height:auto; min-height:0; white-space:nowrap; flex:none; flex-direction:row; gap:6px; padding:5px 12px; border-radius:999px; font-size:11px; background:#fff;}
.ss .bp-card .ws-card-remove{top:6px; right:6px;}
"""
