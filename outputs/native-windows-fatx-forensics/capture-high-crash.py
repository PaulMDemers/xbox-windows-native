"""Preserve emulator-only crash RAM and registers before closing the owned run."""
import json,pathlib,sys,datetime
k=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(k.parent/'native-windows-prebuild'))
from monitor_capture import command,acquire_monitor_lock
run=k.parents[1]/'work/runs/nt5-physical-f-high-allocation-001'
target=run/'crash-memory.ram'
assert run.exists() and not target.exists() and not (run/'cleanup.json').exists()
with acquire_monitor_lock(4594):
    command(4594,'stop')
    r={'scope':__doc__,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'registers':command(4594,'info registers'), 'stop_code':'0x1e',
       'parameters':['0xc0000005','0x824c7a22','0x1','0x006fffc8']}
    command(4594,'pmemsave 0 62914560 '+json.dumps(target.resolve().as_posix()))
    assert target.stat().st_size==62914560
    r['ram_bytes']=target.stat().st_size
    (k/'high-allocation-crash.json').write_text(json.dumps(r,indent=2)+'\n')
    print(r)
