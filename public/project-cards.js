/* Edit slides: project slides (the "Major MEP Projects" layout, section.ss-proj) are fully editable.
   - every card gets a "−" button (remove it)
   - right panel "Projects on this slide": search the Project list and add a project as a card,
     or add a blank card to fill in yourself
   - cards re-space evenly after every change (rows of 2-4, edge to edge, photos as tall as fits)
   Text (title, label, names, values) is edited by clicking it, photos with "Change photo" - as on every slide. */
(function () {
  "use strict";
  if (window.__HTL_SHARE_TOKEN__) return;
  var MAX = 12;
  var M = { l: 72, r: 1208, b: 656 };
  var X0 = 362, GRID_Y = 72 + 12 * 1.3 + 6 + 16, GAP = 24, CAP = 12 * 1.3;
  var PLACEHOLDER = "data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='300'%3E%3Crect width='400' height='300' fill='%23e8e5df'/%3E%3Ctext x='200' y='158' font-family='Arial' font-size='22' fill='%23938c80' text-anchor='middle'%3EPoint here, then Change photo%3C/text%3E%3C/svg%3E";
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }

  var st = document.createElement("style");
  st.textContent =
    ".pc-sec .pc-search{width:100%; box-sizing:border-box; padding:8px 10px; border:1px solid var(--line-strong,#d1d5db); border-radius:8px; font:inherit; font-size:.85rem; margin:6px 0;}" +
    ".pc-sec .pc-list{max-height:260px; overflow:auto; border:1px solid var(--line,#e5e7eb); border-radius:8px;}" +
    ".pc-sec .pc-row{display:flex; align-items:center; gap:8px; padding:7px 9px; border-bottom:1px solid var(--line,#eee); font-size:.8rem;}" +
    ".pc-sec .pc-row:last-child{border-bottom:0;} .pc-sec .pc-row span{flex:1; min-width:0;} .pc-sec .pc-row small{display:block; color:var(--muted,#6b7280);}" +
    ".pc-sec .pc-row button{flex:0 0 auto;} .pc-sec .pc-msg{font-size:.78rem; color:var(--muted,#6b7280); margin:6px 0;}" +
    ".pc-sec .pc-actions{display:flex; gap:8px; margin-top:8px; flex-wrap:wrap;}";
  document.head.appendChild(st);

  /* ------------------------------------------------------------ project register (read once) */
  var ROWS = null, loading = null;
  function loadRows() {
    if (ROWS) return Promise.resolve(ROWS);
    if (loading) return loading;
    loading = new Promise(function (res) {
      if (!window.claude || !window.claude.use) { ROWS = []; return res(ROWS); }
      window.claude.use("db").then(function (db) {
        if (!db) { ROWS = []; return res(ROWS); }
        var done = false;
        db.collection("projects").onSnapshot(function (snap) {
          var rows = [];
          snap.docs.forEach(function (d) { ((d.data() || {}).rows || []).forEach(function (r) { rows.push(r); }); });
          ROWS = rows;
          if (!done) { done = true; res(ROWS); }
        }, function () { ROWS = []; if (!done) { done = true; res(ROWS); } });
      }).catch(function () { ROWS = []; res(ROWS); });
    });
    return loading;
  }
  function areaText(v) { return v == null || v === "" ? "" : (typeof v === "number" ? Math.round(v).toLocaleString("en-IN") + " sq.ft" : String(v)); }

  /* ------------------------------------------------------------ cards */
  var slideEl = function (i) { return wsLeft.querySelector('.ws-slide[data-index="' + i + '"]'); };
  var secOf = function (i) { var el = slideEl(i); return el && el.querySelector(".thumb-stage section.ss-proj"); };
  var cardsOf = function (sec) { return Array.prototype.slice.call(sec.querySelectorAll(":scope > .ss-pcard")); };

  function rowsFor(n) {
    if (n <= 4) return [n];
    if (n <= 6) return [3, n - 3];
    if (n <= 8) return [4, n - 4];
    var out = []; while (n > 0) { out.push(Math.min(4, n)); n -= 4; } return out;
  }
  function cardHTML(p) {
    var kv = (p.kv || []).map(function (x) { return '<p class="t-caption"><span class="is-b ss-k">' + esc(x[0]) + ':</span><span class="is-r ss-v">' + esc(x[1]) + "</span></p>"; }).join("");
    return '<div class="ss-pcard"><div class="pj-ph ss-pc-ph" style="background-image:url(&quot;' + (p.photo || PLACEHOLDER) + '&quot;)"></div>' +
      '<div class="ss-pc-text"><p class="t-caption is-b pj-nm">' + esc(p.name) + "</p>" + (p.loc ? '<p class="t-caption is-r pj-lc">' + esc(p.loc) + "</p>" : "") + "</div>" +
      '<i class="ss-pc-rule"></i><div class="ss-pc-kv ss-kv">' + kv + "</div></div>";
  }
  // lay the cards out again: rows of up to 4 across the area right of the panel, photos as tall as fits
  function relayout(sec) {
    var cards = cardsOf(sec), n = cards.length;
    if (!n) return;
    var rows = rowsFor(n), per = Math.max.apply(null, rows);
    var cw = (M.r - X0 - (per - 1) * GAP) / per;
    var rowH = (M.b - GRID_Y - (rows.length - 1) * GAP) / rows.length;
    // text block height: name (+ wrap) + location + value lines, the tallest card decides
    var hasLoc = cards.some(function (c) { return c.querySelector(".pj-lc"); });
    var longName = cards.some(function (c) { var t = (c.querySelector(".pj-nm") || {}).textContent || ""; return t.length > cw / 6.6; });
    var kvN = Math.max.apply(null, cards.map(function (c) { return c.querySelectorAll(".ss-pc-kv > p").length; }).concat([1]));
    var tx = CAP * (1 + (hasLoc ? 1 : 0) + (longName ? 1 : 0));
    var textH = 8 + tx + 14 + kvN * CAP;
    var ph = Math.max(40, Math.min(cw / 1.25, rowH - textH));
    var i = 0, y = GRID_Y;
    rows.forEach(function (rc) {
      for (var j = 0; j < rc; j++, i++) {
        var c = cards[i];
        c.style.left = (X0 + j * (cw + GAP)).toFixed(1) + "px";
        c.style.top = y.toFixed(1) + "px";
        c.style.width = cw.toFixed(1) + "px";
        c.style.setProperty("--ss-ph", ph.toFixed(1) + "px");
        c.style.setProperty("--ss-tx", tx.toFixed(1) + "px");
      }
      y += rowH + GAP;
    });
  }
  function rebuild(idx) {
    wsBuilt = false;
    window.initWorkspace();
    try { selectWsSlide(idx); } catch (e) {}
    var el = slideEl(idx);
    if (el) el.scrollIntoView({ block: "nearest" });
    window.markAutosaveDirty();
  }
  function addCard(idx, p) {
    var sec = secOf(idx);
    if (!sec) return;
    if (cardsOf(sec).length >= MAX) { alert("A project slide holds up to " + MAX + " projects. Add another project slide for more."); return; }
    var foot = sec.querySelector(":scope > .ss-foot");
    var tmp = document.createElement("div");
    tmp.innerHTML = cardHTML(p);
    sec.insertBefore(tmp.firstChild, foot);
    relayout(sec);
    rebuild(idx);
  }
  function removeCard(idx, card) {
    var sec = secOf(idx);
    if (!sec) return;
    if (cardsOf(sec).length <= 1) { alert("A project slide needs at least one project. To drop the slide, use Delete slide."); return; }
    card.remove();
    relayout(sec);
    rebuild(idx);
  }

  // "−" on every card (editing only: .ws-card-remove is stripped when the slide is saved)
  function wireRemove() {
    if (typeof wsLeft === "undefined" || !wsLeft) return;
    wsLeft.querySelectorAll(".ws-slide").forEach(function (sl) {
      var idx = +sl.getAttribute("data-index");
      sl.querySelectorAll(".thumb-stage section.ss-proj > .ss-pcard").forEach(function (card) {
        if (card.querySelector(".ws-card-remove")) return;
        var b = document.createElement("button");
        b.type = "button"; b.className = "ws-card-remove"; b.title = "Remove this project"; b.textContent = "−";
        b.addEventListener("click", function (e) { e.stopPropagation(); removeCard(idx, card); });
        card.appendChild(b);
      });
    });
  }
  var _init = window.initWorkspace;
  window.initWorkspace = function () {
    var r = _init.apply(this, arguments);
    setTimeout(wireRemove, 60); setTimeout(wireRemove, 700);
    return r;
  };

  /* ------------------------------------------------------------ right panel */
  function panel() {
    var right = document.getElementById("wsRight");
    var idx = window.wsActiveIndex;
    var sec = secOf(idx);
    var old = right && right.querySelector(".pc-sec");
    if (old) old.remove();
    if (!right || !sec) return;
    var n = cardsOf(sec).length;
    var box = document.createElement("div");
    box.className = "ws-section pc-sec";
    box.innerHTML =
      '<h5>Projects on this slide <span class="ws-section__note">' + n + " of " + MAX + "</span></h5>" +
      '<p class="pc-msg">Click a project’s text to change it, point at a photo to change it, or use − on a card to remove it.</p>' +
      '<input type="search" class="pc-search" placeholder="Search the Project list: name, client, city…">' +
      '<div class="pc-list"><div class="pc-row"><span>Type to search your Project list.</span></div></div>' +
      '<div class="pc-actions"><button type="button" class="btn btn--sm" data-pc-blank="1">+ Add blank card</button></div>';
    var actions = right.querySelector(".ws-slide-actions");
    if (actions && actions.nextSibling) right.insertBefore(box, actions.nextSibling); else right.appendChild(box);
    var list = box.querySelector(".pc-list"), q = box.querySelector(".pc-search");
    var found = [];
    function show() {
      var t = q.value.trim().toLowerCase();
      if (!t) { list.innerHTML = '<div class="pc-row"><span>Type to search your Project list.</span></div>'; return; }
      list.innerHTML = '<div class="pc-row"><span>Searching…</span></div>';
      loadRows().then(function (rows) {
        found = rows.filter(function (r) { return [r.project_name, r.client_name, r.city, r.location, r.sector].join(" ").toLowerCase().indexOf(t) >= 0; }).slice(0, 40);
        if (!rows.length) { list.innerHTML = '<div class="pc-row"><span>The Project list is not available here.</span></div>'; return; }
        if (!found.length) { list.innerHTML = '<div class="pc-row"><span>No project matches “' + esc(q.value) + "”.</span></div>"; return; }
        list.innerHTML = found.map(function (r, i) {
          return '<div class="pc-row"><span>' + esc(r.project_name) + "<small>" + esc([r.city, r.scope, areaText(r.area_sqft)].filter(Boolean).join(" · ")) +
            '</small></span><button type="button" class="btn btn--sm" data-pc-add="' + i + '">Add</button></div>';
        }).join("");
      });
    }
    q.addEventListener("input", function () { clearTimeout(q._t); q._t = setTimeout(show, 200); });
    box.addEventListener("click", function (e) {
      var a = e.target.closest("[data-pc-add]");
      if (a) {
        var r = found[+a.getAttribute("data-pc-add")];
        if (!r) return;
        var kv = [];
        if (r.area_sqft) kv.push(["AREA", areaText(r.area_sqft)]);
        if (r.scope) kv.push(["SCOPE", r.scope]);
        if (r.capacity) kv.push(["CAPACITY", r.capacity]);
        addCard(idx, { name: r.project_name, loc: r.city || r.location || "", kv: kv.length ? kv : [["SCOPE", "—"]] });
        return;
      }
      if (e.target.closest("[data-pc-blank]")) addCard(idx, { name: "Project name", loc: "City", kv: [["AREA", "—"], ["SCOPE", "—"]] });
    });
  }
  var _rwr = window.renderWsRight;
  if (_rwr) window.renderWsRight = function () { var r = _rwr.apply(this, arguments); try { panel(); } catch (e) { if (window.console) console.warn(e); } return r; };
})();
