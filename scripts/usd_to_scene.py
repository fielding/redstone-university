#!/usr/bin/env python3
"""
usd_to_scene.py — MiEx USD export -> viewer scene JSON (no Blender needed).

SPIKE for a standalone three.js renderer of the course's Minecraft builds.
Reads the ASCII USD that MiEx writes (renders/usd/<shot>.usd + _chunks/),
applies the geometry-level steps render_usd.py does before rendering
(stray-bedrock trim, hide, ground remove, vector wire rebuild from dust) and
writes a compact JSON the viewer (viewer/) styles and renders in WebGL.

Style (palette, height bands, tints, seams, ink) stays in the viewer so it can
be changed live; only geometry + semantics are baked here.

    python3 scripts/usd_to_scene.py 05_full-adder 00_basic-circuit
    python3 scripts/usd_to_scene.py --all
    python3 scripts/usd_to_scene.py --all --publish   # also refresh the site's figures
    python3 scripts/usd_to_scene.py --usd renders/usd/foo.usd --out viewer/builds

Not ported yet (spike): --clip / --max-layer / --explode, texture swaps,
legend stamping, torch/lamp stroke weights (viewer side), AO.
"""
import glob
import json
import math
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS_FILE = os.path.join(REPO, "renders", "shots.json")
USD_CACHE = os.path.join(REPO, "renders", "usd")
DEFAULT_OUT = os.path.join(REPO, "viewer", "builds")
TEXTURES_SRC = os.path.join(REPO, "viewer", "textures")
SITE_PUBLIC = os.path.join(REPO, "web", "public", "figures", "3d")
SITE_MAP = os.path.join(REPO, "web", "src", "data", "live-figures.json")
# figures whose live build disagrees with the book PNG (scripts/live3d_qa.py);
# they stay static images until the PNG or the build is brought back in line
HOLD_FILE = os.path.join(REPO, "renders", "live3d-hold.json")

BLOCK = 16.0
# same keyword tables as render_usd.py
COMPONENT_KW = ("torch", "lever", "repeater", "comparator", "lamp", "button",
                "redstone_block", "observer", "target", "tripwire", "piston",
                "dispenser", "dropper", "note_block", "rail")
CIRCUIT_KW = ("ru_wires", "redstone_dust") + COMPONENT_KW

# ----------------------------------------------------------------- USD parsing

_MESH_RE = re.compile(r'def Mesh "([^"]+)"\s*(?:\([^)]*\))?\s*\{(.*?)\n    \}', re.S)
_ARR_RE_CACHE = {}


def _arr(body, name):
    """Return the raw '[...]' text of `<type>[] name = [...]` or None."""
    rx = _ARR_RE_CACHE.get(name)
    if rx is None:
        rx = re.compile(r'\b' + re.escape(name) + r'\s*=\s*\[(.*?)\]', re.S)
        _ARR_RE_CACHE[name] = rx
    m = rx.search(body)
    return m.group(1) if m else None


