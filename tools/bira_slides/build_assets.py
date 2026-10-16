"""Cut photos / panels / logo pills out of the BIRA slide screenshots. Output: assets/<slide>/..., assets.json"""
import os, json, sys
import cv2
import numpy as np
from detect4 import detect as detect_boxes
from content import A as ACONTENT

SRC = "src"
OUT = "assets"
os.makedirs(OUT, exist_ok=True)

# slide id -> source file prefix, family
SLIDES = {
    "bfsi1": ("01", "B"), "bfsi2": ("02", "A"), "bfsi3": ("03", "A"),
    "cre1": ("04", "B"), "cre2": ("05", "B"),
    "dcnew": ("06", "B"), "dcmajor": ("07", "A"),
    "edu": ("08", "A"),
    "hosp2": ("09", "C"), "hosp3": ("10", "C"), "hosp4": ("11", "C"), "hosp1": ("12", "C"),
    "ind": ("13", "A"), "mfg": ("14", "A"),
    "res1": ("15", "A"), "res2": ("16", "B"),
    "pune3b": ("17", "A"), "pune3": ("18", "A"), "pune1": ("19", "A"),
    "south1": ("20", "A"), "south2": ("21", "A"), "south3": ("22", "A"), "south4": ("23", "A"), "south5": ("24", "A"),
    "vrv": ("25", "C"),
    "newwins": ("26", "B"), "mep1": ("27", "B"), "mep2": ("28", "B"),
}
# side panel width (source px) and title box (x0,y0,x1,y1) to paint out
PANEL = {
    "bfsi1": (470, (60, 160, 360, 292)), "cre1": (470, (60, 100, 350, 215)), "cre2": (470, (60, 160, 350, 292)),
    "dcnew": (620, (20, 50, 240, 140)), "res2": (615, (20, 65, 235, 118)),
    "newwins": (746, (55, 80, 325, 135)), "mep1": (468, (60, 165, 350, 292)), "mep2": (471, (60, 165, 350, 292)),
}
# photo boxes to force (source px) when detection is off: slide -> {index: [x0,y0,x1,y1]}
FORCE = {}


def f2key(prefix):
    for f in sorted(os.listdir(SRC)):
        if f.startswith(prefix + "_"):
            return f


def fix_narrow(boxes):
    ws = [b[2] - b[0] for b in boxes]
    hs = [b[3] - b[1] for b in boxes]
    mw, mh = float(np.median(ws)), float(np.median(hs))
    out = []
    for b in boxes:
        x0, y0, x1, y1 = b
        if (x1 - x0) < 0.88 * mw and (x1 - x0) > 0.45 * mw and abs((y1 - y0) - mh) < 0.2 * mh:
            x0 = x1 - int(mw)
        out.append([x0, y0, x1, y1])
    return out


def inpaint_text(crop, variant="right"):
    g = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    bg = cv2.medianBlur(g, 31)
    m = ((g > 200) & ((g.astype(int) - bg.astype(int)) > 40)).astype(np.uint8) * 255
    h, w = crop.shape[:2]
    # only the text zone: lower part (and not the left part for right-aligned text)
    zone = np.zeros_like(m)
    if variant == "right":
        zone[int(0.45 * h):, int(0.22 * w):] = 255
        zone[: int(0.40 * h), int(0.55 * w):] = 255   # a few cards carry a small label top-right
    else:
        zone[int(0.50 * h):, :] = 255
    m = cv2.bitwise_and(m, zone)
    # the arrow icon, top-right corner
    ax0, ax1 = int(w - 0.30 * w), int(w - 0.02 * w)
    ay0, ay1 = int(0.02 * h), int(0.30 * h)
    reg = crop[ay0:ay1, ax0:ax1].min(axis=2)
    am = (reg > 205).astype(np.uint8) * 255
    m[ay0:ay1, ax0:ax1] = np.maximum(m[ay0:ay1, ax0:ax1], am)
    m = cv2.dilate(m, np.ones((3, 3), np.uint8), iterations=2)
    return m


def find_pill(crop):
    """white rounded label in the lower part of an overlay card -> (x0,y0,x1,y1) or None"""
    h, w = crop.shape[:2]
    mn = crop.min(axis=2)
    m = (mn > 232).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    best = None
    for i in range(1, n):
        x, y, bw, bh, a = st[i]
        if not (24 <= bh <= 0.35 * h and 0.12 * w <= bw <= 0.75 * w): continue
        if y + bh / 2 < 0.35 * h: continue
        if x > 0.5 * w: continue
        fill = a / float(bw * bh)
        if fill < 0.72: continue
        if best is None or a > best[0]: best = (a, x, y, bw, bh)
    if not best:
        # second pass: duller / translucent labels
        m = (mn > 205).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(m)
        for i in range(1, n):
            x, y, bw, bh, a = st[i]
            if not (24 <= bh <= 0.2 * h and 0.12 * w <= bw <= 0.6 * w): continue
            if y + bh / 2 < 0.55 * h or x > 0.3 * w: continue
            if a / float(bw * bh) < 0.7: continue
            if best is None or a > best[0]: best = (a, x, y, bw, bh)
    if not best: return None
    _, x, y, bw, bh = best
    return [x, y, x + bw, y + bh]


