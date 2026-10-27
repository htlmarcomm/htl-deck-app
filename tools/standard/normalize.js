/* Slide Standard normaliser for the absolutely-positioned slides (".pj" family, 1280 x 720).
   Runs in a browser page that has the app's CSS + tools/standard/tokens.css loaded.
   Keeps each slide's design; standardises the details:
     - heading -> .ss-head (Raleway, 50 pt, caps, at 54/54 pt), bold/light words kept
     - every text size -> one of: sub / body / detail / caption (no inline font sizes)
     - stacked lines -> one text block spaced by the style's line height; centred copy -> left aligned
     - content moved/scaled into the safe area under the heading; photo/card edges snapped to the 12 columns
     - HTL logo -> bottom margin with the page number
   window.ssNormalize(section, {logo}) -> {html, flags[]} */
(function () {
  "use strict";
  var M = { l: 72, r: 1208, t: 72, b: 656, gap: 40, col: 72.667, pitch: 96.667 };
  var colStart = function (i) { return M.l + i * M.pitch; };
  var colEnd = function (i) { return M.l + i * M.pitch + M.col; };
  function snapStart(x) { var i = Math.round((x - M.l) / M.pitch); i = Math.max(0, Math.min(11, i)); return { i: i, x: colStart(i) }; }
  function snapEnd(x) { var i = Math.round((x - M.l - M.col) / M.pitch); i = Math.max(0, Math.min(11, i)); return { i: i, x: colEnd(i) }; }

  function sizeClass(px) {
    if (px < 15) return "t-caption";
    if (px < 22.3) return "t-detail";
    if (px < 30.4) return "t-body";
    return "t-sub";
  }
  function weightClass(el) {
    var w = parseInt(getComputedStyle(el).fontWeight, 10) || 400;
    return w >= 600 ? "is-b" : w <= 330 ? "is-l" : "is-r";
  }
  function num(v) { return parseFloat(v) || 0; }

  window.ssNormalize = function (sec, opts) {
    var flags = [];
    var S = sec.getBoundingClientRect();
    var rel = function (el) { var r = el.getBoundingClientRect(); return { x: r.left - S.left, y: r.top - S.top, w: r.width, h: r.height, r: r.right - S.left, b: r.bottom - S.top }; };
    var kids = function (sel) { return Array.prototype.filter.call(sec.children, function (e) { return e.matches(sel); }); };

    // ---- 1. HTL logo(s) -> footer
    Array.prototype.forEach.call(sec.querySelectorAll("img"), function (im) {
      if (opts.logo && im.getAttribute("src") === opts.logo && im.parentNode === sec) im.remove();
    });

    // ---- 2. heading
    var panel = kids(".pj-panel")[0] || null;
    var titleEls = kids(".pj-ttl, .pj-ptitle").sort(function (a, b) { return rel(a).y - rel(b).y; });
    var lines = [];
    titleEls.forEach(function (t) {
      var parts = [];
      var segs = t.classList.contains("pj-ttl") ? Array.prototype.slice.call(t.children) : [t];
      if (!segs.length) segs = [t];
      segs.forEach(function (sp) {
        var cls = [weightClass(sp)];
        if (sp.classList.contains("pj-red")) cls.push("pj-red");
        parts.push('<span class="' + cls.join(" ") + '">' + sp.innerHTML.replace(/<[^>]+>/g, "") + "</span>");
      });
      lines.push(parts.join(""));
      t.remove();
    });
    var head = document.createElement("h2");
    head.className = "ss-head" + (panel ? " pj-ptitle" : "");
    head.innerHTML = lines.join("<br>");
    sec.insertBefore(head, sec.firstChild);
    var hr = rel(head), fitSize = "";
    if (panel) {
      var room = rel(panel).r - M.l - 16;
      if (hr.w > room) {
        var k = room / hr.w;
        head.classList.add("ss-head--fit");
        fitSize = (66.667 * k).toFixed(2) + "px";
        head.style.fontSize = fitSize;
        flags.push("heading reduced to " + Math.round(50 * k) + " pt to fit inside the photo panel (standard 50 pt is wider than the panel)");
        hr = rel(head);
      }
    }
    var contentTop = M.t + hr.h + M.gap;

    // ---- size groups: text of (nearly) the same original size always gets the same style
    var allSizes = Array.prototype.filter.call(sec.querySelectorAll("*"), function (e) {
      return e !== head && !head.contains(e) && Array.prototype.some.call(e.childNodes, function (n) { return n.nodeType === 3 && n.textContent.trim(); });
    }).map(function (e) { return num(getComputedStyle(e).fontSize); }).sort(function (a, b) { return a - b; });
    var groups = [];
    allSizes.forEach(function (v) { var g = groups[groups.length - 1]; if (g && v <= g[0] * 1.3) g.push(v); else groups.push([v]); });
    var sizeOf = function (px) {
      for (var i = 0; i < groups.length; i++) { var g = groups[i]; if (px >= g[0] - 0.01 && px <= g[g.length - 1] + 0.01) return sizeClass(g[Math.floor(g.length / 2)]); }
      return sizeClass(px);
    };

    // ---- 3. text sizes inside cards / composite blocks (keep their structure, snap sizes, left-align)
    Array.prototype.forEach.call(sec.querySelectorAll(".pj-rt, .pj-kv"), function (b) {
      var fs = num(getComputedStyle(b).fontSize);
      var cls = sizeOf(fs);
      b.style.fontSize = ""; b.style.lineHeight = "";
      b.classList.add(cls);
      // .pj-rt labels on photo cards stay right-aligned: the client logo is printed at the photo's bottom-left
    });
    Array.prototype.forEach.call(sec.querySelectorAll(".pj-pill-t"), function (b) {
      b.classList.add(sizeOf(num(getComputedStyle(b).fontSize))); b.style.fontSize = ""; b.style.lineHeight = "";
    });

    // ---- 4. free text lines -> blocks
    var pills = kids(".pj-pill-o").map(rel);
    var texts = kids(".pj-t, p.pj-t, .pj-jl").filter(function (t) { return t.textContent.trim(); });
    var items = texts.map(function (t) {
      var r = rel(t), cs = getComputedStyle(t);
      var centered = /translateX\(-50%\)/.test(t.getAttribute("style") || "") || cs.textAlign === "center";
      var inPill = pills.some(function (p) { return r.x + r.w / 2 > p.x && r.x + r.w / 2 < p.x + p.w && r.y + r.h / 2 > p.y && r.y + r.h / 2 < p.y + p.h; });
      return { el: t, r: r, fs: num(cs.fontSize), centered: centered, inPill: inPill, cx: r.x + r.w / 2, color: t.style.color, w: weightClass(t) };
    }).sort(function (a, b) { return a.r.y - b.r.y || a.r.x - b.r.x; });
    var blocks = [];
    var boxesSel0 = ".pj-ph, .pj-card, .pj-ecard, .pj-jcard, .pj-jill";
    var photoRects = Array.prototype.filter.call(sec.children, function (e) { return e.matches(boxesSel0); }).map(rel);
    var photoUnder = function (it) {   // the photo a centred caption sits under
      return photoRects.filter(function (r) { return r.w > 60 && it.cx > r.x && it.cx < r.r && r.b <= it.r.y + 6; }).sort(function (a, b) { return b.b - a.b; })[0] || null;
    };
    items.forEach(function (it) {
      if (it.inPill) { it.el.classList.add(sizeOf(it.fs)); it.el.style.fontSize = ""; return; }
      var ph = it.centered ? photoUnder(it) : null;
      var anchor = it.centered ? (ph ? ph.x : it.cx) : it.r.x;
      var bl = null;
      for (var i = blocks.length - 1; i >= 0; i--) {
        var b = blocks[i], last = b.items[b.items.length - 1];
        var same = b.centered === it.centered && Math.abs(b.anchor - anchor) < 6;
        var gap = it.r.y - last.r.b;
        if (same && gap > -2 && gap < Math.max(last.fs, it.fs) * 1.25) { bl = b; break; }
      }
      if (!bl) { bl = { items: [], centered: it.centered, anchor: anchor }; blocks.push(bl); }
      bl.items.push(it);
    });
    var boxesSel = ".pj-ph, .pj-card, .pj-ecard, .pj-jcard, .pj-jill, .pj-pill-o, .pj-rule, .pj-vline, .pj-jline, .pj-obar, .pj-ovline, .pj-logo, img, svg, .pj-ill, .pj-map";
    var boxes = Array.prototype.filter.call(sec.children, function (e) { return e !== head && e !== panel && e.matches(boxesSel) && !e.classList.contains("ss-foot"); });
    blocks.forEach(function (b) {
      var x0 = Math.min.apply(null, b.items.map(function (i) { return i.r.x; }));
      var w = Math.max.apply(null, b.items.map(function (i) { return i.r.w; }));
      var y0 = b.items[0].r.y;
      if (b.centered) {
        // a caption centred under a photo: align it to the photo's left edge instead
        var ph = boxes.filter(function (e) { return e.matches(boxesSel0); }).map(function (e) { return { e: e, r: rel(e) }; }).filter(function (o) {
          return o.r.w > 60 && b.anchor > o.r.x && b.anchor < o.r.r && o.r.b <= y0 + 6;
        }).sort(function (a, c) { return c.r.b - a.r.b; })[0];
        x0 = ph ? ph.r.x : b.anchor - w / 2;
        if (ph) b.photo = ph.e;
      }
      var div = document.createElement("div");
      div.className = "ss-tb";
      div.style.left = x0.toFixed(1) + "px"; div.style.top = y0.toFixed(1) + "px";
      b.items.forEach(function (i) {
        var p = document.createElement("p");
        p.className = [sizeOf(i.fs), i.w].concat(Array.prototype.filter.call(i.el.classList, function (c) { return !/^(pj-t|pj-jl|pj-pilltxt|ss-tb)$/.test(c); })).join(" ");
        if (i.color) p.style.color = i.color;
        p.innerHTML = i.el.innerHTML;
        div.appendChild(p);
        i.el.remove();
      });
      sec.appendChild(div);
      b.div = div;
      if (b.photo) div._photo = b.photo;
    });

    // ---- 5. fit everything into the safe area under the heading
    var pillEls = kids(".pj-pill-o"), badgeLow = 0;
    var pillTexts = Array.prototype.filter.call(sec.children, function (e) { return e.classList.contains("pj-t") && pills.length && e.classList.contains("pj-pilltxt"); });
    pillEls.forEach(function (pe, n) {
      var r = rel(pe), nx = M.r - r.w, ny = M.t;
      pillTexts.forEach(function (t) { var tr = rel(t); if (tr.x + tr.w / 2 > r.x && tr.x + tr.w / 2 < r.r) { t.style.left = (nx + r.w / 2).toFixed(1) + "px"; t.style.top = (ny + (tr.y - r.y)).toFixed(1) + "px"; t.setAttribute("data-ss-fixed", "1"); } });
      if (nx < M.l + hr.w + 24) {   // would touch the heading: drop it just under the heading, still on the right margin
        var dy = hr.h + 8;
        ny += dy;
        pillTexts.forEach(function (t) { if (t.getAttribute("data-ss-fixed")) t.style.top = (num(t.style.top) + dy).toFixed(1) + "px"; });
        contentTop = Math.max(contentTop, ny + r.h + 24);
        badgeLow = ny + r.h + 24;
      }
      pe.style.left = nx.toFixed(1) + "px"; pe.style.top = ny.toFixed(1) + "px"; pe.setAttribute("data-ss-fixed", "1");
    });
    var movable = Array.prototype.filter.call(sec.children, function (e) { return e !== head && e !== panel && !e.hasAttribute("data-ss-fixed") && !e.classList.contains("ss-foot") && !/^(STYLE|SCRIPT)$/.test(e.tagName); });
    var rects0 = movable.map(function (e) { return { e: e, r: rel(e) }; }).filter(function (o) { return o.r.w > 0 && o.r.h > 0; });
    var rects = rects0.filter(function (o) { return !o.e._photo; });   // captions follow their photo afterwards
    if (!rects.length) return finish();
    var bx0 = Math.min.apply(null, rects.map(function (o) { return o.r.x; }));
    var by0 = Math.min.apply(null, rects.map(function (o) { return o.r.y; }));
    var bx1 = Math.max.apply(null, rects.map(function (o) { return o.r.r; }));
    var by1 = Math.max.apply(null, rects0.map(function (o) { return o.r.b; }));
    var left = panel ? Math.max(M.l, rel(panel).r + 24) : M.l;
    var zone = badgeLow ? { x: M.l, y: M.t, r: M.r, b: badgeLow } : { x: M.l, y: M.t, r: M.l + hr.w + 24, b: M.t + hr.h + M.gap };
    var isText = function (e) { return e.classList.contains("ss-tb") || e.matches(".pj-t"); };
    function plan(top, allowShift) {
      var s = Math.min(1, (M.r - left) / (bx1 - bx0), (M.b - top) / (by1 - by0));
      for (var it = 0; it < 40; it++) {   // text keeps its size, so check the real extent at this scale
        var bot = Math.max.apply(null, rects0.map(function (o) { return top + (o.r.y - by0) * s + (isText(o.e) ? o.r.h : o.r.h * s); }));
        var rgt = Math.max.apply(null, rects.map(function (o) { return left + (o.r.x - bx0) * s + (isText(o.e) ? o.r.w : o.r.w * s); }));
        if ((by0 >= top && by0 + (bot - top) <= M.b || bot <= M.b) && (rgt <= M.r || bx0 + (rgt - left) <= M.r)) break;
        s -= 0.01;
      }
      var ox = (bx0 < left || bx0 + (bx1 - bx0) * s > M.r) ? left : bx0;
      var oy = (by0 < top || by0 + (by1 - by0) * s > M.b) ? top : by0;
      var map = function (r) { return { x: ox + (r.x - bx0) * s, y: oy + (r.y - by0) * s, r: ox + (r.r - bx0) * s, b: oy + (r.b - by0) * s }; };
      var hits = function (dx) { return rects.filter(function (o) { var m = map(o.r); return m.x + dx < zone.r && m.r + dx > zone.x && m.y < zone.b && m.b > zone.y; }); };
      var dx = 0, h = hits(0);
      if (h.length && allowShift) {
        var need = Math.max.apply(null, h.map(function (o) { return zone.r - map(o.r).x; }));
        var room = M.r - map({ x: bx1, y: 0, r: bx1, b: 0 }).r;
        if (need <= room) { dx = need; h = hits(dx); }
      }
      return { s: s, ox: ox + dx, oy: oy, ok: !h.length };
    }
    var P = plan(M.t, true);
    if (!P.ok) P = plan(contentTop, false);
    var s = P.s, ox = P.ox, oy = P.oy;
    if (s < 0.82) flags.push("content had to shrink to " + Math.round(s * 100) + "% to fit beside/under the heading (photos and positions only; text sizes kept)");
    var place = function (o) {
      var e = o.e, r = o.r;
      var nx = ox + (r.x - bx0) * s, ny = oy + (r.y - by0) * s;
      e.style.right = ""; e.style.bottom = "";
      e.style.left = nx.toFixed(1) + "px"; e.style.top = ny.toFixed(1) + "px";
      if (e.style.transform && /translateX/.test(e.style.transform)) { e.style.left = (nx + r.w / 2).toFixed(1) + "px"; }
      if (!isText(e)) {
        if (r.w > 3) e.style.width = (r.w * s).toFixed(1) + "px";
        if (r.h > 3) e.style.height = (r.h * s).toFixed(1) + "px";
      }
    };
    rects0.forEach(place);

    // ---- 6. snap photo/card edges to the column grid; text that sat on a photo edge follows it
    var moved = [];
    rects.forEach(function (o) {
      var e = o.e;
      if (!e.matches(".pj-ph, .pj-card, .pj-ecard, .pj-jcard, .pj-rule, .pj-obar")) return;
      var r = rel(e);
      if (r.w < 40) return;
      var a = snapStart(r.x), z = snapEnd(r.r);
      if (z.i < a.i) z = { i: a.i, x: colEnd(a.i) };
      // only snap when it keeps the box (almost) the same size, so rows of equal cards stay equal
      if (Math.abs((z.x - a.x) - r.w) > Math.max(10, r.w * 0.06) || Math.abs(a.x - r.x) > 30) return;
      moved.push({ from: r.x, to: a.x, y0: r.y, y1: r.b });
      e.style.left = a.x.toFixed(1) + "px";
      e.style.width = (z.x - a.x).toFixed(1) + "px";
    });
    Array.prototype.forEach.call(sec.querySelectorAll(":scope > .ss-tb"), function (d) {
      var r = rel(d);
      var hit = moved.filter(function (m) { return Math.abs(m.from - r.x) < 8; })[0];
      if (hit) d.style.left = hit.to.toFixed(1) + "px";
      else { var sn = snapStart(r.x); if (Math.abs(sn.x - r.x) <= 12) d.style.left = sn.x.toFixed(1) + "px"; }
    });

    // captions under photos: start at the photo's left edge; a caption wider than its photo stays centred on it
    Array.prototype.forEach.call(sec.querySelectorAll(":scope > .ss-tb"), function (d) {
      if (!d._photo) return;
      var pr = rel(d._photo), w = rel(d).w;
      if (pr.w >= 180) {   // large photo (project cards): caption starts on the photo's left edge
        d.style.left = (w <= pr.w + 2 ? pr.x : pr.x + pr.w / 2 - w / 2).toFixed(1) + "px";
      } else {             // small photo (people, logos): caption centred under it, wrapping to the photo's column
        var cw = pr.w + 20;
        d.classList.add("ss-tb--under");
        d.style.left = (pr.x - 10).toFixed(1) + "px";
        d.style.width = cw.toFixed(1) + "px";
      }
    });
    return finish();

    function finish() {
      // footer
      var f = document.createElement("footer");
      f.className = "ss-foot";
      f.innerHTML = '<span class="ss-pn"></span>' + (opts.logo ? '<img class="ss-logo" src="' + opts.logo + '" alt="HTL">' : "");
      sec.appendChild(f);
      // checks: inside the safe area, no text overlapping other text
      var tbs = Array.prototype.map.call(sec.querySelectorAll(":scope > .ss-tb, .pj-rt, .pj-kv"), function (e) { return { e: e, r: rel(e) }; });
      tbs.forEach(function (o) {
        if (o.r.b > M.b + 1 || o.r.r > M.r + 1 || o.r.x < M.l - 1) flags.push('text outside the safe area: "' + o.e.textContent.trim().slice(0, 40) + '"');
      });
      for (var i = 0; i < tbs.length; i++) for (var j = i + 1; j < tbs.length; j++) {
        var a = tbs[i].r, b = tbs[j].r;
        if (a.x < b.r - 1 && b.x < a.r - 1 && a.y < b.b - 1 && b.y < a.b - 1 && !tbs[i].e.contains(tbs[j].e) && !tbs[j].e.contains(tbs[i].e))
          flags.push('text overlaps: "' + tbs[i].e.textContent.trim().slice(0, 25) + '" / "' + tbs[j].e.textContent.trim().slice(0, 25) + '"');
      }
      // no inline type sizes left
      Array.prototype.forEach.call(sec.querySelectorAll("[style]"), function (e) {
        e.style.fontSize = ""; e.style.lineHeight = ""; e.style.fontWeight = "";
        if (!e.getAttribute("style").trim()) e.removeAttribute("style");
      });
      if (fitSize) head.style.fontSize = fitSize; // flagged above
      return { html: sec.outerHTML, flags: flags };
    }
  };
})();
