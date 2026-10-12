/* "Add slide" menu (the + between slides) and "Table from a file or paste".
   Reads an Excel / CSV / PDF file (or pasted cells) with table-import.js, shows a
   preview with a few safe clean-ups, then adds one or more slides, each a title
   plus an editable table. */
(function () {
  "use strict";
  if (!window.__HTL_USER__ || window.__HTL_SHARE_TOKEN__) return;

  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function rid() { return "s" + Math.random().toString(36).slice(2, 10) + Date.now().toString(36).slice(-4); }

  var css = document.createElement("style");
  css.textContent =
    ".add-menu{position:fixed; z-index:450; background:var(--surface); border:1px solid var(--line); border-radius:12px; box-shadow:var(--shadow); padding:6px; min-width:260px; display:flex; flex-direction:column;}" +
    ".add-menu button{appearance:none; border:0; background:transparent; text-align:left; padding:10px 12px; border-radius:8px; cursor:pointer; font-family:var(--font-ui); color:var(--ink);}" +
    ".add-menu button:hover{background:var(--surface-sunken);}" +
    ".add-menu strong{display:block; font-size:.84rem;} .add-menu span{display:block; font-size:.72rem; color:var(--muted); margin-top:2px;}" +
    ".imp-modal{position:fixed; inset:0; z-index:500; display:none; background:rgba(20,19,15,.58); padding:24px 16px; overflow-y:auto;}" +
    ".imp-modal.is-open{display:block;}" +
    ".imp-card{max-width:860px; margin:0 auto; background:var(--paper); border-radius:var(--radius-lg); box-shadow:0 30px 70px rgba(0,0,0,.4); padding:22px 24px 20px;}" +
    ".imp-head{display:flex; align-items:center; justify-content:space-between; margin-bottom:6px;}" +
    ".imp-head h3{font-size:1.1rem;} .imp-sub{font-size:.8rem; color:var(--muted); margin:0 0 16px; line-height:1.5;}" +
    ".imp-drop{border:2px dashed var(--line-strong); border-radius:14px; padding:28px 16px; text-align:center; color:var(--muted); font-size:.86rem; line-height:1.6;}" +
    ".imp-drop.is-over{border-color:var(--accent); background:var(--accent-wash); color:var(--ink);}" +
    ".imp-drop .btn{margin-top:10px; position:relative; overflow:hidden;} .imp-drop input[type=file]{position:absolute; inset:0; opacity:0; cursor:pointer;}" +
    ".imp-or{text-align:center; font-size:.74rem; color:var(--muted); margin:14px 0 8px; font-weight:600;}" +
    ".imp-paste{width:100%; min-height:90px; border:1px solid var(--line-strong); border-radius:10px; padding:10px 12px; font-family:var(--font-mono); font-size:.76rem; background:var(--surface); color:var(--ink); resize:vertical;}" +
    ".imp-err{color:var(--accent); font-size:.8rem; margin:10px 0 0; min-height:1em;}" +
    ".imp-field{display:flex; flex-direction:column; gap:4px; margin-bottom:12px;}" +
    ".imp-field label{font-size:.66rem; font-weight:700; text-transform:uppercase; letter-spacing:.05em; color:var(--muted);}" +
    ".imp-field input[type=text]{border:1px solid var(--line-strong); border-radius:8px; padding:9px 11px; font-size:.9rem; background:var(--surface); color:var(--ink); font-family:var(--font-ui);}" +
    ".imp-opts{display:flex; flex-direction:column; gap:7px; margin:0 0 12px; font-size:.82rem;}" +
    ".imp-opts label{display:flex; gap:8px; align-items:flex-start; cursor:pointer;} .imp-opts small{color:var(--muted);}" +
    ".imp-cols{display:flex; flex-wrap:wrap; gap:6px 14px; font-size:.8rem; margin:0 0 12px;}" +
    ".imp-cols label{display:flex; gap:6px; align-items:center; cursor:pointer; text-transform:none; letter-spacing:0; font-size:.8rem; font-weight:500; color:var(--ink);}" +
    ".imp-warn{background:var(--draft-wash); color:var(--draft); border-radius:8px; padding:9px 12px; font-size:.78rem; margin:0 0 12px; line-height:1.5;}" +
    ".imp-warn:empty{display:none;}" +
    ".imp-preview{border:1px solid var(--line); border-radius:10px; overflow:auto; max-height:260px; background:var(--surface);}" +
    ".imp-preview table{border-collapse:collapse; width:100%; font-size:.74rem;} .imp-preview th{background:#e5222a; color:#fff; text-align:left; padding:6px 8px; position:sticky; top:0;}" +
    ".imp-preview td{padding:5px 8px; border-bottom:1px solid var(--line); white-space:nowrap;}" +
    ".imp-foot{display:flex; align-items:center; justify-content:space-between; gap:12px; margin-top:16px; flex-wrap:wrap;} .imp-foot span{font-size:.8rem; color:var(--muted);}";
  document.head.appendChild(css);

  /* ---------------------------------------------------------------- menu */
  var menu = null;
  function closeMenu() { if (menu) { menu.remove(); menu = null; } }
  document.addEventListener("click", function (e) {
    var plus = e.target.closest(".ws-add-slide-btn");
    if (!plus) { if (menu && !e.target.closest(".add-menu")) closeMenu(); return; }
    e.stopImmediatePropagation(); e.preventDefault();
    closeMenu();
    var after = +plus.getAttribute("data-add-after");
    var r = plus.getBoundingClientRect();
    menu = document.createElement("div");
    menu.className = "add-menu";
    menu.innerHTML =
      '<button type="button" data-add="blank"><strong>Blank slide</strong><span>Add text, photos and graphs yourself</span></button>' +
      '<button type="button" data-add="table"><strong>Table from a file or paste</strong><span>Excel, CSV or PDF, or cells copied from Excel</span></button>';
    document.body.appendChild(menu);
    var left = Math.min(Math.max(8, r.left + r.width / 2 - 130), window.innerWidth - 276);
    var top = r.bottom + 4;
    if (top + 140 > window.innerHeight) top = Math.max(8, r.top - 130);
    menu.style.left = left + "px"; menu.style.top = top + "px";
    menu.addEventListener("click", function (ev) {
      var b = ev.target.closest("[data-add]");
      if (!b) return;
      ev.stopPropagation();
      var kind = b.getAttribute("data-add");
      closeMenu();
      if (kind === "blank") wsInsertCustomSlideAt(after);
      else openImport(after);
    });
  }, true);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeMenu(); });

  /* ---------------------------------------------------------------- import dialog */
  var modal = document.createElement("div");
  modal.className = "imp-modal";
  modal.innerHTML =
    '<div class="imp-card" role="dialog" aria-modal="true" aria-labelledby="impTitleH">' +
      '<div class="imp-head"><h3 id="impTitleH">Add a table slide</h3><button type="button" class="btn btn--ghost" id="impClose">Close</button></div>' +
      '<div id="impStep1">' +
        '<p class="imp-sub">Choose a file that contains a table (for example your list of projects) and I’ll turn it into a slide. You can edit every cell afterwards.</p>' +
        '<div class="imp-drop" id="impDrop">Drag an Excel, CSV or PDF file here<br><label class="btn btn--accent">Choose a file<input type="file" id="impFile" accept=".xlsx,.xlsm,.xls,.csv,.pdf"></label></div>' +
        '<div class="imp-or">or paste the table &mdash; select the cells in Excel, Google Sheets or Word, copy, then paste here</div>' +
        '<textarea class="imp-paste" id="impPaste" placeholder="Paste here…"></textarea>' +
        '<div class="imp-foot"><span id="impBusy"></span><button type="button" class="btn" id="impUsePaste">Use the pasted table</button></div>' +
        '<p class="imp-err" id="impErr"></p>' +
      '</div>' +
      '<div id="impStep2" hidden>' +
        '<div class="imp-field"><label for="impTitle">Slide title</label><input type="text" id="impTitle"></div>' +
        '<div class="imp-opts">' +
          '<label><input type="checkbox" id="impTidy" checked><span>Tidy numbers and units <small>(&ldquo;8 .5 Lacs&rdquo; &rarr; &ldquo;8.5 Lacs&rdquo;, &ldquo;13Cr&rdquo; &rarr; &ldquo;13 Cr&rdquo;, &ldquo;CR&rdquo; &rarr; &ldquo;Cr&rdquo;)</small></span></label>' +
          '<label id="impRenumWrap"><input type="checkbox" id="impRenum"><span>Renumber the serial column 1, 2, 3&hellip;</span></label>' +
        '</div>' +
        '<div class="imp-field"><label>Columns to show</label><div class="imp-cols" id="impCols"></div></div>' +
        '<div class="imp-warn" id="impWarn"></div>' +
        '<div class="imp-field"><label>Preview</label><div class="imp-preview" id="impPreview"></div></div>' +
        '<div class="imp-foot"><span id="impSummary"></span><span><button type="button" class="btn" id="impBack">Back</button> <button type="button" class="btn btn--accent" id="impAdd">Add to deck</button></span></div>' +
      '</div>' +
    '</div>';
  document.body.appendChild(modal);

  var state = { after: 0, table: null, name: "" };

  function showErr(m) { $("impErr").textContent = m || ""; }
  function busy(m) { $("impBusy").textContent = m || ""; }
  function open() { modal.classList.add("is-open"); }
  function close() { modal.classList.remove("is-open"); }
  function openImport(after) {
    state = { after: after, table: null, name: "" };
    $("impStep1").hidden = false; $("impStep2").hidden = true;
    $("impPaste").value = ""; $("impFile").value = ""; showErr(""); busy("");
    open();
  }
  $("impClose").addEventListener("click", close);
  modal.addEventListener("click", function (e) { if (e.target === modal) close(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && modal.classList.contains("is-open")) close(); });
  $("impBack").addEventListener("click", function () { $("impStep1").hidden = false; $("impStep2").hidden = true; });

  var libs = {};
  function loadScript(src) {
    return libs[src] || (libs[src] = new Promise(function (res, rej) {
      var s = document.createElement("script");
      s.src = src; s.onload = res; s.onerror = function () { rej(new Error("Could not load " + src)); };
      document.head.appendChild(s);
    }));
  }
  function needTable() { return loadScript("/table-import.js"); }

  function fromFile(file) {
    showErr(""); busy("Reading " + file.name + "…");
    if (file.size > 10 * 1024 * 1024) { busy(""); return showErr("That file is larger than 10 MB. Please use a smaller one."); }
    var ext = (file.name.split(".").pop() || "").toLowerCase();
    file.arrayBuffer().then(function (buf) {
      return needTable().then(function () {
        if (ext === "pdf") {
          return import("/vendor/pdfjs/pdf.min.mjs").then(function (lib) {
            lib.GlobalWorkerOptions.workerSrc = "/vendor/pdfjs/pdf.worker.min.mjs";
            return HTLTable.parsePdf(lib, buf);
          });
        }
        if (ext === "csv" || ext === "txt") return HTLTable.parseDelimited(new TextDecoder("utf-8").decode(buf));
        return loadScript("/vendor/xlsx.full.min.js").then(function () { return HTLTable.parseWorkbook(window.XLSX, buf); });
      });
    }).then(function (t) {
      busy("");
      if (!t || !t.rows.length) return showErr("I couldn't find any rows in that file. Try Paste instead.");
      state.name = file.name.replace(/\.[^.]+$/, "");
      toPreview(t);
    }).catch(function (err) { busy(""); showErr(err && err.message ? err.message : "I couldn't read that file."); });
  }
  $("impFile").addEventListener("change", function () { if (this.files[0]) fromFile(this.files[0]); });
  var drop = $("impDrop");
  ["dragenter", "dragover"].forEach(function (n) { drop.addEventListener(n, function (e) { e.preventDefault(); drop.classList.add("is-over"); }); });
  ["dragleave", "drop"].forEach(function (n) { drop.addEventListener(n, function (e) { e.preventDefault(); drop.classList.remove("is-over"); }); });
  drop.addEventListener("drop", function (e) { var f = e.dataTransfer && e.dataTransfer.files[0]; if (f) fromFile(f); });
  $("impUsePaste").addEventListener("click", function () {
    showErr("");
    var txt = $("impPaste").value;
    if (!txt.trim()) return showErr("Paste a table first.");
    needTable().then(function () {
      var t = HTLTable.parseDelimited(txt);
      if (!t || !t.rows.length) return showErr("I couldn't see a table in that text. Copy the cells straight from Excel or Sheets.");
      state.name = "";
      toPreview(t);
    });
  });

  /* ---------------------------------------------------------------- preview */
  function selectedCols() {
    var out = [];
    modal.querySelectorAll("#impCols input").forEach(function (cb, i) { if (cb.checked) out.push(i); });
    return out;
  }
  function toPreview(t) {
    state.table = t;
    $("impStep1").hidden = true; $("impStep2").hidden = false;
    $("impTitle").value = t.title || state.name || "";
    var hasSerial = t.header.some(HTLTable.isSerialHeader);
    $("impRenumWrap").style.display = hasSerial ? "" : "none";
    $("impRenum").checked = HTLTable.warnings(t).some(function (w) { return /serial/i.test(w); });
    $("impCols").innerHTML = t.header.map(function (h, i) {
      return '<label><input type="checkbox" checked data-col="' + i + '"> ' + esc(h || "(no heading)") + "</label>";
    }).join("");
    refresh();
  }
  function current() {
    var t = state.table;
    return HTLTable.applyOptions(t, { tidy: $("impTidy").checked, renumber: $("impRenum").checked, keepCols: selectedCols(), title: $("impTitle").value.trim() });
  }
  function refresh() {
    var t = state.table;
    if (!t) return;
    var a = current();
    $("impWarn").innerHTML = HTLTable.warnings(t).map(esc).join("<br>");
    $("impPreview").innerHTML = "<table><thead><tr>" + a.header.map(function (h) { return "<th>" + esc(h) + "</th>"; }).join("") + "</tr></thead><tbody>" +
      a.rows.slice(0, 12).map(function (r) { return "<tr>" + r.map(function (c) { return "<td>" + esc(c) + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody></table>";
    var pages = HTLTable.paginate(a.rows, 12).length;
    $("impSummary").textContent = a.rows.length + " rows → " + pages + " slide" + (pages > 1 ? "s" : "") + (a.rows.length > 12 ? " (rows are split evenly)" : "");
    $("impAdd").disabled = !a.header.length;
  }
  modal.addEventListener("change", function (e) { if (e.target.closest("#impStep2")) refresh(); });
  $("impTitle").addEventListener("input", function () { /* title only affects the slide */ });

  /* ---------------------------------------------------------------- add the slides */
  function insertTableSlides(after, a) {
    var pages = HTLTable.paginate(a.rows, 12);
    var weights = HTLTable.columnWeights(a.header, a.rows);
    var base = a.title || "Table";
    var slides = pages.map(function (rows, i) {
      var title = base + (pages.length > 1 ? " (" + (i + 1) + "/" + pages.length + ")" : "");
      return {
        key: "custom_" + rid(), label: title.slice(0, 60), kind: "custom", slots: [],
        elements: [
          { id: csNewId(), type: "text", text: title, x: 60, y: 34, w: 1060, size: "header" },
          { id: csNewId(), type: "table", x: 60, y: 128, w: 1060, header: a.header.slice(), rows: rows.map(function (r) { return r.slice(); }), weights: weights.slice() },
        ],
      };
    });
    WORKSPACE_SLIDES.splice.apply(WORKSPACE_SLIDES, [after + 1, 0].concat(slides));
    wsBuilt = false;
    initWorkspace();
    selectWsSlide(after + 1);
    var el = wsLeft.querySelector('.ws-slide[data-index="' + (after + 1) + '"]');
    if (el) el.scrollIntoView({ block: "center" });
    markAutosaveDirty();
  }
  window.HTLInsertTableSlides = function (after, a) {
    return loadScript("/table-import.js").then(function () { insertTableSlides(after, a); });
  };
  $("impAdd").addEventListener("click", function () {
    insertTableSlides(state.after, current());
    close();
  });
})();
