/* Choose slides: easier to move around and to check slides quickly.
   - a sticky "Jump to" bar (one chip per section, with how many slides are ticked) + a slide search
   - a "Select all / Clear all" button at the top right of every section (and one for the whole list)
   - a magnifier on each slide -> a large preview you can step through with the arrow keys
   Works on the existing picker cards (.thumb-card); ticking a slide still goes through its own eye / + button. */
(function () {
  "use strict";
  var screen = document.getElementById("buildScreen");
  if (!screen || window.__HTL_SHARE_TOKEN__) return;

  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function cardsOf(root) { return Array.prototype.slice.call(root.querySelectorAll(".thumb-card:not(.pending)")); }
  function labelOf(card) { var l = card.querySelector(".thumb-card__label"); return l ? l.textContent.trim() : "Slide"; }
  function isOn(card) { return !card.classList.contains("excluded"); }
  function setOn(card, on) {
    if (isOn(card) === on) return;
    var b = card.querySelector(".thumb-card__toggle");
    if (b) b.click();
  }

  /* ------------------------------------------------------------ styles */
  var st = document.createElement("style");
  st.textContent =
    ".build-nav{position:sticky; top:0; z-index:20; background:var(--paper); padding:10px 0 10px; margin:0 0 14px; border-bottom:1px solid var(--line); display:flex; align-items:center; gap:12px; flex-wrap:wrap;}" +
    ".build-nav__chips{display:flex; align-items:center; gap:6px; overflow-x:auto; flex:1 1 360px; min-width:0; padding:2px 0; scrollbar-width:thin;}" +
    ".build-nav__lbl{font-size:.7rem; font-weight:600; text-transform:uppercase; letter-spacing:.06em; color:var(--muted); white-space:nowrap; margin-right:2px;}" +
    ".build-nav__deck{font-size:.68rem; font-weight:700; color:#9ca3af; text-transform:uppercase; letter-spacing:.06em; white-space:nowrap; padding:0 4px 0 10px; border-left:1px solid var(--line-strong);}" +
    ".build-nav__deck:first-of-type{border-left:0; padding-left:0;}" +
    ".build-chip{appearance:none; border:1px solid var(--line-strong); background:var(--surface); color:#374151; font:inherit; font-size:.78rem; font-weight:500; padding:5px 11px; border-radius:999px; cursor:pointer; white-space:nowrap; display:inline-flex; align-items:center; gap:6px; transition:background .15s, color .15s, border-color .15s;}" +
    ".build-chip:hover{background:var(--accent-wash); color:#b91c1c; border-color:#fecaca;}" +
    ".build-chip.is-here{background:var(--accent-wash); color:#b91c1c; border-color:#fecaca;}" +
    ".build-chip small{font-size:.7rem; color:#9ca3af; font-weight:500;} .build-chip.is-here small{color:#dc2626;}" +
    ".build-nav__tools{display:flex; align-items:center; gap:8px; flex-wrap:wrap;}" +
    ".build-nav__search{width:200px; border:1px solid var(--line-strong); border-radius:8px; background:#fff; font:inherit; font-size:.82rem; padding:6px 10px;}" +
    ".build-nav__search:focus{outline:0; border-color:transparent; box-shadow:0 0 0 2px #ef4444;}" +
    ".section-group__title{display:flex; align-items:center; gap:10px;}" +
    ".sec-select{appearance:none; margin-left:auto; border:1px solid var(--line-strong); background:var(--surface); color:#374151; font:inherit; font-size:.74rem; font-weight:500; letter-spacing:0; text-transform:none; padding:4px 11px; border-radius:8px; cursor:pointer; white-space:nowrap;}" +
    ".sec-select:hover{background:var(--accent-wash); color:#b91c1c; border-color:#fecaca;}" +
    ".sec-count{font-size:.72rem; font-weight:500; letter-spacing:0; text-transform:none; color:#9ca3af;}" +
    "#buildScreen .section-group{scroll-margin-top:72px;}" +
    ".build-empty{padding:40px 10px; text-align:center; color:var(--muted); font-size:.9rem; display:none;} .build-empty.is-on{display:block;}" +
    ".thumb-card__peek{position:absolute; right:6px; bottom:6px; z-index:3; width:28px; height:28px; border-radius:50%; border:1px solid rgba(17,17,17,.12); background:rgba(255,255,255,.96); box-shadow:0 2px 6px rgba(0,0,0,.15); display:flex; align-items:center; justify-content:center; cursor:zoom-in; opacity:0; transform:translateY(4px); transition:opacity .15s, transform .15s; padding:0; color:#111827;}" +
    ".thumb-card__peek svg{width:15px; height:15px; fill:none; stroke:currentColor; stroke-width:2; stroke-linecap:round; stroke-linejoin:round;}" +
    ".thumb-card:hover .thumb-card__peek, .thumb-card__peek:focus-visible{opacity:1; transform:none;}" +
    ".thumb-card__peek:hover{background:#111827; color:#fff;}" +
    "@media (hover:none){.thumb-card__peek{opacity:1; transform:none;}} @media (hover:hover){.thumb-card__peek{display:none;}}" +
    /* the big preview that follows the pointer onto a slide */
    ".hv-pop{position:fixed; z-index:850; width:560px; background:#fff; border-radius:14px; box-shadow:0 18px 50px rgba(0,0,0,.35), 0 0 0 1px rgba(17,24,39,.08); overflow:hidden; pointer-events:none; opacity:0; transform:scale(.97); transition:opacity .12s ease, transform .12s ease;}" +
    ".hv-pop.is-on{opacity:1; transform:none;}" +
    ".hv-pop__frame{position:relative; width:560px; height:315px; overflow:hidden; background:#fff;}" +
    ".hv-pop__frame .share-slide{border-radius:0; box-shadow:none;}" +
    ".hv-pop__cap{padding:11px 16px 13px; border-top:1px solid var(--line);}" +
    ".hv-pop__name{font-weight:600; font-size:.92rem; color:#111827;}" +
    ".hv-pop__hint{font-size:.8rem; color:var(--muted); margin-top:3px;}" +
    /* preview window */
    ".pv-modal{position:fixed; inset:0; z-index:900; background:rgba(17,24,39,.72); display:none; align-items:center; justify-content:center; padding:20px;}" +
    ".pv-modal.is-open{display:flex;}" +
    ".pv-box{background:#fff; border-radius:14px; box-shadow:0 24px 60px rgba(0,0,0,.45); width:min(1180px, 100%); max-height:100%; display:flex; flex-direction:column; overflow:hidden;}" +
    ".pv-stage{position:relative; background:#eceef3; display:flex; align-items:center; justify-content:center; padding:16px; min-height:0;}" +
    ".pv-frame{position:relative; overflow:hidden; background:#fff; border-radius:10px; box-shadow:0 10px 30px -10px rgba(0,0,0,.4); flex:none;}" +
    ".pv-frame .share-slide{border-radius:0; box-shadow:none;}" +
    ".pv-arrow{position:absolute; top:50%; transform:translateY(-50%); width:38px; height:38px; border-radius:50%; border:1px solid var(--line-strong); background:#fff; box-shadow:0 2px 8px rgba(0,0,0,.18); font-size:1.1rem; cursor:pointer; z-index:2; color:#111827; display:flex; align-items:center; justify-content:center;}" +
    ".pv-arrow:hover{background:var(--accent-wash); color:#b91c1c;} .pv-arrow:disabled{opacity:.3; cursor:default;}" +
    ".pv-arrow--prev{left:12px;} .pv-arrow--next{right:12px;}" +
    ".pv-foot{display:flex; align-items:center; gap:12px; padding:12px 18px; border-top:1px solid var(--line); flex-wrap:wrap;}" +
    ".pv-title{font-weight:600; font-size:.95rem; color:#111827;} .pv-sub{font-size:.78rem; color:var(--muted); margin-top:1px;}" +
    ".pv-foot__btns{margin-left:auto; display:flex; gap:8px; flex-wrap:wrap;}" +
    ".pv-pill{display:inline-block; font-size:.72rem; font-weight:600; padding:2px 8px; border-radius:999px; margin-left:6px; vertical-align:1px;}" +
    ".pv-pill.on{background:var(--success-wash); color:var(--success);} .pv-pill.off{background:#f3f4f6; color:#6b7280;}";
  document.head.appendChild(st);

  /* ------------------------------------------------------------ jump bar + search */
  var groups = Array.prototype.slice.call(screen.querySelectorAll(".section-group"));
  var nav = document.createElement("div");
  nav.className = "build-nav";
  nav.id = "buildNav";
  var chipsHtml = "", lastDeck = null;
  groups.forEach(function (g, i) {
    var deck = g.closest(".deck-group");
    var deckTitle = deck && deck.querySelector(".deck-group__title");
    var deckName = deckTitle ? deckTitle.childNodes[0].textContent.trim().replace(/^Master\s+/, "").replace(/\s+Deck$/, "") : "";
    if (deckName !== lastDeck) { chipsHtml += '<span class="build-nav__deck">' + esc(deckName) + " deck</span>"; lastDeck = deckName; }
    var title = g.querySelector(".section-group__title");
    g.id = g.id || "bsec" + i;
    chipsHtml += '<button type="button" class="build-chip" data-sec="' + g.id + '">' + esc(title.firstChild.textContent.trim()) + " <small></small></button>";
  });
  nav.innerHTML =
    '<div class="build-nav__chips" id="buildChips"><span class="build-nav__lbl">Jump to</span>' + chipsHtml + "</div>" +
    '<div class="build-nav__tools">' +
      '<input type="search" class="build-nav__search" id="buildSearch" placeholder="Find a slide…" aria-label="Find a slide">' +
      '<button type="button" class="btn btn--sm" id="buildSelAll">Select all</button>' +
      '<button type="button" class="btn btn--sm" id="buildPreviewSel" title="Look through the slides you ticked, one by one">Preview selected</button>' +
    "</div>";
  var hint = $("buildHint");
  hint.parentNode.insertBefore(nav, hint.nextSibling);
  var none = document.createElement("div");
  none.className = "build-empty";
  none.id = "buildNone";
  none.textContent = "No slides match that search.";
  nav.parentNode.insertBefore(none, nav.nextSibling);

  nav.addEventListener("click", function (e) {
    var chip = e.target.closest(".build-chip");
    if (chip) {
      var g = $(chip.getAttribute("data-sec"));
      if (g) g.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }
    if (e.target.closest("#buildSelAll")) {
      var all = cardsOf(screen).filter(function (c) { return c.style.display !== "none"; });
      var every = all.every(isOn);
      all.forEach(function (c) { setOn(c, !every); });
      refresh();
      return;
    }
    if (e.target.closest("#buildPreviewSel")) {
      var list = cardsOf(screen).filter(isOn);
      if (!list.length) { alert("Tick at least one slide first."); return; }
      openPreview(list, 0);
    }
  });

  var search = $("buildSearch");
  search.addEventListener("input", function () {
    var q = search.value.trim().toLowerCase(), any = false;
    groups.forEach(function (g) {
      var shown = 0;
      cardsOf(g).forEach(function (c) {
        var m = !q || labelOf(c).toLowerCase().indexOf(q) >= 0;
        c.style.display = m ? "" : "none";
        if (m) shown++;
      });
      g.style.display = shown ? "" : "none";
      if (shown) any = true;
    });
    // deck headings with nothing left under them
    Array.prototype.forEach.call(screen.querySelectorAll(".deck-group"), function (d) {
      var vis = Array.prototype.some.call(d.querySelectorAll(".section-group"), function (g) { return g.style.display !== "none"; });
      d.style.display = vis ? "" : "none";
    });
    $("buildNone").classList.toggle("is-on", !any);
    refresh();
  });

  /* ------------------------------------------------------------ per-section Select all */
  groups.forEach(function (g) {
    var title = g.querySelector(".section-group__title");
    var count = document.createElement("span");
    count.className = "sec-count";
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "sec-select";
    title.appendChild(count);
    title.appendChild(btn);
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var cs = cardsOf(g).filter(function (c) { return c.style.display !== "none"; });
      var every = cs.every(isOn);
      cs.forEach(function (c) { setOn(c, !every); });
      refresh();
    });
  });

  function refresh() {
    var onAll = 0, totalAll = 0;
    groups.forEach(function (g) {
      var cs = cardsOf(g), on = cs.filter(isOn).length;
      onAll += on; totalAll += cs.length;
      var btn = g.querySelector(".sec-select"), count = g.querySelector(".sec-count");
      if (count) count.textContent = on + " of " + cs.length + " ticked";
      if (btn) btn.textContent = (cs.length && on === cs.length) ? "Clear all" : "Select all";
      var chip = nav.querySelector('.build-chip[data-sec="' + g.id + '"] small');
      if (chip) chip.textContent = on + "/" + cs.length;
    });
    var sel = $("buildSelAll");
    if (sel) sel.textContent = (totalAll && onAll === totalAll) ? "Clear all" : "Select all";
    var cnt = $("buildCount"); // a slide's own button stops the click, so the old counter never hears about it
    if (cnt) cnt.textContent = onAll + " of " + totalAll + " slides included.";
    markHere();
  }
  screen.addEventListener("click", function () { setTimeout(refresh, 0); });
  refresh();

  /* which section is on screen -> highlight its chip */
  var raf = 0;
  function markHere() {
    var cur = null;
    groups.forEach(function (g) {
      if (g.style.display === "none" || !g.offsetParent) return;
      if (g.getBoundingClientRect().top <= 130) cur = g;
    });
    if (!cur) cur = groups.filter(function (g) { return g.offsetParent; })[0];
    Array.prototype.forEach.call(nav.querySelectorAll(".build-chip"), function (c) {
      var here = !!cur && c.getAttribute("data-sec") === cur.id;
      c.classList.toggle("is-here", here);
      if (here && screen.classList.contains("is-active")) {
        var box = $("buildChips");
        var l = c.offsetLeft - box.offsetLeft, r = l + c.offsetWidth;
        if (l < box.scrollLeft + 90) box.scrollLeft = Math.max(0, l - 90);
        else if (r > box.scrollLeft + box.clientWidth) box.scrollLeft = r - box.clientWidth + 12;
      }
    });
  }
  window.addEventListener("scroll", function () {
    if (!screen.classList.contains("is-active") || raf) return;
    raf = requestAnimationFrame(function () { raf = 0; markHere(); });
  }, { passive: true });

  /* ------------------------------------------------------------ preview */
  var PEEK = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/><path d="M11 8v6M8 11h6"/></svg>';
  cardsOf(screen).forEach(function (card) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = "thumb-card__peek";
    b.title = "Preview this slide";
    b.setAttribute("aria-label", "Preview this slide");
    b.innerHTML = PEEK;
    card.appendChild(b);
    b.addEventListener("click", function (e) {
      e.stopPropagation();
      var list = cardsOf(screen).filter(function (c) { return c.style.display !== "none"; });
      openPreview(list, Math.max(0, list.indexOf(card)));
    });
  });

  var modal = document.createElement("div");
  modal.className = "pv-modal";
  modal.innerHTML =
    '<div class="pv-box" role="dialog" aria-modal="true" aria-label="Slide preview">' +
      '<div class="pv-stage" id="pvStage"><button type="button" class="pv-arrow pv-arrow--prev" id="pvPrev" aria-label="Previous slide">&#8249;</button>' +
      '<div class="pv-frame" id="pvFrame"></div>' +
      '<button type="button" class="pv-arrow pv-arrow--next" id="pvNext" aria-label="Next slide">&#8250;</button></div>' +
      '<div class="pv-foot"><div><div class="pv-title" id="pvTitle"></div><div class="pv-sub" id="pvSub"></div></div>' +
      '<div class="pv-foot__btns"><button type="button" class="btn" id="pvToggle"></button><button type="button" class="btn btn--accent" id="pvClose">Close</button></div></div>' +
    "</div>";
  document.body.appendChild(modal);
  var pv = { list: [], i: 0 };

  function sizeFrame() {
    var stage = $("pvStage");
    var availW = Math.min(1148, stage.clientWidth - 32 || 1000);
    var availH = Math.max(240, window.innerHeight - 40 - 70 - 32); // viewport - padding - footer - stage padding
    var scale = Math.min(availW / 1180, availH / 664);
    var fr = $("pvFrame");
    fr.style.width = Math.round(1180 * scale) + "px";
    fr.style.height = Math.round(664 * scale) + "px";
    var s = fr.querySelector(".share-slide");
    if (s) s.style.zoom = scale;
  }
  function show() {
    var card = pv.list[pv.i];
    if (!card) return;
    var stageEl = card.querySelector(".thumb-stage[data-key]");
    var key = stageEl && stageEl.getAttribute("data-key");
    var fr = $("pvFrame");
    fr.innerHTML = '<div class="share-slide"><div class="thumb-stage real-scope" data-key="' + esc(key) + '" style="width:1180px"></div></div>';
    if (window.fillSnippets) window.fillSnippets(fr);
    sizeFrame();
    var st2 = fr.querySelector(".thumb-stage");
    if (st2 && window.playSlideReveal) setTimeout(function () { try { window.playSlideReveal(st2); } catch (e) {} }, 60);
    var on = isOn(card);
    $("pvTitle").innerHTML = esc(labelOf(card)) + '<span class="pv-pill ' + (on ? "on" : "off") + '">' + (on ? "In your deck" : "Left out") + "</span>";
    $("pvSub").textContent = "Slide " + (pv.i + 1) + " of " + pv.list.length + "  ·  ← → to move, Esc to close";
    $("pvToggle").textContent = on ? "Leave this slide out" : "Put this slide in";
    $("pvPrev").disabled = pv.i === 0;
    $("pvNext").disabled = pv.i === pv.list.length - 1;
  }
  function openPreview(list, i) {
    pv.list = list; pv.i = i;
    modal.classList.add("is-open");
    document.documentElement.style.overflow = "hidden";
    show();
  }
  function closePreview() {
    modal.classList.remove("is-open");
    document.documentElement.style.overflow = "";
    $("pvFrame").innerHTML = "";
  }
  function step(d) { var n = pv.i + d; if (n < 0 || n >= pv.list.length) return; pv.i = n; show(); }
  modal.addEventListener("click", function (e) {
    if (e.target === modal || e.target.closest("#pvClose")) closePreview();
    else if (e.target.closest("#pvPrev")) step(-1);
    else if (e.target.closest("#pvNext")) step(1);
    else if (e.target.closest("#pvToggle")) { var c = pv.list[pv.i]; setOn(c, !isOn(c)); refresh(); show(); }
  });
  document.addEventListener("keydown", function (e) {
    if (!modal.classList.contains("is-open")) return;
    if (e.key === "Escape") { e.preventDefault(); closePreview(); }
    else if (e.key === "ArrowRight") { e.preventDefault(); step(1); }
    else if (e.key === "ArrowLeft") { e.preventDefault(); step(-1); }
  });
  window.addEventListener("resize", function () { if (modal.classList.contains("is-open")) sizeFrame(); });

  /* ------------------------------------------------------------ hover preview */
  var HV_W = 560, HV_H = 315 + 62;
  var pop = document.createElement("div");
  pop.className = "hv-pop";
  pop.innerHTML = '<div class="hv-pop__frame" id="hvFrame"></div><div class="hv-pop__cap"><div class="hv-pop__name" id="hvName"></div><div class="hv-pop__hint" id="hvHint"></div></div>';
  document.body.appendChild(pop);
  var hvCache = {}, hvCard = null, hvTimer = 0, hvHide = 0;

  function hvSlide(key) {
    if (hvCache[key]) return hvCache[key];
    var d = document.createElement("div");
    d.className = "share-slide";
    d.style.zoom = HV_W / 1180;
    d.innerHTML = '<div class="thumb-stage real-scope" data-key="' + esc(key) + '" style="width:1180px"></div>';
    $("hvFrame").appendChild(d);
    if (window.fillSnippets) window.fillSnippets(d.parentNode);
    var stage = d.querySelector(".thumb-stage");
    if (stage && window.playSlideReveal) setTimeout(function () { try { window.playSlideReveal(stage); } catch (e) {} }, 40);
    hvCache[key] = d;
    return d;
  }
  function hvCaption(card) {
    var on = isOn(card);
    $("hvName").innerHTML = esc(labelOf(card)) + '<span class="pv-pill ' + (on ? "on" : "off") + '">' + (on ? "In your deck" : "Not in your deck") + "</span>";
    $("hvHint").textContent = on ? "Click this slide to leave it out." : "Click this slide to add it to your deck.";
  }
  function hvShow(card) {
    var stageEl = card.querySelector(".thumb-stage[data-key]");
    var key = stageEl && stageEl.getAttribute("data-key");
    if (!key) return;
    Array.prototype.forEach.call($("hvFrame").children, function (c) { c.style.display = "none"; });
    hvSlide(key).style.display = "";
    hvCaption(card);
    var r = card.getBoundingClientRect(), vw = window.innerWidth, vh = window.innerHeight, gap = 14;
    var left = r.right + gap;
    if (left + HV_W > vw - 8) left = r.left - gap - HV_W;
    if (left < 8) left = Math.max(8, Math.min(vw - HV_W - 8, r.left + r.width / 2 - HV_W / 2)); // narrow window: centre it over the card
    var top = r.top + r.height / 2 - HV_H / 2;
    top = Math.max(8, Math.min(vh - HV_H - 8, top));
    pop.style.left = Math.round(left) + "px";
    pop.style.top = Math.round(top) + "px";
    pop.classList.add("is-on");
    hvCard = card;
  }
  function hvOff() {
    clearTimeout(hvTimer); clearTimeout(hvHide);
    pop.classList.remove("is-on");
    hvCard = null;
  }
  screen.addEventListener("mouseover", function (e) {
    var card = e.target.closest && e.target.closest(".thumb-card:not(.pending)");
    if (!card || card === hvCard || modal.classList.contains("is-open")) return;
    clearTimeout(hvTimer); clearTimeout(hvHide);
    // already showing one: move straight to the next; otherwise a very short wait so a passing pointer does not flash
    hvTimer = setTimeout(function () { hvShow(card); }, hvCard ? 0 : 220);
  });
  screen.addEventListener("mouseout", function (e) {
    var card = e.target.closest && e.target.closest(".thumb-card:not(.pending)");
    if (!card) return;
    var to = e.relatedTarget;
    if (to && card.contains(to)) return;
    clearTimeout(hvTimer);
    hvHide = setTimeout(hvOff, 60);
  });
  screen.addEventListener("click", function () { if (hvCard) { var c = hvCard; setTimeout(function () { if (hvCard === c) hvCaption(c); }, 0); } });
  window.addEventListener("scroll", function () { if (hvCard) hvOff(); }, { passive: true });
  window.addEventListener("blur", hvOff);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") hvOff(); });
})();
