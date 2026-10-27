// Runs tools/standard/normalize.js over slides in headless Chrome against the local app.
//   node tools/standard/run.mjs <outDir> key1 key2 ...     (needs the app on http://localhost:3100)
// Reads each slide's ORIGINAL markup from tools/standard/originals.json (created on first run from the app),
// writes <outDir>/result.json {key: {html, flags}} and before/after PNGs.
import { spawn } from "node:child_process";
import { readFileSync, writeFileSync, mkdirSync, mkdtempSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const [outDir, ...keys] = process.argv.slice(2);
mkdirSync(outDir, { recursive: true });
const BASE = process.env.BASE || "http://localhost:3100";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const PORT = 9400 + Math.floor(Math.random() * 400);
const chrome = spawn("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe", ["--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${mkdtempSync(join(tmpdir(), "ss-"))}`, "--window-size=1600,1000", "--hide-scrollbars", "about:blank"], { stdio: "ignore" });
let t;
for (let i = 0; i < 120 && !t; i++) { try { t = (await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json()).find((x) => x.type === "page"); } catch {} await sleep(250); }
const ws = new WebSocket(t.webSocketDebuggerUrl);
await new Promise((r) => (ws.onopen = r));
let id = 0; const pend = new Map(); const logs = [];
ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { pend.get(d.id)(d); pend.delete(d.id); } if (d.method === "Runtime.exceptionThrown") logs.push(d.params.exceptionDetails.exception?.description || d.params.exceptionDetails.text); };
const send = (method, params = {}) => new Promise((res) => { const i = ++id; pend.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async (expr) => { const r = await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true }); if (r.result?.exceptionDetails) throw new Error(r.result.exceptionDetails.exception?.description || r.result.exceptionDetails.text); return r.result?.result?.value; };
const shot = async (file) => { const r = await send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width: 1280, height: 720, scale: 1 } }); writeFileSync(file, Buffer.from(r.result.data, "base64")); };
await send("Page.enable"); await send("Runtime.enable");
await send("Emulation.setDeviceMetricsOverride", { width: 1600, height: 1000, deviceScaleFactor: 1, mobile: false });
await send("Page.navigate", { url: BASE + "/login" }); await sleep(2500);
await ev(`fetch('/api/auth/login',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({username:'creator',password:'local-dev-password-1'})}).then(r=>r.status)`);
await send("Page.navigate", { url: BASE + "/" }); await sleep(3500);

const css = readFileSync(join(HERE, "tokens.css"), "utf8") + readFileSync(join(HERE, "flow.css"), "utf8");
await ev(`(()=>{const l=document.createElement('link'); l.rel='stylesheet'; l.href='https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;500;600;700&display=swap'; document.head.appendChild(l);
  const s=document.createElement('style'); s.id='ss-tokens'; s.textContent=${JSON.stringify(css)}; document.head.appendChild(s);})()`);
await ev(readFileSync(join(HERE, "normalize.js"), "utf8"));
await ev(readFileSync(join(HERE, "normalize-flow.js"), "utf8"));
await ev(`document.fonts.load('700 66px Raleway').then(()=>document.fonts.load('300 66px Raleway')).then(()=>document.fonts.ready)`);

const op = join(HERE, "originals.json");
const orig = existsSync(op) ? JSON.parse(readFileSync(op, "utf8")) : {};
const logo = await ev(`(ALL_SNIPPETS.key_clients.match(/class="kc-logo" src="([^"]+)"/)||[])[1]`);
let changed = false;
for (const k of keys) if (!orig[k]) { orig[k] = await ev(`ALL_SNIPPETS[${JSON.stringify(k)}]`); changed = true; }
if (changed) writeFileSync(op, JSON.stringify(orig, null, 0));

const result = existsSync(join(outDir, "result.json")) ? JSON.parse(readFileSync(join(outDir, "result.json"), "utf8")) : {};
for (const k of keys) {
  const mount = (html) => ev(`(async()=>{let h=document.getElementById('__ss'); if(h) h.remove(); h=document.createElement('div'); h.id='__ss'; h.className='real-scope'; h.dataset.key=${JSON.stringify(k)};
     h.style.cssText='position:fixed;left:0;top:0;width:1280px;height:720px;z-index:99999;background:#fff;overflow:hidden'; h.innerHTML=${JSON.stringify(html)}; document.body.appendChild(h);
     await document.fonts.ready; await new Promise(r=>setTimeout(r,250)); return true})()`);
  await mount(orig[k]);
  await shot(join(outDir, k + "_before.png"));
  const out = await ev(`(()=>{const sec=document.querySelector('#__ss > *'); return sec.classList.contains('pj') ? window.ssNormalize(sec, {logo:${JSON.stringify(logo)}}) : window.ssNormalizeFlow(sec, {logo:${JSON.stringify(logo)}, key:${JSON.stringify(k)}})})()`);
  await mount(out.html);
  await shot(join(outDir, k + "_after.png"));
  result[k] = out;
  console.log(k.padEnd(22), out.flags.length ? "FLAGS: " + out.flags.slice(0, 4).join(" | ") + (out.flags.length > 4 ? " (+" + (out.flags.length - 4) + ")" : "") : "ok");
}
writeFileSync(join(outDir, "result.json"), JSON.stringify(result, null, 1));
if (logs.length) console.log("page errors:", logs.slice(0, 5));
ws.close(); chrome.kill(); process.exit(0);
