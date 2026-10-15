# -*- coding: utf-8 -*-
"""Choose slides: point at a slide and a big preview appears next to it straight away (no small
magnifier button to find). The caption says whether the slide is in the deck and what a click does.
Touch screens (no hover) keep the magnifier button."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def edit(path, pairs):
    p = os.path.join(ROOT, path)
    s = open(p, encoding="utf-8").read()
    for o, n in pairs:
        assert s.count(o) == 1, (path, s.count(o), o[:90])
        s = s.replace(o, n)
    open(p, "w", encoding="utf-8").write(s)


edit("public/picker-tools.js", [
    # the magnifier is for touch screens only
    ('''    "@media (hover:none){.thumb-card__peek{opacity:1; transform:none;}}" +''',
     '''    "@media (hover:none){.thumb-card__peek{opacity:1; transform:none;}} @media (hover:hover){.thumb-card__peek{display:none;}}" +
    /* the big preview that follows the pointer onto a slide */
    ".hv-pop{position:fixed; z-index:850; width:560px; background:#fff; border-radius:14px; box-shadow:0 18px 50px rgba(0,0,0,.35), 0 0 0 1px rgba(17,24,39,.08); overflow:hidden; pointer-events:none; opacity:0; transform:scale(.97); transition:opacity .12s ease, transform .12s ease;}" +
    ".hv-pop.is-on{opacity:1; transform:none;}" +
    ".hv-pop__frame{position:relative; width:560px; height:315px; overflow:hidden; background:#fff;}" +
    ".hv-pop__frame .share-slide{border-radius:0; box-shadow:none;}" +
    ".hv-pop__cap{padding:11px 16px 13px; border-top:1px solid var(--line);}" +
    ".hv-pop__name{font-weight:600; font-size:.92rem; color:#111827;}" +
    ".hv-pop__hint{font-size:.8rem; color:var(--muted); margin-top:3px;}" +'''),
    # hover logic, appended after the preview window code
    ('''  window.addEventListener("resize", function () { if (modal.classList.contains("is-open")) sizeFrame(); });
})();''',
     '''  window.addEventListener("resize", function () { if (modal.classList.contains("is-open")) sizeFrame(); });

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
})();'''),
])

edit("public/home.js", [
    ('''setHint("<b>Tick the slides you want.</b> Click a slide to add it, or use <b>Select all</b> at the top of a section to add all of its slides.");''',
     '''setHint("<b>Tick the slides you want.</b> Click a slide to add it, or use <b>Select all</b> at the top of a section. <b>Point at a slide to see it bigger.</b>");'''),
    ('''<b>Click a slide to leave it out</b> &mdash; click it again to put it back.");''',
     '''<b>Click a slide to leave it out</b> &mdash; click it again to put it back. <b>Point at a slide to see it bigger.</b>");'''),
])
print("ok")
