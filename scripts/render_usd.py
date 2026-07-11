"""
Render a MiEx USD export to course-ready PNGs, headlessly.

Usage:
    blender -b -P scripts/render_usd.py -- <file.usd> [options]

Options (after the `--`):
    --out DIR          output directory (default: <usd_dir>/<usd_stem>_renders)
    --name PREFIX      output filename prefix (default: usd filename stem)
    --views LIST       comma list of: iso, beauty (default: iso,beauty)
    --res WxH          resolution (default: 1920x1440)
    --samples N        Cycles samples (default: 96)
    --azimuth DEG      camera azimuth for both views (default: 45 iso / 30 beauty)
    --no-trim          keep stray geometry (default: hide geometry clusters far
                       below the build, e.g. the bedrock floor, and frame only
                       the main build)
    --cluster-gap N    vertical gap (world units, 16/block) that splits clusters
                       (default: 64)
    --lighting MODE    override the view's lighting: flat | sun
    --transform NAME   override tonemapping: standard | agx | punchy | filmic
    --glare on|off     override the bloom pass
    --elevation DEG    override camera elevation above the horizon
    --margin F         zoom-out factor around the auto-fit framing (default
                       1.0 = tight fit; 1.3 gives comfortable breathing room)
    --projection P     ortho (default) | tele: long-lens perspective that
                       keeps the isometric feel but restores depth cues —
                       use for dense/deep builds that interlock in pure ortho
    --max-layer N      build-instruction mode: render only the lowest N block
                       layers of the build (camera stays framed on the full
                       build, so successive N values stack like LEGO steps)
    --explode G        exploded axonometric: float each block layer apart by G
                       blocks of vertical space (e.g. 1.5) so you can see what
                       sits on top of what; wires move with their layer
    --outline MODE     off | full (all edges, 1.4px) | thin (all edges, 0.8px)
                       | sil (silhouettes+borders only, 1.2px). 'on' = full.
                       (default off)
    --grid on|off      darken each block texture's border so EVERY block face
                       shows an outline, even across merged flat surfaces
                       (default: on)
    --toon MODE        off (default) | unlit (pure flat albedo colors, no
                       lighting at all) | cel (banded cartoon shading, EEVEE)
    --technical MODE   off (default) | blueprint (navy ground, glowing line
                       art, cyan wires) | cad (white ground, black linework,
                       red wires) | schematic (white line-art structure, but
                       dust stays power-colored and components keep real color
                       — only the circuit carries color). Forces full outlines.
    --swap A=B[,C=D]   retexture block A with block B's texture at render time
                       (e.g. --swap white_wool=white_concrete); names are the
                       vanilla block texture names
    --tint A=RRGGBB[,C=RRGGBB]  recolor blocks whose name contains A toward the
                       hex color (module-legend tinting, e.g. red_wool=4a90d9)
    --hide A[,B]       hide blocks whose name contains A/B from the render
                       (e.g. --hide lime_concrete for a floating, padless look)
    --top-margin F     extra zoom-out for the aerial 'top' view only
                       (default: inherits --margin)
    --dust STYLE       how to draw redstone dust (default: vector)
                       vector    - REPLACE dust geometry with generated wire
                                   ribbons: connection graph computed from
                                   block adjacency, clean elbows, slope ramps,
                                   state-colored with power gradient
                       realistic - lit/shadowed like everything else
                       schematic - shadeless state colors, vanilla speckle
                       solid     - shadeless state colors, clean solid stroke
                       power     - solid stroke colored by power level 0-15

Pipeline context: export a region from MiEx (keep the Y range tight to the
build), then run this to get an orthographic diagram shot and a perspective
beauty shot. See .tix issue ru-7778b0.
"""

import math
import os
import sys

import bpy
from mathutils import Vector


def parse_args():
    argv = sys.argv
    args = argv[argv.index("--") + 1:] if "--" in argv else []
    if not args:
        print(__doc__)
        sys.exit(1)

    opts = {
        "usd": None,
        "out": None,
        "name": None,
        "views": ["iso", "beauty"],
        "res": (1920, 1440),
        "samples": 96,
        "azimuth": None,
        "trim": True,
        "cluster_gap": 64.0,
        "lighting": None,
        "transform": None,
        "glare": None,
        "elevation": None,
        "margin": 1.3,
        "outline": "sil",
        "_outline_set": False,   # True once --outline is given explicitly
        "projection": "ortho",
        "top_azimuth": None,
        "max_layer": None,
        "explode": None,
        "clip": None,
        "ground_no_outline": False,   # opt-in: drop ground layer from the outline pass
        "grid": True,
        "toon": "off",
        "technical": "off",
        "height_tint": 0.5,
        "transparent": False,
        "dust": "vector",
        "swap": {},
        "hide": [],
        "tint": {},
        "top_margin": None,
        "ground": "keep",
    }
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--out":
            i += 1
            opts["out"] = args[i]
        elif a == "--name":
            i += 1
            opts["name"] = args[i]
        elif a == "--views":
            i += 1
            opts["views"] = [v.strip() for v in args[i].split(",") if v.strip()]
        elif a == "--res":
            i += 1
            w, h = args[i].lower().split("x")
            opts["res"] = (int(w), int(h))
        elif a == "--samples":
            i += 1
            opts["samples"] = int(args[i])
        elif a == "--azimuth":
            i += 1
            opts["azimuth"] = float(args[i])
        elif a == "--no-trim":
            opts["trim"] = False
        elif a == "--cluster-gap":
            i += 1
            opts["cluster_gap"] = float(args[i])
        elif a == "--lighting":
            i += 1
            opts["lighting"] = args[i]
        elif a == "--transform":
            i += 1
            opts["transform"] = args[i].lower()
        elif a == "--glare":
            i += 1
            opts["glare"] = args[i].lower() == "on"
        elif a == "--elevation":
            i += 1
            opts["elevation"] = float(args[i])
        elif a == "--margin":
            i += 1
            opts["margin"] = float(args[i])
        elif a == "--projection":
            i += 1
            opts["projection"] = args[i].lower()
        elif a == "--top-azimuth":
            i += 1
            opts["top_azimuth"] = float(args[i])
        elif a == "--ground":
            i += 1
            opts["ground"] = args[i].lower()   # keep | remove | crop
        elif a == "--max-layer":
            i += 1
            opts["max_layer"] = int(args[i])
        elif a == "--explode":
            i += 1
            opts["explode"] = float(args[i])
        elif a == "--clip":
            i += 1
            # "y:0:0.55,x:0.2:1" -> [("y",0.0,0.55),("x",0.2,1.0)] (bbox fractions)
            cl = []
            for part in args[i].split(","):
                ax, lo, hi = part.split(":")
                cl.append((ax.strip(), float(lo), float(hi)))
            opts["clip"] = cl
        elif a == "--ground-no-outline":
            opts["ground_no_outline"] = True
        elif a == "--outline":
            i += 1
            v = args[i].lower()
            opts["outline"] = "full" if v == "on" else (v if v != "off" else False)
            opts["_outline_set"] = True
        elif a == "--grid":
            i += 1
            opts["grid"] = args[i].lower() == "on"
        elif a == "--toon":
            i += 1
            opts["toon"] = args[i].lower()
        elif a == "--technical":
            i += 1
            opts["technical"] = args[i].lower()
        elif a == "--transparent":
            opts["transparent"] = True
        elif a == "--height-tint":
            i += 1
            opts["height_tint"] = float(args[i])
        elif a == "--dust":
            i += 1
            opts["dust"] = args[i].lower()
        elif a == "--swap":
            i += 1
            for pair in args[i].split(","):
                old, _, new = pair.partition("=")
                if old and new:
                    opts["swap"][old.strip()] = new.strip()
        elif a == "--hide":
            i += 1
            opts["hide"] = [s.strip() for s in args[i].split(",") if s.strip()]
        elif a == "--tint":
            i += 1
            for pair in args[i].split(","):
                block, _, hexcol = pair.partition("=")
                if block and hexcol:
                    h = hexcol.strip().lstrip("#")
                    opts["tint"][block.strip()] = tuple(
                        int(h[j:j + 2], 16) / 255 for j in (0, 2, 4))
        elif a == "--top-margin":
            i += 1
            opts["top_margin"] = float(args[i])
        elif not a.startswith("--") and opts["usd"] is None:
            opts["usd"] = os.path.abspath(os.path.expanduser(a))
        else:
            print(f"Unknown argument: {a}")
            sys.exit(1)
        i += 1

    if not opts["usd"] or not os.path.exists(opts["usd"]):
        print(f"USD file not found: {opts['usd']}")
        sys.exit(1)

    stem = os.path.splitext(os.path.basename(opts["usd"]))[0]
    if opts["name"] is None:
        opts["name"] = stem
    if opts["out"] is None:
        opts["out"] = os.path.join(os.path.dirname(opts["usd"]), f"{stem}_renders")
    return opts


# Blocks that emit light in-game: their textures get wired into emission so
# they actually glow in renders (and bloom in the beauty view).
EMISSIVE = {
    "redstone_torch": 14.0,
    "redstone_lamp_on": 8.0,
    "lamp_on": 8.0,
    # NOTE: repeater_on/comparator_on must NOT be here — emitting the whole
    # base texture washes the block to white; their state already shows via
    # the indicator torches (separate geometry, redstone_torch texture).
    "glowstone": 7.0,
    "sea_lantern": 7.0,
    "shroomlight": 6.0,
    "end_rod": 8.0,
    "lava": 5.0,
    "fire": 8.0,
    "soul_fire": 8.0,
    "torch": 10.0,
    "lantern": 9.0,
    "beacon": 8.0,
    "crying_obsidian": 4.0,
    "amethyst_cluster": 4.0,
}


