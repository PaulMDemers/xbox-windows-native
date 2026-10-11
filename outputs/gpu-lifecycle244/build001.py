"""One fresh observation build; exact borrowed-source restoration under lease."""
import difflib,hashlib,json,os,shutil,subprocess
from pathlib import Path
from patch import apply
assert os.environ.get('XWN_BUILD_LEASE')=='held'
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'build001.json';assert not dest.exists()
assert shutil.disk_usage('/mnt/c').free>=20*1024**3
s=Path('/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet')
assert subprocess.check_output(['git','-c','safe.directory='+str(s),'rev-parse','HEAD'],cwd=s,text=True).strip()=='e72e76bd1f12ce45c6c63b4196c6918ea2cc705d'
prior=ws/'outputs/gpu-reference-pair242';pins=json.loads((prior/'candidate004-source-pins.json').read_text())
inherited=['hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a_int.h','hw/xbox/nv2a/pgraph/gl/renderer.c','hw/xbox/nv2a/pgraph/gl/renderer.h','hw/xbox/nv2a/pgraph/gl/surface.c','hw/xbox/nv2a/pfifo.c','hw/xbox/nv2a/pgraph/pgraph.c']
new=['system/physmem.c','system/trace-events','hw/xbox/nv2a/trace-events','hw/xbox/nv2a/pgraph/gl/display.c','ui/xemu.c']
names=inherited+new;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original={n:(s/n).read_bytes() for n in names}
art=Path('/mnt/e/Codex-archive/xbox-windows-native/phase244-build001');art.mkdir(parents=True,exist_ok=False)
logs=k/'build-logs';logs.mkdir(exist_ok=True)
r=dict(passed=False,source_revision='e72e76bd1f12ce45c6c63b4196c6918ea2cc705d',source_sha256=sha(Path(__file__)),patch_generator_sha256=sha(k/'patch.py'),original_sources={n:sha(s/n) for n in names},physical_access=False,guest_launch=False)
image='ghcr.io/xemu-project/xemu-win64-toolchain-gcc@sha256:a4b2fb230a429d69272cb403de29c1a7a01aa63d84d92b427e6c7d119927aa73';r['toolchain']=image
try:
 for n in inherited:
  p=prior/'artifacts/build004/source'/n;assert sha(p)==pins[n];(s/n).write_bytes(p.read_bytes())
 for n,h in pins.items():
  if (s/n).is_file():assert sha(s/n)==h,n
 baseline={n:(s/n).read_bytes() for n in names}
 apply(s)
 patch=[]
 for n in names:patch.extend(difflib.unified_diff(baseline[n].decode().splitlines(True),(s/n).read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n))
 (k/'inventory242-build001.patch').write_text(''.join(patch))
 allpins={n:sha(s/n) for n in pins if (s/n).is_file()}
 (k/'candidate001-source-pins.json').write_text(json.dumps(allpins,indent=2)+'\n')
 r['changed_sources']=[n for n in pins if allpins[n]!=pins[n]]
 r['patch_sha256']=sha(k/'inventory242-build001.patch')
 for n in names+['cpu-common.c','system/cpus.c','include/qemu/atomic.h','include/qemu/thread.h','include/qemu/thread-win32.h','util/log.c','scripts/tracetool/backend/log.py','hw/xbox/nv2a/trace.h','system/trace.h','COPYING','COPYING.LIB']:
  p=art/'source'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((s/n).read_bytes())
 with (logs/'build001.log').open('xb') as log:
  code=subprocess.run(['podman','run','--rm','--pull=never','-v',str(s)+':/src','-w','/src/build',image,'ninja','-j4','qemu-system-i386w.exe'],stdout=log,stderr=subprocess.STDOUT,timeout=600).returncode
 r['build_exit_code']=code;assert code==0
 exe=art/'xemu-lifecycle244.exe';shutil.copyfile(s/'build/qemu-system-i386w.exe',exe)
 r.update(passed=True,executable_sha256=sha(exe),executable_bytes=exe.stat().st_size,source_manifest_sha256=sha(k/'candidate001-source-pins.json'))
except BaseException as exc:r['error']=repr(exc);raise
finally:
 for n,data in original.items():(s/n).write_bytes(data)
 r['borrowed_sources_restored']=all((s/n).read_bytes()==v for n,v in original.items())
 dest.write_text(json.dumps(r,indent=2)+'\n')
print('244 observation build compiled; all borrowed sources restored')
