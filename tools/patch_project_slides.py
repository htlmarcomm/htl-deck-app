# -*- coding: utf-8 -*-
"""Rebuilds every project slide (Major Projects customisable, Project Slide CRE / Data
Centre, the seven Major Projects segment slides) in the BFSI design the user supplied:
dark building panel with a three-line title on the left, a "PROJECTS" heading and a grid
of photo cards (name, location, Area / Scope) on the right. Also adds a Major BFSI
Projects slide built from that screenshot. Edits src/frontend/app.html (kept for provenance)."""
import hashlib
import io
import json
import os
import re

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, "src", "frontend", "app.html")
SHOT = r"C:\Users\anush\AppData\Local\Temp\claude\C--Users-anush-Downloads-htl-block-library--1-\82340fe9-609b-4b89-a00e-de3b7be70e35\images\52.jpg"

s = open(APP, encoding="utf-8").read()


def blob(i):
    a = s.find('id="%s"' % i)
    o = s.find(">", a) + 1
    e = s.find("</script>", o)
    return json.loads(s[o:e])


old = blob("all-snippets-data")
HTL_LOGO = re.search(r'class=\\"kc-logo\\" src=\\"([^"\\]+)\\"', s).group(1)

shot = Image.open(SHOT).convert("RGB")


def store(im, q=92, name=None):
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q)
    raw = buf.getvalue()
    n = name or (hashlib.sha1(raw).hexdigest()[:16] + ".jpg")
    open(os.path.join(ROOT, "public", "media", n), "wb").write(raw)
    return "/media/" + n


SIDE = "/media/6b6c31fd8090c4b5.jpg"  # built by tools/bp_side_photo.py (panel photo with the title lettering painted out)
PHOTOS = {
    "JP Morgan": store(shot.crop((735, 169, 922, 324))),
    "Goldman Sachs": store(shot.crop((1310, 169, 1499, 330))),
    "Citi Bank": store(shot.crop((468, 517, 656, 671))),
    "HSBC": store(shot.crop((1015, 516, 1202, 671))),
}


def cards_from(key):
    h = old[key]
    out = []
    for c in re.findall(r'<article class="(?:segment-card|project-slide-card)"[^>]*>(.*?)</article>', h, re.S):
        name = re.search(r"<h3>(.*?)</h3>", c).group(1)
        bg = re.search(r"url\('([^']+)'\)", c)
        dl = dict(re.findall(r"<dt>(.*?)</dt><dd>(.*?)</dd>", c))
        out.append(dict(name=name, img=bg.group(1) if bg else "", loc=dl.get("Location", ""),
                        a_lbl="Capacity" if "Capacity" in dl else "Area",
                        area=dl.get("Area") or dl.get("Capacity") or "", scope=dl.get("Scope", "")))
    return out


def card_html(c):
    img = ('<div class="bp-card__img" style="background-image:url(\'%s\')"></div>' % c["img"]) if c["img"] else \
        '<div class="bp-card__img bp-card__img--empty"><span>Image placeholder</span></div>'
    return ('<article class="bp-card%s">%s<h3>%s</h3><p class="bp-loc">%s</p>'
            '<dl class="bp-meta"><div><dt>%s:</dt><dd>%s</dd></div><div><dt>Scope:</dt><dd>%s</dd></div></dl></article>'
            % (c.get("eor", ""), img, c["name"], c["loc"] or "—", c["a_lbl"], c["area"] or "—", c["scope"] or "—"))


