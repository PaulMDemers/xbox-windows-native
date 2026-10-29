"""Build791 horizontal timing checkpoint candidate for isolated CPU tests; no XBE/native launch."""
import hashlib,json,os,subprocess,sys,datetime
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];O=Path('/mnt/c/xwn791/payload005')
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert not O.exists() and not (K/'payload005.json').exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
r={'passed':False,'physical_access':False,'space':require_space(O,20.05),
   'sources':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [K/n for n in ['transaction791.c','transaction.h','probe.c','probe.h']]}}
O.mkdir(parents=True)
try:
 cc=Path('/usr/bin/gcc-12').resolve();r['compiler_sha256']=hashlib.sha256(cc.read_bytes()).hexdigest()
 assert r['compiler_sha256']=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
 commands=[('compile32',[str(cc),'-m32','-Oz','-ffreestanding','-fno-pie','-fno-pic',
  '-fno-stack-protector','-Wall','-Wextra','-Werror','-nostdlib','-static','-no-pie',
  '-Wl,-Ttext=0x100000,-e,native_transaction704,--build-id=none,--emit-relocs,-z,max-page-size=0x20',str(K/'transaction791.c'),str(K/'probe.c'),'-o',str(O/'native.elf')]),
  ('relocations',['readelf','-rW',str(O/'native.elf')]),
  ('objcopy',['objcopy','-O','binary',str(O/'native.elf'),str(O/'native.bin')]),
  ('symbols',['nm','-n',str(O/'native.elf')]),('disassembly',['objdump','-d',str(O/'native.elf')])]
 for name,cmd in commands:
  p=subprocess.run(cmd,capture_output=True,timeout=60)
  (O/(name+'.stdout')).write_bytes(p.stdout);(O/(name+'.stderr')).write_bytes(p.stderr)
  r[name]={'command':cmd,'returncode':p.returncode,'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr':p.stderr.decode()}
  assert p.returncode==0,(name,p.stderr.decode())
 raw=(O/'native.bin').read_bytes();assert len(raw)<=19456
 r['unpadded_bytes']=len(raw);r['unpadded_sha256']=hashlib.sha256(raw).hexdigest()
 (O/'payload.bin').write_bytes(raw+b'\xcc'*(19456-len(raw)))
 r['diagnostic_checkpoint']=0x791;r['payload_extent_bytes']=19456
 r['files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in O.iterdir() if p.is_file()}
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 (K/'payload005.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS fresh32-bit horizontal timing checkpoint build; no hardware access')
