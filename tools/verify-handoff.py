#!/usr/bin/env python3
"""Verify preservation receipts against files in a destination root."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import stat
import sys

REPARSE = getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)


def checked_path(path):
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
        raise ValueError('Path must be a nonempty relative path')
    win = PureWindowsPath(value)
    if win.is_absolute() or win.drive or win.root or any(p in ('', '.', '..') for p in value.replace('\\', '/').split('/')):
        raise ValueError(f'Invalid relative path: {value!r}')
    if any(':' in p or p.endswith((' ', '.')) or PureWindowsPath(p).is_reserved() for p in win.parts):
        raise ValueError(f'Invalid Windows path: {value!r}')
    return Path(*win.parts)


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        while block := stream.read(1024 * 1024):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', help='preservation destination root')
    parser.add_argument('receipts', nargs='+', help='receipt paths relative to root')
    args = parser.parse_args()
    root = checked_path(args.root)
    if not root.is_dir():
        raise ValueError('Root must be an existing directory')
    files = {}
    for name in args.receipts:
        receipt = checked_path(root / relative_name(name))
        records = []
        with open(receipt, encoding='utf-8') as stream:
            for line in stream:
                record = json.loads(line)
                if not isinstance(record, dict):
                    raise ValueError(f'Invalid record in {name}')
                records.append(record)
        if len(records) < 2 or records[0].get('type') != 'start' or records[-1].get('type') != 'complete':
            raise ValueError(f'Receipt is incomplete: {name}')
        entries = records[1:-1]
        if any(r.get('type') != 'file' for r in entries):
            raise ValueError(f'Receipt contains an unexpected record: {name}')
        if type(records[0].get('files')) is not int or records[0]['files'] != len(entries) or type(records[-1].get('files')) is not int or records[-1]['files'] != len(entries):
            raise ValueError(f'Receipt count mismatch: {name}')
        for entry in entries:
            rel = relative_name(entry.get('destination'))
            size, expected = entry.get('size'), entry.get('sha256')
            if type(size) is not int or size < 0 or not isinstance(expected, str) or len(expected) != 64 or any(c not in '0123456789abcdefABCDEF' for c in expected):
                raise ValueError(f'Invalid file metadata in {name}')
            key = str(rel).replace('\\', '/').casefold()
            metadata = (size, expected.lower())
            if key in files and files[key][1] != metadata:
                raise ValueError(f'Conflicting duplicate destination: {rel}')
            files[key] = (rel, metadata)
    total = 0
    for rel, (size, expected) in files.values():
        path = checked_path(root / rel)
        before = path.stat()
        if not stat.S_ISREG(before.st_mode) or before.st_size != size:
            raise ValueError(f'File size or type mismatch: {rel}')
        actual = sha256(path)
        after = path.stat()
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise ValueError(f'File changed during verification: {rel}')
        if actual != expected:
            raise ValueError(f'SHA-256 mismatch: {rel}')
        total += size
    print(f'Verified {len(files)} files ({total} bytes) from {len(args.receipts)} complete receipt(s).')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(1)
