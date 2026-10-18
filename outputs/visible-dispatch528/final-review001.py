"""Close host/emulator preparation; explicitly no rendered or physical qualification."""
import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('C:/xwn528')
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'final-review.json';assert not out.exists()
for n in ['host001','ui-host001','controller-host001','supervisor-host001','capture-host001','preflight001','preflight002','emu-audit002','emu-audit004']:assert read(K/(n+'.json'))['passed']
for n,h in read(K/'ui-host001.json')['source_sha256'].items():assert sha(K/n)==h and sha(O/'ui-host001'/n)==h
for n in ['main.c','engine.c','engine.h','Makefile']:assert (K/n).read_bytes()==(O/'build001'/n).read_bytes()
for n in ['engine.c','engine.h']:assert (K/n).read_bytes()==(O/'host001'/n).read_bytes()
for row in read(K/'source-copy001.json'):
 source=K.parent/'dispatch-control527'/row['file'];assert sha(source)==row['source_sha256']
 assert source.read_bytes().replace(b'527',b'528')==(K/row['file']).read_bytes() and sha(K/row['file'])==row['sha256']
pre=read(K/'prebuild001.json');build=read(K/'build001.json')
for n,h in pre['sdk'].items():assert sha(Path('C:/nxdk')/n)==h
for n,h in pre['tools'].items():assert sha(Path(n))==h
for n,row in build['outputs'].items():assert sha(O/'build001'/n)==row['sha256']
frozen=0;mutable=[]
for name in ['emu-frozen001.json','emu-frozen002.json']:
 for n,h in read(K/name).items():
  if Path(n).name=='hdd.qcow2':mutable.append(n);continue
  assert sha(Path(n))==h,n;frozen+=1
a=read(K/'emu-audit002.json');b=read(K/'emu-audit004.json')
assert a['closure']['closed'] and a['closure']['natural_exit'] and a['closure']['exit']==0 and not a['closure']['fallback']
assert a['actual_runtime_entry'] and a['begin_pipeline_completed'] and a['changed_offsets_outside_E']==[1540] and not a['only_E_changed']
assert b['closure']['closed'] and b['closure']['fallback'] and b['closure']['exit']==-1 and b['whole_disk_equal']
assert not any(b['receipt_present'].values()) and not b['actual_runtime_entry']
assert 'unknown command' in read(K/'capture002-1.json')['reply']
assert not list((O/'emu001').glob('screen*')) and not list((O/'emu002').glob('screen*'))
assert read(K/'capture-host001.json')['source_sha256']==sha(K/'capture.py')
assert read(K/'controller-host001.json')['source_sha256']==sha(K/'physical.py')
assert read(K/'supervisor-host001.json')['source_sha256']==sha(K/'supervise.py')
assert not any((K/n).exists() for n in ['package001.json','physical001-stage.json','physical001-launch.json'])
pids=[30484,27744]+[r['result']['pid'] for r in read(K/'supervisor-host001.json')['cases']]
cmd='Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -like "xemu*" -or $_.ProcessName -like "qemu*" -or $_.Id -in @('+','.join(map(str,pids))+') } | Select-Object Id,ProcessName | ConvertTo-Json -Compress'
live=subprocess.run(['pwsh','-NoProfile','-Command',cmd],capture_output=True,text=True,check=True,timeout=20).stdout.strip();assert not live,live
q=subprocess.run(['wsl','-d','Ubuntu','--','pgrep','-a','^qemu-system'],capture_output=True,text=True,timeout=20);assert q.returncode==1 and not q.stdout.strip()
files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.rglob('*') if p.is_file()}
r=dict(review_passed=True,all_owned_processes_closed=True,closed_pids=pids,closed_sessions=[86350,63335],private_files_verified=len(files),private_files=files,immutable_runtime_pins_verified=frozen,mutable_overlay_exclusions=mutable,SDK_pins_verified=len(pre['sdk']),candidate=build['outputs']['bin\\default.xbe'],host_engine_and_UI_passed=True,emulator_receipt_scope_passed=True,emulator_rendered_output_qualified=False,emulator_disk_isolation_strict=False,second_capture_run_stopped_and_preserved=True,physical_access=False,physical_launch_queued=False,temporary_hook_installed=False,observer_reply_pending=True,no_next_launch_queued=True,scope='Prepared visible diagnostic; no Windows, GPU, game or stability promotion')
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:r[k] for k in ['review_passed','all_owned_processes_closed','private_files_verified','candidate','physical_access','observer_reply_pending']}))
