# -*- coding: utf-8 -*-
"""Plain-language wording for the screens that deck-store.js draws (dashboard
cards, finalize, version history) plus the Choose-slides name check and slide
count. Edits public/deck-store.js (kept for provenance)."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "public", "deck-store.js")
s = open(p, encoding="utf-8").read()


def sw(o, n, cnt=1):
    global s
    assert s.count(o) == cnt, (s.count(o), o[:80])
    s = s.replace(o, n)


# --- dashboard cards
sw("""'<div class="deck-card__meta">' + (d.client_name ? "for " + esc(d.client_name) : "no recipient") + '</div>' +""",
   """'<div class="deck-card__meta">' + (d.client_name ? "For " + esc(d.client_name) : "No client set") + '</div>' +""")
sw("""'<span class="timestamp">' + (d.versions ? "v" + d.versions : "—") + ' &middot; ' + esc(ago(d.updated_at)) + '</span></div></div></button>' +""",
   """'<span class="timestamp">' + (d.versions ? "Version " + d.versions + " &middot; " : "") + 'edited ' + esc(ago(d.updated_at)) + '</span></div></div></button>' +""")
sw("""(live ? "shared" : "draft") + '</span>' +""", """(live ? "Shared" : "Draft") + '</span>' +""")
sw("""data-action="history">Version history</button>' +""", """data-action="history">Versions &amp; links</button>' +""")
sw("""data-action="open">Open</button>' +""", """data-action="open">Open &amp; edit</button>' +""")

# --- dashboard wording that follows the person, and a friendlier empty state
sw("""    fillSnippets(grid);
    applyDashboardFilter();
    refreshDashEmptyState();""", """    fillSnippets(grid);
    applyDashboardFilter();
    refreshDashEmptyState();
    var sub = $("dashSub");
    if (sub) sub.textContent = window.__HTL_USER__.role === "creator" ? "Everyone's decks. Click one to keep editing it." : "Your decks. Click one to keep editing it.";
    var em = $("dashEmpty");
    if (em && !DS.decks.length) {
      em.querySelector("strong").textContent = "No decks yet";
      em.querySelector("span").textContent = "Click \\u201c+ New deck\\u201d (top right) to make your first one.";
    }""")

# --- finalize / share wording
a = s.index("    modal.innerHTML = first")
b = s.index("    modal.querySelectorAll(\".option-card\")")
s = s[:a] + """    modal.innerHTML = first
      ? '<h3>Create the share link</h3><p class="sub">This saves the deck as it is now and gives you a link. Anyone with the link can view it (read-only, no login). You can keep editing afterwards.</p>' +
        '<div class="fin-error" id="finError" hidden></div>' +
        '<div class="modal-footer"><button class="btn btn--ghost" data-goto="workspace">Go back</button><button class="btn btn--accent" id="finalizeGo">Create link</button></div>'
      : '<h3>Share the updated deck</h3><p class="sub">This deck has already been shared. What should happen to the link?</p>' +
        '<div class="option-card selected" data-mode="keep"><div class="option-card__head"><span class="radio"></span>Make a new link</div><p>The old link keeps showing the old version. You get a second, new link for this version.</p></div>' +
        '<div class="option-card" data-mode="replace"><div class="option-card__head"><span class="radio"></span>Update the existing link</div><p>The link people already have will show this new version. Same address.</p></div>' +
        '<div class="fin-error" id="finError" hidden></div>' +
        '<div class="modal-footer"><button class="btn btn--ghost" data-goto="workspace">Go back</button><button class="btn btn--accent" id="finalizeGo">Share</button></div>';
""" + s[b:]
sw("""btn.disabled = true; btn.textContent = "Working…"; err.hidden = true;""", """btn.disabled = true; btn.textContent = "Please wait…"; err.hidden = true;""")
sw("""btn.disabled = false; btn.textContent = mode === "keep" && DS.versions ? "Finalize deck" : "Create & get link";""",
   """btn.disabled = false; btn.textContent = DS.versions ? "Share" : "Create link";""")

# --- version history wording
sw("""(deck.name || "Deck") + " — version history";""", """(deck.name || "Deck") + " — versions & links";""")
sw("""<strong>No versions yet</strong><span>This deck hasn’t been finalized — finalize it once to create v1 and a share link.</span>""",
   """<strong>Not shared yet</strong><span>Open the deck and choose “Finalize &amp; share” to create its first link.</span>""")
sw("""(l.revoked ? "revoked" : "live link") + '</span>' +""", """(l.revoked ? "Link off" : "Link on") + '</span>' +""")
sw("""(l.revoked ? "Turn back on" : "Revoke") + '</button></div>';""", """(l.revoked ? "Turn link on" : "Turn link off") + '</button></div>';""")
sw("""No link points at this version.""", """No link shows this version.""")
sw("""pill.textContent = off ? "revoked" : "live link";""", """pill.textContent = off ? "Link off" : "Link on";""")
sw("""b.textContent = off ? "Turn back on" : "Revoke";""", """b.textContent = off ? "Turn link on" : "Turn link off";""")

# --- Choose slides: a deck name is required; show how many slides are in
sw("""  var nextBtn = $("buildNextBtn");
  if (nextBtn) nextBtn.addEventListener("click", function () {""", """  function updateBuildCount() {
    var all = document.querySelectorAll("#buildScreen .thumb-card:not(.pending)");
    var on = document.querySelectorAll("#buildScreen .thumb-card:not(.pending):not(.excluded)").length;
    var el = $("buildCount");
    if (el) el.textContent = on + " of " + all.length + " slides included.";
  }
  document.addEventListener("click", function (e) {
    if (e.target.closest("#buildScreen .thumb-card")) setTimeout(updateBuildCount, 0);
    if (e.target.closest('[data-goto="build"]')) setTimeout(updateBuildCount, 50);
  });
  updateBuildCount();
  // a deck needs a name before moving on (checked before the screen changes)
  document.addEventListener("click", function (e) {
    if (!e.target.closest("#buildNextBtn")) return;
    var inp = $("buildDeckName");
    if (inp && !inp.value.trim()) {
      e.stopImmediatePropagation(); e.preventDefault();
      inp.classList.add("is-missing"); inp.focus();
      var w = $("buildWarn");
      if (!w) { w = document.createElement("span"); w.id = "buildWarn"; w.className = "build-warn"; inp.parentNode.parentNode.insertBefore(w, $("buildNextBtn")); }
      w.textContent = "Give the deck a name first.";
    }
  }, true);
  $("buildDeckName") && $("buildDeckName").addEventListener("input", function () {
    this.classList.remove("is-missing"); var w = $("buildWarn"); if (w) w.textContent = "";
  });

  var nextBtn = $("buildNextBtn");
  if (nextBtn) nextBtn.addEventListener("click", function () {""")

open(p, "w", encoding="utf-8").write(s)
print("ok")
