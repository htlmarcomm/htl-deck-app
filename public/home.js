/* Landing page: "Use a ready-made deck" / "Make your own deck".
   - ready-made: pick the Profile deck or the Capability deck (or a copy of a deck your team already made);
     the slide list is pre-ticked for it
   - make your own: the slide list starts with nothing ticked */
(function () {
  "use strict";
  if (window.__HTL_SHARE_TOKEN__) return;
  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  var build = $("buildScreen");
  if (!build) return;

  var st = document.createElement("style");
  st.textContent =
    ".home-grid{display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:24px; max-width:960px;}" +
    ".home-card{appearance:none; text-align:left; font:inherit; color:var(--ink); background:var(--surface); border:1px solid var(--line); border-radius:16px; box-shadow:var(--shadow); padding:32px 32px 28px; cursor:pointer; display:flex; flex-direction:column; gap:10px; transition:box-shadow .15s, border-color .15s, transform .15s;}" +
    ".home-card:hover{border-color:#fecaca; box-shadow:0 8px 24px -10px rgba(220,38,38,.25); transform:translateY(-2px);}" +
    ".home-card:focus-visible{outline:0; box-shadow:0 0 0 2px #fff, 0 0 0 4px #ef4444;}" +
    ".home-card__icon{width:48px; height:48px; border-radius:12px; background:var(--accent-wash); color:#dc2626; display:flex; align-items:center; justify-content:center; margin-bottom:8px;}" +
    ".home-card__icon svg{width:24px; height:24px; fill:none; stroke:currentColor; stroke-width:1.8; stroke-linecap:round; stroke-linejoin:round;}" +
    ".home-card__title{font-size:1.25rem; font-weight:600; letter-spacing:-0.01em;}" +
    ".home-card__text{font-size:.92rem; line-height:1.5; color:var(--muted); max-width:36ch;}" +
    ".home-card__cta{margin-top:14px; font-size:.88rem; font-weight:600; color:#dc2626;}" +
    ".home-foot{margin-top:26px;} .home-foot .link-btn{font-size:.85rem; font-weight:500;}" +
    ".dash-grid.tpl-grid{grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); max-width:980px; margin-bottom:34px;}" +
    ".tpl-card .deck-card__body{padding:14px 16px 16px;} .tpl-card .deck-card__name{font-size:1rem;}" +
    ".tpl-desc{font-size:.82rem; line-height:1.45; color:var(--muted); margin:6px 0 14px;}" +
    ".tpl-sub{font-size:.95rem; font-weight:600; margin:6px 0 14px;} .tpl-sub span{font-weight:400; color:var(--muted); font-size:.82rem; margin-left:8px;}" +
    "@media (max-width:760px){.home-grid{grid-template-columns:1fr;} .home-card{padding:24px;}}";
  document.head.appendChild(st);

  /* ------------------------------------------------------------ slide list helpers */
  function cardsOf(root) { return Array.prototype.slice.call(root.querySelectorAll(".thumb-card:not(.pending)")); }
  function isOn(c) { return !c.classList.contains("excluded"); }
  function setOn(c, on) { if (isOn(c) !== on) { var b = c.querySelector(".thumb-card__toggle"); if (b) b.click(); } }
  var groups = Array.prototype.slice.call(build.querySelectorAll(".deck-group"));
  // how the page starts out (some placeholder slides are left out on purpose)
  cardsOf(build).forEach(function (c) { c.setAttribute("data-def", isOn(c) ? "1" : "0"); });
  function defOn(c) { return c.getAttribute("data-def") === "1"; }
  function deckNameOf(g) { var t = g.querySelector(".deck-group__title"); return t ? t.childNodes[0].textContent.replace(/^Master\s+/, "").trim() : ""; }

  function setHint(html) {
    var hint = $("buildHint"), cnt = $("buildCount");
    if (!hint) return;
    hint.innerHTML = html + " ";
    if (cnt) hint.appendChild(cnt);
  }
  function refreshPicker() { build.dispatchEvent(new Event("click")); } // picker-tools.js listens for this to redraw its counts

  function startOwn() {
    cardsOf(build).forEach(function (c) { setOn(c, false); });
    setHint("<b>Tick the slides you want.</b> Click a slide to add it, or use <b>Select all</b> at the top of a section. <b>Point at a slide to see it bigger.</b>");
    refreshPicker();
  }
  function startFrom(idx) {
    groups.forEach(function (g, i) {
      cardsOf(g).forEach(function (c) { setOn(c, i === idx ? defOn(c) : false); });
    });
    var nm = groups[idx] ? deckNameOf(groups[idx]) : "";
    setHint("Starting from the <b>" + esc(nm) + "</b>. <b>Click a slide to leave it out</b> &mdash; click it again to put it back. <b>Point at a slide to see it bigger.</b>");
    refreshPicker();
  }

  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-start]");
    if (!b) return;
    var mode = b.getAttribute("data-start");
    setTimeout(function () {
      if (mode === "own") startOwn(); else startFrom(+mode);
      var nm = $("buildDeckName"); if (nm) nm.focus();
      window.scrollTo(0, 0);
    }, 30);
  });

  // a deck needs at least one slide
  document.addEventListener("click", function (e) {
    if (!e.target.closest("#buildNextBtn")) return;
    if (e.defaultPrevented) return;
    if (!cardsOf(build).some(isOn)) {
      e.stopImmediatePropagation(); e.preventDefault();
      var w = $("buildWarn");
      if (!w) { w = document.createElement("span"); w.id = "buildWarn"; w.className = "build-warn"; $("buildNextBtn").parentNode.insertBefore(w, $("buildNextBtn")); }
      w.textContent = "Tick at least one slide first.";
    }
  }, true);

  /* ------------------------------------------------------------ ready-made decks screen */
  function profileCard(i, key, title, desc) {
    var g = groups[i];
    var n = g ? cardsOf(g).filter(defOn).length : 0;
    return '<div class="deck-card tpl-card"><div class="deck-card__thumb"><div class="thumb-stage-wrap"><div class="thumb-stage real-scope" data-key="' + key + '"></div></div></div>' +
      '<div class="deck-card__body"><div class="deck-card__name">' + esc(title) + '</div>' +
      '<div class="deck-card__meta">' + n + ' slides</div>' +
      '<p class="tpl-desc">' + esc(desc) + '</p>' +
      '<button type="button" class="btn btn--accent" data-goto="build" data-newdeck="1" data-start="' + i + '">Use this deck</button></div></div>';
  }
  function renderTemplates() {
    var grid = $("tplGrid");
    grid.innerHTML =
      profileCard(0, "title_page", "Company profile deck", "Our full company profile: about us, projects and sectors, internal systems, safety and quality.") +
      profileCard(1, "capability_title", "Capability deck", "The capability presentation: about HTL, the project, challenges and execution, credentials.");
    if (window.fillSnippets) window.fillSnippets($("buildScreen") ? grid : document);
    fetch("/api/decks", { credentials: "same-origin" }).then(function (r) { return r.json(); }).then(function (j) {
      var made = (j.decks || []).filter(function (d) { return d.versions > 0 && !d.archived; });
      var box = $("tplTeam"), tg = $("tplTeamGrid");
      box.hidden = !made.length;
      tg.innerHTML = made.map(function (d) {
        return '<div class="deck-card tpl-card" data-copy="' + esc(d.id) + '"><button type="button" class="deck-card__open" data-copy-btn="' + esc(d.id) + '">' +
          '<div class="deck-card__thumb"><div class="thumb-stage-wrap"><div class="thumb-stage real-scope" data-key="' + esc(d.first_key || "title_page") + '"></div></div></div>' +
          '<div class="deck-card__body"><div class="deck-card__name">' + esc(d.name) + '</div>' +
          '<div class="deck-card__meta">' + (d.client_name ? "For " + esc(d.client_name) : "No client set") + ' &middot; by ' + esc(d.owner_name || d.owner_username || "") + '</div>' +
          '<span class="btn btn--sm">Use a copy</span></div></button></div>';
      }).join("");
      if (window.fillSnippets) window.fillSnippets(tg);
    }).catch(function () {});
  }
  $("tplTeamGrid").addEventListener("click", function (e) {
    var b = e.target.closest("[data-copy-btn]");
    if (!b || b.disabled) return;
    b.disabled = true;
    fetch("/api/decks/" + encodeURIComponent(b.getAttribute("data-copy-btn")) + "/duplicate", { method: "POST", credentials: "same-origin" })
      .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j.error || "Could not copy the deck"); return j; }); })
      .then(function (j) {
        var go = document.createElement("button");
        go.setAttribute("data-deck-open", j.deck.id);
        document.body.appendChild(go);
        go.click();
        go.remove();
      })
      .catch(function (err) { b.disabled = false; alert(err.message); });
  });

  /* ------------------------------------------------------------ keep the landing page honest */
  function countDecks() {
    fetch("/api/decks", { credentials: "same-origin" }).then(function (r) { return r.json(); }).then(function (j) {
      var n = (j.decks || []).filter(function (d) { return !d.archived; }).length;
      var el = $("homeDeckCount");
      if (el) el.textContent = n ? "(" + n + ") " : "";
    }).catch(function () {});
  }
  var _act = window.activateScreen;
  window.activateScreen = function (name) {
    var r = _act.apply(this, arguments);
    if (name === "templates") renderTemplates();
    if (name === "home") countDecks();
    return r;
  };
  countDecks();
})();
