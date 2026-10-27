# -*- coding: utf-8 -*-
"""Slide Standard (brief: "Slide Standard: Implementation Brief", Oct 2026).

One grid, one type scale, one spacing system for every slide. The brief is in
PowerPoint points on a 960 x 540 pt canvas; slides here are 1280 x 720 px, so
1 pt = 4/3 px. Every value lives in a token on :root (see CSS below); slide
markup only uses classes - no inline sizes, margins or positions.

Run:  python tools/standard/standard.py [key ...]
      (no keys = every slide that has a builder)
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP = os.path.join(ROOT, "src", "frontend", "app.html")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PT = 4.0 / 3.0


def px(pt):
    v = pt * PT
    return ("%.3f" % v).rstrip("0").rstrip(".") + "px"


# ------------------------------------------------------------------ tokens + base layout
CSS = """
/* ===== Slide Standard: tokens (brief values in pt, canvas 960x540 pt = 1280x720 px) ===== */
:root{
  --slide-w:1280px; --slide-h:720px;
  /* margins: 54 / 54 / 54 / 48 pt */
  --m-left:%(m54)s; --m-right:%(m54)s; --m-top:%(m54)s; --m-bottom:%(m48)s;
  /* grid: 12 x 54.5 pt columns, 18 pt gutter, 72.5 pt pitch */
  --cols:12; --col-w:%(col)s; --gutter:%(gut)s; --pitch:%(pitch)s;
  /* type */
  --font-heading:"Raleway","Montserrat","Segoe UI",Arial,sans-serif;
  --font-text:"TT Norms Pro","TT Norms","Segoe UI",Arial,sans-serif;
  --fw-heading:700;
  --fs-heading:%(h)s; --lh-heading:1.05;
  --fs-sub:%(sub)s;  --lh-sub:1.2;
  --fs-body:%(body)s;  --lh-body:1.4;
  --fs-detail:%(det)s; --lh-detail:1.4;
  /* spacing (multiples of 6 pt) */
  --sp-eyebrow:%(s6)s; --sp-heading-body:%(s30)s; --sp-paragraph:%(s18)s; --sp-section:%(s36)s; --sp-sub-content:%(s12)s;
  --sp-card-pad:%(s12)s; --sp-tight:%(s6)s;
  /* colours already used on the slides (unchanged) */
  --c-ink:#111111; --c-text:#222222; --c-muted:#5b5b5b; --c-accent:#e3262c; --c-card:#f3f3f3; --c-rule:#d4d4d4; --c-bg:#ffffff;
  --logo-h:%(logo)s;
}
""" % dict(m54=px(54), m48=px(48), col=px(54.5), gut=px(18), pitch=px(72.5), h=px(50), sub=px(26), body=px(20), det=px(14),
           s6=px(6), s12=px(12), s18=px(18), s30=px(30), s36=px(36), logo=px(14))

CSS += """
/* ===== base slide: canvas, safe area = 12-column grid ===== */
.ss{position:relative; width:var(--slide-w); height:var(--slide-h); overflow:hidden; background:var(--c-bg); color:var(--c-text);
  font-family:var(--font-text); font-size:var(--fs-body); line-height:var(--lh-body); text-align:left; box-sizing:border-box;}
.ss *, .ss *::before, .ss *::after{box-sizing:border-box;}
.ss .ss-safe{position:absolute; left:var(--m-left); right:var(--m-right); top:var(--m-top); bottom:var(--m-bottom);
  display:grid; grid-template-columns:repeat(var(--cols), var(--col-w)); column-gap:var(--gutter); row-gap:0;
  grid-auto-rows:min-content; align-content:start; align-items:start;}
.ss .ss-safe > *{margin:0; min-width:0;}
/* sub-grid for a block that spans columns and holds its own column-aligned children */
.ss .ss-sub-grid{display:grid; column-gap:var(--gutter); row-gap:var(--sp-paragraph); align-items:start;}

/* ===== the four type styles ===== */
.ss .ss-h{font-family:var(--font-heading); font-weight:var(--fw-heading); font-size:var(--fs-heading); line-height:var(--lh-heading);
  text-transform:uppercase; letter-spacing:0; color:var(--c-ink); grid-column:1 / -1; margin:0 0 var(--sp-heading-body);}
.ss .ss-sub{font-family:var(--font-text); font-weight:700; font-size:var(--fs-sub); line-height:var(--lh-sub); color:var(--c-ink); margin:0;}
.ss .ss-body{font-family:var(--font-text); font-weight:400; font-size:var(--fs-body); line-height:var(--lh-body); color:var(--c-text); margin:0;}
.ss .ss-detail{font-family:var(--font-text); font-weight:400; font-size:var(--fs-detail); line-height:var(--lh-detail); color:var(--c-text); margin:0;}
.ss .ss-sub.is-caps, .ss .ss-detail.is-caps{text-transform:uppercase; letter-spacing:.04em;}
.ss .is-bold{font-weight:700;} .ss .is-accent{color:var(--c-accent);} .ss .is-muted{color:var(--c-muted);}
.ss .ss-body strong, .ss .ss-detail strong, .ss .ss-sub strong{font-weight:700; color:var(--c-ink);}
/* eyebrow: Detail style, sits in the top margin so every heading starts at y = 54 pt */
.ss .ss-eyebrow{position:absolute; left:0; bottom:calc(100% + var(--sp-eyebrow)); font-size:var(--fs-detail); line-height:var(--lh-detail);
  font-weight:700; text-transform:uppercase; letter-spacing:.08em; color:var(--c-accent); white-space:nowrap;}

