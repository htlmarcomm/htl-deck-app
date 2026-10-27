/* Slide Standard normaliser for the flow-layout slides (the older blocks: about us, why HTL, quality ...).
   Keeps each slide's own layout. Standardises:
     - heading -> Raleway caps, 50 pt, top-left of the safe area (bold/light words kept);
       inside a photo panel it stays in the panel and is fitted to the panel width (flagged)
     - every text size -> sub / body / detail / caption (sizes grouped so equal text stays equal)
     - the rest of the slide moves as ONE block (its internal layout untouched) to sit inside the
       safe area, beside or under the heading; only if it cannot fit is it scaled (flagged)
     - centred body copy -> left aligned; footer (page number + logo) in the bottom margin
   Covers (title, thank you) and slides without a single heading (vision/mission/values) keep their
   layout: only text sizes are standardised, and they are listed as exceptions.
   window.ssNormalizeFlow(section, {logo, key}) -> {html, flags[]} */
(function () {
  "use strict";
  var W = 1280, H = 720, M = { l: 72, r: 1208, t: 72, b: 656, gap: 40 };
  var COVERS = { title_page: 1, thank_you: 1 }, NO_HEAD = { mission_vision_values: 1 };
  function num(v) { return parseFloat(v) || 0; }
  function sizeClass(px) { return px < 15 ? "t-caption" : px < 22.3 ? "t-detail" : px < 30.4 ? "t-body" : "t-sub"; }
  function weightClass(el) { var w = parseInt(getComputedStyle(el).fontWeight, 10) || 400; return w >= 600 ? "is-b" : w <= 330 ? "is-l" : "is-r"; }

  window.ssNormalizeFlow = function (sec, opts) {
    var flags = [], key = opts.key || sec.getAttribute("data-block") || "";
    var S = function () { return sec.getBoundingClientRect(); };
    var rel = function (el) { var s = S(), r = el.getBoundingClientRect(); return { x: r.left - s.left, y: r.top - s.top, w: r.width, h: r.height, r: r.right - s.left, b: r.bottom - s.top }; };
    var leafText = function (e) { return Array.prototype.some.call(e.childNodes, function (n) { return n.nodeType === 3 && n.textContent.trim(); }); };
    var size = function (e) { return num(getComputedStyle(e).fontSize); };
    var cover = !!COVERS[key], noHead = !!NO_HEAD[key];

    // ---- heading
    var head = null;
    if (!cover && !noHead) {
      var cands = Array.prototype.filter.call(sec.querySelectorAll("h1, h2, [class*='title'], [class*='heading']"), function (e) {
        return e.textContent.trim() && rel(e).w > 0 && !e.closest("svg") && !e.querySelector("h1, h2, img, svg, p, li");
      });
      head = cands.sort(function (a, b) { return size(b) - size(a); })[0] || null;
    }

    // ---- text sizes: group equal sizes, decide each element's style before anything changes
    var coverTitlePx = 0;
    if (cover) Array.prototype.forEach.call(sec.querySelectorAll("*"), function (e) { if (leafText(e)) coverTitlePx = Math.max(coverTitlePx, size(e)); });
    var texts = Array.prototype.filter.call(sec.querySelectorAll("*"), function (e) {
      return leafText(e) && (!head || !head.contains(e)) && !e.closest("svg") && !(cover && (e.closest("h1, h2") || size(e) >= coverTitlePx * 0.8));
    });
    var sizes = texts.map(size).sort(function (a, b) { return a - b; }), groups = [];
    sizes.forEach(function (v) { var g = groups[groups.length - 1]; if (g && v <= g[0] * 1.3) g.push(v); else groups.push([v]); });
    var sizeOf = function (px) {
      for (var i = 0; i < groups.length; i++) { var g = groups[i]; if (px >= g[0] - 0.01 && px <= g[g.length - 1] + 0.01) return sizeClass(g[Math.floor(g.length / 2)]); }
      return sizeClass(px);
    };
    var plan = texts.map(function (e) {
      var cs = getComputedStyle(e);
      // centred copy that is a paragraph (not a short label in a card/circle) gets left-aligned
      var r = rel(e), centre = cs.textAlign === "center" && r.w >= 260 && e.textContent.trim().length > 40;
      return { e: e, cls: sizeOf(num(cs.fontSize)), center: centre };
    });

    // ---- panel: a tall narrow block (photo / dark panel) that holds the heading
    var panel = null;
    if (head) {
      for (var p = head.parentElement; p && p !== sec; p = p.parentElement) {
        var pr = rel(p);
        if (pr.w < W * 0.42 && pr.h > H * 0.8) { panel = p; break; }
      }
    }

    // ---- heading mode
    //  "band"   : heading becomes its own row at the top (default)
    //  "column" : heading sits in a side column with content beside it -> it stays in the layout and the whole
    //             slide shifts so the heading lands on the 54/54 pt corner
    //  "panel"  : heading inside a photo panel; panel too narrow for the standard spot -> keep its place and size
    var mode = "band", head0 = head ? rel(head) : null, headPx0 = 0;
    if (head) [head].concat(Array.prototype.slice.call(head.querySelectorAll("*"))).forEach(function (e) { if (leafText(e)) headPx0 = Math.max(headPx0, size(e)); });
    if (head && panel && rel(panel).r - M.l - 16 < head0.w) mode = "panel";
    else if (head && !panel && head0.w < W * 0.55) {
      var beside = Array.prototype.some.call(sec.querySelectorAll("img, svg, p, li, span, strong, div"), function (e) {
        if (head.contains(e) || e.contains(head)) return false;
        var r = rel(e);
        return r.w > 30 && r.h > 10 && r.x > head0.r + 40 && r.y < head0.b + 220 && r.b > head0.y;
      });
      if (beside) mode = "column";
    }

    // ---- apply sizes
    sec.classList.add("ss-flow2");
    plan.forEach(function (o) { o.e.classList.add(o.cls); o.e.style.fontSize = ""; o.e.style.lineHeight = ""; if (o.center) o.e.classList.add("ss-left"); });

    if (cover) {
      flags.push("cover slide: kept its own layout (heading stays where the design puts it); text sizes standardised");
      return done(false);
    }

    // ---- logo: drop the slide's own small HTL logo, the footer carries it
    Array.prototype.forEach.call(sec.querySelectorAll("img"), function (im) { if (opts.logo && im.getAttribute("src") === opts.logo) im.remove(); });

    // ---- heading to the standard spot
    var headBox = null;
    if (head && mode !== "band") {
      Array.prototype.forEach.call(head.querySelectorAll("*"), function (q) { q.classList.add(weightClass(q)); });
      if (!head.children.length) head.classList.add(weightClass(head));
      head.classList.add(mode === "panel" ? "ss-head-panel" : "ss-head-col");
      if (mode === "panel") {
        head.style.fontSize = headPx0.toFixed(2) + "px";
        flags.push("heading kept at " + Math.round(headPx0 * 0.75) + " pt in its photo panel (the panel is narrower than the standard heading)");
      } else {
        var hr2 = rel(head);
        var clash = Array.prototype.some.call(sec.querySelectorAll("img, p, span, li, strong, h3, h4, div"), function (e) {
          if (head.contains(e) || e.contains(head) || !e.getBoundingClientRect().width) return false;
          var r = rel(e);
          if (r.w > W * 0.6 && r.h > H * 0.6) return false;
          return r.x < hr2.r - 2 && r.r > hr2.x + 2 && r.y < hr2.b - 2 && r.b > hr2.y + 2;
        });
        if (clash) {
          head.style.fontSize = headPx0.toFixed(2) + "px";
          flags.push("heading kept at " + Math.round(headPx0 * 0.75) + " pt: at 50 pt it runs into the content under it in its column");
        }
      }
    } else if (head) {
      Array.prototype.forEach.call(head.querySelectorAll("*"), function (q) { q.classList.add(weightClass(q)); q.style.fontSize = ""; });
      if (!head.children.length) head.classList.add(weightClass(head));
      head.classList.add("ss-head");
      ["fontSize", "left", "top", "right", "bottom", "transform", "position", "width", "maxWidth"].forEach(function (k) { head.style[k] = ""; });
      sec.appendChild(head);
      var maxW = panel ? rel(panel).r - M.l - 16 : M.r - M.l;
      head.style.maxWidth = maxW + "px";
      // longest word must fit; otherwise the heading gets a smaller size (flagged) - never applies outside panels in practice
      var probe = document.createElement("span");
      probe.style.cssText = "position:absolute;visibility:hidden;white-space:nowrap";
      head.appendChild(probe);
      var widest = 0;
      head.textContent.split(/\s+/).forEach(function (w) { probe.textContent = w; widest = Math.max(widest, probe.getBoundingClientRect().width); });
      probe.remove();
      if (widest > maxW) {
        var k = maxW / widest;
        head.style.fontSize = (66.667 * k).toFixed(2) + "px";
        flags.push("heading reduced to " + Math.round(50 * k) + " pt to fit " + (panel ? "inside the photo panel" : "the slide width"));
      }
      headBox = rel(head);
      var lines = Math.round(headBox.h / (num(getComputedStyle(head).fontSize) * 1.05));
      if (lines > 2) flags.push("heading wraps to " + lines + " lines");
    } else {
      flags.push("no single slide heading (" + (noHead ? "three equal statements" : "none found") + "): heading position rule not applied");
    }

    // ---- move the rest as one block
    var cs = getComputedStyle(sec);
    var wrap = document.createElement("div");
    wrap.className = "ss-wrap";
    ["display", "flexDirection", "flexWrap", "alignItems", "justifyContent", "alignContent", "rowGap", "columnGap",
      "gridTemplateColumns", "gridTemplateRows", "gridTemplateAreas", "gridAutoFlow", "gridAutoRows", "gridAutoColumns",
      "paddingTop", "paddingRight", "paddingBottom", "paddingLeft", "textAlign", "placeItems"].forEach(function (k) { wrap.style[k] = cs[k]; });
    wrap.style.position = "absolute"; wrap.style.left = "0px"; wrap.style.top = "0px";
    wrap.style.width = W + "px"; wrap.style.height = H + "px"; wrap.style.boxSizing = "border-box";
    Array.prototype.slice.call(sec.childNodes).forEach(function (n) {
      if (n === head && mode === "band") return;
      if (n.nodeType === 1 && n.classList.contains("ss-foot")) return;
      wrap.appendChild(n);
    });
    sec.appendChild(wrap);
    if (head && mode === "band") sec.appendChild(head);

    // visible content box (ignores full-bleed backgrounds and the panel)
    var vis = Array.prototype.filter.call(wrap.querySelectorAll("*"), function (e) {
      if (panel && (e === panel || panel.contains(e) || e.contains(panel))) return false;
      var r = rel(e);
      if (r.w < 2 || r.h < 2) return false;
      if (r.w > W * 0.6 && r.h > H * 0.6) return false;       // backgrounds
      if (r.w >= W - 2 || r.h >= H - 2) return false;          // bleeds
      if (r.x <= 1 || r.y <= 1 || r.r >= W - 1 || r.b >= H - 1) return false;   // touches an edge: bleeds off the slide
      var leaf = !e.children.length || e.tagName === "IMG" || e.tagName === "svg" || e.tagName === "SVG";
      return leaf && getComputedStyle(e).visibility !== "hidden" && num(getComputedStyle(e).opacity) > 0.05;
    }).map(rel);
    if (vis.length) {
      var bx0 = Math.min.apply(null, vis.map(function (r) { return r.x; })), by0 = Math.min.apply(null, vis.map(function (r) { return r.y; }));
      var bx1 = Math.max.apply(null, vis.map(function (r) { return r.r; })), by1 = Math.max.apply(null, vis.map(function (r) { return r.b; }));
      var left = panel ? Math.max(M.l, rel(panel).r + 24) : M.l;
      var zone = headBox && !panel ? { x: M.l, y: M.t, r: headBox.r + 24, b: headBox.b + M.gap } : null;
      var under = headBox && !panel ? headBox.b + M.gap : M.t;
      var tryPlace = function (top) {
        var s = Math.min(1, (M.r - left) / (bx1 - bx0), (M.b - top) / (by1 - by0));
        var dx = (bx0 < left || bx0 + (bx1 - bx0) * s > M.r) ? left - bx0 : 0;
        var dy = (by0 < top || by0 + (by1 - by0) * s > M.b) ? top - by0 : 0;
        var hit = zone && vis.some(function (r) {
          var x = bx0 + dx + (r.x - bx0) * s, y = by0 + dy + (r.y - by0) * s, rr = x + r.w * s, bb = y + r.h * s;
          return x < zone.r && rr > zone.x && y < zone.b && bb > zone.y;
        });
        return { s: s, dx: dx, dy: dy, ok: !hit };
      };
      var P;
      if (mode === "column") {
        var hb = rel(head);
        var s0 = 1, ddx = M.l - hb.x, ddy = M.t - hb.y;
        var fx = (bx1 + ddx - bx0 > 0) ? Math.min(1, (M.r - (bx0 + ddx)) / (bx1 - bx0)) : 1;
        var fy = Math.min(1, (M.b - M.t) / (by1 - hb.y));
        s0 = Math.min(fx, fy, (M.r - M.l) / (bx1 - hb.x));
        wrap.style.transformOrigin = hb.x + "px " + hb.y + "px";
        P = { s: s0, dx: ddx, dy: ddy, ok: true };
      } else {
        P = tryPlace(M.t);
        if (!P.ok) P = tryPlace(under);
      }
      if (P.s < 0.995 || P.dx || P.dy) {
        if (mode !== "column") wrap.style.transformOrigin = bx0 + "px " + by0 + "px";
        wrap.style.transform = "translate(" + P.dx.toFixed(1) + "px," + P.dy.toFixed(1) + "px)" + (P.s < 0.995 ? " scale(" + P.s.toFixed(3) + ")" : "");
      }
      if (P.s < 0.995) flags.push("content scaled to " + Math.round(P.s * 100) + "% to fit the safe area" + (P.s < 0.9 ? " - text inside it is below its style size" : ""));
    }
    return done(true);

    function done(footer) {
      if (footer) {
        var f = document.createElement("footer");
        f.className = "ss-foot";
        f.innerHTML = '<span class="ss-pn"></span>' + (opts.logo ? '<img class="ss-logo" src="' + opts.logo + '" alt="HTL">' : "");
        sec.appendChild(f);
      }
      var out = 0;
      Array.prototype.forEach.call(sec.querySelectorAll("*"), function (e) {
        if (!leafText(e) || e.closest(".ss-foot") || e.closest("svg")) return;
        var r = rel(e);
        if (!r.w) return;
        if (r.b > M.b + 2 || r.r > M.r + 2 || r.x < M.l - 2 || r.y < (cover ? 0 : M.t - 30)) out++;
      });
      if (out && !cover) flags.push(out + " text element(s) outside the safe area");
      return { html: sec.outerHTML, flags: flags };
    }
  };
})();