SOLID_DUST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              "renders", "assets")


def swap_to_solid_texture(mat, tex_node):
    """Swap the vanilla speckled dust texture for the generated solid stroke."""
    for part in ("dot", "line0", "line1"):
        if part in mat.name.lower():
            path = os.path.join(SOLID_DUST_DIR, f"redstone_dust_{part}_solid.png")
            if os.path.exists(path):
                tex_node.image = bpy.data.images.load(path, check_existing=True)
                # the strokes are anti-aliased vector shapes, not pixel art
                tex_node.interpolation = 'Linear'
            return


def make_schematic_dust(mat, tex_node, style):
    """
    Replace the dust material with a shadeless, state-readable emission —
    lighting and shadows can't wash it out, circuit-diagram style.
      schematic/solid: state colors (unpowered = matte dark red, powered =
                       vivid red that blooms)
      power:           color ramp by signal strength 0-15
    """
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    output = next(n for n in nodes if n.type == 'OUTPUT_MATERIAL')

    if style in ("solid", "power"):
        swap_to_solid_texture(mat, tex_node)

    attr = nodes.new('ShaderNodeAttribute')
    attr.attribute_name = "Cd"
    # raw tint brightness encodes the power level
    sep = nodes.new('ShaderNodeSeparateColor')
    links.new(attr.outputs["Color"], sep.inputs["Color"])

    if style == "power":
        # signal strength -> flow-readable ramp: unpowered dust is neutral
        # GRAY (present but dead), powered runs red -> hot orange by strength.
        # The brightness gradient along a run shows the direction of flow,
        # like the game does — this is what disambiguates crossings of runs
        # at different power levels.
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = 0.0
        ramp.color_ramp.elements[0].color = (0.30, 0.30, 0.33, 1.0)
        ramp.color_ramp.elements[1].position = 1.0
        ramp.color_ramp.elements[1].color = (1.0, 0.55, 0.10, 1.0)
        e = ramp.color_ramp.elements.new(0.12)
        e.color = (0.45, 0.10, 0.08, 1.0)
        e = ramp.color_ramp.elements.new(0.60)
        e.color = (0.95, 0.15, 0.05, 1.0)
        norm = nodes.new('ShaderNodeMapRange')
        norm.inputs["From Min"].default_value = 0.05
        norm.inputs["From Max"].default_value = 0.95
        links.new(sep.outputs["Red"], norm.inputs["Value"])
        links.new(norm.outputs["Result"], ramp.inputs["Fac"])
        tint_out = ramp.outputs["Color"]
    else:
        # lift the near-black unpowered tint into a readable dark red
        gamma = nodes.new('ShaderNodeGamma')
        gamma.inputs["Gamma"].default_value = 0.42
        links.new(attr.outputs["Color"], gamma.inputs["Color"])
        tint_out = gamma.outputs["Color"]

    # texture pattern x state color = the dust trace
    mix = nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.blend_type = 'MULTIPLY'
    mix.inputs["Factor"].default_value = 1.0
    links.new(tex_node.outputs["Color"], mix.inputs["A"])
    links.new(tint_out, mix.inputs["B"])

    emission = nodes.new('ShaderNodeEmission')
    links.new(mix.outputs["Result"], emission.inputs["Color"])
    # gentle lift on powered dust: state is communicated by COLOR (vivid vs
    # dark red); too much emission blows out and makes line edges look fuzzy
    strength = nodes.new('ShaderNodeMath')
    strength.operation = 'MULTIPLY_ADD'
    links.new(sep.outputs["Red"], strength.inputs[0])
    strength.inputs[1].default_value = 0.8
    strength.inputs[2].default_value = 0.9
    links.new(strength.outputs["Value"], emission.inputs["Strength"])

    transparent = nodes.new('ShaderNodeBsdfTransparent')
    mix_shader = nodes.new('ShaderNodeMixShader')
    links.new(tex_node.outputs["Alpha"], mix_shader.inputs["Fac"])
    links.new(transparent.outputs["BSDF"], mix_shader.inputs[1])
    links.new(emission.outputs["Emission"], mix_shader.inputs[2])
    links.new(mix_shader.outputs["Shader"], output.inputs["Surface"])


def wire_color(power):
    """Map raw Cd power (0..~0.95 linear) to the wire state color."""
    if power < 0.10:
        return (0.12, 0.012, 0.012, 1.0)   # unpowered: matte dark red
    t = min(1.0, max(0.0, (power - 0.05) / 0.90)) ** 0.42
    return (0.25 + 0.75 * t, 0.012 + 0.05 * t, 0.012 + 0.03 * t, 1.0)


