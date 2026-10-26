"""Archive explicitly selected cold files; Python 3.14, no console access.

Plans are private JSON: archive_root, allowed_roots, files (path, bytes,
mtime_ns). Only existing .zst archives and log/trace/ram captures are admitted.
Raw virtual disks, backing chains and directories are deliberately unsupported.
"""
import argparse
from compression import zstd
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import time

CHUNK = 4 * 1024 * 1024
RESERVE = 20 * 1024**3


def plain_path(path):
    path = Path(os.path.abspath(path))
    for part in (path, *path.parents):
        if part.exists() or part.is_symlink():
            info = part.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
                raise ValueError(f'Reparse/symlink path refused: {part}')
    return path.resolve()


def digest(stream):
    h = hashlib.sha256()
    size = 0
    while block := stream.read(CHUNK):
        h.update(block)
        size += len(block)
    return h.hexdigest(), size


def file_digest(path):
    with Path(path).open('rb') as stream:
        return digest(stream)


def durable_json(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def append_event(path, event):
    with Path(path).open('a', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(event) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def validate(item, allowed_roots):
    source = plain_path(item['path'])
    if not any(source.is_relative_to(plain_path(root)) for root in allowed_roots):
        raise ValueError(f'Outside approved roots: {source}')
    if source.suffix.lower() not in ('.zst', '.log', '.trace', '.ram'):
        raise ValueError(f'Unsupported cold artifact: {source}')
    info = source.stat()
    if not stat.S_ISREG(info.st_mode):
        raise ValueError('Not a regular file')
    if (info.st_size, info.st_mtime_ns) != (item['bytes'], item['mtime_ns']):
        raise ValueError(f'Source changed since plan: {source}')
    return source


def archive_one(item, roots, archive_root, remove=False):
    source = validate(item, roots)
    root = plain_path(archive_root)
    if source.is_relative_to(root):
        raise ValueError('Source already inside archive destination')
    if shutil.disk_usage(root).free < item['bytes'] * 1.02 + RESERVE:
        raise RuntimeError('Destination would breach 20 GiB reserve')
    ident = hashlib.sha256(str(source).encode('utf-8')).hexdigest()[:24]
    target = root / 'files' / (ident + '.zst')
    receipt = root / 'receipts' / (ident + '.json')
    pointer = source.with_name(source.name + '.archive-location.json')
    if target.exists() or receipt.exists() or pointer.exists():
        raise FileExistsError(f'Existing archive/receipt/pointer: {source}')
    target.parent.mkdir(exist_ok=True)
    receipt.parent.mkdir(exist_ok=True)
    mode = 'relocate-zst' if source.suffix.lower() == '.zst' else 'compress-zst'
    before = source.stat()
    src_hash = hashlib.sha256()
    with source.open('rb') as inp, target.open('xb') as raw:
        if mode == 'relocate-zst':
            while block := inp.read(CHUNK):
                src_hash.update(block)
                raw.write(block)
        else:
            with zstd.open(raw, 'wb', level=3) as encoder:
                while block := inp.read(CHUNK):
                    src_hash.update(block)
                    encoder.write(block)
        raw.flush()
        os.fsync(raw.fileno())
    archive_hash, archive_bytes = file_digest(target)
    with zstd.open(target, 'rb') as decoded:
        decoded_hash, decoded_bytes = digest(decoded)
    expected = archive_hash if mode == 'relocate-zst' else decoded_hash
    if expected != src_hash.hexdigest():
        raise RuntimeError('Archive verification failed; original retained')
    # Re-read the original immediately before recording/removal. Never rely on
    # age, length or mtime alone to decide whether the source is still identical.
    if file_digest(source) != (src_hash.hexdigest(), item['bytes']):
        raise RuntimeError('Source content changed; original retained')
    after = source.stat()
    if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
        raise RuntimeError('Source identity changed; original retained')
    result = dict(source=str(source), archive=str(target), mode=mode,
                  source_bytes=item['bytes'], source_sha256=src_hash.hexdigest(),
                  archive_bytes=archive_bytes, archive_sha256=archive_hash,
                  decoded_bytes=decoded_bytes, decoded_sha256=decoded_hash,
                  source_mtime_ns=before.st_mtime_ns,
                  source_attributes=getattr(before, 'st_file_attributes', None),
                  verified_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    durable_json(receipt, result)
    durable_json(pointer, result)
    journal = root / 'journal.jsonl'
    append_event(journal, dict(event='verified', receipt=str(receipt), **result))
    if remove:
        validate(item, roots)
        source.unlink()  # One verified regular file; never recursive deletion.
        append_event(journal, dict(event='source-removed', source=str(source), receipt=str(receipt)))
    return result


def restore(receipt_path, destination):
    record = json.loads(Path(receipt_path).read_text(encoding='utf-8'))
    archive = plain_path(record['archive'])
    destination = plain_path(destination)
    if destination.exists():
        raise FileExistsError(destination)
    if file_digest(archive) != (record['archive_sha256'], record['archive_bytes']):
        raise RuntimeError('Archive hash mismatch')
    if shutil.disk_usage(destination.parent).free < record['source_bytes'] + RESERVE:
        raise RuntimeError('Restore would breach 20 GiB reserve')
    with destination.open('xb') as out:
        opener = open if record['mode'] == 'relocate-zst' else zstd.open
        with opener(archive, 'rb') as inp:
            shutil.copyfileobj(inp, out, CHUNK)
        out.flush()
        os.fsync(out.fileno())
    if file_digest(destination) != (record['source_sha256'], record['source_bytes']):
        raise RuntimeError('Restored content failed verification; keep for inspection')
    os.utime(destination, ns=(record['source_mtime_ns'], record['source_mtime_ns']))
    return record['source_sha256']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    run = sub.add_parser('archive')
    run.add_argument('plan')
    run.add_argument('--execute', action='store_true')
    run.add_argument('--remove-verified', action='store_true')
    recover = sub.add_parser('restore')
    recover.add_argument('receipt')
    recover.add_argument('destination')
    args = parser.parse_args()
    if args.command == 'restore':
        print(restore(args.receipt, args.destination))
        return
    plan = json.loads(Path(args.plan).read_text(encoding='utf-8'))
    # Validate the complete selection before creating archives or removing files.
    sources = [validate(x, plan['allowed_roots']) for x in plan['files']]
    if len(set(sources)) != len(sources):
        raise ValueError('Duplicate source in plan')
    print(json.dumps({'files': len(sources), 'bytes': sum(x['bytes'] for x in plan['files']),
                      'execute': args.execute, 'remove_verified': args.remove_verified}), flush=True)
    if not args.execute:
        return
    for i, item in enumerate(plan['files'], 1):
        result = archive_one(item, plan['allowed_roots'], plan['archive_root'], args.remove_verified)
        print(json.dumps({'completed': i, 'total': len(sources), 'source': result['source'],
                          'source_bytes': result['source_bytes'], 'archive_bytes': result['archive_bytes']}), flush=True)


if __name__ == '__main__':
    main()
