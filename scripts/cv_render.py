#!/usr/bin/env python3
"""
Render CircuitVerse circuits straight from a .cv project file to clean SVG (+PNG).

The .cv export is a structured graph of every circuit in the project: each
element carries position + orientation, and `allNodes` carries every wire node
with its connection list. We recompute geometry from that graph, so output is
perfectly grid-aligned (sidestepping CircuitVerse's buggy SVG exporter), runs a
small signal simulation to colour powered wires, and draws straight in the
course light design-system palette — no Figma cleanup step.

    python3 scripts/cv_render.py <project.cv> --list
    python3 scripts/cv_render.py <project.cv> "2-to-4 decoder" -o out.svg [--png]
    python3 scripts/cv_render.py <project.cv> --batch renders/diagrams.json

Design system (light): ink structure, red = powered, muted gray = unpowered.
Gate identity is carried by SHAPE (unified ink), not colour — colour is reserved
for signal state, so it never competes with red = ON.
"""
import argparse, json, math, os, sys

# ── canonical palette (shared with the Minecraft renders in render_usd.py) ──
# Signal colours mirror the render dust: powered = bright red, unpowered = deep
# dark red (both redstone-red so a build render and its diagram read the same).
# Structure stays sepia ink for the reading context (matches site --color-text).
INK   = "#30231e"   # structure / gate outlines (site --color-text)
ON    = "#f0392a"   # powered signal — bright red tuned to the render dust glow
OFF   = "#5a1816"   # unpowered signal — muted dark red, matches render dust
PAPER = "#f5f1ea"   # --color-bg (output bg is transparent; used for masks)
FAINT = "#d2cdc5"   # --color-border — annotation rectangles, unlit segments
ON_TINT = "#f8e3e1"  # faint red wash for powered IO box fill

LW = 3.0            # wire stroke
GW = 3.2            # gate outline stroke
MARGIN = 28

# gate body FILLS = the render's actual light layer pastels (band_palette), so a
# gate is filled with the same colour as the blocks it's built from; an ink
# outline keeps it legible. Negated pairs share their family's pastel; gate
# identity is carried by SHAPE + bubble, colour ties the diagrams to the renders.
GATE_FILLS = {
    "NotGate":  "#f0d6d4",                          # render rose
    "AndGate":  "#d1e3c7", "NandGate": "#d1e3c7",   # render sage
    "OrGate":   "#ccdbe5", "NorGate":  "#ccdbe5",   # render dusty-blue
    "XorGate":  "#fce8ba", "XnorGate": "#fce8ba",   # render amber
}

DIRS = {"RIGHT": (0, lambda x, y: (x, y)),
        "DOWN":  (90, lambda x, y: (-y, x)),
        "LEFT":  (180, lambda x, y: (-x, -y)),
        "UP":    (270, lambda x, y: (y, -x))}


def load(path):
    with open(path) as f:
        return json.load(f)


# ── geometry ──────────────────────────────────────────────────────────────
def abs_nodes(scope):
    N = scope["allNodes"]
    pos = [None] * len(N)
    for i, n in enumerate(N):
        if n["type"] == 2:                       # intermediate = absolute
            pos[i] = (n["x"], n["y"])
    for k, v in scope.items():                   # pin nodes = element + rotated offset
        if not (isinstance(v, list) and v and isinstance(v[0], dict)
                and v[0].get("objectType")):
            continue
        for el in v:
            rotf = DIRS.get(el.get("direction", "RIGHT"), DIRS["RIGHT"])[1]
            for pin, idx in el.get("customData", {}).get("nodes", {}).items():
                for j in (idx if isinstance(idx, list) else [idx]):
                    if j < len(N) and pos[j] is None:
                        ox, oy = rotf(N[j]["x"], N[j]["y"])
                        pos[j] = (el["x"] + ox, el["y"] + oy)
    for sub in scope.get("SubCircuit", []):      # subcircuit boundary pins (no rotation)
        for j in sub.get("inputNodes", []) + sub.get("outputNodes", []):
            if j < len(N) and pos[j] is None:
                pos[j] = (sub["x"] + N[j]["x"], sub["y"] + N[j]["y"])
    for i, n in enumerate(N):                     # fallback
        if pos[i] is None:
            pos[i] = (n["x"], n["y"])
    return pos


# ── signal simulation ───────────────────────────────────────────────────────
GATE_FN = {
    "AndGate":  lambda v: int(all(v)),
    "OrGate":   lambda v: int(any(v)),
    "NotGate":  lambda v: int(not v[0]),
    "NorGate":  lambda v: int(not any(v)),
    "NandGate": lambda v: int(not all(v)),
    "XorGate":  lambda v: sum(v) % 2,
    "XnorGate": lambda v: int(sum(v) % 2 == 0),
}


