#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Lossless FATX name preflight. Never shorten, substitute or alias a name.

The caller must verify the installed Windows OEM code page. CP437 is supported
for the English NT5 profile; this is not a claim of arbitrary Unicode storage.
The disk format's limit is encoded bytes, not Python character count.
"""
import argparse
import json
from pathlib import Path


def encode_component(name, oemcp):
    if oemcp != 437:
        raise ValueError('Unvalidated OEM code page')
    if not isinstance(name, str) or name in ('', '.', '..'):
        raise ValueError('Empty or relative component')
    if any(ord(c) < 32 or ord(c) == 127 or c in '\\/:*?"<>|' for c in name):
        raise ValueError('Invalid FATX component character')
    try:
        raw = name.encode('cp437', errors='strict')
    except UnicodeError as exc:
        raise ValueError('Not losslessly encodable in OEM CP437') from exc
    if raw.decode('cp437') != name:
        raise ValueError('OEM conversion is not reversible')
    if not 1 <= len(raw) <= 42:
        raise ValueError('FATX component exceeds 42 encoded bytes')
    return raw


def check_path(path, oemcp):
    if not isinstance(path, str) or path.startswith(('/', '\\')):
        raise ValueError('Expected relative Windows installation path')
    parts = path.replace('\\', '/').split('/')
    return [encode_component(part, oemcp) for part in parts]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path, help='JSON array of objects containing path')
    parser.add_argument('--oemcp', required=True, type=int)
    args = parser.parse_args()
    rows = json.loads(args.manifest.read_text(encoding='utf-8'))
    result = []
    for row in rows:
        try:
            parts = check_path(row['path'], args.oemcp)
            result.append(dict(path=row['path'],representable=True,component_bytes=[len(v) for v in parts]))
        except ValueError as exc:
            result.append(dict(path=row['path'],representable=False,reason=str(exc)))
    print(json.dumps(dict(paths=result,lossless_names=all(v['representable'] for v in result)),indent=2))
    return 0 if all(v['representable'] for v in result) else 2


if __name__ == '__main__':
    raise SystemExit(main())
