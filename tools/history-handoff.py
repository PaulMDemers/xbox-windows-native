#!/usr/bin/env python3
"""Inventory and verify directory handoffs. This program never moves or deletes data."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys

REPARSE = getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)


def native_path(path):
    """Use extended-length Windows paths for all filesystem access."""
    value = os.path.abspath(os.fspath(path))
    if os.name == 'nt' and not value.startswith('\\\\?\\'):
        if value.startswith('\\\\'):
            value = '\\\\?\\UNC\\' + value[2:]
        else:
            value = '\\\\?\\' + value
    return Path(value)


def is_reparse(st):
    return stat.S_ISLNK(st.st_mode) or bool(getattr(st, 'st_file_attributes', 0) & REPARSE)


def safe_relative(value):
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError('invalid relative path')
    p = PurePosixPath(value)
    if p.is_absolute() or any(part in ('..', '.') for part in p.parts) or ':' in value:
        raise ValueError('unsafe relative path: ' + value)
    return p


def no_links(path):
    path = native_path(path)
    for part in reversed([path, *path.parents]):
        if os.path.lexists(part) and is_reparse(os.lstat(part)):
            raise ValueError('reparse point in path: ' + str(part))


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def walk(root, allow_reparse):
    # scandir's iterator is closed before descending, keeping handles bounded.
    stack = [(native_path(root), '')]
    while stack:
        directory, rel = stack.pop()
        st = os.lstat(directory)
        if is_reparse(st):
            raise ValueError('root or directory is a reparse point: ' + str(directory))
        yield directory, rel, st, 'dir'
        with os.scandir(directory) as entries:
            for entry in entries:
                path = Path(entry.path)
                sub = (rel + '/' if rel else '') + entry.name
                st = os.lstat(path)
                if is_reparse(st):
                    if not allow_reparse:
                        raise ValueError('reparse point: ' + str(path))
                    yield path, sub, st, 'reparse'
                elif stat.S_ISDIR(st.st_mode):
                    stack.append((path, sub))
                elif stat.S_ISREG(st.st_mode):
                    yield path, sub, st, 'file'
                else:
                    raise ValueError('unsupported file type: ' + str(path))


def metadata(st):
    return {'size': st.st_size, 'mtime_ns': st.st_mtime_ns,
            'attributes': getattr(st, 'st_file_attributes', None), 'mode': st.st_mode}


def emit(f, obj):
    f.write(json.dumps(obj, ensure_ascii=True, separators=(',', ':')) + '\n')


def inventory(args):
    with open(native_path(args.plan), encoding='utf-8') as f:
        plan = json.load(f)
    if not isinstance(plan, list) or not plan:
        raise ValueError('plan must be a nonempty JSON array')
    for item in plan:
        if not isinstance(item, dict) or not all(isinstance(item.get(k), str) and os.path.isabs(item[k]) for k in ('source', 'destination')):
            raise ValueError('each plan entry needs absolute source and destination paths')
        no_links(item['source'])
        no_links(item['destination'])
        if not os.path.isdir(native_path(item[args.location])):
            raise ValueError('inventory root is not a directory: ' + item[args.location])
    out = Path(os.path.abspath(args.output))
    for item in plan:
        for key in ('source', 'destination'):
            try:
                inside = os.path.commonpath([str(out), os.path.abspath(item[key])]) == os.path.abspath(item[key])
            except ValueError:  # Different drives cannot overlap.
                inside = False
            if inside:
                raise ValueError('manifest must be outside planned roots')
    counts = {'files': 0, 'dirs': 0, 'reparse': 0, 'bytes': 0}
    with open(native_path(out), 'x', encoding='utf-8', newline='\n') as f:
        emit(f, {'type': 'header', 'version': 1, 'plan': plan, 'allow_reparse': args.allow_reparse, 'metadata_only': args.metadata_only})
        for index, item in enumerate(plan):
            for path, rel, st, kind in walk(item[args.location], args.allow_reparse):
                record = {'type': kind, 'root': index, 'path': rel, **metadata(st)}
                if kind == 'file':
                    if not args.metadata_only:
                        record['sha256'] = digest(path)
                    after = os.lstat(path)
                    if is_reparse(after) or (st.st_size, st.st_mtime_ns, st.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
                        raise ValueError('file changed during hashing: ' + str(path))
                    counts['files'] += 1
                    counts['bytes'] += st.st_size
                    if counts['files'] % 1000 == 0:
                        print('Inventoried {files} files, {bytes} bytes'.format(**counts), flush=True)
                elif kind == 'reparse':
                    record['target'] = os.readlink(path)
                    counts['reparse'] += 1
                else:
                    counts['dirs'] += 1
                emit(f, record)
        emit(f, {'type': 'complete', **counts})
    print(('METADATA-ONLY' if args.metadata_only else 'SHA-256') + ' inventory complete: ' + str(counts), flush=True)


def verify(args):
    counts = {'files': 0, 'dirs': 0, 'reparse': 0, 'bytes': 0}
    complete = None
    with open(native_path(args.manifest), encoding='utf-8') as f:
        header = json.loads(next(f))
        if header.get('type') != 'header' or header.get('version') != 1:
            raise ValueError('invalid manifest header')
        if header.get('metadata_only') and not args.metadata_only:
            raise ValueError('metadata-only manifest requires --metadata-only verification')
        def rebase(value):
            original = os.path.abspath(value)
            matches = []
            for old, new in args.rebase or []:
                if not os.path.isabs(old) or not os.path.isabs(new):
                    raise ValueError('rebase roots must be absolute')
                old = os.path.abspath(old)
                try:
                    if os.path.normcase(os.path.commonpath([original, old])) == os.path.normcase(old):
                        matches.append((len(old), old, new))
                except ValueError:
                    pass
            if matches:
                _, old, new = max(matches)
                return os.path.join(new, os.path.relpath(original, old))
            return original
        roots = [native_path(rebase(x[args.location])) for x in header['plan']]
        for root in roots:
            if not root.is_absolute():
                raise ValueError('root is not absolute')
            no_links(root)
        for line in f:
            rec = json.loads(line)
            kind = rec.get('type')
            if kind == 'complete':
                if complete is not None:
                    raise ValueError('duplicate complete record')
                complete = rec
                continue
            if complete is not None or kind not in ('file', 'dir', 'reparse'):
                raise ValueError('invalid manifest record')
            idx = rec['root']
            if not isinstance(idx, int) or idx < 0 or idx >= len(roots):
                raise ValueError('invalid root index')
            rel = rec['path']
            if rel == '':
                if kind != 'dir':
                    raise ValueError('invalid root record')
                path = roots[idx]
            else:
                path = roots[idx].joinpath(*safe_relative(rel).parts)
            no_links(path.parent if kind == 'reparse' else path)
            st = os.lstat(path)
            if kind == 'file':
                if not stat.S_ISREG(st.st_mode) or is_reparse(st) or st.st_size != rec['size']:
                    raise ValueError('file type or size mismatch: ' + str(path))
                if args.metadata_only:
                    if st.st_mtime_ns != rec['mtime_ns']:
                        raise ValueError('file timestamp mismatch: ' + str(path))
                elif digest(path) != rec['sha256']:
                    raise ValueError('SHA-256 mismatch: ' + str(path))
                after = os.lstat(path)
                if is_reparse(after) or (st.st_size, st.st_mtime_ns, st.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
                    raise ValueError('file changed during verification: ' + str(path))
                counts['files'] += 1
                counts['bytes'] += st.st_size
                if counts['files'] % 1000 == 0:
                    print('Verified {files} files, {bytes} bytes'.format(**counts), flush=True)
            elif kind == 'dir':
                if is_reparse(st) or not stat.S_ISDIR(st.st_mode):
                    raise ValueError('directory mismatch: ' + str(path))
                counts['dirs'] += 1
            else:
                if not header.get('allow_reparse') or not is_reparse(st) or os.readlink(path) != rec['target']:
                    raise ValueError('reparse point mismatch: ' + str(path))
                counts['reparse'] += 1
    if complete is None or any(complete.get(k) != v for k, v in counts.items()):
        raise ValueError('manifest incomplete or totals mismatch')
    actual = {'files': 0, 'dirs': 0, 'reparse': 0, 'bytes': 0}
    for root in roots:
        for path, rel, st, kind in walk(root, header.get('allow_reparse', False)):
            actual[{'file': 'files', 'dir': 'dirs', 'reparse': 'reparse'}[kind]] += 1
            if kind == 'file':
                actual['bytes'] += st.st_size
    if actual != counts:
        raise ValueError('actual directory totals differ: ' + str(actual))
    print(('METADATA-ONLY' if args.metadata_only else 'SHA-256') + ' verification complete: ' + str(counts), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    inv = sub.add_parser('inventory')
    inv.add_argument('--plan', required=True)
    inv.add_argument('--output', required=True)
    inv.add_argument('--allow-reparse', action='store_true')
    inv.add_argument('--location', choices=('source', 'destination'), default='source')
    inv.add_argument('--metadata-only', action='store_true', help='record sizes and timestamps without hashing; weaker verification')
    ver = sub.add_parser('verify')
    ver.add_argument('--manifest', required=True)
    ver.add_argument('--location', choices=('source', 'destination'), required=True)
    ver.add_argument('--rebase', nargs=2, action='append', metavar=('OLDROOT', 'NEWROOT'), help='map a manifest root prefix to its copied location; may be repeated')
    ver.add_argument('--metadata-only', action='store_true', help='check sizes and timestamps instead of hashing; weaker verification')
    args = parser.parse_args()
    try:
        (inventory if args.command == 'inventory' else verify)(args)
    except (OSError, ValueError, KeyError, TypeError, StopIteration, json.JSONDecodeError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
