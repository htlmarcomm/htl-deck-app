/* Easier for everyone:
   - "How it works" help (sidebar button + a first-visit note on the start page)
   - slides open big enough to read when you start editing
   - plain names on the zoom buttons
   - the right-hand panel keeps rarely used parts folded away until you need them */
(function () {
  "use strict";
  if (window.__HTL_SHARE_TOKEN__) return;
  function $(id) { return document.getElementById(id); }
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) {} return null; }

  /* ------------------------------------------------------------ help */
  var host = $("appHeaderUser");
  if (host) {
    var info = $("appHeaderUserInfo");
    var hb = document.createElement("button");
    hb.type = "button";
    hb.className = "link-btn nav-item nav-item--help";
    hb.id = "helpBtn";
    hb.title = "How this works";
    hb.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg><span>How it works</span>';
    host.insertBefore(hb, info);
  }
  var modal = document.createElement("div");
  modal.className = "help-modal";
  modal.innerHTML =
    '<div class="help-box" role="dialog" aria-modal="true" aria-label="How it works">' +
      "<h3>How to make a deck</h3>" +
      '<p class="sub">Three steps. Nothing you do is lost &mdash; your work is saved by itself.</p>' +
      '<div class="help-step"><div class="help-step__n">1</div><div><h4>Choose your slides</h4><p>On the start page pick <b>Use a ready-made deck</b> or <b>Make your own deck</b>. Point at any slide to see it bigger. Click a slide to add it or leave it out, then give the deck a name and press <b>Next</b>.</p></div></div>' +
      '<div class="help-step"><div class="help-step__n">2</div><div><h4>Change what you need</h4><p>Click any text to change it. Point at a photo and press <b>Change photo</b>. Drag the &#10303; handle to move a slide. Click the <b>+</b> between two slides to add a new one. Made a mistake? Press <b>Undo</b>.</p></div></div>' +
      '<div class="help-step"><div class="help-step__n">3</div><div><h4>Share it</h4><p>Press <b>Finish &amp; share</b>. You get a link to send. Anyone with the link can look at the deck &mdash; they cannot change it.</p></div></div>' +
      '<div class="help-tips"><b>Good to know</b><br>&bull; <b>My decks</b> (left menu) lists every deck you have made. Click one to carry on.<br>&bull; The slide is shown small so the whole slide fits &mdash; press <b>Bigger</b> above the slides to enlarge it.<br>&bull; Someone sent you an Excel, PDF or PowerPoint? Open <b>Your files</b> on the right of the editor and pick just the parts you need.</div>' +
      '<div class="help-box__foot"><button type="button" class="btn btn--accent btn--lg" id="helpClose">Got it</button></div>' +
    "</div>";
  document.body.appendChild(modal);
  function openHelp() { modal.classList.add("is-open"); }
  function closeHelp() { modal.classList.remove("is-open"); store("htl_help_seen", "1"); var b = $("helpBanner"); if (b) b.remove(); }
  modal.addEventListener("click", function (e) { if (e.target === modal || e.target.closest("#helpClose")) closeHelp(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && modal.classList.contains("is-open")) closeHelp(); });
  document.addEventListener("click", function (e) { if (e.target.closest("#helpBtn") || e.target.closest("[data-open-help]")) openHelp(); });

  var home = document.querySelector('.screen[data-screen="home"]');
  if (home && !store("htl_help_seen")) {
    var bn = document.createElement("div");
    bn.className = "help-banner";
    bn.id = "helpBanner";
    bn.innerHTML = '<span><b>New here?</b> See how to make a deck in one minute.</span><button type="button" class="btn btn--sm" data-open-help>Show me how</button><button type="button" class="help-banner__x" id="helpHide">No thanks</button>';
    home.insertBefore(bn, home.querySelector(".home-grid"));
    bn.querySelector("#helpHide").addEventListener("click", function () { store("htl_help_seen", "1"); bn.remove(); });
  }

  /* ------------------------------------------------------------ plain words on the zoom buttons */
  var out = $("wsZoomOut"), inn = $("wsZoomIn"), fit = $("wsZoomFit"), full = $("wsZoom100");
  if (out) { out.textContent = "Smaller"; out.title = "Make the slides smaller"; }
  if (inn) { inn.textContent = "Bigger"; inn.title = "Make the slides bigger"; }
  if (fit) { fit.textContent = "Fit to window"; fit.title = "Make the slide fill the space"; }
  if (full) full.style.display = "none";

  // open the editor with slides big enough to read
  var _act = window.activateScreen;
  window.activateScreen = function (name) {
    var r = _act.apply(this, arguments);
    if (name === "workspace") {
      var tries = 0;
      (function fitIt() {
        var left = $("wsLeft");
        if (left && left.querySelector(".ws-slide") && fit) { fit.click(); return; }
        if (tries++ < 20) setTimeout(fitIt, 150);
      })();
    }
    return r;
  };

  /* ------------------------------------------------------------ right-hand panel: fold the extras */
  var opened = {};
  function sources() { try { return window.HTLSources ? HTLSources.exportState().length : 0; } catch (e) { return 0; } }
  function fold() {
    var right = $("wsRight");
    if (!right) return;
    [[".src-panel", "files"], [".ovl-sec", "logo"]].forEach(function (pair) {
      var sec = right.querySelector(pair[0]), key = pair[1];
      if (!sec) return;
      var h = sec.querySelector("h5");
      if (!h || sec.classList.contains("is-collapsible")) return;
      sec.classList.add("is-collapsible");
      var open = key in opened ? opened[key] : (key === "logo" ? true : sources() > 0);
      sec.classList.toggle("is-collapsed", !open);
      h.addEventListener("click", function (e) {
        if (e.target.closest("button, input, a")) return;
        var nowCollapsed = sec.classList.toggle("is-collapsed");
        opened[key] = !nowCollapsed;
      });
    });
  }
  var right = $("wsRight");
  if (right && window.MutationObserver) {
    var busy = false;
    new MutationObserver(function () {
      if (busy) return;
      busy = true;
      requestAnimationFrame(function () { busy = false; try { fold(); } catch (e) {} });
    }).observe(right, { childList: true });
  }
})();
