#!/usr/bin/env python3
"""
verify_exports.py: does each cached MiEx export show the redstone state that
is actually saved in the world?

Reads the Java world named by each shot (Anvil region files, stdlib NBT
reader) and compares every redstone component in the shot's bounds with what
the cached USD export carries:

  redstone_wire   powered in the world (power > 0)   <->  dust tint (Cd) > 0.1
  redstone_lamp   lit                                <->  mesh redstone_lamp_on
  redstone_torch  lit (floor and wall torches)        <->  mesh redstone_torch (not _off)
  repeater        powered                            <->  mesh repeater_on
  comparator      powered                            <->  mesh comparator_on

    python3 scripts/verify_exports.py                 # every shot with a cache
    python3 scripts/verify_exports.py 02_NOT-gate --usd-dir /path/to/old/cache

The Bedrock world MiEx exported from in June carried no redstone power, which
is why the live figures for Part I disagreed with the book. This script is
how a re-export is shown to be faithful to the world, not just to the PNGs.
"""
import glob
import json
import math
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import usd_to_scene as u  # noqa: E402  (USD parsing is shared)

REPO = u.REPO


# ------------------------------------------------------------- tiny NBT reader

def _nbt(buf, i, tag):
    if tag == 1:
        return struct.unpack_from(">b", buf, i)[0], i + 1
    if tag == 2:
        return struct.unpack_from(">h", buf, i)[0], i + 2
    if tag == 3:
        return struct.unpack_from(">i", buf, i)[0], i + 4
    if tag == 4:
        return struct.unpack_from(">q", buf, i)[0], i + 8
    if tag == 5:
        return struct.unpack_from(">f", buf, i)[0], i + 4
    if tag == 6:
        return struct.unpack_from(">d", buf, i)[0], i + 8
    if tag == 7:
        n = struct.unpack_from(">i", buf, i)[0]
        return buf[i + 4:i + 4 + n], i + 4 + n
    if tag == 8:
        n = struct.unpack_from(">H", buf, i)[0]
        return buf[i + 2:i + 2 + n].decode("utf-8", "replace"), i + 2 + n
    if tag == 9:
        t, n = buf[i], struct.unpack_from(">i", buf, i + 1)[0]
        i += 5
        out = []
        for _ in range(n):
            v, i = _nbt(buf, i, t)
            out.append(v)
        return out, i
    if tag == 10:
        out = {}
        while True:
            t = buf[i]
            i += 1
            if t == 0:
                return out, i
            n = struct.unpack_from(">H", buf, i)[0]
            name = buf[i + 2:i + 2 + n].decode("utf-8", "replace")
            out[name], i = _nbt(buf, i + 2 + n, t)
    if tag == 11:
        n = struct.unpack_from(">i", buf, i)[0]
        return list(struct.unpack_from(f">{n}i", buf, i + 4)), i + 4 + 4 * n
    if tag == 12:
        n = struct.unpack_from(">i", buf, i)[0]
        return list(struct.unpack_from(f">{n}q", buf, i + 4)), i + 4 + 8 * n
    raise ValueError(f"bad NBT tag {tag}")


def read_chunk(world, cx, cz, cache={}):
    key = (world, cx, cz)
    if key in cache:
        return cache[key]
    path = os.path.join(world, "region", f"r.{cx >> 5}.{cz >> 5}.mca")
    chunk = None
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
        i = (cx & 31) + (cz & 31) * 32
        off = int.from_bytes(data[i * 4:i * 4 + 3], "big") * 4096
        if off:
            n = int.from_bytes(data[off:off + 4], "big")
            raw = zlib.decompress(data[off + 5:off + 4 + n])
            chunk, _ = _nbt(raw, 3 + struct.unpack_from(">H", raw, 1)[0], 10)
    cache[key] = chunk
    return chunk


