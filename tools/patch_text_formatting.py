# -*- coding: utf-8 -*-
"""Text boxes on new slides: Header / Sub header / Body, bold, colour, in the
deck's own typeface. Edits src/frontend/app.html (kept for provenance)."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "src", "frontend", "app.html")
s = open(p, encoding="utf-8").read()


def sw(o, n):
    global s
    assert s.count(o) == 1, (s.count(o), o[:80])
    s = s.replace(o, n)


# ---- CSS: deck font + three text styles + the formatting row
sw("  .cs-text-block{font-size:22px; line-height:1.4; color:#222; min-height:1.4em; margin:0; padding:6px; background:rgba(255,255,255,.01);}",
   """  /* Text boxes on new slides: the deck's own typeface (TT Norms Pro) and three
     styles sized to match the other slides' hierarchy on this 1180px canvas. */
  .cs-text-block{font-family:var(--font-body,"TT Norms Pro",Arial,sans-serif); font-size:20px; line-height:1.45; font-weight:400; color:#111; min-height:1.4em; margin:0; padding:6px; white-space:pre-wrap; background:rgba(255,255,255,.01);}
  .cs-text-block.cs-t-header{font-size:46px; line-height:1.08; font-weight:700; letter-spacing:-0.03em;}
  .cs-text-block.cs-t-sub{font-size:28px; line-height:1.2; font-weight:700; letter-spacing:-0.015em;}
  .cs-text-block.is-bold{font-weight:700;}
  .cs-text-block.is-regular{font-weight:400;}
  .ws-text-fmt{display:flex; flex-direction:column; gap:8px; padding:8px 0 2px; border-top:1px solid var(--line);}
  .ws-text-fmt[hidden]{display:none;}
  .ws-text-fmt__row{display:flex; align-items:center; gap:6px; flex-wrap:wrap;}
  .ws-text-fmt__label{font-size:0.62rem; font-weight:700; text-transform:uppercase; letter-spacing:.05em; color:var(--muted); width:38px;}
  .ws-seg{display:flex; border:1px solid var(--line-strong); border-radius:8px; overflow:hidden;}
  .ws-seg button, .ws-fmt-bold{appearance:none; border:0; background:var(--surface); color:var(--ink); font-family:var(--font-ui); font-size:0.74rem; font-weight:600; padding:6px 10px; cursor:pointer;}
  .ws-seg button + button{border-left:1px solid var(--line-strong);}
  .ws-seg button.is-active, .ws-fmt-bold.is-active{background:var(--ink); color:var(--paper);}
  .ws-fmt-bold{border:1px solid var(--line-strong); border-radius:8px; width:34px; padding:6px 0; font-size:0.85rem; font-weight:800;}
  .ws-fmt-swatches{display:flex; gap:5px; align-items:center;}
  .ws-fmt-swatch{width:20px; height:20px; border-radius:50%; border:1px solid rgba(0,0,0,.25); cursor:pointer; padding:0;}
  .ws-fmt-swatch.is-active{outline:2px solid var(--accent); outline-offset:2px;}
  .ws-fmt-color{display:flex; align-items:center; gap:6px; font-size:0.72rem; color:var(--muted); cursor:pointer;}
  .ws-fmt-color input{width:26px; height:24px; padding:0; border:1px solid var(--line-strong); border-radius:6px; background:none; cursor:pointer;}""")

# ---- rendering: size / bold / colour come from the slide's data model
sw("""        '<p class="cs-text-block">' + escapeHtml(el.text || 'Click to add text') + '</p>' +""",
   """        '<p class="' + csTextClass(el) + '"' + csTextStyle(el) + '>' + escapeHtml(el.text || 'Click to add text') + '</p>' +""")
sw("  function renderCsElement(el){", """  function csTextSize(el){ return el.size === 'header' || el.size === 'sub' ? el.size : 'body'; }
  function csTextClass(el){
    return 'cs-text-block cs-t-' + csTextSize(el) + (el.bold === true ? ' is-bold' : (el.bold === false ? ' is-regular' : ''));
  }
  function csTextStyle(el){
    return (el.color && /^#[0-9a-fA-F]{6}$/.test(el.color)) ? ' style="color:' + el.color + '"' : '';
  }
  function csTextDefaultWidth(el){ var z = csTextSize(el); return z === 'header' ? 760 : (z === 'sub' ? 560 : 420); }

  function renderCsElement(el){""")

# ---- a text box is as tall as its text
sw("""    var w = el.w || box.w, h = el.h || box.h;
    var x = el.x || 0, y = el.y || 0;
    return 'left:' + x + 'px; top:' + y + 'px; width:' + w + 'px; height:' + h + 'px;';""",
   """    var w = el.w || (el.type === 'text' ? csTextDefaultWidth(el) : box.w), h = el.h || box.h;
    var x = el.x || 0, y = el.y || 0;
    // a text box is as tall as its text (so a Header never spills out of a fixed-height box)
    var height = (el.type === 'text' && !el.h) ? '' : ' height:' + h + 'px;';
    return 'left:' + x + 'px; top:' + y + 'px; width:' + w + 'px;' + height;""")

# ---- the click-to-edit popup gets the formatting row (new-slide text boxes only)
sw("""    '<textarea></textarea>' +
    '<div class="ws-text-popup__row">' +
      '<span class="ws-text-popup__hint" style="margin-right:auto;">Esc to cancel</span>' +
      '<button type="button" class="btn" id="wsTextPopupCancel">Cancel</button>' +""",
   """    '<textarea></textarea>' +
    '<div class="ws-text-fmt" id="wsTextFmt" hidden>' +
      '<div class="ws-text-fmt__row"><span class="ws-text-fmt__label">Style</span>' +
        '<div class="ws-seg" id="wsFmtSize"><button type="button" data-size="header">Header</button><button type="button" data-size="sub">Sub header</button><button type="button" data-size="body">Body</button></div></div>' +
      '<div class="ws-text-fmt__row"><span class="ws-text-fmt__label">Text</span>' +
        '<button type="button" class="ws-fmt-bold" id="wsFmtBold" title="Bold">B</button>' +
        '<div class="ws-fmt-swatches" id="wsFmtSwatches"></div>' +
        '<label class="ws-fmt-color" title="Any colour"><input type="color" id="wsFmtColor" value="#111111"></label></div>' +
    '</div>' +
    '<div class="ws-text-popup__row">' +
      '<span class="ws-text-popup__hint" style="margin-right:auto;">Esc to cancel</span>' +
      '<button type="button" class="btn" id="wsTextPopupCancel">Cancel</button>' +""")

sw("""  function wsOpenTextPopup(el){
    wsTextPopupTarget = el;
    wsTextPopupTextarea.value = el.textContent;
    wsTextPopup.classList.add("is-open");""", """  // ---- formatting for text boxes on new (custom) slides: Header / Sub header /
  // Body, bold, colour. Written to the slide's data model (and the live DOM),
  // so it survives re-renders, autosave and the shared link. ----
  var WS_FMT_COLORS = ["#111111", "#555555", "#e5222a", "#1f4e9c", "#1f7a4d", "#ffffff"];
  var wsFmtSwatches = document.getElementById("wsFmtSwatches");
  wsFmtSwatches.innerHTML = WS_FMT_COLORS.map(function(c){
    return '<button type="button" class="ws-fmt-swatch" data-color="' + c + '" style="background:' + c + '" title="' + c + '"></button>';
  }).join("");
  function wsCsTextCtx(){
    var t = wsTextPopupTarget;
    var sec = t && t.closest && t.closest("[data-cs-section]");
    if(!sec) return null;
    var slideEl = sec.closest(".ws-slide");
    var slide = WORKSPACE_SLIDES[slideEl ? +slideEl.getAttribute("data-index") : -1];
    var el = slide && slide.elements && slide.elements.find(function(e){ return e.id === sec.getAttribute("data-cs-id"); });
    return el && el.type === "text" ? {el: el, p: t, sec: sec} : null;
  }
  function wsFmtSync(ctx){
    var el = ctx.el, size = csTextSize(el);
    document.querySelectorAll("#wsFmtSize button").forEach(function(b){ b.classList.toggle("is-active", b.getAttribute("data-size") === size); });
    var bold = el.bold === true || (el.bold === undefined && size !== "body");
    document.getElementById("wsFmtBold").classList.toggle("is-active", bold);
    var color = (el.color || "#111111").toLowerCase();
    document.getElementById("wsFmtColor").value = color;
    wsFmtSwatches.querySelectorAll(".ws-fmt-swatch").forEach(function(b){ b.classList.toggle("is-active", b.getAttribute("data-color") === color); });
  }
  function wsFmtApply(patch){
    var ctx = wsCsTextCtx();
    if(!ctx) return;
    Object.assign(ctx.el, patch);
    var p = ctx.p;
    p.classList.remove("cs-t-header", "cs-t-sub", "cs-t-body", "is-bold", "is-regular");
    p.classList.add("cs-t-" + csTextSize(ctx.el));
    if(ctx.el.bold === true) p.classList.add("is-bold"); else if(ctx.el.bold === false) p.classList.add("is-regular");
    p.style.color = ctx.el.color || "";
    if(!ctx.el.w) ctx.sec.style.width = csTextDefaultWidth(ctx.el) + "px";
    wsFmtSync(ctx);
    if(typeof markAutosaveDirty === "function") markAutosaveDirty();
  }
  document.getElementById("wsFmtSize").addEventListener("click", function(e){
    var b = e.target.closest("button[data-size]");
    if(b) wsFmtApply({size: b.getAttribute("data-size"), bold: undefined});
  });
  document.getElementById("wsFmtBold").addEventListener("click", function(){
    var ctx = wsCsTextCtx(); if(!ctx) return;
    var bold = ctx.el.bold === true || (ctx.el.bold === undefined && csTextSize(ctx.el) !== "body");
    wsFmtApply({bold: !bold});
  });
  wsFmtSwatches.addEventListener("click", function(e){
    var b = e.target.closest(".ws-fmt-swatch");
    if(b) wsFmtApply({color: b.getAttribute("data-color")});
  });
  document.getElementById("wsFmtColor").addEventListener("input", function(){ wsFmtApply({color: this.value}); });

  function wsOpenTextPopup(el){
    wsTextPopupTarget = el;
    wsTextPopupTextarea.value = el.textContent;
    var csCtx = wsCsTextCtx();
    document.getElementById("wsTextFmt").hidden = !csCtx;
    if(csCtx) wsFmtSync(csCtx);
    wsTextPopup.classList.add("is-open");""")
sw("    if(top + 160 > window.innerHeight) top = Math.max(8, r.top - 168);",
   "    var popH = csCtx ? 270 : 160;\n    if(top + popH > window.innerHeight) top = Math.max(8, r.top - popH - 8);")

open(p, "w", encoding="utf-8").write(s)
print("ok")
