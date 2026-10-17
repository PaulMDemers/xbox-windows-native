"""Read-only hash/process closure for 423/424; not another cold collection."""
import datetime, hashlib, json
from pathlib import Path
K = Path(__file__).resolve().parent
N = K.parent / 'crypto-persistence423'
assert not (K / 'final-review.json').exists() and not (N / 'final-review.json').exists()
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()
load = lambda p: json.loads(p.read_text())
utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
processes = []
for d in Path('/proc').iterdir():
    if not d.name.isdigit(): continue
    try:
        name = (d / 'comm').read_text().strip()
    except (FileNotFoundError, ProcessLookupError): continue
    if name.startswith(('qemu-system', 'qemu-nbd', 'nbdfuse')):
        processes.append({'pid': int(d.name), 'name': name})
assert not processes, processes
mounts = [s for s in Path('/proc/self/mountinfo').read_text().splitlines() if 'crypto423-' in s]
assert not mounts
host = load(K / 'host-closeout001.json')
assert host['xemu_count'] == 0

prep = load(N / 'ntfs-preparation002.json')
ind = load(N / 'ntfs-independent001.json')
assert ind['passed'] and ind['closed'] and ind['disk_unchanged'] and ind['mount_absent']
paths = {Path(prep['source']): prep['source_sha256'],
         Path(prep['path'])/'probe.img': prep['floppy_sha256'],
         Path(prep['path'])/'disk.qcow2': ind['disk_sha256']}
for phase in [1, 2]:
    p = load(N / f'ntfs-phase{phase}.json')
    assert p['closed'] and p['exit_code'] == 0 and not p['deadline']
    assert not any(p.get(n) for n in ['host_kill','host_terminate','host_quit'])
for row in ind['rows']:
    base = Path(ind['private_path'])/'files'
    choices = [p for p in base.rglob('*') if p.is_file() and p.relative_to(base).as_posix().lower() == row['path']]
    assert len(choices) == 1
    assert sha(choices[0]) == row['sha256']
for name, h in prep['inputs'].items(): assert sha(N/name) == h
assembly = load(K / 'assembly002.json')
paths.update({Path(assembly['source']):assembly['source_sha256'], Path(assembly['fixture_path_linux']):assembly['fixture_sha256']})
cases = []
for phase in [1, 2]:
    case = f'emu{phase:03d}'
    a = load(K/case/'audit.json')
    paths[Path('/mnt/e/xwn424/runs')/('nt5-crypto424-'+case)/'hdd.qcow2'] = a['disk_sha256']
    frozen = load(K/case/'frozen.json')
    for name,h in frozen.items(): assert sha(K.parents[1]/name) == h
    cases.append({'case':case, 'closed':a['host_exit']['closed'], 'exit_code':a['host_exit']['exit_code'],
                  'normal_shutdown_delta':a['normal_shutdown_delta'], 'api_errors':a['probe']['api_errors'],
                  'allocation_clean':a['allocation']['allocation_consistent'], 'protected_os_exact':a['protected_os_exact'],
                  'warnings_errors':[(r['source'],r['event_id']) for r in a['warning_error_events']],
                  'frozen_inputs_exact':len(frozen), 'strict_qualification':False})
for p,h in paths.items(): assert sha(p) == h, str(p)
actual = load(K/'actual-review001.json');assert actual['passed']
header = Path('/home/paul/xbox-windows-native/release-readiness403-bootstrap001/RosBE-2.2.1/i386/i686-w64-mingw32/include/winerror.h')
errors = [s for s in header.read_text().splitlines() if any('define '+n+' ' in s for n in ['NTE_FAIL','NTE_BAD_KEYSET','ERROR_FILENAME_EXCED_RANGE','ERROR_FILE_NOT_FOUND'])]
assert len(errors) == 4
common = {'utc':utc, 'all_owned_processes_closed':True, 'wsl_qemu_nbd_fuse_processes':processes,
          'fuse_mounts':mounts, 'host_closeout_sha256':sha(K/'host-closeout001.json'), 'physical_access':False,
          'error_header':{'path':str(header),'sha256':sha(header),'definitions':errors},
          'current_source_fixture_disk_hashes':{str(p):h for p,h in paths.items()}}
n = {**common,'scope':'NTFS two-boot API persistence only; independent selected NTFS-3G content proof',
     'scoped_probe_passed':True,'independent_files_rehashed':len(ind['rows']), 'prepared_inputs_exact':len(prep['inputs']),
     'actual_log_negative_controls_total':actual['malformed_actual_logs_rejected'],
     'limitations':['Eight-file raw-reader mismatch retained; NTFS-3G agrees with prior 7-Zip',
                    'No NTFS allocation ownership audit, COM+ test or public clean-install qualification']}
k = {**common,'scope':'Completed FATX experiment with real API failures; no namespace repair',
     'diagnostic_completed':True,'api_qualification':False,'strict_qualification':False,'cases':cases,
     'actual_review_sha256':sha(K/'actual-review001.json'), 'negative_controls':actual['malformed_actual_logs_rejected'],
     'no_new_build_or_launch':host['c_free_bytes'] < 20*1024**3,
     'limitations':['Exact native failing path/status not traced','PC and Xbox provisioning differ',
                    'No physical access; current demo unchanged']}
for folder,r in [(N,n),(K,k)]:
    r['report_sha256']=sha(folder/'REPORT.md')
    (folder/'final-review.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'closed':True,'disks_and_sources_rehashed':len(paths),'ntfs_independent_files_rehashed':len(ind['rows']),'fatx_api_qualification':False}))
