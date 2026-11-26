#!/usr/bin/env node
// Behavior checks for the live 3D figures against a running build of the site
// (`npx astro build && npx astro preview`). Drives headless Chrome over the
// DevTools protocol; needs only Node >= 22 and a Chrome install.
//
//   node scripts/check-live-figures.mjs [--base http://127.0.0.1:4321] [--chrome PATH]
//
// For every course page that places live figures (src/data/live-figures.json):
//   - each mapped image is upgraded, nothing else is
//   - no console errors or exceptions
//   - scrolling the whole page brings every figure live, never more than
//     MAX_LIVE WebGL contexts at once
//   - a live figure's box equals its image box (no layout shift)
// On one page, additionally: keyboard orbit, wheel scrolls the page until the
// figure is engaged and zooms after, the view toggle, print media, touch mode,
// and the no-WebGL fallback.
import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const MAX_LIVE = 6;
const here = dirname(fileURLToPath(import.meta.url));
const placed = JSON.parse(readFileSync(join(here, '../src/data/live-figures.json'), 'utf8'));
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const BASE = opt('--base', 'http://127.0.0.1:4321').replace(/\/$/, '');
const CHROME = opt('--chrome', process.env.CHROME || [
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
].find(existsSync));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let failures = 0;
const check = (ok, msg) => {
  console.log(`${ok ? '  ok  ' : '  FAIL'} ${msg}`);
  if (!ok) failures++;
};

async function browser(extraFlags = []) {
  const port = 9500 + Math.floor(Math.random() * 400);
  const proc = spawn(CHROME, [
    '--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${mkdtempSync(join(tmpdir(), 'ru3d-'))}`,
    '--no-first-run', '--hide-scrollbars', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist',
    '--use-angle=swiftshader', '--window-size=1440,1000', ...extraFlags, 'about:blank',
  ], { stdio: 'ignore' });
  let targets;
  for (let i = 0; i < 80 && !targets; i++) {
    try { targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json(); } catch { await sleep(150); }
  }
  const ws = new WebSocket(targets.find((t) => t.type === 'page').webSocketDebuggerUrl);
  await new Promise((r) => { ws.onopen = r; });
  let id = 0;
  const pending = new Map();
  const errors = [];
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
    if (m.method === 'Runtime.exceptionThrown') errors.push(m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text);
    if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') errors.push(m.params.args.map((a) => a.value ?? a.description).join(' '));
    if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error' && !/favicon/.test(m.params.entry.url || '')) errors.push(`${m.params.entry.text} ${m.params.entry.url || ''}`);
  };
  const send = (method, params = {}) => new Promise((r) => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
  await send('Runtime.enable'); await send('Log.enable'); await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false });
  const evaluate = async (expression) => {
    const r = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
    if (r.result?.exceptionDetails) throw new Error(r.result.exceptionDetails.exception?.description || 'evaluate failed');
    return r.result?.result?.value;
  };
  const goto = async (url) => {
    errors.length = 0;
    await send('Page.navigate', { url });
    for (let i = 0; i < 60; i++) {
      if (await evaluate('document.readyState').catch(() => '') === 'complete') break;
      await sleep(100);
    }
    await sleep(500);
  };
  return { send, evaluate, goto, errors, close: () => { ws.close(); proc.kill('SIGKILL'); } };
}

// wait until fn() (an expression) is truthy, or time out
async function until(b, expr, ms = 15000) {
  const t0 = Date.now();
  while (Date.now() - t0 < ms) {
    if (await b.evaluate(expr).catch(() => false)) return true;
    await sleep(150);
  }
  return false;
}

const canvasHash = `(() => { const c = document.querySelector('.ru3d[data-state=live] canvas.ru3d-gl');
  if (!c) return null; const d = c.toDataURL(); let h = 0; for (let i = 0; i < d.length; i += 7) h = (h * 31 + d.charCodeAt(i)) | 0; return h; })()`;

