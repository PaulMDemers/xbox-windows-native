#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Back up/restore standard Xbox E in an OFFLINE 10GB raw image (Linux/WSL)."""
import argparse
import contextlib
import gzip
import hashlib
import json
import os
from pathlib import Path
import stat

SIZE = 10_000_000_000
START = 5633024 * 512
LENGTH = 10000048 * 512
CHUNK = 4 * 1024 * 1024


def require(ok, why):
    if not ok:
        raise ValueError(why)


def regular(path):
    p = Path(path).absolute()
    require(not any(x.is_symlink() for x in [p, *p.parents]), 'Symlink path refused')
    require(stat.S_ISREG(p.stat().st_mode), 'Only regular offline files are supported')
    return p


@contextlib.contextmanager
def image(path, write=False):
    import fcntl
    p = regular(path)
    fd = os.open(p, (os.O_RDWR if write else os.O_RDONLY) | os.O_NOFOLLOW)
    with os.fdopen(fd, 'r+b' if write else 'rb') as f:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        require(stat.S_ISREG(os.fstat(f.fileno()).st_mode), 'Not a regular image')
        require(os.fstat(f.fileno()).st_size == SIZE, 'Expected a 10,000,000,000-byte raw image')
        f.seek(0)
        require(f.read(512) == bytes(512), 'Extended/custom partition table refused')
        f.seek(START)
        header = f.read(4096)
        require(header[:4] == b'FATX' and int.from_bytes(header[8:12], 'little') == 32,
                'Expected standard E FATX with 16KiB clusters')
        yield f


def region(f, start, count, dest=None):
    f.seek(start)
    h = hashlib.sha256()
    while count:
        b = f.read(min(count, CHUNK))
        require(bool(b), 'Truncated image')
        h.update(b)
        if dest is not None:
            dest.write(b)
        count -= len(b)
    return h.hexdigest()


def outside(f):
    return [region(f, 0, START), region(f, START + LENGTH, SIZE - START - LENGTH)]


def file_hash(p):
    with regular(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def fresh(path):
    p = Path(path).absolute()
    require(not any(x.is_symlink() for x in [p, *p.parents]), 'Symlink output refused')
    p.mkdir(parents=True, exist_ok=False)
    return p


def save(path, record):
    # Private fresh output, synchronous writes; retain failed/incomplete receipts.
    with path.open('w', encoding='utf-8', newline='\n') as f:
        json.dump(record, f, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def backup(path, output):
    out = fresh(output)
    r = {'schema': 1, 'status': 'started', 'disk_bytes': SIZE,
         'start': START, 'length': LENGTH, 'scope': 'Offline standard E partition only'}
    save(out / 'manifest.json', r)
    try:
        with image(path) as f:
            r['outside_sha256'] = outside(f)
            with (out / 'E.raw.gz').open('xb') as raw:
                with gzip.GzipFile(fileobj=raw, mode='wb', mtime=0) as z:
                    r['e_sha256'] = region(f, START, LENGTH, z)
                raw.flush()
                os.fsync(raw.fileno())
            r['compressed_sha256'] = file_hash(out / 'E.raw.gz')
            verify_payload(out / 'E.raw.gz', r['e_sha256'])
            require(outside(f) == r['outside_sha256'], 'Outside E changed during backup')
            require(region(f, START, LENGTH) == r['e_sha256'], 'E changed during backup')
        r['status'] = 'verified'
        return r
    except BaseException as e:
        r.update(status='failed', error=repr(e))
        raise
    finally:
        save(out / 'manifest.json', r)


def verify_payload(path, expected, dest=None):
    h = hashlib.sha256()
    left = LENGTH
    with regular(path).open('rb') as raw, gzip.GzipFile(fileobj=raw, mode='rb') as z:
        while left:
            b = z.read(min(left, CHUNK))
            require(bool(b), 'Truncated backup')
            h.update(b)
            if dest is not None:
                dest.write(b)
            left -= len(b)
        require(z.read(1) == b'', 'Oversized backup')
    require(h.hexdigest() == expected, 'Uncompressed backup mismatch')


def restore(path, bundle, output):
    bundle = Path(bundle).absolute()
    manifest = regular(bundle / 'manifest.json')
    require(manifest.stat().st_size < 8192, 'Manifest too large')
    r = json.loads(manifest.read_text())
    require((r.get('schema'), r.get('status'), r.get('disk_bytes'), r.get('start'), r.get('length')) ==
            (1, 'verified', SIZE, START, LENGTH), 'Unrecognized/incomplete backup')
    payload = bundle / 'E.raw.gz'
    require(file_hash(payload) == r['compressed_sha256'], 'Compressed backup changed')
    # Read and verify the ENTIRE decompressed payload before opening the destination writable.
    verify_payload(payload, r['e_sha256'])
    out = fresh(output)
    result = {'status': 'started', 'scope': r['scope'], 'e_sha256': r['e_sha256'],
              'backup_manifest_sha256': file_hash(manifest), 'writes_started': False}
    save(out / 'restore.json', result)
    try:
        with image(path, True) as f:
            result['outside_before'] = outside(f)
            require(result['outside_before'] == r['outside_sha256'],
                    'Image outside E differs from this backup; cross-image restore refused')
            result['e_before'] = region(f, START, LENGTH)
            result['writes_started'] = True
            save(out / 'restore.json', result)
            f.seek(START)
            verify_payload(payload, r['e_sha256'], f)
            f.flush()
            os.fsync(f.fileno())
            result['e_after'] = region(f, START, LENGTH)
            result['outside_after'] = outside(f)
            require(result['e_after'] == r['e_sha256'], 'Restore readback mismatch')
            require(result['outside_before'] == result['outside_after'], 'Write escaped E')
        result['status'] = 'verified'
        return result
    except BaseException as e:
        result.update(status='failed', error=repr(e))
        raise
    finally:
        save(out / 'restore.json', result)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['backup', 'restore'])
    p.add_argument('--image', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True, help='Fresh receipt/bundle directory')
    p.add_argument('--bundle', type=Path)
    a = p.parse_args()
    if os.name != 'posix':
        p.error('Use Linux/WSL; raw OFFLINE image files only, never a live console/disk device')
    if a.action == 'restore' and not a.bundle:
        p.error('restore requires --bundle')
    result = backup(a.image, a.output) if a.action == 'backup' else restore(a.image, a.bundle, a.output)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
