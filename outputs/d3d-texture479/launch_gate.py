"""One-shot owned launch admission. No emulator process on failed preflight."""
import hashlib
import json
import os
from pathlib import Path
import time


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def pairs(rows):
    result = {}
    for k, v in rows:
        if k in result:
            raise ValueError('Duplicate JSON field: ' + k)
        result[k] = v
    return result


def read(path):
    raw = Path(path).read_bytes()
    if not 0 < len(raw) <= 1024 * 1024:
        raise ValueError('Receipt size refused')
    return json.loads(raw, object_pairs_hook=pairs)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def publish(path, record):
    """Publish only completed bytes, without replacing an existing receipt."""
    path = Path(path)
    temp = path.with_name(path.name + '.pending')
    with temp.open('xb') as f:
        f.write((json.dumps(record, indent=2) + '\n').encode('utf-8'))
        f.flush()
        os.fsync(f.fileno())
    os.link(temp, path)  # Atomic, fails if destination exists; no overwrite.
    temp.unlink()


def verify(receipt, kit, fixture, attempt, now_ns=None):
    kit, fixture = Path(kit).resolve(), Path(fixture).resolve()
    receipt = Path(receipt).resolve()
    need(receipt == kit / 'preflight001.json', 'Wrong preflight path')
    r = read(receipt)
    need(set(r) == {'schema', 'attempt', 'fixture', 'completed', 'passed',
                   'finished_ns', 'files', 'fixture_files'}, 'Preflight fields')
    need(type(r['schema']) is int and r['schema'] == 1, 'Preflight schema')
    need(r['completed'] is True and r['passed'] is True, 'Preflight not completed')
    need(r['attempt'] == attempt and r['fixture'] == str(fixture), 'Attempt identity')
    now = time.time_ns() if now_ns is None else now_ns
    need(type(r['finished_ns']) is int and 0 <= now-r['finished_ns'] <= 3600*10**9,
         'Stale or future preflight')
    prep_path, cold_path = kit/'ntfs-preparation001.json', kit/'ntfs-cold0-002.json'
    need(type(r['files']) is dict and 4 <= len(r['files']) <= 1024, 'Pin capacity')
    required = {str(prep_path), str(cold_path), str(kit/'run001.py'), str(kit/'launch_gate.py')}
    need(required <= r['files'].keys(), 'Missing required dependency')
    for name, digest in r['files'].items():
        need(type(digest) is str and len(digest) == 64 and
             all(c in '0123456789abcdef' for c in digest), 'Invalid digest')
        need(Path(name).is_absolute() and sha(name) == digest, 'Changed pin: ' + name)
    prep, cold = read(prep_path), read(cold_path)
    need(prep['path'] == str(fixture) and prep['guest_launched'] is False, 'Prepared fixture')
    need(cold['complete'] is True and cold['audit_unchanged'] is True and
         cold['source_unchanged'] is True, 'Cold baseline incomplete')
    expected = {str(fixture/'disk.qcow2'): prep['child_sha256'],
                str(fixture/'probe.img'): prep['floppy_sha256'],
                str(Path(prep['source'])): prep['source_sha256']}
    need(len(expected) == 3 and r['fixture_files'] == expected, 'Fixture pin set')
    need(cold['disk_sha256'] == prep['child_sha256'], 'Cold/preparation mismatch')
    for name, digest in expected.items():
        need(sha(name) == digest, 'Changed fixture: ' + name)
    for name, digest in prep['inputs'].items():
        need(Path(name).name == name and r['files'].get(str(kit/name)) == digest,
             'Prepared input closure')
    for name, digest in prep['runtime_pins'].items():
        need(r['files'].get(name) == digest, 'Runtime closure')
    return {'schema': 1, 'attempt': attempt, 'preflight_sha256': sha(receipt),
            'preflight_finished_ns': r['finished_ns'], 'validated_ns': time.time_ns(),
            'fixture': str(fixture), 'dependencies': len(r['files'])}


def launch(receipt, kit, fixture, attempt, command, *, popen, **kwargs):
    """Validation and exclusive consumption are inseparable from dispatch."""
    record = verify(receipt, kit, fixture, attempt)
    # A failed Popen still consumes this attempt. No automatic retry.
    with (Path(kit)/'launch-admission001.json').open('x', encoding='utf-8') as f:
        json.dump(record, f, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    return popen(command, **kwargs)
