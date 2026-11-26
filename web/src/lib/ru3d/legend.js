// Region legend: port of scripts/shots.py stamp_legend. One chip + label per
// region, bottom-left by default, walking the other corners when the build
// reaches in. Chips are iso cubes shaded like the structure shader (tops
// brighter than sides) so they read as the same material as the regions.
import { TECHNICAL, hexToRgb } from './shaders.js';

export const LEGEND_FONT = '"Young Serif", Georgia, serif';

const inkCss = (theme) => {
  const c = theme.endsWith('dark') ? TECHNICAL[theme].line : [48 / 255, 35 / 255, 30 / 255];
  return `rgb(${c.map((v) => Math.round(v * 255)).join(',')})`;
};
const shadeHex = (hex, k) =>
  `rgb(${hexToRgb(hex).map((v) => Math.min(255, Math.round(v * 255 * k))).join(',')})`;

function drawChip(ctx, x, y, sw, hex, theme) {
  const e = sw / 2;
  const half = e * 0.8660254;
  const cx = x + half;
  const P = {
    apex: [cx, y], rt: [cx + half, y + e / 2], mid: [cx, y + e], lt: [cx - half, y + e / 2],
    lb: [cx - half, y + 1.5 * e], bot: [cx, y + 2 * e], rb: [cx + half, y + 1.5 * e],
  };
  const path = (pts) => pts.forEach(([px, py], i) => (i ? ctx.lineTo(px, py) : ctx.moveTo(px, py)));
  const face = (pts, fill) => { ctx.beginPath(); path(pts); ctx.closePath(); ctx.fillStyle = fill; ctx.fill(); };
  face([P.apex, P.rt, P.mid, P.lt], shadeHex(hex, 1.05));
  face([P.lt, P.mid, P.bot, P.lb], shadeHex(hex, 0.93));
  face([P.mid, P.rt, P.rb, P.bot], shadeHex(hex, 0.84));
  ctx.strokeStyle = inkCss(theme);
  ctx.lineJoin = 'round';
  ctx.lineWidth = Math.max(1, sw / 28);
  ctx.beginPath();
  for (const p of [[P.apex, P.rt, P.rb, P.bot, P.lb, P.lt, P.apex], [P.lt, P.mid, P.rt], [P.mid, P.bot]]) path(p);
  ctx.stroke();
}

// alphaEmpty(x0, y0, x1, y1) reports whether a box is clear of the build.
// minSw: exports keep stamp_legend's 30px floor (figure resolution); live
// overlays scale with the on-screen size so a narrow column isn't swamped.
export function layoutLegend(ctx, w, h, legend, alphaEmpty, minSw = 30) {
  const sw = Math.max(minSw, Math.round(w * 0.023));
  const gap = Math.round(sw * 0.45);
  const pad = Math.round(sw * 0.55);
  const fontPx = Math.round(sw * 0.62);
  ctx.font = `${fontPx}px ${LEGEND_FONT}`;
  const items = [];
  let x = 0;
  for (const [label, hex] of Object.entries(legend)) {
    const cw = sw * 0.8660254;
    items.push({ off: x, label, hex, cw });
    x += cw + gap + ctx.measureText(label).width + pad * 2;
  }
  const rowW = x - pad * 2, rowH = sw, margin = sw, ring = Math.round(sw * 0.75);
  const corners = [[margin, h - margin - rowH], [margin, margin],
    [w - margin - rowW, margin], [w - margin - rowW, h - margin - rowH]];
  const spot = corners.find(([rx, ry]) =>
    alphaEmpty(rx - ring, ry - ring, rx + rowW + ring, ry + rowH + ring)) || null;
  return { sw, gap, fontPx, items, rowW, rowH, margin, ring, spot };
}

export function paintLegend(ctx, L, ox, oy, theme) {
  ctx.save();
  ctx.font = `${L.fontPx}px ${LEGEND_FONT}`;
  ctx.textBaseline = 'middle';
  for (const it of L.items) {
    const sx = ox + it.off;
    drawChip(ctx, sx, oy, L.sw, it.hex, theme);
    ctx.fillStyle = inkCss(theme);
    ctx.fillText(it.label, sx + it.cw + L.gap, oy + L.sw / 2);
  }
  ctx.restore();
}

export function alphaEmptyFn(ctx, w, h) {
  return (x0, y0, x1, y1) => {
    x0 = Math.max(0, Math.floor(x0)); y0 = Math.max(0, Math.floor(y0));
    x1 = Math.min(w, Math.ceil(x1)); y1 = Math.min(h, Math.ceil(y1));
    if (x1 <= x0 || y1 <= y0) return false;
    const d = ctx.getImageData(x0, y0, x1 - x0, y1 - y0).data;
    for (let i = 3; i < d.length; i += 4) if (d[i] > 8) return false;
    return true;
  };
}

// Stamp onto a 2D canvas holding a rendered figure. Grows the canvas downward
// when no corner is free, as stamp_legend does. Returns the (maybe new) canvas.
export function stampLegend(c, legend, theme) {
  const ctx = c.getContext('2d', { willReadFrequently: true });
  const L = layoutLegend(ctx, c.width, c.height, legend, alphaEmptyFn(ctx, c.width, c.height));
  if (L.spot) { paintLegend(ctx, L, L.spot[0], L.spot[1], theme); return c; }
  const g = document.createElement('canvas');
  g.width = c.width;
  g.height = c.height + L.ring + L.rowH + L.margin;
  const gctx = g.getContext('2d');
  gctx.drawImage(c, 0, 0);
  paintLegend(gctx, L, L.margin, c.height + L.ring, theme);
  return g;
}

// Live overlay: same dodge rule against the current WebGL frame.
export function drawLegendOverlay(overlay, glCanvas, legend, theme) {
  const w = glCanvas.width, h = glCanvas.height;
  overlay.width = w; overlay.height = h;
  const octx = overlay.getContext('2d');
  octx.clearRect(0, 0, w, h);
  const probe = document.createElement('canvas');
  probe.width = w; probe.height = h;
  const pctx = probe.getContext('2d', { willReadFrequently: true });
  pctx.drawImage(glCanvas, 0, 0);
  const L = layoutLegend(octx, w, h, legend, alphaEmptyFn(pctx, w, h), 12);
  const [ox, oy] = L.spot || [L.margin, h - L.margin - L.rowH];
  paintLegend(octx, L, ox, oy, theme);
}
