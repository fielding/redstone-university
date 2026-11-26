#!/usr/bin/env node
// snap.mjs — headless PNG renderer for the three.js build viewer (no Blender).
//
//   node viewer/snap.mjs <shot> [view] [--theme schematic|schematic_dark]
//                        [--out path.png] [--ss 2] [--chrome /path/to/Chrome]
//   node viewer/snap.mjs --all [--out-dir renders/out-three]
//   node viewer/snap.mjs --placed [--out-dir DIR]   # every placed figure (for scripts/live3d_qa.py)
//
// Serves the repo root on a local port, opens viewer/ in headless Chrome over
// the DevTools protocol, waits for the build + textures to load, and saves the
// viewer's export (rendered at the shot's resolution, supersampled `ss`x).
// Needs only Node >= 22 (built-in fetch + WebSocket) and a Chrome install.
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { existsSync, mkdtempSync, mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, extname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const REPO = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const opt = (name, d) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : d; };
const flag = (name) => args.includes(name);
const positional = args.filter((a, i) => !a.startsWith('--') && !(i > 0 && args[i - 1].startsWith('--') && !['--all'].includes(args[i - 1])));

const CHROME = opt('--chrome', process.env.CHROME || [
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
].find(existsSync));
if (!CHROME) { console.error('no Chrome found; pass --chrome <path>'); process.exit(1); }

const theme = opt('--theme', 'schematic');
const ss = Number(opt('--ss', '2'));
const outDir = opt('--out-dir', join(REPO, 'renders', 'out-three'));

// --------------------------------------------------------- static server
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json',
  '.png': 'image/png', '.css': 'text/css', '.svg': 'image/svg+xml' };
const server = createServer((req, res) => {
  let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if (p.endsWith('/')) p += 'index.html';
  const file = join(REPO, p);
  if (!file.startsWith(REPO) || !existsSync(file) || statSync(file).isDirectory()) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'Content-Type': MIME[extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-store' });
  res.end(readFileSync(file));
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const port = server.address().port;

// --------------------------------------------------------- chrome + CDP
const dbgPort = 9300 + Math.floor(Math.random() * 600);
const profile = mkdtempSync(join(tmpdir(), 'ru-snap-'));
const chrome = spawn(CHROME, [
  '--headless=new', `--remote-debugging-port=${dbgPort}`, `--user-data-dir=${profile}`,
  '--no-first-run', '--no-default-browser-check', '--hide-scrollbars',
  '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--use-angle=swiftshader',
  '--window-size=1600,1000', 'about:blank',
], { stdio: ['ignore', 'ignore', 'pipe'] });
let stderr = '';
chrome.stderr.on('data', (d) => { stderr += d; });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function cdpJson(path) {
  for (let i = 0; i < 60; i++) {
    try { const r = await fetch(`http://127.0.0.1:${dbgPort}${path}`); return await r.json(); }
    catch { await sleep(200); }
  }
  throw new Error('chrome did not start: ' + stderr.slice(-400));
}
const targets = await cdpJson('/json/list');
const page = targets.find((t) => t.type === 'page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
let msgId = 0;
const pending = new Map();
const logs = [];
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Runtime.exceptionThrown') logs.push('[exception] ' + m.params.exceptionDetails.text + ' ' + (m.params.exceptionDetails.exception?.description || ''));
  if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') logs.push('[console.error] ' + m.params.args.map((a) => a.value ?? a.description).join(' '));
};
const send = (method, params = {}) => new Promise((res) => { const id = ++msgId; pending.set(id, res); ws.send(JSON.stringify({ id, method, params })); });
await send('Runtime.enable');
await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 1600, height: 1000, deviceScaleFactor: 1, mobile: false });

async function snap(shot, view, outPath) {
  const url = `http://127.0.0.1:${port}/viewer/?shot=${encodeURIComponent(shot)}&view=${view}&theme=${theme}`;
  await send('Page.navigate', { url });
  const t0 = Date.now();
  let status = '';
  while (Date.now() - t0 < 60000) {
    const r = await send('Runtime.evaluate', { expression: `(window.__ru && window.__ruLoaded ? 'READY ' : '') + (document.getElementById('status')?.textContent || '')`, returnByValue: true });
    status = r.result?.result?.value || '';
    if (status.startsWith('READY') || status.includes('ERROR') || status.includes('no build JSON')) break;
    await sleep(200);
  }
  if (!status.startsWith('READY')) { console.error(`[${shot}] ${status || 'timeout'}`); return false; }
  await sleep(300);
  const r = await send('Runtime.evaluate', { expression: `window.__ruExport(${ss})`, awaitPromise: true, returnByValue: true });
  const data = r.result?.result?.value;
  if (!data?.startsWith('data:image/png')) { console.error(`[${shot}] export failed`, JSON.stringify(r.result).slice(0, 300)); return false; }
  mkdirSync(dirname(outPath), { recursive: true });
  writeFileSync(outPath, Buffer.from(data.split(',')[1], 'base64'));
  console.log(`[${shot}] ${view} -> ${outPath}  (${status.replace('READY ', '')})`);
  return true;
}

// views per shot come from shots.json (the .rub header needs a gunzip to read)
function shotViews(shot) {
  const shots = JSON.parse(readFileSync(join(REPO, 'renders', 'shots.json'), 'utf8'));
  return { ...shots._defaults, ...shots[shot] }.views || ['iso'];
}

let ok = true;
try {
  if (flag('--placed')) {
    // every placed figure with a build (viewer/builds/places.json), held or
    // not, so scripts/live3d_qa.py can judge all of them
    const places = JSON.parse(readFileSync(join(REPO, 'viewer', 'builds', 'places.json'), 'utf8'));
    const seen = new Set();
    for (const { shot, view } of Object.values(places)) {
      if (seen.has(`${shot}_${view}`)) continue;
      seen.add(`${shot}_${view}`);
      ok = (await snap(shot, view, join(outDir, `${shot}_${view}.png`))) && ok;
    }
  } else if (flag('--all')) {
    const index = JSON.parse(readFileSync(join(REPO, 'viewer', 'builds', 'index.json'), 'utf8'));
    for (const shot of index) {
      const views = shotViews(shot);
      for (const view of views) {
        ok = (await snap(shot, view, join(outDir, `${shot}_${view}.png`))) && ok;
      }
    }
  } else {
    const [shot, view = 'iso'] = positional;
    if (!shot) { console.error('usage: node viewer/snap.mjs <shot> [iso|top] [--out file.png] | --all'); process.exit(2); }
    const out = opt('--out', join(outDir, `${shot}_${view}.png`));
    ok = await snap(shot, view, out);
  }
} finally {
  for (const l of logs) console.error(l);
  ws.close();
  chrome.kill('SIGKILL');
  server.close();
}
process.exit(ok ? 0 : 1);