def simulate(scope, forced=None):
    """Return netval: node index -> 0/1/None (None = undriven).
    forced: {input output-node index -> 0/1} overrides stored Input states."""
    N = scope["allNodes"]
    parent = list(range(len(N)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i, n in enumerate(N):
        for j in n["connections"]:
            if j < len(N):
                union(i, j)

    val = {}                                       # root -> 0/1
    # input sources (forced overrides the .cv's stored state by output node)
    for el in scope.get("Input", []):
        st = el.get("customData", {}).get("values", {}).get("state")
        out = el.get("customData", {}).get("nodes", {}).get("output1")
        if forced is not None and out in forced:
            st = forced[out]
        if out is not None and st is not None:
            val[find(out)] = int(st)
    src_roots = set(val.keys())
    # collect gate drivers
    drivers = []
    for k, v in scope.items():
        if not (isinstance(v, list) and v and isinstance(v[0], dict)):
            continue
        for el in v:
            ot = el.get("objectType")
            if ot not in GATE_FN:
                continue
            nd = el["customData"]["nodes"]
            ins = nd.get("inp", nd.get("inp1"))
            ins = ins if isinstance(ins, list) else [ins]
            out = nd.get("output1")
            if out is not None:
                drivers.append((out, ins, GATE_FN[ot]))
    # iterate to fixpoint (combinational converges; cap guards latches)
    for _ in range(200):
        changed = False
        for out, ins, fn in drivers:
            iv = [val.get(find(i), 0) for i in ins if i is not None]
            o = fn(iv)
            r = find(out)
            if r in src_roots:
                continue
            if val.get(r) != o:
                val[r] = o; changed = True
        if not changed:
            break
    return {i: val.get(find(i)) for i in range(len(N))}


def wcol(v):
    return ON if v == 1 else OFF


def io_box(x, y, st):
    """Sharp input/output box: white fill, square corners, coloured outline+digit.
    powered = red outline + red digit; unpowered/unknown = ink outline + ink digit.
    Digit in the site mono (Fira Code)."""
    on = st == 1
    col = ON if on else INK
    digit_font = 'font-family="Fira Code, ui-monospace, monospace" font-size="14" font-weight="600"'
    rect = (f'<rect x="{x-10}" y="{y-10}" width="20" height="20" '
            f'fill="#ffffff" stroke="{col}" stroke-width="{GW}"/>')
    digit = (f'<text x="{x}" y="{y+5}" {digit_font} text-anchor="middle" fill="{col}">{st}</text>'
             if st is not None else "")
    return rect + digit


# ── gate glyphs (local RIGHT frame, origin = element center, output toward +x) ──
def gate_paths(ot, col=INK, fill="none"):
    """(list of <path/circle/line> svg fragments) drawn in local frame.
    col = outline colour, fill = body fill (a light render pastel for cohesion,
    or 'none' for outline-only)."""
    s = []
    def stroke(d):                       # filled gate body
        return (f'<path d="{d}" fill="{fill}" stroke="{col}" stroke-width="{GW}" '
                f'stroke-linecap="square" stroke-linejoin="miter"/>')
    def line(d):                         # open decorative curve, never filled
        return (f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{GW}" '
                f'stroke-linecap="round" stroke-linejoin="round"/>')
    def bubble(cx):
        return (f'<circle cx="{cx}" cy="0" r="4" fill="{PAPER}" stroke="{col}" '
                f'stroke-width="{GW}"/>')
    if ot == "NotGate":
        s.append(stroke("M -9 -11 L 12 0 L -9 11 Z")); s.append(bubble(15))
    elif ot == "AndGate":  # flat back at x=-10 so input pins (x=-10) sit on the edge
        s.append(stroke("M -10 -19 L 0 -19 A 19 19 0 0 1 0 19 L -10 19 Z"))
    elif ot == "NandGate":
        s.append(stroke("M -10 -19 L 0 -19 A 19 19 0 0 1 0 19 L -10 19 Z")); s.append(bubble(22))
    elif ot == "OrGate":
        s.append(stroke("M -16 -19 Q -3 0 -16 19 Q 6 18 19 0 Q 6 -18 -16 -19 Z"))
    elif ot == "NorGate":
        s.append(stroke("M -16 -19 Q -3 0 -16 19 Q 6 18 19 0 Q 6 -18 -16 -19 Z")); s.append(bubble(23))
    elif ot == "XorGate":
        s.append(line("M -24 -19 Q -11 0 -24 19"))   # decorative back line (clear gap)
        s.append(stroke("M -16 -19 Q -3 0 -16 19 Q 6 18 19 0 Q 6 -18 -16 -19 Z"))
    elif ot == "XnorGate":
        s.append(line("M -24 -19 Q -11 0 -24 19"))
        s.append(stroke("M -16 -19 Q -3 0 -16 19 Q 6 18 19 0 Q 6 -18 -16 -19 Z")); s.append(bubble(23))
    else:
        return None
    return s


def esc(t):
    return (t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# str(scope id) -> scope name, populated from the .cv project so SubCircuit
# boxes can show what they actually are instead of a generic "circuit" label.
SUBCIRCUIT_NAMES = {}


def wrap_label(s, width=16):
    """Greedy word-wrap a subcircuit label into lines so long scope names fit
    inside the box instead of overflowing."""
    lines, cur = [], ""
    for w in s.split():
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines or [s]


# ── 7-segment display (a..g + dot), lit segments coloured by signal ──────────
SEG_PATH = {  # within a 60x110 box centered at origin
    "a": "M -18 -46 L 18 -46", "b": "M 22 -42 L 22 -6", "c": "M 22 6 L 22 42",
    "d": "M -18 46 L 18 46", "e": "M -22 6 L -22 42", "f": "M -22 -42 L -22 -6",
    "g": "M -18 0 L 18 0",
}


def render(scope, scale=2.0, gate_colors=False, inputs=None, only=None):
    """only: optional set/list of objectTypes to draw in isolation (e.g.
    ["Input"]). When set, wires and connection dots are skipped and only those
    elements are rendered — for showing just the I/O of an interface."""
    only = set(only) if only else None
    N = scope["allNodes"]
    pos = abs_nodes(scope)
    # optional input override: a list of 0/1 applied to Input boxes left→right
    # (by x), so a circuit can show the same defining case as its abstract figure.
    forced = None
    if inputs is not None:
        forced = {}
        ins_sorted = sorted(scope.get("Input", []), key=lambda e: e.get("x", 0))
        for el, v in zip(ins_sorted, inputs):
            out = el.get("customData", {}).get("nodes", {}).get("output1")
            if out is not None:
                forced[out] = int(v)
    net = simulate(scope, forced)
    xs, ys, body = [], [], []

    def note(x, y, pad=18):
        xs.extend((x - pad, x + pad)); ys.extend((y - pad, y + pad))

    # pin axis: horizontal-exit for LEFT/RIGHT elements, vertical for UP/DOWN.
    # CircuitVerse stores some gate-input wires as raw diagonals (the alignment
    # you'd otherwise straighten in Figma); we Manhattan-route them, leaving each
    # pin along its natural axis so the bend lands cleanly.
    axis = {}
    for k, v in scope.items():
        if isinstance(v, list) and v and isinstance(v[0], dict) and v[0].get("objectType"):
            for el in v:
                ax = "h" if el.get("direction", "RIGHT") in ("LEFT", "RIGHT") else "v"
                for idx in el.get("customData", {}).get("nodes", {}).values():
                    for j in (idx if isinstance(idx, list) else [idx]):
                        axis[j] = ax

    # wires
    edges = set()
    for i, n in enumerate(N):
        for j in n["connections"]:
            if j < len(N):
                edges.add((min(i, j), max(i, j)))

    def bus_run(t, exclude):
        """If t's neighbours (minus `exclude`) form a straight bus through t,
        return ('v'|'h', lo, hi) for the span; else None."""
        nb = [j for j in N[t]["connections"] if j < len(N) and j != exclude]
        if len(nb) < 2:
            return None
        if all(pos[j][0] == pos[t][0] for j in nb):
            ys = [pos[j][1] for j in nb]; return ("v", min(ys), max(ys))
        if all(pos[j][1] == pos[t][1] for j in nb):
            xs = [pos[j][0] for j in nb]; return ("h", min(xs), max(xs))
        return None

    suppress = set()   # tapped bus nodes that become pass-through (no dot)
    taps = []          # (x, y, net-source-node) perpendicular bus connections
    for a, b in (() if only else sorted(edges)):
        (x1, y1), (x2, y2) = pos[a], pos[b]
        c = wcol(net.get(a))
        note(x1, y1); note(x2, y2)
        if x1 == x2 or y1 == y2:
            body.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" '
                        f'stroke-width="{LW}" stroke-linecap="round"/>')
            continue
        # diagonal. If one end is a pin and the other sits on a straight bus,
        # tap the bus perpendicularly at the pin's level (a real T-junction)
        # instead of running the wire alongside the bus.
        pin = a if a in axis else (b if b in axis else None)
        routed = False
        if pin is not None:
            t = b if pin == a else a
            (px, py), (tx, ty) = pos[pin], pos[t]
            run = bus_run(t, pin)
            if run and axis[pin] == "h" and run[0] == "v" and run[1] <= py <= run[2]:
                body.append(f'<line x1="{px}" y1="{py}" x2="{tx}" y2="{py}" stroke="{c}" '
                            f'stroke-width="{LW}" stroke-linecap="round"/>')
                taps.append((tx, py, pin)); suppress.add(t); routed = True
            elif run and axis[pin] == "v" and run[0] == "h" and run[1] <= px <= run[2]:
                body.append(f'<line x1="{px}" y1="{py}" x2="{px}" y2="{ty}" stroke="{c}" '
                            f'stroke-width="{LW}" stroke-linecap="round"/>')
                taps.append((px, ty, pin)); suppress.add(t); routed = True
        if not routed:                        # fallback: L-bend along pin axis
            if a in axis:
                hf = axis[a] == "h"; (sx, sy), (ex, ey) = (x1, y1), (x2, y2)
            elif b in axis:
                hf = axis[b] == "h"; (sx, sy), (ex, ey) = (x2, y2), (x1, y1)
            else:
                hf = True; (sx, sy), (ex, ey) = (x1, y1), (x2, y2)
            cx, cy = (ex, sy) if hf else (sx, ey)
            body.append(f'<polyline points="{sx},{sy} {cx},{cy} {ex},{ey}" fill="none" '
                        f'stroke="{c}" stroke-width="{LW}" stroke-linecap="square" '
                        f'stroke-linejoin="miter"/>')

    # gate pins get a lead into the gate instead of a dot (above), so the gate
    # stays the focal element — collect them to skip in the dot pass.
    gate_pins = set()
    for k, v in scope.items():
        if (isinstance(v, list) and v and isinstance(v[0], dict)
                and v[0].get("objectType") in GATE_FN):
            for el in v:
                for idx in el.get("customData", {}).get("nodes", {}).values():
                    for j in (idx if isinstance(idx, list) else [idx]):
                        gate_pins.add(j)

    # connection dots: a dot at I/O box pins and at wire terminals/junctions
    # (intermediate nodes, degree != 2). Gate pins, plain bends, and straightened
    # taps get none; perpendicular taps add their own dot.
    DOT = LW * 1.05
    for i, n in (() if only else enumerate(N)):
        if i in suppress or i in gate_pins:   # gate pins use leads, not dots
            continue
        deg = sum(1 for j in n["connections"] if j < len(N))
        if n["type"] in (0, 1) or deg != 2:
            x, y = pos[i]
            body.append(f'<circle cx="{x}" cy="{y}" r="{DOT}" fill="{wcol(net.get(i))}"/>')
    for x, y, src in (() if only else taps):
        body.append(f'<circle cx="{x}" cy="{y}" r="{DOT}" fill="{wcol(net.get(src))}"/>')

    # elements
    def label(el, cx, cy):
        lbl = esc(el.get("label", ""))
        if not lbl:
            return
        d = el.get("labelDirection", "UP")
        off = 22
        dx, dy, anchor = {
            "LEFT":  (-off, 5, "end"),
            "RIGHT": (off, 5, "start"),
            "UP":    (0, -off, "middle"),
            "DOWN":  (0, off + 6, "middle"),
        }.get(d, (0, -off, "middle"))
        body.append(f'<text x="{cx+dx}" y="{cy+dy}" font-family="ui-monospace,monospace" '
                    f'font-size="14" text-anchor="{anchor}" fill="{INK}">{lbl}</text>')

    for k, v in scope.items():
        if not (isinstance(v, list) and v and isinstance(v[0], dict)
                and v[0].get("objectType")):           # skip allNodes/raw lists
            continue
        for el in v:
            ot = el.get("objectType"); ex, ey = el.get("x", 0), el.get("y", 0)
            if only and ot not in only:
                continue
            note(ex, ey, 30)
            gp = gate_paths(ot, INK, GATE_FILLS.get(ot, "none") if gate_colors else "none")
            if gp:
                deg = DIRS.get(el.get("direction", "RIGHT"), DIRS["RIGHT"])[0]
                # short lead from each pin into the gate body so the wire meets
                # the gate flush (no gap/dot poking past the negation bubble);
                # the gate is drawn on top, hiding the overlap and staying focal.
                for idx in el.get("customData", {}).get("nodes", {}).values():
                    for j in (idx if isinstance(idx, list) else [idx]):
                        if j < len(N):
                            px, py = pos[j]
                            ddx, ddy = ex - px, ey - py
                            # snap the lead to the dominant axis so it runs straight
                            # into the gate (the wire approaches perpendicular to the
                            # back); a diagonal toward the center looks like the wire
                            # angles in, esp. on the curved OR/XOR back.
                            if abs(ddx) >= abs(ddy):
                                lx, ly = px + (10 if ddx >= 0 else -10), py
                            else:
                                lx, ly = px, py + (10 if ddy >= 0 else -10)
                            body.append(f'<line x1="{px}" y1="{py}" x2="{lx}" y2="{ly}" '
                                        f'stroke="{wcol(net.get(j))}" stroke-width="{LW}" '
                                        f'stroke-linecap="round"/>')
                body.append(f'<g transform="translate({ex},{ey}) rotate({deg})">'
                            + "".join(gp) + "</g>")
            elif ot in ("Input", "Output"):
                if ot == "Input":
                    out = el.get("customData", {}).get("nodes", {}).get("output1")
                    st = el.get("customData", {}).get("values", {}).get("state")
                    if forced is not None and out in forced:
                        st = forced[out]
                else:  # output: show the simulated value at its input pin
                    inp = el.get("customData", {}).get("nodes", {}).get("inp1")
                    st = net.get(inp) if inp is not None else None
                body.append(io_box(ex, ey, st))
                label(el, ex, ey)
            elif ot == "SevenSegDisplay":
                nd = el.get("customData", {}).get("nodes", {})
                deg = DIRS.get(el.get("direction", "RIGHT"), DIRS["RIGHT"])[0]
                segs = [f'<rect x="-32" y="-58" width="64" height="116" '
                        f'fill="none" stroke="{INK}" stroke-width="{GW}"/>']
                for seg, d in SEG_PATH.items():
                    idx = nd.get(seg)
                    lit = idx is not None and net.get(idx) == 1
                    segs.append(f'<path d="{d}" stroke="{ON if lit else FAINT}" '
                                f'stroke-width="6" stroke-linecap="round"/>')
                body.append(f'<g transform="translate({ex},{ey}) rotate({deg})">'
                            + "".join(segs) + "</g>")
            elif ot == "DigitalLed":
                nd = el.get("customData", {}).get("nodes", {})
                pin = nd.get("inp1")
                lit = net.get(pin) == 1
                # the LED's pin can sit well off its body; draw a lead from the
                # pin to the body (LED drawn on top) so it reads as connected.
                if pin is not None and pin < len(N):
                    px, py = pos[pin]
                    body.append(f'<line x1="{px}" y1="{py}" x2="{ex}" y2="{ey}" '
                                f'stroke="{wcol(net.get(pin))}" stroke-width="{LW}" '
                                f'stroke-linecap="round"/>')
                body.append(f'<circle cx="{ex}" cy="{ey}" r="13" fill="{ON if lit else PAPER}" '
                            f'stroke="{INK}" stroke-width="{GW}"/>')
            elif ot == "Rectangle":
                # the abstraction boundary is auto-computed below from the gate
                # cluster (the .cv Rectangle's units don't map reliably).
                pass

    # subcircuit boxes
    for sub in scope.get("SubCircuit", []):
        pins = [pos[j] for j in sub.get("inputNodes", []) + sub.get("outputNodes", [])
                if j < len(N)]
        if not pins:
            continue
        pxs = [p[0] for p in pins]; pys = [p[1] for p in pins]
        x0, x1 = min(pxs), max(pxs); y0, y1 = min(pys), max(pys)
        body.append(f'<rect x="{x0-10}" y="{y0-10}" width="{x1-x0+20}" height="{y1-y0+20}" '
                    f'fill="{PAPER}" stroke="{INK}" stroke-width="{GW}"/>')
        raw = (SUBCIRCUIT_NAMES.get(str(sub.get("id")))
               or sub.get("label", "") or "circuit")
        # wrap to the box's actual inner width so the label never runs into the
        # border (~0.56em per char for Young Serif at this size; 16px padding).
        fs = 15
        avail = (x1 - x0 + 20) - 18
        budget = max(6, int(avail / (fs * 0.56)))
        lines = wrap_label(raw, budget)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        lh = fs + 3
        y0t = cy - (len(lines) - 1) * lh / 2 + 5
        for i, ln in enumerate(lines):
            body.append(f'<text x="{cx}" y="{y0t + i*lh:.1f}" '
                        f'font-family="Young Serif, Georgia, serif" font-size="{fs}" '
                        f'text-anchor="middle" fill="{INK}">{esc(ln)}</text>')
        for j in sub.get("inputNodes", []) + sub.get("outputNodes", []):
            if j < len(N):
                x, y = pos[j]
                body.append(f'<circle cx="{x}" cy="{y}" r="{LW*1.3}" fill="{wcol(net.get(j))}"/>')
        note(x0, y0); note(x1, y1)

    # abstraction boundary: when the scope has a Rectangle annotation, draw a
    # dashed box around the gate cluster (I/O boxes sit outside) — it signals
    # the whole circuit is black-boxed as one symbol elsewhere. Drawn behind.
    if scope.get("Rectangle"):
        gxs, gys = [], []
        for k, v in scope.items():
            if (isinstance(v, list) and v and isinstance(v[0], dict)
                    and v[0].get("objectType") in GATE_FN):
                for el in v:
                    gxs.append(el["x"]); gys.append(el["y"])
        if gxs:
            pad = 26
            # Horizontal extent must also cover the vertical wire runs that climb
            # from the I/O boxes into the gates (those runs sit at the I/O x); the
            # gate-only extent clips them. Vertical extent stays on the gate
            # cluster so the I/O boxes themselves remain outside the boundary.
            ioxs = [el["x"] for ot in ("Input", "Output") for el in scope.get(ot, [])]
            allx = gxs + ioxs
            bx0, by0 = min(allx) - pad, min(gys) - pad
            bx1, by1 = max(allx) + pad, max(gys) + pad
            body.insert(0, f'<rect x="{bx0}" y="{by0}" width="{bx1-bx0}" height="{by1-by0}" '
                        f'fill="none" stroke="{FAINT}" stroke-width="2.2" stroke-dasharray="8 6"/>')
            note(bx0, by0); note(bx1, by1)

    if not xs:
        xs, ys = [0, 100], [0, 100]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    w, h = (maxx - minx) + 2 * MARGIN, (maxy - miny) + 2 * MARGIN
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w*scale:.0f}" '
           f'height="{h*scale:.0f}" viewBox="0 0 {w} {h}">\n'
           f'<g transform="translate({-minx+MARGIN},{-miny+MARGIN})">\n'
           + "\n".join(body) + "\n</g>\n</svg>\n")
    return svg


