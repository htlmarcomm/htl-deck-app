# -*- coding: utf-8 -*-
"""Restyles the app chrome (everything except the slides) to look like the HTL PreQue app:
light #f8f9fc page, white rounded cards with a hairline border, Inter, a white left sidebar
with icon navigation (red-50 / red-700 active state), dark primary buttons that turn red on
hover, red-50 secondary hovers, soft badges. The slides keep their own palette and font."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "src", "frontend", "app.html")
s = open(p, encoding="utf-8").read()


def sw(o, n):
    global s
    assert s.count(o) == 1, (s.count(o), o[:100])
    s = s.replace(o, n)


# ---------------------------------------------------------------- 1. tokens (light only, like PreQue)
a = s.index("  :root{\n    --ink:#14140f;")
b = s.index("\n  *{box-sizing:border-box;}")
s = s[:a] + """  :root{
    --ink:#111827;
    --paper:#f8f9fc;
    --surface:#ffffff;
    --surface-sunken:#f3f4f6;
    --line:#eceef3;
    --line-strong:#e5e7eb;
    --accent:#dc2626;
    --accent-soft:#f87171;
    --accent-wash:#fef2f2;
    --muted:#6b7280;
    --success:#15803d;
    --success-wash:#f0fdf4;
    --draft:#b45309;
    --draft-wash:#fffbeb;
    --shadow:0 1px 2px 0 rgba(0,0,0,0.05);
    --radius:8px;
    --radius-lg:12px;
    --font-ui: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    --font-mono: "JetBrains Mono", ui-monospace, "SF Mono", "Cascadia Code", Consolas, monospace;
    --font-slide: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }""" + s[b:]

# ---------------------------------------------------------------- 2. fonts
sw("<title>HTL Deck Platform</title>\n<style>",
   '<title>HTL Deck Platform</title>\n<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
   '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">\n<style>')

# ---------------------------------------------------------------- 3. header -> sidebar
ICON = '<svg viewBox="0 0 24 24" aria-hidden="true">%s</svg>'
I_DECKS = ICON % '<path d="M2 3h20"/><path d="M21 3v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V3"/><path d="m7 21 5-5 5 5"/>'
I_PROJ = ICON % '<path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/><rect width="20" height="14" x="2" y="6" rx="2"/>'
I_MASTER = ICON % '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>'
I_USERS = ICON % '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>'
I_OUT = ICON % '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/>'

sw("""  <div class="app-header" id="appHeader">
    <button type="button" class="app-header__brand" data-goto="dashboard" title="Back to your decks">HTL <span>Deck Platform</span></button>
    <div class="app-header__user" id="appHeaderUser" hidden>
      <span class="app-header__user-info" id="appHeaderUserInfo"></span>
      <button class="link-btn" data-goto="dashboard">Decks</button>
      <button class="link-btn" data-goto="projects">Projects</button>
      <button class="link-btn" data-goto="manage-decks" id="manageDecksLink" hidden>Master decks</button>
      <button class="link-btn" data-goto="users" id="usersLink" hidden>Users</button>
      <button class="link-btn" id="logoutBtn">Sign out</button>
    </div>
  </div>""", """  <aside class="app-header" id="appHeader">
    <button type="button" class="app-header__brand" data-goto="dashboard" title="Back to your decks">HTL <span>Deck Platform</span></button>
    <div class="app-header__user" id="appHeaderUser" hidden>
      <button class="link-btn nav-item" data-goto="dashboard" title="Decks">%s<span>Decks</span></button>
      <button class="link-btn nav-item" data-goto="projects" title="Projects">%s<span>Projects</span></button>
      <button class="link-btn nav-item" data-goto="manage-decks" id="manageDecksLink" title="Master decks" hidden>%s<span>Master decks</span></button>
      <button class="link-btn nav-item" data-goto="users" id="usersLink" title="Users" hidden>%s<span>Users</span></button>
      <span class="app-header__user-info" id="appHeaderUserInfo"></span>
      <button class="link-btn nav-item nav-item--out" id="logoutBtn" title="Sign out">%s<span>Sign out</span></button>
    </div>
  </aside>""" % (I_DECKS, I_PROJ, I_MASTER, I_USERS, I_OUT))

# login card copy (matches PreQue: app name + "Sign in to continue")
sw('<h2>Sign in</h2>\n        <p class="sub">Sign in to continue.</p>', '<h2>HTL Deck Platform</h2>\n        <p class="sub">Sign in to continue</p>')

# ---------------------------------------------------------------- 4. screen name on <body> (sidebar highlight / compact mode)
sw("""    screens.forEach(function(s){ s.classList.toggle('is-active', s.getAttribute('data-screen')===name); });
    if(!isBack && navStack""", """    screens.forEach(function(s){ s.classList.toggle('is-active', s.getAttribute('data-screen')===name); });
    document.body.setAttribute('data-screen', name);
    if(!isBack && navStack""")

# ---------------------------------------------------------------- 5. the look
SCREENS_DECKS = ["dashboard", "build", "workspace", "finalize", "share", "history"]
act = ",\n".join(['  body:not([data-screen]) .nav-item[data-goto="dashboard"]'] +
                 ['  body[data-screen="%s"] .nav-item[data-goto="dashboard"]' % n for n in SCREENS_DECKS] +
                 ['  body[data-screen="projects"] .nav-item[data-goto="projects"]',
                  '  body[data-screen="manage-decks"] .nav-item[data-goto="manage-decks"]',
                  '  body[data-screen="users"] .nav-item[data-goto="users"]'])
def compact_rule(sels, body):
    screens = ["build", "workspace", "finalize", "share"]
    return ",\n".join('  body[data-screen="%s"] %s' % (n, sel) for n in screens for sel in sels) + "{" + body + "}\n"


CSS = """
  /* ================= PreQue look =================
     Light page, white rounded cards, left sidebar with icons, dark primary buttons that turn
     red on hover. The slides keep their own palette and font (--font-slide). ================= */
  .real-scope, .ws-slide, .cs-slide-canvas, .share-slide{
    --ink:#14140f; --paper:#f4f3ef; --surface:#ffffff; --surface-sunken:#eae8e1;
    --line:rgba(20,19,15,0.12); --line-strong:rgba(20,19,15,0.22);
    --accent:#e5222a; --accent-soft:#ff6b70; --accent-wash:rgba(229,34,42,0.08); --muted:#6b6a63;
    --shadow:0 1px 2px rgba(20,19,15,0.06), 0 8px 24px -12px rgba(20,19,15,0.18);
    --font-ui:var(--font-slide);
  }
  .real-scope, .cs-slide-canvas, .share-slide{font-family:var(--font-slide);}

  body .shell{max-width:none; margin:0; padding:32px 32px 64px 256px;}
  body .app-header{position:fixed; top:0; left:0; bottom:0; width:224px; margin:0; padding:24px 12px 16px; background:var(--surface);
    border-right:1px solid var(--line); border-bottom:0; display:flex; flex-direction:column; align-items:stretch; justify-content:flex-start; gap:0; z-index:40; overflow-y:auto;}
  body .app-header__brand{padding:0 12px; margin:0 0 28px; font-size:1.25rem; font-weight:700; color:#1f2937; text-align:left; letter-spacing:-0.01em; line-height:2.5rem;}
  body .app-header__brand span{color:inherit;}
  body .app-header__user{display:flex; flex-direction:column; align-items:stretch; gap:4px; margin:0; flex:1; min-height:0;}
  body .app-header__user[hidden]{display:none;}
  body .nav-item{display:flex; align-items:center; gap:12px; width:100%; padding:8px 12px; border-radius:8px; font-size:0.875rem; font-weight:500; color:var(--muted); text-align:left; transition:background .15s ease, color .15s ease;}
  body .nav-item[hidden]{display:none;}
  body .nav-item svg{width:17px; height:17px; flex:none; fill:none; stroke:currentColor; stroke-width:2; stroke-linecap:round; stroke-linejoin:round;}
  body .nav-item:hover{background:var(--accent-wash); color:#b91c1c;}
__ACTIVE__{background:var(--accent-wash); color:#b91c1c;}
  body .app-header__user-info{order:90; margin-top:auto; padding:16px 12px 6px; border-top:1px solid var(--line); font-size:0.75rem; color:var(--muted); line-height:1.4;}
  body .app-header__user-info strong{color:#1f2937; font-weight:600;}
  body .nav-item--out{order:91; padding:6px 12px; font-size:0.75rem; color:#9ca3af;}
  body .nav-item--out svg{width:13px; height:13px;}
  body .nav-item--out:hover{background:transparent; color:#dc2626;}
  /* the editing steps give the slides the room: sidebar shrinks to icons */
@media (min-width:901px){
__COMPACT_SHELL__
__COMPACT_HEADER__
__COMPACT_BRAND__
__COMPACT_LABELS__
__COMPACT_ITEM__
}
  .shell:has(#appHeaderUser[hidden]){padding-left:32px;}
  .shell:has(#appHeaderUser[hidden]) .app-header{display:none;}

  .screen-head{margin-bottom:28px;}
  .screen-head h2{font-size:1.5rem; font-weight:600; letter-spacing:-0.01em; margin-top:0; color:var(--ink);}
  .screen-head__sub{font-size:0.875rem; max-width:none; margin-top:4px; color:var(--muted);}
  .back-link{font-weight:500; margin-bottom:6px; display:inline-block;}

  .btn{border-radius:8px; font-weight:500; font-size:0.875rem; padding:8px 16px; color:#374151; border-color:var(--line-strong); background:var(--surface); transition:background .15s ease, color .15s ease, border-color .15s ease;}
  .btn:hover:not(:disabled){background:var(--accent-wash); color:#b91c1c; border-color:#fecaca;}
  .btn--sm{padding:5px 10px; font-size:0.78rem;}
  .btn--lg{padding:9px 18px; font-size:0.875rem; border-radius:8px;}
  .btn--accent{background:#111827; border-color:#111827; color:#fff;}
  .btn--accent:hover:not(:disabled){background:var(--accent); border-color:var(--accent); color:#fff;}
  .btn--ghost{background:transparent; border-color:transparent; color:var(--muted);}
  .btn--ghost:hover:not(:disabled){background:var(--accent-wash); color:#b91c1c; border-color:transparent;}
  .btn:focus-visible, .nav-item:focus-visible{outline:0; box-shadow:0 0 0 2px #fff, 0 0 0 4px #ef4444;}

  .field-inline label, .login-field label{font-size:0.75rem; font-weight:500; text-transform:none; letter-spacing:0; color:#4b5563;}
  .field-inline select, .field-inline input, .search, .ws-search, .login-field input, .pdb-form .field-inline input, .pdb-form .field-inline select, .pdb-form .field-inline textarea{
    border:1px solid var(--line-strong); border-radius:8px; background:#fff; font-size:0.875rem; padding:8px 12px; color:var(--ink);}
  .field-inline select:focus, .field-inline input:focus, .search:focus, .ws-search:focus, .login-field input:focus, .pdb-form .field-inline input:focus, .pdb-form .field-inline select:focus, .pdb-form .field-inline textarea:focus{
    outline:0; border-color:transparent; box-shadow:0 0 0 2px #ef4444;}
  .dash-toolbar .search{width:288px;}

  .pill{font-weight:500; padding:2px 9px; font-size:0.75rem;}
  .pill::before{display:none;}
  .tag{border-radius:999px; font-weight:600; padding:2px 8px;}

  .deck-card{border-color:var(--line); border-radius:12px; box-shadow:var(--shadow);}
  .deck-card:hover{transform:none; box-shadow:0 4px 12px -2px rgba(0,0,0,.10);}
  .deck-card__name{font-weight:600; font-size:0.875rem; color:var(--ink);}
  .deck-card__meta{font-size:0.75rem; color:#9ca3af;}
  .deck-card__menu{border-radius:10px;}
  .empty-state{background:var(--surface); border:1px solid var(--line); border-radius:12px; box-shadow:var(--shadow); padding:64px 20px;}

  .steps__item{font-weight:500; background:var(--surface-sunken); color:var(--muted);}
  .steps__item.is-now{background:var(--accent-wash); color:#b91c1c;}
  .thumb-card{border-radius:12px; background:#fff; box-shadow:var(--shadow);}
  .section-group__title{font-weight:600; letter-spacing:0.08em; color:#6b7280;}

  .ws-left{background:#eceef3; border-radius:12px;}
  .pdb-table-wrap{border-radius:12px; box-shadow:var(--shadow);}
  .pdb-table th{background:#f9fafb; color:#6b7280;}
  .pdb-modal__inner{background:#fff; border-radius:12px;}

  .login-shell{min-height:calc(100vh - 64px);}
  .login-card{width:384px; max-width:100%; padding:32px; border-radius:12px; border-color:var(--line-strong); box-shadow:var(--shadow);}
  .login-card h2{font-size:1.25rem; font-weight:700; margin-bottom:4px;}
  .login-card p.sub{margin-bottom:24px;}
  .login-field input{background:#fff;}
  .login-error{background:#fef2f2; border:1px solid #fee2e2; color:#b91c1c; border-radius:8px; padding:8px 12px;}

  /* the public share view: same light chrome */
  .dr-head{background:#fff !important; color:#111827 !important; border-bottom:1px solid var(--line-strong);}
  .dr-head h1 span{color:#6b7280 !important;}
  .dr-head__present{background:#111827 !important; color:#fff !important;}
  #deckReview{background:#eceef3 !important;}
  html.dr-presenting #deckReview{background:#000 !important;}

@media (max-width:900px){
  body .shell{padding:16px 16px 48px;}
  body .app-header{position:sticky; top:0; bottom:auto; width:auto; height:auto; flex-direction:row; flex-wrap:wrap; align-items:center; gap:4px 14px; padding:10px 16px; border-right:0; border-bottom:1px solid var(--line); margin:-16px -16px 18px; overflow:visible;}
  body .app-header__brand{margin:0; font-size:1.05rem; line-height:1.6;}
  body .app-header__user{flex-direction:row; flex-wrap:wrap; align-items:center; gap:2px; flex:1;}
  body .nav-item{width:auto; padding:6px 10px;}
  body .app-header__user-info{order:0; margin:0 0 0 auto; padding:0; border:0;}
  body .nav-item--out{order:1;}
  .shell:has(#appHeaderUser[hidden]){padding:16px;}
  .dash-toolbar .search{width:100%;}
}
"""
CSS = CSS.replace("__ACTIVE__", act)
CSS = CSS.replace("__COMPACT_SHELL__", compact_rule([".shell"], "padding-left:96px;"))
CSS = CSS.replace("__COMPACT_HEADER__", compact_rule([".app-header"], "width:64px; padding:20px 8px;"))
CSS = CSS.replace("__COMPACT_BRAND__", compact_rule([".app-header__brand"], "padding:0; text-align:center; font-size:1rem; margin-bottom:20px;"))
CSS = CSS.replace("__COMPACT_LABELS__", compact_rule([".app-header__brand span", ".nav-item span", ".app-header__user-info"], "display:none;"))
CSS = CSS.replace("__COMPACT_ITEM__", compact_rule([".nav-item"], "justify-content:center; padding:10px 0;"))

end = s.index("</style>", s.index("<title>HTL Deck Platform</title>"))
s = s[:end] + CSS + s[end:]

open(p, "w", encoding="utf-8").write(s)
print("ok")
