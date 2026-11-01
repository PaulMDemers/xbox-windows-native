"""One-shot E-only transfer from a completed preflight; no launch or delete API."""
import argparse
import hashlib
import io
import json
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'outputs/demo-audio-level256'))
import tester_bundle as bundle
from common001 import ticket, queue
from preflight import FTP, get, names, sha


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('archive', type=Path)
    ap.add_argument('receipt', type=Path)
    a = ap.parse_args()
    r = json.loads((a.receipt / 'preflight.json').read_text())
    assert r['completed'] and not r['physical_writes']
    assert sha(a.archive.read_bytes()) == r['archive_sha256']
    m = bundle.verify(a.archive)
    assert m['kind'] == 'windows-e-preview' and m['profile'] == 'e-720p'
    rows = {x['path']: x for x in m['files'] if x['path'].startswith('E/')}
    dirs = sorted((x for x in m['directories'] if x == 'E' or x.startswith('E/')), key=lambda p: (p.count('/'), p))
    assert set(rows) == set(r['files']) and set(dirs) == set(r['directories'])
    for path, item in rows.items():
        prior = r['files'][path]
        assert item['sha256'] == prior['target_sha256']
        if prior.get('changed'):
            backup = (a.receipt / 'before' / path).read_bytes()
            assert len(backup) == prior['before_bytes'] and sha(backup) == prior['before_sha256']
    # 843 baseline's conservative remaining budget already deducts its installed
    # allocation and additional owned inventory budget from the last measurement.
    # Charge every growth independently; do not credit truncations.
    cluster = 16384
    alloc = lambda n: ((n + cluster - 1) // cluster) * cluster
    growth = sum(max(0, alloc(item['bytes']) - alloc(r['files'][path].get('before_bytes', 0)))
                 for path, item in rows.items())
    growth += cluster * sum(not exists for exists in r['directories'].values())
    capacity_data = (ROOT / 'outputs/boot720-input843/baseline001.json').read_bytes()
    assert sha(capacity_data) == '020028631f8473d05d40856e8c0262b25fd9f5104790578bf55da4e540317b3e'
    capacity = json.loads(capacity_data)['projected_console_reserve']
    assert capacity['projected_remaining'] == capacity['last_measured_free'] - capacity['installed_allocation'] - capacity['additional_owned_budget']
    available = capacity['projected_remaining']
    reserve = capacity['minimum_required']
    assert growth + reserve <= available, 'Projected E growth exceeds conservative 843 budget'
    journal_path = a.receipt / 'apply.jsonl'
    assert not journal_path.exists(), 'Prior apply requires manual review, never retry automatically'
    ticket()
    lock = queue / 'bundle845-apply-active.lock'
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    ftp = FTP()
    try:
        config = json.loads(Path('C:/xwn820/connection.json').read_text())
        assert config['host'] == r['target_authentication']['host'] == '192.168.50.66'
        ftp.connect(config['host'], timeout=15)
        ftp.login(config['user'], config['password'])
        owner = get(ftp, '/E/Applications/XWN16Boot843/owner843.json', 919)
        assert sha(owner) == r['target_authentication']['owner_sha256'] == '8e5505efd515fd1901e5aec3b7b6816e20a261ed1766912ffb0cbd9a1056fe35'
        with journal_path.open('xb', buffering=0) as journal, zipfile.ZipFile(a.archive) as z:
            def log(kind, path, **fields):
                journal.write((json.dumps({'kind': kind, 'path': path, **fields}) + '\n').encode())
                os.fsync(journal.fileno())
            log('start', 'E', archive_sha256=r['archive_sha256'], projected_growth_bytes=growth,
                conservative_available_bytes=available, remaining_reserve_bytes=reserve,
                capacity_source='outputs/boot720-input843/baseline001.json')
            for directory in dirs:
                if directory == 'E':
                    continue
                parent, leaf = directory.rsplit('/', 1)
                current = names(ftp, '/' + parent).get(leaf.casefold())
                if r['directories'][directory]:
                    assert current and current['directory'], 'Existing directory changed: ' + directory
                else:
                    assert current is None, 'Previously absent directory appeared: ' + directory
                    log('mkdir_intent', directory)
                    ftp.mkd('/' + directory)
                    assert names(ftp, '/' + parent)[leaf.casefold()]['directory']
                    log('mkdir_verified', directory)
            launcher = bundle.LAUNCHER
            for path in sorted(set(rows) - {launcher}) + [launcher]:
                item, prior = rows[path], r['files'][path]
                parent, leaf = path.rsplit('/', 1)
                current = names(ftp, '/' + parent).get(leaf.casefold())
                if prior['exists']:
                    assert current and not current['directory'] and current['bytes'] == prior['before_bytes']
                    assert sha(get(ftp, '/' + path, current['bytes'])) == prior['before_sha256'], 'Preflight state changed: ' + path
                    if not prior['changed']:
                        continue
                else:
                    assert current is None, 'Previously absent path appeared: ' + path
                data = z.read(path)
                assert len(data) == item['bytes'] and sha(data) == item['sha256']
                log('write_intent', path, before_sha256=prior.get('before_sha256'), target_sha256=item['sha256'])
                for offset in range(0, max(1, len(data)), 32768):
                    command = ('STOR ' if offset == 0 else 'APPE ') + '/' + path
                    ftp.storbinary(command, io.BytesIO(data[offset:offset + 32768]), 1024)
                assert sha(get(ftp, '/' + path, len(data))) == item['sha256']
                log('write_verified', path, target_sha256=item['sha256'])
            for path, item in rows.items():
                assert sha(get(ftp, '/' + path, item['bytes'])) == item['sha256'], 'Final readback mismatch: ' + path
            log('complete', 'E', files=len(rows), launcher_last=True)
    finally:
        ftp.close()
        os.close(fd)
        lock.unlink()
    print(json.dumps({'completed': True, 'files': len(rows), 'launcher_last': True, 'launch_requested': False}))


if __name__ == '__main__':
    main()
