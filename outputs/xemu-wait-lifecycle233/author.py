"""Fresh233 read-only lifecycle observer over unchanged232 consuming model."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'xemu-backend-consume232';dest=k/'author.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();inputs={}
for name in ['common.py','typed-state.py','prepare.py','Prepare.ps1','Run.ps1','Invoke-232.ps1','run-emulator.py','supervise-emulator.py','trace.py','audit-emulator.py','test-guards.py','freeze.py','Build.ps1','build.py','decode-result.py']:
    p=old/name;inputs[p.relative_to(ws).as_posix()]=sha(p);s=p.read_text()
    s=s.replace('consume232','wait233').replace('xemu-backend-wait233','xemu-wait-lifecycle233').replace('Invoke-232','Invoke-233')
    if name=='build.py':
        s=s.replace('xemu-backend-publication231','xemu-backend-consume232')
        s=s.replace("'hw/xbox/nv2a/pfifo.c']", "'hw/xbox/nv2a/pfifo.c','hw/xbox/nv2a/pgraph/pgraph.c']")
        s=s.replace("assert sha(p)==pins[n];(s/n).write_bytes(p.read_bytes())", "assert sha(p)==pins[n];(s/n).write_bytes(p.read_bytes())")
        s=s.replace("p=prior/'artifacts/build001/source'/n", "p=prior/('artifacts/wait-source001/pgraph.c' if n.endswith('/pgraph.c') else 'artifacts/build001/source/'+n)")
        s=s.replace("assert sorted(r['changed_sources'])==sorted(n for n in names if not n.endswith(('renderer.h','surface.c')))", "assert sorted(r['changed_sources'])==sorted(['hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a_int.h','hw/xbox/nv2a/pgraph/pgraph.c'])")
    if name=='freeze.py':s=s.replace('xemu-backend-publication231/emulator-frozen.json','xemu-backend-consume232/emulator-frozen.json')
    if name=='trace.py':
        a="lock=acquire_monitor_lock(4594);cmd('stop');stopped=True"
        b="""lock=acquire_monitor_lock(4594)
 # Two fixed read-only live observations, NOT a retry for an empty queue.
 path=qom_path(cmd('info qom-tree'));r['nv2a_qom_path']=path
 r['wait_live_first']=wait_report(path);save();time.sleep(.25)
 r['wait_live_second']=wait_report(path);save()
 cmd('stop');stopped=True"""
        assert s.count(a)==1;s=s.replace(a,b)
        s=s.replace("r['before']=snapshot('before');save()", "r['wait_stopped_before']=wait_report(path);r['before']=snapshot('before');save()")
        s=s.replace("r['after']=snapshot('after');", "r['wait_stopped_after']=wait_report(path);r['after']=snapshot('after');")
        pos=s.index('def wait_dashboard(')
        s=s[:pos]+'''def wait_report(path):
 # Read-only try-lock contention retries, bounded; never repeats a request.
 deadline=time.monotonic()+1;attempts=0
 while True:
  attempts+=1;reply=cmd('qom-get '+path+' xwn-wait233-report')
  if 'busy=1' not in reply:return dict(reply=reply,attempts=attempts)
  assert time.monotonic()<deadline,'Read-only observer lock contention bound'
  time.sleep(.025)

'''+s[pos:]
    q=k/('Invoke-233.ps1' if name=='Invoke-232.ps1' else name);assert not q.exists();q.write_text(s)
    if q.suffix=='.py':ast.parse(s,filename=str(q))
for n in ['gdbstub/gdbstub.c','gdbstub/system.c']:
    p=old/'source'/n;q=k/'source'/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
dest.write_text(json.dumps(dict(parent_inputs=inputs,physical_access=False,guest_launch=False),indent=2)+'\n')
(k/'DESIGN.md').write_text('''#233 isolated compiled read-only wait observer

Observer enabled only by selecting this fresh diagnostic executable. Resident
256-row overwrite ring, monotonically saturated64-bit sequence, protected by
existing PGRAPH lock. Nonzero NO_OPERATION before/after and IRQ-update-return;
guest INTR acknowledgement before/after, enable writes and reset before/after.
No new lock acquisition in record calls. FIFO data valid ONLY where the caller
already holds FIFO AND PGRAPH locks; producer samples mark it unavailable.
QOM getter try-locks FIFO then PGRAPH without blocking BQL; takes no mutable
emulated action, allocates no record storage and never clears waits/interrupts.
Fixed two live samples250ms apart then separate stopped-dashboard request.
No empty-state search/retry or resumed producer within preservation request.
232 parser/publication/GL code otherwise unchanged; no guest/native GPU grant.
Bounded ring overwrites explicit, missing pair boundaries kept as unknown.
One first-boot/restart cold audit, not repeated-boot storage qualification.
''')
(k/'NEXT.md').write_text('Inspect actual233 producer/ack/reset sequences and stopped refusal. Preserve missing/overwritten observations; no ownership. Never replay closed cases.\n')
print('233 fresh lifecycle harness authored')
