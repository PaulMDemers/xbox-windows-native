"""Freeze/test publication prototype. Never rebuild an already consumed ID."""
import hashlib,importlib.util,json,struct,subprocess,sys,traceback
from pathlib import Path
k=Path(__file__).resolve().parent;attempt=sys.argv[1];assert attempt.isdecimal()
dest=k/('host'+attempt+'.json');assert not dest.exists()
out=Path('E:/Codex-archive/xbox-windows-native/publication285-host'+attempt);out.mkdir(exist_ok=False)
for n in ['publication.h','test.c','decode.py','test-host.py']:(out/n).write_bytes((k/n).read_bytes())
for n,source in [('lifetime.h','lifetime.h'),('core_decode.py','decode.py')]:
 (out/n).write_bytes((k.parent/'replacement-life284'/source).read_bytes())
sys.path.insert(0,str(out));spec=importlib.util.spec_from_file_location('independent',out/'decode.py');dec=importlib.util.module_from_spec(spec);spec.loader.exec_module(dec)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();base='/mnt/e/Codex-archive/xbox-windows-native/publication285-host'+attempt
r=dict(passed=False,host_only=True,actual_renderer_adapter=False,guest_launched=False,
 models='C11 publication prototype; supplied owner IDs and core callbacks. No actual QEMU dispatcher/thread proof, GL or runtime hook.')
rejects=0;keys=[bytes((u*31+j)%256 for j in range(32)) for u in range(4)]
def reject(data,owner=123):
 global rejects
 try:dec.decode(data,owner,keys,list(range(100,104)),list(range(10,14)))
 except (AssertionError,struct.error):rejects+=1
 else:raise AssertionError('Invalid publication accepted')
try:
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--','gcc','-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-pthread',base+'/test.c','-o',base+'/test'],capture_output=True,timeout=60)
 r.update(compile_exit=p.returncode,compile_output=(p.stdout+p.stderr).decode());assert p.returncode==0
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--','sh','-c','cd '+base+' && ./test'],capture_output=True,timeout=60)
 r.update(test_exit=p.returncode,test_output=(p.stdout+p.stderr).decode());assert p.returncode==0
 for n in ['control.bin','candidate.bin']:
  d=(out/n).read_bytes();dec.decode(d,123,keys,list(range(100,104)),list(range(10,14)))
  for i in range(64):
   m=bytearray(d);m[i]^=1;reject(bytes(m))
  for i in range(12):
   m=bytearray(d);m[64+i*8]^=1;reject(bytes(m))
  reject(d,124)
  for trim in [1,8,64,5440,5503]:reject(d[:-trim])
  reject(d+b'\0')
 for n in ['foreign-failure.bin','busy-failure.bin','incomplete.bin']:reject((out/n).read_bytes())
 r.update(passed=True,independent_transport_mutations_rejected=rejects)
except BaseException as e:r.update(error=repr(e),traceback=traceback.format_exc())
r['files']={p.name:sha(p) for p in out.iterdir() if p.is_file()}
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:v for a,v in r.items() if a!='files'},indent=2));assert r['passed']
