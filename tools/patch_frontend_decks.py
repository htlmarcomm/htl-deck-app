# -*- coding: utf-8 -*-
"""One-time edits to src/frontend/app.html that wire the prototype's static
dashboard / share / history screens to the real backend (deck-store.js does
the rest). Kept for provenance; app.html is the source of truth from here on."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "src", "frontend", "app.html")
s = open(P, encoding="utf-8").read()


def sw(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)


# 1. the public share page must not fill the whole slide library on load
sw("  function fillSnippets(root){\n", "  function fillSnippets(root){\n    if(!root && window.__HTL_SHARE_TOKEN__) return; // public viewer: only fill what it renders itself\n")

# 2. capability iframes: root-relative so they also work from /s/<token>
sw("src=\"capability-slides.html#slide=' + CAPABILITY_SCREENS[key]", "src=\"/capability-slides.html#slide=' + CAPABILITY_SCREENS[key]")

# 3. sample decks go; the dashboard is rendered from the database
a = s.index('<div class="dash-grid" id="dashGrid">') + len('<div class="dash-grid" id="dashGrid">')
b = s.index('<div class="empty-state" id="dashEmpty">')
s = s[:a] + "\n      " + s[b:]

# 4. Build screen: real recipient + deck-name fields
sw('<div class="field-inline"><label>Recipient</label><select><option>Brookfield Properties</option><option>Biocon Biologics</option><option>+ New client</option></select></div>',
   '<div class="field-inline"><label>Recipient</label><input id="buildClient" list="buildClientList" placeholder="Client / recipient" autocomplete="off" /><datalist id="buildClientList"></datalist></div>')
sw('<div class="field-inline"><label>Deck name</label><input value="Q3 Pitch — Data Centre Capex" /></div>',
   '<div class="field-inline"><label>Deck name</label><input id="buildDeckName" placeholder="Deck name" autocomplete="off" /></div>')

# 5. Workspace title is the deck name (renamed in place)
sw('<h2>Q3 Pitch — Data Centre Capex</h2>\n      </div>\n      <div class="screen-head__fields">\n        <div class="ws-zoom-ctrl"',
   '<h2 id="wsDeckTitle" title="Click to rename" style="cursor:text;">Untitled deck</h2>\n      </div>\n      <div class="screen-head__fields">\n        <div class="ws-zoom-ctrl"')

# 6. Share screen: filled from the finalized deck, with its real link
a = s.index('<div class="share-frame">')
b = s.index("<!-- ============ MANAGE MASTER DECKS")
s = s[:a] + '''<div class="share-frame">
      <div class="share-chrome"><span id="shareChromeUrl"></span><span>view-only · no login</span></div>
      <div class="share-deck-scroll" id="shareDeckScroll"></div>
      <div class="share-footer">
        <span>Shared by HTL Aircon</span>
        <div class="share-footer__actions">
          <a class="btn btn--sm" id="shareOpenLink" href="#" target="_blank" rel="noopener" style="text-decoration:none;">Open link</a>
          <button class="btn btn--sm" id="shareCopyLinkBtn" type="button" data-share-url="">Copy link</button>
          <button class="btn btn--sm" disabled>Download PDF <span style="font-family:var(--font-mono); font-size:0.6rem;">(post-MVP)</span></button>
        </div>
      </div>
    </div>
  </section>

  <!-- ============ USERS (Creator only) ============ -->
  <section class="screen" data-screen="users">
    <div class="screen-head">
      <div><button class="back-link" data-goto="dashboard">‹ Decks</button><h2>Users</h2>
      <div class="screen-head__sub">Create accounts for your team. Users build and share their own decks; Creators can also edit the project database and master decks.</div></div>
    </div>
    <div class="users-grid">
      <form class="manage-card" id="userForm" autocomplete="off">
        <h3>Add a user</h3>
        <div class="field-inline" style="margin-top:10px;"><label>Name</label><input id="userName" style="width:100%;" required /></div>
        <div class="field-inline" style="margin-top:10px;"><label>Username</label><input id="userUsername" style="width:100%;" required pattern="[A-Za-z0-9._-]{3,40}" title="3-40 letters, numbers, . _ -" /></div>
        <div class="field-inline" style="margin-top:10px;"><label>Password (min 10 characters)</label><input id="userPassword" type="text" style="width:100%;" minlength="10" required /></div>
        <div class="field-inline" style="margin-top:10px;"><label>Role</label><select id="userRole"><option value="user">User</option><option value="creator">Creator</option></select></div>
        <div class="manage-card__row"><button type="submit" class="btn btn--accent">Create account</button></div>
        <p class="manage-card__status" id="userStatus"></p>
      </form>
      <div class="manage-card"><h3>Accounts</h3><div id="userList" style="margin-top:10px;"></div></div>
    </div>
  </section>

  ''' + s[b:]

# 7. header link for the Users screen
sw('<button class="link-btn" data-goto="manage-decks" id="manageDecksLink" hidden>Manage master decks</button>',
   '<button class="link-btn" data-goto="manage-decks" id="manageDecksLink" hidden>Manage master decks</button>\n      <button class="link-btn" data-goto="users" id="usersLink" hidden>Users</button>')
sw("if(manageLink) manageLink.hidden = !currentUser || currentUser.role !== \"creator\";",
   "if(manageLink) manageLink.hidden = !currentUser || currentUser.role !== \"creator\";\n    var usersLink = document.getElementById(\"usersLink\");\n    if(usersLink) usersLink.hidden = !currentUser || currentUser.role !== \"creator\";")
sw("if(name === 'manage-decks' && !(", "if((name === 'manage-decks' || name === 'users') && !(")

# 8. photo swaps upload to the server (blob: URLs vanish on reload)
sw("""    var url = URL.createObjectURL(file);
    if(wsPhotoSwapTarget.tagName === "IMG"){
      wsPhotoSwapTarget.src = url;
    } else {
      wsPhotoSwapTarget.style.backgroundImage = "url(" + url + ")";
    }""", """    var url = URL.createObjectURL(file);
    var swapEl = wsPhotoSwapTarget;
    var setPhoto = function(u){
      if(swapEl.tagName === "IMG"){ swapEl.src = u; } else { swapEl.style.backgroundImage = "url(" + u + ")"; }
    };
    setPhoto(url);
    // show the picture at once, then replace it with the stored copy so it survives a reload
    if(window.uploadImage) window.uploadImage(file).then(function(stored){
      setPhoto(stored);
      var cs = swapEl.closest && swapEl.closest("[data-cs-section]");
      if(cs){
        var si = cs.closest(".ws-slide"), sl = si && WORKSPACE_SLIDES[+si.getAttribute("data-index")];
        var ed = sl && sl.elements && sl.elements.find(function(e){ return e.id === cs.getAttribute("data-cs-id"); });
        if(ed) ed.src = stored;
      }
      if(typeof markAutosaveDirty === "function") markAutosaveDirty();
    }).catch(function(err){ alert("The picture could not be saved: " + (err && err.message || "upload failed")); });""")
sw("""        var url = URL.createObjectURL(file);
        row.querySelector('.ws-slot__thumb').style.backgroundImage = 'url(' + url + ')';""",
   """        var url = URL.createObjectURL(file);
        row.querySelector('.ws-slot__thumb').style.backgroundImage = 'url(' + url + ')';
        if(window.uploadImage) window.uploadImage(file).then(function(stored){ row.querySelector('.ws-slot__thumb').style.backgroundImage = 'url(' + stored + ')'; }).catch(function(){});""")

# 9. load the deck store last
sw("</script>\n</body></html>\n</body></html>", "</script>\n<script src=\"/deck-store.js\"></script>\n</body></html>\n</body></html>")

open(P, "w", encoding="utf-8").write(s)
print("patched", len(s))