GATE_NAMES = {"AndGate": "AND", "OrGate": "OR", "NotGate": "NOT", "NorGate": "NOR",
              "NandGate": "NAND", "XorGate": "XOR", "XnorGate": "XNOR"}
NAME_TO_TYPE = {v: k for k, v in GATE_NAMES.items()}


# how far each gate's back extends below center when drawn pointing up
# (= -min local x); used to place the name a consistent gap below each symbol.
GATE_DEPTH = {"NotGate": 9, "AndGate": 10, "NandGate": 10, "OrGate": 16,
              "NorGate": 16, "XorGate": 26, "XnorGate": 26}


def render_hero(ot, scale=5.0):
    """Standalone gate-introduction figure: big symbol (pointing up, like the
    course's intro art) + its name. Pastel fill + ink outline, name in ink."""
    gp = gate_paths(ot, INK, GATE_FILLS.get(ot, "none"))
    if gp is None:
        return None
    name = GATE_NAMES.get(ot, ot)
    glyph = '<g transform="rotate(270)">' + "".join(gp) + "</g>"
    # flat-bottomed gates (NOT/AND/NAND) read cramped at the same gap because
    # the curved gates' receding backs fake extra space — drop their name a bit.
    flat_extra = {"NotGate": 4, "AndGate": 4, "NandGate": 4}.get(ot, 0)
    ty = GATE_DEPTH.get(ot, 16) + 22 + flat_extra   # gap below the gate's low point
    txt = (f'<text x="0" y="{ty}" font-family="Young Serif, Georgia, serif" font-size="19" '
           f'font-weight="800" letter-spacing="0.5" text-anchor="middle" '
           f'fill="{INK}" stroke="{INK}" stroke-width="0.5">{name}</text>')
    vb_x, vb_y, vb_w, vb_h = -46, -30, 92, 92  # uniform canvas across all gates
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{vb_w*scale:.0f}" '
           f'height="{vb_h*scale:.0f}" viewBox="{vb_x} {vb_y} {vb_w} {vb_h}">\n'
           f'{glyph}\n{txt}\n</svg>\n')
    return svg


