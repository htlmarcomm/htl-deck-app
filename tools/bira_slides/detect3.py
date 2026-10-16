import os, json, sys
import cv2
import numpy as np

SRC = "src"
# family: p = plain photos (no shadow), s = side panel + plain photos, c = rounded cards with shadow
CFG = {
    "01": ("s", "rows"), "04": ("s", "rows"), "05": ("s", "rows"), "06": ("s", "rows"), "16": ("s", "rows"),
    "02": ("c", "rows"), "03": ("c", "rows"), "07": ("c", "rows"), "08": ("c", "rows"), "13": ("c", "rows"),
    "14": ("c", "rows"), "15": ("c", "rows"), "17": ("c", "rows"), "18": ("c", "rows"), "19": ("c", "rows"),
    "20": ("c", "cols"), "21": ("c", "rows"), "22": ("c", "rows"), "23": ("c", "cols"), "24": ("c", "cols"),
    "26": ("s", "rows"), "27": ("s", "rows"), "28": ("s", "rows"),
    "09": ("p", "rows"), "10": ("p", "rows"), "11": ("p", "rows"), "12": ("p", "rows"), "25": ("p", "rows"),
}


def runs(profile, thr, min_len):
    out, s = [], None
    for i, v in enumerate(profile):
        if v > thr and s is None: s = i
        elif v <= thr and s is not None:
            if i - s >= min_len: out.append((s, i))
            s = None
    if s is not None and len(profile) - s >= min_len: out.append((s, len(profile)))
    return out


def split(mask, box, order, min_w, min_h):
    x0, y0, x1, y1 = box
    sub = mask[y0:y1, x0:x1]
    res = []
    if order == "rows":
        for (a, b) in runs(sub.mean(axis=1), 0.04, min_h):
            band = sub[a:b]
            for (c, d) in runs(band.mean(axis=0), 0.04, min_w):
                res.append([x0 + c, y0 + a, x0 + d, y0 + b])
    else:
        for (c, d) in runs(sub.mean(axis=0), 0.04, min_w):
            col = sub[:, c:d]
            for (a, b) in runs(col.mean(axis=1), 0.04, min_h):
                res.append([x0 + c, y0 + a, x0 + d, y0 + b])
    return res


def trim(mask, b, frac=0.5):
    """tighten a box to where the mask coverage reaches `frac` of the median coverage"""
    x0, y0, x1, y1 = b
    sub = mask[y0:y1, x0:x1].astype(float)
    cols = sub.mean(axis=0); rows = sub.mean(axis=1)
    cm = np.median(cols[cols > 0]) if (cols > 0).any() else 1
    rm = np.median(rows[rows > 0]) if (rows > 0).any() else 1
    xs = np.where(cols >= frac * cm)[0]; ys = np.where(rows >= frac * rm)[0]
    if len(xs) == 0 or len(ys) == 0: return b
    return [x0 + int(xs[0]), y0 + int(ys[0]), x0 + int(xs[-1]) + 1, y0 + int(ys[-1]) + 1]


def detect(f):
    key = f[:2]
    fam, order = CFG[key]
    im = cv2.imread(os.path.join(SRC, f))
    h, w = im.shape[:2]
    diff = 255 - im.min(axis=2)
    if fam == "p":
        m = (diff > 12).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    elif fam == "s":
        m = (diff > 60).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    else:
        m = (diff > 92).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    boxes = []
    min_w, min_h = int(0.10 * w), int(0.10 * h)
    for i in range(1, n):
        x, y, bw, bh, a = st[i]
        if bw < min_w or bh < min_h or a < 0.01 * w * h: continue
        if fam == "c":
            boxes.extend(split(m, [x, y, x + bw, y + bh], order, min_w, min_h))
        else:
            boxes.append([x, y, x + bw, y + bh])
    boxes = [trim(m, b) for b in boxes]
    boxes.sort(key=lambda b: (round(b[1] / (h * 0.15)), b[0]))
    return im, boxes


if __name__ == "__main__":
    os.makedirs("det3", exist_ok=True)
    allb = {}
    for f in sorted(os.listdir(SRC)):
        if not f.endswith(".png"): continue
        im, boxes = detect(f)
        allb[f] = [[int(v) for v in b] for b in boxes]
        vis = im.copy()
        for j, (x0, y0, x1, y1) in enumerate(boxes):
            cv2.rectangle(vis, (x0, y0), (x1, y1), (0, 0, 255), 4)
            cv2.putText(vis, str(j), (x0 + 12, y0 + 52), cv2.FONT_HERSHEY_SIMPLEX, 1.7, (0, 0, 255), 4)
        H, W = im.shape[:2]
        cv2.imwrite("det3/" + f, cv2.resize(vis, (800, int(800 * H / W))))
        print(f[:2], W, H, len(boxes), end=" | ")
    json.dump(allb, open("boxes3.json", "w"))
    import numpy as np
    fs = sorted(os.listdir("det3"))
    for s in range(0, len(fs), 4):
        ims = [cv2.resize(cv2.imread("det3/" + f), (700, 394)) for f in fs[s:s + 4]]
        while len(ims) < 4: ims.append(np.full((394, 700, 3), 255, np.uint8))
        cv2.imwrite("sheet3_%d.png" % (s // 4), np.vstack([np.hstack(ims[:2]), np.hstack(ims[2:])]))
