# -*- coding: utf-8 -*-
"""New landing page ("Create a deck": ready-made deck / make your own) + a "Ready-made decks" screen.
The old landing page (all decks) becomes "My decks" in the sidebar."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "src", "frontend", "app.html")
s = open(p, encoding="utf-8").read()


def sw(o, n):
    global s
    assert s.count(o) == 1, (s.count(o), o[:100])
    s = s.replace(o, n)


# ---- screens
ICON_TPL = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect width="18" height="7" x="3" y="3" rx="1"/><rect width="9" height="7" x="3" y="14" rx="1"/><rect width="5" height="7" x="16" y="14" rx="1"/></svg>'
ICON_OWN = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>'
ICON_HOME = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>'

SCREENS = """  <!-- ============ HOME (landing) ============ -->
  <section class="screen is-active" data-screen="home">
    <div class="screen-head">
      <div><h2>Create a deck</h2><div class="screen-head__sub">How would you like to start?</div></div>
    </div>
    <div class="home-grid">
      <button type="button" class="home-card" data-goto="templates">
        <span class="home-card__icon">%s</span>
        <span class="home-card__title">Use a ready-made deck</span>
        <span class="home-card__text">Start from one of our finished decks and change only what you need.</span>
        <span class="home-card__cta">See ready-made decks &rarr;</span>
      </button>
      <button type="button" class="home-card" data-goto="build" data-newdeck="1" data-start="own">
        <span class="home-card__icon">%s</span>
        <span class="home-card__title">Make your own deck</span>
        <span class="home-card__text">Pick the slides you want from our library and build a new deck from scratch.</span>
        <span class="home-card__cta">Start from scratch &rarr;</span>
      </button>
    </div>
    <div class="home-foot"><button type="button" class="link-btn" data-goto="dashboard">Open one of my decks <span id="homeDeckCount"></span>&rarr;</button></div>
  </section>

  <!-- ============ READY-MADE DECKS ============ -->
  <section class="screen" data-screen="templates">
    <div class="screen-head">
      <div>
        <button class="back-link" data-goto="home">&lsaquo; Home</button>
        <h2>Ready-made decks</h2>
        <div class="screen-head__sub">Pick a finished deck to start from. You can still leave slides out and change anything.</div>
      </div>
    </div>
    <div class="dash-grid tpl-grid" id="tplGrid"></div>
    <div id="tplTeam" hidden>
      <div class="tpl-sub">Decks your team has already made <span>Click one to start from a copy of it.</span></div>
      <div class="dash-grid" id="tplTeamGrid"></div>
    </div>
  </section>

""" % (ICON_TPL, ICON_OWN)

sw("  <!-- ============ DASHBOARD ============ -->\n  <section class=\"screen is-active\" data-screen=\"dashboard\">",
   SCREENS + "  <!-- ============ DASHBOARD (my decks) ============ -->\n  <section class=\"screen\" data-screen=\"dashboard\">")
sw('<div><h2>Decks</h2><div class="screen-head__sub" id="dashSub">',
   '<div><button class="back-link" data-goto="home">&lsaquo; Home</button><h2>My decks</h2><div class="screen-head__sub" id="dashSub">')
sw('<button class="btn btn--accent btn--lg" data-goto="build" data-newdeck="1">+ New deck</button>',
   '<button class="btn btn--accent btn--lg" data-goto="home">+ New deck</button>')

# ---- sidebar
sw('<button type="button" class="app-header__brand" data-goto="dashboard" title="Back to your decks">',
   '<button type="button" class="app-header__brand" data-goto="home" title="Back to the start page">')
a = s.index('      <button class="link-btn nav-item" data-goto="dashboard" title="Decks">')
b = s.index("</button>", a) + len("</button>")
dash_btn = s[a:b]
assert "<span>Decks</span>" in dash_btn
home_btn = '      <button class="link-btn nav-item" data-goto="home" title="Home">%s<span>Home</span></button>\n' % ICON_HOME
new_dash = dash_btn.replace('title="Decks"', 'title="My decks"').replace("<span>Decks</span>", "<span>My decks</span>")
s = s[:a] + home_btn + new_dash + s[b:]

# ---- which sidebar item is lit
sw("""  body:not([data-screen]) .nav-item[data-goto="dashboard"],
  body[data-screen="dashboard"] .nav-item[data-goto="dashboard"],
  body[data-screen="build"] .nav-item[data-goto="dashboard"],
  body[data-screen="workspace"] .nav-item[data-goto="dashboard"],""",
   """  body:not([data-screen]) .nav-item[data-goto="home"],
  body[data-screen="home"] .nav-item[data-goto="home"],
  body[data-screen="templates"] .nav-item[data-goto="home"],
  body[data-screen="build"] .nav-item[data-goto="home"],
  body[data-screen="dashboard"] .nav-item[data-goto="dashboard"],
  body[data-screen="workspace"] .nav-item[data-goto="dashboard"],""")

# ---- navigation bookkeeping
sw("    dashboard: 'Decks', build: 'Choose slides', workspace: 'Edit slides',\n    finalize: 'Share', share: 'Share', history: 'Decks', roadmap: 'Decks'",
   "    home: 'Home', templates: 'Ready-made decks', dashboard: 'My decks', build: 'Choose slides', workspace: 'Edit slides',\n    finalize: 'Share', share: 'Share', history: 'My decks', roadmap: 'My decks'")
sw("  var navStack = ['dashboard'];", "  var navStack = ['home'];")
sw("var prev = navStack.length > 1 ? navStack[navStack.length - 2] : 'dashboard';", "var prev = navStack.length > 1 ? navStack[navStack.length - 2] : 'home';")
sw('''    applyRoleUI();
    activateScreen("dashboard");
    applyDashboardFilter();''', '''    applyRoleUI();
    activateScreen("home");
    applyDashboardFilter();''')

sw('<script src="/picker-tools.js"></script>', '<script src="/picker-tools.js"></script>\n<script src="/home.js"></script>')
open(p, "w", encoding="utf-8").write(s)
print("ok")
