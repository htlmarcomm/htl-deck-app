# -*- coding: utf-8 -*-
"""Adds a "table" element to new (custom) slides: header + rows, click any cell to
edit it, per-row delete, + Add row, drag like the other elements. Created by
"Add slide > Table from a file or paste" (public/deck-store.js). Edits
src/frontend/app.html (kept for provenance)."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "src", "frontend", "app.html")
s = open(p, encoding="utf-8").read()


def sw(o, n):
    global s
    assert s.count(o) == 1, (s.count(o), o[:90])
    s = s.replace(o, n)


# --- rendering
sw("""    if(el.type === 'image'){
      var hasLink = !!el.link;""", """    if(el.type === 'table'){
      var weights = el.weights && el.weights.length === el.header.length ? el.weights : el.header.map(function(){ return 10; });
      var total = weights.reduce(function(a, b){ return a + b; }, 0) || 1;
      var cols = weights.map(function(w){ return '<col style="width:' + (w / total * 100).toFixed(2) + '%">'; }).join('');
      var head = el.header.map(function(h, c){
        return '<th><span data-cs-head="' + c + '">' + escapeHtml(h || ' ') + '</span></th>';
      }).join('');
      var body = el.rows.map(function(r, ri){
        return '<tr>' + r.map(function(v, c){
          return '<td><span data-cs-cell="' + ri + ':' + c + '">' + escapeHtml(v || ' ') + '</span></td>';
        }).join('') + '<td class="cs-ctl"><button type="button" class="cs-row-del" data-cs-del-row="' + ri + '" title="Delete this row">&#10005;</button></td></tr>';
      }).join('');
      return '<div class="cs-table-wrap" data-cs-section data-cs-id="' + el.id + '" style="' + style + '">' +
        CS_HANDLE_HTML +
        '<table class="cs-table"><colgroup>' + cols + '<col style="width:0"></colgroup><thead><tr>' + head + '<th class="cs-ctl"></th></tr></thead><tbody>' + body + '</tbody></table>' +
        '<button type="button" class="cs-add-row" data-cs-add-row="' + el.id + '">+ Add row</button>' +
        '<button type="button" class="cs-section-remove" data-cs-remove="' + el.id + '" title="Remove table">\\u2715</button>' +
      '</div>';
    }
    if(el.type === 'image'){
      var hasLink = !!el.link;""")

sw("var CS_DEFAULT_BOX = { text: {w: 420, h: 90}, image: {w: 380, h: 260}, graph: {w: 460, h: 260} };",
   "var CS_DEFAULT_BOX = { text: {w: 420, h: 90}, image: {w: 380, h: 260}, graph: {w: 460, h: 260}, table: {w: 1060, h: 0} };")
sw("    var height = (el.type === 'text' && !el.h) ? '' : ' height:' + h + 'px;';",
   "    var height = ((el.type === 'text' || el.type === 'table') && !el.h) ? '' : ' height:' + h + 'px;';")
sw("    var w = el.w || (el.type === 'text' ? csTextDefaultWidth(el) : box.w), h = el.h || box.h;",
   "    var w = el.w || (el.type === 'text' ? csTextDefaultWidth(el) : box.w), h = el.h || box.h;")

# --- editing furniture is never part of the slide
sw(".cs-canvas-toolbar, .cs-add-btn, .cs-empty-hint, .cs-image-link-btn, .cs-section-drag-handle, .cs-section-remove';",
   ".cs-canvas-toolbar, .cs-add-btn, .cs-empty-hint, .cs-image-link-btn, .cs-section-drag-handle, .cs-section-remove, .cs-row-del, .cs-add-row';")

# --- saving a cell edit
sw("""          if(csElData.type === "text"){
            csElData.text = newValue;
          } else if(csElData.type === "graph"){""", """          if(csElData.type === "text"){
            csElData.text = newValue;
          } else if(csElData.type === "table"){
            var cellRef = wsTextPopupTarget.getAttribute("data-cs-cell");
            if(cellRef){
              var rc = cellRef.split(":");
              csElData.rows[+rc[0]][+rc[1]] = newValue;
            } else if(wsTextPopupTarget.hasAttribute("data-cs-head")){
              csElData.header[+wsTextPopupTarget.getAttribute("data-cs-head")] = newValue;
            }
          } else if(csElData.type === "graph"){""")

# --- row buttons
sw("""    slideEl.querySelectorAll('[data-cs-link]').forEach(function(btn){""", """    slideEl.querySelectorAll('[data-cs-del-row]').forEach(function(btn){
      btn.addEventListener('click', function(e){
        e.stopPropagation();
        var sec = btn.closest('[data-cs-section]');
        var tbl = slide.elements.find(function(x){ return x.id === sec.getAttribute('data-cs-id'); });
        if(!tbl || tbl.rows.length <= 1) return;
        tbl.rows.splice(+btn.getAttribute('data-cs-del-row'), 1);
        wsRerenderCustomSlide(slideIndex);
      });
    });
    slideEl.querySelectorAll('[data-cs-add-row]').forEach(function(btn){
      btn.addEventListener('click', function(e){
        e.stopPropagation();
        var tbl = slide.elements.find(function(x){ return x.id === btn.getAttribute('data-cs-add-row'); });
        if(!tbl) return;
        tbl.rows.push(tbl.header.map(function(){ return ''; }));
        wsRerenderCustomSlide(slideIndex);
      });
    });
    slideEl.querySelectorAll('[data-cs-link]').forEach(function(btn){""")

# --- styles
CSS = """
  /* ---- table element on new slides (made by "Add slide > Table from a file or paste") ---- */
  .cs-table-wrap{font-family:var(--font-body,"TT Norms Pro",Arial,sans-serif);}
  .cs-table{width:100%; border-collapse:collapse; table-layout:fixed; font-size:17px; line-height:1.25; color:#111;}
  .cs-table th{background:#e5222a; color:#fff; font-weight:700; text-align:left; padding:13px 14px; font-size:16px; letter-spacing:.01em;}
  .cs-table td{padding:10px 14px; border-bottom:1px solid #e4e2dc; vertical-align:middle; overflow-wrap:anywhere;}
  .cs-table tbody tr:nth-child(even) td{background:#f7f6f3;}
  .cs-table th span, .cs-table td span{display:block;}
  .cs-table th.cs-ctl, .cs-table td.cs-ctl{width:0; padding:0; border:0; background:none !important; position:relative; overflow:visible;}
  .cs-row-del{position:absolute; left:8px; top:50%; transform:translateY(-50%); width:20px; height:20px; border-radius:50%; border:1px solid rgba(17,17,17,.2); background:#fff; color:#333; font-size:11px; line-height:1; cursor:pointer; padding:0; opacity:0; transition:opacity .15s ease;}
  .cs-table tr:hover .cs-row-del{opacity:1;}
  .cs-add-row{appearance:none; margin-top:8px; border:1.5px dashed #bbb; background:#fff; color:#555; font-family:var(--font-ui); font-size:12px; font-weight:600; padding:6px 12px; border-radius:8px; cursor:pointer; opacity:0; transition:opacity .15s ease;}
  .cs-table-wrap:hover .cs-add-row{opacity:1;}
  .cs-table-wrap:hover .cs-section-remove{opacity:1;}
"""
sw("  .ws-card-remove{position:absolute; top:6px; right:6px;", CSS + "\n  .ws-card-remove{position:absolute; top:6px; right:6px;")

open(p, "w", encoding="utf-8").write(s)
print("ok")