def build_vector_wires(scene, dust_objects):
    """
    Replace MiEx's dust geometry with generated wire ribbons.

    Dust block positions and power levels are extracted from the horizontal
    dust quads; connections are recomputed from block adjacency (same level
    4-neighbors plus one-up/one-down slopes, like the game). Each connection
    becomes a flat ribbon between block centers, so the wire network shows
    exactly the real connections — no phantom arms, clean elbows, slope
    ramps, and a per-block power gradient along runs.
    """
    BLOCK = 16.0
    W = 4.6           # ribbon width (~0.29 block)
    LIFT = 0.15       # sit just above the dust plane to avoid z-fighting

    import math as _math
    blocks = {}
    for ob in dust_objects:
        if "overlay" in ob.name.lower():
            # no power data, and MiEx merges its transparent quads into huge
            # sheets that rasterize as phantom dust
            continue
        me = ob.data
        cd = me.color_attributes.get("Cd")
        mw = ob.matrix_world
        nm = mw.to_3x3()
        for poly in me.polygons:
            if abs((nm @ poly.normal).normalized().z) < 0.7:
                continue  # wall-climb visuals; the flat quad defines the block
            # MiEx merges straight runs into long strips — rasterize the
            # quad's footprint into every block it covers, not just its center
            corners = []
            for li in poly.loop_indices:
                v = mw @ me.vertices[me.loops[li].vertex_index].co
                p = cd.data[li].color[0] if cd else 0.0
                corners.append((v, p))
            zs = [c[0].z for c in corners]
            z = sum(zs) / len(zs)
            bz = int(round(z) // BLOCK)
            # the world grid here has block centers at multiples of 16:
            # block b spans [16b-8, 16b+8]
            eps = 0.01
            half = BLOCK / 2
            min_x = min(c[0].x for c in corners) + eps
            max_x = max(c[0].x for c in corners) - eps
            min_y = min(c[0].y for c in corners) + eps
            max_y = max(c[0].y for c in corners) - eps
            for bx in range(_math.floor((min_x + half) / BLOCK), _math.floor((max_x + half) / BLOCK) + 1):
                for by in range(_math.floor((min_y + half) / BLOCK), _math.floor((max_y + half) / BLOCK) + 1):
                    cx = bx * BLOCK
                    cy = by * BLOCK
                    nearest = min(corners,
                                  key=lambda c: (c[0].x - cx) ** 2 + (c[0].y - cy) ** 2)
                    power = nearest[1]
                    key = (bx, by, bz)
                    cur = blocks.get(key)
                    if cur is None or power > cur[0]:
                        blocks[key] = (power, z)

    if not blocks:
        return

    edges = set()
    for (bx, by, bz) in blocks:
        for dx, dy in ((1, 0), (0, 1)):
            n = (bx + dx, by + dy, bz)
            if n in blocks:
                edges.add(((bx, by, bz), n))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (bx + dx, by + dy, bz + 1)
            if n in blocks:
                edges.add(((bx, by, bz), n))

    def center(key):
        power, z = blocks[key]
        return (key[0] * BLOCK, key[1] * BLOCK, z + LIFT)

    from mathutils import Vector as V
    verts, faces, colors = [], [], []

    def add_quad(corners, cols):
        base = len(verts)
        verts.extend(corners)
        faces.append((base, base + 1, base + 2, base + 3))
        colors.extend(cols)

    for a, b in edges:
        pa, pb = V(center(a)), V(center(b))
        ca, cb = wire_color(blocks[a][0]), wire_color(blocks[b][0])
        if a[2] == b[2]:
            d = (pb - pa).normalized()
            side = d.cross(V((0, 0, 1))).normalized() * (W / 2)
            add_quad([pa - side, pa + side, pb + side, pb - side], [ca, ca, cb, cb])
            continue
        # climbing dust renders like the game: flat to the step, a vertical
        # piece up the block face, flat again on top — not a diagonal ramp
        lo, hi = (a, b) if a[2] < b[2] else (b, a)
        cl, ch = (ca, cb) if a[2] < b[2] else (cb, ca)
        plo, phi = V(center(lo)), V(center(hi))
        d = V((phi.x - plo.x, phi.y - plo.y, 0)).normalized()
        side = d.cross(V((0, 0, 1))).normalized() * (W / 2)
        face = V((plo.x, plo.y, 0)) + d * (BLOCK / 2 - LIFT)  # just off the wall
        e_lo = V((face.x, face.y, plo.z))
        e_hi = V((face.x, face.y, phi.z))
        cm = tuple((cl[i] + ch[i]) / 2 for i in range(4))
        add_quad([plo - side, plo + side, e_lo + side, e_lo - side], [cl, cl, cm, cm])
        add_quad([e_lo - side, e_lo + side, e_hi + side, e_hi - side], [cm, cm, cm, cm])
        add_quad([e_hi - side, e_hi + side, phi + side, phi - side], [cm, cm, ch, ch])

    # node patches: cover elbow/junction joints (and isolated dots)
    neighbors = {}
    for a, b in edges:
        neighbors.setdefault(a, []).append(b)
        neighbors.setdefault(b, []).append(a)
    for key in blocks:
        ns = neighbors.get(key, [])
        collinear = (len(ns) == 2 and
                     (ns[0][0] - ns[1][0], ns[0][1] - ns[1][1]) in
                     ((2, 0), (-2, 0), (0, 2), (0, -2)))
        if len(ns) == 2 and collinear:
            continue  # straight-through: ribbon already covers it
        p = V(center(key))
        p.z += 0.02
        h = W / 2
        col = wire_color(blocks[key][0])
        add_quad([p + V((-h, -h, 0)), p + V((h, -h, 0)),
                  p + V((h, h, 0)), p + V((-h, h, 0))], [col] * 4)

    me = bpy.data.meshes.new("RU_Wires")
    me.from_pydata(verts, [], faces)
    attr = me.color_attributes.new("Col", 'FLOAT_COLOR', 'POINT')
    for i, c in enumerate(colors):
        attr.data[i].color = c

    mat = bpy.data.materials.new("RU_Wire")
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    em = nodes.new('ShaderNodeEmission')
    col_node = nodes.new('ShaderNodeVertexColor')
    col_node.layer_name = "Col"
    em.inputs["Strength"].default_value = 1.15
    links.new(col_node.outputs["Color"], em.inputs["Color"])
    links.new(em.outputs["Emission"], out.inputs["Surface"])
    me.materials.append(mat)

    ob = bpy.data.objects.new("RU_Wires", me)
    scene.collection.objects.link(ob)
    print(f"vector wires: {len(blocks)} dust blocks, {len(edges)} connections")

    for d in dust_objects:
        d.hide_render = True


def apply_toon(mode):
    """
    Restyle all block materials after the normal wiring.
      unlit: final base-color chain straight into Emission — pure flat colors.
      cel:   Diffuse -> Shader-to-RGB -> constant 3-band ramp, multiplied by
             the base color (EEVEE only; the render engine is switched there).
    Generated wires (RU_Wire) and schematic dust are already emission-based
    and keep their look.
    """
    for mat in bpy.data.materials:
        if not mat.node_tree or mat.name == "RU_Wire":
            continue
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        principled = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
        output = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL'), None)
        if principled is None or output is None:
            continue
        base = principled.inputs["Base Color"]
        color_out = base.links[0].from_socket if base.is_linked else None
        alpha = principled.inputs["Alpha"]
        alpha_out = alpha.links[0].from_socket if alpha.is_linked else None
        # keep existing emissive blocks emissive
        emissive = principled.inputs["Emission Strength"].default_value > 0.0

        if mode == "unlit":
            shader = nodes.new('ShaderNodeEmission')
            if color_out is not None:
                links.new(color_out, shader.inputs["Color"])
            else:
                shader.inputs["Color"].default_value = base.default_value
            shader.inputs["Strength"].default_value = 2.5 if emissive else 1.0
            final = shader.outputs["Emission"]
        else:  # cel
            diffuse = nodes.new('ShaderNodeBsdfDiffuse')
            to_rgb = nodes.new('ShaderNodeShaderToRGB')
            ramp = nodes.new('ShaderNodeValToRGB')
            ramp.color_ramp.interpolation = 'CONSTANT'
            ramp.color_ramp.elements[0].position = 0.0
            ramp.color_ramp.elements[0].color = (0.45, 0.45, 0.48, 1.0)
            ramp.color_ramp.elements[1].position = 0.35
            ramp.color_ramp.elements[1].color = (0.78, 0.78, 0.80, 1.0)
            e = ramp.color_ramp.elements.new(0.62)
            e.color = (1.0, 1.0, 1.0, 1.0)
            mix = nodes.new('ShaderNodeMix')
            mix.data_type = 'RGBA'
            mix.blend_type = 'MULTIPLY'
            mix.inputs["Factor"].default_value = 1.0
            links.new(diffuse.outputs["BSDF"], to_rgb.inputs["Shader"])
            links.new(to_rgb.outputs["Color"], ramp.inputs["Fac"])
            if color_out is not None:
                links.new(color_out, mix.inputs["A"])
            else:
                mix.inputs["A"].default_value = base.default_value
            links.new(ramp.outputs["Color"], mix.inputs["B"])
            shader = nodes.new('ShaderNodeEmission')
            links.new(mix.outputs["Result"], shader.inputs["Color"])
            shader.inputs["Strength"].default_value = 2.5 if emissive else 1.0
            final = shader.outputs["Emission"]

        if alpha_out is not None:
            transparent = nodes.new('ShaderNodeBsdfTransparent')
            mix_shader = nodes.new('ShaderNodeMixShader')
            links.new(alpha_out, mix_shader.inputs["Fac"])
            links.new(transparent.outputs["BSDF"], mix_shader.inputs[1])
            links.new(final, mix_shader.inputs[2])
            links.new(mix_shader.outputs["Shader"], output.inputs["Surface"])
        else:
            links.new(final, output.inputs["Surface"])


TECHNICAL = {
    "blueprint": {"bg": (0.030, 0.075, 0.26), "fill": (0.11, 0.22, 0.60),
                  "line": (0.78, 0.90, 1.0), "wire": (0.45, 0.95, 1.0), "lw": 1.4},
    "cad":       {"bg": (0.97, 0.97, 0.95), "fill": (0.84, 0.86, 0.89),
                  "line": (0.05, 0.05, 0.07), "wire": (0.85, 0.06, 0.05), "lw": 1.2},
    # height bands interpolate band_lo (ground) -> band_hi (top) across the
    # build's actual layer count, so the full lightness range always spans
    # darkest-to-lightest no matter how many layers there are. A single cool
    # hue (light) / warm stone (dark) keeps them from competing with the red.
    # Each layer has a fixed HUE identity (ground neutral, then amber, sage,
    # dusty blue, mauve, terracotta, ochre) so layers are distinct and the
    # light/dark themes match: same per-layer colors, rendered as soft pastels
    # on light or deeper earthy tones on dark. Muted to stay candlelit and
    # not fight the red dust.
    # per-layer distinct hues (neutral, amber, sage, dusty-blue, rose,
    # terracotta, ochre). The isometric depth read is handled by AO contact
    # shadows, so the colors are free to just mark layers distinctly.
    "schematic": {"bg": (1.0, 1.0, 1.0), "fill": (0.94, 0.94, 0.95),
                  "line": (0.06, 0.06, 0.08), "wire": None, "lw": 1.2,
                  "band_palette": [(0.96, 0.96, 0.97), (0.99, 0.91, 0.73),
                                   (0.82, 0.89, 0.78), (0.80, 0.86, 0.90),
                                   (0.94, 0.84, 0.83), (0.98, 0.86, 0.77),
                                   (0.93, 0.91, 0.76)]},
    "schematic_dark": {"bg": (0.095, 0.082, 0.072), "fill": (0.26, 0.23, 0.19),
                       "line": (0.88, 0.83, 0.74), "wire": None, "lw": 1.2,
                       "band_palette": [(0.30, 0.27, 0.22), (0.60, 0.45, 0.21),
                                        (0.34, 0.50, 0.34), (0.30, 0.46, 0.58),
                                        (0.46, 0.37, 0.53), (0.60, 0.39, 0.28),
                                        (0.53, 0.50, 0.28)]},
    # "aged vellum": warm parchment ground, sepia ink lines, warm aged layer
    # tints — illuminated-manuscript LIGHT theme (ancient-university + legible)
    "schematic_vellum": {"bg": (0.93, 0.88, 0.78), "fill": (0.90, 0.85, 0.74),
                         "line": (0.27, 0.19, 0.12), "wire": None, "lw": 1.2,
                         "band_palette": [(0.91, 0.86, 0.76), (0.93, 0.80, 0.48),
                                          (0.73, 0.82, 0.65), (0.69, 0.79, 0.87),
                                          (0.89, 0.73, 0.72), (0.91, 0.73, 0.54),
                                          (0.82, 0.80, 0.57)]},
    # "illuminated manuscript": gilded ink lines on warm vellum-black, aged
    # jewel-tone layers (oxblood/bottle-green/brass/teal/aubergine)
    "schematic_gilded": {"bg": (0.085, 0.070, 0.058), "fill": (0.28, 0.24, 0.19),
                         "line": (0.83, 0.67, 0.38), "wire": None, "lw": 1.3,
                         "band_palette": [(0.32, 0.27, 0.21), (0.55, 0.44, 0.20),
                                          (0.27, 0.42, 0.34), (0.26, 0.40, 0.50),
                                          (0.45, 0.30, 0.32), (0.50, 0.40, 0.22),
                                          (0.40, 0.30, 0.42)]},
}

# ambient-occlusion contact shadows on schematic fills (depth cue for iso)
_AO_ENABLED = True

# redstone components kept in real color against ghosted white structure
COMPONENT_KW = ("torch", "lever", "repeater", "comparator", "lamp", "button",
                "redstone_block", "observer", "target", "tripwire", "piston",
                "dispenser", "dropper", "note_block", "rail")

# circuit geometry is never "ground": generated wire ribbons, MiEx dust quads,
# and component meshes must survive ground stripping even though flat builds
# put them inside the lowest 16-unit band (dust sits ~0.2 units above the
# floor it rests on)
CIRCUIT_KW = ("ru_wires", "redstone_dust") + COMPONENT_KW


def _flat_fill(nodes, links, em, rgb, htint=None):
    """
    Emission fill faintly shaded by face-normal Z (tops brighter than sides).
    If htint=(base_z, nlayers, strength) is given, the fill color is also
    tinted by the block's layer (warm-white at the ground -> cool blue up top)
    so vertical position reads at a glance — quantized per 16-unit layer.
    """
    geo = nodes.new('ShaderNodeNewGeometry')
    sep = nodes.new('ShaderNodeSeparateXYZ')
    links.new(geo.outputs["Normal"], sep.inputs["Vector"])
    mr = nodes.new('ShaderNodeMapRange')
    mr.inputs["From Min"].default_value = -1.0
    mr.inputs["From Max"].default_value = 1.0
    mr.inputs["To Min"].default_value = 0.80
    mr.inputs["To Max"].default_value = 1.05
    links.new(sep.outputs["Z"], mr.inputs["Value"])

    if htint is not None:
        base_z, nlayers, strength, band = htint
        psep = nodes.new('ShaderNodeSeparateXYZ')
        links.new(geo.outputs["Position"], psep.inputs["Vector"])
        # layer index = floor((Z - base - 0.5)/16); top faces resolve to their
        # own block, hidden bottom faces to the one below (invisible)
        sub = nodes.new('ShaderNodeMath'); sub.operation = 'SUBTRACT'
        links.new(psep.outputs["Z"], sub.inputs[0]); sub.inputs[1].default_value = base_z + 0.5
        div = nodes.new('ShaderNodeMath'); div.operation = 'DIVIDE'
        links.new(sub.outputs["Value"], div.inputs[0]); div.inputs[1].default_value = 16.0
        flr = nodes.new('ShaderNodeMath'); flr.operation = 'FLOOR'
        links.new(div.outputs["Value"], flr.inputs[0])
        nrm = nodes.new('ShaderNodeMath'); nrm.operation = 'DIVIDE'
        links.new(flr.outputs["Value"], nrm.inputs[0]); nrm.inputs[1].default_value = max(1.0, nlayers - 1.0)
        # distinct per-layer bands (constant interpolation) so each relative
        # layer reads as its own color, not a near-identical gradient step
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.interpolation = 'CONSTANT'
        els = ramp.color_ramp.elements
        n = max(2, min(len(band), int(nlayers)))
        # CONSTANT ramp: a stop at position p colors the range [p, next). To
        # land band i on layer i (nrm = i/(n-1)), place stops just below i/(n-1).
        els[0].position = 0.0
        els[0].color = (*band[0], 1.0)
        els[1].position = 0.5 / (n - 1)
        els[1].color = (*band[1], 1.0)
        for i in range(2, n):
            e = els.new((i - 0.5) / (n - 1))
            e.color = (*band[i], 1.0)
        links.new(nrm.outputs["Value"], ramp.inputs["Fac"])
        # blend the tint toward the base fill by (1-strength) so it stays subtle
        blend = nodes.new('ShaderNodeMix'); blend.data_type = 'RGBA'
        blend.inputs["Factor"].default_value = strength
        blend.inputs["A"].default_value = (*rgb[:3], 1.0)
        links.new(ramp.outputs["Color"], blend.inputs["B"])
        tint = nodes.new('ShaderNodeMix'); tint.data_type = 'RGBA'
        tint.blend_type = 'MULTIPLY'; tint.inputs["Factor"].default_value = 1.0
        links.new(blend.outputs["Result"], tint.inputs["A"])
        # reuse the normal shade as a scalar->gray multiply
        links.new(mr.outputs["Result"], tint.inputs["B"])  # scalar broadcast
        color_out = tint.outputs["Result"]
    else:
        mul = nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'
        mul.blend_type = 'MULTIPLY'; mul.inputs["Factor"].default_value = 1.0
        mul.inputs["A"].default_value = (*rgb[:3], 1.0)
        links.new(mr.outputs["Result"], mul.inputs["B"])
        color_out = mul.outputs["Result"]

    # Ambient occlusion: contact shadows in crevices give the depth cue that
    # flat isometric throws away — disambiguates what's stacked on what.
    if _AO_ENABLED:
        ao = nodes.new('ShaderNodeAmbientOcclusion')
        ao.samples = 8
        ao.inputs["Distance"].default_value = 11.0
        aomap = nodes.new('ShaderNodeMapRange')
        aomap.inputs["To Min"].default_value = 0.45   # fully occluded -> 45%
        aomap.inputs["To Max"].default_value = 1.0
        links.new(ao.outputs["AO"], aomap.inputs["Value"])
        aomul = nodes.new('ShaderNodeMix'); aomul.data_type = 'RGBA'
        aomul.blend_type = 'MULTIPLY'; aomul.inputs["Factor"].default_value = 1.0
        links.new(color_out, aomul.inputs["A"])
        links.new(aomap.outputs["Result"], aomul.inputs["B"])
        color_out = aomul.outputs["Result"]

    links.new(color_out, em.inputs["Color"])
    em.inputs["Strength"].default_value = 1.0


def _emit_texture(nodes, links, em, output):
    """Emit a component's own texture flatly (real colors, no lighting needed),
    preserving cutout alpha (torches, levers) via a transparent mix."""
    tex = next((n for n in nodes if n.type == 'TEX_IMAGE'), None)
    if tex is None:
        return False
    links.new(tex.outputs["Color"], em.inputs["Color"])
    em.inputs["Strength"].default_value = 1.15
    transparent = nodes.new('ShaderNodeBsdfTransparent')
    mix = nodes.new('ShaderNodeMixShader')
    links.new(tex.outputs["Alpha"], mix.inputs["Fac"])
    links.new(transparent.outputs["BSDF"], mix.inputs[1])
    links.new(em.outputs["Emission"], mix.inputs[2])
    links.new(mix.outputs["Shader"], output.inputs["Surface"])
    return True


def _srgb_lin(c):
    """sRGB(display) -> scene-linear, so authored palette colors render as the
    intended display tone under the Standard view transform (otherwise dark
    values get lifted by the output gamma)."""
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
                 for v in c[:3])


