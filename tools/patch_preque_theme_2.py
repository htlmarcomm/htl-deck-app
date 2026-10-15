# -*- coding: utf-8 -*-
"""Follow-up to patch_preque_theme.py: the app strips width @media rules (and converts vw/vh)
from everything after the block library's :root rule in the main <style> -- that is meant for the
slides, but it also deleted the sidebar's responsive rules. The PreQue look moves to its own
<style> element (untouched by that freeze). Brand text no longer wraps."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "src", "frontend", "app.html")
s = open(p, encoding="utf-8").read()


def sw(o, n):
    global s
    assert s.count(o) == 1, (s.count(o), o[:100])
    s = s.replace(o, n)


sw("\n  /* ================= PreQue look =================",
   '\n</style>\n<style id="preque-look">\n  /* ================= PreQue look =================')
sw("font-size:1.25rem; font-weight:700; color:#1f2937; text-align:left; letter-spacing:-0.01em; line-height:2.5rem;}",
   "font-size:1.125rem; font-weight:700; color:#1f2937; text-align:left; letter-spacing:-0.01em; line-height:1.5; white-space:nowrap;}")
open(p, "w", encoding="utf-8").write(s)
print("ok")
