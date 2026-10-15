# -*- coding: utf-8 -*-
"""Phone-width sidebar: brand on its own line, nav items in a row below, no user line."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "src", "frontend", "app.html")
s = open(p, encoding="utf-8").read()
old = """  body .app-header{position:sticky; top:0; bottom:auto; width:auto; height:auto; flex-direction:row; flex-wrap:wrap; align-items:center; gap:4px 14px; padding:10px 16px; border-right:0; border-bottom:1px solid var(--line); margin:-16px -16px 18px; overflow:visible;}
  body .app-header__brand{margin:0; font-size:1.05rem; line-height:1.6;}
  body .app-header__user{flex-direction:row; flex-wrap:wrap; align-items:center; gap:2px; flex:1;}
  body .nav-item{width:auto; padding:6px 10px;}
  body .app-header__user-info{order:0; margin:0 0 0 auto; padding:0; border:0;}
  body .nav-item--out{order:1;}"""
new = """  body .app-header{position:sticky; top:0; bottom:auto; width:auto; height:auto; flex-direction:column; align-items:stretch; gap:6px; padding:10px 12px 8px; border-right:0; border-bottom:1px solid var(--line); margin:-16px -16px 18px; overflow:visible;}
  body .app-header__brand{margin:0; padding:0 4px; font-size:1.05rem; line-height:1.5;}
  body .app-header__user{flex-direction:row; flex-wrap:wrap; align-items:center; gap:2px; flex:none;}
  body .nav-item{width:auto; padding:6px 10px;}
  body .app-header__user-info{display:none;}
  body .nav-item--out{order:1; margin-left:auto;}"""
assert s.count(old) == 1
s = s.replace(old, new)
open(p, "w", encoding="utf-8").write(s)
print("ok")
