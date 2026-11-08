#!/usr/bin/env python3
"""Export private pinned package inputs. No build, deployment or console access."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import shutil

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'outputs/bundle-config844'
NAMES = ('xbox16-720.json', 'xbox10-720-matched.json', 'xbox10-480p-matched.json',
         'xbox10-1080i.json', 'xbox10-1024x576-guarded.json')
F_HELPER = 'assemble-f-derived.py'
RESERVE = 20 * 1024**3


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def verify(path, expected):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    if path.is_symlink() or not path.is_file() or len(expected) != 64:
        raise ValueError(f'Missing or unsafe input: {path}')
    actual = sha(path)
    if actual != expected:
        raise ValueError(f'Hash mismatch: {path}; expected {expected}; actual {actual}')
    return path.resolve()


def inventory():
    configs = {n: json.loads((CONFIG / n).read_text(encoding='utf-8')) for n in NAMES}
    # runpy only evaluates the reviewed helper's constants and function definitions.
    helper = runpy.run_path(str(CONFIG / F_HELPER), run_name='migration_inventory')
    inputs = {}
    record_errors = []
    def add(path, expected):
        p = verify(path, expected)
        size = p.stat().st_size
        existing = inputs.setdefault(expected, {'source': str(p), 'bytes': size})
        if existing['bytes'] != size:
            raise ValueError('Inconsistent length for hash')
    for config in configs.values():
        add(config['source_archive'], config['source_sha256'])
        for row in config['overlays']:
            add(row['source'], row['sha256'])
        for row in config['source_records']:
            try:
                verify(row['source'], row['sha256'])
            except ValueError as exc:
                record_errors.append(str(exc))
    add(helper['F'], helper['F_SHA'])
    add(helper['E'], helper['E_SHA'])
    for path, h in helper['OVERLAYS'].values():
        add(path, h)
    for path, h in helper['RECORDS'].values():
        try:
            verify(path, h)
        except ValueError as exc:
            record_errors.append(str(exc))
    return configs, inputs, record_errors


def bind(bundle, checkout):
    bundle, checkout = bundle.resolve(), checkout.resolve()
    for directory in (bundle / 'originals', bundle / 'recipes', bundle / 'blobs'):
        if directory.is_symlink():
            raise ValueError(f'Symlink directory refused: {directory}')
    manifest = json.loads((bundle / 'manifest.json').read_text(encoding='utf-8'))
    for h, info in manifest['inputs'].items():
        if len(h) != 64 or any(c not in '0123456789abcdef' for c in h):
            raise ValueError('Unsafe blob name')
        p = bundle / 'blobs' / h
        if p.is_symlink() or not p.is_file() or p.stat().st_size != info['bytes'] or sha(p) != h:
            raise ValueError(f'Bundled input mismatch: {h}')
    recipes = bundle / 'recipes'
    recipes.mkdir(exist_ok=True)
    for name in (*NAMES, F_HELPER):
        if sha(bundle / 'originals' / name) != manifest['originals'][name]:
            raise ValueError(f'Original recipe mismatch: {name}')
    for name in NAMES:
        config = json.loads((bundle / 'originals' / name).read_text(encoding='utf-8'))
        def blob(h):
            if h not in manifest['inputs']:
                raise ValueError('Unknown input hash')
            return str(bundle / 'blobs' / h)
        config['source_archive'] = blob(config['source_sha256'])
        for row in config['overlays']:
            row['source'] = blob(row['sha256'])
        valid_records = True
        for row in config['source_records']:
            p = (checkout / row['source']).resolve()
            safe = p.is_relative_to(checkout) and not p.is_symlink() and p.is_file()
            actual = sha(p) if safe else 'missing or unsafe'
            if actual != row['sha256']:
                reason = f'checkout record mismatch: {p}; expected {row["sha256"]}; actual {actual}'
                print(f'Skipping {name}: {reason}')
                valid_records = False
                break
            row['source'] = str(p)
        if not valid_records:
            (recipes / name).write_text(json.dumps({'unavailable': reason}) + '\n', encoding='utf-8')
            continue
        (recipes / name).write_text(json.dumps(config, indent=2) + '\n', encoding='utf-8')
    print('Recipes bound to', bundle, 'and', checkout)


def export(destination):
    dest = destination.resolve()
    if dest.exists() or dest.is_relative_to(ROOT) or not dest.parent.is_dir():
        raise ValueError('Choose a fresh output outside checkout, with an existing parent')
    configs, inputs, record_errors = inventory()
    if any(dest.is_relative_to(Path(item['source']).parent) for item in inputs.values()):
        raise ValueError('Output cannot be inside an input directory')
    needed = sum(item['bytes'] for item in inputs.values())
    if shutil.disk_usage(dest.parent).free < needed + RESERVE:
        raise ValueError('Insufficient space for inputs and 20 GiB reserve')
    dest.mkdir()
    (dest / 'blobs').mkdir()
    (dest / 'originals').mkdir()
    for h, info in inputs.items():
        target = dest / 'blobs' / h
        with open(info['source'], 'rb') as src, target.open('xb') as dst:
            shutil.copyfileobj(src, dst, 1024 * 1024)
        if target.stat().st_size != info['bytes'] or sha(target) != h:
            raise ValueError(f'Copy verification failed: {h}')
    for name in (*NAMES, F_HELPER):
        shutil.copyfile(CONFIG / name, dest / 'originals' / name)
    originals = {name: sha(dest / 'originals' / name) for name in (*NAMES, F_HELPER)}
    (dest / 'manifest.json').write_text(json.dumps({'inputs': inputs, 'originals': originals, 'record_errors': record_errors}, indent=2) + '\n', encoding='utf-8')
    bind(dest, ROOT)
    for error in record_errors:
        print('Record warning:', error)
    print('Private input bundle created; F-derived helper needs manual path review.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='action', required=True)
    e = sub.add_parser('export')
    e.add_argument('destination', type=Path)
    b = sub.add_parser('bind')
    b.add_argument('bundle', type=Path)
    b.add_argument('--checkout', required=True, type=Path)
    args = p.parse_args()
    try:
        export(args.destination) if args.action == 'export' else bind(args.bundle, args.checkout)
    except (OSError, ValueError, KeyError) as exc:
        p.exit(1, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
