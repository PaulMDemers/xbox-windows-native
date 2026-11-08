#!/usr/bin/env python3
"""Copy a selected preservation plan with independent verification and a receipt."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import shutil
import stat
import sys
import uuid
from datetime import datetime, timezone

CHUNK = 1024 * 1024
REPARSE = getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)


def checked_path(path):
    """Reject symlinks and Windows reparse points in every existing component."""
    path = Path(os.path.abspath(path))
    for part in (path, *path.parents):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & REPARSE:
            raise ValueError(f'Reparse point or symbolic link: {part}')
    return path


def relative_name(value):
    if not isinstance(value, str) or not value or '\x00' in value:
        raise ValueError('Destination must be a nonempty relative path')
    win = PureWindowsPath(value)
    if win.is_absolute() or win.drive or win.root or any(p in ('.', '..') for p in value.replace('\\', '/').split('/')):
        raise ValueError(f'Invalid relative destination: {value!r}')
    # Windows device names and alternate data streams are not ordinary files.
    if any(':' in p or p.endswith((' ', '.')) or PureWindowsPath(p).is_reserved() for p in win.parts):
        raise ValueError(f'Invalid Windows destination: {value!r}')
    return Path(*win.parts)


def signature(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        while block := stream.read(CHUNK):
            h.update(block)
    return h.hexdigest()


def allocation_unit(path):
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes
        sectors, bytes_per_sector = wintypes.DWORD(), wintypes.DWORD()
        free_clusters, total_clusters = wintypes.DWORD(), wintypes.DWORD()
        anchor = Path(path).anchor
        if not ctypes.windll.kernel32.GetDiskFreeSpaceW(
            str(anchor), ctypes.byref(sectors), ctypes.byref(bytes_per_sector),
            ctypes.byref(free_clusters), ctypes.byref(total_clusters)
        ):
            raise ctypes.WinError()
        return sectors.value * bytes_per_sector.value
    return os.statvfs(path).f_frsize


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', help='JSON object with files array')
    parser.add_argument('destination', help='destination root')
    parser.add_argument('--reserve-gib', type=float, default=5, help='free space to retain (default 5 GiB)')
    parser.add_argument('--manifest', help='unique receipt path relative to destination (default generated)')
    parser.add_argument('--resume', action='store_true', help='verify and reuse existing destination files')
    parser.add_argument('--dry-run', action='store_true', help='validate and report counts without copying')
    args = parser.parse_args()
    if not 0 <= args.reserve_gib < float('inf'):
        raise ValueError('Reserve must be finite and nonnegative')
    root = checked_path(args.destination)
    if root.exists() and not root.is_dir():
        raise ValueError('Destination root is not a directory')
    with open(args.plan, encoding='utf-8') as f:
        plan = json.load(f)
    if not isinstance(plan, dict) or not isinstance(plan.get('files'), list):
        raise ValueError('Plan must be an object containing a files array')
    manifest_rel = relative_name(args.manifest or ('receipt-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex + '.jsonl'))
    manifest = checked_path(root / manifest_rel)
    if manifest.exists():
        raise ValueError('Receipt already exists; choose a unique name')
    existing = root
    while not existing.exists():
        existing = existing.parent
    unit = allocation_unit(existing)
    entries, names = [], {str(manifest_rel).replace('\\', '/').casefold()}
    allocated = 0
    for item in plan['files']:
        if not isinstance(item, dict) or not isinstance(item.get('source'), str) or not os.path.isabs(item['source']):
            raise ValueError('Each source must be an absolute path')
        source = checked_path(item['source'])
        info = source.stat()
        if not stat.S_ISREG(info.st_mode):
            raise ValueError(f'Source is not a regular file: {source}')
        rel = relative_name(item.get('destination'))
        key = str(rel).replace('\\', '/').casefold()
        if key in names:
            raise ValueError(f'Destination collision: {rel}')
        names.add(key)
        target = checked_path(root / rel)
        expected = item.get('sha256')
        if expected is not None and (not isinstance(expected, str) or len(expected) != 64 or any(c not in '0123456789abcdefABCDEF' for c in expected)):
            raise ValueError('Expected SHA-256 must be 64 hexadecimal characters')
        if target.exists():
            if not args.resume or not target.is_file():
                raise ValueError(f'Destination already exists: {target}')
        else:
            allocated += ((info.st_size + unit - 1) // unit) * unit
        entries.append((source, target, rel, expected.lower() if expected else None, signature(info)))
    for key in names:
        if any(key.startswith(other + '/') for other in names if other != key):
            raise ValueError('A destination file is also an ancestor of another destination')
    allocated += max(unit, len(entries) * unit)
    free = shutil.disk_usage(existing).free
    reserve = int(args.reserve_gib * 1024**3)
    if free < allocated + reserve:
        raise ValueError(f'Insufficient free space: need {allocated} bytes plus {reserve} bytes reserve, have {free}')
    print(f'Validated {len(entries)} files; estimated allocation {allocated} bytes; free {free} bytes; reserve {reserve} bytes.', flush=True)
    if args.dry_run:
        return
    checked_path(root)
    root.mkdir(parents=True, exist_ok=True)
    checked_path(manifest.parent)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest, 'x', encoding='utf-8', newline='\n') as journal:
        def record(obj):
            journal.write(json.dumps(obj, ensure_ascii=False) + '\n')
            journal.flush()
            os.fsync(journal.fileno())
        record({'type': 'start', 'files': len(entries), 'utc': datetime.now(timezone.utc).isoformat()})
        try:
            for source, target, rel, expected, initial in entries:
                checked_path(source)
                checked_path(target)
                before = source.stat()
                if signature(before) != initial:
                    raise ValueError(f'Source changed since preflight: {source}')
                target.parent.mkdir(parents=True, exist_ok=True)
                checked_path(target)
                if target.exists():
                    if not args.resume or not target.is_file():
                        raise ValueError(f'Destination already exists: {target}')
                    source_hash = digest(source)
                    target_hash = digest(target)
                    status = 'verified-existing'
                else:
                    h = hashlib.sha256()
                    with open(source, 'rb') as src, open(target, 'xb') as dst:
                        while block := src.read(CHUNK):
                            h.update(block)
                            dst.write(block)
                        dst.flush()
                        os.fsync(dst.fileno())
                    source_hash = h.hexdigest()
                    shutil.copystat(source, target, follow_symlinks=False)
                    target_hash = digest(target)
                    status = 'copied'
                if signature(source.stat()) != signature(before):
                    raise ValueError(f'Source changed during verification: {source}')
                if source_hash != target_hash or (expected and source_hash != expected):
                    raise ValueError(f'SHA-256 mismatch: {source}')
                record({'type': 'file', 'source': str(source), 'destination': str(rel), 'sha256': source_hash, 'size': before.st_size, 'status': status})
            record({'type': 'complete', 'files': len(entries)})
        except Exception as exc:
            record({'type': 'failure', 'error': str(exc)})
            raise
    print(f'Completed {len(entries)} files. Receipt: {manifest}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(1)
