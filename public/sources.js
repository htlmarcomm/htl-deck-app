/* "Your files": keep the documents you receive (Excel, CSV, PDF, Word, PowerPoint, or pasted
   cells) open beside the slide, then pick just the rows / text you need and place them:
     - rows  -> a new table slide, or added to the table already on the slide you are editing
     - text  -> a text box on the slide you are editing
     - any text you are editing -> "Insert from your files" fills it with a cell or a whole row
   The files' tables and text are saved with the deck. */
(function () {
  "use strict";
  if (!window.__HTL_USER__ || window.__HTL_SHARE_TOKEN__) return;

  var items = [];          // [{id, name, tables:[{id,title,header,rows}], blocks:[{id,text,where}]}]
  var sel = {};            // tableId -> {rowIndex:true}
  var status = "";
  var tidyOn = true;

  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function rid() { return "f" + Math.random().toString(36).slice(2, 9); }
  function changed() { if (typeof markAutosaveDirty === "function") markAutosaveDirty(); }

  var css = document.createElement("style");
  css.textContent =
    ".src-panel{border-top:1px solid var(--line); padding-top:14px;}" +
    ".src-panel h5{font-size:.68rem; font-weight:700; text-transform:uppercase; letter-spacing:.05em; color:var(--muted); margin-bottom:8px; display:flex; gap:8px; align-items:center; flex-wrap:wrap;}" +
    ".src-help{font-size:.76rem; color:var(--muted); line-height:1.5; margin:0 0 10px;}" +
    ".src-addrow{display:flex; gap:8px; flex-wrap:wrap; margin-bottom:10px;}" +
    ".src-addrow .btn{position:relative; overflow:hidden;} .src-addrow input[type=file]{position:absolute; inset:0; opacity:0; cursor:pointer;}" +
    ".src-status{font-size:.74rem; color:var(--draft); margin:0 0 10px; line-height:1.4;} .src-status.is-err{color:var(--accent);}" +
    ".src-drop{border:1.5px dashed var(--line-strong); border-radius:10px; padding:8px 10px; font-size:.72rem; color:var(--muted); text-align:center; margin-bottom:10px;}" +
    ".src-drop.is-over{border-color:var(--accent); background:var(--accent-wash); color:var(--ink);}" +
    ".src-card{border:1px solid var(--line); border-radius:10px; margin-bottom:10px; background:var(--surface);}" +
    ".src-card > summary{cursor:pointer; padding:9px 10px; font-size:.8rem; font-weight:700; display:flex; align-items:center; gap:8px; list-style:none;}" +
    ".src-card > summary::-webkit-details-marker{display:none;} .src-card > summary .src-name{flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;}" +
    ".src-x{appearance:none; border:0; background:transparent; color:var(--muted); font-size:.9rem; cursor:pointer; padding:2px 6px; border-radius:6px;} .src-x:hover{background:var(--surface-sunken); color:var(--accent);}" +
    ".src-body{padding:0 10px 10px;}" +
    ".src-table, .src-block{border-top:1px solid var(--line); padding-top:9px; margin-top:9px;}" +
    ".src-ttl{font-size:.76rem; font-weight:700; margin-bottom:6px;} .src-ttl small{font-weight:500; color:var(--muted);}" +
    ".src-q{width:100%; border:1px solid var(--line-strong); border-radius:7px; padding:6px 9px; font-size:.76rem; background:var(--surface); color:var(--ink); font-family:var(--font-ui); margin-bottom:6px;}" +
    ".src-links{display:flex; gap:12px; font-size:.7rem; margin-bottom:4px;} .src-links button{appearance:none; border:0; background:transparent; padding:0; color:var(--accent); font-weight:600; cursor:pointer; font-family:var(--font-ui); font-size:.7rem;}" +
    ".src-rows{max-height:210px; overflow:auto; border:1px solid var(--line); border-radius:8px;}" +
    ".src-row{display:flex; gap:8px; align-items:flex-start; padding:6px 8px; border-bottom:1px solid var(--line); font-size:.74rem; line-height:1.35; cursor:pointer;} .src-row:last-child{border-bottom:0;}" +
    ".src-row:hover{background:var(--surface-sunken);} .src-row input{margin-top:2px; accent-color:var(--accent); flex-shrink:0;} .src-row span{min-width:0; overflow-wrap:anywhere;} .src-row em{color:var(--muted); font-style:normal;}" +
    ".src-btns{display:flex; flex-direction:column; gap:6px; margin-top:8px;} .src-btns .btn{font-size:.74rem; padding:7px 10px; text-align:center;} .src-btns small{font-size:.68rem; color:var(--muted); text-align:center;}" +
    ".src-text{font-size:.74rem; line-height:1.4; white-space:pre-line; max-height:5.6em; overflow:hidden; color:var(--ink);} .src-where{font-size:.64rem; color:var(--muted); margin-bottom:3px; text-transform:uppercase; letter-spacing:.04em; font-weight:700;}" +
    ".src-block .btn, .src-piece .btn{margin-top:6px; font-size:.72rem; padding:5px 9px;}" +
    ".src-piece{padding:7px 0; border-top:1px dashed var(--line);} .src-group > .src-where + .src-piece{border-top:0;}" +
    ".src-tidy{display:flex; gap:7px; align-items:flex-start; font-size:.72rem; color:var(--muted); margin-bottom:10px; cursor:pointer;}" +
    /* insert-from-files popover in the text editor */
    ".src-ins-btn{align-self:flex-start; appearance:none; border:1px solid var(--line-strong); background:var(--surface); color:var(--ink); font-family:var(--font-ui); font-size:.72rem; font-weight:600; padding:5px 10px; border-radius:7px; cursor:pointer;}" +
    ".src-ins-btn:hover{border-color:var(--accent); color:var(--accent);}" +
    ".src-pop{position:fixed; z-index:420; width:380px; max-width:calc(100vw - 24px); max-height:60vh; background:var(--surface); border:1px solid var(--line-strong); border-radius:12px; box-shadow:0 14px 40px rgba(0,0,0,.35); display:none; flex-direction:column; padding:10px;}" +
    ".src-pop.is-open{display:flex;} .src-pop .src-list{overflow:auto; margin-top:8px;}" +
    ".src-pop .src-item{border-bottom:1px solid var(--line); padding:7px 2px; font-size:.74rem;} .src-pop .src-item:last-child{border-bottom:0;}" +
    ".src-chips{display:flex; flex-wrap:wrap; gap:4px; margin-top:4px;} .src-chip{appearance:none; border:1px solid var(--line-strong); background:var(--surface-sunken); color:var(--ink); border-radius:999px; padding:2px 8px; font-size:.7rem; cursor:pointer; font-family:var(--font-ui);} .src-chip:hover{background:var(--accent); border-color:var(--accent); color:#fff;}" +
    ".src-whole{font-size:.68rem; color:var(--accent); font-weight:700; cursor:pointer; background:none; border:0; padding:0; font-family:var(--font-ui);}";
  document.head.appendChild(css);

  /* ------------------------------------------------------------------ loading libraries */
  var libs = {};
  function loadScript(src) {
    return libs[src] || (libs[src] = new Promise(function (res, rej) {
      var s = document.createElement("script"); s.src = src; s.onload = res; s.onerror = function () { rej(new Error("Could not load " + src)); };
      document.head.appendChild(s);
    }));
  }
  var env = {
    pdfjs: function () { return import("/vendor/pdfjs/pdf.min.mjs").then(function (l) { l.GlobalWorkerOptions.workerSrc = "/vendor/pdfjs/pdf.worker.min.mjs"; return l; }); },
    fflate: function () { return loadScript("/vendor/fflate.min.js").then(function () { return window.fflate; }); },
    xlsx: function () { return loadScript("/vendor/xlsx.full.min.js").then(function () { return window.XLSX; }); },
  };

  /* ------------------------------------------------------------------ adding sources */
  function addParsed(name, parsed) {
    var src = { id: rid(), name: name, tables: [], blocks: [] };
    parsed.tables.forEach(function (t) { src.tables.push({ id: rid(), title: t.title || "", header: t.header, rows: t.rows }); });
    parsed.blocks.forEach(function (b) { src.blocks.push({ id: rid(), text: b.text, where: b.where || "" }); });
    items.push(src);
    changed();
  }
  function setStatus(msg, err) { status = msg ? { msg: msg, err: !!err } : ""; render(); }

  function addFiles(files) {
    var list = Array.prototype.slice.call(files || []);
    if (!list.length) return;
    loadScript("/table-import.js").then(function () {
      return list.reduce(function (p, f) {
        return p.then(function () {
          if (f.size > 15 * 1024 * 1024) { setStatus(f.name + " is larger than 15 MB.", true); return; }
          setStatus("Reading " + f.name + "…");
          return HTLTable.parseAny(f, env).then(function (parsed) { addParsed(f.name, parsed); setStatus(""); })
            .catch(function (e) { setStatus((f.name + ": ") + (e && e.message || "could not be read"), true); });
        });
      }, Promise.resolve());
    });
  }
  function addPaste() {
    var txt = window.prompt("Paste the cells or text here (copy from Excel, Google Sheets, Word…):", "");
    if (!txt || !txt.trim()) return;
    loadScript("/table-import.js").then(function () {
      var t = HTLTable.parseDelimited(txt);
      var parsed = { tables: [], blocks: [] };
      if (t && t.header.length >= 2 && t.rows.length) parsed.tables.push(t);
      else txt.split(/\n\s*\n/).forEach(function (b) { if (b.trim()) parsed.blocks.push({ text: b.trim(), where: "Pasted" }); });
      if (!parsed.tables.length && !parsed.blocks.length) return setStatus("Nothing to add.", true);
      addParsed("Pasted " + new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }), parsed);
      setStatus("");
    });
  }

  /* ------------------------------------------------------------------ using what was picked */
  function norm(s) { return String(s || "").toLowerCase().replace(/[^a-z0-9]/g, ""); }
  function tid(t) { return HTLTable.tidyText(t); }
  function pickedRows(table) {
    var s = sel[table.id] || {};
    return table.rows.filter(function (_, i) { return s[i]; });
  }
  function prep(table, rows) {
    // tidy (optional) and renumber the serial column, because a subset of rows rarely keeps 1..n
    var header = table.header.slice();
    var out = rows.map(function (r) { return r.map(function (c) { return tidyOn ? tid(c) : String(c || ""); }); });
    if (tidyOn) header = header.map(tid);
    var si = header.findIndex(HTLTable.isSerialHeader);
    if (si >= 0) out.forEach(function (r, i) { r[si] = String(i + 1); });
    return { title: table.title, header: header, rows: out.map(function (r) { return r.map(function (c) { return c || "—"; }); }) };
  }
  function activeSlide() { return WORKSPACE_SLIDES[wsActiveIndex]; }
  function activeTableEl() {
    var s = activeSlide();
    return s && s.kind === "custom" && s.elements ? s.elements.find(function (e) { return e.type === "table"; }) : null;
  }

  function newSlide(table) {
    var rows = pickedRows(table);
    if (!rows.length) return;
    if (!window.HTLInsertTableSlides) return setStatus("Please try again in a moment.", true);
    window.HTLInsertTableSlides(wsActiveIndex, prep(table, rows));
    sel[table.id] = {};
    render();
  }
  var CONCEPTS = [
    ["serial", null],
    ["pmc", /pmc|architect|consultant/],
    ["value", /value|amount|cost|price|\brs\b|\bcr\b|crore/],
    ["area", /area|sq\.?\s*ft|sqft|square/],
    ["location", /location|address|city|place|\bsite\b|town/],
    ["scope", /scope|package|detail|service|trade/],
    ["sector", /sector|segment|category|\btype\b/],
    ["name", /name|project|client|customer|company/],
    ["date", /date|start|end|finish|handover/],
  ];
  function concept(h) {
    if (HTLTable.isSerialHeader(h)) return "serial";
    var t = String(h || "").toLowerCase();
    for (var i = 1; i < CONCEPTS.length; i++) if (CONCEPTS[i][1].test(t)) return CONCEPTS[i][0];
    return "";
  }
  // for every column of the target table, the index of the matching column in the source (or -1)
  function mapColumns(srcHeader, tgtHeader) {
    var used = {};
    var sc = srcHeader.map(concept);
    return tgtHeader.map(function (h) {
      var n = norm(h), j = srcHeader.findIndex(function (x, i) { return !used[i] && norm(x) === n; });
      if (j < 0) { var c = concept(h); if (c) j = sc.findIndex(function (x, i) { return !used[i] && x === c; }); }
      if (j >= 0) used[j] = true;
      return j;
    });
  }

  function addToTable(table) {
    var rows = pickedRows(table), tgt = activeTableEl();
    if (!rows.length || !tgt) return;
    var prepared = prep(table, rows);
    // line the columns up: same heading, or the same kind of column (name, place, scope, value...)
    var map = mapColumns(table.header, tgt.header);
    prepared.rows.forEach(function (r) { tgt.rows.push(map.map(function (j) { return j >= 0 ? r[j] : "—"; })); });
    var si = tgt.header.findIndex(HTLTable.isSerialHeader);
    if (si >= 0) tgt.rows.forEach(function (r, i) { r[si] = String(i + 1); });
    sel[table.id] = {};
    var matched = map.filter(function (j) { return j >= 0; }).length;
    wsRerenderCustomSlide(wsActiveIndex);
    setStatus("Added " + rows.length + " row" + (rows.length > 1 ? "s" : "") + " (" + matched + " of " + tgt.header.length + " columns matched)" + (tgt.rows.length > 12 ? ". This slide now has " + tgt.rows.length + " rows - some may not fit." : "."));
  }
  function addText(text) {
    var s = activeSlide();
    var body = tidyOn ? text.split("\n").map(tid).join("\n") : text;
    if (s && s.kind === "custom") {
      var pos = csDefaultPos(s);
      s.elements.push({ id: csNewId(), type: "text", text: body, x: pos.x, y: pos.y, w: 760, size: "body" });
      wsRerenderCustomSlide(wsActiveIndex);
    } else {
      // not a blank slide: put it on a new blank slide right after this one
      var after = wsActiveIndex;
      var ns = { key: "custom_" + rid(), label: "Text", kind: "custom", slots: [], elements: [{ id: csNewId(), type: "text", text: body, x: 60, y: 60, w: 1000, size: "body" }] };
      WORKSPACE_SLIDES.splice(after + 1, 0, ns);
      wsBuilt = false; initWorkspace(); selectWsSlide(after + 1); changed();
    }
  }

  /* ------------------------------------------------------------------ the panel */
  function rowLabel(table, r) {
    var parts = [];
    r.forEach(function (c, i) { if (!HTLTable.isSerialHeader(table.header[i]) && c) parts.push(c); });
    return parts;
  }
  function tableHtml(src, t) {
    var picked = sel[t.id] || {}, n = Object.keys(picked).filter(function (k) { return picked[k]; }).length;
    var canAdd = !!activeTableEl();
    return '<div class="src-table" data-src="' + src.id + '" data-tbl="' + t.id + '">' +
      '<div class="src-ttl">' + esc(t.title || "Table") + ' <small>· ' + t.rows.length + ' rows</small></div>' +
      (t.rows.length > 8 ? '<input class="src-q" placeholder="Search these rows…" data-q>' : "") +
      '<div class="src-links"><button type="button" data-all>Select all</button><button type="button" data-none>None</button></div>' +
      '<div class="src-rows">' + t.rows.map(function (r, i) {
        var p = rowLabel(t, r);
        return '<label class="src-row" data-text="' + esc(p.join(" ").toLowerCase()) + '"><input type="checkbox" data-row="' + i + '"' + (picked[i] ? " checked" : "") + '><span>' +
          esc(p.slice(0, 3).join(" · ")) + (p.length > 3 ? ' <em>· ' + esc(p.slice(3, 5).join(" · ")) + "</em>" : "") + "</span></label>";
      }).join("") + "</div>" +
      '<div class="src-btns">' +
        '<button type="button" class="btn btn--accent" data-newslide' + (n ? "" : " disabled") + '>' + (n ? "New slide with " + n + " selected row" + (n > 1 ? "s" : "") : "Tick rows to use them") + "</button>" +
        (canAdd ? '<button type="button" class="btn" data-addtable' + (n ? "" : " disabled") + '>Add selected to the table on this slide</button>'
                : '<small>To add rows to an existing table, select that table’s slide first.</small>') +
      "</div></div>";
  }
  function groupHtml(src, where, list) {
    return '<div class="src-block src-group" data-src="' + src.id + '" data-where="' + esc(where) + '">' +
      '<div class="src-where">' + esc(where || "Text") + " · " + list.length + ' piece' + (list.length > 1 ? "s" : "") + "</div>" +
      list.map(function (b) { return blockHtml(src, b, true); }).join("") +
      (list.length > 1 ? '<button type="button" class="btn" data-addgroup>Add all of this as one text box</button>' : "") + "</div>";
  }
  function blockHtml(src, b, inGroup) {
    return '<div class="' + (inGroup ? "src-piece" : "src-block") + '" data-src="' + src.id + '" data-blk="' + b.id + '" data-text="' + esc(b.text.toLowerCase()) + '">' +
      (!inGroup && b.where ? '<div class="src-where">' + esc(b.where) + "</div>" : "") +
      '<div class="src-text">' + esc(b.text) + '</div><button type="button" class="btn" data-addtext>Add as a text box</button></div>';
  }
  function panelHtml() {
    var h = '<div class="ws-section src-panel"><h5>Your files <span class="ws-section__note">pick only what you need</span></h5>';
    if (!items.length) h += '<p class="src-help">Add the Excel, PDF, Word or PowerPoint files you were sent. You can then tick just the rows or text you want and put them on your slides.</p>';
    h += '<div class="src-addrow"><label class="btn btn--sm">+ Add a file<input type="file" id="srcFile" multiple accept=".xlsx,.xlsm,.xls,.csv,.pdf,.docx,.pptx,.txt"></label><button type="button" class="btn btn--sm" id="srcPaste">Paste cells or text</button></div>';
    h += '<div class="src-drop" id="srcDrop">or drag files here</div>';
    if (status) h += '<p class="src-status' + (status.err ? " is-err" : "") + '">' + esc(status.msg) + "</p>";
    if (items.length) h += '<label class="src-tidy"><input type="checkbox" id="srcTidy"' + (tidyOn ? " checked" : "") + '><span>Tidy numbers and units when adding (“8 .5 Lacs” → “8.5 Lacs”, “CR” → “Cr”)</span></label>';
    items.forEach(function (src) {
      h += '<details class="src-card" open data-src="' + src.id + '"><summary><span class="src-name">' + esc(src.name) + '</span><button type="button" class="src-x" data-rm title="Remove this file">✕</button></summary><div class="src-body">';
      src.tables.forEach(function (t) { h += tableHtml(src, t); });
      if (src.blocks.length > 6) h += '<input class="src-q" placeholder="Search the text…" data-qb>';
      var order = [], by = {};
      src.blocks.forEach(function (b) { var k = b.where || ""; if (!by[k]) { by[k] = []; order.push(k); } by[k].push(b); });
      order.forEach(function (k) { h += groupHtml(src, k, by[k]); });
      h += "</div></details>";
    });
    return h + "</div>";
  }

  var host = null;
  function render() {
    if (!window.wsRight) return;
    if (!window.HTLTable) { loadScript("/table-import.js").then(render); return; }
    var old = wsRight.querySelector(".src-panel");
    // keep scroll positions of the row lists while re-drawing
    var scrolls = {};
    if (old) old.querySelectorAll(".src-table").forEach(function (t) { var r = t.querySelector(".src-rows"); if (r) scrolls[t.getAttribute("data-tbl")] = r.scrollTop; });
    var wrap = document.createElement("div");
    wrap.innerHTML = panelHtml();
    var panel = wrap.firstChild;
    if (old) old.replaceWith(panel); else wsRight.appendChild(panel);
    panel.querySelectorAll(".src-table").forEach(function (t) { var r = t.querySelector(".src-rows"); var v = scrolls[t.getAttribute("data-tbl")]; if (r && v) r.scrollTop = v; });
    wire(panel);
  }

  function findTable(srcId, tblId) {
    var s = items.find(function (x) { return x.id === srcId; });
    return s && s.tables.find(function (t) { return t.id === tblId; });
  }
  function wire(panel) {
    var f = panel.querySelector("#srcFile");
    if (f) f.addEventListener("change", function () { addFiles(f.files); f.value = ""; });
    var pst = panel.querySelector("#srcPaste"); if (pst) pst.addEventListener("click", addPaste);
    var drop = panel.querySelector("#srcDrop");
    if (drop) {
      ["dragenter", "dragover"].forEach(function (n) { drop.addEventListener(n, function (e) { e.preventDefault(); drop.classList.add("is-over"); }); });
      ["dragleave", "drop"].forEach(function (n) { drop.addEventListener(n, function (e) { e.preventDefault(); drop.classList.remove("is-over"); }); });
      drop.addEventListener("drop", function (e) { addFiles(e.dataTransfer.files); });
    }
    var tidy = panel.querySelector("#srcTidy"); if (tidy) tidy.addEventListener("change", function () { tidyOn = tidy.checked; });

    panel.addEventListener("click", function (e) {
      var card = e.target.closest(".src-card");
      if (e.target.closest("[data-rm]")) {
        e.preventDefault();
        if (!window.confirm("Remove this file from the list? (Slides you already made stay as they are.)")) return;
        items = items.filter(function (x) { return x.id !== card.getAttribute("data-src"); }); changed(); render(); return;
      }
      var box = e.target.closest(".src-table");
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
      }
      var t = findTable(box.getAttribute("data-src"), box.getAttribute("data-tbl"));
      if (!t) return;
      if (e.target.closest("[data-all]")) { sel[t.id] = {}; t.rows.forEach(function (_, i) { sel[t.id][i] = true; }); render(); }
      else if (e.target.closest("[data-none]")) { sel[t.id] = {}; render(); }
      else if (e.target.closest("[data-newslide]")) newSlide(t);
      else if (e.target.closest("[data-addtable]")) addToTable(t);
    });
    panel.addEventListener("change", function (e) {
      var cb = e.target.closest("[data-row]");
      if (!cb) return;
      var box = cb.closest(".src-table"), t = findTable(box.getAttribute("data-src"), box.getAttribute("data-tbl"));
      sel[t.id] = sel[t.id] || {};
      sel[t.id][cb.getAttribute("data-row")] = cb.checked;
      // update only the buttons (redrawing would lose the scroll spot)
      var n = Object.keys(sel[t.id]).filter(function (k) { return sel[t.id][k]; }).length;
      var nb = box.querySelector("[data-newslide]");
      nb.disabled = !n; nb.textContent = n ? "New slide with " + n + " selected row" + (n > 1 ? "s" : "") : "Tick rows to use them";
      var ab = box.querySelector("[data-addtable]"); if (ab) ab.disabled = !n;
    });
    panel.addEventListener("input", function (e) {
      var qb = e.target.closest("[data-qb]");
      if (qb) {
        var vb = qb.value.trim().toLowerCase();
        qb.closest(".src-body").querySelectorAll(".src-piece").forEach(function (p) { p.style.display = !vb || p.getAttribute("data-text").indexOf(vb) >= 0 ? "" : "none"; });
        return;
      }
      var q = e.target.closest("[data-q]");
      if (!q) return;
      var v = q.value.trim().toLowerCase();
      q.closest(".src-table").querySelectorAll(".src-row").forEach(function (r) { r.style.display = !v || r.getAttribute("data-text").indexOf(v) >= 0 ? "" : "none"; });
    });
  }

  // draw the panel whenever the right-hand panel is rebuilt (slide selected, etc.)
  var _rwr = window.renderWsRight;
  window.renderWsRight = function () { var r = _rwr.apply(this, arguments); render(); return r; };

  /* ------------------------------------------------------------------ insert-from-files in the text editor */
  var pop = document.createElement("div");
  pop.className = "src-pop";
  pop.innerHTML = '<input class="src-q" id="srcPopQ" placeholder="Search your files…"><div class="src-list" id="srcPopList"></div>';
  document.body.appendChild(pop);
  var insBtn = null;

  function insertAtCursor(text) {
    var ta = wsTextPopupTextarea;
    var a = ta.selectionStart, b = ta.selectionEnd;
    ta.value = ta.value.slice(0, a) + text + ta.value.slice(b);
    ta.focus(); ta.selectionStart = ta.selectionEnd = a + text.length;
    ta.dispatchEvent(new Event("input", { bubbles: true }));
  }
  function popList() {
    var q = $("srcPopQ").value.trim().toLowerCase(), out = "", shown = 0;
    items.forEach(function (src) {
      src.tables.forEach(function (t) {
        t.rows.forEach(function (r) {
          if (shown >= 40) return;
          var parts = rowLabel(t, r);
          if (q && parts.join(" ").toLowerCase().indexOf(q) < 0) return;
          shown++;
          out += '<div class="src-item"><button type="button" class="src-whole" data-row="' + esc(parts.join(" – ")) + '">Insert whole row</button>' +
            '<div class="src-chips">' + parts.map(function (c) { return '<button type="button" class="src-chip" data-cell="' + esc(c) + '">' + esc(c.length > 34 ? c.slice(0, 33) + "…" : c) + "</button>"; }).join("") + "</div></div>";
        });
      });
      src.blocks.forEach(function (b) {
        if (shown >= 40) return;
        if (q && b.text.toLowerCase().indexOf(q) < 0) return;
        shown++;
        out += '<div class="src-item"><button type="button" class="src-chip" data-cell="' + esc(b.text) + '" style="text-align:left; border-radius:8px; white-space:pre-line; max-height:5em; overflow:hidden;">' + esc(b.text.slice(0, 160)) + "</button></div>";
      });
    });
    $("srcPopList").innerHTML = out || '<p class="src-help">Nothing matches.</p>';
  }
  function openPop() {
    var r = insBtn.getBoundingClientRect();
    pop.classList.add("is-open");
    var left = Math.min(Math.max(8, r.left), window.innerWidth - 392);
    var top = r.bottom + 6;
    if (top + 300 > window.innerHeight) top = Math.max(8, r.top - Math.min(window.innerHeight * 0.6, 360) - 6);
    pop.style.left = left + "px"; pop.style.top = top + "px";
    $("srcPopQ").value = ""; popList(); $("srcPopQ").focus();
  }
  $("srcPopQ").addEventListener("input", popList);
  pop.addEventListener("click", function (e) {
    e.stopPropagation();
    var c = e.target.closest("[data-cell]"), w = e.target.closest("[data-row]");
    var text = c ? c.getAttribute("data-cell") : w ? w.getAttribute("data-row") : null;
    if (text == null) return;
    pop.classList.remove("is-open");
    insertAtCursor(tidyOn ? text.split("\n").map(tid).join("\n") : text);
  });
  document.addEventListener("click", function (e) {
    if (pop.classList.contains("is-open") && !pop.contains(e.target) && e.target !== insBtn) pop.classList.remove("is-open");
  });

  loadScript("/table-import.js").then(function () {
    if (!window.wsTextPopup) return;
    insBtn = document.createElement("button");
    insBtn.type = "button"; insBtn.className = "src-ins-btn"; insBtn.textContent = "Insert from your files ▾";
    wsTextPopup.querySelector("textarea").insertAdjacentElement("afterend", insBtn);
    insBtn.addEventListener("click", function (e) { e.stopPropagation(); if (pop.classList.contains("is-open")) pop.classList.remove("is-open"); else openPop(); });
    var _open = window.wsOpenTextPopup;
    window.wsOpenTextPopup = function () {
      var r = _open.apply(this, arguments);
      insBtn.style.display = items.length ? "" : "none";
      pop.classList.remove("is-open");
      return r;
    };
    insBtn.style.display = "none";
  });

  /* ------------------------------------------------------------------ saved with the deck */
  window.HTLSources = {
    exportState: function () { return items; },
    load: function (list) { items = Array.isArray(list) ? list : []; sel = {}; status = ""; render(); },
  };
})();
