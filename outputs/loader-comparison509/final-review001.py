"""Independent record closure and exact correction scope; no network or runtime."""
import datetime,hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'final-review.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((K/'review002.json').read_text(encoding='utf-8'))
assert r['passed'] and r['negative_controls']==993 and len(r['images'])==6 and len(r['physical_joins'])==5
assert (K/'review002.py').read_bytes()==(K/'review001.py').read_bytes().replace(b"OUT=K/'review001.json'",b"OUT=K/'review002.json'").replace(b"'blend-precision487','stage001.json'",b"'blend-precision487','physical001-stage.json'")
for n,h in r['source_pins'].items():assert sha(Path(n))==h,n
cmd='Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -like "xemu*" -or $_.ProcessName -like "qemu*" } | Select-Object Id,ProcessName | ConvertTo-Json -Compress'
live=subprocess.run(['pwsh','-NoProfile','-Command',cmd],capture_output=True,text=True,check=True,timeout=20).stdout.strip();assert not live
q=subprocess.run(['wsl','-d','Ubuntu','--','pgrep','-a','^qemu-system'],capture_output=True,text=True,timeout=20);assert q.returncode==1 and not q.stdout.strip()
v=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),all_original_inputs_rehashed=True,pins=len(r['source_pins']),negative_controls=993,images=6,physical_build_cold_joins=5,
 only_review_correction='historical stage-record filename and new output ID',original_review_failure_preserved=True,
 no_build_or_guest_or_physical_access=True,all_owned_subprocesses_closed=True,windows_emulators=[],wsl_qemu=[],queued_launch=False,
 physical_cause_established=False,physical_LED_observation='508 pending; unknown',
 source_files={str(p):sha(p) for p in K.iterdir() if p.is_file()})
out.write_bytes((json.dumps(v,indent=2)+'\n').encode());print(json.dumps({n:v[n] for n in ['passed','pins','negative_controls','images','physical_build_cold_joins']}))
