"""One-shot E-only installation/launch, or read-only collection, of the FAT snapshot."""
import argparse, datetime, ftplib, hashlib, io, json, os, pathlib, re

k = pathlib.Path(__file__).resolve().parent
p = k.parent / 'native-windows-physical-f'
record = k / 'physical-snapshot.json'
remote = '/E/Applications/XWNFatRO'
sha = lambda b: hashlib.sha256(b).hexdigest()
utc = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
parser = argparse.ArgumentParser()
parser.add_argument('action', choices=['launch', 'collect'])
args = parser.parse_args()

def get(f, path):
    b = io.BytesIO()
    f.retrbinary('RETR ' + path, b.write)
    return b.getvalue()

def save():
    record.write_text(json.dumps(r, indent=2) + '\n')

with ftplib.FTP() as f:
    f.connect('192.168.50.242', timeout=20)
    f.login('xbox', os.environ['XWN_FTP_PASSWORD'])
    ownership = json.loads((p / 'physical-cache-preflight.json').read_text())['ownership_marker']
    assert json.loads(get(f, '/F/xwn-deploy-v1.json')) == ownership
    if args.action == 'launch':
        assert not record.exists(), 'Never repeat an existing launch'
        validation = json.loads((k / 'validation.json').read_text())
        xbe = (k / 'artifacts/default.xbe').read_bytes()
        assert validation['emulator_snapshot_passed']
        assert sha(xbe) == validation['xbe_sha256']
        cycle = json.loads((p / 'physical-cycle-013.json').read_text())
        assert not cycle['startup_restart_enabled']
        f.cwd('/E/Applications')
        assert not any(n.replace('\\', '/').rstrip('/').split('/')[-1].lower() == 'xwnfatro' for n in f.nlst())
        r = dict(scope=__doc__, host=f.host, remote_directory=remote,
                 xbe_sha256=sha(xbe), created_utc=utc(), launch_attempted=False,
                 source_partition_access='GENERIC_READ only', output_partition='E')
        save()
        f.mkd(remote)
        marker = json.dumps({'project':'xbox-windows-native','purpose':'cycle013-readonly-fat-snapshot','xbe_sha256':sha(xbe)}).encode()
        for name, data in [('owner.json', marker), ('default.xbe', xbe)]:
            f.storbinary('STOR ' + remote + '/' + name, io.BytesIO(data))
            assert get(f, remote + '/' + name) == data
        r.update(launch_attempted=True, launch_utc=utc(), command=r'SITE EXEC E:\Applications\XWNFatRO\default.xbe')
        save()
        try:
            r['reply'] = f.sendcmd(r['command'])
        except (EOFError, OSError) as e:
            r['uncertain_reply'] = repr(e)
        save()
        print(json.dumps(r, indent=2))
    else:
        r = json.loads(record.read_text())
        assert r['launch_attempted']
        assert not r.get('collected_utc'), 'Preserve completed evidence'
        assert sha(get(f, remote + '/default.xbe')) == r['xbe_sha256']
        out = k / 'artifacts/physical-013'
        out.mkdir(exist_ok=True)
        f.cwd(remote)
        names = [n.replace('\\', '/').rstrip('/').split('/')[-1] for n in f.nlst()]
        r['files'] = []
        for name in names:
            if name.lower() not in ['snapshot.txt','fat-metadata.bin'] and not re.fullmatch(r'cluster-[0-9a-fA-F]{8}\.bin', name):
                continue
            data = get(f, name)
            path = out / name.lower()
            if path.exists():
                assert path.read_bytes() == data
            else:
                path.write_bytes(data)
            r['files'].append(dict(name=name, bytes=len(data), sha256=sha(data)))
        report = (out / 'snapshot.txt').read_text()
        r.update(report=report, collected_utc=utc(), snapshot_completed='SNAPSHOT_COMPLETE success=1' in report)
        save()
        print(report)