async function checkPage(b, page, names) {
  console.log(`\n${page}`);
  await b.goto(`${BASE}/course/${page}/draft`);
  const n = await b.evaluate(`document.querySelectorAll('.ru3d').length`);
  const imgs = await b.evaluate(`[...document.querySelectorAll('article.prose img')].length`);
  check(n === names.length, `upgraded ${n} of ${names.length} mapped figures (${imgs} images on the page)`);
  // scroll the whole page in steps, watching the live-context count
  const height = await b.evaluate('document.documentElement.scrollHeight');
  let maxLive = 0;
  const everLive = new Set();
  const shifts = [];
  const shiftExpr = `[...document.querySelectorAll('.ru3d')].filter((f) => f.dataset.state === 'live')
    .map((f) => { const a = f.querySelector('.ru3d-stage').getBoundingClientRect(), i = f.querySelector('img').getBoundingClientRect();
      return Math.abs(a.width - i.width) + Math.abs(a.height - i.height) + Math.abs(a.top - i.top) + Math.abs(a.left - i.left); })`;
  for (let y = 0; y <= height; y += 500) {
    await b.evaluate(`window.scrollTo(0, ${y})`);
    await sleep(350);
    const st = await b.evaluate(`[...document.querySelectorAll('.ru3d')].map((f, i) => [i, f.dataset.state, document.querySelectorAll('canvas.ru3d-gl').length])`);
    for (const [i, s] of st) if (s === 'live') everLive.add(i);
    maxLive = Math.max(maxLive, st[0]?.[2] ?? 0);
    shifts.push(...await b.evaluate(shiftExpr));
  }
  await sleep(1500);
  const st = await b.evaluate(`[...document.querySelectorAll('.ru3d')].map((f) => f.dataset.state)`);
  st.forEach((s, i) => { if (s === 'live') everLive.add(i); });
  check(everLive.size === n, `every figure went live while scrolling (${everLive.size}/${n})`);
  check(maxLive <= MAX_LIVE, `at most ${MAX_LIVE} live WebGL contexts at once (max seen ${maxLive})`);
  check(shifts.every((d) => d < 1), `live figures sit exactly on their image box (${shifts.length} checks)`);
  check(b.errors.length === 0, `no console errors${b.errors.length ? ': ' + b.errors.slice(0, 3).join(' | ') : ''}`);
}

async function checkInteraction(b, page) {
  console.log(`\ninteraction (${page})`);
  await b.goto(`${BASE}/course/${page}/draft`);
  await b.evaluate(`document.querySelector('.ru3d').scrollIntoView({ block: 'center' })`);
  check(await until(b, `document.querySelector('.ru3d').dataset.state === 'live'`), 'first figure goes live when scrolled to');
  await sleep(500);

  // keyboard
  await b.evaluate(`document.querySelector('.ru3d-stage').focus()`);
  const h0 = await b.evaluate(canvasHash);
  for (const key of ['ArrowRight', 'ArrowRight', 'ArrowUp']) {
    await b.send('Input.dispatchKeyEvent', { type: 'keyDown', key, code: key, windowsVirtualKeyCode: { ArrowRight: 39, ArrowUp: 38 }[key] });
    await b.send('Input.dispatchKeyEvent', { type: 'keyUp', key, code: key });
  }
  await sleep(300);
  const h1 = await b.evaluate(canvasHash);
  check(h0 !== null && h1 !== h0, 'arrow keys orbit the focused figure');
  await b.send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'r', code: 'KeyR', text: 'r' });
  await b.send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'r', code: 'KeyR' });
  await sleep(300);
  check(await b.evaluate(canvasHash) === h0, 'R resets to the original framing');
  await b.evaluate('document.activeElement.blur()');

  // wheel: scrolls the page while idle; zooms once engaged
  const box = await b.evaluate(`(() => { const r = document.querySelector('.ru3d-stage').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; })()`);
  const y0 = await b.evaluate('scrollY');
  await b.send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: box[0], y: box[1] });
  await b.send('Input.dispatchMouseEvent', { type: 'mouseWheel', x: box[0], y: box[1], deltaX: 0, deltaY: 200 });
  await sleep(500);
  const y1 = await b.evaluate('scrollY');
  check(y1 > y0, `wheel over an idle figure scrolls the page (${y0} -> ${y1})`);
  await b.evaluate(`window.scrollTo(0, ${y0})`);
  await sleep(300);
  const hz0 = await b.evaluate(canvasHash);
  await b.send('Input.dispatchMouseEvent', { type: 'mousePressed', x: box[0], y: box[1], button: 'left', clickCount: 1 });
  await b.send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: box[0], y: box[1], button: 'left', clickCount: 1 });
  await b.send('Input.dispatchMouseEvent', { type: 'mouseWheel', x: box[0], y: box[1], deltaX: 0, deltaY: -300 });
  await sleep(500);
  const y2 = await b.evaluate('scrollY');
  const hz1 = await b.evaluate(canvasHash);
  check(y2 === y0 && hz1 !== hz0, `after a click, the wheel zooms the figure and the page stays put (${y0} -> ${y2})`);
  await b.send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: 5, y: 5 });

  // view toggle (first figure with two views)
  const hasTop = await b.evaluate(`(() => { const f = [...document.querySelectorAll('.ru3d')].find((x) => x.dataset.state === 'live' && !x.querySelector('.ru3d-view[data-view=top]').hidden); if (!f) return false; f.scrollIntoView({ block: 'center' }); f.querySelector('.ru3d-view[data-view=top]').click(); return true; })()`);
  if (hasTop) {
    await sleep(500);
    check(await b.evaluate(`[...document.querySelectorAll('.ru3d-view[data-view=top]')].some((b) => b.getAttribute('aria-pressed') === 'true')`), 'the top-view button switches the view');
  }

  // print media: the image, not the canvas
  await b.send('Emulation.setEmulatedMedia', { media: 'print' });
  await sleep(200);
  const pr = await b.evaluate(`(() => { const f = document.querySelector('.ru3d[data-state=live]');
    return [getComputedStyle(f.querySelector('.ru3d-stage')).display, getComputedStyle(f.querySelector('img')).visibility]; })()`);
  check(pr[0] === 'none' && pr[1] === 'visible', `print shows the image, hides the 3D stage (${pr})`);
  await b.send('Emulation.setEmulatedMedia', { media: '' });
  check(b.errors.length === 0, `no console errors${b.errors.length ? ': ' + b.errors.slice(0, 3).join(' | ') : ''}`);
}

