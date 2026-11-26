// Dev viewer for the live 3D figures: a picker over every converted build
// (viewer/builds/*.rub), style toggles, and the Blender PNG side by side for
// comparison. Rendering lives in web/src/lib/ru3d (shared with the course
// site); this file is only the UI around it.
import { loadRub } from '../web/src/lib/ru3d/format.js';
import { RuFigure, figureAspect } from '../web/src/lib/ru3d/figure.js';

const $ = (id) => document.getElementById(id);
const status = (msg) => { $('status').textContent = msg; };
const url = new URL(location.href);
const state = {
  shot: url.searchParams.get('shot'),
  view: url.searchParams.get('view') || 'iso',
  theme: url.searchParams.get('theme') || 'schematic',
  outline: true, seams: true, bands: true, legend: url.searchParams.get('legend') !== '0',
  orbit: false, linePx: 1,
};

let fig = null;
window.__ruLoaded = false;

function stageSize() {
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const s = $('stage');
  return [s.clientWidth * dpr, s.clientHeight * dpr];
}

function applyStyle() {
  if (!fig) return;
  Object.assign(fig.style, {
    outline: state.outline, seams: state.seams, bands: state.bands, legend: state.legend, linePx: state.linePx,
  });
  fig.setInteractive(state.orbit);
  fig.requestRender();
}

async function loadShot(name) {
  status(`loading ${name}…`);
  window.__ruLoaded = false;
  let data;
  try {
    data = await loadRub(`./builds/${name}.rub`);
  } catch (e) {
    status(`no build for ${name} (run scripts/usd_to_scene.py ${name}): ${e.message}`);
    return;
  }
  state.shot = name;
  if (!data.params.views?.includes(state.view)) state.view = data.params.views?.[0] || 'iso';
  $('view').value = state.view;
  document.documentElement.dataset.theme = state.theme.endsWith('dark') ? 'dark' : 'light';

  // a fresh canvas per build: a disposed renderer leaves its context lost
  fig?.dispose();
  const old = $('gl');
  const canvas = document.createElement('canvas');
  canvas.id = 'gl';
  old.replaceWith(canvas);
  fig = new RuFigure({
    canvas, overlay: $('legend-cv'), data, view: state.view, theme: state.theme,
    textureBase: './textures/', legend: state.legend,
  });
  const { aspect } = figureAspect(data, state.view);
  for (const s of document.querySelectorAll('.stage')) s.style.aspectRatio = `${aspect}`;
  applyStyle();
  fig.resize(...stageSize());
  await fig.ready;
  window.__ruLoaded = true;

  const ref = `../renders/out/${name}_${state.view}.png`;
  $('ref').src = ref;
  $('overlay').src = ref;
  url.searchParams.set('shot', name);
  url.searchParams.set('view', state.view);
  url.searchParams.set('theme', state.theme);
  history.replaceState(null, '', url);
  const tris = data.meshes.reduce((n, m) => n + m.indices.length / 3, 0) + (data.wires ? data.wires.indices.length / 3 : 0);
  const b = data.bounds;
  const blocks = [0, 1, 2].map((a) => Math.round((b.max[a] - b.min[a]) / 16)).join('×');
  status(`${name} [${state.view}] ${data.meshes.length} meshes + wires, ${tris} tris, ~${blocks} blocks, ` +
    `ground=${data.params.ground} az=${data.params.azimuth} legend=${data.params.legend ? 'yes' : 'no'}`);
  window.__ru = { data, fig };
}

// headless drivers (viewer/snap.mjs): PNG at figure resolution, legend stamped
window.__ruExport = (ss) => fig.exportPNG(ss ?? 2);

async function init() {
  const idx = await (await fetch('./builds/index.json')).json();
  const sel = $('shot');
  for (const n of idx) {
    const o = document.createElement('option');
    o.value = n; o.textContent = n;
    sel.appendChild(o);
  }
  if (!state.shot || !idx.includes(state.shot)) state.shot = idx[0];
  sel.value = state.shot;
  $('view').value = state.view;
  $('theme').value = state.theme;
  sel.addEventListener('change', () => loadShot(sel.value));
  $('view').addEventListener('change', () => { state.view = $('view').value; loadShot(state.shot); });
  $('theme').addEventListener('change', () => { state.theme = $('theme').value; loadShot(state.shot); });
  for (const k of ['outline', 'seams', 'bands', 'orbit', 'legend']) {
    $(k).checked = state[k];
    $(k).addEventListener('change', () => { state[k] = $(k).checked; applyStyle(); });
  }
  $('linepx').addEventListener('input', () => { state.linePx = parseFloat($('linepx').value); applyStyle(); });
  $('overlayop').addEventListener('input', () => { $('overlay').style.opacity = $('overlayop').value; });
  $('reset').addEventListener('click', () => fig?.reset());
  $('export').addEventListener('click', async () => {
    const a = document.createElement('a');
    a.href = await fig.exportPNG(2);
    a.download = `${state.shot}_${state.view}_three.png`;
    a.click();
  });
  window.addEventListener('resize', () => fig?.resize(...stageSize()));
  await loadShot(state.shot);
}

init().catch((e) => { status('ERROR: ' + (e.stack || e)); console.error(e); });
