#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independent rung04 raw-index/packed-pixel, palette and GDI oracle."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

FORMATS = {'index8': 8, 'rgb565': 16, 'rgb32': 32}
KINDS = ('source', 'dest', 'rgb', 'palette')


def decode(raw):
    if len(raw) > 65536 or not raw.endswith(b'end=complete\r\n'):
        raise ValueError('Incomplete or oversized report')
    result = {}
    for line in raw.decode('ascii').splitlines():
        key, value = line.split('=', 1)
        if not key or key in result:
            raise ValueError('Duplicate/empty key')
        result[key] = value
    return result


def oracle(fmt):
    """Model rectangles and overlapping copies with immutable Python snapshots."""
    if fmt not in FORMATS:
        raise ValueError('Unknown format')
    masks = (0xf800, 0x7e0, 31) if fmt == 'rgb565' else (0xff0000, 0xff00, 255)
    def packed(n):
        return sum(mask for bit, mask in enumerate(masks) if n & (1 << bit))
    source = [[0 if (x+y) % 5 == 0 else (1+(3*x+7*y) % 15 if fmt == 'index8'
               else packed(1+(3*x+5*y) % 7)) for x in range(16)] for y in range(12)]
    dest = [[200 if fmt == 'index8' else packed(5) for x in range(32)] for y in range(24)]
    result = {k: bytearray() for k in KINDS}
    def words(rows):
        return b''.join(struct.pack('<I', v) for row in rows for v in row)
    for stage in range(4):
        if stage == 0:
            for y in range(24):
                for x in range(32):
                    if 5 <= y < 15 and (6 <= x < 12 or 14 <= x < 19):
                        value = source[y-4][x-4]
                        if value != 0:
                            dest[y][x] = value
        elif stage in (2, 3):
            sx, sy, dx, dy = (4, 4, 7, 6) if stage == 2 else (7, 6, 3, 3)
            old = [row[:] for row in dest]
            for y in range(12):
                dest[dy+y][dx:dx+16] = old[sy+y][sx:sx+16]
        phase = int(stage > 0)
        palette = [((17*i+61*phase) % 256, (29*i+37*phase) % 256,
                    (43*i+19*phase) % 256, 0) for i in range(256)]
        result['source'] += words(source)
        result['dest'] += words(dest)
        rgb = []
        for row in dest:
            converted = []
            for v in row:
                channels = palette[v][:3] if fmt == 'index8' else tuple(255 if v & mask else 0 for mask in masks)
                converted.append((channels[0] << 16) | (channels[1] << 8) | channels[2])
            rgb.append(converted)
        result['rgb'] += words(rgb)
        if fmt == 'index8':
            result['palette'] += bytes(v for entry in palette for v in entry)
    return {k: bytes(v) for k, v in result.items()}


def requirements(backend, fmt):
    """Exact report contract; captures are verified independently below."""
    r = dict(schema='xwn-sprites-2', rung='04', backend=backend, format=fmt,
             scope='owned-system-memory', visual='UNVERIFIED', result='SPRITES_OK', exit=0,
             **{'os.major': 5, 'os.minor': 0, 'os.build': 2195})
    for k in ('ddraw.load', 'ddraw.entry', 'window.create', 'ddraw.unload', 'clipper.exact'):
        r[k] = 1
    for k in ('ddraw.create', 'ddraw.cooperative', 'ddraw.mode', 'source.create', 'dest.create',
              'key.set', 'key.get', 'clipper.create', 'clipper.set', 'clipper.get', 'dest.clipper'):
        r[k] = '00000000'
    for k in ('cleanup.clipper.attached', 'key.low', 'key.high', 'release.source', 'release.dest', 'release.clipper', 'release.ddraw'):
        r[k] = 0
    if fmt == 'index8':
        for k in ('palette.create', 'source.palette', 'dest.palette', 'cleanup.source.palette', 'cleanup.dest.palette'):
            r[k] = '00000000'
        r['release.palette'] = 0
    for stage in range(4):
        p = f's{stage}.'
        for label in ('source.read', 'dest.read') + (('source.write', 'dest.write') if stage == 0 else ()):
            r[p+label+'.lock'] = r[p+label+'.unlock'] = '00000000'
            r[p+label+'.layout'] = 1
            if label.endswith('read'):
                r[p+label+'.mismatches'] = 0
        r[p+'gdi.getdc'] = r[p+'gdi.releasedc'] = '00000000'
        r[p+'gdi.capture'] = r[p+'complete'] = 1
        r[p+'gdi.mismatches'] = 0
        if fmt == 'index8':
            r[p+'palette.get'] = '00000000'
            r[p+'palette.exact'] = 1
    r['s0.blit.keyed'] = r['s2.clipper.detach'] = '00000000'
    r['s2.blit.overlap'] = r['s3.blit.overlap'] = '00000000'
    r['s1.palette.set' if fmt == 'index8' else 's1.palette.not_applicable'] = '00000000' if fmt == 'index8' else 1
    r['end'] = 'complete'
    return r


def validate(raw, captures, backend, fmt, exit_code):
    if backend not in ('default', 'hel') or fmt not in FORMATS or exit_code != 0:
        raise ValueError('Backend/format/process exit')
    r = decode(raw)
    required = requirements(backend, fmt)
    for k, v in required.items():
        if r.get(k) != str(v):
            raise ValueError(f'{k}: expected {v}, found {r.get(k)}')
    def integer(k):
        v = r.get(k, '')
        if not v.isascii() or not v.isdigit() or str(int(v)) != v:
            raise ValueError('Invalid integer: '+k)
        return int(v)
    if integer('mode.width') < 640 or integer('mode.height') < 480 or integer('mode.bpp') not in (16, 32):
        raise ValueError('Display mode')
    allowed = set(required) | {'mode.width', 'mode.height', 'mode.bpp'}
    for stage in range(4):
        for label in ('source.read', 'dest.read') + (('source.write', 'dest.write') if stage == 0 else ()):
            key = f's{stage}.{label}.pitch'
            allowed.add(key)
            pitch = integer(key)
            width = 16 if label.startswith('source') else 32
            if not width*(FORMATS[fmt]//8) <= pitch <= 65536 or pitch % (FORMATS[fmt]//8):
                raise ValueError('Pitch: '+key)
    if set(r) != allowed or set(captures) != set(KINDS):
        raise ValueError('Unexpected/missing fields or captures')
    expected = oracle(fmt)
    for k in KINDS:
        if captures[k] != expected[k]:
            raise ValueError('Pixel/palette bytes: '+k)
    return dict(passed=True, backend=backend, format=fmt, stages=4,
                exact_bytes=sum(map(len, captures.values())),
                sha256={k: hashlib.sha256(v).hexdigest() for k, v in captures.items()},
                scope='Owned offscreen bytes and GDI conversion; not scanout, GPU or game qualification')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('prefix', type=Path)
    p.add_argument('--backend', choices=('default', 'hel'), required=True)
    p.add_argument('--format', choices=tuple(FORMATS), required=True)
    a = p.parse_args()
    prefix = str(a.prefix)
    result = validate(Path(prefix+'.txt').read_bytes(),
                      {k: Path(prefix+'-'+k+'.bin').read_bytes() for k in KINDS},
                      a.backend, a.format, int(Path(prefix+'.exit').read_text()))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
