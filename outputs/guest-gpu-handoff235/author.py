"""Fresh235 guest watchpoint/loader trace, unchanged234 emulator and224 payload."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'xemu-wait-snapshot234';assert not (k/'author.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();inputs={}
for name in ['common.py','typed-state.py','prepare002.py','Prepare002.ps1','Run.ps1','Invoke-234.ps1','run-emulator.py','supervise-emulator.py','audit-emulator.py','test-guards.py','freeze.py']:
 p=old/name;inputs[p.relative_to(ws).as_posix()]=sha(p);s=p.read_text().replace('snapshot234','guest235').replace('xemu-wait-guest235','guest-gpu-handoff235').replace('Invoke-234','Invoke-235').replace('trace002','trace001')
 if name=='Run.ps1':
  s=s.replace('$exe=Join-Path $PSScriptRoot artifacts/build001/xemu-preserve227.exe','$exe=Join-Path $PSScriptRoot ../xemu-wait-snapshot234/artifacts/build001/xemu-preserve227.exe').replace("Join-Path $PSScriptRoot build001.json","Join-Path $PSScriptRoot ../xemu-wait-snapshot234/build001.json")
 if name=='freeze.py':
  s=s.replace('xemu-wait-lifecycle233/emulator-frozen.json','xemu-wait-snapshot234/emulator-frozen.json').replace("b=read(k/'build001.json')", "b=read(k.parent/'xemu-wait-snapshot234/build001.json')").replace("(k/'artifacts/build001').rglob('*')","(k/'artifacts/inputs').rglob('*')")
 if name=='supervise-emulator.py':
  s=s.replace('deadline=time.monotonic()+60','deadline=time.monotonic()+180')
  start=s.index("row=dict(cycle=1,status='requesting'");end=s.index('deadline=time.monotonic()+520',start)
  s=s[:start]+'''# Trace owns the SINGLE loader launch and two executing-code stops.
assert trace['loader_launch']['status']=='accepted'
row=dict(trace['loader_launch']);r['cycles'].append(row);save();f.close()
print('Observing trace-owned single235 launch, never relaunch',flush=True)
'''+s[end:]
 if name=='audit-emulator.py':
  s=s.replace("r['preservation_trace_scope_passed']=", "r['guest_trace_scope_passed']=")
  s=s.replace("r['strict_qualification_passed'] &= r['preservation_trace_scope_passed']", "r['strict_qualification_passed'] &= r['guest_trace_scope_passed']")
  s=s.replace("r['publication_limit']='232 retains231 and uses release/acquire worker-terminal publication; timeout tuple is withheld. This audit does not qualify cross-host GPU visibility, preservation, retirement or ownership.'", "r['publication_limit']='Unchanged234 one-shot worker journal; actual guest watchpoint and executing loader pins remain debugger observations, not producer quiesce/retirement/ownership.'")
 q=k/({'prepare002.py':'prepare.py','Prepare002.ps1':'Prepare.ps1','Invoke-234.ps1':'Invoke-235.ps1'}.get(name,name));assert not q.exists();q.write_text(s)
 if q.suffix=='.py':ast.parse(s,filename=str(q))
for n in ['gdbstub/gdbstub.c','gdbstub/system.c']:
 p=old/'source'/n;q=k/'source'/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
(k/'author.json').write_text(json.dumps(dict(parent_inputs=inputs,new_emulator_build=False,physical_access=False,guest_launch=False),indent=2)+'\n')
print('235 fresh unchanged-model harness authored')
