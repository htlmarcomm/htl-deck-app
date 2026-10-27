/* Edit slides: add slides from the library to the deck you are editing - also an old deck opened from
   My decks, which never goes through Choose slides. "+ Add slides" beside Finish & share (adds after the
   slide you are on) and "Slides from the library" in the + menu between slides (adds right there).
   Tick one or more slides, then "Add". Slides already in the deck say so, but can still be added again. */
(function () {
  "use strict";
  if (window.__HTL_SHARE_TOKEN__) return;
  function $(id) { return document.getElementById(id); }

  var st = document.createElement("style");
  st.textContent =
    "#wsAddModal .ws-replace-modal__head{position:sticky; top:0; z-index:5; background:inherit; gap:10px; flex-wrap:wrap;}" +
    "#wsAddModal .as-search{flex:1; min-width:180px; max-width:320px; padding:9px 12px; border:1px solid var(--line-strong,#d1d5db); border-radius:10px; font:inherit;}" +
    "#wsAddModal .as-count{font-size:.85rem; color:var(--muted,#6b7280);}" +
    "#wsAddModal .thumb-card{cursor:pointer; position:relative;}" +
    "#wsAddModal .thumb-card.as-picked{outline:3px solid #dc2626; outline-offset:2px; border-radius:12px;}" +
    "#wsAddModal .thumb-card.as-picked::after{content:'\\2713'; position:absolute; top:8px; right:8px; z-index:4; width:28px; height:28px; border-radius:50%; background:#dc2626; color:#fff; font:700 16px/28px Inter,system-ui,sans-serif; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,.25);}" +
    "#wsAddModal .as-in{position:absolute; left:8px; top:8px; z-index:4; background:#111827; color:#fff; font:600 11px/1 Inter,system-ui,sans-serif; padding:5px 8px; border-radius:999px;}" +
    "#wsAddModal .as-hide{display:none !important;}" +
    ".ws-add-slides-btn{margin-right:8px;}";
  document.head.appendChild(st);

  var modal = document.createElement("div");
  modal.className = "ws-replace-modal";
  modal.id = "wsAddModal";
  modal.innerHTML =
    '<div class="ws-replace-modal__inner">' +
    '<div class="ws-replace-modal__head"><h3>Add slides to this deck</h3>' +
    '<input type="search" class="as-search" placeholder="Find a slide…">' +
    '<span class="as-count">Click slides to tick them</span>' +
    '<button type="button" class="btn" id="wsAddCancel">Cancel</button>' +
    '<button type="button" class="btn btn--accent" id="wsAddGo" disabled>Add slides</button></div>' +
    '<div id="wsAddPickerBody"></div></div>';
  var after = -1;

  function count() {
    var n = modal.querySelectorAll(".thumb-card.as-picked").length;
    modal.querySelector(".as-count").textContent = n ? n + (n === 1 ? " slide ticked" : " slides ticked") : "Click slides to tick them";
    var go = $("wsAddGo");
    go.disabled = !n;
    go.textContent = n ? "Add " + n + (n === 1 ? " slide" : " slides") : "Add slides";
  }

  function open(afterIndex) {
    if (typeof WORKSPACE_SLIDES === "undefined") return;
    after = afterIndex == null ? (typeof wsActiveIndex === "number" ? wsActiveIndex : WORKSPACE_SLIDES.length - 1) : afterIndex;
    after = Math.max(-1, Math.min(after, WORKSPACE_SLIDES.length - 1));
    var body = $("wsAddPickerBody");
    var html = "";
    document.querySelectorAll("#buildScreen .deck-group").forEach(function (g) { html += g.outerHTML; });
    body.innerHTML = html;
    body.querySelectorAll(".thumb-card__toggle, .thumb-card__order, .sec-select, .sub-select, .sec-count, .sub-count").forEach(function (el) { el.remove(); });
    body.querySelectorAll("[id]").forEach(function (el) { el.removeAttribute("id"); }); // copies of the Choose slides sections: no duplicate ids
    body.querySelectorAll(".thumb-card").forEach(function (c) { c.classList.remove("excluded", "is-in", "in-deck"); });
    var inDeck = {};
    WORKSPACE_SLIDES.forEach(function (s) { inDeck[s.key] = 1; });
    fillSnippets(body);
    body.querySelectorAll(".thumb-card").forEach(function (card) {
      var stage = card.querySelector(".thumb-stage[data-key]");
      if (!stage) { card.classList.add("as-hide"); return; }
      if (inDeck[stage.getAttribute("data-key")]) {
        var b = document.createElement("span"); b.className = "as-in"; b.textContent = "Already in deck"; card.appendChild(b);
      }
      card.addEventListener("click", function (e) { e.preventDefault(); e.stopPropagation(); card.classList.toggle("as-picked"); count(); });
    });
    modal.querySelector(".as-search").value = "";
    count();
    modal.classList.add("is-open");
    modal.querySelector(".ws-replace-modal__inner").scrollTop = 0;
  }

  function close() { modal.classList.remove("is-open"); }

  function add() {
    var meta = getAllBlockMeta();
    var picked = Array.prototype.map.call(modal.querySelectorAll(".thumb-card.as-picked"), function (card) {
      var key = card.querySelector(".thumb-stage[data-key]").getAttribute("data-key");
      var lab = card.querySelector(".thumb-card__label");
      var m = meta[key];
      return m ? { key: m.key, label: m.label, kind: m.kind, slots: m.slots || [] } : { key: key, label: lab ? lab.textContent : key, kind: "static", slots: [] };
    });
    if (!picked.length) return;
    close();
    WORKSPACE_SLIDES.splice.apply(WORKSPACE_SLIDES, [after + 1, 0].concat(picked));
    wsBuilt = false;
    window.initWorkspace();
    var first = after + 1;
    selectWsSlide(first);
    var el = wsLeft.querySelector('.ws-slide[data-index="' + first + '"]');
    if (el) el.scrollIntoView({ block: "center", behavior: "smooth" });
    window.markAutosaveDirty();
  }

  function filter() {
    var q = modal.querySelector(".as-search").value.trim().toLowerCase();
    modal.querySelectorAll("#wsAddPickerBody .thumb-card").forEach(function (card) {
      if (!card.querySelector(".thumb-stage[data-key]")) return;
      var lab = (card.querySelector(".thumb-card__label") || {}).textContent || "";
      card.style.display = !q || lab.toLowerCase().indexOf(q) >= 0 ? "" : "none";
    });
  }

  function mount() {
    var ws = document.querySelector('.screen[data-screen="workspace"]');
    if (!ws) return;
    ws.appendChild(modal);
    $("wsAddCancel").addEventListener("click", close);
    $("wsAddGo").addEventListener("click", add);
    modal.addEventListener("click", function (e) { if (e.target === modal) close(); });
    modal.querySelector(".as-search").addEventListener("input", filter);
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && modal.classList.contains("is-open")) close(); });
    var finish = Array.prototype.find.call(ws.querySelectorAll(".screen-head button"), function (b) { return /Finish/.test(b.textContent); });
    if (finish) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn ws-add-slides-btn";
      btn.id = "wsAddSlidesBtn";
      btn.textContent = "+ Add slides";
      btn.title = "Add slides from the library after the slide you are on";
      btn.addEventListener("click", function () { open(null); });
      finish.parentNode.insertBefore(btn, finish);
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount); else mount();
  window.HTLAddSlides = { open: open };
})();
