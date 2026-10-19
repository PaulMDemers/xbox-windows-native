#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Create and verify deterministic tester ZIPs. Local files only; never FTP or boot."""
import argparse
import hashlib
import json
from pathlib import Path
import stat
import zipfile
from fatx_names import check_path

KINDS = ('utilities', 'windows-e-preview')
LAUNCHER = 'E/Applications/XWNEBoot/default.xbe'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(name, kind):
    require(isinstance(name, str) and name and '\\' not in name, 'Use relative forward-slash paths')
    parts = name.split('/')
    require(all(p not in ('', '.', '..') and ':' not in p and not any(ord(c) < 32 for c in p) for p in parts), 'Unsafe path')
    require(name != 'MANIFEST.json', 'Reserved manifest path')
    require(parts[0] in ('E', 'docs', 'host', 'source', 'licenses') or name == 'README.txt', 'Unexpected archive root')
    if parts[0] == 'E':
        check_path(name, 437)
        require(all(not p.endswith(('.', ' ')) for p in parts), 'Ambiguous trailing character')
        lower = name.lower()
        if kind == 'utilities':
            require(lower.startswith('e/applications/xwninfo/'), 'Utility console path outside XWNInfo')
        else:
            require(any(lower.startswith(p) for p in ('e/winnt/', 'e/documents and settings/',
                'e/program files/', 'e/applications/xwneboot/', 'e/xwndemo372/')), 'Windows path outside dedicated installation roots')
    require(not any(p.lower() in ('eeprom.bin', 'hddkey.bin', '.env') for p in parts), 'Private console data refused')


def validate_manifest(m):
    require(isinstance(m, dict) and set(m) == {'schema','kind','profile','console_target','qualification','files','directories','limits'}, 'Unexpected manifest fields')
    require(type(m.get('schema')) is int and m['schema'] == 1 and m.get('kind') in KINDS, 'Unknown bundle schema/kind')
    require(m.get('qualification') == 'experimental-not-hardware-qualified', 'Unreviewed qualification claim')
    require(m.get('console_target') == 'E', 'Only dashboard E is supported')
    files = m.get('files')
    require(isinstance(files, list) and 0 < len(files) <= 20000, 'File count bound')
    seen = set()
    directories = m.get('directories')
    require(isinstance(directories, list) and len(directories) <= 20000, 'Directory list bound')
    dir_keys = set()
    for name in directories:
        require(isinstance(name, str), 'Invalid directory')
        if name not in ('E', 'E/Applications', 'docs', 'host', 'source', 'licenses'):
            safe_path(name + '/.directory-placeholder', m['kind'])
        key = name.casefold()
        require(key not in dir_keys, 'Duplicate directory')
        dir_keys.add(key)
    for row in files:
        require(isinstance(row, dict) and set(row) == {'path', 'bytes', 'sha256'}, 'Invalid file record')
        safe_path(row['path'], m['kind'])
        key = row['path'].casefold()
        require(key not in seen, 'Case-insensitive duplicate')
        seen.add(key)
        require(type(row['bytes']) is int and 0 <= row['bytes'] <= 256*1024**2, 'File size bound')
        h = row['sha256']
        require(isinstance(h, str) and len(h) == 64 and all(c in '0123456789abcdef' for c in h), 'Invalid digest')
    for name in seen:
        require(not any('/'.join(name.split('/')[:i]) in seen for i in range(1, len(name.split('/')))), 'File/directory collision')
    require(not seen & dir_keys, 'File/directory collision')
    for name in seen | dir_keys:
        require(all('/'.join(name.split('/')[:i]) in dir_keys for i in range(1, len(name.split('/')))), 'Missing parent directory')
    if m['kind'] == 'windows-e-preview':
        required = {LAUNCHER.lower(), 'e/applications/xwneboot/freeldr.sys',
                    'e/applications/xwneboot/rosload.exe', 'e/winnt/system32/config/system',
                    'e/winnt/system32/ntoskrnl.exe'}
        require(required <= seen, 'Incomplete boot payload')
        require(m.get('profile') == 'e-720p', 'Only the reviewed E/720p layout is supported')
    else:
        require(m.get('profile') == 'inventory', 'Unknown utility profile')
        require('e/applications/xwninfo/default.xbe' in seen, 'Missing inventory XBE')
    return files