def render_gate_intro(ot, scale=4.0):
    """Gate-introduction figure: the big hero symbol (left) + a small worked
    example circuit (right), both in the gate's hero colour. The example is
    synthesised (the .cv only has composite gate scopes, not simple ones)."""
    name = GATE_NAMES.get(ot)
    if name is None:
        return None
    glyph_gp = "".join(gate_paths(ot, INK, GATE_FILLS.get(ot, "none")))
    is_not = ot == "NotGate"
    # each gate's defining "aha" case (the input combo that shows its character)
    demo = {"NotGate": (1,), "AndGate": (1, 1), "NandGate": (1, 1), "OrGate": (1, 0),
            "NorGate": (0, 0), "XorGate": (1, 0), "XnorGate": (1, 1)}[ot]
    a = demo[0]; b = demo[-1]
    out = GATE_FN[ot]([a] if is_not else [a, b])
    P = []

    def ddot(x, y, on):
        P.append(f'<circle cx="{x}" cy="{y}" r="{LW*1.05}" fill="{ON if on else OFF}"/>')

    def wire(pts, on):
        p = " ".join(f"{x},{y}" for x, y in pts)
        P.append(f'<polyline points="{p}" fill="none" stroke="{ON if on else OFF}" '
                 f'stroke-width="{LW}" stroke-linecap="square" stroke-linejoin="miter"/>')

    def iobox(x, y, st):
        P.append(io_box(x, y, st))

    # ── example (right, normal size). Wires start inside the gate and the gate
    # is drawn ON TOP, so they meet it flush; dots only at the box pins. ──
    gate_g = f'<g transform="rotate(270)">{glyph_gp}</g>'
    wire([(0, -8), (0, -46)], out); ddot(0, -46, out); iobox(0, -56, out)
    if is_not:
        wire([(0, 8), (0, 46)], a); ddot(0, 46, a); iobox(0, 56, a)
    else:
        wire([(-9, 6), (-9, 34), (-24, 34), (-24, 46)], a); ddot(-24, 46, a); iobox(-24, 56, a)
        wire([(9, 6), (9, 34), (24, 34), (24, 46)], b); ddot(24, 46, b); iobox(24, 56, b)
    example = f'<g transform="translate(56,0)">{"".join(P)}{gate_g}</g>'

    # ── hero (left, large): the symbol is the focus, scaled up; name below ──
    HS = 1.9
    depth = GATE_DEPTH.get(ot, 16) + {"NotGate": 4, "AndGate": 4, "NandGate": 4}.get(ot, 0)
    hero_glyph = f'<g transform="scale({HS})"><g transform="rotate(270)">{glyph_gp}</g></g>'
    hero_txt = (f'<text x="0" y="{depth*HS+22:.0f}" font-family="Young Serif, Georgia, serif" '
                f'font-size="24" font-weight="800" letter-spacing="1" text-anchor="middle" '
                f'fill="{INK}" stroke="{INK}" stroke-width="0.7">{name}</text>')
    hero = f'<g transform="translate(-64,-6)">{hero_glyph}{hero_txt}</g>'

    vb_x, vb_y, vb_w, vb_h = -116, -72, 212, 146
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{vb_w*scale:.0f}" '
            f'height="{vb_h*scale:.0f}" viewBox="{vb_x} {vb_y} {vb_w} {vb_h}">\n'
            f'{hero}\n{example}\n</svg>\n')


