// Palettes and GLSL for the schematic look of scripts/render_usd.py
// (technical: schematic). Shared by the course site and the dev viewer.
// ------------------------------------------------------------------ palette
// TECHNICAL palettes from render_usd.py (display sRGB 0..1)
export const TECHNICAL = {
  schematic: {
    bg: [1, 1, 1], fill: [0.94, 0.94, 0.95], line: [0.06, 0.06, 0.08], lw: 1.2,
    bands: [[0.96, 0.96, 0.97], [0.99, 0.91, 0.73], [0.82, 0.89, 0.78], [0.80, 0.86, 0.90],
            [0.94, 0.84, 0.83], [0.98, 0.86, 0.77], [0.93, 0.91, 0.76]],
  },
  schematic_dark: {
    bg: [0.095, 0.082, 0.072], fill: [0.26, 0.23, 0.19], line: [0.88, 0.83, 0.74], lw: 1.2,
    bands: [[0.30, 0.27, 0.22], [0.60, 0.45, 0.21], [0.34, 0.50, 0.34], [0.30, 0.46, 0.58],
            [0.46, 0.37, 0.53], [0.60, 0.39, 0.28], [0.53, 0.50, 0.28]],
  },
};
export const COMPONENT_KW = ['torch', 'lever', 'repeater', 'comparator', 'lamp', 'button',
  'redstone_block', 'observer', 'target', 'tripwire', 'piston', 'dispenser', 'dropper',
  'note_block', 'rail'];
export const BLOCK = 16;

export const srgbToLin = (c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
export const lin3 = (rgb) => rgb.map(srgbToLin);
export const hexToRgb = (h) => [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16) / 255);

// ------------------------------------------------------------------ shaders
export const STRUCT_VERT = /* glsl */`
  attribute vec3 aBase;   // display-sRGB base color (fill or legend hue)
  attribute float aMode;  // 0 = palette height bands, 1 = hue band (tinted family)
  attribute float aLo;    // band origin y (scene base, or family base)
  attribute float aN;     // band count for this vertex's ramp
  varying vec3 vBase; varying float vMode; varying float vLo; varying float vN;
  varying vec3 vWorld; varying vec3 vNormal;
  void main() {
    vBase = aBase; vMode = aMode; vLo = aLo; vN = aN;
    vWorld = (modelMatrix * vec4(position, 1.0)).xyz;
    vNormal = normalize(mat3(modelMatrix) * normal);
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }`;

export const STRUCT_FRAG = /* glsl */`
  precision highp float;
  uniform vec3 uBands[32];
  uniform int uNBands;
  uniform float uStrength;
  uniform vec3 uInk;
  uniform float uSeamPx;
  uniform bool uSeams;
  uniform float uInterior;   // interior-ink strength, eased by on-screen block size
  uniform bool uBandsOn;
  varying vec3 vBase; varying float vMode; varying float vLo; varying float vN;
  varying vec3 vWorld; varying vec3 vNormal;

  vec3 s2l(vec3 c) {
    vec3 lo = c / 12.92;
    vec3 hi = pow((c + 0.055) / 1.055, vec3(2.4));
    return mix(lo, hi, step(vec3(0.04045), c));
  }
  // render_usd._hue_band: tones of one legend hue, lighter with height
  vec3 hueBand(vec3 hueDisp, float n, float i) {
    float t = 1.0 - i / max(n - 1.0, 1.0);
    vec3 tone;
    if (t < 0.5) { float w = 0.40 * (1.0 - 2.0 * t); tone = (1.0 - w) * hueDisp + w; }
    else { float k = 1.0 - 0.12 * (2.0 * t - 1.0); tone = hueDisp * k; }
    return s2l(tone);
  }
  void main() {
    vec3 n = normalize(vNormal);
    if (!gl_FrontFacing) n = -n;
    // _flat_fill: tops brighter than sides (map normal.y -1..1 -> 0.80..1.05)
    float shade = mix(0.80, 1.05, (n.y + 1.0) * 0.5);
    vec3 base = s2l(vBase);
    vec3 col = base;
    if (uBandsOn && vMode < 1.5) {
      // which block layer does this fragment belong to? top faces sit on the
      // boundary of their own block (-0.5 like render_usd), bottom faces on the
      // boundary below (+0.5); side faces span (16k, 16k+16] so a hair below
      float yoff = (n.y > 0.5) ? -0.5 : ((n.y < -0.5) ? 0.5 : -0.02);
      float layer = floor((vWorld.y - vLo + yoff) / 16.0);
      if (vMode < 0.5) {
        int bi = int(clamp(layer, 0.0, float(uNBands - 1)));
        vec3 band = uBands[bi];
        col = mix(base, band, uStrength);
      } else {
        float li = clamp(layer, 0.0, vN - 1.0);
        col = mix(base, hueBand(vBase, vN, li), uStrength);
      }
    }
    col *= shade;
    if (uSeams) {
      // block grid: x/z boundaries at 16b+8, y boundaries at 16k (mark_block_edges)
      vec3 ph = vec3(8.0, 0.0, 8.0);
      vec3 g = abs(fract((vWorld + ph) / 16.0 + 0.5) - 0.5) * 16.0;   // distance to nearest plane
      vec3 fw = fwidth(vWorld);
      vec3 an = abs(n);
      vec3 tangent = step(an, vec3(0.5));   // 1 for the two in-plane axes
      float line = 0.0;
      for (int a = 0; a < 3; a++) {
        float w = uSeamPx * max(fw[a], 1e-4);
        float l = 1.0 - smoothstep(w * 0.5, w * 1.5, g[a]);
        line = max(line, tangent[a] * l);
      }
      col = mix(col, uInk, line * uInterior);
    }
    gl_FragColor = vec4(col, 1.0);
    #include <colorspace_fragment>
  }`;

