# -*- coding: utf-8 -*-
import os, json, re, sys, html
import cv2
import numpy as np
from content import A, Bs, Cs, SECTIONS
from build_assets import SLIDES, PANEL

SRC = "src"
ASSETS = json.load(open("assets.json"))
CW, CH = 1280, 720


def esc(s): return html.escape(s, quote=False)


# ------------------------------------------------------------------ measuring text
def runs_of(mask, x0, x1, y0, y1, merge_gap=3, min_ink=6):
    """horizontal text lines in a binary mask region -> [{y0,y1,x0,x1,groups}]"""
    sub = mask[y0:y1, x0:x1] > 0
    rows = sub.sum(axis=1) > 0
    out, i, n = [], 0, len(rows)
    while i < n:
        if rows[i]:
            j = i
            gap = 0
            while j < n and (rows[j] or gap < merge_gap):
                gap = 0 if rows[j] else gap + 1
                j += 1
            end = j - gap
            band = sub[i:end]
            if band.sum() >= min_ink:
                cols = band.sum(axis=0) > 0
                xs = np.where(cols)[0]
                # horizontal groups separated by wide gaps
                groups, gs, prev = [], xs[0], xs[0]
                for x in xs[1:]:
                    if x - prev > 22:
                        groups.append((gs + x0, prev + x0)); gs = x
                    prev = x
                groups.append((gs + x0, prev + x0))
                out.append(dict(y0=i + y0, y1=end + y0, x0=int(xs[0]) + x0, x1=int(xs[-1]) + x0, groups=groups))
            i = j
        else:
            i += 1
    return out


def is_rule(r, bandw):
    return (r["y1"] - r["y0"]) <= 4 and (r["x1"] - r["x0"]) > 0.6 * bandw


def has_desc(t): return bool(re.search(r"[gjpqy,;()@]", t))


def fsize(h, text):
    return 0.95 * h / (0.92 if has_desc(text) else 0.76)


# ------------------------------------------------------------------ text emitters (canvas coords)
def T(txt, x, cy, size, weight="r", color=None, align="l", extra="", cls="", lh=1.0):
    st = "font-size:%.1fpx;" % size
    if weight == "b": st += "font-weight:700;"
    elif weight == "m": st += "font-weight:600;"
    elif weight == "l": st += "font-weight:300;"
    if color: st += "color:%s;" % color
    top = cy - size * lh / 2
    if align == "l": st += "left:%.1fpx;" % x
    elif align == "r": st += "right:%.1fpx;text-align:right;" % (CW - x)
    else: st += "left:%.1fpx;transform:translateX(-50%%);text-align:center;" % x
    st += "top:%.1fpx;" % top + extra
    return '<span class="t%s" style="%s">%s</span>' % ((" " + cls) if cls else "", st, esc(txt))


def title_html(lines, x, cys, size):
    """lines: [[(text, weight, red)...], ...]"""
    out = []
    for segs, cy in zip(lines, cys):
        spans = ""
        for (tx, w, red) in segs:
            cls = "tb" if w == "b" else ("tl" if w == "l" else "tr")
            if red: cls += " red"
            spans += '<span class="%s">%s</span>' % (cls, esc(tx))
        out.append('<div class="ttl" style="left:%.1fpx;top:%.1fpx;font-size:%.1fpx;">%s</div>' % (x, cy - size / 2, size, spans))
    return "".join(out)


