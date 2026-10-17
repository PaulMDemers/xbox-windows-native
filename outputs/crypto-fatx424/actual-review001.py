"""Review CLOSED results and mutate actual logs; never launches or recollects a guest."""
import ast, hashlib, json, re, sys
from pathlib import Path

K = Path(__file__).resolve().parent
W = K.parents[1]
N = W / 'outputs/crypto-persistence423'
sys.path.insert(0, str(N))
from results import decode

dest = K / 'actual-review001.json'
assert not dest.exists()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
records = []
rejections = 0
def reject(data, phase):
    global rejections
    try:
        decode(data, phase)
    except (AssertionError, KeyError, ValueError, UnicodeError):
        rejections += 1
        return
    raise AssertionError('Malformed actual log accepted')

for kind in ['ntfs', 'fatx']:
    for phase, name in [(1, 'create.log'), (2, 'reopen.log')]:
        if kind == 'ntfs':
            p = Path('/home/paul/xbox-windows-native/crypto423-independent001/files/XWN423') / name
            if not p.exists():
                candidates = list(Path('/home/paul/xbox-windows-native/crypto423-independent001/files').rglob(name))
                assert len(candidates) == 1
                p = candidates[0]
            expected = json.loads((N / 'ntfs-independent001.json').read_text())['probe'][str(phase)]
        else:
            p = Path('/mnt/e/xwn424') / f'cold{phase}' / 'after' / name
            expected = json.loads((K / f'emu{phase:03d}/audit.json').read_text())['probe']
        data = p.read_bytes()
        actual = decode(data, phase)
        assert json.loads(json.dumps(actual)) == expected
        assert actual['all_api_operations_passed'] == (kind == 'ntfs')
        lines = data.splitlines(keepends=True)
        for i in range(len(lines)):
            reject(b''.join(lines[:i] + lines[i+1:]), phase)
            reject(b''.join(lines[:i] + [lines[i], lines[i]] + lines[i+1:]), phase)
        reject(data[:-1], phase)
        reject(data.replace(b'probe.complete=423', b'probe.complete=424'), phase)
        reject(data + b'unknown.field=0\r\n', phase)
        reject(data, 3-phase)
        reject(re.sub(rb'probe.api_failures=\d+', b'probe.api_failures=4294967295', data), phase)
        if kind == 'fatx':
            reject(data.replace(b'probe.api_failures=3', b'probe.api_failures=0'), phase)
            assert len(actual['api_errors']) == 3
            assert actual['values']['dpapi_machine.exact_plaintext'] == 0
            assert actual['values']['rsa_user.acquire'] == 206
            assert actual['values']['rsa_machine.acquire'] == (0x80090020 if phase == 1 else 0x80090016)
            assert actual['values']['dpapi_user.' + ('protect' if phase == 1 else 'load_blob')] == (206 if phase == 1 else 2)
            assert actual['name_errors'] == {'41': 0, '42': 0, '43': 206 if phase == 1 else 2, '69': 206 if phase == 1 else 2}
        records.append({'kind': kind, 'phase': phase, 'path': str(p), 'sha256': sha(p), 'bytes': len(data), 'result': actual})

pins = []
for case in ['emu001', 'emu002']:
    frozen = json.loads((K / case / 'frozen.json').read_text())
    for path, h in frozen.items():
        assert sha(W / path) == h, path
    a = json.loads((K / case / 'audit.json').read_text())
    assert a['host_exit']['passed'] and a['host_exit']['exit_code'] == 0
    assert not a['host_exit']['fallback_kill'] and not a['host_exit']['timeout']
    assert a['normal_shutdown_delta'] == 1 and a['event_history']
    assert a['protected_os_exact'] and a['staged_exact']
    assert a['source_unchanged'] and a['audit_unchanged']
    assert a['allocation']['allocation_consistent'] and not a['allocation']['errors']
    assert a['allocation']['orphan_cluster_count'] == 0
    assert len(a['hives']) == 5 and all(h['clean'] and h['independent_raw_values_agree'] for h in a['hives'])
    assert a['strict_qualification'] is False
    pins.append({'case': case, 'frozen_exact': len(frozen), 'audit_sha256': sha(K / case / 'audit.json')})

preparation = json.loads((N / 'ntfs-preparation002.json').read_text())
for path, h in preparation['inputs'].items():
    assert sha(N / path) == h, path
build = json.loads((N / 'build001.json').read_text())
assert sha(N / 'probe.c') == build['source_sha256']
for row in build['rows']:
    assert sha(Path(row['path'])) == row['sha256']
for root in [N, K]:
    for p in root.rglob('*.py'):
        ast.parse(p.read_bytes().decode('utf-8-sig'))

captures = {}
for root in [Path('/mnt/e/xwn424/runs/nt5-crypto424-emu001'), Path('/mnt/e/xwn424/runs/nt5-crypto424-emu002')]:
    for p in root.iterdir():
        if p.suffix in ['.png', '.json']:
            captures[str(p)] = sha(p)
record = {'scope': 'Closed evidence and actual-log negative controls; no guest operation', 'passed': True,
          'logs': records, 'malformed_actual_logs_rejected': rejections, 'fatx_frozen_inputs': pins,
          'ntfs_preparation_inputs_exact': len(preparation['inputs']), 'native_binaries_exact': len(build['rows']),
          'private_capture_hashes': captures, 'strict_fatx_qualification': False,
          'limitations': ['No actual file-call trace or long-name fix', 'Different PC NTFS and Xbox FATX environments',
                         'Machine RSA generic creation failure does not identify its filename', 'No physical access']}
dest.write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'passed': True, 'actual_logs': len(records), 'negative_controls': rejections, 'frozen_inputs': pins}))
