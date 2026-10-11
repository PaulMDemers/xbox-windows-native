"""Fresh opt-in candidate build under lease; restore every borrowed source."""
import difflib,hashlib,json,os,shutil,subprocess
from pathlib import Path
from patch import apply
assert os.environ.get('XWN_BUILD_LEASE')=='held'
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'build001.json';assert not dest.exists()
assert shutil.disk_usage('/mnt/c').free>=20*1024**3
s=Path('/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet')
assert subprocess.check_output(['git','-c','safe.directory='+str(s),'rev-parse','HEAD'],cwd=s,text=True).strip()=='e72e76bd1f12ce45c6c63b4196c6918ea2cc705d'
prior=ws/'outputs/xemu-wait-snapshot234';pins=json.loads((prior/'candidate001-source-pins.json').read_text())
names=['hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a_int.h','hw/xbox/nv2a/pgraph/gl/renderer.c','hw/xbox/nv2a/pgraph/gl/renderer.h','hw/xbox/nv2a/pgraph/gl/surface.c','hw/xbox/nv2a/pfifo.c','hw/xbox/nv2a/pgraph/pgraph.c']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original={n:(s/n).read_bytes() for n in names};art=k/'artifacts/build001';art.mkdir(parents=True,exist_ok=False)
logs=k/'build-logs';logs.mkdir(exist_ok=True);r=dict(passed=False,source_revision='e72e76bd1f12ce45c6c63b4196c6918ea2cc705d',source_sha256=sha(Path(__file__)),patch_generator_sha256=sha(k/'patch.py'),original_sources={n:sha(s/n) for n in names},guest_launch=False,physical_access=False)
image='ghcr.io/xemu-project/xemu-win64-toolchain-gcc@sha256:a4b2fb230a429d69272cb403de29c1a7a01aa63d84d92b427e6c7d119927aa73';r['toolchain']=image
try:
 # Reconstruct the exact compiled227 diagnostic; backend coverage did not qualify.
 for n in names:
  p=prior/'artifacts/build001/source'/n
  assert sha(p)==pins[n];(s/n).write_bytes(p.read_bytes())
 baseline={n:(s/n).read_bytes() for n in names}
 for n,h in pins.items():
  if (s/n).is_file():assert sha(s/n)==h,n
 apply(s)
 patch=[]
 for n in names:
  patch.extend(difflib.unified_diff(baseline[n].decode().splitlines(True),(s/n).read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n))
 (k/'snapshot238-build001.patch').write_text(''.join(patch));r['patch_sha256']=sha(k/'snapshot238-build001.patch')
 allpins={n:sha(s/n) for n in pins if (s/n).is_file()};(k/'candidate001-source-pins.json').write_text(json.dumps(allpins,indent=2)+'\n')
 r['changed_sources']=[n for n in pins if allpins[n]!=pins[n]];assert sorted(r['changed_sources'])==sorted(['hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a_int.h','hw/xbox/nv2a/pgraph/gl/renderer.c'])
 for n in names+['include/qemu/atomic.h','include/qemu/compiler.h','hw/xbox/nv2a/nv2a_regs.h','include/qemu/queue.h','hw/xbox/nv2a/pgraph/pgraph.h']:
  q=art/'source'/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes((s/n).read_bytes())
 with (logs/'build001.log').open('xb') as log:
  result=subprocess.run(['podman','run','--rm','--pull=never','-v',str(s)+':/src','-w','/src/build',image,'ninja','-j4','qemu-system-i386w.exe'],stdout=log,stderr=subprocess.STDOUT,timeout=600)
 r['build_exit_code']=result.returncode;assert result.returncode==0
 exe=art/'xemu-reference238.exe';shutil.copyfile(s/'build/qemu-system-i386w.exe',exe)
 r.update(passed=True,executable_sha256=sha(exe),executable_bytes=exe.stat().st_size,source_manifest_sha256=sha(k/'candidate001-source-pins.json'))
except BaseException as exc:r['error']=repr(exc);raise
finally:
 for n,data in original.items():(s/n).write_bytes(data)
 r['borrowed_sources_restored']=all((s/n).read_bytes()==v for n,v in original.items())
 dest.write_text(json.dumps(r,indent=2)+'\n')
print('227 opt-in xemu candidate compiled; borrowed sources restored')