# ------------------------------------------------------------------ logo
def logo_box(im, s, boxes=()):
    H, W = im.shape[:2]
    y0 = int(0.90 * H); x0 = int(0.86 * W)
    im = im.copy()
    for (a, b, c, d) in boxes:
        im[max(0, b - 8):d + 8, max(0, a - 8):c + 8] = 255
    reg = im[y0:, x0:]
    hsv = cv2.cvtColor(reg, cv2.COLOR_BGR2HSV)
    red = ((hsv[:, :, 0] < 10) | (hsv[:, :, 0] > 170)) & (hsv[:, :, 1] > 120) & (hsv[:, :, 2] > 120)
    dark = reg.max(axis=2) < 95
    m = red | dark
    ys, xs = np.where(red)
    if len(xs) < 40: return None
    rx0, ry0, rx1, ry1 = x0 + int(xs.min()), y0 + int(ys.min()), x0 + int(xs.max()), y0 + int(ys.max())
    sw = rx1 - rx0
    return [rx0, ry0 - 1, rx0 + int(3.15 * sw), ry1 + 1]


LOGO = '<img class="logo" src="{{LOGO}}" alt="HTL" style="left:%.1fpx;top:%.1fpx;width:%.1fpx;">'


def logo_html(im, s, boxes=()):
    b = logo_box(im, s, boxes)
    if not b: return ""
    return LOGO % (b[0] * s, b[1] * s - 1, (b[2] - b[0]) * s + 2)