def slide_html(key, lines, size, cards):
    n = len(cards)
    for i, c in enumerate(cards):
        c["eor"] = " bp-eor" if (i % 4 == 3 or i == n - 1) else ""
    rows = max(1, min(3, -(-n // 4)))
    t2 = "".join("<span>%s</span>" % l for l in lines)
    return ('<section class="bp-slide" data-block="%s">'
            '<div class="bp-side" style="background-image:url(\'%s\')"><div class="bp-title">'
            '<span class="bp-t1">MAJOR</span><strong class="bp-t2" style="font-size:%dpx">%s</strong>'
            '<span class="bp-t3">PROJECTS</span></div></div>'
            '<div class="bp-main"><div class="bp-head">PROJECTS</div><i class="bp-rule"></i>'
            '<div class="bp-grid" data-rows="%d">%s</div></div>'
            '<img class="bp-logo" src="%s" alt="HTL"></section>'
            % (key, SIDE, size, t2, rows, "".join(card_html(c) for c in cards), HTL_LOGO))


NEW = {}
LABELS = {}

# (key, title lines, font size of the big word)
SEG = [
    ("project_slide_cre", ["CRE"], 72),
    ("project_slide_dc", ["DATA", "CENTRE"], 56),
    ("major_projects_segment_industrial", ["INDUSTRIAL", "+", "WAREHOUSING"], 30),
    ("major_projects_segment_mep", ["MEP"], 72),
    ("major_projects_segment_manufacturing", ["MANUFACTURING"], 26),
    ("major_projects_segment_private_luxury", ["PRIVATE", "LUXURY", "RESIDENTIAL"], 30),
    ("major_projects_segment_hospitality", ["HOSPITALITY"], 30),
    ("major_projects_segment_edu", ["EDUCATION", "INSTITUTES"], 34),
    ("major_projects_segment_hospitals", ["HOSPITAL"], 42),
]
for key, lines, size in SEG:
    NEW[key] = slide_html(key, lines, size, cards_from(key))

NEW["major_projects_customisable"] = slide_html("major_projects_customisable", ["SELECTED"], 40, [
    dict(name="80MW Data Centre", img="", loc="Mumbai", a_lbl="Area", area="1.2M sq.ft", scope=""),
    dict(name="Foxconn Manufacturing", img="", loc="Chennai", a_lbl="Area", area="850K sq.ft", scope=""),
    dict(name="Biocon Campus", img="", loc="Bengaluru", a_lbl="Area", area="640K sq.ft", scope=""),
])

# the BFSI slide, copied from the screenshot
ms = re.search(r"/media/aa41381e03448674\.jpg", old["project_slide_cre"]).group(0)
boa = re.search(r"/media/e0370c6e96e57793\.jpg", old["project_slide_cre"]).group(0)
mc = re.search(r"/media/b6b77774c91a9023\.jpg", old["project_slide_cre"]).group(0)
indus = re.search(r"/media/56077098d3caa757\.jpg", old["major_projects_segment_mep"]).group(0)
bfsi = [
    ("Morgan Stanley", ms, "Mumbai", "1.M", "Mechanical"),
    ("JP Morgan", PHOTOS["JP Morgan"], "Powai, Mumbai", "3.5L", "HVAC"),
    ("Bank of America", boa, "Mum, Guj, Chennai &amp; BLR", "0.2 M", "HVAC"),
    ("Goldman Sachs", PHOTOS["Goldman Sachs"], "Worli, Mumbai", "40,000", "HVAC"),
    ("Citi Bank", PHOTOS["Citi Bank"], "Mumbai, Pune &amp; Chennai", "3,00,000", "HVAC"),
    ("Mastercard", mc, "Mumbai, Pune &amp; Vadodara", "9,00,000", "HVAC"),
    ("HSBC", PHOTOS["HSBC"], "Chennai", "2,00,000", "HVAC"),
    ("IndusInd Bank", indus, "Chennai", "5,00,000", "MEP"),
]
NEW["major_projects_segment_bfsi"] = slide_html("major_projects_segment_bfsi", ["BFSI"], 72, [
    dict(name=a, img=b, loc=c, a_lbl="Area", area=d, scope=e) for a, b, c, d, e in bfsi])

CSS = """
  /* ---- Project slides (BFSI design): dark building panel + three-line title on the
     left, "PROJECTS" heading and a grid of photo cards on the right. Laid out on a
     1280x720 page (SLIDE_LAYOUT_W) and scaled to the slide by fitSlideStage(). The
     grid holds up to 4 cards per row; bpLayout() sets data-rows (1-3) and the
     bp-eor class (last card of a row, so its divider stops at the card). ---- */
  .real-scope .bp-slide{position:relative; width:1280px; height:720px; background:#fff; color:#1b1b1b; overflow:hidden;}
  .real-scope .bp-slide *{box-sizing:border-box;}
  .real-scope .bp-slide .bp-side{position:absolute; left:0; top:0; width:314px; height:720px; background-color:#4b5a5a; background-size:cover; background-position:center bottom;}
  .real-scope .bp-slide .bp-title{position:absolute; left:48px; top:44px; width:250px; color:#fff; line-height:1;}
  .real-scope .bp-slide .bp-t1, .real-scope .bp-slide .bp-t3{display:block; font-size:33px; font-weight:300; letter-spacing:.01em; line-height:1.15;}
  .real-scope .bp-slide .bp-t2{display:block; font-weight:700; line-height:1.04; margin:6px 0 4px; letter-spacing:-.005em;}
  .real-scope .bp-slide .bp-t2 span{display:block; white-space:nowrap;}
  .real-scope .bp-slide .bp-main{position:absolute; left:369px; top:0; width:851px; height:720px;}
  .real-scope .bp-slide .bp-head{position:absolute; left:0; top:58px; font-size:15px; font-weight:700; letter-spacing:.02em; line-height:20px;}
  .real-scope .bp-slide .bp-rule{position:absolute; left:0; top:92px; width:851px; height:1px; background:#4a4a4a; display:block;}
  .real-scope .bp-slide .bp-grid{position:absolute; left:0; top:125px; width:851px; height:520px; display:grid; grid-template-columns:repeat(4,183px); column-gap:40px; row-gap:16px; align-content:start; grid-template-rows:repeat(2,minmax(0,1fr));}
  .real-scope .bp-slide .bp-grid[data-rows="1"]{grid-template-rows:252px;}
  .real-scope .bp-slide .bp-grid[data-rows="3"]{grid-template-rows:repeat(3,minmax(0,1fr)); row-gap:12px;}
  .real-scope .bp-slide .bp-card{position:relative; display:flex; flex-direction:column; min-width:0; min-height:0;}
  .real-scope .bp-slide .bp-card__img{flex:1 1 0; min-height:44px; background-color:#e4e1da; background-size:cover; background-position:center; position:relative;}
  .real-scope .bp-slide .bp-card__img--empty{display:grid; place-items:center;}
  .real-scope .bp-slide .bp-card__img--empty span{font-size:10.5px; color:#8d887c;}
  .real-scope .bp-slide .bp-card h3{margin:11px 0 0; font-size:14.5px; font-weight:700; line-height:1.2; max-height:2.4em; overflow:hidden; color:#111;}
  .real-scope .bp-slide .bp-loc{margin:2px 0 0; font-size:11px; font-weight:400; line-height:1.25; color:#444; max-height:2.5em; overflow:hidden;}
  .real-scope .bp-slide .bp-meta{position:relative; margin:9px 0 0; padding:10px 0 0; display:grid; grid-template-columns:auto auto; justify-content:space-between; column-gap:8px; row-gap:3px; font-size:10.5px; line-height:1.25;}
  .real-scope .bp-slide .bp-meta::before{content:""; position:absolute; left:0; top:0; width:calc(100% + 40px); height:1px; background:#c9c9c9;}
  .real-scope .bp-slide .bp-eor .bp-meta::before{width:100%;}
  .real-scope .bp-slide .bp-meta > div{display:contents;}
  .real-scope .bp-slide .bp-meta dt{margin:0; font-weight:700; text-transform:uppercase; letter-spacing:.02em; color:#111;}
  .real-scope .bp-slide .bp-meta dd{margin:0; font-weight:400; color:#555; overflow-wrap:anywhere;}
  .real-scope .bp-slide .bp-logo{position:absolute; left:1216px; top:672px; width:40px; height:auto; max-width:none; display:block;}
  .real-scope .bp-slide .bp-grid > .ws-ghost-card{position:absolute; top:-70px; right:0; width:auto; height:auto; min-height:0; white-space:nowrap; flex:none; flex-direction:row; gap:6px; padding:5px 12px; border-radius:999px; font-size:11px; background:#fff;}
  .real-scope .bp-slide .bp-grid > .ws-ghost-card .ws-ghost-icon{width:18px; height:18px; font-size:13px;}
  .real-scope .bp-slide .bp-card .ws-card-remove{top:6px; right:6px;}
"""


def sw(o, n):
    global s
    assert s.count(o) == 1, (s.count(o), o[:100])
    s = s.replace(o, n)


def edit_json(marker, fn):
    global s
    a = s.find(marker)
    o = s.find(">", a) + 1
    e = s.find("</script>", o)
    orig = s[o:e]
    compact = '": "' not in orig[:400]
    data = json.loads(orig)
    data = fn(data) or data
    out = json.dumps(data, ensure_ascii=False, separators=(",", ":") if compact else None).replace("</script", "<\\/script")
    s = s[:o] + out + s[e:]


def snip(d):
    new = {}
    for k, v in d.items():
        if k == "major_projects_segment_industrial":
            new["major_projects_segment_bfsi"] = NEW["major_projects_segment_bfsi"]
        new[k] = NEW[k] if (k in NEW and k != "major_projects_segment_bfsi") else v
    assert "major_projects_segment_bfsi" in new
    return new


edit_json('id="all-snippets-data"', snip)


def seed(d):
    out = []
    for x in d:
        if x["key"] == "major_projects_segment_industrial":
            out.append({"key": "major_projects_segment_bfsi", "label": "Major Projects \u2014 BFSI", "kind": "static", "slots": []})
        out.append(x)
    return out


edit_json('id="workspace-data"', seed)

# ------------------------------------------------------------------ CSS + layout widths
sw("  .ws-card-remove{position:absolute; top:6px; right:6px;", CSS + "\n  .ws-card-remove{position:absolute; top:6px; right:6px;")

BP_KEYS = ["major_projects_customisable", "project_slide_cre", "project_slide_dc", "major_projects_segment_bfsi"] + \
          [k for k, _, _ in SEG if k.startswith("major_projects_segment_")]
sw("    thank_you: 1003\n  };", "    thank_you: 1003,\n" + ",\n".join("    %s: 1280" % k for k in BP_KEYS) + "\n  };")

# fitSlideStage: these slides are fixed pages now, not auto-fitting card grids
sw("""  function projectGridCfg(key){
    if(!key) return null;""", """  function isBpKey(k){
    return k === 'major_projects_customisable' || k.indexOf('project_slide_') === 0 || k.indexOf('major_projects_segment_') === 0;
  }
  function projectGridCfg(key){
    if(!key) return null;
    if(isBpKey(key)) return null; // BFSI-design project slides are fixed 1280x720 pages (SLIDE_LAYOUT_W)""")

sw("    major_projects_customisable: ['stagger', '.project-card'],\n    project_slide_cre: ['stagger', '.project-slide-card'],\n    project_slide_dc: ['stagger', '.project-slide-card'],",
   "    major_projects_customisable: ['stagger', '.bp-card'],\n    project_slide_cre: ['stagger', '.bp-card'],\n    project_slide_dc: ['stagger', '.bp-card'],")
sw("return ['stagger', '.segment-card'];", "return ['stagger', '.bp-card'];")

# ------------------------------------------------------------------ editing code
sw("""    if(key === 'major_projects_customisable') return slideEl.querySelector('.project-grid');
    if(key.indexOf('project_slide') === 0) return slideEl.querySelector('.project-slide-grid');
    return null;
  }""", """    var bp = slideEl.querySelector('.bp-grid');
    if(bp) return bp;
    if(key === 'major_projects_customisable') return slideEl.querySelector('.project-grid');
    if(key.indexOf('project_slide') === 0) return slideEl.querySelector('.project-slide-grid');
    return null;
  }
  // BFSI-design grid: 4 cards a row, 1-3 rows; the last card of each row ends its divider line
  function bpLayout(grid){
    var cards = realCards(grid), n = cards.length;
    grid.setAttribute('data-rows', Math.max(1, Math.min(3, Math.ceil(n / 4))));
    cards.forEach(function(c, i){ c.classList.toggle('bp-eor', i % 4 === 3 || i === n - 1); });
  }""")

sw("""  function balanceGrid(grid, ghost){
    var width = grid.clientWidth;""", """  function balanceGrid(grid, ghost){
    if(grid.classList.contains('bp-grid')){ bpLayout(grid); return; }
    var width = grid.clientWidth;""")

sw("""  function cardName(card){
    var h3 = card.querySelector('h3');
    return h3 ? h3.textContent.trim() : '';
  }""", """  function cardName(card){
    var full = card.getAttribute('data-full');
    if(full) return full;
    var h3 = card.querySelector('h3');
    return h3 ? h3.textContent.trim() : '';
  }""")

sw("""      ghost.className = key.indexOf('project_slide') === 0 ? 'project-slide-card ws-ghost-card' : 'project-card project-card--ghost';""",
   """      ghost.className = grid.classList.contains('bp-grid') ? 'ws-ghost-card bp-ghost' :
        key.indexOf('project_slide') === 0 ? 'project-slide-card ws-ghost-card' : 'project-card project-card--ghost';""")

sw("""    var h3 = card.querySelector('h3'); if(h3) h3.textContent = name;
    var p = card.querySelector('p'); if(p) p.textContent = detail ? (detail.location + ' · ' + detail.area) : 'Location · Area';
    card.querySelectorAll('dd').forEach(function(dd, i){
      dd.textContent = detail ? (i === 0 ? detail.area : detail.location) : (i === 0 ? 'Sq.ft' : 'Location');
    });
    var img = card.querySelector('.project-card__image, .project-slide-image');
    if(img){
      img.style.backgroundImage = '';
      if(img.classList.contains('project-slide-image') && !img.querySelector('span')) img.innerHTML = '<span>Image placeholder</span>';
    }""", """    var h3 = card.querySelector('h3');
    var loc = card.querySelector('.bp-loc');
    if(loc){
      // BFSI-design card: short name on the card, the full database name kept to tick / untick the list
      card.setAttribute('data-full', name);
      if(h3) h3.textContent = name.split(' \\u2014 ')[0];
      loc.textContent = detail ? detail.location : 'Location';
      var dds = card.querySelectorAll('dd');
      if(dds[0]) dds[0].textContent = detail ? detail.area : '\\u2014';
      if(dds[1]) dds[1].textContent = '\\u2014';
      var bimg = card.querySelector('.bp-card__img');
      if(bimg){
        bimg.style.backgroundImage = '';
        bimg.classList.add('bp-card__img--empty');
        bimg.innerHTML = '<span>Image placeholder</span>';
      }
    } else {
      if(h3) h3.textContent = name;
      var p = card.querySelector('p'); if(p) p.textContent = detail ? (detail.location + ' · ' + detail.area) : 'Location · Area';
      card.querySelectorAll('dd').forEach(function(dd, i){
        dd.textContent = detail ? (i === 0 ? detail.area : detail.location) : (i === 0 ? 'Sq.ft' : 'Location');
      });
      var img = card.querySelector('.project-card__image, .project-slide-image');
      if(img){
        img.style.backgroundImage = '';
        if(img.classList.contains('project-slide-image') && !img.querySelector('span')) img.innerHTML = '<span>Image placeholder</span>';
      }
    }""")

sw("""          if(card){
            var p = card.querySelector('p'); if(p) p.textContent = detail.location + ' · ' + detail.area;
            card.querySelectorAll('dd').forEach(function(dd, i){ dd.textContent = i === 0 ? detail.area : detail.location; });
          }""", """          if(card){
            var bl = card.querySelector('.bp-loc');
            if(bl){
              bl.textContent = detail.location;
              var bd = card.querySelector('dd'); if(bd) bd.textContent = detail.area;
            } else {
              var p = card.querySelector('p'); if(p) p.textContent = detail.location + ' · ' + detail.area;
              card.querySelectorAll('dd').forEach(function(dd, i){ dd.textContent = i === 0 ? detail.area : detail.location; });
            }
          }""")

# deck-level key list (Master Profile Deck download / upload)
sw('"major_projects_segment_industrial","major_projects_segment_mep"', '"major_projects_segment_bfsi","major_projects_segment_industrial","major_projects_segment_mep"')

# picker thumbnail for the new slide, just before Industrial + Warehousing
eye = "\U0001F441"
card = ('<div class="thumb-card"><div class="thumb-stage-wrap"><div class="thumb-stage real-scope" data-key="major_projects_segment_bfsi"></div></div>'
        '<div class="thumb-card__order">12</div><div class="thumb-card__label">Major Projects \u2014 BFSI</div>'
        '<button class="thumb-card__toggle" aria-label="Hide slide">%s</button></div>' % eye)
anchor = '<div class="thumb-card"><div class="thumb-stage-wrap"><div class="thumb-stage real-scope" data-key="major_projects_segment_industrial"></div></div>'
sw(anchor, card + anchor)

open(APP, "w", encoding="utf-8").write(s)
print("ok", len(NEW), "slides rebuilt; side image", SIDE)
