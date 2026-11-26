// One live 3D figure: a WebGL renderer bound to a canvas, showing one build
// (decoded .rub) in the schematic look of scripts/render_usd.py.
//
// What it reproduces: flat emission fills with a faint normal shade, per-layer
// height bands, legend tints with per-family tone bands, block seams drawn
// in-shader on the 16-unit grid, an ink post-pass (silhouette + crease from
// depth/normal edges, components and wires excluded like the Freestyle
// exclusion collection, lamp and top-view torch rims), power-colored wires,
// and the tele iso / ortho plan cameras framed like make_camera().
// Not reproduced: Cycles ambient occlusion.
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import {
  TECHNICAL, BLOCK, lin3, hexToRgb,
  STRUCT_VERT, STRUCT_FRAG, NORMAL_VERT, NORMAL_FRAG, EDGE_VERT, EDGE_FRAG,
} from './shaders.js';
import { drawLegendOverlay, stampLegend, LEGEND_FONT } from './legend.js';

const ISO_ELEVATION = 35.264;

function longestKey(map, name) {
  let best = null;
  for (const k of Object.keys(map)) {
    if (name.includes(k.toLowerCase()) && (best === null || k.length > best.length)) best = k;
  }
  return best;
}

function viewDirection(azDeg, elDeg) {
  // Blender: rotation_euler (90-el, 0, az) looks along (-sin az cos el, cos az cos el, -sin el);
  // USD/three (Y-up) maps Blender (x, y, z) to (x, z, -y)
  const az = THREE.MathUtils.degToRad(azDeg), el = THREE.MathUtils.degToRad(elDeg);
  return new THREE.Vector3(-Math.sin(az) * Math.cos(el), -Math.sin(el), -Math.cos(az) * Math.cos(el)).normalize();
}

/** The aspect (w/h) the shot's figure PNG was rendered at. */
export function figureAspect(data, view) {
  const p = data.params;
  const res = (view === 'top' && p.top_res) ? p.top_res : (p.res || '1920x1440');
  const [w, h] = String(res).split('x').map(Number);
  return { w, h, aspect: w / h };
}

export class RuFigure {
  /**
   * @param {object} o
   * @param {HTMLCanvasElement} o.canvas      WebGL canvas
   * @param {HTMLCanvasElement} [o.overlay]  2D canvas stacked on top, for the legend
   * @param {object} o.data                  decoded build (format.js)
   * @param {string} [o.view]                'iso' | 'top'
   * @param {string} [o.theme]               key of TECHNICAL
   * @param {string} o.textureBase           URL prefix for block textures
   * @param {boolean} [o.legend]
   */
  constructor({ canvas, overlay = null, data, view, theme = 'schematic', textureBase, legend = true }) {
    this.canvas = canvas;
    this.overlay = overlay;
    this.data = data;
    this.theme = TECHNICAL[theme] ? theme : 'schematic';
    this.textureBase = textureBase;
    this.style = { outline: true, seams: true, bands: true, linePx: 1, legend };
    this.view = data.params.views?.includes(view) ? view : (data.params.views?.[0] || 'iso');
    this.exporting = false;
    this.userMoved = false;
    this._pending = false;
    this._disposed = false;
    this._size = [0, 0];

    this.renderer = new THREE.WebGLRenderer({
      canvas, antialias: false, alpha: true, preserveDrawingBuffer: true,
      powerPreference: 'low-power',
    });
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.setClearColor(0x000000, 0);
    this.renderer.setPixelRatio(1);

    this.scene = new THREE.Scene();
    this._textures = new Map();
    this._texUsers = {};
    this._texLoads = [];
    this._buildScene();
    this.ready = Promise.allSettled(this._texLoads).then(() => this.requestRender());
    this._fontsReady = document.fonts?.load?.(`40px ${LEGEND_FONT}`).catch(() => {});
    this._fontsReady?.then(() => this.requestRender());
  }

