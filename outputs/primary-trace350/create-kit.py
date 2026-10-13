"""New diagnostic namespace from349; immutable existing binaries and oracles."""
import ast,difflib,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;P=K.parent/'primary-runtime349';changes={}
names=['Invoke.ps1','Run.ps1','close-host.py','analyze-allocation002.py','stock_io002.py','analyze-capture.py','typed-state.py','installed-binding.py','supervise.py','audit.py','prepare002.py','Prepare002.ps1','primary_analysis.py','phase349_analysis.py']
for name in names:
    old=(P/name).read_text();s=old.replace('xwn349','xwn350').replace('primary349','primary350').replace('5176','5186').replace('5177','5187').replace('5178','5188')
    if name=='Prepare002.ps1':s=s.replace('primary-runtime349','primary-trace350')
    if name=='Run.ps1':s=s.replace('debugger=$false','debugger=$true')
    if name=='supervise.py':
        s=s.replace('debugger=False','debugger=True')
        s=s.replace("assert not (run/'cleanup.json').exists()\nrow=dict", "assert (out/'trace-armed.signal').exists(),'Arm trace BEFORE single launch'\nassert not (run/'cleanup.json').exists()\nrow=dict")
    if name=='audit.py':
        s=s.replace('debugger=False','debugger=True')
        s=s.replace('from phase_analysis import analyze as large_phase','from phase349_analysis import analyze as large_phase')
        # Preserve every old gate; this trace is independently never ordinary.
        s=s.replace("save(dest,r);", "r['ordinary_qualified']=False\nr['debugger_timing_invalid']=True\nr['limits']='Read-only350 debugger experiment; original348 full-byte/strict gates retained. No ordinary/performance/physical qualification.'\nsave(dest,r);")
    if name=='prepare002.py':
        s=s.replace("assert case in ['control001','candidate001']", "assert case=='candidate001'")
        s=s.replace("s=s", "s=s")
    ast.parse(s) if name.endswith('.py') else None
    assert not (K/name).exists();(K/name).write_bytes(s.encode())
    (K/(name+'.patch')).write_bytes(''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='349/'+name,tofile='350/'+name)).encode())
    changes[name]=dict(parent_sha256=hashlib.sha256((P/name).read_bytes()).hexdigest(),sha256=hashlib.sha256((K/name).read_bytes()).hexdigest())
(K/'.gitignore').write_bytes(b'**/artifacts/\n')
(K/'source-review.json').write_text(json.dumps(dict(changes=changes,new_binaries=False,physical_access=False,debugger=True,old_gates_retained=True),indent=2)+'\n')
