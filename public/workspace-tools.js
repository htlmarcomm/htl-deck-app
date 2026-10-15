/* Edit slides:
   1) Undo / Redo - buttons beside the zoom controls (and Ctrl+Z / Ctrl+Y). Every change to the deck is
      remembered (up to 40 steps); Undo puts the whole deck back the way it was.
   2) Logo / image upload - "Add a logo or image" in the right-hand panel puts a picture on the slide you
      are looking at. Drag it to move it, drag its corner to resize it, x to remove it. */
(function () {
  "use strict";
  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }

  /* ------------------------------------------------------------ styles (also needed by the share page) */
  var st = document.createElement("style");
  st.textContent =
    ".ws-ovl{position:absolute; z-index:30; line-height:0; box-sizing:border-box;}" +
    ".ws-ovl > img{display:block; width:100%; height:auto; max-width:none; pointer-events:none; user-select:none; -webkit-user-drag:none;}" +
    ".ws-slide .ws-ovl{cursor:move; outline:1.5px dashed transparent; outline-offset:2px; touch-action:none;}" +
    ".ws-slide .ws-ovl:hover, .ws-slide .ws-ovl.is-dragging{outline-color:#ef4444;}" +
    ".ws-ovl-del{position:absolute; top:-12px; right:-12px; width:26px; height:26px; border-radius:50%; border:1px solid rgba(17,17,17,.15); background:#fff; color:#111; box-shadow:0 2px 6px rgba(0,0,0,.25); font-size:15px; line-height:24px; padding:0; cursor:pointer; display:none; text-align:center;}" +
    ".ws-ovl-rs{position:absolute; right:-9px; bottom:-9px; width:18px; height:18px; border-radius:50%; background:#ef4444; border:2px solid #fff; box-shadow:0 1px 4px rgba(0,0,0,.35); cursor:nwse-resize; display:none;}" +
    ".ws-ovl:hover .ws-ovl-del, .ws-ovl:hover .ws-ovl-rs, .ws-ovl.is-dragging .ws-ovl-rs{display:block;}" +
    ".ovl-sec .ovl-up{display:inline-flex; margin-top:2px; cursor:pointer;}" +
    ".ovl-sec .ovl-up input{display:none;}" +
    ".ovl-row{display:flex; align-items:center; gap:10px; margin-top:8px; padding:6px; border:1px solid var(--line); border-radius:8px; background:#fff;}" +
    ".ovl-row img{width:44px; height:34px; object-fit:contain; background:#f3f4f6; border-radius:4px;}" +
    ".ovl-row span{flex:1; font-size:.78rem; color:var(--muted);}" +
    ".ovl-msg{font-size:.78rem; color:var(--accent); margin-top:6px;}" +
    ".ws-undo{display:flex; gap:4px; margin-right:10px;}" +
    ".ws-undo .ws-zoom-ctrl__btn{display:inline-flex; align-items:center; gap:5px; padding:0 10px; font-size:.74rem; font-weight:500;}" +
    ".ws-undo svg{width:14px; height:14px; fill:none; stroke:currentColor; stroke-width:2; stroke-linecap:round; stroke-linejoin:round;}";
  document.head.appendChild(st);
  if (window.__HTL_SHARE_TOKEN__) return;

  /* ============================================================ Undo / Redo */
  var undo = [], redo = [], last = null, timer = 0, busy = false, MAX = 40;
  function wsActive() { var s = document.querySelector(".screen.is-active"); return !!s && s.getAttribute("data-screen") === "workspace"; }
  function snap() { try { return window.HTLDeckState ? window.HTLDeckState.snapshot() : null; } catch (e) { return null; } }

  var bar = document.createElement("div");
  bar.className = "ws-zoom-ctrl ws-undo";
  bar.innerHTML =
    '<button type="button" class="ws-zoom-ctrl__btn" id="wsUndo" title="Undo (Ctrl+Z)" disabled><svg viewBox="0 0 24 24"><path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/></svg>Undo</button>' +
    '<button type="button" class="ws-zoom-ctrl__btn" id="wsRedo" title="Redo (Ctrl+Y)" disabled><svg viewBox="0 0 24 24"><path d="m15 14 5-5-5-5"/><path d="M20 9H9.5a5.5 5.5 0 0 0 0 11H13"/></svg>Redo</button>';
  var zoomCtrl = document.querySelector(".screen-head__fields .ws-zoom-ctrl");
  if (zoomCtrl) zoomCtrl.parentNode.insertBefore(bar, zoomCtrl);

  function update() {
    var u = $("wsUndo"), r = $("wsRedo");
    if (u) u.disabled = !undo.length && !timer;
    if (r) r.disabled = !redo.length;
  }
  function record() {
    timer = 0;
    if (busy || !wsActive()) { update(); return; }
    var s = snap();
    if (s == null || s === last) { update(); return; }
    if (last != null) undo.push(last);
    if (undo.length > MAX) undo.shift();
    last = s; redo = [];
    update();
  }
  function apply(s) {
    busy = true;
    try { window.HTLDeckState.restore(s); } catch (e) { if (window.console) console.warn("undo failed", e); }
    setTimeout(function () { busy = false; }, 900);
    update();
  }
  function flush() { if (timer) { clearTimeout(timer); record(); } }
  function doUndo() {
    flush();
    if (!undo.length) return;
    redo.push(last); last = undo.pop(); apply(last);
  }
  function doRedo() {
    flush();
    if (!redo.length) return;
    undo.push(last); last = redo.pop(); apply(last);
  }
  window.HTLHistory = {
    changed: function () {
      if (busy) return;
      clearTimeout(timer);
      timer = setTimeout(record, 600);
      update();
    }
  };
  $("wsUndo").addEventListener("click", doUndo);
  $("wsRedo").addEventListener("click", doRedo);

  // keep the history while you stay in this deck; start fresh when a different deck / slide list shows up
  var _act = window.activateScreen;
  window.activateScreen = function (name) {
    var r = _act.apply(this, arguments);
    if (name === "workspace") {
      setTimeout(function () {
        var s = snap();
        if (s == null) return;
        if (last == null || s !== last) { if (last == null || !busy) { undo = []; redo = []; last = s; update(); } }
      }, 900);
    }
    return r;
  };

  document.addEventListener("keydown", function (e) {
    if (!wsActive()) return;
    var k = (e.key || "").toLowerCase();
    if (!(e.ctrlKey || e.metaKey) || (k !== "z" && k !== "y")) return;
    var t = e.target;
    if (t && (/^(input|textarea|select)$/i.test(t.tagName) || t.isContentEditable)) return; // typing: leave the browser's own undo alone
    e.preventDefault();
    if (k === "y" || (k === "z" && e.shiftKey)) doRedo(); else doUndo();
  });

  /* ============================================================ Logo / image upload */
  function slideStage(i) {
    var el = wsLeft.querySelector('.ws-slide[data-index="' + i + '"]');
    return el && el.querySelector(".thumb-stage");
  }
  function rootBlock(stage) {
    var b = stage && stage.firstElementChild;
    if (!b || b.tagName === "IFRAME" || (b.classList && b.classList.contains("cap-screen"))) return null;
    if (b.classList.contains("cs-slide-canvas")) return b;
    return b;
  }
  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
  function pct(el, prop) { return parseFloat(el.style[prop]) || 0; }

  function wire(d) {
    if (d.getAttribute("data-wired")) return;
    d.setAttribute("data-wired", "1");
    var block = d.parentNode;
    if (!d.querySelector(".ws-ovl-del")) {
      var del = document.createElement("button");
      del.type = "button"; del.className = "ws-ovl-del"; del.title = "Remove this image"; del.textContent = "×";
      var rs = document.createElement("i");
      rs.className = "ws-ovl-rs"; rs.title = "Drag to resize";
      d.appendChild(del); d.appendChild(rs);
    }
    var delBtn = d.querySelector(".ws-ovl-del"), rsEl = d.querySelector(".ws-ovl-rs");
    delBtn.addEventListener("pointerdown", function (e) { e.stopPropagation(); });
    delBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      d.remove();
      window.markAutosaveDirty();
      if (window.renderWsRight) window.renderWsRight();
    });
    function rect() { return d.parentNode.getBoundingClientRect(); }
    d.addEventListener("pointerdown", function (e) {
      if (e.target === delBtn || e.target === rsEl || e.button > 0) return;
      e.preventDefault(); e.stopPropagation();
      var R = rect(), x0 = e.clientX, y0 = e.clientY, l0 = pct(d, "left"), t0 = pct(d, "top");
      d.setPointerCapture(e.pointerId);
      d.classList.add("is-dragging");
      function mv(ev) {
        d.style.left = clamp(l0 + (ev.clientX - x0) / R.width * 100, -20, 105) + "%";
        d.style.top = clamp(t0 + (ev.clientY - y0) / R.height * 100, -20, 105) + "%";
      }
      function up() {
        d.classList.remove("is-dragging");
        d.removeEventListener("pointermove", mv); d.removeEventListener("pointerup", up); d.removeEventListener("pointercancel", up);
        window.markAutosaveDirty();
      }
      d.addEventListener("pointermove", mv); d.addEventListener("pointerup", up); d.addEventListener("pointercancel", up);
    });
    rsEl.addEventListener("pointerdown", function (e) {
      e.preventDefault(); e.stopPropagation();
      var R = rect(), left = d.getBoundingClientRect().left;
      rsEl.setPointerCapture(e.pointerId);
      d.classList.add("is-dragging");
      function mv(ev) { d.style.width = clamp((ev.clientX - left) / R.width * 100, 3, 100) + "%"; }
      function up() {
        d.classList.remove("is-dragging");
        rsEl.removeEventListener("pointermove", mv); rsEl.removeEventListener("pointerup", up); rsEl.removeEventListener("pointercancel", up);
        window.markAutosaveDirty();
      }
      rsEl.addEventListener("pointermove", mv); rsEl.addEventListener("pointerup", up); rsEl.addEventListener("pointercancel", up);
    });
  }
  function wireAll() {
    if (typeof wsLeft === "undefined" || !wsLeft) return;
    Array.prototype.forEach.call(wsLeft.querySelectorAll(".ws-ovl"), wire);
  }
  // slides rebuilt from saved markup lost their controls -> put them back
  var _init = window.initWorkspace;
  window.initWorkspace = function () {
    var r = _init.apply(this, arguments);
    setTimeout(wireAll, 50); setTimeout(wireAll, 600);
    return r;
  };

  function addOverlay(file) {
    var msg = document.querySelector(".ovl-msg");
    if (msg) msg.textContent = "";
    var stage = slideStage(wsActiveIndex), block = rootBlock(stage);
    if (!block) { if (msg) msg.textContent = "This slide can't take a picture."; return; }
    if (getComputedStyle(block).position === "static") block.style.position = "relative";
    var url = URL.createObjectURL(file);
    var d = document.createElement("div");
    d.className = "ws-ovl";
    d.style.left = "5%"; d.style.top = "6%"; d.style.width = "16%";
    var img = document.createElement("img");
    img.alt = "";
    img.src = url;
    d.appendChild(img);
    block.appendChild(d);
    wire(d);
    window.markAutosaveDirty();
    if (window.uploadImage) {
      window.uploadImage(file).then(function (stored) { img.src = stored; window.markAutosaveDirty(); if (window.renderWsRight) window.renderWsRight(); })
        .catch(function (err) { d.remove(); alert("The picture could not be saved: " + (err && err.message || "upload failed")); window.markAutosaveDirty(); });
    }
    if (window.renderWsRight) window.renderWsRight();
  }

  function panel() {
    var right = $("wsRight");
    if (!right || typeof WORKSPACE_SLIDES === "undefined") return;
    var slide = WORKSPACE_SLIDES[wsActiveIndex];
    if (!slide) return;
    var old = right.querySelector(".ovl-sec");
    if (old) old.remove();
    var stage = slideStage(wsActiveIndex), block = rootBlock(stage);
    var sec = document.createElement("div");
    sec.className = "ws-section ovl-sec";
    if (!block || slide.kind === "custom") {
      sec.innerHTML = '<h5>Logo or image</h5><p class="ws-empty-note">' +
        (slide.kind === "custom" ? "On a slide you built yourself, use the picture button on the slide." : "This slide is a fixed picture, so nothing can be added on top of it.") + "</p>";
    } else {
      var items = Array.prototype.slice.call(block.querySelectorAll(".ws-ovl"));
      sec.innerHTML =
        '<h5>Add a logo or image <span class="ws-section__note">on top of this slide</span></h5>' +
        '<p class="ws-empty-note">Pick a picture from your computer. It appears on the slide: drag it to move it, drag the red dot to make it bigger or smaller.</p>' +
        '<label class="btn ovl-up"><input type="file" accept="image/*">+ Upload a logo or image</label>' +
        '<div class="ovl-msg"></div>' +
        items.map(function (it, n) {
          var im = it.querySelector("img");
          return '<div class="ovl-row" data-n="' + n + '"><img src="' + esc(im ? im.getAttribute("src") : "") + '" alt=""><span>Image ' + (n + 1) + ' on this slide</span><button type="button" class="btn btn--sm" data-rm="' + n + '">Remove</button></div>';
        }).join("");
      sec.querySelector("input").addEventListener("change", function () {
        var f = this.files && this.files[0];
        this.value = "";
        if (f) addOverlay(f);
      });
      sec.addEventListener("click", function (e) {
        var b = e.target.closest("[data-rm]");
        if (!b) return;
        var it = items[+b.getAttribute("data-rm")];
        if (it) { it.remove(); window.markAutosaveDirty(); window.renderWsRight(); }
      });
    }
    // right under the slide's own options, above "Your files"
    var files = right.querySelector(".src-panel, .src-sec");
    if (files) right.insertBefore(sec, files); else right.appendChild(sec);
  }
  var _rwr = window.renderWsRight;
  if (_rwr) window.renderWsRight = function () { var r = _rwr.apply(this, arguments); try { panel(); } catch (e) { if (window.console) console.warn(e); } return r; };
})();
