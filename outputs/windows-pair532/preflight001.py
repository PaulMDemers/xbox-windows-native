"""Read local pinned build provenance and actual files; no network/console."""
import ast,hashlib,json,shutil,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
def wslcat(path):return subprocess.check_output(['wsl','-d','Ubuntu','-u','paul','--','cat',path],timeout=30)
base='/home/paul/xbox-windows-native/build/hd-reservation300-build001/'
trace=wslcat(base+'source/win32ss/drivers/miniport/xboxvmp/nt5/video_trace.c')
cache=wslcat(base+'candidate001/CMakeCache.txt')
driver=wslcat(base+'candidate001/win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.sys')
assert sha(driver)=='74ccdc9fc7b26fe76919941fe978822b1fb538c7814343b0f0755d99e661c1dd'
assert b'XBOX_NT5_VIDEO_TRACE_REUSE:BOOL=ON' in cache
assert b'#ifdef XBOX_NT5_VIDEO_TRACE_REUSE' in trace and b'((PUCHAR)TraceData)[I] = 0;' in trace
wrapper=wslcat('/home/paul/xbox-windows-native/build/resolution-e374-build001/source/boot_xbe/xbeboot.S')
assert sha(wrapper)=='b8ddf72f41a682d3868f1b801492b31005611c6868aa5927f54e5ce14bb94a2c'
assert b'NtCreateFile' not in wrapper and b'NtWriteFile' not in wrapper
xbe=Path('E:/xwn374/build001/default.xbe').read_bytes()
assert sha(xbe)=='6240a801d97c4894e56d516a934059da056446fb77cf895b5364bdd6cd24be9a'
free=shutil.disk_usage('C:/').free;assert free-96*1024**2>=20*1024**3
paths=[K/'controller.py',K/'supervise.py',K/'host001.json',K/'readiness001.json',
 W/'outputs/visible-dispatch528/physical.py',W/'outputs/visible-dispatch528/entry_decode.py',
 W/'outputs/field-scanout428/physical.py',W/'outputs/demo-audio-level256/common001.py',
 W/'outputs/surface-bridge260/atomic_json.py',W/'tools/configure-e-display.py',W/'tools/e-display-policy.json',
 W/'outputs/demo-integration399/accepted-state.json',W/'outputs/hd-reservation300/build001.json',W/'outputs/resolution-e374/build001.json']
for p in [K/'controller.py',K/'supervise.py']:ast.parse(p.read_text(encoding='utf-8'))
r=dict(passed=True,free_c_bytes=free,reserve_bytes=96*1024**2,pins={str(p):sha(p.read_bytes()) for p in paths},
      driver_sha256=sha(driver),trace_source_sha256=sha(trace),cache_sha256=sha(cache),wrapper_source_sha256=sha(wrapper),
      xbe_sha256=sha(xbe),trace_reuse_enabled=True,host_trace_reseed_needed=False,remote_access=False,
      scope='Exact retained build driver matches installed policy pin; build cache enables trace reuse; source retains header/length checks and clears in-memory records; wrapper has no file logger')
out=K/'preflight001.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({n:r[n] for n in ['passed','free_c_bytes','trace_reuse_enabled','remote_access']}))
