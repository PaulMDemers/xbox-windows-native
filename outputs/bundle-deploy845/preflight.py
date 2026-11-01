"""Read-only console comparison and private preimage capture. No writes to Xbox."""
import argparse
import ftplib
import hashlib
import json
import os
import shutil
import socket
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'outputs/demo-audio-level256'))
import tester_bundle as bundle
from common001 import ticket, queue


def sha(data):
    return hashlib.sha256(data).hexdigest()


class FTP(ftplib.FTP):
    def ntransfercmd(self, *args, **kwargs):
        sock, size = super().ntransfercmd(*args, **kwargs)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        return sock, size


def names(ftp, path):
    assert path == '/E' or path.startswith('/E/')
    ftp.cwd(path)
    assert ftp.pwd().replace('\\', '/').rstrip('/').lower() == path.lower()
    rows = []
    ftp.retrlines('LIST', rows.append)
    result = {}
    for row in rows:
        fields = row.split(None, 8)
        assert len(fields) == 9
        name = fields[8]
        if name in ('.', '..'):
            continue
        assert '/' not in name and '\\' not in name and name.casefold() not in result
        result[name.casefold()] = {'name': name, 'directory': fields[0].startswith('d'), 'bytes': int(fields[4])}
    return result


def get(ftp, path, expected_size):
    assert path.startswith('/E/') and 0 <= expected_size <= 256 * 1024**2
    data = bytearray()
    def take(block):
        data.extend(block)
        assert len(data) <= expected_size
    ftp.retrbinary('RETR ' + path, take, 65536)
    assert len(data) == expected_size
    return bytes(data)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('archive', type=Path)
    ap.add_argument('expected_sha256')
    ap.add_argument('destination', type=Path, help='new private receipt directory')
    a = ap.parse_args()
    assert not a.destination.exists()
    assert shutil.disk_usage(a.destination.parent).free >= 21 * 1024**3
    archive_hash = bundle.digest(a.archive.read_bytes())
    assert archive_hash == a.expected_sha256
    m = bundle.verify(a.archive)
    assert m['kind'] == 'windows-e-preview' and m['profile'] == 'e-720p'
    files = [x for x in m['files'] if x['path'].startswith('E/')]
    dirs = sorted((x for x in m['directories'] if x == 'E' or x.startswith('E/')), key=lambda p: (p.count('/'), p))
    a.destination.mkdir()
    record = {'archive_sha256': archive_hash, 'completed': False, 'physical_writes': False, 'files': {}, 'directories': {}}
    def save():
        p = a.destination / 'preflight.json'
        tmp = p.with_suffix('.tmp')
        tmp.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
        os.replace(tmp, p)
    save()
    ticket()
    lock = queue / 'bundle845-preflight-active.lock'
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    ftp = FTP()
    try:
        config = json.loads(Path('C:/xwn820/connection.json').read_text())
        assert config['host'] == '192.168.50.66', 'Unexpected console address'
        ftp.connect(config['host'], timeout=15)
        ftp.login(config['user'], config['password'])
        owner = get(ftp, '/E/Applications/XWN16Boot843/owner843.json', 919)
        assert sha(owner) == '8e5505efd515fd1901e5aec3b7b6816e20a261ed1766912ffb0cbd9a1056fe35', 'Unexpected target owner marker'
        record['target_authentication'] = {'host': config['host'], 'owner_sha256': sha(owner), 'owner_bytes': len(owner)}
        save()
        listings = {}
        for directory in dirs:
            if directory == 'E':
                exists = True
            else:
                parent, leaf = directory.rsplit('/', 1)
                row = listings.get(parent, {}).get(leaf.casefold())
                exists = row is not None
                assert not exists or row['directory'], 'Directory collides with file: ' + directory
            record['directories'][directory] = exists
            listings[directory] = names(ftp, '/' + directory) if exists else {}
        for item in files:
            path = item['path']
            parent, leaf = path.rsplit('/', 1)
            row = listings[parent].get(leaf.casefold())
            if row is None:
                record['files'][path] = {'exists': False, 'target_sha256': item['sha256']}
                continue
            assert not row['directory'], 'File collides with directory: ' + path
            # FTP is case-insensitive on FATX; preserve the listed leaf spelling.
            remote = '/' + parent + '/' + row['name']
            data = get(ftp, remote, row['bytes'])
            before = sha(data)
            changed = before != item['sha256'] or len(data) != item['bytes']
            if changed:
                target = a.destination / 'before' / path
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open('xb') as f:
                    f.write(data)
                    f.flush()
                    os.fsync(f.fileno())
                assert sha(target.read_bytes()) == before
            record['files'][path] = {'exists': True, 'before_bytes': len(data), 'before_sha256': before,
                                     'target_sha256': item['sha256'], 'changed': changed}
            if len(record['files']) % 100 == 0:
                save()
        record['completed'] = True
        save()
    except BaseException as exc:
        record['error_type'] = type(exc).__name__
        record['error'] = str(exc)
        save()
        raise
    finally:
        ftp.close()
        os.close(fd)
        lock.unlink()
    print(json.dumps({'completed': True, 'files': len(record['files']),
                      'backed_up': sum(v.get('changed', False) for v in record['files'].values()),
                      'physical_writes': False}))


if __name__ == '__main__':
    main()
