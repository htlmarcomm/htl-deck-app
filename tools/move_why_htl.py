# -*- coding: utf-8 -*-
"""Moves the "Why HTL for MEP" card from the Company section to Safety & Quality
(after Service Implementation Process) in the Master Profile Deck picker."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "src", "frontend", "app.html")
s = open(p, encoding="utf-8").read()


def card(key):
    m = re.search(r'<div class="thumb-card[^"]*"><div class="thumb-stage-wrap"><div class="thumb-stage real-scope" data-key="%s"></div></div>.*?</button></div>' % key, s)
    assert m, key
    return m


why = card("why_htl_mep")
assert s.count(why.group(0)) == 1
svc = card("service_implementation_process")
card_html = why.group(0)
# remove from Company (and the newline it may sit on), then append after the service card
s = s.replace(card_html + "\n", "", 1) if (card_html + "\n") in s else s.replace(card_html, "", 1)
svc = card("service_implementation_process")
s = s[: svc.end()] + card_html + s[svc.end():]
open(p, "w", encoding="utf-8").write(s)
print("moved")
