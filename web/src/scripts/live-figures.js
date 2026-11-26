// Live 3D figures: progressive enhancement of the course's Minecraft renders.
//
// Every placed *_minecraft.png that has a published build (web/src/data/
// live-figures.json, written by scripts/usd_to_scene.py --publish) becomes an
// orbitable 3D view of the same build. The <img> stays in the page and keeps
// the figure's box, so there is no layout shift and the PNG remains the
// figure for no-JS, no-WebGL, print, crawlers and screen readers.
//
// Budget: browsers cap live WebGL contexts (~16 per page) and each figure is a
// download, so a figure goes live only near the viewport, at most MAX_LIVE at
// once, and falls back to its PNG when it scrolls far away. three.js itself is
// loaded on first use.
import placed from '../data/live-figures.json';

const MAX_LIVE = 6;
// Components (lamps, torches, levers, repeaters, comparators) wear the vanilla
// Minecraft textures, served from figures/3d/textures/. Set to false to draw
// them as flat colors instead, without serving any Mojang texture files.
const USE_TEXTURES = true;
const BASE = `${import.meta.env.BASE_URL.replace(/\/$/, '')}/figures/3d/`;
const NAME_RE = /([A-Za-z0-9_-]+_minecraft)(?:\.[A-Za-z0-9_-]+)?\.(?:png|webp|avif|jpe?g)/;

function pageKey() {
  const m = location.pathname.match(/\/course\/(.+?)\/(?:draft\/?)?$/);
  return m ? decodeURIComponent(m[1]).toLowerCase() : null;
}

function webglOk() {
  if (typeof WebGL2RenderingContext === 'undefined') return false;
  try {
    const gl = document.createElement('canvas').getContext('webgl2');
    gl?.getExtension('WEBGL_lose_context')?.loseContext();
    return !!gl;
  } catch {
    return false;
  }
}

let core = null;              // lazy: { loadRub, RuFigure }
const coreLoad = () => (core ??= Promise.all([
  import('../lib/ru3d/format.js'), import('../lib/ru3d/figure.js'),
]).then(([f, g]) => ({ loadRub: f.loadRub, RuFigure: g.RuFigure })));
const dataCache = new Map();  // shot -> Promise<decoded build>
const live = new Set();       // LiveFigure instances holding a WebGL context

const coarse = matchMedia('(hover: none)').matches;
const theme = () => (document.documentElement.dataset.theme === 'dark' ? 'schematic_dark' : 'schematic');

class LiveFigure {
  constructor(img, entry) {
    this.img = img;
    this.shot = entry.shot;
    this.view = entry.view;
    this.fig = null;
    this.visible = false;
    this.active = false;     // engaged: wheel zoom, full touch orbit
    this.loading = null;

    const host = img.parentElement?.tagName === 'P' && img.parentElement.childElementCount === 1
      ? img.parentElement : img;
    const el = document.createElement('figure');
    el.className = 'ru3d';
    el.dataset.state = 'poster';
    host.replaceWith(el);
    el.append(img);
    img.classList.add('ru3d-poster');
    this.el = el;

    const stage = document.createElement('div');
    stage.className = 'ru3d-stage';
    stage.tabIndex = 0;
    stage.setAttribute('role', 'application');
    stage.setAttribute('aria-roledescription', 'interactive 3D figure');
    const label = img.alt ? `${img.alt}. ` : '';
    stage.setAttribute('aria-label', `${label}Interactive 3D view: arrow keys rotate, plus and minus zoom, R resets.`);
    this.stage = stage;
    el.append(stage);

    const ui = document.createElement('div');
    ui.className = 'ru3d-ui';
    ui.innerHTML = `
      <span class="ru3d-badge" aria-hidden="true">3D</span>
      <button type="button" class="ru3d-view" data-view="iso" aria-label="Angled view">iso</button>
      <button type="button" class="ru3d-view" data-view="top" aria-label="View from above">top</button>
      <button type="button" class="ru3d-reset" aria-label="Reset the view">reset</button>
      <button type="button" class="ru3d-done" aria-label="Stop interacting with the figure">done</button>`;
    this.ui = ui;
    el.append(ui);
    // shown on touch-only devices, and on hybrids as soon as a touch lands
    const tap = document.createElement('button');
    tap.type = 'button';
    tap.className = 'ru3d-tap';
    tap.textContent = 'Tap to explore in 3D';
    tap.addEventListener('click', () => this.setActive(true));
    el.append(tap);
    if (coarse) el.classList.add('is-touch');

    ui.addEventListener('click', (e) => {
      const b = e.target.closest('button');
      if (!b) return;
      if (b.dataset.view) this.setView(b.dataset.view);
      else if (b.classList.contains('ru3d-reset')) this.fig?.reset();
      else if (b.classList.contains('ru3d-done')) this.setActive(false);
    });
    stage.addEventListener('keydown', (e) => this.onKey(e));
    stage.addEventListener('pointerdown', (e) => {
      // a mouse press engages zoom; on touch the explicit tap button does
      if (e.pointerType === 'mouse') this.setActive(true);
      else if (e.pointerType === 'touch') this.el.classList.add('is-touch');
    });
    stage.addEventListener('pointerleave', (e) => {
      if (e.pointerType === 'mouse') this.setActive(false);
    });
    stage.addEventListener('focus', () => this.ensureLive());
    this.ro = new ResizeObserver(() => this.resize());
  }