def apply_technical(mode, height_tint=0.0, tints=None):
    """
    Reskin the scene as a technical drawing with full per-block outlines.
    blueprint/cad: everything flat-filled in one palette.
    schematic: structure blocks ghosted to white line-art while redstone
    components keep their real color and the dust wires stay power-colored —
    only the circuit carries color.
    height_tint>0 tints structure fills by block layer (warm white at the
    ground -> cool blue up top) so vertical position reads at a glance.
    """
    cfg = TECHNICAL[mode]
    htint = None
    if height_tint > 0.0:
        zs = [(ob.matrix_world @ Vector(c)).z
              for ob in bpy.data.objects if ob.type == 'MESH' and not ob.hide_render
              for c in ob.bound_box]
        if zs:
            base_z, top_z = min(zs), max(zs)
            # Blender colorbands hard-cap at 32 elements; huge bboxes (e.g. MiEx
            # padding an export to full region files) crash past it
            nlayers = min(32, max(2, round((top_z - base_z) / 16.0)))
            if "band_palette" in cfg:
                pal = cfg["band_palette"]
                bands_lin = [_srgb_lin(pal[i % len(pal)]) for i in range(nlayers)]
            else:
                lo, hi = cfg["band_lo"], cfg["band_hi"]
                bands_lin = [_srgb_lin(tuple(lo[c] + (hi[c] - lo[c]) * (i / (nlayers - 1))
                                             for c in range(3)))
                             for i in range(nlayers)]
            htint = (base_z, nlayers, height_tint, bands_lin)
            print(f"height tint: {nlayers} layers over {top_z - base_z:.0f} units")
    world = bpy.data.worlds.new("TechWorld")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (*_srgb_lin(cfg["bg"]), 1.0)
    bg.inputs[1].default_value = 1.0

    for mat in bpy.data.materials:
        if not mat.node_tree:
            continue
        name = mat.name.lower()
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        output = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL'), None)
        if output is None:
            continue

        schem = mode.startswith("schematic")
        if mat.name == "RU_Wire":
            if schem:
                continue  # keep the colored power-gradient wires
            em = nodes.new('ShaderNodeEmission')
            em.inputs["Color"].default_value = (*_srgb_lin(cfg["wire"]), 1.0)
            em.inputs["Strength"].default_value = 1.5
            links.new(em.outputs["Emission"], output.inputs["Surface"])
            continue

        if mat.name.startswith("RU_GroundPads"):
            # synthesized base layer (ground crop): warm cream to match the
            # Part I bottoms (decided 2026-07-09) — unless the pad replaced a
            # block family that carries a legend tint, in which case the
            # region's base wears the region color
            fam = mat.name.partition("|")[2].lower()
            rgb = None
            if tints and fam:
                m = max((k for k in tints if k.lower() in fam),
                        key=len, default=None)
                if m is not None:
                    rgb = tints[m]
            if rgb is None:
                pal = cfg.get("band_palette")
                rgb = pal[1] if pal else cfg["fill"]
            em = nodes.new('ShaderNodeEmission')
            _flat_fill(nodes, links, em, _srgb_lin(rgb))
            links.new(em.outputs["Emission"], output.inputs["Surface"])
            continue

        if schem and any(k in name for k in COMPONENT_KW):
            em = nodes.new('ShaderNodeEmission')
            if _emit_texture(nodes, links, em, output):
                continue
            # no texture: fall through to a colored fill so it still stands out
            _flat_fill(nodes, links, em, (0.6, 0.6, 0.62))
            links.new(em.outputs["Emission"], output.inputs["Surface"])
            continue

        # Legend tint beats the generic structure fill (but never overrides
        # redstone components above — circuit state must stay readable).
        # Longest matching key wins so "light_blue_wool" beats "blue_wool".
        if tints:
            match = max((k for k in tints if k.lower() in name),
                        key=len, default=None)
            if match is not None:
                em = nodes.new('ShaderNodeEmission')
                _flat_fill(nodes, links, em, _srgb_lin(tints[match]))
                links.new(em.outputs["Emission"], output.inputs["Surface"])
                continue

        em = nodes.new('ShaderNodeEmission')
        _flat_fill(nodes, links, em, _srgb_lin(cfg["fill"]), htint)
        links.new(em.outputs["Emission"], output.inputs["Surface"])
    return cfg


