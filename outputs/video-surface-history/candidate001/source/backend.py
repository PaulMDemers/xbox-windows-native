"""Pinned trace help and borrowed generated-backend evidence; no guest launch."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'backend.json';assert not dest.exists()
exe=ws/'outputs/native-windows-physical-f/artifacts/xemu-resource-model.exe'
sha=lambda data:hashlib.sha256(data).hexdigest()
assert sha(exe.read_bytes())=='969a99a83a308ba547ce3918015d676efee79912d97253d336bf8a35b5bc047d'
p=subprocess.run([str(exe),'-trace','help'],capture_output=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
assert p.returncode==0,(p.returncode,p.stderr)
text=(p.stdout+p.stderr).decode('utf-8','replace')
from lifecycle import EVENTS
names=['nv2a_pgraph_surface_cpu_read','nv2a_pgraph_surface_cpu_write']+list(EVENTS)
assert all(n in text.splitlines() for n in names)
root='/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet/'
files=['build/config-host.h','build/trace/trace-hw_xbox_nv2a.h','trace/trace-hmp-cmds.c','trace/control.c','scripts/tracetool/backend/log.py','util/log.c','hw/xbox/nv2a/pgraph/gl/surface.c','accel/tcg/cputlb.c','hw/xbox/nv2a/trace-events','system/physmem.c']
pins={};contents={}
for f in files:
 data=subprocess.check_output(['wsl','-d','Ubuntu','--','cat',root+f]);pins[root+f]=sha(data);contents[f]=data.decode()
assert '#define CONFIG_TRACE_LOG' in contents['build/config-host.h']
assert '#define CONFIG_TRACE_SIMPLE' not in contents['build/config-host.h']
assert 'qemu_log("nv2a_pgraph_surface_cpu_write ' in contents['build/trace/trace-hw_xbox_nv2a.h']
assert 'log_flags |= LOG_TRACE;' in contents['util/log.c'] and 'fflush(logfile);' in contents['util/log.c']
r=dict(passed=True,physical_access=False,guest_launched=False,executable=str(exe),executable_sha256=sha(exe.read_bytes()),help_exit=p.returncode,events=names,help_sha256=sha(p.stdout+p.stderr),source_pins=pins,
 routing='CONFIG_TRACE_LOG; generated event calls qemu_log, -D selects global file, each unlock flushes. HMP dynamic state toggles independently.',
 limitation='Borrowed build sources and generated headers are corroborating pins, not a pristine tree claim. Runtime event state and exact byte windows must still be verified before/around the owned draws.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['passed','events','guest_launched']},indent=2))
