"""Audit and continue one interrupted E transfer; never launch, delete or retry."""
import argparse
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
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('archive', type=Path)
    p.add_argument('receipt', type=Path)
    a = p.parse_args()
    prior = json.loads((a.receipt / 'preflight.json').read_text())
    assert prior['completed'] and not prior['physical_writes']
    assert sha(a.archive.read_bytes()) == prior['archive_sha256'] == 'b711fe0f7d660f1eb921bbfef902c174bb45616eb6c522ee6971dee48a3ca81d'
    m = bundle.verify(a.archive)
    assert m['kind'] == 'windows-e-preview' and m['profile'] == 'e-720p'
    rows = {x['path']: x for x in m['files'] if x['path'].startswith('E/')}
    dirs = sorted((x for x in m['directories'] if x == 'E' or x.startswith('E/')), key=lambda x: (x.count('/'), x))
    assert set(rows) == set(prior['files']) and set(dirs) == set(prior['directories'])
    journal_path = a.receipt / 'apply.jsonl'
    old = [json.loads(x) for x in journal_path.read_text().splitlines()]
    assert old[0]['kind'] == 'start' and old[0]['archive_sha256'] == prior['archive_sha256']
    intent = {x['path'] for x in old if x['kind'] == 'write_intent'}
    done = {x['path'] for x in old if x['kind'] == 'write_verified'}
    assert len(intent) == len(done) == 609 and intent == done and not any(x['kind'] == 'complete' for x in old)
    assert sum(x['kind'] == 'write_intent' for x in old) == sum(x['kind'] == 'write_verified' for x in old) == 609
    assert all(x['target_sha256'] == rows[x['path']]['sha256'] for x in old if x['kind'] in ('write_intent', 'write_verified'))
    assert bundle.LAUNCHER not in done
    mkdir_intent = {x['path'] for x in old if x['kind'] == 'mkdir_intent'}
    mkdir_done = {x['path'] for x in old if x['kind'] == 'mkdir_verified'}
    assert len(mkdir_intent) == len(mkdir_done) == 3 and mkdir_intent == mkdir_done
    assert mkdir_done == {d for d, exists in prior['directories'].items() if not exists}
    for path, item in rows.items():
        old_file = prior['files'][path]
        assert old_file['target_sha256'] == item['sha256']
        if old_file.get('changed'):
            before = (a.receipt / 'before' / path).read_bytes()
            assert len(before) == old_file['before_bytes'] and sha(before) == old_file['before_sha256']
    capacity_data = (ROOT / 'outputs/boot720-input843/baseline001.json').read_bytes()
    assert sha(capacity_data) == '020028631f8473d05d40856e8c0262b25fd9f5104790578bf55da4e540317b3e'
    capacity = json.loads(capacity_data)['projected_console_reserve']
    cluster = 16384
    alloc = lambda n: ((n + cluster - 1) // cluster) * cluster
    growth = sum(max(0, alloc(item['bytes']) - alloc(prior['files'][path].get('before_bytes', 0))) for path, item in rows.items())
    growth += cluster * len(mkdir_done)
    assert capacity['projected_remaining'] == capacity['last_measured_free'] - capacity['installed_allocation'] - capacity['additional_owned_budget']
    assert growth + capacity['minimum_required'] <= capacity['projected_remaining']
    out = a.receipt / 'resume001.jsonl'
    assert not out.exists(), 'A prior continuation requires manual review'
    ticket()
    lock = queue / 'bundle845-resume-active.lock'
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    ftp = FTP()
    try:
        config = json.loads(Path('C:/xwn820/connection.json').read_text())
        assert config['host'] == prior['target_authentication']['host'] == '192.168.50.66'
        ftp.connect(config['host'], timeout=20)
        ftp.login(config['user'], config['password'])
        assert sha(get(ftp, '/E/Applications/XWN16Boot843/owner843.json', 919)) == prior['target_authentication']['owner_sha256'] == '8e5505efd515fd1901e5aec3b7b6816e20a261ed1766912ffb0cbd9a1056fe35'
        with out.open('xb', buffering=0) as journal, zipfile.ZipFile(a.archive) as z:
            def log(kind, path, **fields):
                journal.write((json.dumps({'kind': kind, 'path': path, **fields}) + '\n').encode())
                os.fsync(journal.fileno())
            log('audit_start', 'E', original_journal_sha256=sha(journal_path.read_bytes()))
            listings = {}
            for directory in dirs:
                if directory != 'E':
                    parent, leaf = directory.rsplit('/', 1)
                    entry = listings[parent].get(leaf.casefold())
                    assert entry and entry['directory'], 'Directory missing: ' + directory
                listings[directory] = names(ftp, '/' + directory)
            for index, (path, item) in enumerate(rows.items(), 1):
                parent, leaf = path.rsplit('/', 1)
                entry = listings[parent].get(leaf.casefold())
                before = prior['files'][path]
                if path in done:
                    assert entry and not entry['directory'] and entry['bytes'] == item['bytes']
                    assert sha(get(ftp, '/' + path, entry['bytes'])) == item['sha256'], 'Written file changed: ' + path
                elif before['exists']:
                    assert entry and not entry['directory'] and entry['bytes'] == before['before_bytes']
                    assert sha(get(ftp, '/' + path, entry['bytes'])) == before['before_sha256'], 'Preimage changed: ' + path
                else:
                    assert entry is None, 'Unwritten file appeared: ' + path
                if index % 100 == 0:
                    log('audit_progress', 'E', files=index)
            log('audit_complete', 'E', files=len(rows), already_written=len(done))
            launcher = bundle.LAUNCHER
            for path in sorted(set(rows) - {launcher}) + [launcher]:
                if path in done:
                    continue
                item, before = rows[path], prior['files'][path]
                if before['exists'] and not before['changed']:
                    continue
                parent, leaf = path.rsplit('/', 1)
                entry = names(ftp, '/' + parent).get(leaf.casefold())
                if before['exists']:
                    assert entry and not entry['directory'] and entry['bytes'] == before['before_bytes']
                    assert sha(get(ftp, '/' + path, entry['bytes'])) == before['before_sha256']
                else:
                    assert entry is None
                data = z.read(path)
                assert len(data) == item['bytes'] and sha(data) == item['sha256']
                log('write_intent', path, target_sha256=item['sha256'])
                for offset in range(0, max(1, len(data)), 32768):
                    ftp.storbinary(('STOR ' if offset == 0 else 'APPE ') + '/' + path,
                                   io.BytesIO(data[offset:offset + 32768]), 1024)
                assert sha(get(ftp, '/' + path, len(data))) == item['sha256']
                log('write_verified', path, target_sha256=item['sha256'])
            for index, (path, item) in enumerate(rows.items(), 1):
                assert sha(get(ftp, '/' + path, item['bytes'])) == item['sha256'], 'Final readback mismatch: ' + path
                if index % 100 == 0:
                    log('readback_progress', 'E', files=index)
            log('complete', 'E', files=len(rows), launcher_last=True, launch_requested=False)
    finally:
        ftp.close()
        os.close(fd)
        lock.unlink()
    print(json.dumps({'completed': True, 'files': len(rows), 'launcher_last': True, 'launch_requested': False}))


if __name__ == '__main__':
    main()
