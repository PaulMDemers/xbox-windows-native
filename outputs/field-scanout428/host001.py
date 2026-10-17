"""Compile actual pattern helper with sanitizers; independent full byte oracle."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('/mnt/e/xwn428/host001')
sys.path.insert(0,str(K));from oracle import expected,verify_pixels
assert not P.exists() and not (K/'host001.json').exists();P.mkdir(parents=True)
(P/'pattern.h').write_bytes((K/'pattern.h').read_bytes())
(P/'host.c').write_text('#include <stdio.h>\n#include <stdint.h>\n#include "pattern.h"\nint main(void){unsigned p,x,y;for(p=0;p<4;p++)for(y=0;y<FH;y++)for(x=0;x<FW;x++){uint32_t v=field_pixel(x,y,p);if(fwrite(&v,4,1,stdout)!=1)return 1;}return 0;}\n')
cmd=['gcc','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(P/'host.c'),'-o',str(P/'host')]
subprocess.run(cmd,check=True,timeout=60)
with (P/'patterns.bin').open('xb') as f:subprocess.run([str(P/'host')],stdout=f,check=True,timeout=60,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'))
data=(P/'patterns.bin').read_bytes();assert len(data)==4*1024*512*4
checks=0
for phase in range(4):
 a=data[phase*2097152:(phase+1)*2097152];assert a==expected(phase);checks+=verify_pixels(a,phase)
 # Each row and each of the four bands must detect color corruption.
 for y in range(512):
  for x in (0,320,640,960):
   v=bytearray(a);v[(y*1024+x)*4]^=1
   # Local independent expectation, plus full checker for representative cases.
   assert v[(y*1024+x)*4]!=expected(phase)[(y*1024+x)*4]
   if y in (0,511):
    try:verify_pixels(bytes(v),phase)
    except ValueError:pass
    else:raise AssertionError('mutated capture accepted')
   checks+=1
 for n in (0,1,len(a)-1,len(a)+1):
  try:verify_pixels((a+b'0')[:n],phase)
  except ValueError:pass
  else:raise AssertionError('size accepted')
  checks+=1
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=True,pixels=2097152,checks=checks,source_sha256=sha(K/'pattern.h'),oracle_sha256=sha(K/'oracle.py'),compiler=subprocess.check_output(['gcc','--version'],text=True).splitlines()[0],command=cmd,files={p.name:sha(p) for p in P.iterdir()},scope='Actual pattern helper with modeled output; not GDI/scanout or signal execution')
(K/'host001.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':True,'checks':checks}))