def hide_material(mat):
    """Make a material fully transparent (used for the dust overlay layer)."""
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    output = next(n for n in nodes if n.type == 'OUTPUT_MATERIAL')
    transparent = nodes.new('ShaderNodeBsdfTransparent')
    links.new(transparent.outputs["BSDF"], output.inputs["Surface"])


VANILLA_TEXTURES = os.path.expanduser(
    "~/apps/MiEx/resources/base_resource_pack/assets/minecraft/textures/block")


def apply_block_swaps(mat, tex_node, swaps):
    """Retexture a block material with another block's vanilla texture."""
    name = mat.name.lower()
    for old, new in swaps.items():
        if old.lower() in name:
            path = os.path.join(VANILLA_TEXTURES, f"{new}.png")
            if not os.path.exists(path):
                print(f"swap target texture not found: {path}")
                return
            tex_node.image = bpy.data.images.load(path, check_existing=True)
            return


def add_block_grid(image, factor=0.62):
    """
    Darken the texture's outer pixel ring. Block textures tile once per block
    face — even on MiEx's merged quads, UVs repeat per block — so this draws
    a consistent outline on every block in the scene.
    """
    import numpy as np
    w, h = image.size
    if w == 0 or h == 0:
        return
    px = np.array(image.pixels[:], dtype=np.float32).reshape(h, w, 4)
    b = max(1, w // 16)
    px[:b, :, :3] *= factor
    px[-b:, :, :3] *= factor
    px[:, :b, :3] *= factor
    px[:, -b:, :3] *= factor
    image.pixels[:] = px.ravel()


def import_and_prepare(usd_path, dust_style="schematic", swaps=None, grid=False,
                       mark_edges=True, tints=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.usd_import(filepath=usd_path)
    print(f"Imported {len(bpy.data.objects)} objects")
    gridded = set()

    for mat in bpy.data.materials:
        if not mat.node_tree:
            continue
        nodes = mat.node_tree.nodes
        # Minecraft textures need nearest-neighbor filtering to stay pixel-crisp.
        tex_node = None
        for node in nodes:
            if node.type == 'TEX_IMAGE':
                node.interpolation = 'Closest'
                tex_node = tex_node or node
        name = mat.name.lower()
        principled = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if principled is None or tex_node is None:
            continue
        links = mat.node_tree.links
        color_out = tex_node.outputs["Color"]

        # MiEx bakes biome/power tints (grass green, redstone-dust red) into a
        # 'Cd' color primvar; the UsdPreviewSurface materials don't apply it,
        # so multiply it in here.
        if swaps and tex_node is not None:
            apply_block_swaps(mat, tex_node, swaps)

        if "redstone_dust" in name and dust_style != "realistic":
            if dust_style == "vector":
                pass  # geometry replaced wholesale after this loop
            elif "biome" in name:
                make_schematic_dust(mat, tex_node, dust_style)
            elif "overlay" in name and dust_style in ("solid", "power"):
                # the untinted overlay speckle just adds noise on solid strokes
                hide_material(mat)
            continue

        if grid and tex_node is not None and tex_node.image is not None:
            if tex_node.image.name not in gridded:
                gridded.add(tex_node.image.name)
                try:
                    add_block_grid(tex_node.image)
                except Exception as ex:
                    print(f"grid failed for {tex_node.image.name}: {ex}")

        emission_color_out = None
        if "biome" in name:
            attr = nodes.new('ShaderNodeAttribute')
            attr.attribute_name = "Cd"
            tint_out = attr.outputs["Color"]
            # Dust legibility: the unpowered power-tint is nearly black
            # (Cd ~0.07) which renders invisible against pale blocks. Lift the
            # dark end (gamma < 1) so unpowered dust reads as a clear red while
            # powered dust stays bright. Emission stays tied to the RAW tint
            # below, so only powered dust glows — the on/off state must remain
            # readable in course images.
            if "redstone_dust" in name:
                gamma = nodes.new('ShaderNodeGamma')
                gamma.inputs["Gamma"].default_value = 0.42
                links.new(tint_out, gamma.inputs["Color"])
                tint_out = gamma.outputs["Color"]
                raw_mix = nodes.new('ShaderNodeMix')
                raw_mix.data_type = 'RGBA'
                raw_mix.blend_type = 'MULTIPLY'
                raw_mix.inputs["Factor"].default_value = 1.0
                links.new(color_out, raw_mix.inputs["A"])
                links.new(attr.outputs["Color"], raw_mix.inputs["B"])
                emission_color_out = raw_mix.outputs["Result"]
            mix = nodes.new('ShaderNodeMix')
            mix.data_type = 'RGBA'
            mix.blend_type = 'MULTIPLY'
            mix.inputs["Factor"].default_value = 1.0
            links.new(color_out, mix.inputs["A"])
            links.new(tint_out, mix.inputs["B"])
            links.new(mix.outputs["Result"], principled.inputs["Base Color"])
            color_out = mix.outputs["Result"]

        # Component tinting: recolor whole block families toward a legend
        # color (e.g. blue_concrete=a8c4d6 turns a data lane course dusty-blue).
        # Longest matching key wins so "red_wool" beats "wool"; the mix keeps
        # 15% texture so the block grid stays readable.
        if tints:
            match = max((k for k in tints if k.lower() in name),
                        key=len, default=None)
            if match is not None:
                tmix = nodes.new('ShaderNodeMix')
                tmix.data_type = 'RGBA'
                tmix.blend_type = 'MIX'
                tmix.inputs["Factor"].default_value = 0.85
                links.new(color_out, tmix.inputs["A"])
                tmix.inputs["B"].default_value = (*_srgb_lin(tints[match]), 1.0)
                links.new(tmix.outputs["Result"], principled.inputs["Base Color"])
                color_out = tmix.outputs["Result"]

        # Wire emissive block textures into the Principled emission socket.
        # OFF/unlit variants must never glow: the lit-vs-unlit contrast is how
        # component state is read in course images.
        strength = 0.0
        if "_off" not in name and "unlit" not in name:
            for key, val in EMISSIVE.items():
                if key in name:
                    strength = max(strength, val)
        # Tinted redstone dust: emission follows the RAW power tint — powered
        # dust (bright red Cd) glows, unpowered (near-black Cd) stays matte.
        if "redstone_dust" in name and "biome" in name:
            strength = max(strength, 8.0)
        if strength > 0.0:
            links.new(emission_color_out or color_out, principled.inputs["Emission Color"])
            principled.inputs["Emission Strength"].default_value = strength

    if dust_style == "vector":
        dust_objects = [ob for ob in bpy.data.objects
                        if ob.type == 'MESH' and "redstone_dust" in ob.name.lower()]
        if dust_objects:
            build_vector_wires(bpy.context.scene, dust_objects)

    if mark_edges:   # per-block seam marks are only used by full/thin outlines
        mark_block_edges()


def object_bounds(ob):
    corners = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    zs = [c.z for c in corners]
    return corners, min(zs), max(zs)


def scene_bounds(scene, trim, cluster_gap):
    """
    Returns (center, size, fit_coords) of the geometry to frame.

    MiEx exports often drag along the world floor (bedrock/ground) far below
    the actual build because the export Y-range defaults wide. When trim is
    on, meshes are grouped into clusters of overlapping Z-intervals; clusters
    separated by more than cluster_gap are considered disconnected, and only
    the cluster with the most meshes (ties: topmost) is framed — the rest are
    hidden from the render.
    """
    meshes = []
    for ob in scene.objects:
        if ob.type != 'MESH' or ob.hide_render:
            continue
        corners, z0, z1 = object_bounds(ob)
        meshes.append({"ob": ob, "corners": corners, "z0": z0, "z1": z1})
    if not meshes:
        print("ERROR: no mesh geometry imported")
        sys.exit(1)

    keep = meshes
    if trim and len(meshes) > 1:
        # merge Z-intervals into clusters
        meshes.sort(key=lambda m: m["z0"])
        clusters = [[meshes[0]]]
        cluster_top = meshes[0]["z1"]
        for m in meshes[1:]:
            if m["z0"] <= cluster_top + cluster_gap:
                clusters[-1].append(m)
                cluster_top = max(cluster_top, m["z1"])
            else:
                clusters.append([m])
                cluster_top = m["z1"]
        # most meshes wins; on a tie, the topmost cluster
        best = max(clusters, key=lambda c: (len(c), max(m["z1"] for m in c)))
        if len(clusters) > 1:
            dropped = [m for c in clusters if c is not best for m in c]
            for m in dropped:
                m["ob"].hide_render = True
            names = sorted({m["ob"].name.rsplit(".", 1)[0] for m in dropped})
            print(f"Trimmed {len(dropped)} stray mesh(es) outside the build cluster: {', '.join(names[:6])}")
            keep = best

    min_v = Vector((1e18, 1e18, 1e18))
    max_v = Vector((-1e18, -1e18, -1e18))
    coords = []
    for m in keep:
        for w in m["corners"]:
            coords.extend([w.x, w.y, w.z])
            min_v.x = min(min_v.x, w.x); min_v.y = min(min_v.y, w.y); min_v.z = min(min_v.z, w.z)
            max_v.x = max(max_v.x, w.x); max_v.y = max(max_v.y, w.y); max_v.z = max(max_v.z, w.z)
    center = (min_v + max_v) / 2
    size = (max_v - min_v).length
    print(f"framed bbox min={tuple(round(v,1) for v in min_v)} max={tuple(round(v,1) for v in max_v)} size={size:.1f}")
    return center, size, coords


def setup_lighting(scene, mode, cam_azimuth=45.0):
    """
    'flat' — bright, even, near-shadowless: matches vanilla in-game screenshot
    lighting for course diagram shots.
    'sun'  — warm directional key with soft shadows for beauty shots.
    """
    for ob in list(scene.objects):
        if ob.type == 'LIGHT':
            bpy.data.objects.remove(ob, do_unlink=True)

    if scene.world is None:
        world = bpy.data.worlds.new("World")
        scene.world = world
        world.use_nodes = True
    bg = scene.world.node_tree.nodes["Background"]

    sun_data = bpy.data.lights.new("Sun", type='SUN')
    sun = bpy.data.objects.new("Sun", sun_data)
    scene.collection.objects.link(sun)

    if mode == 'flat':
        # bright and even, but with a defined soft shadow: multi-level dust
        # runs are indistinguishable without depth cues, so shadows are
        # load-bearing for circuit legibility. 'Standard' view transform:
        # AgX desaturates flat-lit textures into a washed-out look.
        set_transform(scene, 'standard')
        bg.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        bg.inputs[1].default_value = 0.55
        sun_data.energy = 1.35
        sun_data.color = (1.0, 1.0, 0.98)
        sun_data.angle = math.radians(10)
        # key light follows the camera, offset 30° so faces model instead of
        # washing out under dead-frontal light
        sun.rotation_euler = (math.radians(25), 0, math.radians(cam_azimuth + 30.0))
    else:
        set_transform(scene, 'punchy')
        bg.inputs[0].default_value = (0.85, 0.88, 0.95, 1.0)
        bg.inputs[1].default_value = 0.55
        sun_data.energy = 3.5
        sun_data.color = (1.0, 0.96, 0.9)
        sun_data.angle = math.radians(15)
        sun.rotation_euler = (math.radians(50), 0, math.radians(cam_azimuth - 15.0))


TRANSFORMS = {
    "standard": ('Standard', 'None'),
    "agx": ('AgX', 'None'),
    "punchy": ('AgX', 'AgX - Punchy'),
    "filmic": ('Filmic', 'None'),
}


def set_transform(scene, name):
    view_transform, look = TRANSFORMS[name]
    scene.view_settings.view_transform = view_transform
    try:
        scene.view_settings.look = look
    except TypeError:
        pass


def setup_glare(scene, enabled):
    """Compositor bloom so emissive redstone components glow (Blender 5 API)."""
    if not enabled:
        scene.compositing_node_group = None
        return
    ng = bpy.data.node_groups.get("RU_Glare")
    if ng is None:
        ng = bpy.data.node_groups.new("RU_Glare", 'CompositorNodeTree')
        ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
        rl = ng.nodes.new('CompositorNodeRLayers')
        glare = ng.nodes.new('CompositorNodeGlare')
        glare.inputs['Type'].default_value = 'Bloom'
        glare.inputs['Threshold'].default_value = 1.2
        glare.inputs['Strength'].default_value = 0.6
        glare.inputs['Size'].default_value = 0.55
        out = ng.nodes.new('NodeGroupOutput')
        ng.links.new(rl.outputs['Image'], glare.inputs['Image'])
        ng.links.new(glare.outputs['Image'], out.inputs['Image'])
    scene.compositing_node_group = ng


def mark_block_edges():
    """
    Freestyle-mark every mesh edge that lies on a block-grid plane so block
    seams outline individually (needs runOptimiser=false exports — merged
    geometry has no seam edges to mark). Grid: x/y boundaries at 16b+8,
    z boundaries at 16b.
    """
    marked = 0
    for ob in bpy.data.objects:
        if ob.type != 'MESH' or ob.name == "RU_Wires":
            continue
        me = ob.data
        mw = ob.matrix_world
        coords = [mw @ v.co for v in me.vertices]
        attr = me.attributes.get("freestyle_edge")
        if attr is None:
            attr = me.attributes.new("freestyle_edge", 'BOOLEAN', 'EDGE')
        for i, e in enumerate(me.edges):
            c1, c2 = coords[e.vertices[0]], coords[e.vertices[1]]
            for ax, phase in ((0, 8.0), (1, 8.0), (2, 0.0)):
                u1, u2 = c1[ax], c2[ax]
                if abs(u1 - u2) > 0.01:
                    continue
                r = (u1 + phase) % 16.0
                if r < 0.05 or r > 15.95:
                    attr.data[i].value = True
                    marked += 1
                    break
    print(f"block-seam edges marked: {marked}")


def explode_layers(scene, base_z, gap_blocks):
    """
    Exploded axonometric, grouped by block layer: every column is sliced at
    each 16-unit height and each face is assigned to the block layer it
    belongs to (using its normal so top/bottom faces resolve to the right
    layer), then the whole layer is fanned up by layer*gap. Unlike grouping
    by connected island, a multi-block tower splits across tiers instead of
    moving as one lump. Operates in world space (survives MiEx's rotation).
    """
    import bmesh, math as _m
    gap = gap_blocks * 16.0
    for ob in list(scene.objects):
        if ob.type != 'MESH' or ob.hide_render:
            continue
        mw = ob.matrix_world
        mwi = mw.inverted()
        nm = mw.to_3x3()
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        # disconnect every face so layers can move independently (no shared
        # verts to tear between tiers)
        bmesh.ops.split_edges(bm, edges=bm.edges[:])
        bm.faces.ensure_lookup_table()
        for f in bm.faces:
            c = mw @ f.calc_center_median()
            n = (nm @ f.normal).normalized()
            key_z = c.z + (-0.5 if n.z > 0.5 else 0.5 if n.z < -0.5 else 0.0)
            layer = max(0, _m.floor((key_z - base_z) / 16.0))
            if layer == 0:
                continue
            dz = layer * gap
            for v in f.verts:
                w = mw @ v.co
                w.z += dz
                v.co = mwi @ w
        bm.to_mesh(ob.data)
        bm.free()
    print(f"exploded by layer: {gap_blocks} block gap per tier")


def slice_above_layer(scene, fit_coords, max_layer):
    """
    Delete all geometry above the build's lowest `max_layer` block layers
    (16 units per layer). Applies to block meshes AND the generated wires, so
    dust on removed layers disappears too. Call after the camera is fitted —
    framing stays constant across successive layer renders.
    """
    import bmesh
    base_z = min(fit_coords[2::3])
    thr = base_z + max_layer * 16.0 + 1.0
    removed = 0
    for ob in list(scene.objects):
        if ob.type != 'MESH' or ob.hide_render:
            continue
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        mw = ob.matrix_world
        doomed = [f for f in bm.faces if (mw @ f.calc_center_median()).z > thr]
        if doomed:
            removed += len(doomed)
            bmesh.ops.delete(bm, geom=doomed, context='FACES')
            bm.to_mesh(ob.data)
        bm.free()
    print(f"max-layer {max_layer}: removed {removed} faces above z={thr:.1f}")


def clip_geometry(scene, fit_coords, clips):
    """Cutaway: keep only the geometry within fractional ranges of the build's
    bounding box. `clips` is a list of (axis, lo, hi) with axis in x/y/z and
    lo/hi in [0,1]. e.g. ('y',0.0,0.55) keeps the back 55% along Y — slice the
    front off to peek inside. Call after the camera is fitted so framing holds."""
    import bmesh
    AX = {"x": 0, "y": 1, "z": 2}
    xs, ys, zs = fit_coords[0::3], fit_coords[1::3], fit_coords[2::3]
    lo_w = [min(xs), min(ys), min(zs)]
    span = [max(xs) - lo_w[0], max(ys) - lo_w[1], max(zs) - lo_w[2]]
    planes = []  # (axis_idx, world_lo, world_hi)
    for ax, lo, hi in clips:
        i = AX[ax]
        planes.append((i, lo_w[i] + span[i] * lo, lo_w[i] + span[i] * hi))
    removed = 0
    for ob in list(scene.objects):
        if ob.type != 'MESH' or ob.hide_render:
            continue
        bm = bmesh.new(); bm.from_mesh(ob.data); mw = ob.matrix_world
        # delete VERTICES outside the range (takes their faces with them, and
        # updates the bounding box so the frame tightens to what remains)
        doomed = [v for v in bm.verts
                  if any((mw @ v.co)[i] < a or (mw @ v.co)[i] > b for i, a, b in planes)]
        if doomed:
            removed += len(doomed)
            bmesh.ops.delete(bm, geom=doomed, context='VERTS')
            bm.to_mesh(ob.data)
        bm.free()
        ob.data.update()
    bpy.context.view_layer.update()   # refresh ob.bound_box so reframing tightens
    print(f"clip {clips}: removed {removed} verts")


def strip_ground(scene, mode, base_z):
    """Handle the flat base layer the circuit sits on (the platform that often
    overhangs the circuit footprint).
      remove: delete the lowest block layer entirely (circuit sits on its own base)
      crop:   delete the TRUE ground and generate a clean base block under every
              cell the build occupies — the ground is treated as if it were just
              the block the circuit sits on. Reproduces the hand-lift-and-export
              look of the Part I figures (full bottom blocks, floating build)
              without touching the world; bare ground vanishes.
    Circuit geometry (CIRCUIT_KW) is never deleted: flat dust and the generated
    wire ribbons live inside the lowest band, and stripping them used to gut
    on-ground builds. Buried ground has no side faces in a MiEx export, so crop
    synthesizes full cubes instead of keeping original faces.
    `base_z` must be the build's real base (call AFTER stray bedrock is trimmed).
    Re-frame after calling so the frame tightens to what remains."""
    if mode not in ("remove", "remove2", "crop"):
        return
    import bmesh
    import math as _math
    from mathutils import Matrix
    BLOCK = 16.0
    layers = 2 if mode == "remove2" else 1    # remove2 also drops the base block
    band_top = base_z + layers * BLOCK + 1.0  # everything in the lowest layer(s)

    def is_circuit(ob):
        nm = ob.name.lower()
        return any(k in nm for k in CIRCUIT_KW)

    if mode == "crop":
        # The resting plane: the block-grid plane the lowest circuit geometry
        # sits on. Depending on the export's minY this differs from base_z —
        # bounds starting AT the dust level leave the true ground as a paper
        # thin face sheet at base_z (dust ~0.25 above it), while bounds one
        # block lower include the full ground layer (dust ~BLOCK above).
        # Clamped to at most one layer above base_z so a mistaken crop on a
        # pad-built build can't eat the build itself.
        circ_z = [(ob.matrix_world @ v.co).z
                  for ob in scene.objects
                  if ob.type == 'MESH' and not ob.hide_render and is_circuit(ob)
                  for v in ob.data.vertices]
        rest = _math.floor((min(circ_z) - base_z) / BLOCK) * BLOCK + base_z \
            if circ_z else base_z + BLOCK
        rest = max(base_z, min(rest, base_z + BLOCK))
        band_top = rest + 1.0

    def covered_cells(xs, ys):
        # every block cell an AABB overlaps (centers at multiples of BLOCK,
        # cell b spans [16b-8, 16b+8]); eps keeps shared edges out
        eps = 0.01
        for bx in range(_math.floor((min(xs) + eps + BLOCK / 2) / BLOCK),
                        _math.floor((max(xs) - eps + BLOCK / 2) / BLOCK) + 1):
            for by in range(_math.floor((min(ys) + eps + BLOCK / 2) / BLOCK),
                            _math.floor((max(ys) - eps + BLOCK / 2) / BLOCK) + 1):
                yield (bx, by)

    footprint = set()
    if mode == "crop":
        # every cell occupied by the build itself: any geometry above the
        # ground band, plus circuit geometry inside it (flat dust, wire
        # ribbons). AABB rasterization so MiEx's merged strips count fully.
        for ob in scene.objects:
            if ob.type != 'MESH' or ob.hide_render:
                continue
            circuit = is_circuit(ob)
            mw = ob.matrix_world
            me = ob.data
            for poly in me.polygons:
                c = mw @ poly.center
                if c.z > band_top or circuit:
                    pts = [mw @ me.vertices[v].co for v in poly.vertices]
                    footprint.update(covered_cells([p.x for p in pts],
                                                   [p.y for p in pts]))
    removed = 0
    cell_src = {}   # crop: cell -> (z, block family) of the topmost deleted face
    for ob in list(scene.objects):
        if ob.type != 'MESH' or ob.hide_render or is_circuit(ob):
            continue
        nm = ob.name.lower()
        bm = bmesh.new(); bm.from_mesh(ob.data); mw = ob.matrix_world
        doomed = []
        for f in bm.faces:
            c = mw @ f.calc_center_median()
            if c.z <= band_top:
                doomed.append(f)
                if mode == "crop":
                    pts = [mw @ v.co for v in f.verts]
                    for cell in covered_cells([p.x for p in pts],
                                              [p.y for p in pts]):
                        if cell not in cell_src or c.z > cell_src[cell][0]:
                            cell_src[cell] = (c.z, nm)
        if doomed:
            removed += len(doomed)
            bmesh.ops.delete(bm, geom=doomed, context='FACES')
            bm.to_mesh(ob.data)
        bm.free()
    if mode == "crop" and footprint:
        # synthesize the build's bottom layer: one clean cube per occupied
        # cell, in place of the deleted ground. Each pad remembers the block
        # family it replaced (topmost deleted face wins, so a build's own
        # base course shadows the world ground) — a legend tint can then
        # color a region's base the same as the region instead of cream.
        groups = {}
        for cell in footprint:
            groups.setdefault(cell_src.get(cell, (0, ""))[1], []).append(cell)
        for fam, cells in groups.items():
            bm = bmesh.new()
            for (bx, by) in cells:
                bmesh.ops.create_cube(
                    bm, size=BLOCK,
                    matrix=Matrix.Translation((bx * BLOCK, by * BLOCK,
                                               rest - BLOCK / 2)))
            suffix = f"|{fam}" if fam else ""
            me = bpy.data.meshes.new(f"RU_GroundPads{suffix}")
            bm.to_mesh(me)
            bm.free()
            # per-block seams: the import-time edge-mark pass already ran, so
            # mark the generated cubes' edges ourselves (freestyle_edge
            # attribute — same mechanism as mark_block_edges)
            attr = me.attributes.new("freestyle_edge", 'BOOLEAN', 'EDGE')
            for i in range(len(me.edges)):
                attr.data[i].value = True
            mat = bpy.data.materials.new(f"RU_GroundPads{suffix}")
            mat.use_nodes = True
            bsdf = next((n for n in mat.node_tree.nodes
                         if n.type == 'BSDF_PRINCIPLED'), None)
            if bsdf is not None:
                bsdf.inputs["Base Color"].default_value = (0.92, 0.92, 0.93, 1.0)
            me.materials.append(mat)
            pads = bpy.data.objects.new(f"RU_GroundPads{suffix}", me)
            scene.collection.objects.link(pads)
        print(f"ground crop: {len(footprint)} base blocks generated in "
              f"{len(groups)} region groups (resting plane z={rest:.0f})")
    print(f"ground {mode}: removed {removed} faces (base z={base_z:.1f})")


def outline_exclude_collection():
    """
    Collection of glowing/colored objects (components + dust wires) to keep
    OUT of the Freestyle outline pass — a light outline haloing a lit lamp
    looks wrong; let components read by their own color/texture instead.
    """
    coll = bpy.data.collections.get("RU_NoOutline")
    if coll is None:
        coll = bpy.data.collections.new("RU_NoOutline")
        bpy.context.scene.collection.children.link(coll)
    for ob in bpy.data.objects:
        if ob.type != 'MESH':
            continue
        n = ob.name.lower()
        if ob.name == "RU_Wires" or any(k in n for k in COMPONENT_KW):
            if ob.name not in coll.objects:
                coll.objects.link(ob)
    return coll


def exclude_ground_from_outline(coll, base_z):
    """Add objects that live entirely in the bottom block layer (the kept/cropped
    ground platform) to the no-outline collection, so a zoomed-out build's floor
    doesn't drown in a grid of per-block outlines. The build above still outlines."""
    BLOCK, n = 16.0, 0
    top = base_z + BLOCK + 1.0
    for ob in bpy.data.objects:
        if ob.type != 'MESH' or ob.hide_render or ob.name in coll.objects:
            continue
        zs = [(ob.matrix_world @ v.co).z for v in ob.data.vertices]
        if zs and max(zs) <= top:          # whole object sits in the ground layer
            coll.objects.link(ob); n += 1
    if n:
        print(f"ground excluded from outline: {n} object(s)")
    return n


def setup_outlines(scene, mode, exclude=None):
    """Freestyle silhouette lines — separates overlapping levels in iso."""
    scene.render.use_freestyle = bool(mode)
    if not mode:
        return
    width = {"full": 1.4, "thin": 0.8, "sil": 1.2}.get(mode, 1.4)
    scene.render.line_thickness = width
    vl = bpy.context.view_layer
    vl.use_freestyle = True
    fs = vl.freestyle_settings
    for ls in list(fs.linesets):
        fs.linesets.remove(ls)
    ls = fs.linesets.new("outline")
    ls.select_silhouette = True
    # 'sil' = outer silhouette only (clean for zoomed-out builds); full/thin add
    # per-block borders, creases, and block-seam edge marks (the dense schematic
    # linework that drowns a large build's ground in a grid).
    ls.select_border = (mode != "sil")
    ls.select_crease = (mode != "sil")
    ls.select_edge_mark = (mode != "sil")
    if exclude is not None:
        ls.select_by_collection = True
        ls.collection = exclude
        ls.collection_negation = 'EXCLUSIVE'   # outline everything NOT in it
    ls.linestyle.color = (0.08, 0.07, 0.07)
    ls.linestyle.thickness = width


def setup_render(scene, res, samples):
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type = 'METAL'
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        scene.cycles.device = 'GPU'
        print("Using Metal GPU")
    except Exception as e:
        print("GPU setup failed, using CPU:", e)


def make_camera(scene, name, elevation_deg, azimuth_deg, ortho, center, size, fit_coords, margin=1.0, tele=False):
    cam_data = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cam_data)
    scene.collection.objects.link(cam)
    cam.rotation_euler = (math.radians(90 - elevation_deg), 0, math.radians(azimuth_deg))
    if tele:
        # long lens: near-isometric look with just enough perspective for depth
        ortho = False
        cam_data.lens = 110.0
    elif ortho:
        cam_data.type = 'ORTHO'
    deps = bpy.context.evaluated_depsgraph_get()
    loc, fit_scale = cam.camera_fit_coords(deps, fit_coords)
    cam.location = loc
    if ortho:
        # camera_fit_coords under-fits when the content aspect differs a lot
        # from the render aspect (it can crop the long axis of a wide flat
        # build). Compute the true contain-fit in camera space and never go
        # below it; max() keeps existing well-behaved framings identical.
        rot_inv = cam.rotation_euler.to_matrix().inverted()
        pts = [rot_inv @ Vector(fit_coords[i:i + 3])
               for i in range(0, len(fit_coords), 3)]
        w = max(p.x for p in pts) - min(p.x for p in pts)
        h = max(p.y for p in pts) - min(p.y for p in pts)
        rx, ry = scene.render.resolution_x, scene.render.resolution_y
        # sensor_fit AUTO: ortho_scale spans the larger render dimension
        need = max(w, h * rx / ry) if rx >= ry else max(h, w * ry / rx)
        print(f"ortho fit: content {w:.0f}x{h:.0f} units, "
              f"fit_scale={fit_scale:.0f}, contain={need:.0f}")
        cam_data.ortho_scale = max(fit_scale, need) * 1.05 * margin
    else:
        direction = (loc - center).normalized()
        cam.location = loc + direction * size * (0.08 + 0.6 * (margin - 1.0))
    cam_data.clip_start = 0.1
    cam_data.clip_end = size * 20
    return cam


VIEWS = {
    # name: (elevation above horizon, default azimuth, orthographic, lighting, glare)
    "iso": (35.264, 45.0, True, 'flat', False),
    "top": (90.0, 0.0, True, 'flat', False),    # aerial plan: wires read as a schematic
    "beauty": (28.0, 30.0, False, 'sun', True),
}


def main():
    opts = parse_args()
    # per-block seam marks are only consumed by full/thin outlines; skip the
    # expensive edge walk for beauty/sil/off renders (huge on large builds).
    _mark = opts["outline"] in ("full", "thin", "on") or (
        opts["technical"] != "off" and not opts["_outline_set"])
    import_and_prepare(opts["usd"], opts["dust"], opts["swap"], opts["grid"], _mark,
                       tints=opts["tint"])
    if opts["hide"]:
        import re as _re
        subs = [h for h in opts["hide"] if not h.startswith("=")]
        exact = {h[1:] for h in opts["hide"] if h.startswith("=")}  # "=stone" -> exact block id

        FACE = ("_top", "_bottom", "_side", "_front", "_back", "_end", "_inner", "_outer")

        def _bid(name):  # "minecraft_block_stone.001" -> "stone"
            b = _re.sub(r"\.\d+$", "", name.lower())
            return b[len("minecraft_block_"):] if b.startswith("minecraft_block_") else b

        def _core(bid):  # strip a MiEx face suffix so "deepslate_top" -> "deepslate"
            for s in FACE:                # but "deepslate_bricks" stays itself
                if bid.endswith(s):
                    return bid[:-len(s)]
            return bid
        n = 0
        for ob in bpy.data.objects:
            if ob.type != 'MESH':
                continue
            nm = ob.name.lower()
            bid = _bid(nm)
            if any(h in nm for h in subs) or bid in exact or _core(bid) in exact:
                ob.hide_render = True
                n += 1
        print(f"hid {n} object(s) (subs={subs}, exact={sorted(exact)})")
    if opts["toon"] != "off":
        apply_toon(opts["toon"])
    scene = bpy.context.scene
    # trim stray geometry (bedrock/ground) FIRST so the technical height-tint
    # measures the build, not the world floor far below
    center, size, fit_coords = scene_bounds(scene, opts["trim"], opts["cluster_gap"])
    # remove/crop the flat base platform, then re-frame to what remains
    if opts["ground"] in ("remove", "remove2", "crop"):
        strip_ground(scene, opts["ground"], min(fit_coords[2::3]))
        center, size, fit_coords = scene_bounds(scene, opts["trim"], opts["cluster_gap"])
    tech = None
    if opts["technical"] != "off":
        ht = opts["height_tint"] if opts["technical"].startswith("schematic") else 0.0
        tech = apply_technical(opts["technical"], ht, tints=opts["tint"])
        if not opts["_outline_set"]:
            opts["outline"] = "full"   # per-block linework is the default schematic look
        opts["grid"] = False       # outlines carry the seams; grid muddies fills
    if opts["clip"] is not None:
        clip_geometry(scene, fit_coords, opts["clip"])
        center, size, fit_coords = scene_bounds(scene, opts["trim"], opts["cluster_gap"])
    if opts["max_layer"] is not None:
        slice_above_layer(scene, fit_coords, opts["max_layer"])
    if opts["explode"] is not None:
        explode_layers(scene, min(fit_coords[2::3]), opts["explode"])
        center, size, fit_coords = scene_bounds(scene, False, opts["cluster_gap"])
    setup_render(scene, opts["res"], opts["samples"])
    if tech is not None:
        # show the technical background unless a transparent cutout is wanted
        scene.render.film_transparent = opts["transparent"]
    if opts["toon"] == "cel":
        # Shader-to-RGB is EEVEE-only
        try:
            scene.render.engine = 'BLENDER_EEVEE_NEXT'
        except TypeError:
            scene.render.engine = 'BLENDER_EEVEE'
        scene.eevee.taa_render_samples = 64

    os.makedirs(opts["out"], exist_ok=True)
    for view in opts["views"]:
        if view not in VIEWS:
            print(f"Unknown view '{view}' (choices: {', '.join(VIEWS)})")
            continue
        elevation, azimuth, ortho, lighting, glare = VIEWS[view]
        if view == "top":
            # plan view keeps the build squared to the frame — it does NOT
            # inherit the iso azimuth; override with --top-azimuth if needed.
            # Default: orient the build's long axis horizontally.
            if opts["top_azimuth"] is not None:
                azimuth = opts["top_azimuth"]
            else:
                xs, ys = fit_coords[0::3], fit_coords[1::3]
                if (max(ys) - min(ys)) > (max(xs) - min(xs)):
                    azimuth = 90.0
        else:
            if opts["azimuth"] is not None:
                azimuth = opts["azimuth"]
            if opts["elevation"] is not None:
                elevation = opts["elevation"]
        if opts["lighting"] is not None:
            lighting = opts["lighting"]
        if opts["glare"] is not None:
            glare = opts["glare"]
        if tech is None:
            setup_lighting(scene, lighting, azimuth)
            if opts["transform"] is not None:
                set_transform(scene, opts["transform"])
        else:
            set_transform(scene, 'standard')   # exact palette colors, emission self-lit
        # dark schematic: bloom so the circuit (dust, lamps) glows on dark
        if opts["technical"] == "schematic_dark":
            glare = True
        setup_glare(scene, glare)
        tech_excl = outline_exclude_collection() if (tech is not None and opts["technical"].startswith("schematic")) else None
        if (tech_excl is not None and opts["outline"] and opts["ground_no_outline"]
                and opts["ground"] in ("keep", "crop")):
            exclude_ground_from_outline(tech_excl, min(fit_coords[2::3]))
        setup_outlines(scene, opts["outline"], tech_excl)
        if tech is not None and opts["outline"]:
            for ls in bpy.context.view_layer.freestyle_settings.linesets:
                if ls.linestyle:
                    ls.linestyle.color = _srgb_lin(tech["line"])
                    ls.linestyle.thickness = tech["lw"]
        tele = (view == "iso" and opts["projection"] == "tele")
        margin = opts["margin"]
        if view == "top" and opts["top_margin"] is not None:
            margin = opts["top_margin"]
        cam = make_camera(scene, f"Cam_{view}", elevation, azimuth, ortho, center, size, fit_coords, margin, tele)
        scene.camera = cam
        if opts["outline"] and ortho and not tele:
            # constant pixel width reads heavy on large builds: scale the line
            # width with zoom so outlines weigh the same relative to a block
            ref = 370.0  # ortho_scale where 1.2px looks right (the XOR shot)
            w = max(0.5, min(1.6, 1.2 * ref / cam.data.ortho_scale))
            scene.render.line_thickness = w
            for ls in bpy.context.view_layer.freestyle_settings.linesets:
                ls.linestyle.thickness = w
        elif opts["outline"] and tele:
            # perspective has no single ortho_scale to key off; the build is
            # framed to fill, so a fixed weight matching the ortho cap keeps
            # the schematic outline crisp at near-iso depth
            w = 1.5
            scene.render.line_thickness = w
            for ls in bpy.context.view_layer.freestyle_settings.linesets:
                ls.linestyle.thickness = w
        out_path = os.path.join(opts["out"], f"{opts['name']}_{view}.png")
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        print(f"wrote {out_path}")


main()