  async ensureLive() {
    if (this.fig || this.loading) return this.loading;
    this.loading = (async () => {
      const { loadRub, RuFigure } = await coreLoad();
      let data;
      try {
        if (!dataCache.has(this.shot)) dataCache.set(this.shot, loadRub(`${BASE}${this.shot}.rub`));
        data = await dataCache.get(this.shot);
      } catch (e) {
        console.warn(`[live 3D] ${this.shot}: ${e.message}; keeping the image`);
        dataCache.delete(this.shot);
        this.el.dataset.state = 'failed';
        return;
      }
      if (!this.visible && document.activeElement !== this.stage) return;
      makeRoom(this);
      const canvas = document.createElement('canvas');
      canvas.className = 'ru3d-gl';
      const overlay = document.createElement('canvas');
      overlay.className = 'ru3d-legend';
      overlay.setAttribute('aria-hidden', 'true');
      this.stage.replaceChildren(canvas, overlay);
      canvas.addEventListener('webglcontextlost', (e) => { e.preventDefault(); this.release(); });
      try {
        this.fig = new RuFigure({ canvas, overlay, data, view: this.view, theme: theme(), textureBase: USE_TEXTURES ? `${BASE}textures/` : null });
      } catch (e) {
        console.warn(`[live 3D] ${this.shot}: WebGL failed (${e.message}); keeping the image`);
        this.stage.replaceChildren();
        this.el.dataset.state = 'failed';
        return;
      }
      live.add(this);
      this.fig.setZoomEnabled(false);
      this.syncViewButtons();
      this.applyTouchMode();
      this.ro.observe(this.stage);
      this.resize();
      await this.fig.ready;
      if (this.fig) this.el.dataset.state = 'live';
    })().finally(() => { this.loading = null; });
    return this.loading;
  }

  resize() {
    if (!this.fig) return;
    const r = this.stage.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    if (r.width > 0 && r.height > 0) this.fig.resize(r.width * dpr, r.height * dpr);
  }

  /** Give the context back and show the PNG again. */
  release() {
    if (!this.fig) return;
    this.setActive(false);
    this.ro.disconnect();
    this.fig.dispose();
    this.fig = null;
    live.delete(this);
    this.stage.replaceChildren();
    this.el.dataset.state = 'poster';
  }

  setView(view) {
    this.view = view;
    this.fig?.setView(view);
    this.syncViewButtons();
  }

  syncViewButtons() {
    const views = this.fig?.data.params.views || [this.view];
    for (const b of this.ui.querySelectorAll('.ru3d-view')) {
      b.hidden = views.length < 2 || !views.includes(b.dataset.view);
      b.setAttribute('aria-pressed', String(b.dataset.view === this.view));
    }
  }

