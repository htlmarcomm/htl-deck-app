// Quick check of public/table-import.js against real files.
//   node scripts/test-table-import.mjs <file.pdf|file.xlsx|file.csv> ...
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);
const T = require("../public/table-import.js");
const pdfjs = await import(pathToFileURL(path.resolve("node_modules/pdfjs-dist/legacy/build/pdf.mjs")).href);
const XLSX = require("xlsx");

for (const f of process.argv.slice(2)) {
  const buf = fs.readFileSync(f);
  const ab = buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength);
  const ext = path.extname(f).toLowerCase();
  let t;
  if (ext === ".pdf") t = await T.parsePdf(pdfjs, ab);
  else if (ext === ".csv") t = T.parseDelimited(buf.toString("utf8"));
  else t = T.parseWorkbook(XLSX, ab);
  console.log("====", path.basename(f));
  console.log("title:", JSON.stringify(t.title));
  console.log("header:", JSON.stringify(t.header));
  console.log("rows:", t.rows.length);
  t.rows.slice(0, 4).forEach((r) => console.log("  ", JSON.stringify(r)));
  console.log("  ...");
  t.rows.slice(-2).forEach((r) => console.log("  ", JSON.stringify(r)));
  console.log("warnings:", T.warnings(t));
  const a = T.applyOptions(t, { tidy: true, renumber: true });
  console.log("tidy sample:", JSON.stringify(a.rows[3]), "| pages:", T.paginate(a.rows, 12).map((p) => p.length));
}