async function checkTouch(b, page) {
  console.log(`\ntouch (${page})`);
  // a phone: touch input, no hover (what (hover: none) keys off)
  await b.send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 5 });
  await b.send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
  await b.goto(`${BASE}/course/${page}/draft`);
  await b.evaluate(`document.querySelector('.ru3d').scrollIntoView({ block: 'center' })`);
  check(await until(b, `document.querySelector('.ru3d').dataset.state === 'live'`), 'figure goes live');
  await sleep(300);
  const before = await b.evaluate(`[getComputedStyle(document.querySelector('.ru3d-tap')).display, document.querySelector('canvas.ru3d-gl').style.touchAction]`);
  check(before[0] !== 'none' && before[1] === 'pan-y', `idle: "tap to explore" shown, vertical swipes scroll the page (${before})`);
  await b.evaluate(`document.querySelector('.ru3d-tap').click()`);
  await sleep(200);
  const after = await b.evaluate(`[document.querySelector('.ru3d').classList.contains('is-active'), document.querySelector('canvas.ru3d-gl').style.touchAction]`);
  check(after[0] && after[1] === 'none', `engaged: all gestures go to the figure (${after})`);
  await b.evaluate(`document.querySelector('.ru3d-done').click()`);
  await sleep(200);
  check(!(await b.evaluate(`document.querySelector('.ru3d').classList.contains('is-active')`)), '"done" hands gestures back to the page');
  await b.send('Emulation.setTouchEmulationEnabled', { enabled: false });
  await b.send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false });
}

async function checkNoWebGL(page) {
  console.log(`\nno WebGL (${page})`);
  const b = await browser(['--disable-webgl', '--disable-3d-apis']);
  try {
    await b.goto(`${BASE}/course/${page}/draft`);
    await sleep(1000);
    const r = await b.evaluate(`[document.querySelectorAll('.ru3d').length, [...document.querySelectorAll('article.prose img')].filter((i) => /_minecraft/.test(i.currentSrc || i.src)).length]`);
    check(r[0] === 0 && r[1] > 0, `figures stay plain images (${r[0]} upgraded, ${r[1]} Minecraft images in place)`);
    check(b.errors.length === 0, `no console errors${b.errors.length ? ': ' + b.errors.slice(0, 3).join(' | ') : ''}`);
  } finally { b.close(); }
}

const b = await browser();
try {
  for (const [page, figs] of Object.entries(placed)) await checkPage(b, page, Object.keys(figs));
  const demo = 'part-ii-thinking-machine/05_adder-and-hex';
  await checkInteraction(b, demo);
  await checkTouch(b, demo);
} finally { b.close(); }
await checkNoWebGL('part-ii-thinking-machine/05_adder-and-hex');

console.log(failures ? `\n${failures} check(s) failed` : '\nall checks passed');
process.exit(failures ? 1 : 0);
