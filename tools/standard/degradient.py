# -*- coding: utf-8 -*-
"""Undo the dark caption gradient that is baked into the project-card photos.
Those photos were cut from the original slide screenshots, where a black gradient sat over each photo
(darkest at the right edge, where the white captions were). Averaging all 83 such photos against the
119 plain photos gives the gradient's shape; it is fitted as a smooth surface t(x, y) (how much light
got through) and divided back out: original = pixel / t. Photos are written as new files (originals
kept) and the mapping is saved to tools/standard/degradient_map.json.

  python tools/standard/degradient.py [--sample OUTDIR]   (sample: before/after previews only)"""
import json
import os
import re
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MEDIA = os.path.join(ROOT, "public", "media")
orig = json.load(open(os.path.join(HERE, "originals.json"), encoding="utf-8"))

A, B = [], []
for k, h in orig.items():
    if not k.startswith("pj_"):
        continue
    for m in re.finditer(r'class="(pj-card|pj-ph[^"]*)"[^>]*background-image:url\(([^)]+)\)', h):
        (A if m.group(1) == "pj-card" else B).append(m.group(2))
A = sorted(set(A))
N = 48


def mean_map(urls):
    acc, n = np.zeros((N, N)), 0
    for u in urls:
        acc += np.asarray(Image.open(os.path.join(ROOT, "public", u.lstrip("/"))).convert("L").resize((N, N), Image.BILINEAR), float)
        n += 1
    return acc / n


# measured (8x8 average of the 83 photos against the 119 plain ones): the overlay is horizontal only -
# no darkening on the left 45 %, then a straight fade to ~30 % light at the right edge, the same on every row
def t_of(x):
    return np.clip(1.0 - 1.41 * np.clip(x - 0.45, 0, None), 0.28, 1.0)


def undo(path):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    t = t_of((np.arange(w) + 0.5) / w)[None, :, None]
    a = np.asarray(im, float) / t
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--sample":
        out = sys.argv[2]
        os.makedirs(out, exist_ok=True)
        tiles = []
        for u in A[:8]:
            p = os.path.join(ROOT, "public", u.lstrip("/"))
            b, a = Image.open(p).convert("RGB"), undo(p)
            row = Image.new("RGB", (b.width * 2 + 10, b.height), "white")
            row.paste(b, (0, 0)); row.paste(a, (b.width + 10, 0))
            tiles.append(row.resize((420, int(420 * row.height / row.width))))
        H = sum(t.height + 8 for t in tiles)
        sheet = Image.new("RGB", (420 * 2 + 10, (H + 1) // 2 + 300), "#888")
        x = y = 0
        for i, t in enumerate(tiles):
            if i == 4:
                x, y = 430, 0
            sheet.paste(t, (x, y)); y += t.height + 8
        sheet.save(os.path.join(out, "degradient_sample.jpg"), quality=88)
        print("light-through by column:", np.round(t_of(np.linspace(0, 1, 9)), 2))
        sys.exit(0)
    mapping = {}
    import hashlib
    for u in A:
        p = os.path.join(ROOT, "public", u.lstrip("/"))
        img = undo(p)
        import io
        buf = io.BytesIO(); img.save(buf, "JPEG", quality=92)
        raw = buf.getvalue()
        name = hashlib.sha1(raw).hexdigest()[:16] + ".jpg"
        open(os.path.join(MEDIA, name), "wb").write(raw)
        mapping[u] = "/media/" + name
    json.dump(mapping, open(os.path.join(HERE, "degradient_map.json"), "w"), indent=0)
    print("fixed", len(mapping), "photos")