def collect(root, kind):
    require(root.is_dir() and not any(p.is_symlink() or getattr(p, 'is_junction', lambda: False)()
            for p in (root, *root.absolute().parents)), 'Expected a regular staging directory without redirected ancestors')
    rows = []
    directories = []
    for p in sorted(root.rglob('*')):
        require(not p.is_symlink() and not getattr(p, 'is_junction', lambda: False)(), 'Links/reparse points refused')
        if p.is_dir():
            directories.append(p.relative_to(root).as_posix())
            continue
        require(stat.S_ISREG(p.stat().st_mode), 'Non-regular file refused')
        name = p.relative_to(root).as_posix()
        safe_path(name, kind)
        require(p.stat().st_size <= 256*1024**2, 'File size bound')
        data = p.read_bytes()
        rows.append(dict(path=name, bytes=len(data), sha256=digest(data)))
    m = dict(schema=1, kind=kind, profile='e-720p' if kind == 'windows-e-preview' else 'inventory',
             console_target='E', qualification='experimental-not-hardware-qualified', files=rows, directories=directories,
             limits='Hashes establish package integrity, not bootability, safety, licensing or hardware compatibility. No credentials, uploads or activation.')
    validate_manifest(m)
    return m


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON key')
        result[key] = value
    return result


def decode(data):
    require(len(data) <= 8*1024**2, 'Manifest size bound')
    return json.loads(data, object_pairs_hook=no_duplicates)


def verify(archive):
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        require(len(names) == len(set(names)), 'Duplicate ZIP member')
        require('MANIFEST.json' in names and z.getinfo('MANIFEST.json').file_size <= 8*1024**2, 'Missing/oversized manifest')
        header = z.getinfo('MANIFEST.json')
        require(not header.flag_bits & 1 and stat.S_IFMT(header.external_attr >> 16) in (0, stat.S_IFREG), 'Invalid manifest member')
        m = decode(z.read('MANIFEST.json'))
        rows = validate_manifest(m)
        require(set(names) == {'MANIFEST.json'} | {r['path'] for r in rows} | {n+'/' for n in m['directories']}, 'Unmanifested/missing member')
        for name in m['directories']:
            info = z.getinfo(name+'/')
            require(info.is_dir() and info.file_size == 0 and stat.S_IFMT(info.external_attr >> 16) in (0, stat.S_IFDIR), 'Invalid ZIP directory')
        for row in rows:
            info = z.getinfo(row['path'])
            require(info.file_size == row['bytes'] and not info.flag_bits & 1, 'Size/encryption mismatch')
            require(stat.S_IFMT(info.external_attr >> 16) in (0, stat.S_IFREG), 'Non-regular ZIP member')
            require(digest(z.read(row['path'])) == row['sha256'], 'Content mismatch')
    return m