def render_compose(parts, sep="equiv", scale=2.0, gap=64):
    """Lay several rendered diagrams (full <svg> strings from render()) side by
    side, separated by a glyph (default ≡), into one SVG. Each part keeps its own
    0..W,0..H coordinate space (its content starts with a translate to MARGIN), so
    we just wrap it in a translate and stack horizontally, vertically centred."""
    import re
    items = []
    for s in parts:
        vb = re.search(r'viewBox="([\d.\- ]+)"', s).group(1)
        _, _, W, H = map(float, vb.split())
        inner = s[s.index(">", s.index("<svg")) + 1: s.rindex("</svg>")]
        items.append((W, H, inner))
    sep_w = 44
    total_w = sum(w for w, _, _ in items) + gap * 2 * (len(items) - 1) + sep_w * (len(items) - 1)
    total_h = max(h for _, h, _ in items)
    body, x = [], 0.0
    for i, (w, h, inner) in enumerate(items):
        yoff = (total_h - h) / 2
        body.append(f'<g transform="translate({x:.1f},{yoff:.1f})">{inner}</g>')
        x += w
        if i != len(items) - 1:
            cx = x + gap + sep_w / 2
            cy = total_h / 2
            if sep == "equiv":   # ≡ identical-to, drawn (Young Serif lacks the glyph)
                for dy in (-9, 0, 9):
                    body.append(f'<line x1="{cx-13}" y1="{cy+dy}" x2="{cx+13}" y2="{cy+dy}" '
                                f'stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/>')
            else:
                body.append(f'<text x="{cx}" y="{cy}" font-family="Young Serif, Georgia, serif" '
                            f'font-size="34" text-anchor="middle" dominant-baseline="central" '
                            f'fill="{INK}">{sep}</text>')
            x += gap * 2 + sep_w
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w*scale:.0f}" '
            f'height="{total_h*scale:.0f}" viewBox="0 0 {total_w:.1f} {total_h:.1f}">\n'
            + "\n".join(body) + "\n</svg>\n")


