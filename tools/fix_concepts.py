# -*- coding: utf-8 -*-
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "public", "sources.js")
s = open(p, encoding="utf-8").read()
a = s.index("  var CONCEPTS = [")
b = s.index("  ];", a) + len("  ];")
new = r'''  var CONCEPTS = [
    ["serial", null],
    ["pmc", /pmc|architect|consultant/],
    ["value", /value|amount|cost|price|\brs\b|\bcr\b|crore/],
    ["area", /area|sq\.?\s*ft|sqft|square/],
    ["location", /location|address|city|place|\bsite\b|town/],
    ["scope", /scope|package|detail|service|trade/],
    ["sector", /sector|segment|category|\btype\b/],
    ["name", /name|project|client|customer|company/],
    ["date", /date|start|end|finish|handover/],
  ];'''
s = s[:a] + new + s[b:]
assert "\x08" not in s, "stray backspace characters left"
open(p, "w", encoding="utf-8").write(s)
print("fixed")
