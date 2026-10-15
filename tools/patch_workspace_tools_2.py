# -*- coding: utf-8 -*-
"""Undo bug: initWorkspace() first calls captureAll(), which copies the slides currently on screen
over the restored ones. Empty the slide list on screen before rebuilding."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "public", "deck-store.js")
s = open(p, encoding="utf-8").read()
o = """      if (window.HTLSources) HTLSources.load(st.sources);
      wsBuilt = false;
      window.initWorkspace();
      if (WORKSPACE_SLIDES.length) {"""
n = """      if (window.HTLSources) HTLSources.load(st.sources);
      if (wsLeft) wsLeft.innerHTML = ""; // else initWorkspace()'s captureAll() copies the old screen over what we restore
      wsBuilt = false;
      window.initWorkspace();
      if (WORKSPACE_SLIDES.length) {"""
assert s.count(o) == 1
open(p, "w", encoding="utf-8").write(s.replace(o, n))
print("ok")
