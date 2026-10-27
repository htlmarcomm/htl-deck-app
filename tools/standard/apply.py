# -*- coding: utf-8 -*-
"""Writes the normalised slides (result.json files from run.mjs) into src/frontend/app.html,
adds the Slide Standard CSS (tokens.css + flow.css) in its own <style id="slide-standard"> block,
the Raleway font link, and lays every standardised slide out at 1280 px.

  python tools/standard/apply.py <result.json> [<result.json> ...]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(os.path.dirname(os.path.dirname(HERE)), "src", "frontend", "app.html")
FONT = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;500;600;700&amp;display=swap" id="ss-font">'

s = open(APP, encoding="utf-8").read()
results = {}
for p in sys.argv[1:]:
    results.update(json.load(open(p, encoding="utf-8")))

a = s.find('id="all-snippets-data"')
o = s.find(">", a) + 1
e = s.find("</script>", o)
compact = '": "' not in s[o:o + 400]
snip = json.loads(s[o:e])
for k, r in results.items():
    assert k in snip, k
    snip[k] = r["html"]
s = s[:o] + json.dumps(snip, ensure_ascii=False, separators=(",", ":") if compact else None).replace("</script", "<\\/script") + s[e:]

css = "".join(open(os.path.join(HERE, f), encoding="utf-8").read() for f in ("tokens.css", "flow.css", "templates.css", "projects.css", "sectors.css"))
s = re.sub(r'<style id="slide-standard">.*?</style>\n?', "", s, flags=re.S)
s = s.replace("</head>", '<style id="slide-standard">\n' + css + "</style>\n</head>", 1)
if 'id="ss-font"' not in s:
    s = s.replace("</head>", FONT + "\n</head>", 1)

m = re.search(r"  var SLIDE_LAYOUT_W = \{\n(.*?)\n  \}", s, re.S)
body = "\n".join(l if l.rstrip().endswith(",") or not l.strip() else l.rstrip() + "," for l in m.group(1).split("\n"))
for k in results:
    if re.search(r"(^|\n)    %s: \d+," % re.escape(k), body):
        body = re.sub(r"(^|\n)    %s: \d+," % re.escape(k), r"\1    %s: 1280," % k, body)
    else:
        body += "\n    %s: 1280," % k
s = s[:m.start(1)] + body + s[m.end(1):]
open(APP, "w", encoding="utf-8").write(s)
print("applied", len(results), "slides")
