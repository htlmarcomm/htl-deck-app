import os, json
import cv2
import numpy as np
from detect3 import CFG, runs, split, trim

SRC = "src"
PANEL = {"01": 470, "04": 470, "05": 470, "06": 620, "16": 615, "26": 746, "27": 468, "28": 471}  # width of the left photo panel (image px)


def cluster(vals, tol):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    groups, cur = [], [order[0]]
    for i in order[1:]:
        if abs(vals[i] - np.mean([vals[j] for j in cur])) <= tol: cur.append(i)
        else: groups.append(cur); cur = [i]
    groups.append(cur)
    return groups


def repair(boxes, w, h):
    if len(boxes) < 2: return boxes
    bs = [list(b) for b in boxes]
    hs = [b[3] - b[1] for b in bs]
    ws = [b[2] - b[0] for b in bs]
    mh, mw = float(np.median(hs)), float(np.median(ws))
    # columns (x extents), ignoring boxes that are not about the usual width
    idx = [i for i in range(len(bs)) if 0.6 * mw < ws[i] < 1.5 * mw]
    for g in cluster([(bs[i][0] + bs[i][2]) / 2 for i in idx], 0.3 * mw):
        gi = [idx[j] for j in g]
        x0 = min(bs[i][0] for i in gi); x1 = max(bs[i][2] for i in gi)
        for i in gi: bs[i][0], bs[i][2] = x0, x1
    idx = [i for i in range(len(bs)) if 0.6 * mh < hs[i] < 1.5 * mh]
    for g in cluster([(bs[i][1] + bs[i][3]) / 2 for i in idx], 0.35 * mh):
        gi = [idx[j] for j in g]
        y0 = min(bs[i][1] for i in gi); y1 = max(bs[i][3] for i in gi)
        for i in gi: bs[i][1], bs[i][3] = y0, y1
    return bs


def detect(f):
    key = f[:2]
    fam, order = CFG[key]
    im = cv2.imread(os.path.join(SRC, f))
    h, w = im.shape[:2]
    diff = 255 - im.min(axis=2)
    min_w, min_h = int(0.07 * w), int(0.07 * h)
    boxes = []
    if key in PANEL:
        pw = PANEL[key]
        m = (diff > 12).astype(np.uint8)
        m[:, :pw + 12] = 0
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(m)
        for i in range(1, n):
            x, y, bw, bh, a = st[i]
            if bw < min_w or bh < min_h or a < 0.004 * w * h: continue
            boxes.append(trim(m, [x, y, x + bw, y + bh]))
        boxes.sort(key=lambda b: (round(b[1] / (h * 0.2)), b[0]))
        return im, [[0, 0, pw, h]] + boxes
    if fam == "p":
        m = (diff > 12).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(m)
        for i in range(1, n):
            x, y, bw, bh, a = st[i]
            if bw < 0.10 * w or bh < 0.10 * h or a < 0.01 * w * h: continue
            boxes.append(trim(m, [x, y, x + bw, y + bh]))
    else:
        m = (diff > 92).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(m)
        for i in range(1, n):
            x, y, bw, bh, a = st[i]
            if bw < 0.10 * w or bh < 0.10 * h or a < 0.01 * w * h: continue
            for b in split(m, [x, y, x + bw, y + bh], order, int(0.10 * w), int(0.10 * h)):
                boxes.append(trim(m, b))
        boxes = repair(boxes, w, h)
    boxes.sort(key=lambda b: (round(b[1] / (h * 0.15)), b[0]))
    return im, boxes


if __name__ == "__main__":
    os.makedirs("det4", exist_ok=True)
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
        cv2.imwrite("det4/" + f, cv2.resize(vis, (800, int(800 * H / W))))
        print(f[:2], len(boxes), end=" | ")
    json.dump(allb, open("boxes4.json", "w"))
    fs = sorted(os.listdir("det4"))
    for s in range(0, len(fs), 4):
        ims = [cv2.resize(cv2.imread("det4/" + f), (700, 394)) for f in fs[s:s + 4]]
        while len(ims) < 4: ims.append(np.full((394, 700, 3), 255, np.uint8))
        cv2.imwrite("sheet4_%d.png" % (s // 4), np.vstack([np.hstack(ims[:2]), np.hstack(ims[2:])]))
