#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Identify a local ISO against recorded bytes; never installs or modifies it."""
import argparse
import hashlib
import json
from pathlib import Path


def identify(path, manifest):
    hashes = {name: hashlib.new(name) for name in ('sha256', 'sha1')}
    size = 0
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            size += len(block)
            for h in hashes.values():
                h.update(block)
    result = {'bytes': size, **{name: h.hexdigest() for name, h in hashes.items()}}
    if manifest.get('schema') != 1:
        raise ValueError('Unknown media manifest schema')
    matches = [row for row in manifest['media']
               if row['bytes'] == size and row['sha256'] == result['sha256']]
    if len(matches) > 1:
        raise ValueError('Ambiguous duplicate media identity')
    result['recognized'] = bool(matches)
    result['validation'] = matches[0]['validation'] if matches else {'status': 'unvalidated'}
    result['media_id'] = matches[0]['id'] if matches else None
    result['scope'] = 'Byte identity only; validation states describe recorded runs, not this machine or a license grant'
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iso', type=Path, required=True)
    p.add_argument('--manifest', type=Path, default=Path(__file__).resolve().parents[1] / 'upstream/windows-media.json')
    a = p.parse_args()
    r = identify(a.iso, json.loads(a.manifest.read_text(encoding='utf-8')))
    print(json.dumps(r, indent=2))
    raise SystemExit(0 if r['recognized'] else 2)


if __name__ == '__main__':
    main()
