"""Read-only paused diagnostic memory from our owned diagnostic002, never ordinary proof."""
import datetime,hashlib,json,os,pathlib,sys,time
os.environ['PYTHONPATH']='C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages'
sys.path.insert(0,os.environ['PYTHONPATH'])
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
sys.path.insert(0,str(k.parent/'native-windows-prebuild'))
from monitor_capture import command,acquire_monitor_lock
run=repo/'work/runs/nt5-audio207-diagnostic002'
assert (run/'instance.json').exists()
launch=json.loads((k/'diagnostic002/launch.json').read_text())
assert launch['host']=='127.0.0.1' and launch['port']==4696 and len(launch['cycles'])==1
at=datetime.datetime.fromisoformat(launch['cycles'][0]['launch_requested_utc']).timestamp()+120
while time.time()<at:
    assert not (run/'cleanup.json').exists()
    time.sleep(min(2,at-time.time()))
assert not (run/'cleanup.json').exists()
raw=run/'diagnostic-retained.ram';dest=run/'diagnostic-retained.json'
assert not raw.exists() and not dest.exists()
r=dict(diagnostic_only=True,ordinary_qualified=False,physical_access=False,paused=True,
       memory_writes=False,register_writes=False,script_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest())
lock=acquire_monitor_lock(4694)
running='VM status: running' in command(4694,'info status')
command(4694,'stop')
try:
    r['registers']=command(4694,'info registers')
    r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    r['command_reply']=command(4694,'pmemsave 0 67108864 '+json.dumps(raw.resolve().as_posix()))
    assert raw.stat().st_size==67108864
    r['memory_sha256']=hashlib.sha256(raw.read_bytes()).hexdigest()
finally:
    try:
        if running:command(4694,'cont')
    finally:
        lock.close();dest.write_text(json.dumps(r,indent=2)+'\n')
print('Retained owned diagnostic memory; no ordinary qualification')
