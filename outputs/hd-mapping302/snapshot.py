"""One read-only HMP physical snapshot, always resume, no breakpoints or writes."""
import datetime,hashlib,json,re,sys,time,traceback
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'candidate001';run=Path('D:/xwn302/runs/nt5-map302-candidate001')
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
sys.path.insert(0,str(k.parent/'surface-bridge260'));from atomic_json import write_json
dest=out/'snapshot.json';assert not dest.exists()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
r=dict(status='waiting',started_utc=utc(),physical_access=False,diagnostic=True,ordinary_qualified=False,
       guest_memory_writes=False,guest_register_writes=False,breakpoints=0,monitor=[])
def save():write_json(dest,r)
def cmd(s):
    reply=command(5024,s);r['monitor'].append(dict(command=s,reply=reply,utc=utc()));save();return reply
save();lock=None;stopped=False
try:
    deadline=time.monotonic()+100
    while True:
        if (out/'launch.json').exists():
            launch=json.loads((out/'launch.json').read_text())
            if launch['cycles']:break
        assert time.monotonic()<deadline,'No launch record within bound';time.sleep(.5)
    row=launch['cycles'][0];assert row['status']=='accepted'
    when=datetime.datetime.fromisoformat(row['launch_requested_utc'])+datetime.timedelta(seconds=75)
    while datetime.datetime.now(datetime.timezone.utc)<when:
        assert not (run/'cleanup.json').exists(),'Runner already closed';time.sleep(.5)
    assert (run/'instance.json').exists() and not (run/'cleanup.json').exists()
    lock=acquire_monitor_lock(5024)
    assert 'VM status: running' in cmd('info status')
    cmd('stop');stopped=True;r['register_text']=cmd('info registers')
    r['control_registers']={n:int(re.search(n+r'=([0-9a-fA-F]+)',r['register_text']).group(1),16) for n in ['CR0','CR3','CR4']}
    assert r['control_registers']['CR0']&0x80000000 and not r['control_registers']['CR4']&0x20
    raw=Path('D:/xwn302/capture001/desktop.ram');raw.parent.mkdir(parents=True,exist_ok=False)
    cmd('pmemsave 0 67108864 '+json.dumps(raw.as_posix()))
    assert raw.stat().st_size==67108864
    r.update(status='captured',path=raw.as_posix(),sha256=hashlib.sha256(raw.read_bytes()).hexdigest())
except Exception as exc:r.update(status='failed',error=repr(exc),traceback=traceback.format_exc())
finally:
    if stopped:
        try:cmd('cont');r['resumed']=True
        except Exception as exc:r['resume_error']=repr(exc)
    if lock:lock.close()
    r['ended_utc']=utc();save()
print(json.dumps({n:r[n] for n in ['status','error','resumed'] if n in r}))
