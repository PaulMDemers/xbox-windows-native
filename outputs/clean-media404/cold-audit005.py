"""Extract selected evidence from a CLOSED clean PC disk; never boot or modify it."""
import argparse, hashlib, json, struct, subprocess, sys
from pathlib import Path

K = Path(__file__).resolve().parent
W = K.parents[1]
P = Path('/home/paul/xbox-windows-native/clean-media404-oem001')
sys.path.insert(0, str(W / 'work/python-packages'))
from Registry import Registry
import pefile
sys.path.insert(0, str(W / 'tools'))
from build_space import require_space

def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', type=int, choices=[3, 4], required=True)
    args = parser.parse_args()
    state = json.loads((K / f'oem001-phase{args.phase:02d}.json').read_text())
    assert state['closed'] and state['exit_code'] == 0 and not state['deadline']
    assert not any(P.glob('phase*/qmp.sock'))
    output = K / f'cold-phase{args.phase:02d}.json'
    assert not output.exists()
    target = P / f'cold-phase{args.phase:02d}'
    resume = args.phase == 3
    disk = P / 'disk.qcow2'
    before = sha(disk)
    assert before == state['disk_sha256']
    raw = target / 'disk.raw'
    extracted = target / 'files'
    if resume:
        assert target.exists() and raw.is_file() and extracted.is_dir()
        space = {'scope': 'Reused completed001 read-only conversion/extraction; no duplicate conversion'}
        check_data = json.loads((target / 'qcow-check.json').read_text())
        with raw.open('rb') as f:
            mbr = f.read(512)
        partitions = []
        for i in range(4):
            e = mbr[446 + 16*i:462 + 16*i]
            partitions.append(dict(index=i+1, boot=e[0], type=e[4], start_lba=struct.unpack_from('<I', e, 8)[0], sectors=struct.unpack_from('<I', e, 12)[0]))
    else:
        # A 2 GiB disposable conversion plus selected evidence must retain 20 GiB.
        from space005 import preflight
        space = preflight(P)
        target.mkdir()
        disk = P / 'disk.qcow2'
        before = sha(disk)
        assert before == state['disk_sha256']
        raw = target / 'disk.raw'
        extracted = target / 'files'
        files = ['boot.ini', 'ntldr', 'ntdetect.com', 'XWN404.EXE',
                 'XWN404-SETUP.TXT', 'XWN404-BOOT.TXT',
                 'WINNT/system32/config/*', 'WINNT/system32/ntoskrnl.exe',
                 'WINNT/system32/hal.dll', 'WINNT/system32/bootvid.dll',
                 'WINNT/setupact.log', 'WINNT/setuperr.log', 'WINNT/setupapi.log']
        check = subprocess.run(['qemu-img', 'check', '--output=json', str(disk)],
                               capture_output=True, text=True)
        (target / 'qcow-check.json').write_text(check.stdout)
        assert check.returncode == 0, check.stderr
        subprocess.run(['qemu-img', 'convert', '-S', '4k', '-O', 'raw', str(disk), str(raw)], check=True)
        with raw.open('rb') as f:
            mbr = f.read(512)
        assert mbr[510:512] == b'\x55\xaa'
        partitions = []
        for i in range(4):
            e = mbr[446 + 16*i:462 + 16*i]
            partitions.append(dict(index=i+1, boot=e[0], type=e[4],
                                   start_lba=struct.unpack_from('<I', e, 8)[0],
                                   sectors=struct.unpack_from('<I', e, 12)[0]))
        tool = '/home/paul/xbox-windows-native/toolchains/7zip/root/usr/lib/7zip/7z'
        with (target / 'extract.log').open('xb') as log:
            subprocess.run([tool, 'x', '-y', '-ssc-', '-o' + str(extracted), str(raw), *files],
                           check=True, stdout=log, stderr=subprocess.STDOUT)
        check_data = json.loads(check.stdout)
    paths = {p.relative_to(extracted).as_posix().lower(): p for p in extracted.rglob('*') if p.is_file()}
    def path(name):
        return paths[name.lower()]
    assert raw.stat().st_blocks * 512 <= space['sparse_raw_allocated_upper_bound']
    assert sum(p.stat().st_size for p in paths.values()) < space['extraction_and_metadata_budget']
    records = {name: dict(bytes=p.stat().st_size, sha256=sha(p)) for name, p in paths.items()}
    markers = {}
    for name in ['xwn404-setup.txt', 'xwn404-boot.txt']:
        if name in paths:
            markers[name] = dict(line.split('=', 1) for line in path(name).read_text().splitlines() if '=' in line)
    from hive_audit004 import audit
    hives = [audit(path('winnt/system32/config/' + name)) for name in ['system', 'software', 'sam', 'security', 'default']]
    system = Registry.Registry(str(path('winnt/system32/config/system')))
    setup = {v.name(): v.value() for v in system.open('Setup').values()
             if v.name() in ['SystemSetupInProgress', 'SetupType', 'CmdLine']}
    versions = {}
    for name in ['ntoskrnl.exe', 'hal.dll', 'bootvid.dll']:
        p = path('winnt/system32/' + name)
        pe = pefile.PE(str(p)); v = pe.VS_FIXEDFILEINFO[0]
        versions[name] = dict(sha256=sha(p), version='.'.join(map(str, [v.FileVersionMS >> 16,
            v.FileVersionMS & 65535, v.FileVersionLS >> 16, v.FileVersionLS & 65535])))
        pe.close()
    events = {}
    for name, label in [('sysevent.evt', 'system'), ('appevent.evt', 'application')]:
        dest = target / (label + '-events.json')
        subprocess.run([sys.executable, str(K.parent / 'native-windows-physical-f/decode-legacy-events.py'),
                        str(path('winnt/system32/config/' + name)), '--output', str(dest)],
                       check=True, stdout=subprocess.DEVNULL)
        rows = json.loads(dest.read_text())['records']
        events[label] = [dict(record=r['record'], source=r['source'], event_id=r['event_id'], type=r['type']) for r in rows]
    report = dict(phase=args.phase, disk_sha256=before, unchanged_by_audit=sha(disk) == before,
                  qcow_check=check_data, partitions=partitions, space=space,
                  private_extraction=str(target), files=records, markers=markers,
                  hives=hives, setup=setup, versions=versions, events=events,
                  normal_shutdown_events=sum(r['source'] == 'EventLog' and r['event_id'] == 6006 for r in events['system']),
                  warnings_errors=[r for rows in events.values() for r in rows if r['type'] in [1, 2]],
                  raw_sha256=sha(raw), raw_copy_removed_after_verified_extraction=False,
                  typed_decode_complete=all(h['typed_decode_complete'] for h in hives),
                  scope='Independent raw hive readers agree; original typed-decoder failure retained. Selected-file and full five-hive parse; not a complete NTFS allocation/file-content audit or Xbox qualification')
    # Only this newly created disposable conversion; preserve the actual disk/evidence.
    assert raw.resolve().parent == target.resolve() and target.resolve().parent == P.resolve()
    raw.unlink()
    report['raw_copy_removed_after_verified_extraction'] = True
    report['final_space'] = require_space(P)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['phase', 'setup', 'markers', 'normal_shutdown_events', 'warnings_errors']}))

if __name__ == '__main__':
    main()