def run(sid):
    prefix, fam = SLIDES[sid]
    f = f2key(prefix)
    im = cv2.imread(os.path.join(SRC, f))
    H, W = im.shape[:2]
    d = os.path.join(OUT, sid)
    os.makedirs(d, exist_ok=True)
    _, boxes = detect_boxes(f)
    info = {"src": f, "size": [W, H], "family": fam, "photos": []}
    if sid in PANEL:
        pw, tb = PANEL[sid]
        boxes = [b for b in boxes if not (b[0] == 0 and b[2] == pw)]
        panel = im[:, :pw].copy()
        x0, y0, x1, y1 = tb
        mask = np.zeros(panel.shape[:2], np.uint8)
        sub = panel[y0:y1, x0:x1]
        g = cv2.cvtColor(sub, cv2.COLOR_BGR2GRAY)
        bgm = cv2.medianBlur(g, 41)
        mm = ((g > 190) & ((g.astype(int) - bgm.astype(int)) > 35)).astype(np.uint8) * 255
        mm = cv2.dilate(mm, np.ones((3, 3), np.uint8), iterations=2)
        mask[y0:y1, x0:x1] = mm
        panel = cv2.inpaint(panel, mask, 5, cv2.INPAINT_TELEA)
        cv2.imwrite(os.path.join(d, "panel.jpg"), panel, [cv2.IMWRITE_JPEG_QUALITY, 90])
        info["panel"] = {"w": pw, "img": "panel.jpg"}
    if fam == "A":
        boxes = fix_narrow(boxes)
    for i, (x0, y0, x1, y1) in enumerate(boxes):
        x0 = max(0, x0); y0 = max(0, y0); x1 = min(W, x1); y1 = min(H, y1)
        crop = im[y0:y1, x0:x1].copy()
        rec = {"box": [int(x0), int(y0), int(x1), int(y1)]}
        if fam == "A":
            pill = find_pill(crop)
            spec = ACONTENT.get(sid, {}).get("cards", [])
            variant = "left" if (i < len(spec) and spec[i].get("left")) else "right"
            m = inpaint_text(crop, variant)
            if pill:
                px0, py0, px1, py1 = pill
                pm = np.zeros(crop.shape[:2], np.uint8)
                cv2.rectangle(pm, (px0 - 3, py0 - 3), (px1 + 3, py1 + 3), 255, -1)
                m = cv2.bitwise_or(m, pm)
                # pill cut-out with rounded alpha
                pc = crop[py0:py1, px0:px1].copy()
                alpha = np.zeros(pc.shape[:2], np.uint8)
                r = min(pc.shape[:2]) // 2
                cv2.rectangle(alpha, (r, 0), (pc.shape[1] - r, pc.shape[0]), 255, -1)
                cv2.circle(alpha, (r, pc.shape[0] // 2), r, 255, -1)
                cv2.circle(alpha, (pc.shape[1] - r, pc.shape[0] // 2), r, 255, -1)
                pcb = cv2.cvtColor(pc, cv2.COLOR_BGR2BGRA)
                pcb[:, :, 3] = alpha
                cv2.imwrite(os.path.join(d, "pill%d.png" % i), pcb)
                rec["pill"] = {"box": [int(v) for v in pill], "img": "pill%d.png" % i}
            clean = cv2.inpaint(crop, m, 3, cv2.INPAINT_TELEA)
            cv2.imwrite(os.path.join(d, "card%d.jpg" % i), clean, [cv2.IMWRITE_JPEG_QUALITY, 90])
            rec["img"] = "card%d.jpg" % i
        else:
            cv2.imwrite(os.path.join(d, "photo%d.jpg" % i), crop, [cv2.IMWRITE_JPEG_QUALITY, 92])
            rec["img"] = "photo%d.jpg" % i
        info["photos"].append(rec)
    # title / pill bbox for family A (dark+red pixels in the top band)
    if fam == "A":
        band = im[: int(0.2 * H)]
        hsv = cv2.cvtColor(band, cv2.COLOR_BGR2HSV)
        red = ((hsv[:, :, 0] < 10) | (hsv[:, :, 0] > 170)) & (hsv[:, :, 1] > 120) & (hsv[:, :, 2] > 120)
        dark = band.max(axis=2) < 90
        info["top"] = {}
        ys, xs = np.where(red)
        if len(xs):
            info["top"]["red"] = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
        ys, xs = np.where(dark)
        if len(xs):
            info["top"]["dark"] = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    return info


if __name__ == "__main__":
    ids = sys.argv[1:] or list(SLIDES)
    allinfo = json.load(open("assets.json")) if os.path.exists("assets.json") else {}
    for sid in ids:
        allinfo[sid] = run(sid)
        print(sid, len(allinfo[sid]["photos"]), "photos", sum(1 for p in allinfo[sid]["photos"] if p.get("pill")), "pills")
    json.dump(allinfo, open("assets.json", "w"))