/* ===== spacing steps ===== */
.ss .sp-para{margin-top:var(--sp-paragraph);} .ss .sp-section{margin-top:var(--sp-section);} .ss .sp-sub{margin-top:var(--sp-sub-content);}
.ss .sp-tight{margin-top:var(--sp-tight);}
.ss .ss-sub + .ss-detail, .ss .ss-sub + .ss-body, .ss .ss-sub + .ss-sub-grid{margin-top:var(--sp-sub-content);}
.ss .ss-body + .ss-body, .ss .ss-detail + .ss-detail.is-para{margin-top:var(--sp-paragraph);}

/* ===== media: snaps to the columns it spans ===== */
.ss .ss-media{position:relative; overflow:hidden; width:100%; background:#ece9e4;}
.ss .ss-media > img{position:absolute; inset:0; width:100%; height:100%; object-fit:cover; display:block; max-width:none;}
.ss .ss-media.is-contain{background:transparent;} .ss .ss-media.is-contain > img{object-fit:contain; object-position:left top;}
.ss .ar-16-9{aspect-ratio:16/9;} .ss .ar-3-2{aspect-ratio:3/2;} .ss .ar-2-1{aspect-ratio:2/1;} .ss .ar-5-2{aspect-ratio:5/2;} .ss .ar-3-1{aspect-ratio:3/1;} .ss .ar-4-1{aspect-ratio:4/1;} .ss .ar-4-3{aspect-ratio:4/3;} .ss .ar-1-1{aspect-ratio:1/1;}
/* intentional bleed: a photo strip in the left margin, flush with the slide edge */
.ss .ss-bleed-left{position:absolute; left:0; top:0; bottom:0; width:calc(var(--m-left) - var(--gutter)); overflow:hidden;}
.ss .ss-bleed-left > img{width:100%; height:100%; object-fit:cover; display:block; max-width:none;}

/* ===== cards + rules (shapes only; text inside uses the type styles) ===== */
.ss .ss-card{background:var(--c-card); padding:var(--sp-card-pad); border-radius:var(--sp-card-pad);}
.ss .ss-rule{border:0; border-top:1px solid var(--c-rule); height:0; margin:0;}
.ss .ss-kv{display:grid; grid-template-columns:auto 1fr; column-gap:var(--sp-tight);}

/* ===== bottom margin: page number left, logo right ===== */
.ss .ss-foot{position:absolute; left:var(--m-left); right:var(--m-right); bottom:0; height:var(--m-bottom); display:flex; align-items:center; justify-content:space-between;}
.ss .ss-pn{font-size:var(--fs-detail); line-height:1; color:var(--c-muted); font-variant-numeric:tabular-nums;}
.ss .ss-pn::before{content:counter(ss-page, decimal-leading-zero);}
.ss .ss-logo{height:var(--logo-h); width:auto; display:block; max-width:none;}
.ws-slide, .share-slide, .dr-item, .thumb-card{counter-increment:ss-page;}
#wsLeft, #wsPreviewScroll, .deck-group, body{counter-reset:ss-page;}
"""

# grid placement classes: c-a-b spans columns a..b (all 78 combinations), r-n puts a block on row n
for a in range(1, 13):
    for b in range(a, 13):
        CSS += ".ss .c-%d-%d{grid-column:%d / %d;}" % (a, b, a, b + 1)
    CSS += "\n"
for n in range(1, 9):
    CSS += ".ss .r-%d{grid-row:%d;}" % (n, n)
CSS += "\n"
for k in (2, 3, 4, 5, 6, 7, 8):
    CSS += ".ss .ss-sub-grid.g-%d{grid-template-columns:repeat(%d, minmax(0, 1fr));}" % (k, k)
CSS += "\n"


# ------------------------------------------------------------------ helpers
def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def slide(key, kind, inner, eyebrow=None, bleed=None, logo=None):
    out = ['<section class="ss ss-%s" data-block="%s">' % (kind, key)]
    if bleed:
        out.append('<div class="ss-bleed-left"><img src="%s" alt=""></div>' % bleed)
    out.append('<div class="ss-safe">')
    if eyebrow:
        out.append('<p class="ss-eyebrow">%s</p>' % esc(eyebrow))
    out.extend(inner)
    out.append("</div>")
    out.append('<footer class="ss-foot"><span class="ss-pn"></span>%s</footer>' % ('<img class="ss-logo" src="%s" alt="HTL">' % logo if logo else ""))
    out.append("</section>")
    return "".join(out)
