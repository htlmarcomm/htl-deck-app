/* Slide Standard for the Capability deck screens, applied only when a screen is shown as a deck slide
   (capability-slides.html#slide=<id>, "embed" mode). The full interactive proposal is untouched.
   The frame is 1440 x 810 (= 960 x 540 pt), so 1 pt = 1.5 px here.
   Keeps each screen's design; standardises:
     - heading -> Raleway caps 50 pt at the 54 / 54 pt corner (bold/light words kept)
     - text sizes -> sub / body / detail / caption (equal sizes stay equal)
     - content nudged into the safe area (CSS "translate", so the screens' own animations still work)
     - centred paragraphs -> left aligned; footer: page number (its place in the deck) + HTL logo
   Covers / section dividers keep their layout (text sizes only). Anything that cannot meet the standard
   without redesigning the screen is left as designed and reported in window.__ssFlags. */
(function () {
  "use strict";
  var m = location.hash.match(/slide=([\w-]+)/);
  if (!m) return;
  var ID = m[1], W = 1440, H = 810, PT = 1.5;
  var M = { l: 54 * PT, r: W - 54 * PT, t: 54 * PT, b: H - 48 * PT, gap: 30 * PT };
  var COVERS = { "title-page": 1, intro: 1, "section-3": 1, "section-4": 1, "section-5": 1 };
  var LOGO = "/media/a18705566cb26d29.jpg";
  var flags = window.__ssFlags = [];

  var css = document.createElement("style");
  css.id = "ss-capability";
  css.textContent =
    "html.embed-slide{--pt:1.5px;--m-left:calc(54*var(--pt));--m-right:calc(54*var(--pt));--m-top:calc(54*var(--pt));--m-bottom:calc(48*var(--pt));" +
    "--font-heading:'Raleway','Montserrat','Segoe UI',Arial,sans-serif;--font-text:'TT Norms Pro','TT Norms','Segoe UI',Arial,sans-serif;" +
    "--fs-heading:calc(50*var(--pt));--lh-heading:1.05;--fs-sub:calc(26*var(--pt));--lh-sub:1.2;--fs-body:calc(20*var(--pt));--lh-body:1.4;" +
    "--fs-detail:calc(14*var(--pt));--lh-detail:1.4;--fs-caption:calc(9*var(--pt));--lh-caption:1.3;--logo-h:calc(14*var(--pt));}" +
    "html.embed-slide .ss-c-head{font-family:var(--font-heading)!important;font-size:var(--fs-heading)!important;line-height:var(--lh-heading)!important;text-transform:uppercase!important;letter-spacing:0!important;text-align:left!important;}" +
    "html.embed-slide .ss-c-head *{font-family:inherit!important;font-size:inherit!important;line-height:inherit!important;letter-spacing:0!important;}" +
    "html.embed-slide .ss-c-head.ss-c-keep{font-size:var(--ss-keep)!important;}" +
    "html.embed-slide .t-sub{font-size:var(--fs-sub)!important;line-height:var(--lh-sub)!important;}" +
    "html.embed-slide .t-body{font-size:var(--fs-body)!important;line-height:var(--lh-body)!important;}" +
    "html.embed-slide .t-detail{font-size:var(--fs-detail)!important;line-height:var(--lh-detail)!important;}" +
    "html.embed-slide .t-caption{font-size:var(--fs-caption)!important;line-height:var(--lh-caption)!important;}" +
    "html.embed-slide .ss-left{text-align:left!important;}" +
    "html.embed-slide .ss-measure, html.embed-slide .ss-measure *{transition:none!important;animation:none!important;}" +
    "html.embed-slide .ss-foot{position:fixed;left:var(--m-left);right:var(--m-right);bottom:0;height:var(--m-bottom);display:flex;align-items:center;justify-content:space-between;pointer-events:none;z-index:50;}" +
    "html.embed-slide .ss-pn{font-family:var(--font-text);font-size:var(--fs-caption);line-height:1;color:#6b6b6b;font-variant-numeric:tabular-nums;}" +
    "html.embed-slide .ss-logo{height:var(--logo-h);width:auto;display:block;}";
  document.head.appendChild(css);
  if (!document.getElementById("ss-font")) {
    var l = document.createElement("link");
    l.id = "ss-font"; l.rel = "stylesheet";
    l.href = "https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;500;600;700&display=swap";
    document.head.appendChild(l);
  }

  function num(v) { return parseFloat(v) || 0; }
  function sizeClass(px) { var pt = px / PT; return pt < 11.2 ? "t-caption" : pt < 16.7 ? "t-detail" : pt < 22.8 ? "t-body" : "t-sub"; }
  function leafText(e) { return Array.prototype.some.call(e.childNodes, function (n) { return n.nodeType === 3 && n.textContent.trim(); }); }
  function rect(e) { var r = e.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height, r: r.right, b: r.bottom }; }
  function visible(e) { var cs = getComputedStyle(e), r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && cs.visibility !== "hidden" && num(cs.opacity) > 0.05; }

  function pageNumber() {
    try {
      var fe = window.frameElement;
      if (!fe) return "";
      var doc = fe.ownerDocument;
      var host = fe.closest(".ws-slide, .share-slide, .dr-item");
      if (!host) return "";
      var all = Array.prototype.filter.call(doc.querySelectorAll(host.classList.contains("ws-slide") ? ".ws-slide" : host.classList.contains("dr-item") ? ".dr-item" : ".share-slide"), function (h) { return h.closest(".ws-left, #wsLeft, #wsPreviewScroll, .dr-list, body") === host.closest(".ws-left, #wsLeft, #wsPreviewScroll, .dr-list, body"); });
      var i = all.indexOf(host);
      return i < 0 ? "" : String(i + 1).padStart(2, "0");
    } catch (e) { return ""; }
  }

  function run() {
    var sc = document.getElementById(ID);
    if (!sc || sc.__ss) return;
    sc.__ss = 1;
    var cover = !!COVERS[ID];
    sc.classList.add("ss-measure");

    // heading: biggest h1/h2/strong in the screen's top half (not a big number)
    var heads = Array.prototype.filter.call(sc.querySelectorAll("h1, h2, h3, strong, [class*='title']"), function (e) {
      return visible(e) && e.textContent.trim().length > 2 && !/^\d+$/.test(e.textContent.trim()) && rect(e).y < H * 0.45;
    });
    var size = function (e) { return num(getComputedStyle(e).fontSize); };
    var top = heads.sort(function (a, b) { return size(b) - size(a); })[0] || null;
    // the heading block = the element that holds the bold + light words together
    var head = top;
    if (head && !cover) {
      var p = head.parentElement;
      if (p && p !== sc && /^H[1-3]$/.test(p.tagName)) head = p;
      else if (p && p !== sc && p.textContent.trim().length < 60 && p.children.length <= 3 && rect(p).h < rect(head).h * 2.4 &&
        Array.prototype.every.call(p.children, function (c) { return c === head || /^(SPAN|STRONG|B|EM|I|BR)$/.test(c.tagName) && getComputedStyle(c).display.indexOf("inline") === 0; })) head = p;
    }

    // text sizes (decided before anything changes)
    var texts = Array.prototype.filter.call(sc.querySelectorAll("*"), function (e) {
      return leafText(e) && visible(e) && !(head && head.contains(e)) && !e.closest("svg") && !(cover && size(e) >= 40 * PT);
    });
    var sizes = texts.map(size).sort(function (a, b) { return a - b; }), groups = [];
    sizes.forEach(function (v) { var g = groups[groups.length - 1]; if (g && v <= g[0] * 1.3) g.push(v); else groups.push([v]); });
    var sizeOf = function (px) {
      for (var i = 0; i < groups.length; i++) { var g = groups[i]; if (px >= g[0] - 0.01 && px <= g[g.length - 1] + 0.01) return sizeClass(g[Math.floor(g.length / 2)]); }
      return sizeClass(px);
    };
    var tiny = 0;
    texts.forEach(function (e) {
      var px = size(e);
      if (px < 6.5 * PT) { tiny++; return; }      // printed-size text inside logos / org boxes: left as designed
      var cs = getComputedStyle(e);
      e.classList.add(sizeOf(px));
      if (cs.textAlign === "center" && e.textContent.trim().length > 40 && rect(e).w > 260) e.classList.add("ss-left");
    });
    if (tiny) flags.push(tiny + " very small text item(s) (under 6.5 pt) left as designed - enlarging them breaks their boxes");

    if (cover) {
      flags.push("cover / section divider: kept its own layout; text sizes standardised");
      return finish();
    }
    if (!head) { flags.push("no heading found: heading rule not applied"); return finish(); }

    // keep a heading that sits in a right-hand column beside other content (e.g. WHO WE ARE beside the map)
    var h0 = rect(head), px0 = 0;
    [head].concat(Array.prototype.slice.call(head.querySelectorAll("*"))).forEach(function (e) { if (leafText(e)) px0 = Math.max(px0, size(e)); });
    var band = h0.x > W * 0.25;   // heading placed right/centre in a top band: it moves on its own
    var leftOfHead = Array.prototype.some.call(sc.querySelectorAll("img, svg, p, li, div"), function (e) {
      if (head.contains(e) || e.contains(head) || !visible(e)) return false;
      var r = rect(e);
      return r.w > 60 && r.h > 40 && r.r < h0.x - 20 && r.y < h0.b + 200 && r.b > h0.y - 100 && r.w < W * 0.6;
    });
    head.classList.add("ss-c-head");
    if (h0.x > W * 0.4 && leftOfHead) {
      flags.push("heading sits in the right-hand column beside the visual: kept in its column (moving it would swap the layout)");
      return finish();
    }

    // heading in a narrow column with content below it: keep its size if the standard size would run into that content
    var hr = rect(head);
    if (band) {
      head.style.width = "max-content"; head.style.maxWidth = "none"; head.style.whiteSpace = "nowrap";
      if (rect(head).w > M.r - M.l) { head.style.maxWidth = (M.r - M.l) + "px"; head.style.whiteSpace = "normal"; }
      hr = rect(head);
    }
    var clash = !band && Array.prototype.some.call(sc.querySelectorAll("*"), function (e) {
      if (head.contains(e) || e.contains(head) || !visible(e)) return false;
      var r = rect(e);
      if (r.w > W * 0.6 && r.h > H * 0.6) return false;
      return r.x < hr.r - 2 && r.r > hr.x + 2 && r.y < hr.b - 2 && r.b > hr.y + 2;
    });
    if (clash) {
      head.classList.add("ss-c-keep");
      head.style.setProperty("--ss-keep", px0 + "px");
      flags.push("heading kept at " + Math.round(px0 / PT) + " pt: at 50 pt it runs into the content beside/under it");
      hr = rect(head);
    }

    // move: the heading to the 54/54 pt corner, everything else (except edge-touching backgrounds) the same amount;
    // if that pushes content past the right/bottom margin, move content only as far as the margins allow
    var dx = band ? 0 : M.l - hr.x, dy = band ? 0 : M.t - hr.y;
    var kids = Array.prototype.filter.call(sc.children, function (e) {
      var r = rect(e);
      if (!visible(e) || e.classList.contains("ss-foot")) return false;
      if (r.x <= 1 && r.y <= 1 && r.w >= W - 2 && r.h >= H - 2 && !e.contains(head)) return false;   // full-bleed layer
      return true;
    });
    var leaves = Array.prototype.filter.call(sc.querySelectorAll("*"), function (e) {
      if (!visible(e) || head.contains(e)) return false;
      var r = rect(e);
      if (r.w > W * 0.6 && r.h > H * 0.6) return false;
      if (r.x <= 1 || r.y <= 1 || r.r >= W - 1 || r.b >= H - 1) return false;   // bleeds off the edge
      return !e.children.length || /^(IMG|svg|SVG|CANVAS)$/.test(e.tagName);
    }).map(rect);
    if (leaves.length) {
      var bx1 = Math.max.apply(null, leaves.map(function (r) { return r.r; })), by1 = Math.max.apply(null, leaves.map(function (r) { return r.b; }));
      var bx0 = Math.min.apply(null, leaves.map(function (r) { return r.x; }));
      var by0 = Math.min.apply(null, leaves.map(function (r) { return r.y; }));
      if (band) {
        // where the heading will be: corner + its new size
        var hb = { x: M.l, y: M.t, r: M.l + hr.w, b: M.t + hr.h };
        var under = hb.b + M.gap;
        var hits = leaves.some(function (r) { return r.x < hb.r && r.r > hb.x && r.y < under && r.b > hb.y; });
        if (hits) dy = under - Math.min.apply(null, leaves.filter(function (r) { return r.b > hb.y; }).map(function (r) { return r.y; }));
        if (bx0 < M.l) dx = M.l - bx0;
        if (bx1 + dx > M.r) dx = Math.max(M.r - bx1, M.l - bx0);
      } else {
        if (bx1 + dx > M.r) dx = Math.max(M.r - bx1, M.l - hr.x);
        if (bx0 + dx < M.l && hr.x + dx > M.l + 1) dx = Math.max(dx, M.l - bx0);
      }
      if (by1 + dy > M.b) { flags.push("content runs " + Math.round((by1 + dy - M.b) / PT) + " pt into the bottom margin"); }
      if (bx1 + dx > M.r + 1) flags.push("content runs " + Math.round((bx1 + dx - M.r) / PT) + " pt into the right margin");
    }
    kids.forEach(function (e) { e.style.translate = dx.toFixed(1) + "px " + dy.toFixed(1) + "px"; });
    var hr2 = rect(head);
    if (Math.abs(hr2.x - M.l) > 2 || Math.abs(hr2.y - M.t) > 2) {
      // heading is inside a child that could not move all the way: place the heading itself
      var t0 = (head.style.translate || "0px 0px").split(" ");
      head.style.translate = (num(t0[0]) + M.l - hr2.x).toFixed(1) + "px " + (num(t0[1] || 0) + M.t - hr2.y).toFixed(1) + "px";
    }
    var shift = function (e, ddx, ddy) {
      var t = (e.style.translate || "0px 0px").split(" ");
      e.style.translate = (num(t[0]) + ddx).toFixed(1) + "px " + (num(t[1] || 0) + ddy).toFixed(1) + "px";
    };
    var overlaps = function (a, b) { return a.x < b.r - 1 && b.x < a.r - 1 && a.y < b.b - 1 && b.y < a.b - 1; };
    // small labels (kickers / eyebrows) the heading now sits on: move them into the top margin, above the heading
    var hb = rect(head), kick = [];
    Array.prototype.forEach.call(sc.querySelectorAll("*"), function (e) {
      if (!leafText(e) || head.contains(e) || e.contains(head) || !visible(e) || size(e) > 14 * PT) return;
      var r = rect(e);
      if (overlaps(r, hb) && r.h < 40) kick.push([e, r]);
    });
    kick.forEach(function (k) { shift(k[0], M.l - k[1].x, (M.t - 6 * PT - k[1].h) - k[1].y); });
    if (kick.length) flags.push("small section label moved above the heading (it sat where the heading now goes)");
    // heading running into a visual (map, photo, chart): fall back to its original size
    hb = rect(head);
    var hitVisual = Array.prototype.some.call(sc.querySelectorAll("*"), function (e) {
      if (head.contains(e) || e.contains(head) || !visible(e)) return false;
      var r = rect(e);
      return r.w > 150 && r.h > 150 && r.w < W * 0.8 && overlaps(r, hb);
    });
    if (head.scrollWidth > head.clientWidth + 1) hitVisual = true;   // a word wider than its own column
    // or clipped by its own column (a parent that hides overflow)
    for (var pa = head.parentElement; pa && pa !== sc && !hitVisual; pa = pa.parentElement) {
      var ov = getComputedStyle(pa).overflowX;
      if ((ov === "hidden" || ov === "clip") && rect(pa).r < hb.r - 1) hitVisual = true;
    }
    if (hitVisual && !head.classList.contains("ss-c-keep")) {
      head.classList.add("ss-c-keep");
      head.style.setProperty("--ss-keep", px0 + "px");
      flags.push("heading kept at " + Math.round(px0 / PT) + " pt: at 50 pt it runs into the picture beside it");
    }
    finish();

    function finish() {
      var f = document.createElement("footer");
      f.className = "ss-foot";
      f.innerHTML = '<span class="ss-pn">' + pageNumber() + '</span><img class="ss-logo" src="' + LOGO + '" alt="HTL">';
      document.body.appendChild(f);
      // replay the screen's entrance with everything in its final place
      requestAnimationFrame(function () {
        sc.classList.remove("ss-measure");
        if (sc.classList.contains("active") && ID !== "intro") { sc.classList.remove("active"); void sc.offsetWidth; sc.classList.add("active"); }
      });
    }
  }

  function start() {
    var sc = document.getElementById(ID);
    if (!sc) return;
    var go = function () { (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(function () { setTimeout(run, 60); }); };
    if (sc.classList.contains("active") || ID === "intro") go();
    else {
      var mo = new MutationObserver(function () { if (sc.classList.contains("active")) { mo.disconnect(); go(); } });
      mo.observe(sc, { attributes: true, attributeFilter: ["class"] });
      setTimeout(function () { mo.disconnect(); go(); }, 1500);
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
