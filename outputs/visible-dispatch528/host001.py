"""One fresh ASan/UBSan engine run and independent receipt transport mutations."""
import hashlib,json,shutil,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('C:/xwn528/host001')
assert not O.exists() and not (K/'host001.json').exists()
assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
O.mkdir(parents=True);sys.path.insert(0,str(K))
from entry_decode import decode
for n in ('engine.c','engine.h','engine-host.c'):shutil.copyfile(K/n,O/n)
r=dict(passed=False,actual_engine=True,OS_services='MODELED',physical_access=False)
def cmd(args,log):
 p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
 (O/log).write_bytes(p.stdout);assert p.returncode==0,p.stdout.decode(errors='replace');return p.stdout.decode()
try:
 r['compile']=cmd(['wsl','-d','Ubuntu','--','cc','-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-g','/mnt/c/xwn528/host001/engine.c','/mnt/c/xwn528/host001/engine-host.c','-o','/mnt/c/xwn528/host001/engine-host'],'compile.txt')
 r['run']=cmd(['wsl','-d','Ubuntu','--','/mnt/c/xwn528/host001/engine-host','/mnt/c/xwn528/host001/model.bin'],'run.txt')
 data=(O/'model.bin').read_bytes();assert len(data)==96
 for stage in (1,2):assert decode(data[(stage-1)*48:stage*48],stage)['stage']==stage
 entry=data[48:];(K/'model-entry.bin.hex').write_text(entry.hex()+'\n')
 cases=[]
 for i in range(48):
  b=bytearray(entry);b[i]^=1;cases.append(bytes(b))
 cases += [entry[:n] for n in range(48)]+[entry+b'\0',data[:48]]
 # Repaired checksums force semantic validation independently of checksum rejection.
 for index,value in [(0,0),(1,2),(2,47),(3,526),(4,0),(4,3),(5,2),(6,1),(7,0),(7,65536),(8,65536),(9,0),(9,2),(10,1)]:
  v=list(struct.unpack('<12I',entry));v[index]=value;b=struct.pack('<11I',*v[:11]);h=2166136261
  for c in b:h=((h^c)*16777619)&0xffffffff
  cases.append(b+struct.pack('<I',h))
 for b in cases:
  try:decode(b)
  except ValueError:pass
  else:raise AssertionError('bad transport accepted')
 r.update(passed=True,transport_rejections=len(cases),engine_scenarios=19)
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['private_files']={str(p):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in O.rglob('*') if p.is_file()}
 (K/'host001.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS engine19 and independent transport',len(cases))
