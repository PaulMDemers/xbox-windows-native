"""Verify closed owned phases and preserve private evidence identities."""
import hashlib, json, subprocess
from pathlib import Path
K = Path(__file__).resolve().parent
W = K.parents[1]
P = Path('/home/paul/xbox-windows-native/clean-media404-oem001')
def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()
read = lambda p: json.loads(p.read_text())
assert not (K / 'closure001.json').exists()
phases = [read(K / f'oem001-phase{n:02d}.json') for n in range(1, 5)]
assert all(r['closed'] and r['exit_code'] == 0 and not r['deadline'] and not any(r.get(n) for n in ['host_quit','host_terminate','host_kill']) for r in phases)
assert not any(P.glob('phase*/qmp.sock'))
assert sha(P / 'disk.qcow2') == phases[-1]['disk_sha256']
prep = read(K / 'preparation001.json')
assert sha(P / 'answer.img') == prep['answer_sha256']
for p, h in prep['runtime_pins'].items():
    assert sha(Path(p)) == h
assert sha(W / 'outputs/Windows 2000 (SP4).iso') == prep['iso_sha256']
probe = Path('/home/paul/xbox-windows-native/clean-media404-build002/PROBE.EXE')
assert sha(probe) == prep['probe_sha256']
private = {}
for p in P.rglob('*'):
    if p.is_file():
        assert p.suffix != '.raw', 'Disposable RAW still present'
        private[p.relative_to(P).as_posix()] = dict(bytes=p.stat().st_size, sha256=sha(p))
with (K / 'private-evidence001.json').open('x') as f:
    json.dump(dict(private_root=str(P), files=private, proprietary_files_not_for_distribution=True), f, indent=2)
result = dict(owned_guest_closed=True, phase_exit_codes=[r['exit_code'] for r in phases],
              all_guest_requested_exits=True, no_force_or_timeout=True,
              final_disk_sha256=phases[-1]['disk_sha256'], private_files_rehashed=len(private),
              clean_pc_install_scoped_passed=read(K / 'qualification001.json')['clean_pc_install_scoped_passed'],
              strict_clean_pc_passed=False, automatic_handoff_failed=True, typed_decode_failed=True,
              physical_access=False, fresh_xbox_assembly_qualified=False,
              never_relaunch_or_recollect_completed_phases=True)
with (K / 'closure001.json').open('x') as f:
    json.dump(result, f, indent=2)
print(json.dumps(result))
