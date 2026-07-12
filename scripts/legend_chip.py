"""
Render legend chip blocks: one flat-hue cube per requested color, through the
same visual language as the figures (iso camera, flat emission fill, Freestyle
ink outline with inner edges) so a chip is indistinguishable from a block
lifted out of a render — a single block floating on transparency.

Usage (called by shots.py when a shot's "legend" needs missing chips):
    blender -b -P scripts/legend_chip.py -- --out renders/out/chips f2d489 aecf9c
"""
import math
import os
import sys

import bpy
from mathutils import Vector

INK = (0.08, 0.07, 0.07)
RES = 320             # chips are pasted at ~44px; 320 downsamples cleanly
THICKNESS = 12.0      # ~4.6% of the block's on-screen size, matching figures
BLOCK = 16.0


def _srgb_lin(c):
    return tuple((v / 12.92) if v <= 0.04045 else (((v + 0.055) / 1.055) ** 2.4)
                 for v in c)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    out_dir = argv[argv.index("--out") + 1]
    hexes = [a for a in argv if a != out_dir and not a.startswith("--")]
    os.makedirs(out_dir, exist_ok=True)

    scene = bpy.context.scene
    for ob in list(scene.objects):
        bpy.data.objects.remove(ob, do_unlink=True)

    bpy.ops.mesh.primitive_cube_add(size=BLOCK)
    cube = bpy.context.object
    # Blender 5.x: freestyle marks live in an attribute layer (same
    # mechanism render_usd.py uses for generated pads)
    attr = cube.data.attributes.new("freestyle_edge", 'BOOLEAN', 'EDGE')
    for i in range(len(cube.data.edges)):
        attr.data[i].value = True

    mat = bpy.data.materials.new("RU_Chip")
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    em = nodes.new('ShaderNodeEmission')
    outn = nodes.new('ShaderNodeOutputMaterial')
    links.new(em.outputs["Emission"], outn.inputs["Surface"])
    cube.data.materials.append(mat)

    cam = bpy.data.cameras.new("ChipCam")
    cam.type = 'ORTHO'
    cam.ortho_scale = BLOCK * 1.85
    co = bpy.data.objects.new("ChipCam", cam)
    scene.collection.objects.link(co)
    # same iso as VIEWS["iso"] in render_usd.py: elevation 35.264, azimuth 45
    el, az = math.radians(35.264), math.radians(45.0)
    d = 200.0
    co.location = (d * math.cos(el) * math.sin(az),
                   -d * math.cos(el) * math.cos(az),
                   d * math.sin(el))
    co.rotation_euler = (Vector((0, 0, 0)) - co.location) \
        .to_track_quat('-Z', 'Y').to_euler()
    scene.camera = co

    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 16
    scene.render.film_transparent = True
    scene.render.resolution_x = scene.render.resolution_y = RES
    scene.view_settings.view_transform = 'Standard'
    scene.render.use_freestyle = True
    scene.render.line_thickness_mode = 'ABSOLUTE'
    scene.render.line_thickness = 1.0
    vl = scene.view_layers[0]
    vl.use_freestyle = True
    fs = vl.freestyle_settings
    ls = fs.linesets.new("chip")
    ls.select_silhouette = True
    ls.select_border = False
    ls.select_crease = True
    ls.select_edge_mark = True
    ls.linestyle.color = INK
    ls.linestyle.thickness = THICKNESS

    world = bpy.data.worlds.new("ChipWorld")
    scene.world = world

    for hx in hexes:
        rgb = tuple(int(hx[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
        em.inputs["Color"].default_value = (*_srgb_lin(rgb), 1.0)
        em.inputs["Strength"].default_value = 1.0
        scene.render.filepath = os.path.join(out_dir, f"{hx.lower()}.png")
        bpy.ops.render.render(write_still=True)
        print(f"wrote {scene.render.filepath}")


main()