def build(root, manifest, output, private_windows=False):
    m = decode(manifest.read_bytes())
    rows = validate_manifest(m)
    require(m['kind'] != 'windows-e-preview' or private_windows, 'Windows input requires --private-windows; no redistribution clearance implied')
    actual = collect(root, m['kind'])
    require(actual['files'] == rows and actual['directories'] == m['directories'], 'Staging files/directories changed since planning')
    require(not output.exists() and not output.resolve().is_relative_to(root.resolve()), 'Fresh output outside staging required')
    # Exclusive creation; a failed partial archive remains evidence and must not be used.
    with output.open('xb') as f, zipfile.ZipFile(f, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in m['directories']:
            info = zipfile.ZipInfo(name+'/', (2000, 1, 1, 0, 0, 0))
            info.external_attr = ((stat.S_IFDIR | 0o755) << 16) | 16
            z.writestr(info, b'')
        entries = [('MANIFEST.json', (json.dumps(m, indent=2, sort_keys=True)+'\n').encode())]
        def contents():
            yield from entries
            for row in rows:
                data = (root/row['path']).read_bytes()
                require(digest(data) == row['sha256'], 'File changed during packaging')
                yield row['path'], data
        for name, data in contents():
            info = zipfile.ZipInfo(name, (2000, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            z.writestr(info, data)
    verify(output)
    return digest(output.read_bytes())


def verify_tree(archive, root, console_only=False, defer_launcher=False):
    """Verify an extracted tree or manually downloaded FTP readback. No transfer API."""
    m = verify(archive)
    require(not defer_launcher or (console_only and m['kind'] == 'windows-e-preview'), 'Launcher deferral is Windows console-only')
    require(root.is_dir() and not any(p.is_symlink() or getattr(p, 'is_junction', lambda: False)()
            for p in (root, *root.absolute().parents)), 'Redirected/missing readback root')
    rows = [r for r in m['files'] if not console_only or r['path'].startswith('E/')]
    dirs = [d for d in m['directories'] if not console_only or d == 'E' or d.startswith('E/')]
    if defer_launcher:
        rows = [r for r in rows if r['path'].casefold() != LAUNCHER.casefold()]
    expected = {r['path']: r for r in rows}
    actual_files = set(); actual_dirs = set()
    for p in root.rglob('*'):
        require(not p.is_symlink() and not getattr(p, 'is_junction', lambda: False)(), 'Redirected readback path')
        name = p.relative_to(root).as_posix()
        if p.is_dir():
            actual_dirs.add(name); continue
        require(stat.S_ISREG(p.stat().st_mode), 'Non-regular readback file')
        # The embedded archive manifest is optional for a fully extracted PC tree.
        if name == 'MANIFEST.json' and not console_only:
            require(decode(p.read_bytes()) == m, 'Changed extracted manifest'); continue
        require(name in expected, 'Unmanifested readback file: ' + name)
        row = expected[name]
        require(p.stat().st_size == row['bytes'] and digest(p.read_bytes()) == row['sha256'], 'Readback mismatch: ' + name)
        actual_files.add(name)
    require(actual_files == set(expected) and actual_dirs == set(dirs), 'Missing/extra readback file or directory')
    return dict(files=len(rows), directories=len(dirs), bytes_verified=True,
                launcher_deferred=defer_launcher, hardware_qualified=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    plan = sub.add_parser('plan'); plan.add_argument('--root', type=Path, required=True)
    plan.add_argument('--kind', choices=KINDS, required=True); plan.add_argument('--output', type=Path, required=True)
    pack = sub.add_parser('build'); pack.add_argument('--root', type=Path, required=True)
    pack.add_argument('--manifest', type=Path, required=True); pack.add_argument('--output', type=Path, required=True)
    pack.add_argument('--private-windows', action='store_true')
    check = sub.add_parser('verify'); check.add_argument('archive', type=Path)
    tree = sub.add_parser('verify-tree'); tree.add_argument('archive', type=Path)
    tree.add_argument('--root', type=Path, required=True); tree.add_argument('--console-only', action='store_true')
    tree.add_argument('--defer-launcher', action='store_true')
    a = p.parse_args()
    if a.command == 'plan':
        require(not a.output.resolve().is_relative_to(a.root.resolve()), 'Plan must be outside staging')
        m = collect(a.root, a.kind)
        with a.output.open('x', encoding='utf-8') as f: json.dump(m, f, indent=2); f.write('\n')
        print(f"Planned {len(m['files'])} files; review contents and provenance before building")
    elif a.command == 'build':
        print(build(a.root, a.manifest, a.output, a.private_windows))
    elif a.command == 'verify-tree':
        print(json.dumps(verify_tree(a.archive, a.root, a.console_only, a.defer_launcher), indent=2))
    else:
        m = verify(a.archive); print(f"Verified {len(m['files'])} files: {m['qualification']}")


if __name__ == '__main__':
    main()
