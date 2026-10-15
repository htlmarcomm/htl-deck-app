# -*- coding: utf-8 -*-
"""Deck cards: the "made by" name no longer sits on top of the slide picture; it is a plain line under the name."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "src", "frontend", "app.html")
s = open(p, encoding="utf-8").read()


def sw(o, n):
    global s
    assert s.count(o) == 1, (s.count(o), o[:90])
    s = s.replace(o, n)


sw("""          badge.textContent = ownerAccount ? ownerAccount.name : owner;
          card.appendChild(badge);""", """          badge.textContent = ownerAccount ? ownerAccount.name : owner;
          var meta = card.querySelector(".deck-card__meta");
          if(meta) meta.insertAdjacentElement("afterend", badge); else card.appendChild(badge);""")
sw("""  /* help */
  .help-banner{""", """  .deck-card__owner{position:static; display:block; background:none; color:#6b7280; padding:0; border-radius:0; font-size:.88rem; font-weight:500; letter-spacing:0; margin:-4px 0 9px;}
  .deck-card__owner::before{content:"Made by ";}

  /* help */
  .help-banner{""")
open(p, "w", encoding="utf-8").write(s)
print("ok")
