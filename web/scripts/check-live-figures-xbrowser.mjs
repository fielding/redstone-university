#!/usr/bin/env node
// Cross-engine checks for the live 3D figures: WebKit (Safari's engine),
// Firefox, WebKit with iPhone touch emulation, and Chromium on the hardware
// GPU. Complements check-live-figures.mjs (headless Chrome, full matrix).
// Playwright is not a site dependency; install it ad hoc:
//
//   npm i --no-save playwright && npx playwright install webkit firefox chromium
//   node scripts/check-live-figures-xbrowser.mjs [base-url] [screenshot-dir]
import { webkit, firefox, chromium, devices } from 'playwright';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const BASE = process.argv[2] || 'http://127.0.0.1:4321';
const OUT = process.argv[3] || '/tmp';
const PAGE = 'part-ii-thinking-machine/05_adder-and-hex';
const placed = JSON.parse(readFileSync(join(dirname(fileURLToPath(import.meta.url)), '../src/data/live-figures.json'), 'utf8'));
const expected = Object.keys(placed[PAGE]).length;
let failures = 0;
const check = (ok, msg) => { console.log(`${ok ? '  ok  ' : '  FAIL'} ${msg}`); if (!ok) failures++; };
const hashExpr = `(() => { const c = document.querySelector('.ru3d[data-state=live] canvas.ru3d-gl'); if (!c) return null;
  const d = c.toDataURL(); let h = 0; for (let i = 0; i < d.length; i += 7) h = (h * 31 + d.charCodeAt(i)) | 0; return [h, d.length]; })()`;