  // -------------------------------------------------------------- scene
  // A texture that fails to load must not leave its component invisible (an
  // empty map with alphaTest discards every fragment): fall back to the
  // component's flat color and say so.
  _loadTexture(name, mat, fallback) {
    (this._texUsers[name] ??= []).push([mat, fallback]);
    if (this._textures.has(name)) return this._textures.get(name);
    const tex = new THREE.Texture();
    tex.magFilter = THREE.NearestFilter;
    tex.minFilter = THREE.NearestFilter;
    tex.generateMipmaps = false;
    tex.colorSpace = THREE.SRGBColorSpace;
    this._textures.set(name, tex);
    this._texLoads.push(new Promise((resolve, reject) => {
      const img = new Image();
      img.decoding = 'async';
      img.onload = () => { tex.image = img; tex.needsUpdate = true; resolve(); };
      img.onerror = () => {
        console.warn(`[live 3D] texture ${name} failed to load; drawing flat colors`);
        for (const [m, color] of this._texUsers[name]) {
          m.map = null;
          m.color.copy(color);
          m.needsUpdate = true;
        }
        this.requestRender();
        reject(new Error(`texture ${name}`));
      };
      img.src = this.textureBase + name;
    }));
    return tex;
  }

  _buildScene() {
    const data = this.data;
    const cfg = TECHNICAL[this.theme];
    const p = data.params;
    const tints = p.tint || {};
    // band origin: Blender's height-tint bbox is stale after ground removal, so
    // the removed platform layer still counts as layer 0 (see the converter)
    const baseY = data.band_base_y ?? (data.bounds_pre || data.bounds).min[1];
    const nLayers = Math.min(32, Math.max(2, Math.round((data.bounds.max[1] - baseY) / BLOCK)));
    const bandOffset = p.band_offset || 0;
    const bands = [];
    for (let i = 0; i < 32; i++) {
      const c = cfg.bands[(Math.min(i, nLayers - 1) + bandOffset) % cfg.bands.length];
      bands.push(new THREE.Vector3(...lin3(c)));
    }
    const strength = (p.technical || 'schematic').startsWith('schematic') ? (p.height_tint ?? 0.9) : 0;

    // per-family y ranges for tinted families, keyed by hue like render_usd
    const famRange = {};
    for (const m of data.meshes) {
      if (m.role !== 'structure' && m.role !== 'pad') continue;
      const key = longestKey(tints, m.name.toLowerCase());
      if (!key) continue;
      let lo = Infinity, hi = -Infinity;
      for (let i = 1; i < m.positions.length; i += 3) { lo = Math.min(lo, m.positions[i]); hi = Math.max(hi, m.positions[i]); }
      const cur = famRange[tints[key]];
      famRange[tints[key]] = cur ? [Math.min(cur[0], lo), Math.max(cur[1], hi)] : [lo, hi];
    }

    this.structMat = new THREE.ShaderMaterial({
      vertexShader: STRUCT_VERT, fragmentShader: STRUCT_FRAG,
      uniforms: {
        uBands: { value: bands }, uNBands: { value: nLayers }, uStrength: { value: strength },
        uInk: { value: new THREE.Vector3(...lin3(cfg.line)) },
        uSeamPx: { value: 1.2 * this.style.linePx }, uSeams: { value: this.style.seams },
        uBandsOn: { value: this.style.bands }, uInterior: { value: 1 },
      },
      side: THREE.DoubleSide,
    });
    // stroke class -> alpha of the normal pass: 0 none, 0.4 base ink,
    // 0.6 lamp rim (1.33x), 1.0 top-view torch rim (2.5x)
    this.inkMaterials = {};
    for (const cls of [0, 0.4, 0.6, 1.0]) {
      this.inkMaterials[cls] = new THREE.ShaderMaterial({
        vertexShader: NORMAL_VERT, fragmentShader: NORMAL_FRAG,
        uniforms: { uInk: { value: cls } }, side: THREE.DoubleSide,
      });
    }

    for (const m of data.meshes) {
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.BufferAttribute(m.positions, 3));
      g.setAttribute('normal', new THREE.BufferAttribute(m.normals, 3));
      if (m.uvs) g.setAttribute('uv', new THREE.BufferAttribute(m.uvs, 2));
      g.setIndex(new THREE.BufferAttribute(m.indices, 1));
      const nv = m.positions.length / 3;
      const lname = m.name.toLowerCase();
      let mesh;
      if (m.role === 'component') {
        const mat = new THREE.MeshBasicMaterial({ side: THREE.DoubleSide, alphaTest: 0.5 });
        const emit = lname.includes('lamp_on') ? 1.6 : 1.15;
        const flat = new THREE.Color(...(m.displayColor || [0.6, 0.6, 0.62])).multiplyScalar(emit);
        if (m.texture && this.textureBase) {
          mat.map = this._loadTexture(m.texture, mat, flat);
          mat.color.setScalar(emit);
        } else {
          mat.color.copy(flat);
        }
        mesh = new THREE.Mesh(g, mat);
        mesh.userData.lamp = lname.includes('lamp');
        mesh.userData.torch = lname.includes('redstone_torch');
      } else {
        const key = longestKey(tints, lname);
        let rgb, md, l0, n0;
        if (m.role === 'pad') {
          // RU_GroundPads: flat neutral fill, or the region's flat tint (no bands)
          rgb = key ? hexToRgb(tints[key]) : cfg.fill; md = 2; l0 = baseY; n0 = nLayers;
        } else if (key) {
          rgb = hexToRgb(tints[key]);
          const fr = famRange[tints[key]];
          md = 1; l0 = fr[0]; n0 = Math.min(32, Math.max(2, Math.round((fr[1] - fr[0]) / BLOCK)));
        } else {
          rgb = cfg.fill; md = 0; l0 = baseY; n0 = nLayers;
        }
        const base = new Float32Array(nv * 3), mode = new Float32Array(nv);
        const lo = new Float32Array(nv), nn = new Float32Array(nv);
        for (let i = 0; i < nv; i++) {
          base[i * 3] = rgb[0]; base[i * 3 + 1] = rgb[1]; base[i * 3 + 2] = rgb[2];
          mode[i] = md; lo[i] = l0; nn[i] = n0;
        }
        g.setAttribute('aBase', new THREE.BufferAttribute(base, 3));
        g.setAttribute('aMode', new THREE.BufferAttribute(mode, 1));
        g.setAttribute('aLo', new THREE.BufferAttribute(lo, 1));
        g.setAttribute('aN', new THREE.BufferAttribute(nn, 1));
        mesh = new THREE.Mesh(g, this.structMat);
        mesh.userData.ink = 0.4;
      }
      mesh.userData.role = m.role;
      mesh.name = m.name;
      this.scene.add(mesh);
    }
    if (data.wires) {
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.BufferAttribute(data.wires.positions, 3));
      g.setAttribute('color', new THREE.BufferAttribute(data.wires.colors, 3));
      g.setIndex(new THREE.BufferAttribute(data.wires.indices, 1));
      g.computeVertexNormals();
      // RU_Wire: emission 1.15 of the linear power color
      const mat = new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.DoubleSide });
      mat.color.setScalar(1.15);
      const w = new THREE.Mesh(g, mat);
      w.name = 'RU_Wires';
      w.userData.ink = 0;
      w.userData.role = 'wire';
      this.scene.add(w);
    }
    this._applyInkClasses();
  }

  // Freestyle exclusion: components carry no ink, except lamps (rim, every
  // view) and torches in plan views (torch_marks)
  _applyInkClasses() {
    this.scene.traverse((o) => {
      if (!o.isMesh || o.userData.role !== 'component') return;
      let cls = 0;
      if (o.userData.lamp) cls = 0.6;
      if (this.view === 'top' && o.userData.torch) cls = 1.0;
      o.userData.ink = cls;
    });
  }

  // ------------------------------------------------------------- camera
  _fitCamera(aspect) {
    const p = this.data.params;
    // Frame what Blender frames: render_usd re-fits after deleting the ground,
    // but object bounding boxes are not refreshed by the bmesh delete, so the
    // removed platform still counts. Union of pre- and post-strip bounds.
    const post = this.data.bounds, pre = this.data.bounds_pre || post;
    const b = {
      min: post.min.map((v, i) => Math.min(v, pre.min[i])),
      max: post.max.map((v, i) => Math.max(v, pre.max[i])),
    };
    const center = new THREE.Vector3((b.min[0] + b.max[0]) / 2, (b.min[1] + b.max[1]) / 2, (b.min[2] + b.max[2]) / 2);
    const size = new THREE.Vector3(b.max[0] - b.min[0], b.max[1] - b.min[1], b.max[2] - b.min[2]).length();
    // fit to the corners of every object's box, as camera_fit_coords does over
    // render_usd's fit_coords; the union box's corners can float in empty space
    const corners = [];
    for (const [lo, hi] of this.data.fit_boxes || [[b.min, b.max]]) {
      for (const x of [lo[0], hi[0]]) for (const y of [lo[1], hi[1]]) for (const z of [lo[2], hi[2]]) {
        corners.push(new THREE.Vector3(x, y, z));
      }
    }
    const margin = p.margin ?? 1.3;
    const bboxCenter = center.clone();
    this.size = size;
    this.center = center;

    const orthoFit = (cam) => {
      // contain-fit in camera space (make_camera ortho branch), then 1.05 * margin
      cam.updateMatrixWorld();
      let minx = Infinity, maxx = -Infinity, miny = Infinity, maxy = -Infinity;
      for (const c of corners) {
        const v = c.clone().applyMatrix4(cam.matrixWorldInverse);
        minx = Math.min(minx, v.x); maxx = Math.max(maxx, v.x); miny = Math.min(miny, v.y); maxy = Math.max(maxy, v.y);
      }
      const w = maxx - minx, h = maxy - miny;
      // camera_fit_coords centers the projected extents, not the bbox center;
      // slide the camera (and its orbit target) by the offset in its own plane
      const right = new THREE.Vector3().setFromMatrixColumn(cam.matrixWorld, 0);
      const up = new THREE.Vector3().setFromMatrixColumn(cam.matrixWorld, 1);
      const shift = right.multiplyScalar((minx + maxx) / 2).add(up.multiplyScalar((miny + maxy) / 2));
      cam.position.add(shift);
      center.add(shift);
      cam.updateMatrixWorld();
      const need = aspect >= 1 ? Math.max(w, h * aspect) : Math.max(h, w / aspect);
      const o = need * 1.05 * margin;
      const hw = aspect >= 1 ? o / 2 : (o * aspect) / 2;
      const hh = aspect >= 1 ? (o / aspect) / 2 : o / 2;
      cam.left = -hw; cam.right = hw; cam.top = hh; cam.bottom = -hh;
      cam.zoom = 1;
      cam.updateProjectionMatrix();
    };

    let cam;
    if (this.view === 'top') {
      let az = p.top_azimuth;
      if (az == null) az = (b.max[2] - b.min[2]) > (b.max[0] - b.min[0]) ? 90 : 0;
      const azr = THREE.MathUtils.degToRad(az);
      cam = new THREE.OrthographicCamera(-1, 1, 1, -1, size * 0.5, size * 3.5);
      // Plan view with a Y-up camera so orbiting behaves: sit a hair off
      // vertical, offset opposite the wanted screen-up (-sin az, 0, -cos az),
      // and lookAt resolves the roll to exactly that orientation.
      const eps = size * 2e-4;
      cam.up.set(0, 1, 0);
      cam.position.set(center.x + Math.sin(azr) * eps, center.y + size * 2, center.z + Math.cos(azr) * eps);
      cam.lookAt(center);
      orthoFit(cam);
    } else {
      const az = p.azimuth ?? 135;
      const dir = viewDirection(az, ISO_ELEVATION);
      if ((p.projection || 'tele') === 'tele') {
        // 110mm on a 36mm sensor; sensor_fit AUTO spans the larger dimension
        const hfov = 2 * Math.atan(18 / 110);
        const vfov = aspect >= 1 ? 2 * Math.atan(Math.tan(hfov / 2) / aspect) : hfov;
        cam = new THREE.PerspectiveCamera(THREE.MathUtils.radToDeg(vfov), aspect, 1, size * 20);
        // camera_fit_coords: the tightest frustum around the corners, centered
        // on their projection (not on the bbox center, which projects off-center)
        let dist = size * 3;
        const tanV = Math.tan(THREE.MathUtils.degToRad(cam.fov) / 2);
        for (let it = 0; it < 24; it++) {
          cam.position.copy(center).addScaledVector(dir, -dist);
          cam.lookAt(center);
          cam.updateMatrixWorld();
          cam.updateProjectionMatrix();
          let minx = Infinity, maxx = -Infinity, miny = Infinity, maxy = -Infinity;
          for (const c of corners) {
            const v = c.clone().project(cam);
            minx = Math.min(minx, v.x); maxx = Math.max(maxx, v.x); miny = Math.min(miny, v.y); maxy = Math.max(maxy, v.y);
          }
          const right = new THREE.Vector3().setFromMatrixColumn(cam.matrixWorld, 0);
          const up = new THREE.Vector3().setFromMatrixColumn(cam.matrixWorld, 1);
          center.addScaledVector(right, (minx + maxx) / 2 * dist * tanV * aspect)
            .addScaledVector(up, (miny + maxy) / 2 * dist * tanV);
          dist *= Math.max((maxx - minx) / 2, (maxy - miny) / 2);
        }
        cam.position.copy(center).addScaledVector(dir, -dist);
        // make_camera then pushes back by size * (0.08 + 0.6 * (margin - 1))
        // along (loc - bbox center), not along the view axis; that slides the
        // build off-center in every book figure, so keep it
        const push = cam.position.clone().sub(bboxCenter).normalize();
        cam.position.addScaledVector(push, size * (0.08 + 0.6 * (margin - 1)));
        // orbit around the point on the view axis nearest the build
        const axis = new THREE.Vector3();
        cam.getWorldDirection(axis);
        center.copy(cam.position).addScaledVector(axis, bboxCenter.clone().sub(cam.position).dot(axis));
      } else {
        cam = new THREE.OrthographicCamera(-1, 1, 1, -1, size * 0.5, size * 3.5);
        cam.position.copy(center).addScaledVector(dir, -size * 2);
        cam.lookAt(center);
        orthoFit(cam);
      }
    }
    this._setDepthRange(cam, center);
    cam.updateMatrixWorld();
    return cam;
  }

  // a tight near/far keeps depth precision for the 0.15-unit wire lift and the
  // ink pass's depth-step test
  _setDepthRange(cam, target) {
    if (!cam.isPerspectiveCamera) return;
    const d = cam.position.distanceTo(target);
    cam.near = Math.max(1, d - this.size * 1.5);
    cam.far = d + this.size * 1.5;
    cam.updateProjectionMatrix();
  }

  _attachControls() {
    this.controls?.dispose();
    const c = new OrbitControls(this.camera, this.canvas);
    // the constructor already ran update() against the default target (0,0,0)
    c.target.copy(this.center);
    c.enableDamping = false;
    c.enablePan = false;
    c.zoomToCursor = false;
    c.minDistance = this.size * 0.15;
    c.maxDistance = this.size * 8;
    c.minZoom = 0.3;
    c.maxZoom = 12;
    c.update();
    c.enabled = this._interactive ?? true;
    c.enableZoom = this._zoomEnabled ?? true;
    // OrbitControls forces touch-action: none on connect; the host decides
    if (this._touchAction) this.canvas.style.touchAction = this._touchAction;
    c.addEventListener('change', () => {
      this.userMoved = true;
      this._setDepthRange(this.camera, c.target);
      this.requestRender();
      this.onChange?.();
    });
    this.controls = c;
  }

  /** Re-frame to the figure's default camera for the current canvas aspect. */
  reset() {
    const [w, h] = this._size;
    this.camera = this._fitCamera(w && h ? w / h : figureAspect(this.data, this.view).aspect);
    this._attachControls();
    this.userMoved = false;
    this.requestRender();
    this.onChange?.();
  }

  setView(view) {
    if (!this.data.params.views?.includes(view)) return;
    this.view = view;
    this._applyInkClasses();
    this.reset();
  }

  setInteractive(on) {
    this._interactive = on;
    if (this.controls) this.controls.enabled = on;
  }

  /** CSS touch-action for the canvas, kept across camera resets. */
  setTouchAction(value) {
    this._touchAction = value;
    this.canvas.style.touchAction = value;
  }

  setZoomEnabled(on) {
    this._zoomEnabled = on;
    if (this.controls) this.controls.enableZoom = on;
  }

  /** Orbit by degrees (keyboard). */
  orbit(dAzDeg, dElDeg) {
    const c = this.controls;
    const offset = this.camera.position.clone().sub(c.target);
    const s = new THREE.Spherical().setFromVector3(offset);
    s.theta += THREE.MathUtils.degToRad(dAzDeg);
    s.phi = THREE.MathUtils.clamp(s.phi - THREE.MathUtils.degToRad(dElDeg), 1e-3, Math.PI - 1e-3);
    offset.setFromSpherical(s);
    this.camera.position.copy(c.target).add(offset);
    this.camera.lookAt(c.target);
    c.update();
  }

  /** Zoom by a factor > 1 (in) or < 1 (out) (keyboard). */
  zoom(f) {
    const c = this.controls;
    if (this.camera.isOrthographicCamera) {
      this.camera.zoom = THREE.MathUtils.clamp(this.camera.zoom * f, c.minZoom, c.maxZoom);
      this.camera.updateProjectionMatrix();
    } else {
      const offset = this.camera.position.clone().sub(c.target);
      const len = THREE.MathUtils.clamp(offset.length() / f, c.minDistance, c.maxDistance);
      this.camera.position.copy(c.target).add(offset.setLength(len));
    }
    c.update();
  }

  // ------------------------------------------------------------- render
  _ensureTargets(w, h) {
    if (this.rtColor && this.rtColor.width === w && this.rtColor.height === h) return;
    this.rtColor?.dispose(); this.rtNormal?.dispose(); this.depthTex?.dispose();
    const depth = new THREE.DepthTexture(w, h);
    depth.type = THREE.UnsignedIntType;
    this.depthTex = depth;
    this.rtColor = new THREE.WebGLRenderTarget(w, h, { depthTexture: depth, depthBuffer: true });
    this.rtNormal = new THREE.WebGLRenderTarget(w, h, { depthBuffer: true });
    if (!this.edgeMat) {
      this.edgeMat = new THREE.ShaderMaterial({
        vertexShader: EDGE_VERT, fragmentShader: EDGE_FRAG,
        depthTest: false, depthWrite: false, transparent: true,
        uniforms: {
          tColor: { value: null }, tDepth: { value: null }, tNormal: { value: null },
          uTexel: { value: new THREE.Vector2() }, uRadius: { value: 1 }, uInk: { value: new THREE.Vector3() },
          uOutline: { value: true }, uInterior: { value: 1 }, uSilhouette: { value: 1 },
          uOneSided: { value: true }, uOrtho: { value: false }, uNear: { value: 0.1 }, uFar: { value: 1000 },
        },
      });
      this.edgeScene = new THREE.Scene();
      this.edgeScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.edgeMat));
      this.edgeCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    }
    this.edgeMat.uniforms.tColor.value = this.rtColor.texture;
    this.edgeMat.uniforms.tDepth.value = depth;
    this.edgeMat.uniforms.tNormal.value = this.rtNormal.texture;
    this.edgeMat.uniforms.uTexel.value.set(1 / w, 1 / h);
  }

  _renderFrame(w, h) {
    const r = this.renderer;
    const cam = this.camera;
    this._ensureTargets(w, h);
    const cfg = TECHNICAL[this.theme];
    this.structMat.uniforms.uSeams.value = this.style.seams;
    this.structMat.uniforms.uBandsOn.value = this.style.bands;
    this.structMat.uniforms.uSeamPx.value = 1.2 * this.style.linePx;

    // Blender thins its linework on big builds; here the same idea keyed to how
    // many pixels one block covers. Interior lines fade hardest (they are the
    // grid that turns a zoomed-out build dark); the silhouette fades less.
    // Exports are figure PNGs meant to match the Blender set: full ink.
    const viewH = cam.isOrthographicCamera ? (cam.top - cam.bottom) / cam.zoom
      : 2 * cam.position.distanceTo(this.controls.target) * Math.tan(THREE.MathUtils.degToRad(cam.fov) / 2);
    const blockPx = h * BLOCK / Math.max(viewH, 1e-3);
    const interior = this.exporting ? 1 : THREE.MathUtils.clamp((blockPx - 8) / 30, 0.15, 0.8);
    const silhouette = this.exporting ? 1 : THREE.MathUtils.clamp((blockPx - 4) / 22, 0.45, 0.95);
    this.structMat.uniforms.uInterior.value = interior;

    // pass 1: styled color + depth
    r.setRenderTarget(this.rtColor);
    r.clear();
    r.render(this.scene, cam);
    // pass 2: normals + ink eligibility
    const saved = [];
    this.scene.traverse((o) => {
      if (o.isMesh) { saved.push([o, o.material]); o.material = this.inkMaterials[o.userData.ink || 0]; }
    });
    r.setRenderTarget(this.rtNormal);
    r.clear();
    r.render(this.scene, cam);
    for (const [o, m] of saved) o.material = m;
    // pass 3: composite + ink
    const u = this.edgeMat.uniforms;
    u.uInk.value.set(...lin3(cfg.line));
    u.uOutline.value = this.style.outline;
    u.uOrtho.value = cam.isOrthographicCamera;
    u.uNear.value = cam.near;
    u.uFar.value = cam.far;
    u.uRadius.value = this.style.linePx;
    u.uInterior.value = interior;
    u.uSilhouette.value = silhouette;
    u.uOneSided.value = !this.exporting;
    r.setRenderTarget(null);
    r.clear();
    r.render(this.edgeScene, this.edgeCam);
  }

  /** Size the drawing buffer (device pixels) and draw. */
  resize(w, h) {
    w = Math.max(2, Math.round(w)); h = Math.max(2, Math.round(h));
    const changed = w !== this._size[0] || h !== this._size[1];
    this._size = [w, h];
    this.renderer.setSize(w, h, false);
    if (!this.camera) {
      this.camera = this._fitCamera(w / h);
      this._attachControls();
    } else if (changed) {
      if (!this.userMoved) {
        this.camera = this._fitCamera(w / h);
        this._attachControls();
      } else if (this.camera.isPerspectiveCamera) {
        this.camera.aspect = w / h;
        this.camera.updateProjectionMatrix();
      }
    }
    this.draw();
  }

  draw() {
    if (this._disposed || !this.camera) return;
    const [w, h] = this._size;
    this._renderFrame(w, h);
    if (this.overlay) {
      if (this.style.legend && this.data.params.legend && Object.keys(this.data.params.legend).length) {
        drawLegendOverlay(this.overlay, this.canvas, this.data.params.legend, this.theme);
      } else {
        this.overlay.getContext('2d').clearRect(0, 0, this.overlay.width, this.overlay.height);
      }
    }
  }

  requestRender() {
    if (this._pending || this._disposed) return;
    this._pending = true;
    requestAnimationFrame(() => { this._pending = false; this.draw(); });
  }

  /**
   * Render the shot at its figure resolution (2x supersampled, downsampled),
   * with the legend stamped like shots.py does. Returns a PNG data URL.
   */
  async exportPNG(ss = 2) {
    await this.ready;
    await this._fontsReady;
    const { w, h, aspect } = figureAspect(this.data, this.view);
    const saved = { size: this._size, camera: this.camera, controls: this.controls, moved: this.userMoved };
    const W = Math.round(w * ss), H = Math.round(h * ss);
    this.renderer.setSize(W, H, false);
    this.camera = this._fitCamera(aspect);
    this.controls = { target: this.center };
    this.exporting = true;
    this._renderFrame(W, H);
    this.exporting = false;
    let c = document.createElement('canvas');
    c.width = w; c.height = h;
    const ctx = c.getContext('2d', { willReadFrequently: true });
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(this.canvas, 0, 0, w, h);
    if (this.style.legend && this.data.params.legend && Object.keys(this.data.params.legend).length) {
      c = stampLegend(c, this.data.params.legend, this.theme);
    }
    // restore the live view
    this.camera = saved.camera;
    this.controls = saved.controls;
    this.userMoved = saved.moved;
    this._size = saved.size;
    this.renderer.setSize(saved.size[0], saved.size[1], false);
    this.draw();
    return c.toDataURL('image/png');
  }

  /** Current frame as a data URL (used to leave a still behind on dispose). */
  snapshot() {
    return this.canvas.toDataURL('image/png');
  }

  dispose() {
    if (this._disposed) return;
    this._disposed = true;
    this.controls?.dispose();
    this.scene.traverse((o) => {
      if (o.isMesh) {
        o.geometry.dispose();
        if (o.material !== this.structMat) { o.material.map?.dispose(); o.material.dispose(); }
      }
    });
    this.structMat?.dispose();
    for (const m of Object.values(this.inkMaterials || {})) m.dispose();
    this.edgeMat?.dispose();
    this.rtColor?.dispose(); this.rtNormal?.dispose(); this.depthTex?.dispose();
    for (const t of this._textures.values()) t.dispose();
    this.renderer.dispose();
    this.renderer.forceContextLoss();
  }
}
