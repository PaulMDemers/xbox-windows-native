"""Measure candidate native code sizes; no payload admission, XBE or runtime launch."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys
K=Path(__file__).resolve().parent; W=K.parents[1]; O=Path('/mnt/c/xwn817/measure003')
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert not O.exists() and not (K/'measure003.json').exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False,qualification=False,space=require_space(O,20.05),
       sources={n:sha(K/n) for n in ['transaction817.c','transaction.h','probe-native.c','probe-compact-native.c','probe-shared-native.c','probe-pairs-native.c','probe.h']},variants=[])
O.mkdir(parents=True)
try:
 cc=Path('/usr/bin/gcc-12').resolve();r['compiler_sha256']=sha(cc)
 assert r['compiler_sha256']=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
 for name,extra in [('pairs-native',[])]:
  p=O/name;p.mkdir()
  cmd=[str(cc),'-m32','-Oz',*extra,'-ffreestanding','-fno-pie','-fno-pic','-fno-stack-protector',
       '-Wall','-Wextra','-Werror','-nostdlib','-static','-no-pie',
       '-Wl,-Ttext=0x100000,-e,native_transaction704,--build-id=none,--emit-relocs,-z,max-page-size=0x20',
       str(K/'transaction817.c'),str(K/'probe-pairs-native.c'),'-o',str(p/'native.elf')]
  q=subprocess.run(cmd,capture_output=True,timeout=60)
  (p/'compile.stdout').write_bytes(q.stdout);(p/'compile.stderr').write_bytes(q.stderr)
  assert q.returncode==0,q.stderr.decode()
  for label,c in [('binary',['objcopy','-O','binary',str(p/'native.elf'),str(p/'native.bin')]),
                  ('symbols',['nm','-n',str(p/'native.elf')]),('disassembly',['objdump','-d',str(p/'native.elf')]),('sections',['readelf','-SW',str(p/'native.elf')]),('relocations',['readelf','-rW',str(p/'native.elf')])]:
   q=subprocess.run(c,capture_output=True,timeout=30);assert q.returncode==0,q.stderr.decode()
   (p/(label+'.stdout')).write_bytes(q.stdout)
  r['variants'].append(dict(name=name,command=cmd,raw_bytes=(p/'native.bin').stat().st_size,
      files={f.name:sha(f) for f in p.iterdir() if f.is_file()}))
 r['passed']=True
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 (K/'measure003.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps([(v['name'],v['raw_bytes']) for v in r['variants']]))
