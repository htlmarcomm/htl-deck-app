/* Table import: turn an Excel sheet, a CSV, a pasted block or a text-based PDF table
   into { title, header[], rows[][], notes[] }. Used by "Add slide > Table from a
   file or paste" (deck-store.js). Runs in the browser; also loadable in Node for tests. */
(function (root) {
  "use strict";

  function cell(v) {
    if (v == null) return "";
    if (v instanceof Date) return v.toISOString().slice(0, 10);
    return String(v).replace(/\s+/g, " ").trim();
  }

  /* ---------------------------------------------------------- generic grid -> table */
  // grid: array of arrays of strings. Finds the title (single-cell rows above), the
  // header row (first row with 3+ filled cells that is followed by another such row)
  // and the data rows below it.
  function gridToTable(grid) {
    var rows = grid.map(function (r) { return r.map(cell); })
      .filter(function (r) { return r.some(function (c) { return c; }); });
    var filled = function (r) { return r.filter(function (c) { return c; }).length; };
    // header row = the first row (within the top 25) that is nearly as full as the fullest row,
    // so a few description lines above a wide schedule header are skipped
    var maxFill = 0;
    rows.slice(0, 25).forEach(function (r) { maxFill = Math.max(maxFill, filled(r)); });
    var h = -1;
    for (var i = 0; i < Math.min(rows.length - 1, 25); i++) {
      if (filled(rows[i]) >= 2 && filled(rows[i]) >= maxFill * 0.6 && filled(rows[i + 1]) >= 2) { h = i; break; }
    }
    if (h < 0) h = 0;
    var title = rows.slice(0, h).map(function (r) { return r.filter(Boolean).join(" "); }).filter(Boolean)[0] || "";
    var header = rows[h] || [];
    var body = rows.slice(h + 1);
    // drop columns that are empty everywhere (header and body)
    var keep = [];
    for (var c = 0; c < header.length; c++) {
      if (header[c] || body.some(function (r) { return r[c]; })) keep.push(c);
    }
    var width = keep.length;
    return {
      title: title,
      header: keep.map(function (c) { return header[c] || ""; }),
      rows: body.map(function (r) { return keep.map(function (c) { return r[c] || ""; }); }).filter(function (r) { return r.some(Boolean); }),
      notes: [],
      width: width,
    };
  }

  /* ---------------------------------------------------------- paste / CSV */
  function parseDelimited(text) {
    text = String(text || "").replace(/\r\n?/g, "\n").replace(/^﻿/, "").trim();
    if (!text) return null;
    var first = text.split("\n").slice(0, 5).join("\n");
    var delim = first.indexOf("\t") >= 0 ? "\t" : (first.split(";").length > first.split(",").length ? ";" : ",");
    var grid = [], row = [], cur = "", q = false;
    for (var i = 0; i < text.length; i++) {
      var ch = text[i];
      if (q) {
        if (ch === '"' && text[i + 1] === '"') { cur += '"'; i++; }
        else if (ch === '"') q = false;
        else cur += ch;
      } else if (ch === '"') q = true;
      else if (ch === delim) { row.push(cur); cur = ""; }
      else if (ch === "\n") { row.push(cur); grid.push(row); row = []; cur = ""; }
      else cur += ch;
    }
    row.push(cur); grid.push(row);
    return gridToTable(grid);
  }

  /* ---------------------------------------------------------- Excel */
  function parseWorkbook(XLSX, buf) {
    var wb = XLSX.read(buf, { type: "array", cellDates: true });
    var best = null;
    wb.SheetNames.forEach(function (n) {
      var grid = XLSX.utils.sheet_to_json(wb.Sheets[n], { header: 1, raw: false, defval: "", blankrows: false });
      var t = gridToTable(grid);
      t.sheet = n;
      if (!best || t.rows.length > best.rows.length) best = t;
    });
    return best;
  }

  /* ---------------------------------------------------------- PDF (text-based tables) */
  // Items on one visual line (same baseline), each cell's words joined.
  function pageLines(items) {
    items = items.filter(function (i) { return i.s.trim(); })
      .sort(function (a, b) { return b.y - a.y || a.x - b.x; });
    var lines = [];
    items.forEach(function (it) {
      var ln = lines.length ? lines[lines.length - 1] : null;
      if (ln && Math.abs(ln.y - it.y) <= Math.max(2.5, it.h * 0.35)) ln.items.push(it);
      else lines.push({ y: it.y, h: it.h, items: [it] });
    });
    lines.forEach(function (l) {
      l.items.sort(function (a, b) { return a.x - b.x; });
      // glue fragments of one word (touching runs)
      var out = [];
      l.items.forEach(function (it) {
        var p = out[out.length - 1];
        if (p && it.x - (p.x + p.w) < 1.2) { p.s += it.s; p.w = it.x + it.w - p.x; }
        else out.push({ s: it.s, x: it.x, w: it.w, h: it.h, y: it.y });
      });
      l.items = out;
    });
    return lines;
  }

  function tableFromLines(lines) {
    var count = function (l) { return l.items.length; };
    // the header is the first line with 3+ cells; wrapped header text can sit on lines just above
    // and below it (vertically centred headers), so that band is merged
    var hi = -1;
    for (var i = 0; i < lines.length; i++) if (count(lines[i]) >= 3) { hi = i; break; }
    if (hi < 0) return null;
    var hy = lines[hi].y, hh = lines[hi].h || 10;
    // typical distance between two table rows; a wrapped header line sits much closer than that
    var ys = lines.slice(hi + 1).filter(function (l) { return count(l) >= 3; }).map(function (l) { return l.y; });
    var gaps = [];
    for (var g = 1; g < ys.length; g++) if (ys[g - 1] - ys[g] > 1) gaps.push(ys[g - 1] - ys[g]);
    gaps.sort(function (a, b) { return a - b; });
    var pitch = gaps.length ? gaps[Math.floor(gaps.length / 2)] : hh * 1.3;
    var near = pitch * 0.75;
    var band = [hi];
    for (var u = hi - 1; u >= 0; u--) {
      if (lines[u].y > hy && lines[u].y - hy <= near && count(lines[u]) < 3) band.unshift(u); else break;
    }
    var bottom = hi;
    for (var d = hi + 1; d < lines.length; d++) {
      if (lines[d].y < hy && hy - lines[d].y <= near && count(lines[d]) < 3) { band.push(d); bottom = d; } else break;
    }
    var bandSet = band.slice().sort(function (a, b) { return a - b; });
    var topIdx = bandSet[0];
    var after = lines.slice(bottom + 1);
    var cands = after.filter(function (l) { return count(l) >= 3; });
    if (!cands.length) return null;

    // column left edges: x positions where a cell starts (first item, or after a clear gap) in
    // most data lines
    var xs = [];
    cands.forEach(function (l) {
      l.items.forEach(function (it, k) {
        var gap = k === 0 ? 99 : it.x - (l.items[k - 1].x + l.items[k - 1].w);
        if (gap > 5) xs.push({ x: it.x, line: l });
      });
    });
    xs.sort(function (a, b) { return a.x - b.x; });
    var clusters = [];
    xs.forEach(function (o) {
      var c = clusters[clusters.length - 1];
      if (c && o.x - c.last <= 4) { c.pts.push(o); c.last = o.x; } else clusters.push({ pts: [o], last: o.x });
    });
    var need = Math.max(2, Math.ceil(cands.length * 0.4));
    var anchors = clusters.filter(function (c) {
      var set = new Set(c.pts.map(function (o) { return o.line; }));
      return set.size >= need;
    }).map(function (c) {
      var v = c.pts.map(function (o) { return o.x; }).sort(function (a, b) { return a - b; });
      return v[Math.floor(v.length / 2)];
    });
    if (anchors.length < 2) return null;

    function nearest(x) {
      var j = 0, best = 1e9;
      anchors.forEach(function (a, k) { var dd = Math.abs(x - a); if (dd < best) { best = dd; j = k; } });
      return { j: j, d: best };
    }
    function lineCells(l) {
      var cells = anchors.map(function () { return []; });
      var cur = -1;
      l.items.forEach(function (it, k) {
        var n = nearest(it.x);
        var gap = k === 0 ? 99 : it.x - (l.items[k - 1].x + l.items[k - 1].w);
        if (k === 0) cur = n.j;
        else if (n.j > cur && ((gap > 5 && n.d <= 10) || n.d <= 3)) cur = n.j;
        cells[cur].push(it.s);
      });
      return cells.map(function (a) { return a.join(" ").replace(/\s+/g, " ").trim(); });
    }

    var header = anchors.map(function () { return ""; });
    bandSet.forEach(function (li) {
      lineCells(lines[li]).forEach(function (t, k) { if (t) header[k] = (header[k] ? header[k] + " " : "") + t; });
    });
    var title = lines.slice(0, topIdx).map(function (l) { return l.items.map(function (i) { return i.s; }).join(" "); }).join(" ").trim();

    // body: data lines, plus wrapped continuation lines glued onto the row above
    var rows = [], prevY = null, lineH = 0;
    var firstCand = lines.indexOf(cands[0]);
    for (var m = firstCand; m < lines.length; m++) {
      var l = lines[m], cells = lineCells(l);
      if (count(l) >= Math.max(2, Math.ceil(anchors.length * 0.4))) {
        rows.push(cells); prevY = l.y; lineH = l.h || lineH;
      } else if (rows.length && prevY != null && prevY - l.y < (lineH || 10) * 1.9 &&
                 l.items.every(function (it) { return nearest(it.x).d <= 3; })) {
        var last = rows[rows.length - 1];
        cells.forEach(function (t, k) { if (t) last[k] = (last[k] ? last[k] + " " : "") + t; });
        prevY = l.y;
      }
    }
    return { title: title, header: header, rows: rows, notes: [], width: anchors.length };
  }

  async function parsePdf(lib, buf) {
    var pdf = await lib.getDocument({ data: new Uint8Array(buf), isEvalSupported: false, useSystemFonts: true }).promise;
    var all = null;
    for (var p = 1; p <= pdf.numPages; p++) {
      var page = await pdf.getPage(p);
      var tc = await page.getTextContent();
      var items = tc.items.map(function (i) {
        return { s: i.str, x: i.transform[4], y: i.transform[5], w: i.width, h: i.height || Math.abs(i.transform[3]) };
      });
      var t = tableFromLines(pageLines(items));
      if (!t) continue;
      if (!all) all = t;
      else {
        // continuation page: skip a repeated header row
        var rows = t.rows.filter(function (r) { return r.join("|") !== all.header.join("|"); });
        all.rows = all.rows.concat(rows);
      }
    }
    if (!all) throw new Error("I couldn't find a table in this PDF. If it is a scanned picture, copy the table from the original file and use Paste instead.");
    return all;
  }

  /* ---------------------------------------------------------- tidy-up */
  // Light, safe fixes so the slide reads consistently.
  function tidyText(s) {
    return String(s)
      .replace(/\s+/g, " ")
      .replace(/(\d)\s+\.(\d)/g, "$1.$2")                    // "8 .5" -> "8.5"
      .replace(/(\d)(Cr|CR|cr|Lacs|LACS|Lakhs?|Lakh)\b/g, "$1 $2") // "13Cr" -> "13 Cr"
      .replace(/\bCR\b/g, "Cr")
      .replace(/\bLACS\b/g, "Lacs")
      .replace(/\s+([,.;:])/g, "$1")
      .trim();
  }
  function isSerialHeader(h) { return /^(s\.?\s*no\.?|sl\.?\s*no\.?|sr\.?\s*no\.?|no\.?|#)$/i.test(String(h).trim()); }

  /* checks shown to the user before the slide is made */
  function warnings(t) {
    var w = [];
    var empties = 0;
    t.rows.forEach(function (r) { r.forEach(function (c, k) { if (!c && !isSerialHeader(t.header[k])) empties++; }); });
    if (empties) w.push(empties + " empty cell" + (empties > 1 ? "s" : "") + " (they will show as “—”).");
    var si = t.header.findIndex(isSerialHeader);
    if (si >= 0) {
      var seen = {}, dup = false, gap = false, prev = 0;
      t.rows.forEach(function (r) {
        var n = parseInt(r[si], 10);
        if (isNaN(n)) return;
        if (seen[n]) dup = true;
        seen[n] = 1;
        if (n !== prev + 1) gap = true;
        prev = n;
      });
      if (dup || gap) w.push("The serial numbers repeat or skip a number. Tick “Renumber” to fix them.");
    }
    return w;
  }

  function applyOptions(t, o) {
    o = o || {};
    var header = t.header.slice(), rows = t.rows.map(function (r) { return r.slice(); });
    var keep = o.keepCols || header.map(function (_, i) { return i; });
    if (o.tidy) {
      header = header.map(tidyText);
      rows = rows.map(function (r) { return r.map(tidyText); });
    }
    var si = header.findIndex(isSerialHeader);
    if (o.renumber && si >= 0) rows.forEach(function (r, i) { r[si] = String(i + 1); });
    rows = rows.map(function (r) { return r.map(function (c) { return c || "—"; }); });
    // empty serial cells stay empty
    return {
      title: o.title != null ? o.title : t.title,
      header: keep.map(function (i) { return header[i]; }),
      rows: rows.map(function (r) { return keep.map(function (i) { return r[i]; }); }),
    };
  }

  /* split rows over slides evenly, at most `max` per slide */
  function paginate(rows, max) {
    max = max || 12;
    var pages = Math.max(1, Math.ceil(rows.length / max));
    var per = Math.ceil(rows.length / pages);
    var out = [];
    for (var i = 0; i < rows.length; i += per) out.push(rows.slice(i, i + per));
    return out.length ? out : [[]];
  }

  /* relative column widths from the content (headers wrap, so they count less) */
  function columnWeights(header, rows) {
    return header.map(function (h, c) {
      var max = 0;
      rows.forEach(function (r) { max = Math.max(max, String(r[c] || "").length); });
      var hl = String(h || "").split(/\s+/).reduce(function (a, w) { return Math.max(a, w.length); }, 0);
      return Math.min(40, Math.max(max, hl) + 4);   // + cell padding, so short values never wrap
    });
  }

  /* ---------------------------------------------------------- schedule sheets */
  // A project-schedule sheet has one narrow column per day/week holding an "X" for the
  // bar. Those columns are noise in a list, so they are dropped.
  function dropScheduleColumns(t) {
    var keep = [];
    t.header.forEach(function (h, c) {
      var vals = t.rows.map(function (r) { return String(r[c] || "").trim(); }).filter(Boolean);
      var xs = vals.filter(function (v) { return /^x$/i.test(v); }).length;
      var mostlyX = vals.length > 0 && xs / vals.length >= 0.9;
      var emptyCol = !vals.length && (!h || t.header.length >= 20);
      if (!mostlyX && !emptyCol) keep.push(c);
    });
    if (keep.length === t.header.length) return t;
    return {
      title: t.title, notes: t.notes, width: keep.length,
      header: keep.map(function (c) { return t.header[c]; }),
      rows: t.rows.map(function (r) { return keep.map(function (c) { return r[c]; }); }),
    };
  }

  /* ---------------------------------------------------------- Word / PowerPoint */
  // .pptx and .docx are zip files of XML: pull out the tables and the pieces of text.
  function xmlDoc(str) { return new DOMParser().parseFromString(str, "application/xml"); }
  function paraText(p, tTag) {
    var out = "";
    var walk = function (n) {
      for (var ch = n.firstChild; ch; ch = ch.nextSibling) {
        if (ch.nodeType !== 1) continue;
        if (ch.nodeName === tTag) out += ch.textContent;
        else if (ch.nodeName === "a:br" || ch.nodeName === "w:br") out += "\n";
        else if (ch.nodeName === "w:tab") out += " ";
        else walk(ch);
      }
    };
    walk(p);
    return out.replace(/[ \t]+/g, " ").trim();
  }
  function officeTables(doc, tbl, tr, tc, para, tTag) {
    var tables = [];
    Array.prototype.forEach.call(doc.getElementsByTagName(tbl), function (t) {
      var grid = [];
      Array.prototype.forEach.call(t.getElementsByTagName(tr), function (row) {
        var cells = [];
        for (var c = row.firstChild; c; c = c.nextSibling) {
          if (c.nodeName !== tc) continue;
          cells.push(Array.prototype.map.call(c.getElementsByTagName(para), function (p) { return paraText(p, tTag); }).filter(Boolean).join(" "));
        }
        grid.push(cells);
      });
      var tt = gridToTable(grid);
      if (tt.rows.length) tables.push(tt);
    });
    return tables;
  }
  function parseOffice(fflate, buf, ext) {
    var files = fflate.unzipSync(new Uint8Array(buf));
    var tables = [], blocks = [];
    if (ext === "pptx") {
      var names = Object.keys(files).filter(function (n) { return /^ppt\/slides\/slide\d+\.xml$/.test(n); })
        .sort(function (a, b) { return parseInt(a.match(/(\d+)\.xml/)[1], 10) - parseInt(b.match(/(\d+)\.xml/)[1], 10); });
      names.forEach(function (n, i) {
        var doc = xmlDoc(fflate.strFromU8(files[n]));
        officeTables(doc, "a:tbl", "a:tr", "a:tc", "a:p", "a:t").forEach(function (t) { t.slide = i + 1; tables.push(t); });
        Array.prototype.forEach.call(doc.getElementsByTagName("p:sp"), function (sp) {
          var txt = Array.prototype.map.call(sp.getElementsByTagName("a:p"), function (p) { return paraText(p, "a:t"); }).filter(Boolean).join("\n");
          if (txt.replace(/\s/g, "").length >= 3) blocks.push({ text: txt, where: "Slide " + (i + 1) });
        });
      });
    } else if (ext === "docx") {
      var f = files["word/document.xml"];
      if (!f) throw new Error("This Word file has no readable text.");
      var d2 = xmlDoc(fflate.strFromU8(f));
      officeTables(d2, "w:tbl", "w:tr", "w:tc", "w:p", "w:t").forEach(function (t) { tables.push(t); });
      Array.prototype.forEach.call(d2.getElementsByTagName("w:p"), function (p) {
        // paragraphs inside a table are already in the table
        for (var a = p.parentNode; a; a = a.parentNode) if (a.nodeName === "w:tc") return;
        var txt = paraText(p, "w:t");
        if (txt.length >= 3) blocks.push({ text: txt, where: "Document" });
      });
    } else throw new Error("Unsupported Office file.");
    return { tables: tables, blocks: blocks };
  }

  /* ---------------------------------------------------------- PDFs without a table: text blocks */
  async function parsePdfText(lib, buf) {
    var pdf = await lib.getDocument({ data: new Uint8Array(buf), isEvalSupported: false, useSystemFonts: true }).promise;
    var blocks = [];
    for (var p = 1; p <= pdf.numPages; p++) {
      var tc = await (await pdf.getPage(p)).getTextContent();
      var lines = pageLines(tc.items.map(function (i) { return { s: i.str, x: i.transform[4], y: i.transform[5], w: i.width, h: i.height || 10 }; }));
      var cur = [], prev = null;
      lines.forEach(function (l) {
        var t = l.items.map(function (i) { return i.s; }).join(" ").replace(/\s+/g, " ").trim();
        if (!t) return;
        if (prev != null && prev - l.y > (l.h || 10) * 1.9 && cur.length) { blocks.push({ text: cur.join("\n"), where: "Page " + p }); cur = []; }
        cur.push(t); prev = l.y;
      });
      if (cur.length) blocks.push({ text: cur.join("\n"), where: "Page " + p });
    }
    return blocks;
  }

  /* ---------------------------------------------------------- one entry point */
  // -> { tables: [{title, header, rows}], blocks: [{text, where}] }
  async function parseAny(file, env) {
    var ext = (file.name.split(".").pop() || "").toLowerCase();
    var buf = await file.arrayBuffer();
    var out = { tables: [], blocks: [] };
    if (ext === "pdf") {
      var lib = await env.pdfjs();
      try { out.tables.push(await parsePdf(lib, buf)); }
      catch (e) { out.blocks = await parsePdfText(lib, buf); if (!out.blocks.length) throw e; }
    } else if (ext === "pptx" || ext === "docx") {
      out = parseOffice(await env.fflate(), buf, ext);
    } else if (ext === "csv" || ext === "txt" || ext === "tsv") {
      var t = parseDelimited(new TextDecoder("utf-8").decode(buf));
      if (t && t.rows.length) out.tables.push(t);
    } else if (ext === "xlsx" || ext === "xlsm" || ext === "xls") {
      var X = await env.xlsx();
      var wb = X.read(buf, { type: "array", cellDates: true });
      wb.SheetNames.forEach(function (n) {
        var grid = X.utils.sheet_to_json(wb.Sheets[n], { header: 1, raw: false, defval: "", blankrows: false });
        var tb = dropScheduleColumns(gridToTable(grid));
        if (tb.rows.length) { tb.sheet = n; if (!tb.title) tb.title = n; out.tables.push(tb); }
      });
    } else if (ext === "ppt" || ext === "doc") {
      throw new Error("Old ." + ext + " files can't be read. Please save it as ." + ext + "x and try again.");
    } else throw new Error("I can read Excel, CSV, PDF, Word (.docx) and PowerPoint (.pptx) files.");
    if (!out.tables.length && !out.blocks.length) throw new Error("I couldn't find a table or any text in that file.");
    return out;
  }

  var API = {
    parseDelimited: parseDelimited, parseWorkbook: parseWorkbook, parsePdf: parsePdf, gridToTable: gridToTable,
    warnings: warnings, applyOptions: applyOptions, paginate: paginate, columnWeights: columnWeights,
    isSerialHeader: isSerialHeader, tidyText: tidyText, parseAny: parseAny, parseOffice: parseOffice, dropScheduleColumns: dropScheduleColumns,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.HTLTable = API;
})(typeof window !== "undefined" ? window : globalThis);
