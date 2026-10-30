"""Close the already collected physical run; no hardware access or rerun."""
from pathlib import Path
import json, hashlib, datetime, subprocess
K=Path(__file__).resolve().parent; W=K.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def put(n,v):
    with (K/n).open('x',encoding='utf-8',newline='\n') as f: f.write(json.dumps(v,indent=2)+'\n')
a=json.loads((K/'audit001.json').read_text()); assert a['passed']
for n,h in json.loads((K/'sources001.json').read_text())['files'].items(): assert sha(K/n)==h,n
put('closed001.json',dict(closed=True,passed=True,utc=utc(),audit_sha256=sha(K/'audit001.json'),native_photo=True,kernel_preparation_only_on_disk=True,launch_count=1,collection_count=1,manual_power_cycle=True,console='Authenticated UnleashX dashboard002 after user Green, ready',hook=False,windows_launched=False,full_visible_mode_proved=False))
put('process-state002.json',dict(utc=utc(),owned_host_processes=[],owned_CPU_VM_count=0,console='Authenticated dashboard002 after manual power cycle',hook=False,windows_launched=False,automation='PAUSED'))
head='''# Native817 CLOSED PASS: preserving mode controls

Photo decoded and independently reviewed: final status 0x817, CR1A38 ->3C;
last raw3C is after CR2D undo BEFORE its own undo, not final restoration.
Seven displayed cleanup masks and one forward mask are zero;27 other cleanup
masks and final own CR1A restoration are aggregate-only through strict success.
Same-value CR25/28/2D controls do not prove effective writes.

User Green, ready under standing photo/power-off-on workflow. Dashboard002
authenticated; nine kernel preparation reports collected once; audit001 PASS.
No startup hook, Windows launch, normal Windows shutdown or owned host VM.
All817 runtime work CLOSED: never relaunch/recollect/runtime-parent. Pinned
source-only reuse allowed. Tail002 and invocation failures remain preserved.

Next: fresh combined visible native mode candidate based on817's preserving
prefix and source-backed704 encoder/VGA sequence. Review remaining writes,
validate complete control flow, bounds and failure reporting before staging.
Then Windows handoff/display integration. Full visible low mode and Windows1.6
desktop remain unproved; do not infer either from green recovery reports.
User renewed tonight work; expired automation remains PAUSED.
'''
(K/'NEXT.md').write_text(head,encoding='utf-8',newline='\n')
for n in ['CONTINUATION.md','STATUS.md']:
    p=W/'outputs/engineering-notes'/n; s=p.read_text(encoding='utf-8-sig'); p.write_text(head+'\n'+s,encoding='utf-8',newline='\n')
p=K/'README.md';s=p.read_text();s=s.replace('See NEXT.md. One accepted SITE at02:00:22 UTC; no repeat or collection yet.','See NEXT.md and closed001.json. One accepted SITE at02:00:22 UTC; nine\npreparation reports collected once after manual power cycle. Photo and audit001\npass; final own CR1A recovery is aggregate-only. No Windows launch.')
p.write_text(s,encoding='utf-8',newline='\n')
old=json.loads((K/'staging-check001.json').read_text()); lines=old['output'].splitlines(); assert len(lines)%2==0
for i in range(0,len(lines),2):
    assert any('/'+n+':' in lines[i] for n in ['probe-bitmap-native.c','probe-pairs-native.c'])
    assert lines[i].endswith('trailing whitespace.') and lines[i+1].startswith('+') and not lines[i+1][1:].strip()
put('whitespace-review001.json',dict(passed=True,raw_check_passed=False,raw_check_sha256=sha(K/'staging-check001.json'),warnings=len(lines)//2,classification='Whitespace-only generated blank lines in frozen source; preserved exact tested bytes',no_functional_gate_waiver=True))
files=[p for p in K.iterdir() if p.is_file() and p.name!='prefix002.json']
assert all(p.suffix in ['.py','.json','.c','.h','.S','.ld','.md','.zlib64',''] or p.name in ['.gitattributes','.gitignore'] for p in files)
subprocess.run(['git','add','-f','--']+[str(p.relative_to(W)) for p in files]+['outputs/engineering-notes/CONTINUATION.md','outputs/engineering-notes/STATUS.md'],cwd=W,check=True)
for n,h in json.loads((K/'sources001.json').read_text())['files'].items():
    b=subprocess.check_output(['git','show',':'+str((K/n).relative_to(W)).replace('\\','/')],cwd=W)
    assert hashlib.sha256(b).hexdigest()==h,n
print('817 CLOSED; frozen staged bytes exact; generated whitespace-only warnings retained')