def render_seg_labeled(scale=2.0):
    """A standalone 7-segment display with every segment drawn and labeled a-g.
    Matches the SevenSegDisplay in the CV diagrams (sharp INK-outlined panel,
    round-capped signal-red segments) but with the bars thick enough to carry
    the letter on each — cream letters, our 'powered = cream digit' convention."""
    S = 5.0
    centers = {"a": (0, -46), "b": (22, -24), "c": (22, 24), "d": (0, 46),
               "e": (-22, 24), "f": (-22, -24), "g": (0, 0)}
    bx, by, bw, bh = -32 * S, -58 * S, 64 * S, 116 * S
    parts = [f'<rect x="{bx:.0f}" y="{by:.0f}" width="{bw:.0f}" height="{bh:.0f}" '
             f'fill="{PAPER}" stroke="{INK}" stroke-width="7"/>',   # sharp corners
             f'<g transform="scale({S})">']
    for d in SEG_PATH.values():       # thick round-capped bars, all lit (an "8")
        parts.append(f'<path d="{d}" fill="none" stroke="{ON}" stroke-width="5" '
                     f'stroke-linecap="round"/>')
    parts.append("</g>")
    nudge = {"g": -6}             # lift g off the bar's lower edge
    for k, (cx, cy) in centers.items():
        ty = cy * S + 8 + nudge.get(k, 0)
        parts.append(f'<text x="{cx*S:.0f}" y="{ty:.0f}" '
                     f'font-family="Young Serif, Georgia, serif" font-size="22" '
                     f'font-weight="700" text-anchor="middle" fill="{PAPER}">{k}</text>')
    M = 12
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{(bw+2*M)*scale:.0f}" '
            f'height="{(bh+2*M)*scale:.0f}" '
            f'viewBox="{bx-M:.0f} {by-M:.0f} {bw+2*M:.0f} {bh+2*M:.0f}">\n'
            + "\n".join(parts) + "\n</svg>\n")


