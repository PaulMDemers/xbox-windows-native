#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independently verify rung03 reports and private source/GDI pixel captures."""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def decode(raw):
    if len(raw) > 65536 or not raw.endswith(b'end=complete\r\n'):
        raise ValueError('Incomplete or oversized report')
    result = {}
    for line in raw.decode('ascii').splitlines():
        key, value = line.split('=', 1)
        if not key or key in result:
            raise ValueError('Duplicate or empty key')
        result[key] = value
    return result


def expected(stage, kind):
    """Canonical BGR0, independently generated; no guest hashes as oracle."""
    width, height = (128, 112) if kind == 'source' else (256, 192)
    data = bytearray()
    for y in range(height):
        for x in range(width):
            n = ((x // 8) ^ (y // 8) ^ stage) % 8
            rgb = (255 if n & 1 else 0, 255 if n & 2 else 0, 255 if n & 4 else 0)
            if kind != 'source':
                if stage in (1, 2) and 48 <= x < 88 and 40 <= y < 72:
                    rgb = (255, 0, 255)
                elif 16 <= x < 112 and 16 <= y < 96:
                    if kind == 'before':
                        rgb = (0, 0, 0)
                else:
                    rgb = (0, 0, 255)
            data.extend((rgb[2], rgb[1], rgb[0], 0))
    return bytes(data)


def validate(raw, captures, backend, exit_code):
    r = decode(raw)
    def need(key, value):
        if r.get(key) != str(value):
            raise ValueError(f'{key}: expected {value}, found {r.get(key)}')
    def integer(key):
        value = r.get(key, '')
        if not value.isascii() or not value.isdigit() or str(int(value)) != value:
            raise ValueError(f'Invalid integer: {key}')
        return int(value)
    if backend not in ('default', 'hel') or exit_code != 0:
        raise ValueError('Backend/process exit')
    for k, v in dict(schema='xwn-present-2', rung='03', backend=backend,
                     visual='UNVERIFIED', scope='owned-window-gdi-readback',
                     result='PRESENTATION_OK', exit=0, end='complete').items():
        need(k, v)
    for k in ('ddraw.load', 'ddraw.entry', 'window.create', 'clipper.owner', 'ddraw.unload'):
        need(k, 1)
    for k in ('ddraw.create', 'ddraw.cooperative', 'ddraw.mode', 'primary.create',
              'primary.format', 'source.create', 'clipper.create', 'clipper.hwnd',
              'clipper.gethwnd', 'primary.clipper', 'primary.detach'):
        need(k, '00000000')
    for k in ('source', 'primary', 'clipper', 'ddraw'):
        need('release.' + k, 0)
    fmt = tuple(integer('format.' + k) for k in ('flags', 'bits', 'red', 'green', 'blue'))
    if fmt not in ((64, 32, 0xff0000, 0xff00, 255), (64, 16, 0xf800, 0x7e0, 31), (64, 16, 0x7c00, 0x3e0, 31)):
        raise ValueError('Unsupported native format')
    if integer('mode.bpp') != fmt[1] or integer('mode.width') < 640 or integer('mode.height') < 480:
        raise ValueError('Mode/format disagreement')
    for key in ('os.major', 'os.minor', 'os.build'):
        integer(key)
    for stage in range(4):
        prefix = f's{stage}.'
        ox, oy = (64, 64) if stage < 2 else (144, 112)
        need(prefix + 'origin.x', ox); need(prefix + 'origin.y', oy)
        need(prefix + 'cover', int(stage in (1, 2)))
        need(prefix + 'cover.visible', int(stage in (1, 2)))
        need(prefix + 'cover.above', 1)
        if integer(prefix + 'cover.preabove') not in (0, 1):
            raise ValueError('Invalid prior sibling order')
        for key in ('clip.size', 'clip.list', 'source.write.lock', 'source.read.lock',
                    'source.write.unlock', 'source.read.unlock', 'primary.blit'):
            need(prefix + key, '00000000')
        for key in ('clip.exact', 'before.capture', 'after.capture', 'source.write.layout',
                    'source.read.layout', 'source.exact', 'complete'):
            need(prefix + key, 1)
        need(prefix + 'before.mismatches', 0); need(prefix + 'after.mismatches', 0)
        for key in ('source.write.pitch', 'source.read.pitch'):
            pitch = integer(prefix + key)
            if not 128 * (fmt[1] // 8) <= pitch <= 65536 or pitch % (fmt[1] // 8):
                raise ValueError('Invalid pitch')
        count = integer(prefix + 'clip.count')
        if not 1 <= count <= 64:
            raise ValueError('Clip capacity')
        need(prefix + 'clip.bytes', 32 + count * 16)
        coverage = bytearray(96 * 80)
        for i in range(count):
            left, top, right, bottom = (integer(prefix + f'clip.r{i}.' + k)
                                       for k in ('left', 'top', 'right', 'bottom'))
            left -= ox; right -= ox; top -= oy; bottom -= oy
            if not 16 <= left < right <= 112 or not 16 <= top < bottom <= 96:
                raise ValueError('Clip leaks outside owned target')
            for y in range(top, bottom):
                for x in range(left, right):
                    index = (y-16)*96 + x-16
                    if coverage[index]:
                        raise ValueError('Overlapping clip rectangles')
                    coverage[index] = 1
        for y in range(16, 96):
            for x in range(16, 112):
                want = not (stage in (1, 2) and 48 <= x < 88 and 40 <= y < 72)
                if coverage[(y-16)*96+x-16] != want:
                    raise ValueError('Occlusion/clip coverage mismatch')
    total = 0
    for kind in ('source', 'before', 'after'):
        oracle = b''.join(expected(s, kind) for s in range(4))
        if captures.get(kind) != oracle:
            raise ValueError(f'{kind} pixels/length disagree with independent oracle')
        total += len(oracle)
    return dict(passed=True, backend=backend, stages=4, exact_bytes=total,
                display=[integer('mode.width'), integer('mode.height'), fmt[1]],
                report_sha256=hashlib.sha256(raw).hexdigest(), visual='UNVERIFIED',
                scope='Owned source and GDI-observed primary pixels; no GPU/scanout/performance claim')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('prefix', type=Path)
    p.add_argument('--backend', required=True, choices=('default', 'hel'))
    a = p.parse_args(); prefix = str(a.prefix)
    result = validate(Path(prefix+'.txt').read_bytes(),
                      {k:Path(prefix+'-'+k+'.bin').read_bytes() for k in ('source','before','after')},
                      a.backend, int(Path(prefix+'.exit').read_text().strip()))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