  setActive(on) {
    if (on === this.active) return;
    this.active = on;
    this.el.classList.toggle('is-active', on);
    if (on) this.ensureLive();
    this.fig?.setZoomEnabled(on);
    this.applyTouchMode();
    if (on && this.el.classList.contains('is-touch')) {
      // a tap anywhere else ends touch interaction
      this.outside = (e) => { if (!this.el.contains(e.target)) this.setActive(false); };
      setTimeout(() => document.addEventListener('pointerdown', this.outside), 0);
    } else if (this.outside) {
      document.removeEventListener('pointerdown', this.outside);
      this.outside = null;
    }
  }

  // Touch: until engaged, a vertical swipe scrolls the page and a horizontal
  // one turns the build; engaged, every gesture belongs to the figure.
  applyTouchMode() {
    this.fig?.setTouchAction(this.active ? 'none' : 'pan-y');
  }

  async onKey(e) {
    const keys = ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', '+', '=', '-', '_', 'r', 'R', '0', 't', 'T', 'Escape'];
    if (!keys.includes(e.key) || e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.key === 'Escape') { this.setActive(false); return; }
    e.preventDefault();
    await this.ensureLive();
    const f = this.fig;
    if (!f) return;
    const step = e.shiftKey ? 45 : 10;
    switch (e.key) {
      case 'ArrowLeft': f.orbit(-step, 0); break;
      case 'ArrowRight': f.orbit(step, 0); break;
      case 'ArrowUp': f.orbit(0, step); break;
      case 'ArrowDown': f.orbit(0, -step); break;
      case '+': case '=': f.zoom(1.2); break;
      case '-': case '_': f.zoom(1 / 1.2); break;
      case 't': case 'T': {
        const views = f.data.params.views || [];
        const next = views[(views.indexOf(this.view) + 1) % views.length];
        if (next && next !== this.view) this.setView(next);
        break;
      }
      default: f.reset();
    }
  }
}

// Keep at most MAX_LIVE contexts: evict whichever live figure is farthest
// from the viewport (never the one being made live, never a focused one).
function makeRoom(incoming) {
  if (live.size < MAX_LIVE) return;
  const mid = innerHeight / 2;
  const dist = (lf) => {
    const r = lf.el.getBoundingClientRect();
    return Math.abs(r.top + r.height / 2 - mid);
  };
  const candidates = [...live].filter((lf) => lf !== incoming && document.activeElement !== lf.stage);
  candidates.sort((a, b) => dist(b) - dist(a));
  candidates[0]?.release();
}

function init() {
  const page = placed[pageKey()];
  if (!page || !webglOk()) return;
  const figs = [];
  for (const img of document.querySelectorAll('article.prose img')) {
    const src = decodeURIComponent(img.currentSrc || img.src || '');
    const name = (src.match(NAME_RE) || [])[1];
    if (name && page[name]) figs.push(new LiveFigure(img, page[name]));
  }
  if (!figs.length) return;
  const byEl = new Map(figs.map((f) => [f.el, f]));
  // near: start loading a little before the figure scrolls in
  const near = new IntersectionObserver((entries) => {
    for (const e of entries) {
      const lf = byEl.get(e.target);
      lf.visible = e.isIntersecting;
      if (e.isIntersecting) lf.ensureLive();
    }
  }, { rootMargin: '400px 0px' });
  // far: release contexts that have scrolled well out of reach
  const far = new IntersectionObserver((entries) => {
    for (const e of entries) {
      const lf = byEl.get(e.target);
      if (!e.isIntersecting && document.activeElement !== lf.stage) lf.release();
    }
  }, { rootMargin: '1600px 0px' });
  for (const f of figs) { near.observe(f.el); far.observe(f.el); }
  addEventListener('keydown', (e) => {
    if (e.key === 'Escape') for (const lf of live) lf.setActive(false);
  });
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
else init();