def render_subcircuit_box(label, left=(), right=(), top=(), bottom=(),
                          bw=150, bh=280, scale=2.0):
    """A single labeled subcircuit black-box with pins on chosen edges (dots
    outside the border, labels inside), in the design-system palette. Used for
    the 'default vs organized layout' figures in the abstraction interlude."""
    PL, R = 14, 3.4
    p = [f'<rect x="0" y="0" width="{bw}" height="{bh}" fill="{PAPER}" '
         f'stroke="{INK}" stroke-width="{GW}"/>']
    # title wraps to the box width (and clears the top-row pins) so it never
    # runs into the border or collides with the first output label.
    tfs = 14
    tbudget = max(6, int((bw - 26) / (tfs * 0.56)))
    for i, ln in enumerate(wrap_label(label, tbudget)):
        p.append(f'<text x="{bw/2}" y="{22 + i*(tfs+3)}" '
                 f'font-family="Young Serif, Georgia, serif" font-size="{tfs}" '
                 f'text-anchor="middle" fill="{INK}">{esc(ln)}</text>')

    def edge(names, e):
        n = len(names)
        for i, nm in enumerate(names):
            t = (i + 1) / (n + 1)
            if e in ("L", "R"):
                y = t * bh
                x = 0 if e == "L" else bw
                xo = x - PL if e == "L" else x + PL
                tx = x + 9 if e == "L" else x - 9
                anc = "start" if e == "L" else "end"
                p.append(f'<line x1="{x}" y1="{y:.1f}" x2="{xo}" y2="{y:.1f}" '
                         f'stroke="{INK}" stroke-width="{LW}"/>')
                p.append(f'<circle cx="{xo}" cy="{y:.1f}" r="{R}" fill="{OFF}"/>')
                p.append(f'<text x="{tx}" y="{y+5:.1f}" font-family="ui-monospace,monospace" '
                         f'font-size="13" text-anchor="{anc}" fill="{INK}">{esc(nm)}</text>')
            else:
                x = t * bw
                y = 0 if e == "T" else bh
                yo = y - PL if e == "T" else y + PL
                ty = y - PL - 8 if e == "T" else y + PL + 16
                p.append(f'<line x1="{x:.1f}" y1="{y}" x2="{x:.1f}" y2="{yo}" '
                         f'stroke="{INK}" stroke-width="{LW}"/>')
                p.append(f'<circle cx="{x:.1f}" cy="{yo}" r="{R}" fill="{OFF}"/>')
                p.append(f'<text x="{x:.1f}" y="{ty}" font-family="ui-monospace,monospace" '
                         f'font-size="13" text-anchor="middle" fill="{INK}">{esc(nm)}</text>')
    edge(left, "L"); edge(right, "R"); edge(top, "T"); edge(bottom, "B")
    M = 46
    vb_w, vb_h = bw + 2 * M, bh + 2 * M
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{vb_w*scale:.0f}" '
            f'height="{vb_h*scale:.0f}" viewBox="{-M} {-M} {vb_w} {vb_h}">\n'
            + "\n".join(p) + "\n</svg>\n")


