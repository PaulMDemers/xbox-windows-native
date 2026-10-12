"""Freeze and test the new core and independent transport; no actual GL or guest."""
import hashlib,json,subprocess,sys,struct,traceback
from pathlib import Path
import decode
k=Path(__file__).resolve().parent;attempt=sys.argv[1];assert attempt.isdecimal()
dest=k/('host'+attempt+'.json');assert not dest.exists();out=Path('E:/Codex-archive/xbox-windows-native/life284-host'+attempt);out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['lifetime.h','test.c','decode.py','test-host.py']:(out/n).write_bytes((k/n).read_bytes())
base='/mnt/e/Codex-archive/xbox-windows-native/life284-host'+attempt
r=dict(passed=False,host_only=True,guest_launched=False,actual_renderer_hook_coverage=False,
 models='Owner IDs and original allocation/GL/free/bind callbacks explicitly supplied by host; no real callback or publication adapter yet')
rejected=0
keys=[bytes((u*31+j)%256 for j in range(32)) for u in range(4)];ids=list(range(100,104));names=list(range(10,14))
def reject(data):
 global rejected
 try:decode.decode(data,keys,ids,names)
 except (AssertionError,struct.error):rejected+=1
 else:raise AssertionError('Invalid generation record accepted')
try:
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--','gcc','-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',base+'/test.c','-o',base+'/test'],capture_output=True,timeout=60)
 r.update(compile_exit=p.returncode,compile_output=(p.stdout+p.stderr).decode());assert p.returncode==0
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--','sh','-c','cd '+base+' && ./test'],capture_output=True,timeout=60)
 r.update(test_exit=p.returncode,test_output=(p.stdout+p.stderr).decode());assert p.returncode==0
 for name in ['control.bin','reuse.bin','fresh.bin','cross-reuse.bin']:
  data=(out/name).read_bytes();decode.decode(data,keys,ids,names)
  for word in range(12):
   m=bytearray(data);value=struct.unpack_from('<Q',m,word*8)[0]
   # A positive changed owner is meaningful only when linked to real runtime attestation.
   struct.pack_into('<Q',m,word*8,0 if word==4 else value^1);reject(bytes(m))
  for u in range(4):
   at=96+1336*u
   for field in range(11):
    m=bytearray(data);value=struct.unpack_from('<Q',m,at+field*8)[0];struct.pack_into('<Q',m,at+field*8,value^1);reject(bytes(m))
   for field in range(28):
    m=bytearray(data);off=at+1112+field*8;value=struct.unpack_from('<Q',m,off)[0];struct.pack_into('<Q',m,off,value^1);reject(bytes(m))
   for byte in range(1024):
    m=bytearray(data);m[at+88+byte]^=1;reject(bytes(m))
  for trim in [1,8,56,1024,len(data)-1]:reject(data[:-trim])
  reject(data+b'\0'*8)
 reject((out/'failed-saturation.bin').read_bytes())
 r.update(passed=True,independent_transport_mutations_rejected=rejected)
except BaseException as e:r.update(error=repr(e),traceback=traceback.format_exc())
r['files']={p.name:sha(p) for p in out.iterdir() if p.is_file()};dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({a:v for a,v in r.items() if a!='files'},indent=2));assert r['passed']
