# -*- coding: utf-8 -*-
"""Easier for everyone (managers who are not at ease with software):
bigger type and buttons, sidebar always with words, clearer step bar, labelled "In deck / Add" tags on the
slide picker, plain button names, a gentler right-hand panel, a "How it works" guide (public/easy-ui.js)."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def edit(path, pairs):
    p = os.path.join(ROOT, path)
    s = open(p, encoding="utf-8").read()
    for o, n in pairs:
        assert s.count(o) == 1, (path, s.count(o), o[:90])
        s = s.replace(o, n)
    open(p, "w", encoding="utf-8").write(s)


p = os.path.join(ROOT, "src", "frontend", "app.html")
s = open(p, encoding="utf-8").read()

# 1 -- sidebar keeps its words on every screen (drop the icons-only mode)
a = s.index("@media (min-width:901px){\n  body[data-screen=\"build\"] .shell")
b = s.index("\n}\n", a) + 3
s = s[:a] + s[b:]

# 2 -- wording
for o, n in [
    ("Finalize &amp; share</button>", "Finish &amp; share</button>"),
    ('<span>Projects</span></button>', '<span>Project list</span></button>'),
    ('title="Projects"', 'title="Project list"'),
    ('<button class="back-link" data-goto="dashboard">‹ Decks</button><h2>Projects</h2>', '<button class="back-link" data-goto="dashboard">‹ Decks</button><h2>Project list</h2>'),
]:
    assert s.count(o) >= 1, o
    s = s.replace(o, n)

CSS = """
<style id="easy-ui">
  /* ================= Easier for everyone: bigger, clearer, fewer surprises ================= */
  body{font-size:16px; line-height:1.45;}
  body .shell{padding:36px 40px 72px 264px;}
  body .app-header{width:232px; padding:26px 14px 18px;}
  body .app-header__brand{font-size:1.2rem; margin-bottom:30px;}
  body .nav-item{font-size:1rem; padding:12px 14px; gap:14px; border-radius:10px;}
  body .nav-item svg{width:20px; height:20px;}
  body .app-header__user-info{font-size:.88rem; margin-top:12px;}
  body .nav-item--out{font-size:.92rem; padding:9px 14px;}
  body .nav-item--out svg{width:16px; height:16px;}
  body .nav-item--help{order:80; margin-top:auto; color:#1f2937; background:var(--surface-sunken); font-weight:600;}
  body .nav-item--help:hover{background:var(--accent-wash); color:#b91c1c;}

  .screen-head h2{font-size:1.9rem; font-weight:700;}
  .screen-head__sub{font-size:1.05rem;}
  .back-link{font-size:.95rem; font-weight:600; color:#4b5563; padding:4px 0;}
  .back-link:hover{color:#b91c1c;}

  .btn{font-size:1rem; padding:10px 18px; min-height:44px; border-radius:10px;}
  .btn--lg{font-size:1.05rem; padding:12px 24px; min-height:48px;}
  .btn--sm{font-size:.9rem; padding:7px 14px; min-height:36px;}
  .field-inline label, .login-field label{font-size:.9rem; font-weight:600; color:#374151;}
  .field-inline select, .field-inline input, .search, .ws-search, .login-field input{font-size:1rem; padding:10px 14px; border-radius:10px;}
  .dash-toolbar .search{width:340px;}
  .dash-toolbar__archive-toggle{font-size:.95rem;}

  /* the 1-2-3 steps */
  .steps{gap:10px; margin:0 0 20px; font-size:1rem;}
  .steps i{width:28px;}
  .steps__item{padding:9px 18px; font-size:1rem; font-weight:600; border-radius:999px;}
  .steps__item.is-now{background:#111827; color:#fff;}
  .steps__item.is-done{background:var(--success-wash); color:var(--success);}

  /* deck cards */
  .deck-card__name{font-size:1.05rem;}
  .deck-card__meta{font-size:.9rem;}
  .pill{font-size:.85rem; padding:3px 11px;}
  .timestamp{font-size:.82rem;}
  .deck-card__menu-btn{width:auto; height:auto; border-radius:999px; padding:6px 14px; font-size:.9rem; font-weight:600; line-height:1.2; top:10px; right:10px;}
  .deck-card__menu{top:48px; right:10px; min-width:200px;}
  .deck-card__menu-item{font-size:1rem; padding:11px 14px;}
  .empty-state strong{font-size:1.1rem;} .empty-state span{font-size:1rem;}

  /* choose slides */
  .deck-hint{font-size:1rem; padding:12px 16px; background:var(--surface); border:1px solid var(--line); border-radius:12px; margin-bottom:16px;}
  .section-group__title{font-size:.95rem;}
  .deck-group__title{font-size:1.1rem;}
  .build-nav__lbl, .build-nav__deck{font-size:.8rem;}
  .build-chip{font-size:.95rem; padding:8px 15px;}
  .build-nav__search{font-size:1rem; padding:9px 12px; width:220px;}
  .sec-select{font-size:.92rem; padding:8px 16px; min-height:38px; font-weight:600;}
  .sec-count{font-size:.88rem;}
  .thumb-card__label{font-size:.82rem; padding:3px 9px;}
  /* every slide says in words whether it is in the deck (instead of a small eye / + that shows on hover) */
  .thumb-card__toggle{width:auto; height:auto; padding:6px 13px; border-radius:999px; font-size:0 !important; opacity:1 !important; transform:none !important; top:8px; right:8px; background:#fff; border:1px solid rgba(17,17,17,.15);}
  .thumb-card__toggle::after{font-size:.85rem; font-weight:700; line-height:1.2; font-family:var(--font-ui);}
  .thumb-card:not(.excluded) .thumb-card__toggle{background:#15803d; border-color:#15803d;}
  .thumb-card:not(.excluded) .thumb-card__toggle::after{content:"\\2713  In your deck"; color:#fff;}
  .thumb-card.excluded .thumb-card__toggle{background:#fff; border-color:#9ca3af;}
  .thumb-card.excluded .thumb-card__toggle::after{content:"+  Add to deck"; color:#111827;}
  .thumb-card.excluded{opacity:.62;}
  .thumb-card__order{width:22px; height:22px; font-size:.7rem;}

  /* edit slides */
  .ws-tip{font-size:1rem; gap:10px 26px; padding:12px 18px; background:var(--surface); border:1px solid var(--line); border-radius:12px; color:#374151; margin-bottom:16px;}
  .ws-tip b{color:#111827;}
  .ws-zoom-ctrl__btn{height:38px; min-width:38px; padding:0 14px; font-size:.92rem; font-weight:600; border-radius:10px;}
  .ws-zoom-ctrl__label{font-size:.9rem; width:52px;}
  .ws-undo .ws-zoom-ctrl__btn{font-size:.95rem; padding:0 14px;}
  .ws-preview-fab{font-size:1.05rem; padding:15px 24px; font-weight:600;}
  #wsRight{font-size:1rem;}
  #wsRight .ws-panel-head h4{font-size:1.15rem;}
  #wsRight .ws-section h5{font-size:.9rem; letter-spacing:.04em;}
  #wsRight .ws-empty-note{font-size:.98rem; line-height:1.5;}
  #wsRight .ws-section__note{font-size:.8rem;}
  #wsRight .ws-check, #wsRight .ws-slot__name, #wsRight .ws-slot-count{font-size:.95rem;}
  #wsRight .btn{font-size:.95rem;}
  .ws-section.is-collapsible > h5{cursor:pointer; display:flex; align-items:center; gap:8px; user-select:none;}
  .ws-section.is-collapsible > h5::after{content:"\\25BE"; margin-left:auto; font-size:1rem; color:#6b7280; transition:transform .15s;}
  .ws-section.is-collapsible.is-collapsed > h5::after{transform:rotate(-90deg);}
  .ws-section.is-collapsible.is-collapsed > :not(h5){display:none !important;}

  /* help */
  .help-banner{display:flex; align-items:center; gap:16px; flex-wrap:wrap; max-width:960px; margin:0 0 22px; padding:14px 18px; border-radius:12px; background:#eff6ff; border:1px solid #bfdbfe; color:#1e3a8a; font-size:1rem;}
  .help-banner b{font-weight:700;} .help-banner .btn{background:#fff;}
  .help-banner__x{margin-left:auto; appearance:none; border:0; background:transparent; color:#1e3a8a; font:inherit; font-size:.92rem; cursor:pointer; text-decoration:underline;}
  .help-modal{position:fixed; inset:0; z-index:950; background:rgba(17,24,39,.6); display:none; align-items:center; justify-content:center; padding:20px;}
  .help-modal.is-open{display:flex;}
  .help-box{background:#fff; border-radius:16px; width:min(720px,100%); max-height:100%; overflow:auto; padding:28px 32px 24px; box-shadow:0 24px 60px rgba(0,0,0,.4);}
  .help-box h3{font-size:1.5rem; margin:0 0 4px;} .help-box .sub{color:var(--muted); font-size:1rem; margin:0 0 20px;}
  .help-step{display:flex; gap:16px; padding:14px 0; border-top:1px solid var(--line);}
  .help-step__n{flex:none; width:36px; height:36px; border-radius:50%; background:#111827; color:#fff; font-weight:700; display:flex; align-items:center; justify-content:center;}
  .help-step h4{font-size:1.1rem; margin:0 0 4px;} .help-step p{margin:0; color:#374151; font-size:1rem; line-height:1.5;}
  .help-tips{margin:14px 0 0; padding:14px 16px; background:var(--surface-sunken); border-radius:12px; font-size:.98rem; color:#374151; line-height:1.6;}
  .help-box__foot{display:flex; justify-content:flex-end; margin-top:18px;}

@media (max-width:900px){
  body .shell{padding:16px 16px 56px;}
  body .app-header{width:auto; padding:10px 12px 8px;}
  body .nav-item--help{margin-top:0; margin-left:auto;}
  .dash-toolbar .search{width:100%;}
}
</style>
"""
marker = '<style id="preque-look">'
i = s.index(marker)
j = s.index("</style>", i) + len("</style>")
s = s[:j] + "\n" + CSS.strip("\n") + s[j:]
sw_old = '<script src="/home.js"></script>'
assert s.count(sw_old) == 1
s = s.replace(sw_old, sw_old + '\n<script src="/easy-ui.js"></script>')
open(p, "w", encoding="utf-8").write(s)

# deck card: a word instead of the three dots
edit("public/deck-store.js", [
    ('aria-label="More actions">&#8942;</button>', 'aria-label="More actions">More &#9662;</button>'),
])
print("ok")