def to_png(svg_path, png_path):
    # the SVG already declares width/height = viewBox * scale, so rasterise at
    # its natural size (don't let cairosvg scale again).
    import cairosvg
    cairosvg.svg2png(url=svg_path, write_to=png_path)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("cv", nargs="?")
    p.add_argument("name", nargs="?")
    p.add_argument("--list", action="store_true")
    p.add_argument("--batch")
    p.add_argument("-o", "--out", default="/tmp/cv-out.svg")
    p.add_argument("--png", action="store_true")
    p.add_argument("--scale", type=float, default=2.0)
    p.add_argument("--gate-colors", action="store_true",
                   help="colour each gate (negated pairs share a hue) instead of ink")
    p.add_argument("--hero", help="render one gate-intro figure (e.g. NOT or NotGate)")
    p.add_argument("--heroes", action="store_true",
                   help="render all 7 standalone gate hero symbols to --out dir")
    p.add_argument("--gate-intros", action="store_true",
                   help="render all 7 gate-intro figures (hero + example) to --out dir")
    p.add_argument("--layout-demo", action="store_true",
                   help="render the subcircuit default-vs-organized layout pair to --out dir")
    p.add_argument("--seg-labeled", action="store_true",
                   help="render the labeled 7-segment naming reference to --out")
    a = p.parse_args()

    if a.seg_labeled:
        svg = render_seg_labeled(1.6 if a.scale == 2.0 else a.scale)
        out = a.out if a.out.endswith(".svg") else os.path.join(a.out, "7-segment-display_labeled.svg")
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        with open(out, "w") as f:
            f.write(svg)
        to_png(out, out[:-4] + ".png")
        print(f"wrote {out} + .png")
        return

    if a.layout_demo:
        os.makedirs(a.out, exist_ok=True)
        Ls = [f"L{i}" for i in range(10)]
        figs = {
            # default: inputs in creation (scrambled) order on the left, outputs
            # on the right — the disorganized layout CircuitVerse gives you.
            "subcircuit-layout-before": render_subcircuit_box(
                "4-to-10 decoder", left=["B0", "B1", "B3", "B2"], right=Ls,
                bw=196, bh=300, scale=a.scale),
            # organized: inputs B3..B0 on the bottom, outputs L0..L9 on the left.
            "subcircuit-layout-after": render_subcircuit_box(
                "4-to-10 decoder", bottom=["B3", "B2", "B1", "B0"], left=Ls,
                bw=190, bh=300, scale=a.scale),
        }
        for nm, svg in figs.items():
            base = os.path.join(a.out, nm)
            with open(base + ".svg", "w") as f:
                f.write(svg)
            to_png(base + ".svg", base + ".png")
            print(f"wrote {base}.svg + .png")
        return

    if a.gate_intros:
        os.makedirs(a.out, exist_ok=True)
        for ot in GATE_NAMES:
            svg = render_gate_intro(ot, a.scale)
            base = os.path.join(a.out, f"{GATE_NAMES[ot]}-gate_circuitverse")
            with open(base + ".svg", "w") as f:
                f.write(svg)
            to_png(base + ".svg", base + ".png")
            print(f"wrote {base}.svg + .png")
        return

    if a.hero or a.heroes:
        outdir = a.out if (os.path.isdir(a.out) or not a.out.endswith(".svg")) else \
            (os.path.dirname(a.out) or ".")
        os.makedirs(outdir, exist_ok=True)
        types = list(GATE_NAMES) if a.heroes else \
            [NAME_TO_TYPE.get(a.hero.upper(), a.hero)]
        for ot in types:
            svg = render_hero(ot, a.scale)
            if svg is None:
                print(f"skip {ot}: no glyph"); continue
            base = os.path.join(outdir, GATE_NAMES.get(ot, ot))
            with open(base + ".svg", "w") as f:
                f.write(svg)
            if a.png or a.heroes:
                to_png(base + ".svg", base + ".png")
            print(f"wrote {base}.svg" + (" + .png" if a.png or a.heroes else ""))
        return

    if not a.cv:
        sys.exit("need a .cv project file (or use --heroes)")
    proj = load(a.cv)
    by = {s["name"]: s for s in proj["scopes"]}
    SUBCIRCUIT_NAMES.update({str(s.get("id")): s["name"] for s in proj["scopes"]})
    if a.list or (not a.name and not a.batch):
        for n in by:
            print(n)
        return
    if a.batch:
        cfg = load(a.batch)
        defaults = cfg.pop("_defaults", {})
        for key, e in cfg.items():
            e = {**defaults, **e}
            cname = e.get("circuit", key)
            if not e.get("compose") and cname not in by:
                print(f"skip {key}: no circuit '{cname}'"); continue
            outdir = e.get("out", os.path.dirname(a.out) or ".")
            os.makedirs(outdir, exist_ok=True)
            base = os.path.join(outdir, e.get("name", key))
            if e.get("compose"):
                missing = [c for c in e["compose"] if c not in by]
                if missing:
                    print(f"skip {key}: no circuit {missing}"); continue
                parts = [render(by[c], e.get("scale", a.scale),
                                e.get("gate_colors", a.gate_colors), e.get("inputs"))
                         for c in e["compose"]]
                svg = render_compose(parts, e.get("sep", "equiv"), e.get("scale", a.scale))
                with open(base + ".svg", "w") as f:
                    f.write(svg)
                to_png(base + ".svg", base + ".png")
                print(f"wrote {base}.svg + .png (composed)")
                continue
            svg = render(by[cname], e.get("scale", a.scale),
                         e.get("gate_colors", a.gate_colors), e.get("inputs"), e.get("only"))
            with open(base + ".svg", "w") as f:
                f.write(svg)
            to_png(base + ".svg", base + ".png")
            print(f"wrote {base}.svg + .png")
        return
    if a.name not in by:
        sys.exit(f"No circuit '{a.name}'. Use --list.")
    svg = render(by[a.name], a.scale, a.gate_colors)
    with open(a.out, "w") as f:
        f.write(svg)
    print(f"wrote {a.out}")
    if a.png:
        png = a.out[:-4] + ".png" if a.out.endswith(".svg") else a.out + ".png"
        to_png(a.out, png)
        print(f"wrote {png}")


if __name__ == "__main__":
    main()
