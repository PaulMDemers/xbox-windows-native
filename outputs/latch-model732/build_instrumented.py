"""Fresh host-only build of unchanged704 source; no old runtime/image reused."""
import datetime, hashlib, json, os, subprocess, sys
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]; S=K.parent/'xcal-transaction704'
P=Path('/mnt/c/xwn732/build002'); out=K/'build002.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not P.exists() and not out.exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
r={'passed':False,'physical_access':False,'space':require_space(P,20.05),'sources':{p.name:sha(p) for p in S.glob('*.[ch]')}}
assert sha(S/'transaction003.c')=='6336794d817f0b801db939b2611c1832736acad598e71437f9ca87bc797a345b'
P.mkdir(parents=True)
try:
 cc=Path('/usr/bin/gcc-12').resolve();r['compiler_sha256']=sha(cc)
 assert r['compiler_sha256']=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
 # Copy source only, never a closed runtime or executable.
 for p in S.glob('*.[ch]'):(P/p.name).write_bytes(p.read_bytes())
 (P/'transaction732.c').write_bytes((K/'transaction732.c').read_bytes())
 r['diagnostic_source_sha256']=sha(K/'transaction732.c')
 commands=[('compile',[str(cc),'-m32','-Os','-ffreestanding','-fno-pie','-fno-pic','-fno-stack-protector','-Wall','-Wextra','-Werror','-nostdlib','-static','-no-pie','-Wl,-Ttext=0x100000,-e,native_transaction704,--build-id=none,--emit-relocs',*[str(P/n) for n in ['transaction732.c','encoder.c','xcal_bus.c','gpu_legacy.c']],'-o',str(P/'native.elf')]),('objcopy',['objcopy','-O','binary',str(P/'native.elf'),str(P/'native.bin')]),('symbols',['nm','-n',str(P/'native.elf')]),('disassembly',['objdump','-d',str(P/'native.elf')])]
 for name,cmd in commands:
  cp=subprocess.run(cmd,capture_output=True,timeout=60)
  (P/(name+'.stdout')).write_bytes(cp.stdout);(P/(name+'.stderr')).write_bytes(cp.stderr)
  r[name]={'command':cmd,'exit_code':cp.returncode};assert cp.returncode==0,cp.stderr.decode()
 r['files']={p.name:sha(p) for p in P.iterdir() if p.is_file()}
 r['same_binary_as704_build004']=sha(P/'native.bin')==json.loads((S/'build004.json').read_text())['files']['native.bin']
 assert not r['same_binary_as704_build004'];r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS fresh732 host build, RAM-only instrumented setup predicate; no hardware access')
