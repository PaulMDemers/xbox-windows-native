"""Record native emulator evidence without claiming unsupported dashboard FTP access."""
import pathlib,json,hashlib,datetime
k=pathlib.Path(__file__).resolve().parent;ws=k.parent.parent
run=ws/'work/runs/nt5-physical-f-package-003'
a=json.loads((k.parent/'native-windows-extended-storage/nt5-physical-f-package-003-cold-audit.json').read_text())
fixture=json.loads((k/'emulator-fixture-003.json').read_text())
inputs=json.loads((run/'input-hashes.json').read_text())
assert any(v['Hash'].lower()==fixture['sha256'] for v in inputs)
assert a['passed'] and a['native_probe']['passed'] and (run/'cleanup.json').exists()
assert json.loads((run/'state-075.json').read_text())['status']=='shell_running'
r=dict(a['native_probe'],utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),run=run.name,
 scope='Native Windows result retrieved by read-only cold audit after observed normal restart; emulator only',
 fixture_sha256=fixture['sha256'],ftp_report_retrieved=False,
 ftp_limitation='Complex4627 dashboard reports 122195 MiB and empty F; native Windows and offline audit see the large partition correctly. Physical UnleashX supports F and the staged files.',
 desktop_observed=True,dashboard_restart_observed=True,cold_audit_passed=True,
 capture_limitation='Runtime capture timed out after normal reboot; screenshots and cold audit retained.')
r['screenshots']={n:hashlib.sha256((run/n).read_bytes()).hexdigest() for n in ['frame-075.png','frame-120.png','frame-135.png']}
(k/'emulator-cycle.json').write_text(json.dumps(r,indent=2)+'\n');print(r['log'])
