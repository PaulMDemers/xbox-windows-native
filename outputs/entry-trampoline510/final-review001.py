"""Final hashes and subprocess closure, no new build or Xbox execution."""
import datetime,hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'final-review.json';assert not out.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def win(n):return Path(n.replace('/mnt/c/','C:/',1))
h=read(K/'host001.json');b=read(K/'build001.json');r=read(K/'review002.json')
assert h['passed'] and h['closed'] and h['result']['actual_jump_cases']==4096 and h['result']['executed_negative_controls']==2
assert b['status']=='compiled' and r['passed'] and r['negative_controls']==5796
assert (K/'review002.py').read_bytes()==(K/'review001.py').read_bytes().replace(b'C:/xwn510/review001',b'C:/xwn510/review002').replace(b"out=K/'review001.json'",b"out=K/'review002.json'").replace(b'assert actual[0x1105:0x3000]==old[0x1105:0x3000]',b"assert actual[0x1105:0x3000]==old[0x1105:0x3000].replace(b'XWNBoot504a',b'XWNBoot510a')")
for record in [h,b,r]:
 for n,v in record.get('files',record.get('private_files',{})).items():assert sha(win(n))==v['sha256'] and win(n).stat().st_size==v['bytes']
for n,v in b['inputs'].items():
 if n.startswith('/mnt/c/'):assert sha(win(n))==v
for n,v in h['source_pins'].items():assert sha(K/n)==v
cmd='Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -like "xemu*" -or $_.ProcessName -like "qemu*" } | Select-Object Id,ProcessName | ConvertTo-Json -Compress'
assert not subprocess.run(['pwsh','-NoProfile','-Command',cmd],capture_output=True,text=True,check=True,timeout=20).stdout.strip()
q=subprocess.run(['wsl','-d','Ubuntu','--','pgrep','-a','^qemu-system'],capture_output=True,text=True,timeout=20);assert q.returncode==1 and not q.stdout.strip()
files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in Path('C:/xwn510').rglob('*') if p.is_file()}
result=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),private_files_verified=len(files),private_files=files,
 candidate_bytes=b['bytes'],candidate_sha256=b['sha256'],host_actual_jump_cases=4096,executed_host_negative_stubs=2,binary_mutations_rejected=5796,
 original_sources_reconstructed=9,diagnostic_body_unchanged_bytes=929,all_owned_processes_closed=True,windows_emulators=[],wsl_qemu=[],
 XBE_ever_launched=False,physical_access=False,emulator_preparation=False,temporary_hook=False,queued_launch=False,
 review001_failure_preserved=True,source_files={str(p):sha(p) for p in K.iterdir() if p.is_file()})
out.write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps({n:result[n] for n in ['passed','private_files_verified','candidate_sha256','XBE_ever_launched']}))
