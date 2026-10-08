"""New emulator-only lifecycle child; exact167 workload and unchanged drivers."""
import ast,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'video-hook-counters167';assert not (k/'Run.ps1').exists()
for name in ['common.py','prepare.py','preflight.py','audit.py','supervise.py','check-leases.ps1','Run.ps1','freeze.py','sample_analysis.py','close-emulator.py','gdi-probe.c']:
    text=(old/name).read_text(encoding='utf-8').replace('video-hook-counters167','video-process-lifecycle168').replace('vhooks167','vlife168').replace('xwnvh167','xwnvl168')
    if name=='audit.py':text=text.replace('debugger=False','debugger=True').replace('r[\'physical_qualified\']=False;',"r['ordinary_qualified']=False;r['physical_qualified']=False;")
    if name=='prepare.py':text=text.replace("rr=readers(io,source)","rr=readers(io,source)\n    caller=k/'artifacts/umpnpmgr.dll'\n    assert m.sha(rr['F'].read('winnt/system32/umpnpmgr.dll'))==sha(caller),'Actual caller DLL differs from owned review'\n    f['files']['F/winnt/system32/umpnpmgr.dll']=sha(caller)",1)
    if name=='Run.ps1':text=text.replace('debugger=$false','debugger=$true')
    if name=='supervise.py':
        text=text.replace('debugger=False','debugger=True').replace('no debugger/UI interventions','bounded read-only debugger, no UI/data/register changes')
        text=text.replace("assert (run/'instance.json').exists() and not (run/'cleanup.json').exists()", "assert (run/'instance.json').exists() and not (run/'cleanup.json').exists()\nassert (out/'trace-armed.signal').exists()")
        text=text.replace("(run/'capture-complete.signal').touch(exist_ok=False)","\n                trace_deadline=time.monotonic()+20\n                while not (out/'trace-closed.signal').exists() and time.monotonic()<trace_deadline:time.sleep(0.25)\n                assert (out/'trace-closed.signal').exists(),'Tracer must tear down before runner cleanup'\n                (run/'capture-complete.signal').touch(exist_ok=False)",1)
    if name=='close-emulator.py':text=text.replace('debugger=False','debugger=True').replace("samples=5,live_checks=20", "ordinary_qualified=False,samples=5,live_checks=20")
    if name=='freeze.py':
        text=text.replace("k/'gdi-probe.c',k/'DESIGN.md'","k/'sites.json',k/'timing-interface.json',k/'gdi-probe.c',k/'DESIGN.md'")
        text=text.replace("save(dest,{str(p.relative_to(ws)).replace('\\\\','/'):sha(p) for p in paths})", "pins={str(p.relative_to(ws)).replace('\\\\','/'):sha(p) for p in paths}\n    for name,row in read(k/'sites.json')['binaries'].items():pins[row['path']]=row['sha256']\n    pins.update(read(k/'sites.json')['dependency_pins'])\n    save(dest,pins)")
    ast.parse(text) if name.endswith('.py') else None
    (k/name).write_bytes(text.encode('utf-8'))
(k/'artifacts').mkdir(exist_ok=False)
for name in ['runner.exe','gdi-probe.exe']:shutil.copyfile(old/'artifacts'/name,k/'artifacts'/name)
shutil.copyfile(old/'build-review.json',k/'build-review.json')
shutil.copyfile(k.parent/'fatx-mapped-lifecycle/atomic_json.py',k/'atomic_json.py')
shutil.copyfile(k.parent/'video-desktop-trace/discover_kernel.py',k/'discover_kernel.py')
print('Fresh168 child kit; no build/guest/physical access')
