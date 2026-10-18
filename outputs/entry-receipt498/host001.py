"""Build/run exact proposed assembly in Linux i386; NT calls explicitly modeled."""
import datetime,hashlib,importlib.util,json,os,shutil,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent
O=Path('/mnt/c/xwn498/host001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert not O.exists() and not (K/'host001.json').exists()
assert shutil.disk_usage('/mnt/c').free-32*1024**2>=20*1024**3
O.mkdir(parents=True)
r=dict(started=utc(),passed=False,closed=True,physical_access=False,scope='Linux i386 execution of proposed entry assembly; Xbox services modeled; no privileged CPU/context or physical file guarantee',cases=[])
def save():(K/'host001.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
try:
 names=['entry.S','host.S','host.c','decode.py','host001.py']
 for n in names:shutil.copyfile(K/n,O/n)
 r['source_pins']={n:sha(O/n) for n in names}
 cmd=['gcc','-m32','-O2','-g','-fno-pie','-no-pie','-fno-stack-protector','-Wall','-Wextra','-Werror','-MMD','host.c','host.S','entry.S','-o','host']
 r['command']=cmd
 with (O/'build.log').open('xb') as f:subprocess.run(cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=60)
 (O/'disassembly.txt').write_bytes(subprocess.check_output(['objdump','-dr','-Mintel',str(O/'host')]))
 r['tool_pins']={p:sha(Path(p)) for p in ['/usr/bin/gcc','/usr/bin/as','/usr/bin/ld','/usr/bin/objdump']}
 r['compiler_version']=subprocess.check_output(['gcc','--version'],text=True).splitlines()[0]
 r['dependencies']=subprocess.check_output(['ldd',str(O/'host')],text=True)
 spec=importlib.util.spec_from_file_location('decoder498',O/'decode.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
 cases=[]
 flagbits=[1,4,16,64,128,1024,2048]
 for i in range(128):cases.append((0,0,0x202|sum(bit for j,bit in enumerate(flagbits) if i>>j&1),0))
 for call,kinds in [(1,range(1,7)),(2,range(1,6)),(3,[1,2,4,5]),(4,range(1,6)),(5,[1,2,4,5]),(6,[1])]:
  for kind in kinds:
   for df in (0,0x400):cases.append((call,kind,0x202|df,0))
   if call<6 and not (call==1 and kind in (1,4,6)):cases.append((call,kind,0x602,1))
 for i,case in enumerate(cases):
  output=O/f'case{i:03}.bin';argv=[str(O/'host'),*map(str,case),str(output)]
  p=subprocess.run(argv,cwd=O,capture_output=True,timeout=3)
  (O/f'case{i:03}.stdout').write_bytes(p.stdout);(O/f'case{i:03}.stderr').write_bytes(p.stderr)
  v=dict(index=i,parameters=case,exit_code=p.returncode)
  r['cases'].append(v);save()
  assert p.returncode==0,(case,p.stderr.decode(errors='replace'))
  v.update(json.loads(p.stdout));v['sha256']=sha(output)
  if case[0]==0:
   decoded=d.decode(output.read_bytes());assert decoded['entry_witness'] and not decoded['windows_boot_proved']
  elif case[0] in (5,6):
   # Commit bytes exist even when final flush/close failed: parser never claims those.
   decoded=d.decode(output.read_bytes());assert not decoded['final_flush_or_close_proved']
 good=(O/'case000.bin').read_bytes();rejects=0
 def reject(b):
  global rejects
  try:d.decode(b)
  except ValueError:rejects+=1
  else:raise AssertionError('accepted malformed entry transport')
 for i in range(112):reject(good[:i])
 reject(good+b'\0')
 for i in range(112):
  for bit in range(8):
   b=bytearray(good);b[i]^=1<<bit;reject(bytes(b))
 # Recomputed checksum still cannot make invalid version/reserved/selectors valid.
 import struct
 for index,value in [(1,2),(2,95),(3,0),(4,0),(13,0x10000),*[(x,1) for x in range(19,24)]]:
  b=bytearray(good);struct.pack_into('<I',b,index*4,value);h=2166136261
  for v in b[:96]:h=((h^v)*16777619)&0xffffffff
  struct.pack_into('<I',b,100,h);reject(bytes(b))
 r.update(passed=True,transport_mutations_rejected=rejects,case_count=len(cases),register_flag_success_cases=128,model_failure_and_cleanup_cases=len(cases)-128)
 assert all(sha(K/n)==r['source_pins'][n] for n in names)
except BaseException as e:r['error']=repr(e);raise
finally:
 r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()}
 r['finished']=utc();save()