def _floats(txt):
    return [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?', txt)]


def _ints(txt):
    return [int(x) for x in re.findall(r'-?\d+', txt)] if txt else []


def parse_chunk(path):
    """Yield dicts per Mesh prim: name, points (list of 3-tuples), faces (list of
    index lists), and per-loop st / normals / Cd (or None), displayColor."""
    with open(path, "r") as f:
        txt = f.read()
    for m in _MESH_RE.finditer(txt):
        name, body = m.group(1), m.group(2)
        pts_raw = _arr(body, "points")
        if pts_raw is None:
            continue
        fl = _floats(pts_raw)
        points = [(fl[i], fl[i + 1], fl[i + 2]) for i in range(0, len(fl), 3)]
        fvi = _ints(_arr(body, "faceVertexIndices"))
        fvc = _ints(_arr(body, "faceVertexCounts"))
        faces, k = [], 0
        for c in fvc:
            faces.append(fvi[k:k + c])
            k += c
        nloops = len(fvi)

        def primvar(pname, width):
            raw = _arr(body, "primvars:" + pname)
            if raw is None:
                return None
            vals = _floats(raw)
            tuples = [tuple(vals[i:i + width]) for i in range(0, len(vals), width)]
            idx = _ints(_arr(body, f"primvars:{pname}:indices"))
            if idx:
                return [tuples[i] for i in idx]
            if len(tuples) == nloops:
                return tuples
            if len(tuples) == len(points):        # vertex interpolation
                return [tuples[i] for i in fvi]
            if len(tuples) == 1:                  # constant
                return tuples * nloops
            return None

        dc = _arr(body, "primvars:displayColor")
        yield {
            "name": name,
            "points": points,
            "faces": faces,
            "st": primvar("st", 2),
            "normals": primvar("normals", 3),
            "cd": primvar("Cd", 3),
            "displayColor": tuple(_floats(dc)[:3]) if dc else None,
        }


def parse_materials(path):
    """material name -> texture basename (from the UsdUVTexture file asset)."""
    out = {}
    if not os.path.exists(path):
        return out
    txt = open(path).read()
    for m in re.finditer(r'def Material "([^"]+)"(.*?)\n    \}', txt, re.S):
        name, body = m.group(1), m.group(2)
        f = re.search(r'inputs:file = @([^@]+)@', body)
        if f:
            out[name] = os.path.basename(f.group(1))
    return out


def load_usd(usd_path):
    stem = os.path.splitext(os.path.basename(usd_path))[0]
    chunks_dir = os.path.join(os.path.dirname(usd_path), stem + "_chunks")
    files = sorted(p for p in glob.glob(os.path.join(chunks_dir, "region_*_chunk_*.usd"))
                   if not p.endswith("_render.usd"))
    if not files:
        sys.exit(f"no chunk files under {chunks_dir}")
    meshes = []
    for p in files:
        for mesh in parse_chunk(p):
            meshes.append(mesh)
    tex = parse_materials(os.path.join(os.path.dirname(usd_path), stem + "_materials.usd"))
    return meshes, tex


def parse_region(usd_path):
    """MiEx export metadata from the root layer: region bounds + offsets.
    Block (X, Y, Z) maps to USD units as x = 16*(X-offX) (cell spans +-8),
    y = 16*(Y-offY) (cell spans [y, y+16]), z = 16*(Z-offZ) (cell spans +-8)."""
    txt = open(usd_path).read(20000)
    out = {}
    for key in ("minX", "minY", "minZ", "maxX", "maxY", "maxZ", "offsetX", "offsetY", "offsetZ"):
        m = re.search(r"region_region_1_" + key + r" = (-?\d+)", txt)
        if m:
            out[key] = int(m.group(1))
    return out


def clip_to_bounds(meshes, bounds, region):
    """Drop faces outside the shot's block bounds (inclusive). Guards against a
    cached USD exported with wider bounds than shots.json currently says."""
    if not region or len(bounds) != 6:
        return meshes
    # a cache exported at a different location (build moved, shot re-bounded)
    # has nothing in common with the shot: clipping would delete everything.
    # Leave it alone and shout; the export must be refreshed.
    for lo, hi in ((0, 3), (2, 5)):
        if bounds[hi] < region[("minX", "minZ")[lo // 2]] or bounds[lo] > region[("maxX", "maxZ")[lo // 2]]:
            print(f"  WARNING: cached USD region does not overlap shots.json bounds at all "
                  f"(USD {[region.get(k) for k in ('minX','minY','minZ','maxX','maxY','maxZ')]} vs shot {bounds}); "
                  f"rendering the cache unclipped. RE-EXPORT this shot.")
            return meshes
    ox, oy, oz = region["offsetX"], region["offsetY"], region["offsetZ"]
    x0, x1 = 16 * (bounds[0] - ox) - 8, 16 * (bounds[3] - ox) + 8
    y0, y1 = 16 * (bounds[1] - oy), 16 * (bounds[4] - oy) + 16
    z0, z1 = 16 * (bounds[2] - oz) - 8, 16 * (bounds[5] - oz) + 8
    eps = 0.5
    out, removed = [], 0
    for m in meshes:
        keep = []
        for i, f in enumerate(m["faces"]):
            c = face_center(m, f)
            if (x0 - eps <= c[0] <= x1 + eps and y0 - eps <= c[1] <= y1 + eps
                    and z0 - eps <= c[2] <= z1 + eps):
                keep.append(i)
        removed += len(m["faces"]) - len(keep)
        if keep:
            out.append(m if len(keep) == len(m["faces"]) else _subset_faces(m, keep))
    if removed:
        print(f"  clipped {removed} face(s) outside shots.json bounds "
              f"(USD region y {region['minY']}..{region['maxY']} vs shot {bounds[1]}..{bounds[4]})")
    return out


# ----------------------------------------------------------- geometry helpers

def block_id(name):
    b = re.sub(r"\.\d+$", "", name.lower())
    return b[len("minecraft_block_"):] if b.startswith("minecraft_block_") else b


def is_circuit(name):
    n = name.lower()
    return any(k in n for k in CIRCUIT_KW)


def role_of(name):
    n = name.lower()
    if n.startswith("ru_groundpads"):
        return "pad"
    if "redstone_dust" in n:
        return "dust"
    if any(k in n for k in COMPONENT_KW):
        return "component"
    return "structure"


def mesh_bounds(mesh):
    ys = [p[1] for p in mesh["points"]]
    return min(ys), max(ys)


def face_center(mesh, face):
    pts = [mesh["points"][i] for i in face]
    n = len(pts)
    return tuple(sum(p[a] for p in pts) / n for a in range(3))


def face_normal(mesh, fi, face):
    if mesh["normals"] is not None:
        # loop index of this face's first vertex
        li = sum(len(f) for f in mesh["faces"][:fi])
        return mesh["normals"][li]
    a, b, c = (mesh["points"][i] for i in face[:3])
    u = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    v = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    l = math.sqrt(sum(x * x for x in n)) or 1.0
    return (n[0] / l, n[1] / l, n[2] / l)


def trim_strays(meshes, gap=64.0):
    """render_usd.scene_bounds: cluster meshes by overlapping Y-intervals; keep the
    cluster with the most meshes (ties: topmost). Drops the world floor / bedrock
    that MiEx drags along when the export Y-range is wide."""
    if len(meshes) < 2:
        return meshes
    items = sorted(((mesh_bounds(m), m) for m in meshes), key=lambda t: t[0][0])
    clusters, top = [[items[0]]], items[0][0][1]
    for (y0, y1), m in items[1:]:
        if y0 <= top + gap:
            clusters[-1].append(((y0, y1), m))
            top = max(top, y1)
        else:
            clusters.append([((y0, y1), m)])
            top = y1
    best = max(clusters, key=lambda c: (len(c), max(b[1] for b, _ in c)))
    if len(clusters) > 1:
        dropped = [m["name"] for c in clusters if c is not best for _, m in c]
        print(f"  trimmed {len(dropped)} stray mesh(es): {', '.join(sorted(set(dropped))[:6])}")
    return [m for _, m in best]


def apply_hide(meshes, hide):
    subs = [h for h in hide if not h.startswith("=")]
    exact = {h[1:] for h in hide if h.startswith("=")}
    FACE = ("_top", "_bottom", "_side", "_front", "_back", "_end", "_inner", "_outer")

    def core(bid):
        for s in FACE:
            if bid.endswith(s):
                return bid[:-len(s)]
        return bid
    kept, n = [], 0
    for m in meshes:
        nm = m["name"].lower()
        bid = block_id(nm)
        if any(h in nm for h in subs) or bid in exact or core(bid) in exact:
            n += 1
            continue
        kept.append(m)
    if n:
        print(f"  hid {n} mesh(es)")
    return kept


def covered_cells(xs, zs):
    """Every block cell an AABB overlaps (centers at multiples of 16, cell b
    spans [16b-8, 16b+8]); eps keeps shared edges out."""
    eps = 0.01
    for bx in range(math.floor((min(xs) + eps + BLOCK / 2) / BLOCK),
                    math.floor((max(xs) - eps + BLOCK / 2) / BLOCK) + 1):
        for bz in range(math.floor((min(zs) + eps + BLOCK / 2) / BLOCK),
                        math.floor((max(zs) - eps + BLOCK / 2) / BLOCK) + 1):
            yield (bx, bz)


def _cube_mesh(name, cells, rest):
    """One clean 16-unit cube per cell, top at `rest` (synthesized ground pad)."""
    pts, faces, normals = [], [], []
    for (bx, bz) in cells:
        cx, cz = bx * BLOCK, bz * BLOCK
        y0, y1 = rest - BLOCK, rest
        b = len(pts)
        pts.extend([(cx - 8, y0, cz - 8), (cx + 8, y0, cz - 8), (cx + 8, y0, cz + 8), (cx - 8, y0, cz + 8),
                    (cx - 8, y1, cz - 8), (cx + 8, y1, cz - 8), (cx + 8, y1, cz + 8), (cx - 8, y1, cz + 8)])
        quads = [([4, 5, 6, 7], (0, 1, 0)), ([0, 3, 2, 1], (0, -1, 0)),
                 ([0, 1, 5, 4], (0, 0, -1)), ([2, 3, 7, 6], (0, 0, 1)),
                 ([3, 0, 4, 7], (-1, 0, 0)), ([1, 2, 6, 5], (1, 0, 0))]
        for q, n in quads:
            faces.append([b + i for i in q])
            normals.extend([n] * 4)
    return {"name": name, "points": pts, "faces": faces, "st": None,
            "normals": normals, "cd": None, "displayColor": None}


def strip_ground(meshes, mode, base_y):
    """Port of render_usd.strip_ground in USD (Y-up) coordinates.
      remove / remove2: delete every non-circuit face in the lowest layer(s).
      crop: delete the true ground and synthesize a clean base cube under every
            cell the build occupies, each pad named after the block family that
            stands on it (so legend tints color a region's base too). Levers
            never seed pads; cells with an exported bottom face (air below)
            stay floating; familyless cells adopt the neighbors' family or get
            no pad at all."""
    if mode not in ("remove", "remove2", "crop"):
        return meshes
    layers = 2 if mode == "remove2" else 1
    band_top = base_y + layers * BLOCK + 1.0
    rest = None
    footprint, region_src, lowest_y, open_below = set(), {}, {}, {}
    if mode == "crop":
        circ_y = sorted(m["points"][v][1] for m in meshes if is_circuit(m["name"])
                        for f in m["faces"] for v in f)
        if circ_y:
            med = circ_y[len(circ_y) // 2]
            rest = math.floor((med - base_y) / BLOCK + 0.03) * BLOCK + base_y
        else:
            rest = base_y + BLOCK
        rest = max(base_y, min(rest, base_y + BLOCK))
        band_top = rest + 1.0
        for m in meshes:
            nm = m["name"].lower()
            circuit = is_circuit(nm)
            if circuit and "lever" in nm:
                continue
            for fi, face in enumerate(m["faces"]):
                pts = [m["points"][i] for i in face]
                c = face_center(m, face)
                n = face_normal(m, fi, face)
                cells = list(covered_cells([p[0] for p in pts], [p[2] for p in pts]))
                if n[1] < -0.5 and c[1] > base_y + 0.5:
                    for cell in cells:
                        if cell not in open_below or c[1] < open_below[cell]:
                            open_below[cell] = c[1]
                if circuit:
                    if not (-2.0 <= c[1] - rest <= 4.0):
                        continue
                elif c[1] <= band_top:
                    continue
                footprint.update(cells)
                for cell in cells:
                    if cell not in lowest_y or c[1] < lowest_y[cell]:
                        lowest_y[cell] = c[1]
                    if not circuit and (cell not in region_src or c[1] < region_src[cell][0]):
                        region_src[cell] = (c[1], nm)

    removed = 0
    cell_src = {}
    out = []
    for m in meshes:
        if is_circuit(m["name"]):
            out.append(m)
            continue
        nm = m["name"].lower()
        keep_idx = []
        for i, f in enumerate(m["faces"]):
            c = face_center(m, f)
            if c[1] <= band_top:
                removed += 1
                if mode == "crop":
                    pts = [m["points"][v] for v in f]
                    for cell in covered_cells([p[0] for p in pts], [p[2] for p in pts]):
                        if cell not in cell_src or c[1] > cell_src[cell][0]:
                            cell_src[cell] = (c[1], nm)
            else:
                keep_idx.append(i)
        if keep_idx:
            out.append(m if len(keep_idx) == len(m["faces"]) else _subset_faces(m, keep_idx))

    if mode == "crop" and footprint:
        floating = {cell for cell in footprint
                    if open_below.get(cell, 1e9) <= lowest_y.get(cell, -1e9) + 0.6}
        if floating:
            print(f"  crop: {len(floating)} floating cell(s) get no pad")
        fam_by_cell = {cell: region_src.get(cell, cell_src.get(cell, (0, "")))[1]
                       for cell in footprint if cell not in floating}
        for cell, fam in list(fam_by_cell.items()):
            if fam:
                continue
            nb = [fam_by_cell.get((cell[0] + dx, cell[1] + dz))
                  for dx in (-1, 0, 1) for dz in (-1, 0, 1) if (dx, dz) != (0, 0)]
            nb = [f for f in nb if f]
            if nb:
                best = max(set(nb), key=nb.count)
                if nb.count(best) >= 2 or len(set(nb)) == 1:
                    fam_by_cell[cell] = best
        dropped = sum(1 for f in fam_by_cell.values() if not f)
        if dropped:
            print(f"  crop: {dropped} familyless cell(s) get no pad")
        groups = {}
        for cell, fam in fam_by_cell.items():
            if fam:
                groups.setdefault(fam, []).append(cell)
        for fam, cells in groups.items():
            out.append(_cube_mesh(f"RU_GroundPads|{fam}", sorted(cells), rest))
        print(f"  ground crop: {sum(len(c) for c in groups.values())} pads in "
              f"{len(groups)} family groups (resting plane y={rest:.0f})")
    print(f"  ground {mode}: removed {removed} faces (base y={base_y:.1f})")
    return out


FULL_COMPONENTS = ("redstone_lamp", "redstone_block", "target", "observer", "piston",
                   "dispenser", "dropper", "note_block")


def _full_face_cell(m, face, n):
    """If this face is one side of a full 16x16x16 block on the grid, return
    (cell, axis, sign): the cell the face belongs to (inward of its normal)."""
    pts = [m["points"][v] for v in face]
    if len(pts) != 4:
        return None
    axis = max(range(3), key=lambda a: abs(n[a]))
    if abs(n[axis]) < 0.99:
        return None
    lo = [min(p[a] for p in pts) for a in range(3)]
    hi = [max(p[a] for p in pts) for a in range(3)]
    for a in range(3):
        if a != axis and abs(hi[a] - lo[a] - BLOCK) > 0.02:
            return None
    plane = pts[0][axis]
    # grid: x/z block boundaries at 16b+8, y boundaries at 16k
    phase = 0.0 if axis == 1 else 8.0
    if abs((plane + phase) / BLOCK - round((plane + phase) / BLOCK)) > 0.002:
        return None
    sign = 1 if n[axis] > 0 else -1
    c = [(lo[a] + hi[a]) / 2 for a in range(3)]
    c[axis] -= sign * BLOCK / 2               # step inward to the block's center
    cell = (math.floor((c[0] + 8) / BLOCK), math.floor(c[1] / BLOCK), math.floor((c[2] + 8) / BLOCK))
    return cell, axis, sign


def add_missing_bottoms(meshes):
    """Close the underside of the build. MiEx culls every face that touched a
    solid block, so a block that rested on ground (removed for the figure) has
    no bottom face, and the build is open when seen from below. Add a bottom
    to every full block that has none and has no full block beneath it."""
    full = {}       # cell -> mesh index (first owner)
    has_bottom = set()
    for mi, m in enumerate(meshes):
        nm = m["name"].lower()
        if is_circuit(nm) and not any(k in nm for k in FULL_COMPONENTS):
            continue
        for fi, face in enumerate(m["faces"]):
            r = _full_face_cell(m, face, face_normal(m, fi, face))
            if not r:
                continue
            cell, axis, sign = r
            full.setdefault(cell, mi)
            if axis == 1 and sign < 0:
                has_bottom.add(cell)
    added = 0
    for cell, mi in sorted(full.items()):
        below = (cell[0], cell[1] - 1, cell[2])
        if cell in has_bottom or below in full:
            continue
        m = meshes[mi]
        x, y, z = cell[0] * BLOCK, cell[1] * BLOCK, cell[2] * BLOCK
        base = len(m["points"])
        m["points"] = m["points"] + [(x - 8, y, z - 8), (x + 8, y, z - 8), (x + 8, y, z + 8), (x - 8, y, z + 8)]
        m["faces"] = m["faces"] + [[base, base + 1, base + 2, base + 3]]
        if m["normals"] is not None:
            m["normals"] = m["normals"] + [(0.0, -1.0, 0.0)] * 4
        if m["st"] is not None:
            m["st"] = m["st"] + [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        if m["cd"] is not None:
            m["cd"] = m["cd"] + [m["cd"][-1]] * 4
        added += 1
    if added:
        print(f"  closed {added} open block bottom(s)")
    return meshes


def _subset_faces(m, keep_idx):
    """Copy of mesh m with only the faces at keep_idx (per-loop primvars follow)."""
    loop_start, k = [], 0
    for f in m["faces"]:
        loop_start.append(k)
        k += len(f)
    new = dict(m)
    new["faces"] = [m["faces"][i] for i in keep_idx]
    for key in ("st", "normals", "cd"):
        if m[key] is not None:
            vals = []
            for i in keep_idx:
                s = loop_start[i]
                vals.extend(m[key][s:s + len(m["faces"][i])])
            new[key] = vals
    return new


# -------------------------------------------------------------- vector wires

def wire_color(power):
    """render_usd.wire_color (scene-linear RGB)."""
    if power < 0.10:
        return (0.12, 0.012, 0.012)
    t = min(1.0, max(0.0, (power - 0.05) / 0.90)) ** 0.42
    return (0.25 + 0.75 * t, 0.012 + 0.05 * t, 0.012 + 0.03 * t)


def build_vector_wires(dust_meshes):
    """Port of render_usd.build_vector_wires, in USD (Y-up) coordinates.
    Dust block positions + power come from the horizontal dust quads; the wire
    network is recomputed from block adjacency and emitted as flat ribbons."""
    W = 4.6
    LIFT = 0.15
    blocks = {}
    for m in dust_meshes:
        if "overlay" in m["name"].lower():
            continue
        li = 0
        for fi, face in enumerate(m["faces"]):
            n = face_normal(m, fi, face)
            corners = [(m["points"][v], (m["cd"][li + j][0] if m["cd"] else 0.0))
                       for j, v in enumerate(face)]
            li += len(face)
            if abs(n[1]) < 0.7:
                continue
            y = sum(c[0][1] for c in corners) / len(corners)
            by = int(round(y) // BLOCK)
            eps, half = 0.01, BLOCK / 2
            min_x = min(c[0][0] for c in corners) + eps
            max_x = max(c[0][0] for c in corners) - eps
            min_z = min(c[0][2] for c in corners) + eps
            max_z = max(c[0][2] for c in corners) - eps
            for bx in range(math.floor((min_x + half) / BLOCK), math.floor((max_x + half) / BLOCK) + 1):
                for bz in range(math.floor((min_z + half) / BLOCK), math.floor((max_z + half) / BLOCK) + 1):
                    cx, cz = bx * BLOCK, bz * BLOCK
                    nearest = min(corners, key=lambda c: (c[0][0] - cx) ** 2 + (c[0][2] - cz) ** 2)
                    key = (bx, by, bz)
                    cur = blocks.get(key)
                    if cur is None or nearest[1] > cur[0]:
                        blocks[key] = (nearest[1], y)
    if not blocks:
        return None

    edges = set()
    for (bx, by, bz) in blocks:
        for dx, dz in ((1, 0), (0, 1)):
            n = (bx + dx, by, bz + dz)
            if n in blocks:
                edges.add(((bx, by, bz), n))
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (bx + dx, by + 1, bz + dz)
            if n in blocks:
                edges.add(((bx, by, bz), n))

    def center(key):
        power, y = blocks[key]
        return (key[0] * BLOCK, y + LIFT, key[2] * BLOCK)

    verts, cols, tris = [], [], []

    def add_quad(c4, k4):
        b = len(verts)
        verts.extend(c4)
        cols.extend(k4)
        tris.extend([b, b + 1, b + 2, b, b + 2, b + 3])

    def v3(a, b, s=1.0):
        return (a[0] + b[0] * s, a[1] + b[1] * s, a[2] + b[2] * s)

    def side_of(d):
        # horizontal direction d -> perpendicular in the ground plane, length W/2
        return (-d[2] * W / 2, 0.0, d[0] * W / 2)

    for a, b in edges:
        pa, pb = center(a), center(b)
        ca, cb = wire_color(blocks[a][0]), wire_color(blocks[b][0])
        if a[1] == b[1]:
            d = (pb[0] - pa[0], 0.0, pb[2] - pa[2])
            l = math.hypot(d[0], d[2]) or 1.0
            d = (d[0] / l, 0.0, d[2] / l)
            s = side_of(d)
            add_quad([v3(pa, s, -1), v3(pa, s), v3(pb, s), v3(pb, s, -1)], [ca, ca, cb, cb])
            continue
        lo, hi = (a, b) if a[1] < b[1] else (b, a)
        cl, ch = (ca, cb) if a[1] < b[1] else (cb, ca)
        plo, phi = center(lo), center(hi)
        d = (phi[0] - plo[0], 0.0, phi[2] - plo[2])
        l = math.hypot(d[0], d[2]) or 1.0
        d = (d[0] / l, 0.0, d[2] / l)
        s = side_of(d)
        face = (plo[0] + d[0] * (BLOCK / 2 - LIFT), 0.0, plo[2] + d[2] * (BLOCK / 2 - LIFT))
        e_lo = (face[0], plo[1], face[2])
        e_hi = (face[0], phi[1], face[2])
        cm = tuple((cl[i] + ch[i]) / 2 for i in range(3))
        add_quad([v3(plo, s, -1), v3(plo, s), v3(e_lo, s), v3(e_lo, s, -1)], [cl, cl, cm, cm])
        add_quad([v3(e_lo, s, -1), v3(e_lo, s), v3(e_hi, s), v3(e_hi, s, -1)], [cm] * 4)
        add_quad([v3(e_hi, s, -1), v3(e_hi, s), v3(phi, s), v3(phi, s, -1)], [cm, cm, ch, ch])

    neighbors = {}
    for a, b in edges:
        neighbors.setdefault(a, []).append(b)
        neighbors.setdefault(b, []).append(a)
    for key in blocks:
        ns = neighbors.get(key, [])
        collinear = (len(ns) == 2 and
                     (ns[0][0] - ns[1][0], ns[0][2] - ns[1][2]) in ((2, 0), (-2, 0), (0, 2), (0, -2)))
        if len(ns) == 2 and collinear:
            continue
        p = center(key)
        p = (p[0], p[1] + 0.02, p[2])
        h = W / 2
        col = wire_color(blocks[key][0])
        add_quad([(p[0] - h, p[1], p[2] - h), (p[0] + h, p[1], p[2] - h),
                  (p[0] + h, p[1], p[2] + h), (p[0] - h, p[1], p[2] + h)], [col] * 4)
    print(f"  vector wires: {len(blocks)} dust blocks, {len(edges)} connections")
    return {"positions": [round(c, 3) for v in verts for c in v],
            "colors": [round(c, 4) for k in cols for c in k],
            "indices": tris}


# ------------------------------------------------------------------ emit JSON

def flatten_mesh(m, tex_by_mat):
    """Expand to non-indexed triangles with per-vertex normal/uv/color."""
    pos, nrm, uv, col, idx = [], [], [], [], []
    li = 0
    for fi, face in enumerate(m["faces"]):
        n = face_normal(m, fi, face)
        base = len(pos) // 3
        for j, v in enumerate(face):
            p = m["points"][v]
            pos.extend((round(p[0], 3), round(p[1], 3), round(p[2], 3)))
            nrm.extend((round(n[0], 3), round(n[1], 3), round(n[2], 3)))
            if m["st"] is not None:
                s = m["st"][li + j]
                uv.extend((round(s[0], 5), round(s[1], 5)))
            if m["cd"] is not None:
                c = m["cd"][li + j]
                col.extend((round(c[0], 4), round(c[1], 4), round(c[2], 4)))
        li += len(face)
        for k in range(1, len(face) - 1):
            idx.extend((base, base + k, base + k + 1))
    mat = "MAT_" + re.sub(r"\.\d+$", "", m["name"])
    return {
        "name": m["name"],
        "block": block_id(m["name"]),
        "role": role_of(m["name"]),
        "texture": tex_by_mat.get(mat),
        "displayColor": m["displayColor"],
        "positions": pos,
        "normals": nrm,
        "uvs": uv if uv else None,
        "colors": col if col else None,
        "indices": idx,
    }


def bounds_of(meshes, wires=None):
    lo = [1e18] * 3
    hi = [-1e18] * 3
    for m in meshes:
        for p in m["points"]:
            for a in range(3):
                lo[a] = min(lo[a], p[a]); hi[a] = max(hi[a], p[a])
    if wires:
        ps = wires["positions"]
        for i in range(0, len(ps), 3):
            for a in range(3):
                lo[a] = min(lo[a], ps[i + a]); hi[a] = max(hi[a], ps[i + a])
    return {"min": lo, "max": hi}


def _used_points_only(m):
    """Bounds must measure kept faces, not orphaned points left by face deletion."""
    used = sorted({v for f in m["faces"] for v in f})
    return {"points": [m["points"][i] for i in used]}


def scene_has_geometry(solid, wires):
    return any(m["faces"] for m in solid) or bool(wires and wires["indices"])


def convert(name, shot, usd_path, out_dir):
    print(f"[{name}] {os.path.relpath(usd_path, REPO)}")
    meshes, tex = load_usd(usd_path)
    print(f"  {len(meshes)} mesh prims")
    region = parse_region(usd_path)
    if region and shot.get("bounds"):
        b6 = shot["bounds"]
        if [region.get(k) for k in ("minX", "minY", "minZ", "maxX", "maxY", "maxZ")] != list(b6):
            print(f"  NOTE: cached USD region {[region.get(k) for k in ('minX','minY','minZ','maxX','maxY','maxZ')]}"
                  f" != shots.json bounds {b6}; clipping to shots.json (re-export to refresh)")
        meshes = clip_to_bounds(meshes, b6, region)
    hide = [h.strip() for h in str(shot.get("hide", "")).split(",") if h.strip()]
    meshes = apply_hide(meshes, hide)
    meshes = trim_strays(meshes, float(shot.get("cluster_gap", 64.0)))

    dust = [m for m in meshes if role_of(m["name"]) == "dust"]
    solid = [m for m in meshes if role_of(m["name"]) != "dust"]
    wires = build_vector_wires(dust) if dust else None

    b_pre = bounds_of([_used_points_only(m) for m in solid], wires)
    # Blender fits its camera to the bounding-box corners of every visible
    # object, one object per block family, and those boxes are not refreshed
    # by the ground delete. Record them as Blender sees them: pre-strip boxes
    # for the imported meshes, plus the wire object and (below) the pads.
    def box(points):
        return [[min(p[a] for p in points) for a in range(3)], [max(p[a] for p in points) for a in range(3)]]
    fit_boxes = [box(_used_points_only(m)["points"]) for m in solid if m["faces"]]
    if wires:
        ps = wires["positions"]
        fit_boxes.append(box([(ps[i], ps[i + 1], ps[i + 2]) for i in range(0, len(ps), 3)]))
    # the generated wire ribbons take part in ground stripping like Blender's
    # RU_Wires object does (crop footprint / resting plane), never deleted
    wire_mesh = None
    if wires:
        ps = wires["positions"]
        faces = [list(wires["indices"][i:i + 3]) for i in range(0, len(wires["indices"]), 3)]
        # Ribbons are decals lying on blocks. Their winding faces -Y in this
        # Y-up space (Blender's Z-up, other-handed space sees +Z), and a
        # downward face would read as "air below" to the crop pass and strip
        # the pad from every wired cell. Declare them up-facing.
        wire_mesh = {"name": "RU_Wires", "st": None, "normals": [(0.0, 1.0, 0.0)] * (3 * len(faces)),
                     "cd": None, "displayColor": None,
                     "points": [(ps[i], ps[i + 1], ps[i + 2]) for i in range(0, len(ps), 3)],
                     "faces": faces}
        solid = solid + [wire_mesh]
    solid = strip_ground(solid, shot.get("ground", "keep"), b_pre["min"][1])
    solid = [m for m in solid if m["name"] != "RU_Wires"]
    solid = add_missing_bottoms(solid)
    fit_boxes += [box(m["points"]) for m in solid if m["name"].startswith("RU_GroundPads")]
    b = bounds_of([_used_points_only(m) for m in solid], wires)
    # height-band origin: Blender measures bands off object bboxes that are not
    # refreshed after the ground deletion, so the stripped layer still counts
    # (and crop pads extend the range too). Reproduce: min of pre-strip and post.
    band_base_y = min(b_pre["min"][1], b["min"][1])

    tints = {}
    for pair in str(shot.get("tint", "")).split(","):
        k, _, v = pair.partition("=")
        if k and v:
            tints[k.strip()] = v.strip().lstrip("#")

    if not scene_has_geometry(solid, wires):
        raise RuntimeError("no geometry left after trim/hide/clip/ground (stale cache or bad bounds)")
    scene = {
        "name": name,
        "params": {
            "views": shot.get("views", ["iso"]),
            "azimuth": shot.get("azimuth", 135),
            "top_azimuth": shot.get("top_azimuth"),
            "projection": shot.get("projection", "tele"),
            "technical": shot.get("technical", "schematic"),
            "height_tint": shot.get("height_tint", 0.9),
            "band_offset": shot.get("band_offset", 0),
            "ground": shot.get("ground", "keep"),
            "tint": tints,
            "legend": shot.get("legend"),
            "res": shot.get("res"),
            "top_res": shot.get("top_res"),
            "margin": shot.get("margin", 1.3),
        },
        "bounds": b,
        "band_base_y": band_base_y,
        # bounds BEFORE ground stripping: render_usd.apply_technical measures
        # height bands off Blender's object bboxes, which are not refreshed
        # after the bmesh ground deletion, so the removed platform layer still
        # sets band 0 and the build's own bottom course lands on band 1 (the
        # cream Part I bottoms). Keep that behavior: the viewer bands from here.
        "bounds_pre": b_pre,
        "fit_boxes": [[[round(v, 3) for v in lo], [round(v, 3) for v in hi]] for lo, hi in fit_boxes],
        "meshes": [flatten_mesh(m, tex) for m in solid],
        "wires": wires,
    }
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{name}.rub")
    write_rub(scene, out)
    tris = sum(len(m["indices"]) // 3 for m in scene["meshes"])
    print(f"  wrote {os.path.relpath(out, REPO)} ({os.path.getsize(out) // 1024} KB, "
          f"{len(scene['meshes'])} meshes, {tris} tris)")
    return out


# ------------------------------------------------------------ binary (.rub)
#
# The site ships one .rub per placed figure, so size matters: JSON floats ran
# to 2.2 MB for the largest build. Everything sits on a 16-unit block grid, so
# quantized integers lose nothing visible.
#
#   gzip( "RUB1" | u32 header_len | header JSON | pad to 4 | arrays... )
#
# The header carries the scene metadata and, per mesh, the byte offset, count
# and type of each array. Positions are int16 relative to `origin` at `1/q`
# units, normals int8 (x127), uvs uint16 (x65535), wire colors uint8, indices
# uint16 or uint32. gzip runs with mtime=0 so unchanged builds stay byte-identical
# in git.

import gzip
import struct
from array import array

RUB_MAGIC = b"RUB1"
if sys.byteorder != "little":
    sys.exit("usd_to_scene: .rub output assumes a little-endian host")


def write_rub(scene, path):
    meshes = scene["meshes"]
    wires = scene["wires"]
    allpos = [m["positions"] for m in meshes] + ([wires["positions"]] if wires else [])
    lo = [min(min(p[a::3]) for p in allpos if p) for a in range(3)]
    hi = [max(max(p[a::3]) for p in allpos if p) for a in range(3)]
    origin = [(lo[a] + hi[a]) / 2 for a in range(3)]
    max_abs = max(max(hi[a] - origin[a], origin[a] - lo[a]) for a in range(3)) or 1.0
    q = 64
    while q > 1 and max_abs * q > 32000:
        q //= 2

    body = bytearray()

    def put(arr_type, values):
        a = array(arr_type, values)
        while len(body) % 4:
            body.append(0)
        off = len(body)
        body.extend(a.tobytes())
        return [off, len(a), arr_type]

    def qpos(ps):
        return [round((ps[i] - origin[i % 3]) * q) for i in range(len(ps))]

    def idx(ix):
        return put("H" if (max(ix) if ix else 0) < 65536 else "I", ix)

    head_meshes = []
    for m in meshes:
        arrays = {
            "position": put("h", qpos(m["positions"])),
            "normal": put("b", [max(-127, min(127, round(v * 127))) for v in m["normals"]]),
            "index": idx(m["indices"]),
        }
        if m["uvs"]:
            arrays["uv"] = put("H", [max(0, min(65535, round(v * 65535))) for v in m["uvs"]])
        head_meshes.append({k: m[k] for k in ("name", "block", "role", "texture", "displayColor")} | {"arrays": arrays})
    head_wires = None
    if wires:
        head_wires = {"arrays": {
            "position": put("h", qpos(wires["positions"])),
            "color": put("B", [max(0, min(255, round(v * 255))) for v in wires["colors"]]),
            "index": idx(wires["indices"]),
        }}
    header = {k: scene[k] for k in ("name", "params", "bounds", "band_base_y", "bounds_pre", "fit_boxes")}
    header |= {"version": 1, "origin": origin, "q": q, "meshes": head_meshes, "wires": head_wires}
    hb = json.dumps(header, separators=(",", ":")).encode()
    out = bytearray(RUB_MAGIC + struct.pack("<I", len(hb)) + hb)
    while len(out) % 4:
        out.append(0x20)          # JSON-safe padding (trailing spaces)
    out.extend(body)
    with open(path, "wb") as f:
        f.write(gzip.compress(bytes(out), compresslevel=9, mtime=0))


def load_shots():
    with open(SHOTS_FILE) as f:
        data = json.load(f)
    defaults = data.pop("_defaults", {})
    return {k: {**defaults, **v} for k, v in data.items()}


def page_slug(dest):
    """src/<Part>/<Module>/images/x.png -> the Astro route prefix of that
    module's page ('part-i--foundations/02_the-grammar-of-circuits')."""
    parts = dest.replace(os.sep, "/").split("/")
    i = parts.index("src")
    return "/".join(p.lower() for p in parts[i + 1:i + 3])


def publish(shots, builds_dir):
    """Copy every placed figure's build into the site, plus the component
    textures those builds use, and write the page -> image -> build map the
    course page reads. The site dir is fully generated: it is rebuilt from
    scratch so removed placements disappear."""
    import shutil
    if os.path.isdir(SITE_PUBLIC):
        shutil.rmtree(SITE_PUBLIC)
    os.makedirs(os.path.join(SITE_PUBLIC, "textures"))
    figures, textures, skipped = {}, set(), []
    hold = json.load(open(HOLD_FILE)) if os.path.exists(HOLD_FILE) else {}
    for shot_name in sorted(shots):
        for view, dest in sorted((shots[shot_name].get("place") or {}).items()):
            src = os.path.join(builds_dir, f"{shot_name}.rub")
            if f"{shot_name}/{view}" in hold:
                skipped.append(f"{shot_name}/{view}: held ({hold[f'{shot_name}/{view}']})")
                continue
            if not os.path.exists(os.path.join(REPO, dest)):
                skipped.append(f"{shot_name}/{view}: placed image {dest} does not exist")
                continue
            if not os.path.exists(src):
                skipped.append(f"{shot_name}/{view}: no build (convert it first)")
                continue
            page = page_slug(dest)
            name = os.path.splitext(os.path.basename(dest))[0]
            module_dir = os.path.join(REPO, *dest.split("/")[:3])
            prose = "".join(open(os.path.join(module_dir, f)).read()
                            for f in ("draft.md", "introduction.md") if os.path.exists(os.path.join(module_dir, f)))
            if f"images/{name}.png" not in prose:
                skipped.append(f"{shot_name}/{view}: {dest} is not referenced by its module's prose")
                continue
            if name in figures.setdefault(page, {}):
                sys.exit(f"publish: {page} places {name} twice")
            figures[page][name] = {"shot": shot_name, "view": view}
            shutil.copyfile(src, os.path.join(SITE_PUBLIC, f"{shot_name}.rub"))
            with gzip.open(src) as f:
                raw = f.read()
            head = json.loads(raw[8:8 + struct.unpack("<I", raw[4:8])[0]])
            textures |= {m["texture"] for m in head["meshes"] if m["role"] == "component" and m["texture"]}
    for t in sorted(textures):
        shutil.copyfile(os.path.join(TEXTURES_SRC, t), os.path.join(SITE_PUBLIC, "textures", t))
    os.makedirs(os.path.dirname(SITE_MAP), exist_ok=True)
    with open(SITE_MAP, "w") as f:
        json.dump(figures, f, indent=1, sort_keys=True)
        f.write("\n")
    n = sum(len(v) for v in figures.values())
    size = sum(os.path.getsize(os.path.join(SITE_PUBLIC, x)) for x in os.listdir(SITE_PUBLIC) if x.endswith(".rub"))
    print(f"publish: {n} figure(s) on {len(figures)} page(s), "
          f"{len([x for x in os.listdir(SITE_PUBLIC) if x.endswith('.rub')])} build(s) ({size // 1024} KB), "
          f"{len(textures)} texture(s) -> {os.path.relpath(SITE_PUBLIC, REPO)}")
    for msg in skipped:
        print(f"publish: skipped {msg}")


def main():
    args = sys.argv[1:]
    out_dir = DEFAULT_OUT
    usd_override = None
    do_publish = False
    names = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--out":
            i += 1; out_dir = args[i]
        elif a == "--usd":
            i += 1; usd_override = args[i]
        elif a == "--all":
            names = None
        elif a == "--publish":
            do_publish = True
        elif a.startswith("--"):
            sys.exit(f"unknown flag {a}")
        else:
            names.append(a)
        i += 1

    if usd_override:
        stem = os.path.splitext(os.path.basename(usd_override))[0]
        convert(stem, {}, usd_override, out_dir)
        return

    shots = load_shots()
    if names is None:
        names = sorted(shots)
    written = []
    for n in names:
        if n not in shots:
            print(f"[{n}] not in shots.json, skipping")
            continue
        usd = os.path.join(USD_CACHE, f"{n}.usd")
        if not os.path.exists(usd):
            print(f"[{n}] no cached USD at {usd}, skipping")
            continue
        try:
            convert(n, shots[n], usd, out_dir)
            written.append(n)
        except Exception as ex:  # keep the batch going; report at the end
            print(f"[{n}] FAILED: {ex}")
            stale = os.path.join(out_dir, f"{n}.rub")
            if os.path.exists(stale):
                os.remove(stale)
    # index for the viewer's shot picker: exactly the build files on disk
    idx_path = os.path.join(out_dir, "index.json")
    have = {f[:-4] for f in os.listdir(out_dir) if f.endswith(".rub")}
    idx = sorted(have)
    with open(idx_path, "w") as f:
        json.dump(idx, f, indent=0)
    print(f"index: {len(idx)} build(s) -> {os.path.relpath(idx_path, REPO)}")
    # placed figure -> (shot, view), from each shot's "place" map, so a page can
    # swap a static *_minecraft.png for the live build it was rendered from
    places = {}
    for shot_name, shot in shots.items():
        if shot_name not in have:
            continue
        for view, dest in (shot.get("place") or {}).items():
            places[os.path.splitext(os.path.basename(dest))[0]] = {"shot": shot_name, "view": view}
    with open(os.path.join(out_dir, "places.json"), "w") as f:
        json.dump(places, f, indent=1, sort_keys=True)
    print(f"places: {len(places)} placed figure(s) -> live builds")
    if do_publish:
        publish(shots, out_dir)


if __name__ == "__main__":
    main()
