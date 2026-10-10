"""Unique227 diagnostic child of owned immutable211; unchanged native payloads."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'video-loader-handoff225'
dest=k/'derivation.json';assert not dest.exists();pins={}
for name in ['common.py','typed-state.py','Prepare.ps1','prepare.py','Run.ps1','Invoke-225.ps1','run-emulator.py','supervise-emulator.py','audit-emulator.py']:
 p=old/name;pins[name]=hashlib.sha256(p.read_bytes()).hexdigest();text=p.read_text()
 text=text.replace('handoff225','preserve227').replace('video-loader-handoff225','xemu-backend-preserve227').replace('Invoke-225.ps1','Invoke-227.ps1')
 if name=='prepare.py':
  text=text.replace("'Unique225 debugger standalone child", "'Unique227 debugger standalone child")
  text=text.replace("print('Fresh225 trace001", "print('Fresh227 trace001")
 if name=='Run.ps1':
  text=text.replace('../xemu-cpu-surface-evict/build003/artifacts/xemu-candidate.exe','artifacts/build004/xemu-preserve227.exe')
  text=text.replace("$digest='685f24e317322469cac8710286bf928f7b2accbde5062f3cf8c86a9b21e97890'","$digest=(Get-Content (Join-Path $PSScriptRoot build004.json) -Raw | ConvertFrom-Json).executable_sha256")
 if name=='audit-emulator.py':
  text=text.replace("r['handoff_scope_passed']=", "r['preservation_trace_scope_passed']=")
  text=text.replace("r['handoff_scope_passed']", "r['preservation_trace_scope_passed']")
  text=text.replace("handoff_scope_passed=r['preservation_trace_scope_passed']", "preservation_trace_scope_passed=r['preservation_trace_scope_passed']")
  text=text.replace("r['strict_qualification_passed'] &= r['preservation_trace_scope_passed']", "r['strict_qualification_passed'] &= r['preservation_trace_scope_passed']\nr['dirty_surface_coverage']=r['handoff_trace'].get('dirty_surface_coverage',False)\nr['backend_preservation_qualified']=r['preservation_trace_scope_passed'] and r['dirty_surface_coverage']\nr['strict_qualification_passed'] &= r['backend_preservation_qualified']")
  text=text.replace('Debugger loader handoff with unchanged224 CPU manager and bounded read-only FIFO observation','Debugger227 opt-in backend preservation with unchanged224 CPU manager. No renderer-reference retirement or native permit')
 q=k/('Invoke-227.ps1' if name=='Invoke-225.ps1' else name);assert not q.exists();q.write_text(text)
dest.write_text(json.dumps(dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),parents=pins,debugger=True,physical_access=False,native_payload_changed=False,namespace='xwnret224'),indent=2)+'\n')
