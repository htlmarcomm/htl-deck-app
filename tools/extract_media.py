# -*- coding: utf-8 -*-
"""One-time conversion of the prototype into the deployable front end.

The prototype is one 14 MB HTML file with every photo and font embedded as a
base64 data: URI. That is fine for a prototype but too big to serve through
a serverless function (Vercel caps responses at ~4.5 MB) and it re-downloads
every image on every visit. This pulls each embedded image/font out into
public/media/<hash>.<ext> (immutable, cached forever) and rewrites the
reference to /media/<hash>.<ext>.

usage: python tools/extract_media.py <prototype.html> <capability-slides.html>
writes: src/frontend/app.html, public/capability-slides.html, public/media/*
"""
import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT = {
    "image/png": "png", "image/jpeg": "jpg", "image/jpg": "jpg", "image/gif": "gif",
    "image/webp": "webp", "image/svg+xml": "svg", "image/x-icon": "ico",
    "font/woff2": "woff2", "font/woff": "woff", "application/font-woff": "woff",
    "application/font-woff2": "woff2", "font/ttf": "ttf", "font/otf": "otf",
    "application/x-font-ttf": "ttf", "application/vnd.ms-fontobject": "eot",
}
URI = re.compile(r"data:([a-zA-Z0-9.+/\-]+);base64,([A-Za-z0-9+/=]{1500,})")
MEDIA = os.path.join(ROOT, "public", "media")
seen = {}


def pull(m):
    mime, b64 = m.group(1), m.group(2)
    ext = EXT.get(mime)
    if not ext:
        return m.group(0)
    import base64
    raw = base64.b64decode(b64 + "=" * (-len(b64) % 4))
    h = hashlib.sha1(raw).hexdigest()[:16]
    name = "%s.%s" % (h, ext)
    if name not in seen:
        os.makedirs(MEDIA, exist_ok=True)
        with open(os.path.join(MEDIA, name), "wb") as f:
            f.write(raw)
        seen[name] = len(raw)
    return "/media/" + name


def convert(src, dst, wrap):
    with open(src, "r", encoding="utf-8") as f:
        text = f.read()
    before = len(text.encode("utf-8"))
    text = URI.sub(pull, text)
    if wrap:
        text = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                '<style>:root{color-scheme:light}body{margin:0;padding:0}</style></head><body>\n'
                + text + "\n</body></html>")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(text)
    print("%s: %.2f MB -> %.2f MB" % (os.path.basename(dst), before / 1e6, len(text.encode("utf-8")) / 1e6))


if __name__ == "__main__":
    proto, cap = sys.argv[1], sys.argv[2]
    convert(proto, os.path.join(ROOT, "src", "frontend", "app.html"), wrap=True)
    with open(cap, "r", encoding="utf-8") as f:
        head = f.read(200).lower()
    convert(cap, os.path.join(ROOT, "public", "capability-slides.html"), wrap="<!doctype" not in head)
    print("%d media files, %.2f MB" % (len(seen), sum(seen.values()) / 1e6))
