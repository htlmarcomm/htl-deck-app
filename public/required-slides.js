/* Company slides are compulsory: every new deck (own or ready-made, Profile or Capability) includes the five
   Company slides, and they cannot be left out on Choose slides, or deleted / replaced on Edit slides.
   They can still be edited (text, photos, client logo) and moved. Decks saved before this keep what they have. */
(function () {
  "use strict";
  if (window.__HTL_SHARE_TOKEN__) return;
  var REQUIRED = ["title_page", "about_us", "mission_vision_values", "pj_journey", "pj_orgstructure"];
  window.HTL_REQUIRED_SLIDES = REQUIRED;
  var isReq = function (key) { return REQUIRED.indexOf(key) >= 0; };
  var keyOfCard = function (card) { var st = card && card.querySelector(".thumb-stage[data-key]"); return st ? st.getAttribute("data-key") : null; };
  var inBuild = function (el) { return !!(el && el.closest && el.closest("#buildScreen")); };

  var st = document.createElement("style");
  st.textContent =
    "#buildScreen .thumb-card.is-required{cursor:default;}" +
    "#buildScreen .thumb-card.is-required .thumb-card__toggle{pointer-events:none; background:#374151 !important; border-color:#374151 !important;}" +
    "#buildScreen .thumb-card.is-required .thumb-card__toggle::after{content:'\\1F512  Always included' !important; color:#fff !important;}" +
    "#buildScreen .section-group.is-required-group .sec-select{display:none;}" +
    ".ws-req-note{font-size:.78rem; color:var(--muted,#6b7280); margin:6px 0 2px;}" +
    ".ws-slide-actions .is-locked, .ws-slide__menu .is-locked{opacity:.45; pointer-events:none;}";
  document.head.appendChild(st);

  /* ------------------------------------------------------------ Choose slides */
  // block anything that would leave a compulsory slide out (card click, its toggle, Select / Clear all, deck presets)
  document.addEventListener("click", function (e) {
    var t = e.target;
    if (!inBuild(t)) return;
    var card = t.closest(".thumb-card");
    if (!card || !isReq(keyOfCard(card))) return;
    if (!card.classList.contains("excluded")) { e.stopImmediatePropagation(); e.preventDefault(); }
  }, true);

  function lockCards() {
    var build = document.getElementById("buildScreen");
    if (!build) return;
    build.querySelectorAll(".thumb-card").forEach(function (card) {
      if (!isReq(keyOfCard(card))) return;
      card.classList.add("is-required");
      card.classList.remove("is-toggleable");
      card.title = "Company slide - always included in every deck";
      if (card.classList.contains("excluded")) {   // bring it back through the app's own toggle (keeps numbering right)
        var b = card.querySelector(".thumb-card__toggle");
        if (b) b.click();
      }
      var g = card.closest(".section-group");
      if (g && Array.prototype.every.call(g.querySelectorAll(".thumb-card:not(.pending)"), function (c) { return isReq(keyOfCard(c)); })) g.classList.add("is-required-group");
    });
  }
  function watch() {
    var build = document.getElementById("buildScreen");
    if (!build) return;
    lockCards();
    new MutationObserver(function (ms) {
      if (ms.some(function (m) { return m.attributeName === "class" && m.target.classList && m.target.classList.contains("thumb-card") && m.target.classList.contains("excluded") && isReq(keyOfCard(m.target)); }))
        setTimeout(lockCards, 0);
    }).observe(build, { subtree: true, attributes: true, attributeFilter: ["class"] });
  }

  /* ------------------------------------------------------------ Edit slides */
  var slideKey = function (i) { var s = window.WORKSPACE_SLIDES && WORKSPACE_SLIDES[i]; return s && s.key; };
  function wrapDelete() {
    var del = window.wsDeleteByIndices;
    if (!del || del.__req) return;
    window.wsDeleteByIndices = function (indices) {
      var keep = indices.filter(function (i) { return !isReq(slideKey(i)); });
      if (keep.length < indices.length) {
        if (!keep.length) { alert("Company slides are part of every deck and can't be deleted."); return; }
        alert("Company slides are part of every deck, so they were kept. The other selected slides will be deleted.");
      }
      return del.call(this, keep);
    };
    window.wsDeleteByIndices.__req = 1;
  }
  function wrapReplace() {
    var rep = window.wsOpenReplacePicker;
    if (!rep || rep.__req) return;
    window.wsOpenReplacePicker = function (idx) {
      if (isReq(slideKey(idx))) { alert("Company slides are part of every deck and can't be replaced."); return; }
      return rep.apply(this, arguments);
    };
    window.wsOpenReplacePicker.__req = 1;
  }
  function wrapPanel() {
    var rwr = window.renderWsRight;
    if (!rwr || rwr.__req) return;
    window.renderWsRight = function () {
      var r = rwr.apply(this, arguments);
      try {
        if (isReq(slideKey(window.wsActiveIndex))) {
          var bar = document.querySelector("#wsRight .ws-slide-actions");
          if (bar && !bar.querySelector(".ws-req-note")) {
            bar.querySelectorAll("button").forEach(function (b) { b.classList.add("is-locked"); b.disabled = true; });
            var n = document.createElement("p");
            n.className = "ws-req-note";
            n.textContent = "🔒 Company slide: always in the deck. You can edit it and move it, but not delete or replace it.";
            bar.appendChild(n);
          }
        }
      } catch (e) {}
      return r;
    };
    window.renderWsRight.__req = 1;
  }
  // the "..." slide menu: grey out Replace / Delete on compulsory slides
  function wrapMenu() {
    var om = window.wsOpenSlideMenu;
    if (!om || om.__req) return;
    window.wsOpenSlideMenu = function (btn, idx) {
      var r = om.apply(this, arguments);
      if (isReq(slideKey(idx))) {
        var menu = document.querySelector(".ws-slide__menu.is-open");
        if (menu) menu.querySelectorAll("button").forEach(function (b) { b.classList.add("is-locked"); b.disabled = true; });
      }
      return r;
    };
    window.wsOpenSlideMenu.__req = 1;
  }

  function start() { watch(); wrapDelete(); wrapReplace(); wrapPanel(); wrapMenu(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
