# -*- coding: utf-8 -*-
"""Hooks for public/workspace-tools.js (Undo / Redo + logo-image upload) and the new picker tools:
 - deck-store.js: markAutosaveDirty tells HTLHistory; HTLDeckState.snapshot()/restore() expose the saved-deck state
 - app.html: overlay controls are editing furniture (not saved / shared); the two new scripts are loaded."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def edit(path, pairs):
    p = os.path.join(ROOT, path)
    s = open(p, encoding="utf-8").read()
    for o, n in pairs:
        assert s.count(o) == 1, (path, s.count(o), o[:90])
        s = s.replace(o, n)
    open(p, "w", encoding="utf-8").write(s)


edit("public/deck-store.js", [
    ("""  window.markAutosaveDirty = function () {
    DS.dirty = true;""", """  window.markAutosaveDirty = function () {
    if (window.HTLHistory) window.HTLHistory.changed();
    DS.dirty = true;"""),
    ("""  window.addEventListener("beforeunload", function (e) {""", """  // used by Undo / Redo (workspace-tools.js): the whole deck as text, and back again
  window.HTLDeckState = {
    snapshot: function () {
      captureAll();
      return JSON.stringify({ slides: serialSlides(), sources: window.HTLSources ? HTLSources.exportState() : [] });
    },
    restore: function (json) {
      var st = JSON.parse(json);
      var active = wsActiveIndex, top = wsLeft ? wsLeft.scrollTop : 0;
      WORKSPACE_SLIDES.length = 0;
      st.slides.forEach(function (s) { WORKSPACE_SLIDES.push(s); });
      wsSelectedIndices = {};
      if (window.HTLSources) HTLSources.load(st.sources);
      wsBuilt = false;
      window.initWorkspace();
      if (WORKSPACE_SLIDES.length) {
        try { selectWsSlide(Math.min(active, WORKSPACE_SLIDES.length - 1)); } catch (e) {}
      }
      if (wsLeft) wsLeft.scrollTop = top;
      window.markAutosaveDirty();
    }
  };
  window.addEventListener("beforeunload", function (e) {"""),
])

edit("src/frontend/app.html", [
    ("""'.cs-canvas-toolbar, .cs-add-btn, .cs-empty-hint, .cs-image-link-btn, .cs-section-drag-handle, .cs-section-remove, .cs-row-del, .cs-add-row';""",
     """'.cs-canvas-toolbar, .cs-add-btn, .cs-empty-hint, .cs-image-link-btn, .cs-section-drag-handle, .cs-section-remove, .cs-row-del, .cs-add-row, .ws-ovl-del, .ws-ovl-rs';"""),
    ("""<script src="/sources.js"></script>""", """<script src="/sources.js"></script>\n<script src="/picker-tools.js"></script>\n<script src="/workspace-tools.js"></script>"""),
])
print("ok")
