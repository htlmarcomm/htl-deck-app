# -*- coding: utf-8 -*-
"""Puts the "Internal Systems & Processes" section ahead of "Safety & Quality"
in the Master Profile Deck picker."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "src", "frontend", "app.html")
s = open(p, encoding="utf-8").read()

OPEN = '<div class="section-group"><div class="section-group__title">'
a = s.index(OPEN + "Safety &amp; Quality</div>") if (OPEN + "Safety &amp; Quality</div>") in s else s.index(OPEN + "Safety & Quality</div>")
b = s.index(OPEN + "Internal Systems &amp; Processes</div>")
c = s.index(OPEN + "Closing</div>")
assert a < b < c
safety, internal = s[a:b], s[b:c]
s = s[:a] + internal + safety + s[c:]
open(p, "w", encoding="utf-8").write(s)
print("swapped")
