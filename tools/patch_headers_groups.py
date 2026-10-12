# -*- coding: utf-8 -*-
"""1) Better header-row detection for sheets (project-schedule files have a few
description lines above a very wide header row). 2) Drop the empty day columns of
wide schedules. 3) Group pasted/PowerPoint text by slide, with 'add all' and search."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def edit(path, pairs):
    p = os.path.join(ROOT, path)
    s = open(p, encoding="utf-8").read()
    for o, n in pairs:
        assert s.count(o) == 1, (path, s.count(o), o[:80])
        s = s.replace(o, n)
    open(p, "w", encoding="utf-8").write(s)


# ---------------------------------------------------------------- table-import.js
edit("public/table-import.js", [
    (r'''    var h = -1;
    for (var i = 0; i < rows.length - 1; i++) {
      if (filled(rows[i]) >= 2 && filled(rows[i + 1]) >= 2) { h = i; break; }
    }
    if (h < 0) h = 0;
    var title = rows.slice(0, h).map(function (r) { return r.filter(Boolean).join(" "); }).join(" ").trim();''',
     r'''    // header row = the first row (within the top 25) that is nearly as full as the fullest row,
    // so a few description lines above a wide schedule header are skipped
    var maxFill = 0;
    rows.slice(0, 25).forEach(function (r) { maxFill = Math.max(maxFill, filled(r)); });
    var h = -1;
    for (var i = 0; i < Math.min(rows.length - 1, 25); i++) {
      if (filled(rows[i]) >= 2 && filled(rows[i]) >= maxFill * 0.6 && filled(rows[i + 1]) >= 2) { h = i; break; }
    }
    if (h < 0) h = 0;
    var title = rows.slice(0, h).map(function (r) { return r.filter(Boolean).join(" "); }).filter(Boolean)[0] || "";'''),
    (r'''      var emptyCol = !vals.length && !h;
      if (!mostlyX && !emptyCol) keep.push(c);''',
     r'''      var emptyCol = !vals.length && (!h || t.header.length >= 20);
      if (!mostlyX && !emptyCol) keep.push(c);'''),
])

# ---------------------------------------------------------------- sources.js
edit("public/sources.js", [
    (r'''  function blockHtml(src, b) {''',
     r'''  function groupHtml(src, where, list) {
    return '<div class="src-block src-group" data-src="' + src.id + '" data-where="' + esc(where) + '">' +
      '<div class="src-where">' + esc(where || "Text") + " · " + list.length + ' piece' + (list.length > 1 ? "s" : "") + "</div>" +
      list.map(function (b) { return blockHtml(src, b, true); }).join("") +
      (list.length > 1 ? '<button type="button" class="btn" data-addgroup>Add all of this as one text box</button>' : "") + "</div>";
  }
  function blockHtml(src, b, inGroup) {'''),
    (r'''    return '<div class="src-block" data-src="' + src.id + '" data-blk="' + b.id + '">' +
      (b.where ? '<div class="src-where">' + esc(b.where) + "</div>" : "") +
      '<div class="src-text">' + esc(b.text) + '</div><button type="button" class="btn" data-addtext>Add as a text box</button></div>';''',
     r'''    return '<div class="' + (inGroup ? "src-piece" : "src-block") + '" data-src="' + src.id + '" data-blk="' + b.id + '" data-text="' + esc(b.text.toLowerCase()) + '">' +
      (!inGroup && b.where ? '<div class="src-where">' + esc(b.where) + "</div>" : "") +
      '<div class="src-text">' + esc(b.text) + '</div><button type="button" class="btn" data-addtext>Add as a text box</button></div>';'''),
    (r'''      src.blocks.slice(0, 60).forEach(function (b) { h += blockHtml(src, b); });
      if (src.blocks.length > 60) h += '<p class="src-help">…and ' + (src.blocks.length - 60) + " more pieces of text.</p>";''',
     r'''      if (src.blocks.length > 6) h += '<input class="src-q" placeholder="Search the text…" data-qb>';
      var order = [], by = {};
      src.blocks.forEach(function (b) { var k = b.where || ""; if (!by[k]) { by[k] = []; order.push(k); } by[k].push(b); });
      order.forEach(function (k) { h += groupHtml(src, k, by[k]); });'''),
    (r'''      var box = e.target.closest(".src-table");
      if (!box) {
        var blk = e.target.closest(".src-block");
        if (blk && e.target.closest("[data-addtext]")) {
          var s = items.find(function (x) { return x.id === blk.getAttribute("data-src"); });
          var b = s && s.blocks.find(function (x) { return x.id === blk.getAttribute("data-blk"); });
          if (b) addText(b.text);
        }
        return;
      }''',
     r'''      var box = e.target.closest(".src-table");
      if (!box) {
        var grp = e.target.closest("[data-addgroup]");
        if (grp) {
          var gb = grp.closest(".src-group"), gs = items.find(function (x) { return x.id === gb.getAttribute("data-src"); });
          var w = gb.getAttribute("data-where");
          if (gs) addText(gs.blocks.filter(function (x) { return (x.where || "") === w; }).map(function (x) { return x.text; }).join("\n\n"));
          return;
        }
        var blk = e.target.closest("[data-addtext]");
        if (blk) {
          var pc = blk.closest("[data-blk]");
          var s = items.find(function (x) { return x.id === pc.getAttribute("data-src"); });
          var b = s && s.blocks.find(function (x) { return x.id === pc.getAttribute("data-blk"); });
          if (b) addText(b.text);
        }
        return;
      }'''),
    (r'''    panel.addEventListener("input", function (e) {
      var q = e.target.closest("[data-q]");
      if (!q) return;''',
     r'''    panel.addEventListener("input", function (e) {
      var qb = e.target.closest("[data-qb]");
      if (qb) {
        var vb = qb.value.trim().toLowerCase();
        qb.closest(".src-body").querySelectorAll(".src-piece").forEach(function (p) { p.style.display = !vb || p.getAttribute("data-text").indexOf(vb) >= 0 ? "" : "none"; });
        return;
      }
      var q = e.target.closest("[data-q]");
      if (!q) return;'''),
    (r'''".src-block .btn{margin-top:6px; font-size:.72rem; padding:5px 9px;}" +''',
     r'''".src-block .btn, .src-piece .btn{margin-top:6px; font-size:.72rem; padding:5px 9px;}" +
    ".src-piece{padding:7px 0; border-top:1px dashed var(--line);} .src-group > .src-where + .src-piece{border-top:0;}" +'''),
])
print("ok")
