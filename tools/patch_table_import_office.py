# -*- coding: utf-8 -*-
"""Extends public/table-import.js: Word/PowerPoint files, schedule sheets (drop the
"X" day columns), PDFs without a table (text blocks) and one entry point parseAny()."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "public", "table-import.js")
s = open(p, encoding="utf-8").read()

ADD = r'''  /* ---------------------------------------------------------- schedule sheets */
  // A project-schedule sheet has one narrow column per day/week holding an "X" for the
  // bar. Those columns are noise in a list, so they are dropped.
  function dropScheduleColumns(t) {
    var keep = [];
    t.header.forEach(function (h, c) {
      var vals = t.rows.map(function (r) { return String(r[c] || "").trim(); }).filter(Boolean);
      var xs = vals.filter(function (v) { return /^x$/i.test(v); }).length;
      var mostlyX = vals.length > 0 && xs / vals.length >= 0.9;
      var emptyCol = !vals.length && !h;
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

'''

marker = "  var API = {"
assert s.count(marker) == 1
s = s.replace(marker, ADD + marker)
o = "    isSerialHeader: isSerialHeader, tidyText: tidyText,"
assert s.count(o) == 1
s = s.replace(o, o + " parseAny: parseAny, parseOffice: parseOffice, dropScheduleColumns: dropScheduleColumns,")
open(p, "w", encoding="utf-8").write(s)
print("ok")
