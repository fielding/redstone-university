// Decoder for .rub build files written by scripts/usd_to_scene.py (write_rub).
//
//   gzip( "RUB1" | u32 header_len | header JSON | pad to 4 | arrays... )
//
// Arrays are little-endian typed views; positions are int16 relative to
// header.origin at 1/header.q units.

const TYPES = {
  h: Int16Array, H: Uint16Array, b: Int8Array, B: Uint8Array, I: Uint32Array,
};

async function gunzip(bytes) {
  // a host may already have stripped a transport gzip; the file's own gzip
  // starts with 1f 8b, raw RUB1 does not
  if (bytes[0] !== 0x1f || bytes[1] !== 0x8b) return bytes;
  const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
  return new Uint8Array(await new Response(stream).arrayBuffer());
}

export function decodeRub(bytes) {
  const magic = String.fromCharCode(...bytes.subarray(0, 4));
  if (magic !== 'RUB1') throw new Error(`not a .rub file (magic ${JSON.stringify(magic)})`);
  const dv = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const headLen = dv.getUint32(4, true);
  const header = JSON.parse(new TextDecoder().decode(bytes.subarray(8, 8 + headLen)));
  if (header.version !== 1) throw new Error(`unsupported .rub version ${header.version}`);
  let bodyStart = 8 + headLen;
  while (bodyStart % 4) bodyStart++;
  // copy the body so typed views are aligned regardless of the source offset
  const body = bytes.slice(bodyStart).buffer;

  const view = ([off, count, type]) => new TYPES[type](body, off, count);
  const { origin, q } = header;
  const positions = (spec) => {
    const raw = view(spec);
    const out = new Float32Array(raw.length);
    for (let i = 0; i < raw.length; i++) out[i] = raw[i] / q + origin[i % 3];
    return out;
  };
  const scaled = (spec, k) => {
    const raw = view(spec);
    const out = new Float32Array(raw.length);
    for (let i = 0; i < raw.length; i++) out[i] = raw[i] / k;
    return out;
  };

  const meshes = header.meshes.map((m) => ({
    name: m.name,
    block: m.block,
    role: m.role,
    texture: m.texture,
    displayColor: m.displayColor,
    positions: positions(m.arrays.position),
    normals: scaled(m.arrays.normal, 127),
    uvs: m.arrays.uv ? scaled(m.arrays.uv, 65535) : null,
    indices: view(m.arrays.index),
  }));
  const wires = header.wires && {
    positions: positions(header.wires.arrays.position),
    colors: scaled(header.wires.arrays.color, 255),
    indices: view(header.wires.arrays.index),
  };
  return {
    name: header.name,
    params: header.params,
    bounds: header.bounds,
    bounds_pre: header.bounds_pre,
    fit_boxes: header.fit_boxes,
    band_base_y: header.band_base_y,
    meshes,
    wires,
  };
}

export async function loadRub(url, init) {
  const res = await fetch(url, init);
  if (!res.ok) throw new Error(`${url}: HTTP ${res.status}`);
  return decodeRub(await gunzip(new Uint8Array(await res.arrayBuffer())));
}
