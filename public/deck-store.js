/* Deck store: connects the editor's screens to the real backend.
     - dashboard    <- GET /api/decks
     - workspace    <- autosaves to PUT /api/decks/:id (slide markup + all edits)
     - finalize     -> POST /api/decks/:id/finalize  (version + real share link)
     - history      <- GET /api/decks/:id/versions   (copy / open / revoke links)
     - users        <- /api/users                    (Creator only)
     - pictures     -> POST /api/assets              (window.uploadImage)
     - /s/<token>   -> read-only viewer for share links (no login)
   Loaded last, after the editor's own scripts; it wraps a few of their global
   functions rather than rewriting them. */
(function () {
  "use strict";
  var TOKEN = window.__HTL_SHARE_TOKEN__;
  if (TOKEN) { startViewer(TOKEN); return; }
  if (!window.__HTL_USER__) return;

  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }

  function api(method, url, body) {
    return fetch(url, {
      method: method, credentials: "same-origin",
      headers: body !== undefined ? { "Content-Type": "application/json" } : {},
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }).then(function (r) {
      if (r.status === 401) { window.location.href = "/login"; throw new Error("Not signed in"); }
      return r.json().catch(function () { return {}; }).then(function (j) {
        if (!r.ok) throw Object.assign(new Error(j.error || "Request failed (" + r.status + ")"), { status: r.status });
        return j;
      });
    });
  }

  function ago(iso) {
    var s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
    if (s < 60) return "just now";
    if (s < 3600) return Math.floor(s / 60) + "m ago";
    if (s < 86400) return Math.floor(s / 3600) + "h ago";
    if (s < 86400 * 30) return Math.floor(s / 86400) + "d ago";
    return new Date(iso).toLocaleDateString();
  }
  function uid() { return "s" + Math.random().toString(36).slice(2, 10) + Date.now().toString(36).slice(-4); }

  var css = document.createElement("style");
  css.textContent =
    ".users-grid{display:grid; grid-template-columns:minmax(260px,340px) 1fr; gap:18px; align-items:start;}" +
    "@media (max-width:820px){.users-grid{grid-template-columns:1fr;}}" +
    ".user-row{display:flex; align-items:center; gap:10px; padding:10px 0; border-bottom:1px solid var(--line); font-size:.82rem; flex-wrap:wrap;}" +
    ".user-row:last-child{border-bottom:0;} .user-row__who{flex:1; min-width:150px;} .user-row__who small{display:block; color:var(--muted);}" +
    ".user-row select{border:1px solid var(--line-strong); border-radius:7px; padding:5px 8px; background:var(--surface); color:var(--ink); font-size:.78rem;}" +
    ".user-row.is-off{opacity:.55;}" +
    ".hist-links{display:flex; flex-direction:column; gap:6px; margin-top:8px;}" +
    ".hist-link{display:flex; align-items:center; gap:8px; flex-wrap:wrap; font-size:.76rem;}" +
    ".hist-link code{font-family:var(--font-mono); background:var(--surface-sunken); padding:2px 6px; border-radius:5px;}" +
    ".pill--off{background:var(--accent-wash); color:var(--accent);}" +
    ".fin-error{color:var(--accent); font-size:.8rem; margin-top:10px;}" +
    "#wsDeckTitle[contenteditable=true]{outline:2px solid var(--accent); outline-offset:4px; border-radius:4px;}";
  document.head.appendChild(css);

  var DS = { deck: null, creating: null, name: "", client: "", versions: 0, dirty: false, timer: null, chain: Promise.resolve(), err: false, decks: [] };

  /* ------------------------------------------------------------ pictures */
  // Downsize in the browser (the server accepts up to 4 MB), then store.
  window.uploadImage = function (file) {
    function post(blob) {
      return fetch("/api/assets", { method: "POST", credentials: "same-origin", headers: { "Content-Type": blob.type }, body: blob })
        .then(function (r) {
          return r.json().catch(function () { return {}; }).then(function (j) {
            if (!r.ok) throw new Error(j.error || "Upload failed (" + r.status + ")");
            return j.url;
          });
        });
    }
    var rawOk = /^image\/(jpeg|png|webp|gif)$/.test(file.type) && file.size < 3.9e6;
    if (!window.createImageBitmap) return rawOk ? post(file) : Promise.reject(new Error("This picture type isn't supported"));
    return createImageBitmap(file).then(function (bm) {
      var scale = Math.min(1, 2200 / Math.max(bm.width, bm.height));
      var c = document.createElement("canvas");
      c.width = Math.max(1, Math.round(bm.width * scale)); c.height = Math.max(1, Math.round(bm.height * scale));
      c.getContext("2d").drawImage(bm, 0, 0, c.width, c.height);
      function blobOf(type, q) { return new Promise(function (res) { c.toBlob(res, type, q); }); }
      var png = file.type === "image/png" || file.type === "image/gif" || file.type === "image/webp";
      return blobOf(png ? "image/png" : "image/jpeg", 0.86).then(function (b) {
        if (b && b.size > 3.8e6) return blobOf("image/jpeg", 0.82);
        return b;
      }).then(function (b) {
        if (!b || b.size > 3.95e6) throw new Error("Picture is too large - try a smaller one");
        return post(b);
      });
    }, function () {
      if (rawOk) return post(file);
      throw new Error("This picture type isn't supported");
    });
  };

  /* --------------------------------------------- capture / rehydrate state */
  function isFrameKey(k) { return typeof CAPABILITY_SCREENS !== "undefined" && Object.prototype.hasOwnProperty.call(CAPABILITY_SCREENS, k); }

  // A slide as it is on screen, minus the editing furniture.
  function cleanStage(stage) {
    var clone = stage.cloneNode(true);
    clone.querySelectorAll(".ws-editable-text").forEach(function (el) {
      el.removeAttribute("contenteditable");
      el.classList.remove("ws-editable-text");
      if (!el.getAttribute("class")) el.removeAttribute("class");
    });
    clone.querySelectorAll("[contenteditable]").forEach(function (el) { el.removeAttribute("contenteditable"); });
    clone.querySelectorAll(WS_EDIT_ONLY_SELECTOR).forEach(function (el) { el.remove(); });
    clone.querySelectorAll('[style*="pointer-events"]').forEach(function (el) {
      el.style.pointerEvents = "";
      if (!el.getAttribute("style")) el.removeAttribute("style");
    });
    if (clone.firstElementChild) clearReveal(clone.firstElementChild);
    return clone.innerHTML;
  }

  function captureAll() {
    if (!wsLeft) return;
    wsLeft.querySelectorAll(".ws-slide[data-uid]").forEach(function (el) {
      var id = el.getAttribute("data-uid");
      var entry = WORKSPACE_SLIDES.find(function (s) { return s.uid === id; });
      if (!entry || entry.kind === "custom" || isFrameKey(entry.key)) return;
      var stage = el.querySelector(".thumb-stage");
      if (!stage || !stage.firstElementChild) return;
      entry.html = cleanStage(stage);
    });
  }

  function serialSlides() {
    return WORKSPACE_SLIDES.map(function (s) {
      return { uid: s.uid, key: s.key, label: s.label, kind: s.kind, slots: s.slots || [], elements: s.elements, html: s.html };
    });
  }

  // every slide gets its own object + id (the picker's metadata objects are shared)
  var _init = window.initWorkspace;
  window.initWorkspace = function () {
    if (window.wsBuilt) return;
    captureAll();
    for (var i = 0; i < WORKSPACE_SLIDES.length; i++) {
      var s = WORKSPACE_SLIDES[i];
      if (!s.uid) { s = JSON.parse(JSON.stringify(s)); s.uid = uid(); WORKSPACE_SLIDES[i] = s; }
    }
    return _init.apply(this, arguments);
  };

  var _fill = window.fillSnippets;
  window.fillSnippets = function (root) {
    var scope = root || document;
    var slides = scope.matches && scope.matches(".ws-slide") ? [scope] : Array.prototype.slice.call(scope.querySelectorAll(".ws-slide"));
    slides.forEach(function (el) {
      var entry = WORKSPACE_SLIDES[+el.getAttribute("data-index")];
      if (!entry) return;
      if (entry.uid) el.setAttribute("data-uid", entry.uid);
      var stage = el.querySelector(".thumb-stage[data-key]");
      if (stage && entry.html && !stage.dataset.filled && entry.kind !== "custom" && !isFrameKey(entry.key)) {
        stage.innerHTML = entry.html;
        stage.dataset.filled = "1";
      }
    });
    return _fill.apply(this, arguments);
  };

  /* ------------------------------------------------------------- saving */
  function setSaveText(t) { var el = $("wsAutosave"); if (el) el.textContent = t; }
  window.updateAutosaveText = function () {
    if (DS.err) return setSaveText("Not saved - retrying…");
    if (DS.dirty) return setSaveText("Saving…");
    if (window.wsLastSavedAt) {
      var secs = Math.round((Date.now() - window.wsLastSavedAt) / 1000);
      setSaveText(secs < 2 ? "Saved just now" : "Saved " + secs + "s ago");
    }
  };
  window.markAutosaveDirty = function () {
    DS.dirty = true;
    setSaveText("Saving…");
    clearTimeout(DS.timer);
    DS.timer = setTimeout(saveNow, 1500);
  };
  function saveNow() {
    clearTimeout(DS.timer);
    if (!DS.deck && !DS.creating) return Promise.resolve();
    DS.chain = DS.chain.then(function () { return DS.creating; }).then(function () {
      if (!DS.deck || !DS.dirty) return;
      captureAll();
      DS.dirty = false;
      return api("PUT", "/api/decks/" + DS.deck.id, { name: DS.name, client_name: DS.client || null, state: { slides: serialSlides() } })
        .then(function () { DS.err = false; window.wsLastSavedAt = Date.now(); window.updateAutosaveText(); })
        .catch(function (e) {
          DS.dirty = true; DS.err = true; window.updateAutosaveText();
          if (e && e.status && e.status < 500 && e.status !== 408) setSaveText("Not saved: " + e.message);
          else DS.timer = setTimeout(saveNow, 8000);
        });
    });
    return DS.chain;
  }
  window.addEventListener("beforeunload", function (e) {
    if (DS.dirty) { e.preventDefault(); e.returnValue = ""; }
  });

  var _act = window.activateScreen;
  window.activateScreen = function (name, isBack) {
    var cur = document.querySelector(".screen.is-active");
    var from = cur && cur.getAttribute("data-screen");
    if (from === "workspace" && name !== "workspace" && DS.dirty) saveNow();
    var r = _act.apply(this, arguments);
    if (name === "dashboard") loadDecks();
    if (name === "users") loadUsers();
    return r;
  };

  /* ------------------------------------------------------------ new deck */
  document.addEventListener("click", function (e) {
    var b = e.target.closest('[data-newdeck="1"][data-goto="build"]');
    if (!b) return;
    if (DS.dirty) saveNow();
    DS.deck = null; DS.creating = null; DS.name = ""; DS.client = ""; DS.versions = 0; DS.dirty = false;
    $("buildDeckName").value = ""; $("buildClient").value = "";
  }, true);

  var nextBtn = $("buildNextBtn");
  if (nextBtn) nextBtn.addEventListener("click", function () {
    DS.name = $("buildDeckName").value.trim() || "Untitled deck";
    DS.client = $("buildClient").value.trim();
    $("wsDeckTitle").textContent = DS.name;
    if (!DS.deck && !DS.creating) {
      DS.creating = api("POST", "/api/decks", { name: DS.name, client_name: DS.client || null, state: { slides: [] } })
        .then(function (r) { DS.deck = r.deck; DS.creating = null; return r; })
        .catch(function (err) { DS.creating = null; setSaveText("Could not create the deck: " + err.message); throw err; });
      DS.creating.catch(function () {});
    }
    window.markAutosaveDirty();
  });

  // rename in place
  var title = $("wsDeckTitle");
  if (title) {
    title.addEventListener("click", function () {
      if (title.isContentEditable) return;
      title.contentEditable = "true"; title.focus();
      var r = document.createRange(); r.selectNodeContents(title);
      var sel = getSelection(); sel.removeAllRanges(); sel.addRange(r);
    });
    var endRename = function (cancel) {
      if (!title.isContentEditable) return;
      title.contentEditable = "false";
      var n = title.textContent.replace(/\s+/g, " ").trim();
      if (cancel || !n) { title.textContent = DS.name || "Untitled deck"; return; }
      if (n !== DS.name) { DS.name = n; window.markAutosaveDirty(); }
    };
    title.addEventListener("blur", function () { endRename(false); });
    title.addEventListener("keydown", function (e) {
      if (e.key === "Enter") { e.preventDefault(); title.blur(); }
      else if (e.key === "Escape") { endRename(true); }
    });
  }

  /* ----------------------------------------------------------- dashboard */
  function loadDecks() {
    return api("GET", "/api/decks").then(function (r) { DS.decks = r.decks; renderDash(); }).catch(function (e) {
      var g = $("dashGrid"); if (g && !g.querySelector(".deck-card")) { var em = $("dashEmpty"); if (em) { em.querySelector("strong").textContent = "Could not load decks"; em.querySelector("span").textContent = e.message; em.classList.add("is-visible"); } }
    });
  }

  function cardEl(d) {
    var live = d.status === "finalized" && d.versions > 0;
    var el = document.createElement("div");
    el.className = "deck-card" + (d.archived ? " is-archived" : "");
    el.setAttribute("data-deck-id", d.id);
    el.setAttribute("data-owner", d.owner_username);
    el.setAttribute("data-archived", d.archived ? "1" : "0");
    el.setAttribute("data-search", (d.name + " " + (d.client_name || "")).toLowerCase());
    el.innerHTML =
      '<button class="deck-card__open" data-deck-open="' + esc(d.id) + '">' +
        '<div class="deck-card__thumb"><div class="thumb-stage-wrap"><div class="thumb-stage real-scope" data-key="' + esc(d.first_key || "title_page") + '"></div></div></div>' +
        '<div class="deck-card__body"><div class="deck-card__name">' + esc(d.name) + '</div>' +
        '<div class="deck-card__meta">' + (d.client_name ? "for " + esc(d.client_name) : "no recipient") + '</div>' +
        '<div class="deck-card__row"><span class="pill ' + (live ? "pill--live" : "pill--draft") + '">' + (live ? "shared" : "draft") + '</span>' +
        '<span class="timestamp">' + (d.versions ? "v" + d.versions : "—") + ' &middot; ' + esc(ago(d.updated_at)) + '</span></div></div></button>' +
      '<button type="button" class="deck-card__menu-btn" aria-label="More actions">&#8942;</button>' +
      '<div class="deck-card__menu">' +
        '<button type="button" class="deck-card__menu-item" data-action="open">Open</button>' +
        '<button type="button" class="deck-card__menu-item" data-action="duplicate">Duplicate</button>' +
        '<button type="button" class="deck-card__menu-item" data-action="history">Version history</button>' +
        (d.token ? '<button type="button" class="deck-card__menu-item" data-action="copylink">Copy share link</button>' : "") +
        '<button type="button" class="deck-card__menu-item" data-action="archive">' + (d.archived ? "Unarchive" : "Archive") + '</button>' +
      '</div>';
    return el;
  }

  function renderDash() {
    var grid = $("dashGrid"), empty = $("dashEmpty");
    grid.querySelectorAll(".deck-card").forEach(function (c) { c.remove(); });
    ACCOUNTS.length = 0;
    DS.decks.forEach(function (d) {
      if (!ACCOUNTS.some(function (a) { return a.username === d.owner_username; })) ACCOUNTS.push({ username: d.owner_username, name: d.owner_name });
      grid.insertBefore(cardEl(d), empty);
    });
    fillSnippets(grid);
    applyDashboardFilter();
    refreshDashEmptyState();
    var dl = $("buildClientList");
    if (dl) {
      var seen = {};
      dl.innerHTML = DS.decks.map(function (d) { return d.client_name; }).filter(function (c) { if (!c || seen[c]) return false; return (seen[c] = 1); })
        .map(function (c) { return '<option value="' + esc(c) + '">'; }).join("");
    }
  }

  function openDeck(id) {
    return api("GET", "/api/decks/" + id).then(function (r) {
      var d = r.deck, slides = (d.state && d.state.slides) || [];
      if (DS.dirty) saveNow();
      DS.deck = { id: d.id }; DS.creating = null; DS.name = d.name; DS.client = d.client_name || ""; DS.versions = d.versions; DS.dirty = false; DS.err = false;
      wsIsNewDeck = !d.versions;
      $("wsDeckTitle").textContent = d.name;
      if (!slides.length) { activateScreen("build"); return; }
      WORKSPACE_SLIDES.length = 0;
      slides.forEach(function (s) { WORKSPACE_SLIDES.push(s); });
      wsSelectedIndices = {};
      wsBuilt = false;
      window.wsLastSavedAt = Date.now();
      activateScreen("workspace");
    }).catch(function (e) { alert("Could not open the deck: " + e.message); });
  }

  document.addEventListener("click", function (e) {
    var open = e.target.closest("[data-deck-open]");
    if (open) { e.preventDefault(); openDeck(open.getAttribute("data-deck-open")); return; }
    var item = e.target.closest(".deck-card__menu-item");
    if (!item) return;
    var card = item.closest(".deck-card"), id = card.getAttribute("data-deck-id"), action = item.getAttribute("data-action");
    e.stopImmediatePropagation(); // the prototype's own handler would act on the page only
    document.querySelectorAll(".deck-card__menu.is-open").forEach(function (m) { m.classList.remove("is-open"); });
    var deck = DS.decks.find(function (d) { return d.id === id; }) || {};
    if (action === "open") openDeck(id);
    else if (action === "duplicate") api("POST", "/api/decks/" + id + "/duplicate").then(loadDecks).catch(function (er) { alert(er.message); });
    else if (action === "archive") api("PUT", "/api/decks/" + id, { archived: !deck.archived }).then(loadDecks).catch(function (er) { alert(er.message); });
    else if (action === "history") showHistory(deck);
    else if (action === "copylink") copyText(location.origin + "/s/" + deck.token, item);
  }, true);

  function copyText(text, btn) {
    var done = function () { if (btn) { var t = btn.textContent; btn.textContent = "Copied!"; setTimeout(function () { btn.textContent = t; }, 1500); } };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, function () { window.prompt("Copy this link:", text); });
    else window.prompt("Copy this link:", text);
  }

  /* ------------------------------------------------------------ finalize */
  window.renderFinalizeModal = function () {
    var modal = $("finalizeModal"), first = !DS.versions;
    modal.innerHTML = first
      ? '<h3>Finalize this deck</h3><p class="sub">This freezes the deck as version 1 and creates its share link. Anyone with the link can view it (read-only, no login).</p>' +
        '<div class="fin-error" id="finError" hidden></div>' +
        '<div class="modal-footer"><button class="btn btn--ghost" data-goto="workspace">Cancel</button><button class="btn btn--accent" id="finalizeGo">Create &amp; get link</button></div>'
      : '<h3>Finalize this deck</h3><p class="sub">This deck already has ' + DS.versions + ' finalized version' + (DS.versions > 1 ? "s" : "") + '. Choose what happens to its share link.</p>' +
        '<div class="option-card selected" data-mode="keep"><div class="option-card__head"><span class="radio"></span>Keep previous version</div><p>Creates v' + (DS.versions + 1) + ' and a brand-new link. The existing link keeps showing the older version exactly as before.</p></div>' +
        '<div class="option-card" data-mode="replace"><div class="option-card__head"><span class="radio"></span>Replace current version</div><p>Creates v' + (DS.versions + 1) + ' and points the existing link at it. Same address, new content.</p></div>' +
        '<div class="fin-error" id="finError" hidden></div>' +
        '<div class="modal-footer"><button class="btn btn--ghost" data-goto="workspace">Cancel</button><button class="btn btn--accent" id="finalizeGo">Finalize deck</button></div>';
    modal.querySelectorAll(".option-card").forEach(function (card) {
      card.addEventListener("click", function () {
        modal.querySelectorAll(".option-card").forEach(function (c) { c.classList.remove("selected"); });
        card.classList.add("selected");
      });
    });
    $("finalizeGo").addEventListener("click", function () {
      var btn = this, err = $("finError"), sel = modal.querySelector(".option-card.selected");
      var mode = sel ? sel.getAttribute("data-mode") : "keep";
      btn.disabled = true; btn.textContent = "Working…"; err.hidden = true;
      DS.dirty = true; // force a final save of exactly what is on screen
      saveNow().then(function () {
        if (!DS.deck) throw new Error("The deck has not been saved yet - try again in a moment.");
        var slides = snapshotSlides();
        return api("POST", "/api/decks/" + DS.deck.id + "/finalize", { mode: mode, snapshot: { slides: slides } }).then(function (res) {
          DS.versions = res.versionNum; wsIsNewDeck = false;
          showShare(res, slides);
          activateScreen("share");
        });
      }).catch(function (e) {
        btn.disabled = false; btn.textContent = mode === "keep" && DS.versions ? "Finalize deck" : "Create & get link";
        err.textContent = e.message; err.hidden = false;
      });
    });
  };

  // the slides exactly as a viewer should see them
  function snapshotSlides() {
    var out = [];
    wsLeft.querySelectorAll(".ws-slide").forEach(function (el) {
      var s = WORKSPACE_SLIDES[+el.getAttribute("data-index")], stage = el.querySelector(".thumb-stage");
      if (!s || !stage) return;
      var o = { key: s.key, label: s.label };
      if (isFrameKey(s.key)) { o.html = ALL_SNIPPETS[s.key]; if (MT.edits[s.key]) o.fe = MT.edits[s.key]; }
      else o.html = cleanStage(stage);
      out.push(o);
    });
    return out;
  }

  function showShare(res, slides) {
    var url = location.origin + res.url;
    $("shareChromeUrl").textContent = url.replace(/^https?:\/\//, "");
    $("shareCopyLinkBtn").setAttribute("data-share-url", url);
    $("shareOpenLink").href = url;
    var scroll = $("shareDeckScroll");
    scroll.innerHTML = "";
    slides.forEach(function (s) {
      var wrap = document.createElement("div"); wrap.className = "share-slide";
      var stage = document.createElement("div"); stage.className = "thumb-stage real-scope"; stage.setAttribute("data-key", s.key);
      stage.style.width = "1180px"; stage.innerHTML = s.html; stage.dataset.filled = "1";
      wrap.appendChild(stage); scroll.appendChild(wrap);
    });
    fillSnippets(scroll);
  }

  /* ------------------------------------------------------------- history */
  function showHistory(deck) {
    $("historyTitle").textContent = (deck.name || "Deck") + " — version history";
    var list = $("historyList");
    list.innerHTML = '<div class="empty-state is-visible" style="border:none; padding:40px 20px;"><span>Loading…</span></div>';
    activateScreen("history");
    api("GET", "/api/decks/" + deck.id + "/versions").then(function (r) {
      if (!r.versions.length) {
        list.innerHTML = '<div class="empty-state is-visible" style="border:none; padding:40px 20px;"><strong>No versions yet</strong><span>This deck hasn’t been finalized — finalize it once to create v1 and a share link.</span></div>';
        return;
      }
      list.innerHTML = r.versions.map(function (v, i) {
        var links = v.links.map(function (l) {
          return '<div class="hist-link" data-link="' + esc(l.id) + '" data-token="' + esc(l.token) + '">' +
            '<code>/s/' + esc(l.token) + '</code>' +
            '<span class="pill ' + (l.revoked ? "pill--off" : "pill--live") + '">' + (l.revoked ? "revoked" : "live link") + '</span>' +
            '<span class="timestamp">' + l.views + ' view' + (l.views === 1 ? "" : "s") + '</span>' +
            '<button class="btn btn--sm" data-hist="copy">Copy link</button>' +
            '<a class="btn btn--sm" href="/s/' + esc(l.token) + '" target="_blank" rel="noopener" style="text-decoration:none;">Open</a>' +
            '<button class="btn btn--sm" data-hist="' + (l.revoked ? "restore" : "revoke") + '">' + (l.revoked ? "Turn back on" : "Revoke") + '</button></div>';
        }).join("");
        return '<div class="history-row" style="align-items:flex-start;"><div class="history-row__left" style="align-items:flex-start;">' +
          '<span class="history-row__version">v' + v.version_num + '</span><div><div><strong>' + (i === 0 ? "Latest version" : "Earlier version") + '</strong></div>' +
          '<div class="history-row__meta">Finalized ' + esc(ago(v.created_at)) + (v.created_by ? " by " + esc(v.created_by) : "") + '</div>' +
          '<div class="hist-links">' + (links || '<span class="history-row__meta">No link points at this version.</span>') + '</div></div></div></div>';
      }).join("");
    }).catch(function (e) { list.innerHTML = '<div class="empty-state is-visible" style="border:none;"><strong>Could not load</strong><span>' + esc(e.message) + '</span></div>'; });
  }
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-hist]");
    if (!b) return;
    var row = b.closest("[data-link]"), id = row.getAttribute("data-link"), what = b.getAttribute("data-hist");
    if (what === "copy") return copyText(location.origin + "/s/" + row.getAttribute("data-token"), b);
    var call = what === "revoke" ? api("DELETE", "/api/links/" + id) : api("PATCH", "/api/links/" + id, {});
    call.then(function () {
      var pill = row.querySelector(".pill"), off = what === "revoke";
      pill.className = "pill " + (off ? "pill--off" : "pill--live"); pill.textContent = off ? "revoked" : "live link";
      b.setAttribute("data-hist", off ? "restore" : "revoke"); b.textContent = off ? "Turn back on" : "Revoke";
    }).catch(function (er) { alert(er.message); });
  });

  /* --------------------------------------------------------------- users */
  function loadUsers() {
    var box = $("userList");
    api("GET", "/api/users").then(function (r) {
      box.innerHTML = r.users.map(function (u) {
        return '<div class="user-row' + (u.active ? "" : " is-off") + '" data-uid="' + esc(u.id) + '">' +
          '<div class="user-row__who"><strong>' + esc(u.name) + '</strong><small>' + esc(u.username) + (u.active ? "" : " · deactivated") + '</small></div>' +
          '<select data-u="role"><option value="user"' + (u.role === "user" ? " selected" : "") + '>User</option><option value="creator"' + (u.role === "creator" ? " selected" : "") + '>Creator</option></select>' +
          '<button class="btn btn--sm" data-u="pw">Reset password</button>' +
          '<button class="btn btn--sm" data-u="active">' + (u.active ? "Deactivate" : "Reactivate") + '</button></div>';
      }).join("");
      box._users = r.users;
    }).catch(function (e) { box.innerHTML = '<span class="manage-card__note">' + esc(e.message) + "</span>"; });
  }
  var userList = $("userList");
  if (userList) {
    userList.addEventListener("change", function (e) {
      var sel = e.target.closest('[data-u="role"]'); if (!sel) return;
      api("PATCH", "/api/users/" + sel.closest(".user-row").getAttribute("data-uid"), { role: sel.value }).then(loadUsers).catch(function (er) { alert(er.message); loadUsers(); });
    });
    userList.addEventListener("click", function (e) {
      var b = e.target.closest("[data-u]"); if (!b || b.tagName === "SELECT") return;
      var row = b.closest(".user-row"), id = row.getAttribute("data-uid"), u = (userList._users || []).find(function (x) { return x.id === id; }) || {};
      if (b.getAttribute("data-u") === "pw") {
        var pw = window.prompt("New password for " + u.name + " (at least 10 characters):");
        if (!pw) return;
        api("PATCH", "/api/users/" + id, { password: pw }).then(function () { alert("Password changed."); }).catch(function (er) { alert(er.message); });
      } else {
        api("PATCH", "/api/users/" + id, { active: !u.active }).then(loadUsers).catch(function (er) { alert(er.message); });
      }
    });
  }
  var userForm = $("userForm");
  if (userForm) userForm.addEventListener("submit", function (e) {
    e.preventDefault();
    var st = $("userStatus");
    api("POST", "/api/users", { name: $("userName").value, username: $("userUsername").value, password: $("userPassword").value, role: $("userRole").value })
      .then(function () { st.textContent = "Account created."; st.classList.add("is-visible"); userForm.reset(); loadUsers(); })
      .catch(function (er) { st.textContent = er.message; st.classList.add("is-visible"); });
  });

  // first load (enterApp activates the dashboard on DOMContentLoaded, which triggers loadDecks)

  /* ===================================================== public viewer ===== */
  function startViewer(token) {
    document.documentElement.classList.add("deck-review");
    var root = document.createElement("div");
    root.id = "deckReview";
    root.innerHTML = '<header class="dr-head"><h1 id="vTitle">Loading…<span id="vSub"></span></h1><nav><button type="button" class="dr-head__present" id="vPresent" hidden>▶ Present</button></nav></header>' +
      '<div class="dr-group" id="vSlides"></div><div class="dr-present-hint" id="vHint"></div>';
    document.body.appendChild(root);
    var items = [], cur = 0, hint;

    function fail(msg) { root.querySelector("#vSlides").innerHTML = '<div style="padding:80px 20px;text-align:center;font-family:var(--font-ui);color:#333;"><h2 style="margin:0 0 8px;">' + esc(msg) + '</h2><p>Ask the person who sent you this link for a new one.</p></div>'; root.querySelector("#vTitle").textContent = "HTL Aircon"; }

    fetch("/api/share/" + encodeURIComponent(token)).then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); }).then(function (x) {
      if (!x.ok) return fail(x.j.error || "This link is no longer available.");
      var d = x.j;
      document.title = d.name + " — HTL Aircon";
      root.querySelector("#vTitle").innerHTML = esc(d.name) + "<span>" + d.slides.length + " slides</span>";
      var html = "";
      d.slides.forEach(function (s, i) {
        if (s.fe && typeof MT !== "undefined") MT.edits[s.key] = s.fe;
        html += '<div class="dr-item" id="S' + (i + 1) + '"><div class="dr-item__frame"><div class="share-slide"><div class="thumb-stage real-scope" data-key="' + esc(s.key) + '" data-filled="1" style="width:1180px">' + s.html + "</div></div></div></div>";
      });
      root.querySelector("#vSlides").innerHTML = html;
      items = Array.prototype.slice.call(root.querySelectorAll(".dr-item"));
      fillSnippets(root);
      sizeSlides();
      window.addEventListener("resize", sizeSlides);
      var pbtn = root.querySelector("#vPresent"); pbtn.hidden = false;
      hint = root.querySelector("#vHint");
      pbtn.addEventListener("click", startPresenting);
    }).catch(function () { fail("Could not load this deck."); });

    function sizeSlides() {
      var frame = root.querySelector(".dr-item.is-current .dr-item__frame") || root.querySelector(".dr-item__frame");
      if (frame && frame.clientWidth) root.style.setProperty("--dr-zoom", frame.clientWidth / 1180);
    }
    function showSlide(i) {
      cur = Math.max(0, Math.min(items.length - 1, i));
      items.forEach(function (it, j) { it.classList.toggle("is-current", j === cur); });
      hint.textContent = (cur + 1) + " / " + items.length + "   ← →  ·  Esc to exit";
      sizeSlides();
      var stage = items[cur].querySelector(".thumb-stage");
      if (stage && window.playSlideReveal) window.playSlideReveal(stage);
    }
    function startPresenting() {
      var start = 0;
      items.forEach(function (it, j) { if (it.getBoundingClientRect().top < window.innerHeight / 2) start = j; });
      document.documentElement.classList.add("dr-presenting");
      showSlide(start);
      if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen().catch(function () {});
    }
    function stopPresenting() {
      document.documentElement.classList.remove("dr-presenting");
      items.forEach(function (it) { it.classList.remove("is-current"); });
      if (document.fullscreenElement && document.exitFullscreen) document.exitFullscreen().catch(function () {});
      sizeSlides();
      if (items[cur]) items[cur].scrollIntoView({ block: "start" });
    }
    document.addEventListener("keydown", function (e) {
      if (!document.documentElement.classList.contains("dr-presenting")) return;
      if (e.key === "ArrowRight" || e.key === "ArrowDown" || e.key === "PageDown" || e.key === " ") { e.preventDefault(); showSlide(cur + 1); }
      else if (e.key === "ArrowLeft" || e.key === "ArrowUp" || e.key === "PageUp") { e.preventDefault(); showSlide(cur - 1); }
      else if (e.key === "Escape") stopPresenting();
    });
    document.addEventListener("fullscreenchange", function () {
      if (!document.fullscreenElement && document.documentElement.classList.contains("dr-presenting")) stopPresenting();
    });
    root.addEventListener("click", function (e) {
      if (!document.documentElement.classList.contains("dr-presenting") || !e.target.closest(".dr-item")) return;
      if (e.target.closest("a, button")) return;
      showSlide(cur + 1);
    });
  }
})();