# ------------------------------------------------------------------ family B
def build_B(sid):
    info = ASSETS[sid]; spec = Bs[sid]
    W, H = info["size"]; s = CW / W
    im = cv2.imread(os.path.join(SRC, info["src"]))
    ink = (im.min(axis=2) < 175).astype(np.uint8)
    photos = info["photos"]
    boxes = [p["box"] for p in photos]
    out = ['<section class="pj pj-b" data-block="pj_%s">' % sid]
    pw = info["panel"]["w"]
    out.append('<div class="panel" style="width:%.1fpx;background-image:url({{IMG:%s/panel.jpg}})"></div>' % (pw * s, sid))
    # panel title: measure white text lines
    tb = PANEL[sid][1]
    panel = im[:, :pw]
    g = cv2.cvtColor(panel[tb[1]:tb[3], tb[0]:tb[2]], cv2.COLOR_BGR2GRAY)
    bgm = cv2.medianBlur(g, 41)
    mm = np.zeros(im.shape[:2], np.uint8)
    mm[tb[1]:tb[3], tb[0]:tb[2]] = ((g > 190) & ((g.astype(int) - bgm.astype(int)) > 35)).astype(np.uint8)
    pr = runs_of(mm, tb[0], tb[2], tb[1], tb[3], merge_gap=6)
    pr = [r for r in pr if (r["y1"] - r["y0"]) > 12]
    lines = spec["panel"]
    if len(pr) != len(lines):
        print("  !! panel runs", sid, len(pr), "expected", len(lines))
        pr = pr[:len(lines)] if len(pr) > len(lines) else pr + [dict(y0=pr[-1]["y0"] + 60, y1=pr[-1]["y1"] + 60, x0=pr[0]["x0"], x1=pr[0]["x1"])] * (len(lines) - len(pr))
    for ln, r in zip(lines, pr):
        out.append(T(ln, r["x0"] * s, (r["y0"] + r["y1"]) / 2 * s, (r["y1"] - r["y0"]) / 0.76 * s, "b", "#fff", cls="ptitle"))
    # heading "PROJECTS" + rule, above the first row
    top = min(b[1] for b in boxes)
    hr = runs_of(ink, pw + 25, W - 40, 5, top - 6)
    for r in hr:
        if is_rule(r, W - pw):
            col = im[(r["y0"] + r["y1"]) // 2, (r["x0"] + r["x1"]) // 2]
            red = col[2] > 150 and col[1] < 130
            out.append('<i class="rule%s" style="left:%.1fpx;top:%.1fpx;width:%.1fpx;"></i>' % (" red" if red else "", r["x0"] * s, (r["y0"] + r["y1"]) / 2 * s, (r["x1"] - r["x0"]) * s))
        elif (r["y1"] - r["y0"]) > 8:
            out.append(T("PROJECTS", r["x0"] * s, (r["y0"] + r["y1"]) / 2 * s, (r["y1"] - r["y0"]) / 0.72 * s, "b"))
    # cards
    metas = []
    for i, ((name, loc, meta), p) in enumerate(zip(spec["cards"], photos)):
        x0, y0, x1, y1 = p["box"]
        # band for captions
        same = [b for b in boxes if b is not p["box"] and not (b[3] < y0 or b[1] > y1)]
        left = [b[2] for b in same if b[2] <= x0 + 5]
        right = [b[0] for b in same if b[0] >= x1 - 5]
        bx0 = (max(left) + x0) // 2 if left else x0 - 15
        bx1 = (min(right) + x1) // 2 if right else min(W - 30, x1 + 60)
        below = [b[1] for b in boxes if b[1] > y1 + 5 and not (b[2] < x0 - 5 or b[0] > x1 + 5)]
        by1 = min(below) - 4 if below else H - 6
        by0 = y1 + 3
        if sid == "dcnew" and i == 3: bx1 = W - 30
        sub_ink = ink.copy()
        # drop HTL logo area
        sub_ink[int(0.9 * H):, int(0.86 * W):] = 0
        rr = [r for r in runs_of(sub_ink, bx0, bx1, by0, by1) if not is_rule(r, bx1 - bx0) and (r["y1"] - r["y0"]) >= 6]
        metas.append((p, rr, (bx0, bx1)))
    # medians for templates
    need = None
    good = [(p, rr) for (p, rr, _), (n, l, m) in zip(metas, spec["cards"]) if len(rr) == 2 + len(m)]
    sizes = {"name": [], "loc": [], "lab": [], "val": []}
    off = {"name": [], "loc": [], "meta": []}
    for (p, rr), (n, l, m) in zip(good, [c for (pp, rr2, _), c in zip(metas, spec["cards"]) if len(rr2) == 2 + len(c[2])]):
        y1 = p["box"][3]
        sizes["name"].append(fsize(rr[0]["y1"] - rr[0]["y0"], n)); sizes["loc"].append(fsize(rr[1]["y1"] - rr[1]["y0"], l))
        off["name"].append((rr[0]["y0"] + rr[0]["y1"]) / 2 - y1); off["loc"].append((rr[1]["y0"] + rr[1]["y1"]) / 2 - y1)
        for k, r in enumerate(rr[2:]):
            sizes["lab"].append((r["groups"][0][1] and (r["y1"] - r["y0"]) / 0.74))
            off["meta"].append((k, (r["y0"] + r["y1"]) / 2 - y1, r["groups"][0][0] - p["box"][0], r["groups"][-1][0] - p["box"][0] if len(r["groups"]) > 1 else None))
    med = lambda a, d: float(np.median(a)) if a else d
    fs_name = med(sizes["name"], 20); fs_loc = med(sizes["loc"], 18) * 1.1; fs_lab = med(sizes["lab"], 15)
    o_name = med(off["name"], 28); o_loc = med(off["loc"], 56)
    o_meta0 = med([o for k, o, _, _ in off["meta"] if k == 0], 120); pitch = med([off["meta"][i + 1][1] - off["meta"][i][1] for i in range(len(off["meta"]) - 1) if off["meta"][i + 1][0] == off["meta"][i][0] + 1], 19)
    v_dx = med([v for _, _, _, v in off["meta"] if v is not None], 140)
    for (name, loc, meta), (p, rr, (bx0, bx1)) in zip(spec["cards"], metas):
        x0, y0, x1, y1 = p["box"]
        out.append('<div class="ph" style="left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;background-image:url({{IMG:%s/%s}})"></div>' % (x0 * s, y0 * s, (x1 - x0) * s, (y1 - y0) * s, sid, p["img"]))
        if len(rr) == 2 + len(meta):
            n_cy = (rr[0]["y0"] + rr[0]["y1"]) / 2; n_x = rr[0]["x0"]
            l_cy = (rr[1]["y0"] + rr[1]["y1"]) / 2; l_x = rr[1]["x0"]
            m_rows = []
            for k, r in enumerate(rr[2:]):
                m_rows.append(((r["y0"] + r["y1"]) / 2, r["groups"][0][0], r["groups"][-1][0] if len(r["groups"]) > 1 else x0 + v_dx))
        else:
            n_cy = y1 + o_name; n_x = x0 + 3; l_cy = y1 + o_loc; l_x = x0 + 3
            m_rows = [(y1 + o_meta0 + k * pitch, x0 + 3, x0 + v_dx) for k in range(len(meta))]
            print("  fallback layout", sid, i if False else name, len(rr), "runs")
        out.append(T(name, n_x * s, n_cy * s, fs_name * s, "b", cls="nm"))
        out.append(T(loc, l_x * s, l_cy * s, fs_loc * s, "r", "#333", cls="lc"))
        for (lab, val), (cy, lx, vx) in zip(meta, m_rows):
            out.append(T(lab, lx * s, cy * s, fs_lab * s * 0.92, "b", "#222", cls="ml"))
            out.append(T(val, vx * s, cy * s, fs_lab * s * 0.95, "r", "#555", cls="mv"))
        # divider across the card's column
    # long divider lines under each photo row (measured)
    divs = set()
    for (p, rr, (bx0, bx1)) in metas:
        x0, y0, x1, y1 = p["box"]
        band = ink[y1 + 3: y1 + 140, :]
    # find rules directly: wide thin dark/gray rows below photos (gray threshold)
    gray = (im.min(axis=2) < 215).astype(np.uint8)
    for rowtop in sorted(set(b[3] for b in boxes)):
        yy0, yy1 = rowtop + 25, rowtop + 120
        rr = runs_of(gray, pw + 20, W - 20, yy0, yy1, merge_gap=1, min_ink=60)
        for r in rr:
            if (r["y1"] - r["y0"]) <= 4 and (r["x1"] - r["x0"]) > 0.35 * (W - pw):
                key = (r["y0"] // 6, r["x0"] // 20)
                if key in divs: continue
                divs.add(key)
                out.append('<i class="rule thin" style="left:%.1fpx;top:%.1fpx;width:%.1fpx;"></i>' % (r["x0"] * s, (r["y0"] + r["y1"]) / 2 * s, (r["x1"] - r["x0"]) * s))
    out.append(logo_html(im, s))
    out.append("</section>")
    return "\n".join(out)


# ------------------------------------------------------------------ family C
def build_C(sid):
    info = ASSETS[sid]; spec = Cs[sid]
    W, H = info["size"]; s = CW / W
    im = cv2.imread(os.path.join(SRC, info["src"]))
    ink = (im.min(axis=2) < 170).astype(np.uint8)
    photos = info["photos"]; boxes = [p["box"] for p in photos]
    out = ['<section class="pj pj-c" data-block="pj_%s">' % sid]
    top = min(b[1] for b in boxes)
    tr = [r for r in runs_of(ink, 5, W - 5, 5, top - 8) if (r["y1"] - r["y0"]) > 14]
    if tr:
        r = tr[0]
        size = (r["y1"] - r["y0"]) / 0.80
        out.append(title_html(spec["title"], r["x0"] * s, [(r["y0"] + r["y1"]) / 2 * s], size * s))
    for i, (card, p) in enumerate(zip(spec["cards"], photos)):
        x0, y0, x1, y1 = p["box"]
        out.append('<div class="ph rnd" style="left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;background-image:url({{IMG:%s/%s}})"></div>' % (x0 * s, y0 * s, (x1 - x0) * s, (y1 - y0) * s, sid, p["img"]))
        below = [b[1] for b in boxes if b[1] > y1 + 5 and not (b[2] < x0 - 5 or b[0] > x1 + 5)]
        by1 = min(below) - 4 if below else H - 6
        same = [b for b in boxes if b is not p["box"] and not (b[3] < y0 or b[1] > y1)]
        left = [b[2] for b in same if b[2] <= x0 + 5]; right = [b[0] for b in same if b[0] >= x1 - 5]
        bx0 = (max(left) + x0) // 2 if left else x0 - 20
        bx1 = (min(right) + x1) // 2 if right else x1 + 20
        rr = [r for r in runs_of(ink, bx0, bx1, y1 + 3, by1) if (r["y1"] - r["y0"]) >= 6]
        if sid == "vrv":
            lines = [(card[0], "r", None), ("Capacity : %s HP" % card[1], "b", "#d3262a"), ("(%s)" % card[2], "r", None)]
        elif sid == "hosp4":
            lines = [(card[0], "b", None), (card[1], "b", None), ("SCOPE:  %s" % card[2], "scope", None)]
        else:
            lines = [(card[0], "b", None), ("SCOPE:  %s" % card[1], "scope", None)]
        if len(rr) != len(lines):
            print("  !! C runs", sid, i, len(rr), "expected", len(lines))
            cx = (x0 + x1) / 2
            base = y1 + 24
            rr = [dict(y0=base + k * 24 - 8, y1=base + k * 24 + 8, x0=cx - 60, x1=cx + 60, groups=[]) for k in range(len(lines))]
        for (tx, w, col), r in zip(lines, rr):
            cx = (r["x0"] + r["x1"]) / 2
            cy = (r["y0"] + r["y1"]) / 2
            fs = fsize(r["y1"] - r["y0"], tx) * s
            if w == "scope":
                lab, val = tx.split("  ", 1)
                out.append('<span class="t" style="left:%.1fpx;top:%.1fpx;font-size:%.1fpx;transform:translateX(-50%%);text-align:center;"><span class="tb">%s</span><span class="tr">  %s</span></span>' % (cx * s, cy * s - fs / 2, fs, esc(lab), esc(val)))
            else:
                out.append(T(tx, cx * s, cy * s, fs, w, col, align="c"))
    out.append("</section>")
    return "\n".join(out)


# ------------------------------------------------------------------ family A
def build_A(sid):
    info = ASSETS[sid]; spec = A[sid]
    W, H = info["size"]; s = CW / W
    im = cv2.imread(os.path.join(SRC, info["src"]))
    photos = info["photos"]
    out = ['<section class="pj pj-a" data-block="pj_%s">' % sid]
    # ---- title / pill (top band)
    top = info.get("top", {})
    red = top.get("red")
    boxes = [p["box"] for p in photos]
    ytop = min(b[1] for b in boxes) - 10
    ink = ((im.min(axis=2) < 110) | ((im[:, :, 2] > 170) & (im[:, :, 1] < 110) & (im[:, :, 0] < 110))).astype(np.uint8)
    pillx0 = W if spec.get("pill") else int(0.55 * W)
    if spec.get("pill"):
        # pill outline = red pixels in the top-right
        hsv = cv2.cvtColor(im[:int(ytop)], cv2.COLOR_BGR2HSV)
        redm = (((hsv[:, :, 0] < 10) | (hsv[:, :, 0] > 170)) & (hsv[:, :, 1] > 45) & (hsv[:, :, 2] > 120))
        redm[:, : int(0.45 * W)] = False
        ys, xs = np.where(redm)
        px0, py0, px1, py1 = int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())
        pillx0 = px0
        out.append('<div class="pill-o" style="left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;"></div>' % (px0 * s, py0 * s, (px1 - px0) * s, (py1 - py0) * s))
        ph = py1 - py0
        out.append(T(spec["pill"], (px0 + px1) / 2 * s, (py0 + py1) / 2 * s, min(ph * 0.47 * s, 0.88 * (px1 - px0) * s / (0.60 * len(spec["pill"]))), "r", "#d3262a", align="c", cls="pilltxt"))
    tr = [r for r in runs_of(ink, 5, pillx0 - 15, 5, int(ytop)) if (r["y1"] - r["y0"]) > 14]
    if tr:
        # titles may include stats top-right for dcmajor (handled below), so keep only lines left of x=0.6W
        tr = [r for r in tr if r["x0"] < 0.5 * W]
        tl = len(spec["title"])
        tr = tr[:tl]
        size = np.median([(r["y1"] - r["y0"]) / 0.80 for r in tr])
        out.append(title_html(spec["title"], tr[0]["x0"] * s, [(r["y0"] + r["y1"]) / 2 * s for r in tr], size * s))
    if spec.get("stats"):
        hsv = cv2.cvtColor(im[:int(ytop)], cv2.COLOR_BGR2HSV)
        redm = (((hsv[:, :, 0] < 10) | (hsv[:, :, 0] > 170)) & (hsv[:, :, 1] > 110) & (hsv[:, :, 2] > 120))
        redm[:, : int(0.6 * W)] = False
        ys, xs = np.where(redm)
        lx = int(xs.min())
        out.append('<i class="vline" style="left:%.1fpx;top:%.1fpx;height:%.1fpx;"></i>' % (lx * s, ys.min() * s, (ys.max() - ys.min()) * s))
        # numbers: red text right of the line
        numm = redm.copy(); numm[:, : lx + 12] = False
        nr = runs_of(numm.astype(np.uint8), lx + 12, W, 0, int(ytop), merge_gap=6)
        nr = [r for r in nr if (r["y1"] - r["y0"]) > 14]
        labs = [("120 MW", "Executed"), ("156 MW", "Under Execution")]
        blk = ink.copy(); blk[:, : lx + 12] = 0
        lr = runs_of(blk, lx + 12, W - 4, 0, int(ytop), merge_gap=6)
        for (num, lab), r in zip(labs, nr):
            size = (r["y1"] - r["y0"]) / 0.72 * s
            out.append(T(num, r["x0"] * s, (r["y0"] + r["y1"]) / 2 * s, size, "r", "#d3262a"))
            rows = [q for q in lr if abs((q["y0"] + q["y1"]) / 2 - (r["y0"] + r["y1"]) / 2) < 25]
            gx = [g for q in rows for g in q["groups"] if g[0] > r["x1"]]
            lx2 = min(g[0] for g in gx) if gx else r["x1"] + 30
            out.append(T(lab, lx2 * s, (r["y0"] + r["y1"]) / 2 * s, size * s * 0.78, "r", "#111"))
    # ---- cards (text is placed by rule: right-aligned block bottom-right, or label/value grid bottom-left)
    first_bold = sid in ("south1", "south2")
    PITCH_R = 31.5 * s   # canvas px between right-aligned lines
    PITCH_L = 25.0 * s
    for i, (c, p) in enumerate(zip(spec["cards"], photos)):
        x0, y0, x1, y1 = p["box"]
        cw, ch = x1 - x0, y1 - y0
        rad = 0.045 * cw * s
        out.append('<div class="card" style="left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;border-radius:%.1fpx;background-image:url({{IMG:%s/%s}})">' % (x0 * s, y0 * s, cw * s, ch * s, rad, sid, p["img"]))
        out.append('<svg class="arw" viewBox="0 0 24 24" style="width:%.1fpx;right:%.1fpx;top:%.1fpx"><path d="M5.5 18.5 18 6M8.5 5.5h10v10" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>' % (0.105 * cw * s, 0.06 * cw * s, 0.05 * ch * s))
        pill = p.get("pill")
        if pill:
            pb = pill["box"]
            if c.get("pilltext"):
                out.append('<span class="pill-t" style="left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;font-size:%.1fpx;line-height:%.1fpx;">%s</span>' % (pb[0] * s, pb[1] * s, (pb[2] - pb[0]) * s, (pb[3] - pb[1]) * s, (pb[3] - pb[1]) * s * 0.42, (pb[3] - pb[1]) * s, esc(c["pilltext"])))
            else:
                out.append('<img class="pill-i" src="{{IMG:%s/%s}}" alt="" style="left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;">' % (sid, pill["img"], pb[0] * s, pb[1] * s, (pb[2] - pb[0]) * s, (pb[3] - pb[1]) * s))
        if c.get("right"):
            lines = c["right"]
            fs = PITCH_R * 0.66
            rows = "".join('<span class="%s">%s</span>' % ("tb" if (first_bold and k == 0) else "tr", esc(ln)) for k, ln in enumerate(lines))
            out.append('<div class="rt cw" style="right:%.1fpx;bottom:%.1fpx;font-size:%.1fpx;line-height:%.1fpx;">%s</div>' % (0.055 * cw * s, 40 * s - PITCH_R / 2, fs, PITCH_R, rows))
            if c.get("topright"):
                out.append('<span class="t cw" style="right:%.1fpx;top:%.1fpx;font-size:%.1fpx;">%s</span>' % (0.055 * cw * s, 0.10 * ch * s, fs * 0.8, esc(c["topright"])))
        elif c.get("left"):
            rows = c["left"]
            fs = PITCH_L * 0.84
            cells = "".join('<span class="tb">%s</span><span class="tr">%s</span>' % (esc(a), esc(b)) for a, b in rows)
            out.append('<div class="kv cw" style="left:%.1fpx;bottom:%.1fpx;font-size:%.1fpx;line-height:%.1fpx;">%s</div>' % (0.07 * cw * s, 30 * s - PITCH_L / 2 + 4 * s, fs, PITCH_L, cells))
            if c.get("above") and pill:
                pb = pill["box"]
                out.append('<span class="t cw" style="left:%.1fpx;top:%.1fpx;font-size:%.1fpx;">%s</span>' % (pb[0] * s, pb[1] * s - 30 * s, fs * 1.2, esc(c["above"])))
        out.append("</div>")
        if c.get("caption"):
            ink2 = (im.min(axis=2) < 110).astype(np.uint8)
            ink2[int(0.9 * H):, int(0.88 * W):] = 0
            q = [r for r in runs_of(ink2, x0 - 30, x1 + 30, y1 + 4, min(H - 4, y1 + 120)) if r["y1"] - r["y0"] >= 8 and r["x0"] < 0.98 * W]
            q = [r for r in q if not (r["y0"] > 0.93 * H and r["x0"] > 0.86 * W)]
            for ln, r in zip(c["caption"], q):
                fs = fsize(r["y1"] - r["y0"], ln) * s
                out.append(T(ln, (r["x0"] + r["x1"]) / 2 * s, (r["y0"] + r["y1"]) / 2 * s, fs, "r", "#111", align="c"))
    out.append(logo_html(im, s, boxes))
    out.append("</section>")
    return "\n".join(out)


def build(sid):
    fam = SLIDES[sid][1]
    return {"A": build_A, "B": build_B, "C": build_C}[fam](sid)


CSS = r"""
  /* ---- Project slides from the BIRA "PROJECT SLIDE" folder: fixed 1280x720 pages, text and photos are click-to-edit ---- */
  .real-scope .pj{position:relative; width:1280px; height:720px; background:#fff; color:#161616; overflow:hidden; font-family:var(--font-slide);}
  .real-scope .pj *{box-sizing:border-box;}
  .real-scope .pj .t{position:absolute; white-space:nowrap; line-height:1; margin:0; padding:0;}
  .real-scope .pj .tb{font-weight:700;} .real-scope .pj .tr{font-weight:400;} .real-scope .pj .tl{font-weight:300;}
  .real-scope .pj .red{color:#d3262a;}
  .real-scope .pj .ttl{position:absolute; white-space:nowrap; line-height:1; color:#111; letter-spacing:-.01em;}
  .real-scope .pj .ph{position:absolute; background-size:cover; background-position:center; background-color:#e4e1da;}
  .real-scope .pj .ph.rnd{border-radius:7px;}
  .real-scope .pj .panel{position:absolute; left:0; top:0; height:720px; background-size:cover; background-position:center; background-color:#59656a;}
  .real-scope .pj .ptitle{color:#fff; letter-spacing:-.01em;}
  .real-scope .pj .rule{position:absolute; height:1px; background:#2b2b2b; display:block;}
  .real-scope .pj .rule.red{background:#e2433f;} .real-scope .pj .rule.thin{background:#c8c8c8;}
  .real-scope .pj .vline{position:absolute; width:2px; background:#e2433f; display:block;}
  .real-scope .pj .logo{position:absolute; height:auto; max-width:none; display:block;}
  .real-scope .pj .pill-o{position:absolute; border:1.5px solid #d3262a; border-radius:999px; background:transparent;}
  .real-scope .pj .pilltxt{white-space:nowrap;}
  .real-scope .pj .card{position:absolute; background-size:cover; background-position:center; background-color:#59656a; overflow:hidden; box-shadow:0 14px 16px -12px rgba(0,0,0,.45);}
  .real-scope .pj .card .rt{position:absolute; text-align:right; white-space:nowrap;}
  .real-scope .pj .card .rt > span{display:block;}
  .real-scope .pj .card .kv{position:absolute; display:grid; grid-template-columns:auto auto; column-gap:1.2em; white-space:nowrap; align-items:center;}
  .real-scope .pj .card .arw{position:absolute; height:auto; display:block; filter:drop-shadow(0 1px 2px rgba(0,0,0,.25));}
  .real-scope .pj .card .cw{color:#fff; text-shadow:0 1px 3px rgba(0,0,0,.35);}
  .real-scope .pj .card .pill-i{position:absolute; display:block; max-width:none;}
  .real-scope .pj .card .pill-t{position:absolute; display:block; background:#fff; color:#111; border-radius:999px; text-align:center; white-space:nowrap; font-weight:500; overflow:hidden;}
  .real-scope .pj-b .nm{color:#111;}
  .real-scope .pj-e{background:#f4f3f5;}
  .real-scope .pj .ecard{position:absolute; background:#fff; display:block;}
  .real-scope .pj .enum{font-weight:300; color:#111;} .real-scope .pj .etitle{font-weight:400; color:#111; letter-spacing:-.005em;}
  .real-scope .pj .edesc{font-weight:400;}
  .real-scope .pj .ph.rnd2{border-radius:10px;}
  .real-scope .pj .obar{position:absolute; background:#d9d9d9; display:block;}
  .real-scope .pj .ovline{position:absolute; width:1px; background:#d8d8d8; display:block;}
"""

if __name__ == "__main__":
    ids = sys.argv[1:] or list(SLIDES)
    res = {}
    for sid in ids:
        print(sid)
        res[sid] = build(sid)
    old = json.load(open("slides.json")) if os.path.exists("slides.json") else {}
    old.update(res)
    json.dump(old, open("slides.json", "w"))
    # preview page
    def prev(sid):
        h = old[sid].replace("{{LOGO}}", "../logo.jpg")
        h = re.sub(r"\{\{IMG:([^}]+)\}\}", lambda m: "assets/" + m.group(1), h)
        return '<div class="real-scope" style="width:1280px;height:720px;margin:0 0 6px;position:relative;">%s</div>' % h
    page = "<!doctype html><meta charset=utf-8><style>body{margin:0;background:#888;font-family:Arial} .real-scope{--font-slide:Raleway,Montserrat,Arial,sans-serif}%s</style>%s" % (CSS, "".join(prev(i) for i in ids))
    os.makedirs("preview", exist_ok=True)
    open("preview/index.html", "w", encoding="utf-8").write(page)
