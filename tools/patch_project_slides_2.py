# -*- coding: utf-8 -*-
"""Follow-up to patch_project_slides.py: empty photo slots on the BFSI-design project slides
get the "Change photo" hover (a background-image style is what the swap scan looks for),
cards added later get it too, and a swapped-in photo replaces the "Image placeholder" text."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "src", "frontend", "app.html")
s = open(p, encoding="utf-8").read()


def sw(o, n):
    global s
    assert s.count(o) == 1, (s.count(o), o[:100])
    s = s.replace(o, n)


# 1 -- snippets: empty photo slots carry an inline background-image
a = s.find('id="all-snippets-data"')
o = s.find(">", a) + 1
e = s.find("</script>", o)
orig = s[o:e]
data = json.loads(orig)
n = 0
for k, v in data.items():
    if "bp-card__img--empty" in v:
        data[k] = v.replace('class="bp-card__img bp-card__img--empty">', 'class="bp-card__img bp-card__img--empty" style="background-image:none">')
        n += 1
compact = '": "' not in orig[:400]
out = json.dumps(data, ensure_ascii=False, separators=(",", ":") if compact else None).replace("</script", "<\\/script")
s = s[:o] + out + s[e:]

# 2 -- the hover wiring becomes a function that addProjectCard can call too
sw("""    candidates.forEach(function(el){
      if(wsIsBrandLocked(el)) return;
      // same pointer-events:none-ancestor problem as .ws-editable-text
      // (see CSS comment) -- force it back on per-element so hover works
      // regardless of any imported deck's own pointer-events rules.
      el.style.pointerEvents = "auto";
      el.addEventListener("mouseenter", function(){
        wsPhotoSwapTarget = el;
        wsPositionSwapBtn(el);
      });
      el.addEventListener("mouseleave", function(){ wsHideSwapBtnSoon(el); });
    });
  }
""", """    candidates.forEach(wsWirePhoto);
  }
  function wsWirePhoto(el){
    if(wsIsBrandLocked(el)) return;
    // same pointer-events:none-ancestor problem as .ws-editable-text
    // (see CSS comment) -- force it back on per-element so hover works
    // regardless of any imported deck's own pointer-events rules.
    el.style.pointerEvents = "auto";
    el.addEventListener("mouseenter", function(){
      wsPhotoSwapTarget = el;
      wsPositionSwapBtn(el);
    });
    el.addEventListener("mouseleave", function(){ wsHideSwapBtnSoon(el); });
  }
""")

sw("""    var setPhoto = function(u){
      if(swapEl.tagName === "IMG"){ swapEl.src = u; } else { swapEl.style.backgroundImage = "url(" + u + ")"; }
    };""", """    var setPhoto = function(u){
      if(swapEl.tagName === "IMG"){ swapEl.src = u; } else { swapEl.style.backgroundImage = "url(" + u + ")"; }
      if(swapEl.classList && swapEl.classList.contains("bp-card__img--empty")){
        swapEl.classList.remove("bp-card__img--empty");
        var ph = swapEl.querySelector("span"); if(ph) ph.remove();
      }
    };""")

sw("""        bimg.style.backgroundImage = '';
        bimg.classList.add('bp-card__img--empty');
        bimg.innerHTML = '<span>Image placeholder</span>';
      }""", """        bimg.style.backgroundImage = 'none';
        bimg.classList.add('bp-card__img--empty');
        bimg.innerHTML = '<span>Image placeholder</span>';
        wsWirePhoto(bimg);
      }""")

open(p, "w", encoding="utf-8").write(s)
print("ok", n, "slides updated")
