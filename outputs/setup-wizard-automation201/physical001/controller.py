"""One physical known-wizard cancellation boot; startup-only changes, preserve device policy."""
import argparse, hashlib, importlib.util, json, sys, zipfile
from pathlib import Path

k = Path(__file__).resolve().parent
kit = k.parent
ws = kit.parents[1]
sys.path.insert(0, str(kit.parent / 'device-observation188'))
from atomic_json import write_json
spec = importlib.util.spec_from_file_location('ftp_helpers201', kit.parent / 'fatx0098-soak3/physical.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda b: hashlib.sha256(b).hexdigest()
record = k / 'physical.json'
art = k / 'artifacts/physical'
remote = '/F/xwnwiz201p'
startup = m.startup
test_startup = b'@echo off\r\nC:\\xwnwiz201p\\guardian.exe\r\nexit\r\n'
capture = read(kit.parent / 'video-phase-physical200/capture.json')
mutable = ('/config/system', '/config/software', '/config/default', '/config/sam',
           '/config/security', '/config/sysevent.evt', '/config/appevent.evt',
           '/setupapi.log', '/xwn-video-trace.bin')
fixed = {v['path']: v['sha256'] for v in capture['files']
         if not v['path'].endswith(mutable) and v['path'] != startup}
for review in ['build-review006.json', 'guardian-physical-review001.json']:
    for name, row in read(kit / review)['providers'].items():
        path = '/F/winnt/system32/' + name
        assert path not in fixed or fixed[path] == row['sha256']
        fixed[path] = row['sha256']
aux = [('startup.cmd', startup)] + [(n, '/F/winnt/system32/config/' + n) for n in
      ['system', 'software', 'default', 'sam', 'security', 'sysevent.evt', 'appevent.evt']]
aux += [('setupapi.log', '/F/winnt/setupapi.log'), ('trace.bin', '/F/winnt/system32/xwn-video-trace.bin')]
helpers = {'wizard.exe': kit / 'artifacts/build006/wizard.exe',
           'guardian.exe': kit / 'artifacts/guardian-physical001/guardian.exe'}


def save(r):
    write_json(record, r)


def preserve(name, data):
    p = art / name
    if p.exists():
        assert p.read_bytes() == data, 'Changed preserved evidence: ' + name
    else:
        p.write_bytes(data)
    return dict(path=p.relative_to(ws).as_posix(), bytes=len(data), sha256=sha(data))


def checks(f):
    rows = []
    for path, expected in fixed.items():
        actual = sha(m.get(f, path))
        assert actual == expected, 'Baseline/provider drift: ' + path
        rows.append(dict(path=path, sha256=actual))
    return rows


def ready():
    r = read(k / 'ready.json')
    assert r['prepared'] and not r['physical_qualified']
    for path, digest in r['pins'].items():
        assert sha((ws / path).read_bytes()) == digest, path
    for case in ['cancel006', 'cancel007']:
        assert read(kit / case / 'closure.json')['closed']
        assert read(kit / case / 'audit.json')['diagnostic_usable']
    prior = read(kit.parent / 'video-phase-physical200/candidate001/closure.json')
    assert prior['closed'] and prior['baseline_restored']
    assert read(kit.parent / 'video-phase-physical200/candidate001/restored-verification.json')['passed']


def launch():
    ready()
    assert not record.exists(), 'Never repeat a launch or uncertain launch'
    art.mkdir(parents=True, exist_ok=False)
    with m.connect() as f:
        m.owner(f)
        baseline = checks(f)
        m.missing(f, remote)
        original = m.get(f, startup)
        assert sha(original) == next(v['sha256'] for v in capture['files'] if v['path'] == startup)
        assert sha(m.get(f, '/F/winnt/system32/config/system')) == next(
            v['sha256'] for v in capture['files'] if v['path'].endswith('/config/system'))
        r = dict(scope=__doc__, created_utc=m.utc(), launch_requested=False, startup_enabled=False,
                 physical_result=True, physical_qualified=False, release_qualified=False,
                 keyboard_persistently_unplugged_user_authorization=True,
                 before_checks=baseline, before={}, after={},
                 helper_hashes={name: sha(path.read_bytes()) for name, path in helpers.items()})
        for name, path in aux:
            r['before'][name] = preserve('before-' + name, m.get(f, path))
        for i, path in enumerate(fixed):
            r['before'][path] = preserve('before-protected-' + str(i), m.get(f, path))
        save(r)
        backup = art / 'rollback201.zip'
        files = sorted(art.glob('before-*'))
        with zipfile.ZipFile(backup, 'x', compression=zipfile.ZIP_DEFLATED) as z:
            for path in files:
                z.writestr(path.name, path.read_bytes())
        with zipfile.ZipFile(backup) as z:
            assert z.namelist() == [p.name for p in files]
            assert all(z.read(p.name) == p.read_bytes() for p in files)
        r.update(rollback_sha256=sha(backup.read_bytes()), rollback_entries=len(files))
        save(r)
        try:
            f.mkd(remote)
            for name, path in helpers.items():
                m.put(f, remote + '/' + name, path.read_bytes())
            m.put(f, remote + '/normal-startup.cmd', original)
            m.put(f, remote + '/rollback201.zip', backup.read_bytes())
            m.put(f, startup, test_startup)
            r['startup_enabled'] = True
            save(r)
        except Exception as exc:
            r['staging_failure'] = type(exc).__name__
            save(r)
            m.put(f, startup, original)
            r['startup_enabled'] = False
            save(r)
            raise
        r.update(launch_requested=True, launch_utc=m.utc(),
                 command=r'SITE EXEC E:\Applications\XWNFBoot\default.xbe')
        save(r)
        try:
            r['reply'] = f.sendcmd(r['command'])
        except Exception as exc:
            r['reply_uncertain'] = type(exc).__name__
        save(r)
        print('Single201 physical cancellation requested; never relaunch', flush=True)


def collect():
    r = read(record)
    assert r['launch_requested'] and not r.get('collected_utc') and not r.get('collection_failure')
    original = (art / 'before-startup.cmd').read_bytes()
    assert sha(original) == r['before']['startup.cmd']['sha256']
    with m.connect() as f:
        m.owner(f)
        assert m.get(f, startup) in [test_startup, original], 'Unknown startup; preserve it'
        # FIRST restore and readback normal startup; no SYSTEM rollback or device edits.
        m.put(f, startup, original)
        r.update(startup_enabled=False, startup_restored_utc=m.utc())
        save(r)
        try:
            for name, path in [('wizard201.log', remote + '/wizard201.log'),
                               ('guardian201.log', remote + '/guardian201.log'), *aux,
                               *[(path, path) for path in fixed]]:
                data = m.get(f, path, optional=name in ['wizard201.log', 'guardian201.log'])
                filename = 'after-protected-' + str(len(r['after'])) if name.startswith('/') else 'after-' + name
                r['after'][name] = None if data is None else preserve(filename, data)
                save(r)
            r['after_checks'] = checks(f)
            r['helpers_exact'] = all(sha(m.get(f, remote + '/' + name)) == digest
                                     for name, digest in r['helper_hashes'].items())
            r['startup_backup_exact'] = m.get(f, remote + '/normal-startup.cmd') == original
            r['rollback_exact'] = sha(m.get(f, remote + '/rollback201.zip')) == r['rollback_sha256']
            r['startup_restored_verified'] = m.get(f, startup) == original
            r['collected_utc'] = m.utc()
            save(r)
        except Exception as exc:
            r['collection_failure'] = type(exc).__name__
            save(r)
            raise
        print('201 normal startup restored FIRST; physical logs/hives/events preserved', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['launch', 'collect'])
    args = parser.parse_args()
    launch() if args.action == 'launch' else collect()
