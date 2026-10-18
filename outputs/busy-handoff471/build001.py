"""Integrate exact470 busy predicate into both exact468 marker placements."""
import hashlib,json,os,shutil,struct,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('/mnt/c/xwn468/build001');O=Path('/mnt/c/xwn471/build001')
sha=lambda b:hashlib.sha256(b).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists() and not (K/'build001.json').exists()
assert shutil.disk_usage('/mnt/c').free-32*1024**2>=20*1024**3
parent=json.loads((K.parent/'marker-capture468/build001.json').read_text())
for name,v in parent['files'].items():assert sha(Path(name).read_bytes())==v['sha256'],name
core=K.parent/'marker-busy470/marker.S';h=json.loads((core.parent/'host001.json').read_text())
assert h['status']=='passed' and sha(core.read_bytes())==h['source'][str(core)]
cc=Path('/usr/bin/x86_64-linux-gnu-gcc-12');assert sha(cc.read_bytes())==h['compiler_sha256']
old=(K.parent/'entry-marker465/marker.S').read_text().replace('.section .note.GNU-stack,"",@progbits','')
new=core.read_text().replace('.section .note.GNU-stack,"",@progbits','')
source=(P/'xbeboot.S').read_text();assert source.count(old)==1
source=source.replace(old,new).replace('468','471')
assert source.replace(new,old).replace('471','468')==(P/'xbeboot.S').read_text()
O.mkdir(parents=True);(O/'xbeboot.S').write_text(source)
stub_source=(K.parent/'marker-handoff466/after-stack.S').read_text()+'\n'+new
(O/'stub.S').write_text(stub_source)
for name in ['xbe.S','font.S']:shutil.copyfile(P/name,O/name)
commands=[]
def run(cmd):
 commands.append(cmd)
 with (O/'build.log').open('a') as f:subprocess.run(cmd,cwd=O,stdout=f,stderr=f,check=True,timeout=30)
def syms(name):
 s=subprocess.check_output(['nm','-n',name],cwd=O,text=True);(O/(name+'.symbols.txt')).write_text(s)
 return {v[2]:int(v[0],16) for line in s.splitlines() if len(v:=line.split())==3}
r=dict(status='building',physical_access=False,parent_sha256=parent['sha256'],source_parent_reconstructed=True,
 source_pins={str(p):sha(p.read_bytes()) for p in [K/'build001.py',P/'xbeboot.S',core,K.parent/'marker-handoff466/after-stack.S',cc]})
def save():(K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 run([str(cc),'-m32','-c','stub.S','-o','stub.o'])
 run(['ld','-m','elf_i386','-Ttext','0x02680000','-e','after_stack_stub','stub.o','-o','stub.elf'])
 run(['objcopy','-O','binary','stub.elf','stub.bin']);ss=syms('stub.elf')
 blob=(O/'stub.bin').read_bytes();oldpayload=(P/'payload.bin').read_bytes()
 assert ss==parent['stub_symbols'] and len(blob)==len(oldpayload)-0x80000
 payload=oldpayload[:0x80000]+blob
 delta=[dict(offset=i,old=a,new=b) for i,(a,b) in enumerate(zip(oldpayload,payload)) if a!=b]
 assert len(delta)==4 and sorted((v['old'],v['new']) for v in delta)==[(0,8),(0,8),(239,231),(239,231)]
 (O/'payload.bin').write_bytes(payload)
 run([str(cc),'-m32','-DASSEMBLER','-c','xbeboot.S','-o','xbeboot.o'])
 run(['ld','-m','elf_i386','-Ttext','0x10000','-e','_start','xbeboot.o','-o','wrapper.elf'])
 run(['objcopy','-O','binary','wrapper.elf','wrapper.bin']);ws=syms('wrapper.elf')
 assert ws==parent['wrapper_symbols']
 prefix=(O/'wrapper.bin').read_bytes();assert len(prefix)==0x3000
 original=(P/'default.xbe').read_bytes();xbe=bytearray(prefix+payload+original[0x3000+len(payload):]);xbe[:4096]=original[:4096]
 assert len(xbe)==len(original)
 xbe[0x348+36:0x348+56]=hashlib.sha1(struct.pack('<I',len(xbe)-4096)+xbe[4096:]).digest()
 (O/'default.xbe').write_bytes(xbe)
 r.update(status='compiled',sha256=sha(xbe),bytes=len(xbe),payload_bytes=len(payload),payload_sha256=sha(payload),
  payload_delta=delta,wrapper_symbols=ws,stub_symbols=ss,commands=commands,original_pre_tail_payload_exact=True)
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:
 r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in O.iterdir() if p.is_file()};save()