def block_at(world, x, y, z):
    c = read_chunk(world, x >> 4, z >> 4)
    if not c:
        return "air", {}
    for s in c.get("sections", []):
        if s.get("Y") != y >> 4 or "block_states" not in s:
            continue
        bs = s["block_states"]
        pal = bs["palette"]
        if "data" not in bs:
            e = pal[0]
        else:
            bits = max(4, math.ceil(math.log2(len(pal))))
            per = 64 // bits
            idx = ((y & 15) * 16 + (z & 15)) * 16 + (x & 15)
            word = bs["data"][idx // per] & 0xFFFFFFFFFFFFFFFF
            e = pal[(word >> ((idx % per) * bits)) & ((1 << bits) - 1)]
        return e["Name"].replace("minecraft:", ""), e.get("Properties", {})
    return "air", {}


# --------------------------------------------------------------- comparison

KIND = {"redstone_wire": "dust", "redstone_lamp": "lamp", "redstone_torch": "torch",
        "redstone_wall_torch": "torch", "repeater": "repeater", "comparator": "comparator"}


def world_state(world, b):
    """{(x,y,z): (kind, on)} for redstone components in the inclusive bounds."""
    out = {}
    for y in range(b[1], b[4] + 1):
        for z in range(b[2], b[5] + 1):
            for x in range(b[0], b[3] + 1):
                name, p = block_at(world, x, y, z)
                kind = KIND.get(name)
                if not kind:
                    continue
                if kind == "dust":
                    on = int(p.get("power", "0")) > 0
                elif kind in ("lamp", "torch"):
                    on = p.get("lit") == "true"
                else:
                    on = p.get("powered") == "true"
                out[(x, y, z)] = (kind, on)
    return out


def export_state(usd_path):
    """{(x,y,z): (kind, on)} as the cached export shows it, in world coords."""
    meshes, _ = u.load_usd(usd_path)
    reg = u.parse_region(usd_path)
    ox, oy, oz = reg["offsetX"], reg["offsetY"], reg["offsetZ"]
    out = {}
    for m in meshes:
        n = m["name"].lower()
        if "redstone_dust" in n and "overlay" not in n:
            kind = "dust"
        elif "lamp" in n:
            kind = "lamp"
        elif "redstone_torch" in n:
            kind = "torch"
        elif "repeater" in n:
            kind = "repeater"
        elif "comparator" in n:
            kind = "comparator"
        else:
            continue
        li = 0
        for fi, face in enumerate(m["faces"]):
            pts = [m["points"][v] for v in face]
            c = [sum(p[a] for p in pts) / len(pts) for a in range(3)]
            nrm = u.face_normal(m, fi, face)
            if kind == "dust":
                if abs(nrm[1]) < 0.7:          # wall-climb visuals; flat quads define cells
                    li += len(face)
                    continue
                on = (max(m["cd"][li + j][0] for j in range(len(face))) > 0.1) if m["cd"] else False
                # merged strips: rasterize the quad over every cell it covers
                for bx, bz in u.covered_cells([p[0] for p in pts], [p[2] for p in pts]):
                    key = (bx + ox, math.floor(c[1] / 16) + oy, bz + oz)
                    prev = out.get(key)
                    out[key] = (kind, on or (prev[1] if prev else False))
            else:
                # nudge the face center inward so it lands in its own block
                c = [c[a] - nrm[a] * 0.5 for a in range(3)]
                key = (math.floor((c[0] + 8) / 16) + ox, math.floor(c[1] / 16) + oy,
                       math.floor((c[2] + 8) / 16) + oz)
                on = ("lamp_on" in n) if kind == "lamp" else ("_off" not in n) if kind == "torch" else ("_on" in n)
                out.setdefault(key, (kind, on))
            li += len(face)
    return out


def verify(shot_name, shot, usd_path):
    world = shot["world"]
    b = shot["bounds"]
    # shots.json bounds are min-inclusive, max-exclusive in x/z by convention
    # but exports are made with the same numbers, so read the same box
    w = world_state(world, b)
    e = export_state(usd_path)
    wrong = []
    for pos, (kind, on) in sorted(w.items()):
        got = e.get(pos)
        if got is None:
            continue                     # outside the export (bounds slop) or hidden
        if got[0] == kind and got[1] != on:
            wrong.append((pos, kind, on, got[1]))
    checked = sum(1 for p, (k, _) in w.items() if e.get(p, (None,))[0] == k)
    return checked, wrong


def main():
    args = sys.argv[1:]
    usd_dir = u.USD_CACHE
    if "--usd-dir" in args:
        i = args.index("--usd-dir")
        usd_dir = args[i + 1]
        del args[i:i + 2]
    shots = u.load_shots()
    names = args or sorted(shots)
    total_checked = total_wrong = 0
    for n in names:
        usd = os.path.join(usd_dir, f"{n}.usd")
        if n not in shots or not os.path.exists(usd):
            continue
        checked, wrong = verify(n, shots[n], usd)
        total_checked += checked
        total_wrong += len(wrong)
        flag = "OK  " if not wrong else "DIFF"
        print(f"{flag} {n:40s} {checked:5d} components checked, {len(wrong):4d} differ from the world")
        for pos, kind, want, got in wrong[:3]:
            print(f"       {kind} at {pos}: world {'on' if want else 'off'}, export {'on' if got else 'off'}")
    print(f"\n{total_checked} components checked, {total_wrong} differ from the world")
    sys.exit(1 if total_wrong else 0)


if __name__ == "__main__":
    main()
