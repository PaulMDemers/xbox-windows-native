"""Unique build attempt, exact269 source closure, leased replacement/restoration."""
import argparse,datetime,difflib,hashlib,importlib.util,json,os,shutil,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
arg=argparse.ArgumentParser();arg.add_argument('attempt');args=arg.parse_args()
assert args.attempt in ('002',)
spec=importlib.util.spec_from_file_location('patch278',k/'patch-renderer.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
assert os.environ.get('XWN_BUILD_LEASE')=='held'
dest=k/('renderer-build'+args.attempt+'.json');assert not dest.exists()
assert shutil.disk_usage('/mnt/c').free>=20*1024**3
s=Path('/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet')
base='e72e76bd1f12ce45c6c63b4196c6918ea2cc705d'
assert subprocess.check_output(['git','-c','safe.directory='+str(s),'rev-parse','HEAD'],cwd=s,text=True).strip()==base
prior=ws/'outputs/callback-inventory276';pins=json.loads((prior/'renderer-source-pins003.json').read_text())
names=['hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a_int.h','hw/xbox/nv2a/nv2a.h','hw/xbox/nv2a/pgraph/gl/renderer.c','hw/xbox/nv2a/pgraph/gl/renderer.h','hw/xbox/nv2a/pgraph/gl/surface.c','hw/xbox/nv2a/pfifo.c','hw/xbox/nv2a/pgraph/pgraph.c','system/physmem.c','system/trace-events','hw/xbox/nv2a/trace-events','hw/xbox/nv2a/pgraph/gl/display.c','ui/xemu.c','ui/xui/main.cc','ui/xemu-thumbnail.cc','hw/xbox/nv2a/pgraph/gl/shaders.c','hw/xbox/nv2a/pgraph/thirdparty/gloffscreen/gloffscreen.h','hw/xbox/nv2a/pgraph/thirdparty/gloffscreen/sdl.c','hw/xbox/nv2a/pgraph/gl/texture.c']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();original={n:(s/n).read_bytes() for n in names}
art=Path('/mnt/e/Codex-archive/xbox-windows-native/boundary278-build'+args.attempt);art.mkdir(parents=True,exist_ok=False)
parent=Path('/mnt/e/Codex-archive/xbox-windows-native/callback276-build003/source')
image='ghcr.io/xemu-project/xemu-win64-toolchain-gcc@sha256:a4b2fb230a429d69272cb403de29c1a7a01aa63d84d92b427e6c7d119927aa73'
inputs=['build-renderer.py','patch-renderer.py','patch-clock.py','clock.c','admission.h','adapter.c']
r=dict(passed=False,source_revision=base,toolchain=image,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 inputs={n:sha(k/n) for n in inputs},physical_access=False,guest_launch=False,gl_executed=False,
 original_sources={n:sha(s/n) for n in names})
for n in inputs:
    p=art/'inputs'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((k/n).read_bytes())
try:
 for n in names:
    p=parent/n
    if not p.is_file():p=s/n
    assert sha(p)==pins[n],n
    (s/n).write_bytes(p.read_bytes())
 for n,h in pins.items():
    if (s/n).is_file():assert sha(s/n)==h,n
 before={n:(s/n).read_bytes() for n in names};mod.apply(s)
 patch=[]
 for n in names:patch.extend(difflib.unified_diff(before[n].decode().splitlines(True),(s/n).read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n))
 delta=k/('renderer-delta'+args.attempt+'.patch');delta.write_text(''.join(patch));r['delta_sha256']=sha(delta)
 after={n:sha(s/n) for n in pins if (s/n).is_file()};(k/('renderer-source-pins'+args.attempt+'.json')).write_text(json.dumps(after,indent=2)+'\n')
 r['changed_sources']=[n for n in names if before[n]!=(s/n).read_bytes()]
 assert set(r['changed_sources'])=={'system/physmem.c','hw/xbox/nv2a/pgraph/gl/renderer.c'}
 for n in names+['COPYING','COPYING.LIB']:
    p=art/'source'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((s/n).read_bytes())
 with (k/('renderer-build'+args.attempt+'.log')).open('xb') as log:
    code=subprocess.run(['podman','run','--rm','--pull=never','-v',str(s)+':/src','-w','/src/build',image,'ninja','-j4','qemu-system-i386w.exe'],stdout=log,stderr=subprocess.STDOUT,timeout=600).returncode
 r['build_exit_code']=code;assert code==0
 exe=art/'xemu-boundary278.exe';shutil.copyfile(s/'build/qemu-system-i386w.exe',exe)
 r.update(passed=True,executable_sha256=sha(exe),executable_bytes=exe.stat().st_size)
except BaseException as exc:r['error']=repr(exc);raise
finally:
 for n,data in original.items():(s/n).write_bytes(data)
 r['borrowed_sources_restored']=all((s/n).read_bytes()==data for n,data in original.items())
 r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();dest.write_text(json.dumps(r,indent=2)+'\n')
print('278 opt-in callback admission compiled; no guest launch; borrowed sources restored')
