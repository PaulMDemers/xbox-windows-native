"""Derive unique225 observer kit using reviewed unchanged224 native payloads."""
from pathlib import Path
import hashlib,json
k=Path(__file__).resolve().parent;old=k.parent/'video-fifo-retirement224'
dest=k/'derivation.json';assert not dest.exists()
pins={}
for name in ['common.py','typed-state.py','Prepare.ps1','prepare.py','Run.ps1','Invoke-224.ps1','run-emulator.py','supervise-emulator.py','audit-emulator.py']:
 p=old/name;text=p.read_text();pins[name]=hashlib.sha256(p.read_bytes()).hexdigest()
 text=text.replace("['control001','candidate001']","['trace001']").replace("'control001','candidate001'","'trace001'")
 text=text.replace('retirement224-runs','handoff225-runs').replace('nt5-retirement224-','nt5-handoff225-').replace('windows-native-retirement224','windows-native-handoff225').replace('retirement224-scratch','handoff225-scratch')
 text=text.replace('xbox-windows-native/retirement224','xbox-windows-native/handoff225')
 text=text.replace('video-fifo-retirement224/audit-emulator.py','video-loader-handoff225/audit-emulator.py')
 text=text.replace('debugger=False','debugger=True').replace('debugger=$false','debugger=$true')
 text=text.replace("case=='candidate001'","True")
 text=text.replace("'One retirement224 bounded FIFO observation launch; never relaunch'","'One225 bounded loader trace launch; never relaunch'")
 if name=='prepare.py':
  text=text.replace("read(k/'build-review002.json')","read(k.parent/'video-fifo-retirement224/build-review002.json')")
  text=text.replace("p=k/'artifacts/build002'/('probe.exe' if name=='probe.exe' else case+'/resident.sys')","p=k.parent/'video-fifo-retirement224/artifacts/build002'/('probe.exe' if name=='probe.exe' else 'candidate001/resident.sys')")
  text=text.replace("'probe.exe' if name=='probe.exe' else case","'probe.exe' if name=='probe.exe' else 'candidate001'")
  text=text.replace('Unique ordinary222 standalone child','Unique225 debugger standalone child; unchanged224 payload')
  text=text.replace("print('Fresh222 runtime001 prepared and cold audited')","print('Fresh225 trace001 prepared and cold audited')")
 if name=='Run.ps1':
  text=text.replace('Invoke-224.ps1','Invoke-225.ps1').replace('-MonitorPort 4594 -CompactTrace','-MonitorPort 4594 -GdbPort 4595 -CompactTrace')
 if name=='supervise-emulator.py':
  at='assert not (run/\'cleanup.json\').exists()\nrow=dict(cycle=1'
  repl="while not (out/'trace-armed.signal').exists():\n    assert time.monotonic()<deadline and not (out/'trace-finished.signal').exists(),'Tracer did not arm; no launch'\n    time.sleep(.2)\nassert not (run/'cleanup.json').exists()\nrow=dict(cycle=1"
  assert at in text;text=text.replace(at,repl)
 if name=='run-emulator.py':
  text=text.replace("if True:assert read(k/'control001/closure.json')['closed'],'Control must be closed first'",'')
  text=text.replace('child=None;observer=None','child=None;observer=None;tracer=None')
  text=text.replace("with (out/'observer-console.txt').open('x',encoding='utf-8') as observer_log:","with (out/'tracer-console.txt').open('x',encoding='utf-8') as tracer_log:\n  tracer=launch([sys.executable,str(k/'trace.py'),case],tracer_log)\n  r.update(tracer_pid=tracer.pid);save()\n with (out/'observer-console.txt').open('x',encoding='utf-8') as observer_log:")
  text=text.replace("assert (run/'cleanup.json').exists(),'Owned cleanup required before cold inspection'","assert (run/'cleanup.json').exists(),'Owned cleanup required before cold inspection'\n r['tracer_exit_code']=tracer.wait(timeout=15);save()")
  text=text.replace("closed=child is None or child.poll() is not None","if tracer is not None and tracer.poll() is None:\n  try:tracer.wait(timeout=210)\n  except subprocess.TimeoutExpired:r['owned_tracer_still_active']=True\n closed=(child is None or child.poll() is not None) and (tracer is None or tracer.poll() is not None)")
 if name=='audit-emulator.py':
  text=text.replace("k/'analyze-retirement.py'","k.parent/'video-fifo-retirement224/analyze-retirement.py'")
  text=text.replace("r.update(ordinary_qualified=r['strict_qualification_passed']","r['handoff_trace']=read(out/'trace.json')\nr['handoff_scope_passed']=r['observation_scope_passed'] and r['handoff_trace']['passed'] and r['handoff_trace']['closed'] and r['handoff_trace'].get('guest_resumed') and not r['handoff_trace']['remaining_breakpoints']\nr['strict_qualification_passed'] &= r['handoff_scope_passed']\nr.update(ordinary_qualified=False")
  text=text.replace("observation_scope_passed=r['observation_scope_passed'],strict_qualification_passed", "handoff_scope_passed=r['handoff_scope_passed'],observation_scope_passed=r['observation_scope_passed'],strict_qualification_passed")
  text=text.replace('Ordinary CPU manager plus bounded read-only FIFO observation','Debugger loader handoff with unchanged224 CPU manager and bounded read-only FIFO observation')
 q=k/('Invoke-225.ps1' if name=='Invoke-224.ps1' else name);assert not q.exists();q.write_text(text,encoding='utf-8')
dest.write_text(json.dumps(dict(scope=__doc__,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),parents=pins,unchanged_payload=True,namespace='xwnret224',debugger=True,physical_access=False),indent=2)+'\n')