async function run(name, browserType, contextOpts, { touch = false, launch = {} } = {}) {
  console.log(`\n${name}`);
  const browser = await browserType.launch(launch);
  const ctx = await browser.newContext(contextOpts);
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => { if ((m.type() === 'error' && !/favicon/.test(m.text())) || (m.type() === 'warning' && /\[live 3D\]/.test(m.text()))) errors.push(m.text()); });
  await page.goto(`${BASE}/course/${PAGE}/draft`, { waitUntil: 'load' });
  await page.waitForTimeout(800);
  const n = await page.evaluate(() => document.querySelectorAll('.ru3d').length);
  check(n === expected, `${n} of ${expected} figures upgraded`);
  const fig = page.locator('.ru3d').first();
  await fig.scrollIntoViewIfNeeded();
  await page.waitForFunction(() => document.querySelector('.ru3d')?.dataset.state === 'live', null, { timeout: 30000 }).catch(() => {});
  const state = await page.evaluate(() => document.querySelector('.ru3d').dataset.state);
  check(state === 'live', `first figure goes live (${state})`);
  await page.waitForTimeout(800);
  // the canvas must hold a real frame, not a blank: count opaque pixels
  const opaque = await page.evaluate(() => {
    const c = document.querySelector('.ru3d[data-state=live] canvas.ru3d-gl');
    const t = document.createElement('canvas'); t.width = c.width; t.height = c.height;
    const x = t.getContext('2d'); x.drawImage(c, 0, 0);
    const d = x.getImageData(0, 0, t.width, t.height).data; let n = 0;
    for (let i = 3; i < d.length; i += 16) if (d[i] > 200) n++;
    return n / (d.length / 16);
  });
  check(opaque > 0.05, `canvas draws the build (${(opaque * 100).toFixed(1)}% of sampled pixels opaque)`);
  await fig.screenshot({ path: `${OUT}/xb_${name.replace(/\W+/g, '_')}.png` });

  // keyboard
  await page.evaluate(() => document.querySelector('.ru3d-stage').focus());
  const h0 = await page.evaluate(hashExpr);
  await page.keyboard.press('ArrowRight');
  await page.keyboard.press('ArrowRight');
  await page.waitForTimeout(400);
  const h1 = await page.evaluate(hashExpr);
  check(h0 && h1 && h0[0] !== h1[0], 'arrow keys orbit');
  await page.keyboard.press('r');
  await page.waitForTimeout(400);
  const h2 = await page.evaluate(hashExpr);
  check(h2 && h2[0] === h0[0], 'R resets the view');
  await page.evaluate(() => document.activeElement.blur());

  const box = await page.locator('.ru3d-stage').first().boundingBox();
  const cx = box.x + box.width / 2, cy = box.y + box.height / 2;
  if (!touch) {
    // wheel: idle -> page scrolls; after a click -> zoom, page still
    await page.mouse.move(cx, cy);
    const y0 = await page.evaluate(() => scrollY);
    await page.mouse.wheel(0, 200);
    await page.waitForTimeout(500);
    const y1 = await page.evaluate(() => scrollY);
    check(y1 > y0, `wheel over an idle figure scrolls the page (${y0} -> ${y1})`);
    await page.evaluate((y) => scrollTo(0, y), y0);
    await page.waitForTimeout(300);
    const b2 = await page.locator('.ru3d-stage').first().boundingBox();
    const z0 = await page.evaluate(hashExpr);
    await page.mouse.click(b2.x + b2.width / 2, b2.y + b2.height / 2);
    await page.mouse.wheel(0, -300);
    await page.waitForTimeout(500);
    const y2 = await page.evaluate(() => scrollY);
    const z1 = await page.evaluate(hashExpr);
    check(Math.abs(y2 - y0) < 2 && z1[0] !== z0[0], `after a click, the wheel zooms and the page stays (${y0} -> ${y2})`);
    // drag orbits
    const z2 = await page.evaluate(hashExpr);
    await page.mouse.move(b2.x + b2.width / 2, b2.y + b2.height / 2);
    await page.mouse.down(); await page.mouse.move(b2.x + b2.width / 2 + 120, b2.y + b2.height / 2, { steps: 8 }); await page.mouse.up();
    await page.waitForTimeout(400);
    const z3 = await page.evaluate(hashExpr);
    check(z3[0] !== z2[0], 'mouse drag orbits');
    await page.mouse.move(2, 2);
  } else {
    const idle = await page.evaluate(() => [getComputedStyle(document.querySelector('.ru3d-tap')).display,
      document.querySelector('canvas.ru3d-gl').style.touchAction]);
    check(idle[0] !== 'none' && idle[1] === 'pan-y', `idle: tap hint shown, vertical swipes scroll (${idle})`);
    await page.locator('.ru3d-tap').first().tap();
    await page.waitForTimeout(300);
    const act = await page.evaluate(() => [document.querySelector('.ru3d').classList.contains('is-active'),
      document.querySelector('canvas.ru3d-gl').style.touchAction]);
    check(act[0] && act[1] === 'none', `tap engages the figure (${act})`);
    await page.locator('.ru3d-done').first().tap();
    await page.waitForTimeout(300);
    check(!(await page.evaluate(() => document.querySelector('.ru3d').classList.contains('is-active'))), '"done" releases it');
  }

  // whole page: every figure goes live, never more than six at once
  const height = await page.evaluate(() => document.documentElement.scrollHeight);
  let maxLive = 0; const ever = new Set();
  for (let y = 0; y <= height; y += 600) {
    await page.evaluate((v) => scrollTo(0, v), y);
    await page.waitForTimeout(450);
    const r = await page.evaluate(() => [[...document.querySelectorAll('.ru3d')].map((f, i) => f.dataset.state === 'live' ? i : -1).filter((i) => i >= 0),
      document.querySelectorAll('canvas.ru3d-gl').length]);
    r[0].forEach((i) => ever.add(i)); maxLive = Math.max(maxLive, r[1]);
  }
  check(ever.size === n, `every figure went live while scrolling (${ever.size}/${n})`);
  check(maxLive <= 6, `at most 6 live contexts at once (max ${maxLive})`);
  check(errors.length === 0, `no console errors${errors.length ? ': ' + errors.slice(0, 3).join(' | ') : ''}`);
  await browser.close();
}

await run('WebKit desktop (Safari engine)', webkit, { viewport: { width: 1440, height: 1000 } });
await run('Firefox desktop', firefox, { viewport: { width: 1440, height: 1000 } });
await run('WebKit iPhone 15 (touch)', webkit, { ...devices['iPhone 15'] }, { touch: true });
await run('Chromium, hardware GPU', chromium, { viewport: { width: 1440, height: 1000 } },
  { launch: { args: ['--enable-gpu', '--use-angle=metal', '--ignore-gpu-blocklist'] } });
console.log(failures ? `\n${failures} check(s) failed` : '\nall checks passed');
process.exit(failures ? 1 : 0);
