"""One bounded 845 launch after completed apply; never retry an accepted or uncertain command."""
import argparse
import datetime
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'outputs/demo-audio-level256'))
import tester_bundle as bundle
from common001 import ticket, queue
from preflight import FTP, get, sha

ARCHIVE_SHA256 = 'b711fe0f7d660f1eb921bbfef902c174bb45616eb6c522ee6971dee48a3ca81d'
OWNER_SHA256 = '8e5505efd515fd1901e5aec3b7b6816e20a261ed1766912ffb0cbd9a1056fe35'
COMMAND = r'SITE EXEC E:\Applications\XWNEBoot\default.xbe'
EXPECTED = {
    'E/Applications/XWNEBoot/default.xbe': '099c540a91ab1c0975f084fc92ebf9ae58171b12a1f8eb339d28cd9b5a40b4d2',
    'E/Applications/XWNEBoot/freeldr.sys': '721cf348903138773854b3dd3dce336cb660610d8d85673f3105d8c26aa13d9e',
    'E/Applications/XWNEBoot/rosload.exe': 'c78576199f6cb9effdfd736b787614ce19dd023d2066509104364816443dc687',
    'E/Applications/XWNEBoot/freeldr.ini': '5d003852c683031a90b8ab7de21077e0ee9133501fa847cf18a9544212e5124c',
    'E/Applications/XWNEBoot/loader/halxboxnt5.dll': 'a3a84368d59936dfa6bbcdc6d5839d57b886342211142d305e9dde941e4d1648',
    'E/Applications/XWNEBoot/loader/xboxbvid.dll': '0c8f5d494016a72e098134072d340aa83252fada2739b538b9be5a633d20623f',
    'E/Applications/XWNEBoot/loader/xwnfatx.sys': '3b2179ecec681cd91bc910a6178956d660f7bac18aa69bf6eafdb9f483a9af2c',
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('archive', type=Path)
    ap.add_argument('receipt', type=Path, help='completed 845 preflight and apply receipt')
    a = ap.parse_args()
    launch_path = a.receipt / 'launch845.jsonl'
    assert not launch_path.exists(), 'Prior launch intent exists; never retry'
    pre = json.loads((a.receipt / 'preflight.json').read_text(encoding='utf-8'))
    assert pre['completed'] and not pre['physical_writes'] and pre['archive_sha256'] == ARCHIVE_SHA256
    journal = [json.loads(line) for line in (a.receipt / 'apply.jsonl').read_text(encoding='utf-8').splitlines()]
    assert journal and journal[0]['kind'] == 'start' and journal[0]['archive_sha256'] == ARCHIVE_SHA256
    assert journal[-1]['kind'] == 'complete' and journal[-1]['path'] == 'E' and journal[-1]['launcher_last'] is True
    assert sum(row['kind'] == 'complete' for row in journal) == 1
    assert sha(a.archive.read_bytes()) == ARCHIVE_SHA256
    manifest = bundle.verify(a.archive)
    assert manifest['kind'] == 'windows-e-preview' and manifest['profile'] == 'e-720p'
    files = {row['path']: row for row in manifest['files'] if row['path'].startswith('E/')}
    assert set(files) == set(pre['files']) and journal[-1]['files'] == len(files)
    assert all(files[path]['sha256'] == digest == pre['files'][path]['target_sha256'] for path, digest in EXPECTED.items())
    # Apply logs all changed/new writes as intent followed by verification. Every
    # unchanged file was verified in its final full readback before complete.
    intents = [(r['path'], r['target_sha256']) for r in journal if r['kind'] == 'write_intent']
    verified = [(r['path'], r['target_sha256']) for r in journal if r['kind'] == 'write_verified']
    assert intents == verified and len({p for p, _ in intents}) == len(intents)
    assert all(path in files and files[path]['sha256'] == digest for path, digest in intents)
    assert not launch_path.exists()
    ticket()
    lock = queue / 'bundle845-launch-active.lock'
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    ftp = FTP()
    try:
        config = json.loads(Path('C:/xwn820/connection.json').read_text())
        assert config['host'] == pre['target_authentication']['host'] == '192.168.50.66'
        ftp.connect(config['host'], timeout=15)
        ftp.login(config['user'], config['password'])
        owner = get(ftp, '/E/Applications/XWN16Boot843/owner843.json', 919)
        assert sha(owner) == pre['target_authentication']['owner_sha256'] == OWNER_SHA256
        checked = {}
        for path, digest in EXPECTED.items():
            item = files[path]
            data = get(ftp, '/' + path, item['bytes'])
            assert sha(data) == digest, 'Target changed: ' + path
            checked[path] = digest
        # Exclusive creation and fsync happen before the command can leave the host.
        with launch_path.open('xb', buffering=0) as log:
            def record(row):
                log.write((json.dumps(row, sort_keys=True) + '\n').encode())
                os.fsync(log.fileno())
            record({'kind': 'intent', 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    'host': config['host'], 'command': COMMAND, 'archive_sha256': ARCHIVE_SHA256,
                    'owner_sha256': OWNER_SHA256, 'checked': checked,
                    'automatic_retry': False, 'expected_return': 'Windows remains running; dashboard return is not assumed'})
            ftp.sock.settimeout(20)
            try:
                reply = ftp.sendcmd(COMMAND)
                record({'kind': 'reply', 'reply': reply})
            except Exception as exc:
                record({'kind': 'reply_uncertain', 'error_type': type(exc).__name__})
    finally:
        ftp.close()
        os.close(fd)
        lock.unlink()


if __name__ == '__main__':
    main()


