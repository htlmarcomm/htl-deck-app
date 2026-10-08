# -*- coding: utf-8 -*-
"""Plain-language pass over the app's static wording and layout: no prototype
leftovers, one short instruction per screen, a clear 3-step flow
(Choose slides -> Edit slides -> Share). Edits src/frontend/app.html (kept for
provenance); the dynamic wording lives in public/deck-store.js."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "src", "frontend", "app.html")
s = open(p, encoding="utf-8").read()
EM = "—"


def sw(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:90])
    s = s.replace(old, new)


def rx(pattern, new, flags=re.S):
    global s
    m = re.search(pattern, s, flags)
    assert m, pattern[:90]
    s = s[: m.start()] + new + s[m.end():]


# ---------------------------------------------------------------- page / header
sw("<title>Deck Platform MVP</title>", "<title>HTL Deck Platform</title>")
sw('<div class="app-header__brand">Deck Platform <span>/ MVP</span></div>',
   '<button type="button" class="app-header__brand" data-goto="dashboard" title="Back to your decks">HTL <span>Deck Platform</span></button>')
sw('<button class="link-btn" data-goto="projects">Project database</button>',
   '<button class="link-btn" data-goto="dashboard">Decks</button>\n      <button class="link-btn" data-goto="projects">Projects</button>')
sw('id="manageDecksLink" hidden>Manage master decks</button>', 'id="manageDecksLink" hidden>Master decks</button>')
sw('      <button class="link-btn" data-goto="roadmap">Build order ↗</button>\n', "")
sw('<button class="link-btn" id="logoutBtn">Log out</button>', '<button class="link-btn" id="logoutBtn">Sign out</button>')
sw('userInfo.innerHTML = "Signed in as <strong>" + currentUser.name + "</strong> \\u00b7 " + currentUser.role;',
   'userInfo.innerHTML = "<strong>" + currentUser.name + "</strong> \\u00b7 " + (currentUser.role === "creator" ? "Creator" : "User");')

# the prototype's roadmap screen goes away
rx(r'\s*<!-- =+ ROADMAP =+ -->\s*<section class="screen" data-screen="roadmap">.*?</section>', "\n")

# the sign-in screen is no longer shown (the server handles it): start on the deck list
sw('<section class="screen is-active" data-screen="login">', '<section class="screen" data-screen="login">')
sw('<section class="screen" data-screen="dashboard">', '<section class="screen is-active" data-screen="dashboard">')
sw('<p class="sub">Creator and User accounts see different things — Users only see their own decks.</p>', '<p class="sub">Sign in to continue.</p>')

# ---------------------------------------------------------------- dashboard
sw('<div class="screen-head__sub">Every deck the team has built. Flat list, no folders — this is a single-tenant tool.</div>',
   '<div class="screen-head__sub" id="dashSub">Your decks. Click one to keep editing it.</div>')
sw('data-goto="build" data-newdeck="1">+ New Deck</button>', 'data-goto="build" data-newdeck="1">+ New deck</button>')
sw('placeholder="Search decks or clients"', 'placeholder="Search by deck or client name"')
sw('id="dashArchiveToggle">Show archived</button>', 'id="dashArchiveToggle">Show archived decks</button>')
sw("showing ? 'Hide archived' : 'Show archived'", "showing ? 'Hide archived decks' : 'Show archived decks'")
sw('<strong>No decks match</strong><span>Try a different search, or check "Show archived".</span>',
   '<strong>No decks to show</strong><span>Try a different search, or choose “Show archived decks”.</span>')

# ---------------------------------------------------------------- 3-step strip
STEPS = ('<div class="steps" aria-label="Progress">'
         '<span class="steps__item%s">1 &middot; Choose slides</span><i></i>'
         '<span class="steps__item%s">2 &middot; Edit slides</span><i></i>'
         '<span class="steps__item%s">3 &middot; Share</span></div>')


def steps(a, b, c):
    return STEPS % (a, b, c)


sw('<section class="screen" data-screen="build" id="buildScreen">\n',
   '<section class="screen" data-screen="build" id="buildScreen">\n    ' + steps(" is-now", "", "") + "\n")
sw('<section class="screen" data-screen="workspace">\n', '<section class="screen" data-screen="workspace">\n    ' + steps(" is-done", " is-now", "") + "\n")
sw('<section class="screen" data-screen="finalize">\n', '<section class="screen" data-screen="finalize">\n    ' + steps(" is-done", " is-done", " is-now") + "\n")
sw('<section class="screen" data-screen="share">\n', '<section class="screen" data-screen="share">\n    ' + steps(" is-done", " is-done", " is-done") + "\n")

# ---------------------------------------------------------------- Choose slides
sw('<div class="field-inline"><label>Recipient</label><input id="buildClient" list="buildClientList" placeholder="Client / recipient" autocomplete="off" />',
   '<div class="field-inline"><label>Client</label><input id="buildClient" list="buildClientList" placeholder="Who is it for?" autocomplete="off" />')
sw('<div class="field-inline"><label>Deck name</label><input id="buildDeckName" placeholder="Deck name" autocomplete="off" /></div>',
   '<div class="field-inline"><label>Deck name <b style="color:var(--accent)">*</b></label><input id="buildDeckName" placeholder="e.g. Q3 pitch for Acme" autocomplete="off" /></div>')
sw('data-goto="workspace" id="buildNextBtn">Next →</button>',
   'data-goto="workspace" id="buildNextBtn">Next: edit slides →</button>')
rx(r'<div class="deck-hint">.*?</div>',
   '<div class="deck-hint" id="buildHint">All slides are included. <b>Click a slide to leave it out</b> &mdash; click it again to put it back. <span id="buildCount"></span></div>')
sw('<span class="tag tag--muted">New</span>', "", 1)

# ---------------------------------------------------------------- Edit slides (workspace)
sw('data-goto="finalize">Finalize</button>', 'data-goto="finalize">Finalize &amp; share</button>')
sw('<div class="ws-shell">\n      <div class="ws-left" id="wsLeft"></div>',
   '<div class="ws-tip"><span><b>Text:</b> click it to edit</span><span><b>Photos:</b> hover, then &ldquo;Change photo&rdquo;</span>'
   '<span><b>Order:</b> drag the &#10303; handle</span><span><b>New slide:</b> click + between slides</span></div>\n'
   '    <div class="ws-shell">\n      <div class="ws-left" id="wsLeft"></div>')
sw("dashboard: 'Decks', build: 'Choose slides', workspace: 'Workspace',\n    finalize: 'Finalize',", "dashboard: 'Decks', build: 'Choose slides', workspace: 'Edit slides',\n    finalize: 'Share',")
sw('<button class="back-link" data-goto="build">‹ Choose slides</button>', '<button class="back-link" data-goto="build">‹ Choose slides</button>')
sw('<button class="back-link" data-goto="workspace">‹ Workspace</button>\n        <h2>Finalize this deck</h2>',
   '<button class="back-link" data-goto="workspace">‹ Edit slides</button>\n        <h2>Share this deck</h2>')

# right-hand panel wording
sw("""'<div class="ws-panel-head"><h4>' + slide.label + '</h4><span class="tag">dynamic</span></div>' +
        '<div class="ws-section"><h5>Project selection <span class="ws-section__note">from project database — wired up in Phase 1</span></h5>' +""",
   """'<div class="ws-panel-head"><h4>' + slide.label + '</h4></div>' +
        '<div class="ws-section"><h5>Projects on this slide <span class="ws-section__note">tick the ones to show</span></h5>' +""")
sw("' of ' + SLOT_MAX + ' project blocks' +", "' of ' + SLOT_MAX + ' projects shown' +")
sw("'<div class=\"ws-section\"><h5>Upload images <span class=\"ws-section__note\">one per selected project</span></h5>'",
   "'<div class=\"ws-section\"><h5>Photos <span class=\"ws-section__note\">one per project</span></h5>'")
sw("""'<div class="ws-panel-head"><h4>' + slide.label + '</h4><span class="tag">imagery</span></div>' +
        '<p class="ws-empty-note">These ' + slide.slots.length + ' categories are fixed template copy — only the photo behind each one changes per deck.</p>' +
        '<div class="ws-section"><h5>Assign images <span class="ws-section__note">from the asset library — wired up in Phase 1</span></h5>' + rows + '</div>' +""",
   """'<div class="ws-panel-head"><h4>' + slide.label + '</h4></div>' +
        '<p class="ws-empty-note">The ' + slide.slots.length + ' headings are fixed. Choose a photo for each one.</p>' +
        '<div class="ws-section"><h5>Photos</h5>' + rows + '</div>' +""")
rx(r"""'<div class="ws-panel-head"><h4>' \+ slide\.label \+ '</h4><span class="tag">custom</span></div>' \+\s*'<p class="ws-empty-note">.*?</p>';""",
   """'<div class="ws-panel-head"><h4>' + slide.label + '</h4></div>' +
        '<p class="ws-empty-note">A blank slide. Add a text box, image or graph with the buttons at the top-left of the slide. Drag the &#10303; handle to move it. Click text to edit it, and use the &#10005; to remove it.</p>';""")
rx(r"""'<div class="ws-panel-head"><h4>' \+ slide\.label \+ '</h4><span class="tag tag--muted">static</span></div>' \+\s*'<p class="ws-empty-note">.*?</p>';""",
   """'<div class="ws-panel-head"><h4>' + slide.label + '</h4></div>' +
        '<p class="ws-empty-note">Click any text on this slide to edit it. Hover over a photo to change it. To remove this slide, use the &#8943; button on the slide.</p>';""")
sw("""<h5>Image library</h5><div class="ws-asset-tray__empty">Nothing uploaded yet this session.</div>""",
   """<h5>Your uploaded photos</h5><div class="ws-asset-tray__empty">Photos you upload will appear here so you can reuse them.</div>""")
sw("""<h5>Image library <span class="ws-section__note">click to reuse on the last-picked slot</span></h5>""",
   """<h5>Your uploaded photos <span class="ws-section__note">click one to reuse it</span></h5>""")

# ---------------------------------------------------------------- Share
sw('<h2>Share link ready</h2>', '<h2>Your link is ready</h2>\n        <div class="screen-head__sub">Anyone with this link can view the deck &mdash; read-only, no login needed.</div>')
sw('<span>view-only · no login</span>', '<span>read-only</span>')
rx(r'\s*<button class="btn btn--sm" disabled>Download PDF.*?</button>', "")
sw('id="shareCopyLinkBtn" type="button" data-share-url="">Copy link</button>', 'id="shareCopyLinkBtn" type="button" data-share-url="" style="font-weight:700;">Copy link</button>')
sw('id="shareOpenLink" href="#" target="_blank" rel="noopener" style="text-decoration:none;">Open link</a>', 'id="shareOpenLink" href="#" target="_blank" rel="noopener" style="text-decoration:none;">Open in new tab</a>')

# ---------------------------------------------------------------- Users
sw('<div class="screen-head__sub">Create accounts for your team. Users build and share their own decks; Creators can also edit the project database and master decks.</div>',
   '<div class="screen-head__sub">Add the people who will use the app. <b>Users</b> build and share decks. <b>Creators</b> can also edit the project list and the master decks.</div>')
sw('<label>Password (min 10 characters)</label>', '<label>Password (at least 10 characters)</label>')

# ---------------------------------------------------------------- Projects
sw('<h2>Project database</h2>\n      <div class="screen-head__sub">Every HTL project in one register, merged from the sector register, the File Cabinet registry files and the consolidated master. Tick the ones you want to show on deck slides.</div>',
   '<h2>Projects</h2>\n      <div class="screen-head__sub">All HTL projects in one list. Search or filter, then tick the ones you want on your slides.</div>')
sw('id="pdbExport">Download picks (CSV)</button>', 'id="pdbExport">Download ticked projects</button>')
sw('id="pdbPickPage">Tick this page</button>', 'id="pdbPickPage">Tick all on this page</button>')
sw('id="pdbClearPicks">Clear picks</button>', 'id="pdbClearPicks">Untick all</button>')
sw('" picked for slides"', '" ticked"', 2)
sw('? "You are signed in as a Creator: use Edit on any row, or Add project, to change the shared register. Changes appear for everyone straight away."',
   '? "You can edit projects: use Edit on a row, or + Add project. Changes show for everyone straight away."')
sw(': "Read-only. Only Creator accounts can edit project details. You can still tick projects to use on your slides.";',
   ': "View only. Only Creators can edit projects. You can still tick projects to use on your slides.";')
sw('<strong>The project register is empty</strong>\n      <span>Load the 2,182 merged projects once. After that everyone sees them, and only Creators can change them.</span>',
   '<strong>The project list is empty</strong>\n      <span>Load the 2,182 HTL projects once. After that everyone can see them, and only Creators can change them.</span>')
sw('id="pdbSeedBtn" hidden>Load project register</button>', 'id="pdbSeedBtn" hidden>Load the projects</button>')

# ---------------------------------------------------------------- Master decks
sw('<h2>Manage master decks</h2>', '<h2>Master decks</h2>')
rx(r'<div class="screen-head__sub">Use <strong>Edit text</strong>.*?</div>',
   '<div class="screen-head__sub">Click <b>Edit text</b> to change the wording of a master deck. Only Creators can open this page.</div>')
s = s.replace(">Download HTML</button>", ">Download (advanced)</button>")
s = s.replace(">Upload updated HTML<input", ">Upload (advanced)<input")
s = re.sub(r'<p class="manage-card__note">Uploaded file must keep each slide.*?</p>',
           '<p class="manage-card__note">Advanced: download the deck as a file, edit it, then upload it back. Only upload a file you downloaded from here.</p>', s, flags=re.S)

# ---------------------------------------------------------------- styles
CSS = """
  /* ---- plain-language pass: step strip, one-line tips, clickable brand ---- */
  .app-header__brand{appearance:none; border:0; background:transparent; font-family:var(--font-ui); color:var(--ink); padding:0; cursor:pointer; font-size:1rem; font-weight:700; letter-spacing:-0.01em;}
  .app-header__brand span{color:var(--accent);}
  .steps{display:flex; align-items:center; gap:8px; margin:0 0 14px; font-size:0.72rem; font-weight:600; color:var(--muted); flex-wrap:wrap;}
  .steps i{width:18px; height:1px; background:var(--line-strong); display:block;}
  .steps__item{padding:4px 10px; border-radius:999px; background:var(--surface-sunken);}
  .steps__item.is-now{background:var(--accent); color:#fff;}
  .steps__item.is-done{background:var(--success-wash); color:var(--success);}
  .ws-tip{display:flex; gap:6px 18px; flex-wrap:wrap; font-size:0.74rem; color:var(--muted); margin:-6px 0 14px;}
  .ws-tip b{color:var(--ink); font-weight:600;}
  .deck-hint{display:block; font-size:0.84rem; color:var(--ink);}
  #buildCount{color:var(--muted); margin-left:6px;}
  #buildScreen .thumb-card.pending{display:none;}
  #wsDeckTitle::after{content:" \\270E"; font-size:.6em; opacity:.45; margin-left:6px;}
  #wsDeckTitle[contenteditable=true]::after{content:"";}
  .field-inline input.is-missing{border-color:var(--accent); box-shadow:0 0 0 3px var(--accent-wash);}
  .build-warn{color:var(--accent); font-size:0.78rem; font-weight:600; align-self:center;}
"""
sw("  .ws-card-remove{position:absolute; top:6px; right:6px;", CSS + "\n  .ws-card-remove{position:absolute; top:6px; right:6px;")

open(p, "w", encoding="utf-8").write(s)
print("ok")
