# -*- coding: utf-8 -*-
"""Share screen: the link and its Copy button sit at the TOP (above the slides),
not below a long scroll. Also: Back from the share screen always goes to Decks."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "src", "frontend", "app.html")
s = open(p, encoding="utf-8").read()


def sw(o, n):
    global s
    assert s.count(o) == 1, (s.count(o), o[:80])
    s = s.replace(o, n)


a = s.index('<div class="share-frame">')
b = s.index("<!-- ============ USERS (Creator only)")
s = s[:a] + '''<div class="share-frame">
      <div class="share-chrome">
        <span id="shareChromeUrl" class="share-chrome__url"></span>
        <div class="share-footer__actions">
          <button class="btn btn--accent btn--sm" id="shareCopyLinkBtn" type="button" data-share-url="">Copy link</button>
          <a class="btn btn--sm" id="shareOpenLink" href="#" target="_blank" rel="noopener" style="text-decoration:none;">Open in new tab</a>
        </div>
      </div>
      <div class="share-deck-scroll" id="shareDeckScroll"></div>
    </div>
  </section>

  ''' + s[b:]
sw("  .ws-card-remove{position:absolute; top:6px; right:6px;",
   "  .share-chrome{gap:14px; flex-wrap:wrap;}\n  .share-chrome__url{font-family:var(--font-mono); font-size:0.78rem; color:#ddd; word-break:break-all; flex:1; min-width:200px;}\n"
   "  .ws-card-remove{position:absolute; top:6px; right:6px;")
open(p, "w", encoding="utf-8").write(s)

p2 = os.path.join(ROOT, "public", "deck-store.js")
t = open(p2, encoding="utf-8").read()
o = '    if (name === "dashboard") loadDecks();'
assert t.count(o) == 1
t = t.replace(o, o + '\n    if (name === "share") { navStack = ["dashboard", "share"]; if (window.updateBackLinks) updateBackLinks(); }')
open(p2, "w", encoding="utf-8").write(t)
print("ok")
