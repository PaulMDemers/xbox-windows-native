"""One read-only HMP register observation; no stop, breakpoint or guest writes."""
import datetime,hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;run=Path('D:/xwn312/runs/nt5-hd312-candidate001')
out=k/'candidate001/register-observation.json';assert not out.exists()
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists()
helper=k.parent/'native-windows-prebuild/monitor_capture.py'
pins=json.loads((k/'emulator-frozen.json').read_text())
assert hashlib.sha256(helper.read_bytes()).hexdigest()==pins[helper.relative_to(k.parents[1]).as_posix()]
sys.path.insert(0,str(helper.parent));from monitor_capture import acquire_monitor_lock,command
r=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),guest_pause=False,guest_writes=False,physical_access=False,queries={},source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),limits='Live emulated register values, not physical signal or Windows caps; no framebuffer pixel readback.')
try:
 lock=acquire_monitor_lock(5044)
 for a in [0xfd600800,0xfd680838,0xfd680818,0xfd680600]:r['queries'][hex(a)]=command(5044,'xp /1wx '+hex(a))
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
