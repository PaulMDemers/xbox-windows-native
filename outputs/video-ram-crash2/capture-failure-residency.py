"""Read-only post-observer-failure snapshot; never relaunch or mutate the guest."""
import hashlib,json,sys,datetime
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'crash001';run=ws/'work/runs/nt5-video-ram-crash2-crash001'
assert not (run/'cleanup.json').exists();dest=out/'failure-residency.json';assert not dest.exists()
t=json.loads((out/'trace.json').read_text());assert t['status']=='capture_incomplete' and t['guest_resumed'] and not t['armed_breakpoints_remaining']
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
raw=out/'artifacts/failure-residency.ram';assert not raw.exists();lock=acquire_monitor_lock(4594);stopped=False
r=dict(physical_access=False,scope=__doc__,trace_sha256=hashlib.sha256((out/'trace.json').read_bytes()).hexdigest(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
try:
 command(4594,'stop');stopped=True;r['registers']=command(4594,'info registers')
 r['reply']=command(4594,'pmemsave 0 67108864 '+json.dumps(raw.resolve().as_posix()));assert raw.stat().st_size==67108864
 r['private_memory']=str(raw.resolve());r['private_memory_sha256']=hashlib.sha256(raw.read_bytes()).hexdigest()
finally:
 if stopped:r['resume_reply']=command(4594,'cont');r['resumed']=True
 lock.close();dest.write_text(json.dumps(r,indent=2)+'\n')
print('Post-failure physical snapshot preserved; no crash qualification')