// normal + ink-eligibility pass (rgb = normal, a = 1 when this surface may get ink)
export const NORMAL_VERT = /* glsl */`
  varying vec3 vNormal;
  void main() {
    vNormal = normalize(mat3(modelMatrix) * normal);
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }`;
export const NORMAL_FRAG = /* glsl */`
  precision highp float;
  uniform float uInk;
  varying vec3 vNormal;
  void main() {
    vec3 n = normalize(vNormal);
    if (!gl_FrontFacing) n = -n;
    gl_FragColor = vec4(n * 0.5 + 0.5, uInk);
  }`;

// composite: color + ink edges from depth/normal discontinuities
export const EDGE_VERT = /* glsl */`
  varying vec2 vUv;
  void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`;
export const EDGE_FRAG = /* glsl */`
  precision highp float;
  #include <packing>
  uniform sampler2D tColor;
  uniform sampler2D tDepth;
  uniform sampler2D tNormal;
  uniform vec2 uTexel;
  uniform float uRadius;
  uniform vec3 uInk;
  uniform bool uOutline;
  uniform bool uOrtho;
  uniform float uInterior;
  uniform float uSilhouette;
  uniform bool uOneSided;
  uniform float uNear; uniform float uFar;
  varying vec2 vUv;

  float viewZ(vec2 uv) {
    float d = texture2D(tDepth, uv).x;
    if (d >= 1.0) return -1e6;   // background
    return uOrtho ? orthographicDepthToViewZ(d, uNear, uFar)
                  : perspectiveDepthToViewZ(d, uNear, uFar);
  }
  // one 4-neighbour probe at radius r; ink only where the responsible surface's
  // stroke class reaches thr (0.4 structure, 0.6 lamps, 1.0 top-view torches)
  float probe(float r, float thr, float zc, bool bgc, vec3 n0, float ac) {
    float ink = 0.0;
    vec2 offs[4];
    offs[0] = vec2(uTexel.x, 0.0); offs[1] = vec2(-uTexel.x, 0.0);
    offs[2] = vec2(0.0, uTexel.y); offs[3] = vec2(0.0, -uTexel.y);
    for (int i = 0; i < 4; i++) {
      vec2 uv = vUv + offs[i] * r;
      float z = viewZ(uv);
      vec4 nn = texture2D(tNormal, uv);
      bool bgn = (z < -9e5);
      float a = -1.0;
      // one-sided (live view): only the pixel on the owning side inks, so lines
      // are 1px instead of straddling the edge; exports keep both sides and
      // get thinned by the 2x downsample instead
      if (bgc && !bgn) a = uOneSided ? -1.0 : nn.a;  // silhouette, seen from outside
      else if (!bgc && bgn) a = ac;              // silhouette, seen from inside
      else if (!bgc && !bgn) {
        float dz = abs(z - zc);
        float thrz = 1.5 + 0.004 * abs(zc);       // world units (block = 16)
        vec3 n1 = nn.rgb * 2.0 - 1.0;
        if (dz > thrz) a = (z > zc) ? (uOneSided ? -1.0 : nn.a) : ac;  // depth step: nearer surface owns the line
        else if (dot(n0, n1) < 0.80 && (!uOneSided || i == 0 || i == 2)) a = ac;  // crease: one side only when one-sided
      }
      // the outer silhouette always gets full ink; interior lines ease off when
      // blocks are small on screen so they don't bury the region colors
      if (a >= thr && a > 0.0) ink = max(ink, (bgc != bgn) ? uSilhouette : uInterior);
    }
    return ink;
  }
  void main() {
    vec4 col = texture2D(tColor, vUv);
    if (!uOutline) { gl_FragColor = col;
      #include <colorspace_fragment>
      return; }
    vec4 nc = texture2D(tNormal, vUv);
    float zc = viewZ(vUv);
    bool bgc = (zc < -9e5);
    vec3 n0 = nc.rgb * 2.0 - 1.0;
    float ink = probe(uRadius, 0.3, zc, bgc, n0, nc.a);
    ink = max(ink, probe(uRadius * 1.33, 0.5, zc, bgc, n0, nc.a));
    ink = max(ink, probe(uRadius * 2.5, 0.9, zc, bgc, n0, nc.a));
    vec3 rgb = mix(col.rgb, uInk, ink);
    float alpha = max(col.a, ink);
    gl_FragColor = vec4(rgb, alpha);
    // pass 1 rendered to a linear target; encode once here for the canvas
    #include <colorspace_fragment>
  }`;
