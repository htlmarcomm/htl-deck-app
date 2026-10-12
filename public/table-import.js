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
    var h = -1;
    for (var i = 0; i < rows.length - 1; i++) {
      if (filled(rows[i]) >= 2 && filled(rows[i + 1]) >= 2) { h = i; break; }
    }
    if (h < 0) h = 0;
    var title = rows.slice(0, h).map(function (r) { return r.filter(Boolean).join(" "); }).join(" ").trim();
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

  var API = {
    parseDelimited: parseDelimited, parseWorkbook: parseWorkbook, parsePdf: parsePdf, gridToTable: gridToTable,
    warnings: warnings, applyOptions: applyOptions, paginate: paginate, columnWeights: columnWeights,
    isSerialHeader: isSerialHeader, tidyText: tidyText,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.HTLTable = API;
})(typeof window !== "undefined" ? window : globalThis);
