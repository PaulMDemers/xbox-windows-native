"""Compile isolated247 UI diagnostic; restore every borrowed source under lease."""
import difflib,hashlib,json,os,shutil,subprocess
from pathlib import Path
from patch import apply
assert os.environ.get('XWN_BUILD_LEASE')=='held'
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'build002.json';assert not dest.exists()
assert shutil.disk_usage('/mnt/c').free>=20*1024**3
s=Path('/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet')
base='e72e76bd1f12ce45c6c63b4196c6918ea2cc705d'
assert subprocess.check_output(['git','-c','safe.directory='+str(s),'rev-parse','HEAD'],cwd=s,text=True).strip()==base
prior=ws/'outputs/frontend-close246';pins=json.loads((prior/'candidate002-source-pins.json').read_text())
names=['hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a_int.h','hw/xbox/nv2a/nv2a.h','hw/xbox/nv2a/pgraph/gl/renderer.c','hw/xbox/nv2a/pgraph/gl/renderer.h','hw/xbox/nv2a/pgraph/gl/surface.c','hw/xbox/nv2a/pfifo.c','hw/xbox/nv2a/pgraph/pgraph.c','system/physmem.c','system/trace-events','hw/xbox/nv2a/trace-events','hw/xbox/nv2a/pgraph/gl/display.c','ui/xemu.c']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();original={n:(s/n).read_bytes() for n in names}
art=Path('/mnt/e/Codex-archive/xbox-windows-native/phase247-build002');art.mkdir(parents=True,exist_ok=False)
image='ghcr.io/xemu-project/xemu-win64-toolchain-gcc@sha256:a4b2fb230a429d69272cb403de29c1a7a01aa63d84d92b427e6c7d119927aa73'
r=dict(passed=False,source_revision=base,toolchain=image,source_sha256=sha(Path(__file__)),patch_sha256=sha(k/'patch.py'),worker_sha256=sha(k/'worker.c'),physical_access=False,guest_launch=False,original_sources={n:sha(s/n) for n in names})
try:
 for n in names:
  p=prior/'artifacts/build001/source'/n
  if not p.exists():p=s/n
  assert sha(p)==pins[n],n
  (s/n).write_bytes(p.read_bytes())
 for n,h in pins.items():
  if (s/n).is_file():assert sha(s/n)==h,n
 before={n:(s/n).read_bytes() for n in names};apply(s)
 patch=[]
 for n in names:patch.extend(difflib.unified_diff(before[n].decode().splitlines(True),(s/n).read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n))
 (k/'delta002.patch').write_text(''.join(patch));r['delta_sha256']=sha(k/'delta002.patch')
 after={n:sha(s/n) for n in pins if (s/n).is_file()};(k/'candidate002-source-pins.json').write_text(json.dumps(after,indent=2)+'\n')
 r['changed_sources']=[n for n in names if before[n]!=(s/n).read_bytes()]
 for n in names+['include/qemu/atomic.h','include/qemu/compiler.h','include/qemu/queue.h','include/qemu/thread.h','include/qemu/thread-win32.h','util/log.c','scripts/tracetool/backend/log.py','hw/xbox/nv2a/trace.h','system/trace.h','COPYING','COPYING.LIB']:
  p=art/'source'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((s/n).read_bytes())
 with (k/'build002.log').open('xb') as log:
  code=subprocess.run(['podman','run','--rm','--pull=never','-v',str(s)+':/src','-w','/src/build',image,'ninja','-j4','qemu-system-i386w.exe'],stdout=log,stderr=subprocess.STDOUT,timeout=600).returncode
 r['build_exit_code']=code;assert code==0
 exe=art/'xemu-worker247.exe';shutil.copyfile(s/'build/qemu-system-i386w.exe',exe)
 r.update(passed=True,executable_sha256=sha(exe),executable_bytes=exe.stat().st_size)
except BaseException as exc:r['error']=repr(exc);raise
finally:
 for n,data in original.items():(s/n).write_bytes(data)
 r['borrowed_sources_restored']=all((s/n).read_bytes()==data for n,data in original.items())
 dest.write_text(json.dumps(r,indent=2)+'\n')
print('247 compiled; borrowed sources restored')
