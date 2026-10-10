"""Execute captured allocator arithmetic under mocked callees, never a guest grant."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'claim-arithmetic-tests.json';assert not dest.exists()
sys.path.insert(0,str(ws/'work/python-packages'))
import unicorn
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
r=json.loads((k/'capture004.json').read_text());p=k/'artifacts/kernel004/kernel-resident.bin';data=p.read_bytes()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(p)==r['kernel_resident_sha256'] and r['passed']
base=r['kernel_base'];entry=r['claim_address'];length=0xbc
body=data[entry-base:entry-base+length];assert body[-3:]==b'\xc2\x08\x00'
assert body[:3]==b'\x55\x8b\xec' and body== (k/'artifacts/kernel004/claim-window.bin').read_bytes()[:length]
global_addr=0x800360d0;counter_addr=0x8003ab64
for a in [entry,global_addr,counter_addr]:assert not any(v['rva']<=a-base<v['rva']+v['bytes'] for v in r['unmapped_pages'])
tests=[];checks=0
for old in [0,1,4095,4096,0x5000,0x5001,0x10000,0x10111,0x400000]:
 for request in [0xffffffff,0,1,4095,4096,4097,0x5000,0x5001,0x10000,0x10111,0x400000]:
  u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,0x400000);u.mem_write(base,data)
  u.mem_map(0x100000,0x10000);u.mem_map(0x200000,4096);u.mem_map(0x300000,4096)
  stack=0x108000;u.mem_write(stack,struct.pack('<III',0x300000,request,0x200000));u.mem_write(0x200000,b'\xa5'*4)
  u.mem_write(global_addr,struct.pack('<I',old));u.mem_write(counter_addr,struct.pack('<I',0x2000));u.reg_write(UC_X86_REG_ESP,stack)
  saved={UC_X86_REG_EBP:0x12340000,UC_X86_REG_EBX:0x23450000,UC_X86_REG_ESI:0x34560000,UC_X86_REG_EDI:0x45670000}
  for reg,value in saved.items():u.reg_write(reg,value)
  calls=[]
  def hook(uc,a,n,unused):
   if a==0x300000:uc.emu_stop();return
   if a in [0x80014348,0x80014368,0x8001f899]:
    calls.append(dict(address=a,ecx=uc.reg_read(UC_X86_REG_ECX),edx=uc.reg_read(UC_X86_REG_EDX)))
    if a==0x80014348:uc.reg_write(UC_X86_REG_EAX,2)
    esp=uc.reg_read(UC_X86_REG_ESP);ret=struct.unpack('<I',uc.mem_read(esp,4))[0]
    uc.reg_write(UC_X86_REG_ESP,esp+4);uc.reg_write(UC_X86_REG_EIP,ret)
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(entry,0x300001,count=100000)
  query=request==0xffffffff;new=old if query else ((request+4095)//4096)*4096
  old_pages=(old+4095)//4096;new_pages=(new+4095)//4096
  freed=[] if query or new_pages>=old_pages else list(range(0x3ff0-old_pages,0x3ff0-new_pages))
  observed=[v['ecx'] for v in calls if v['address']==0x8001f899]
  assert observed==freed
  assert all(v['edx']&255==1 for v in calls if v['address']==0x8001f899)
  assert u.reg_read(UC_X86_REG_EAX)==0x83ff0000
  assert u.reg_read(UC_X86_REG_ESP)==stack+12
  assert struct.unpack('<I',u.mem_read(0x200000,4))[0]==0x10000
  assert struct.unpack('<I',u.mem_read(global_addr,4))[0]==new
  assert struct.unpack('<I',u.mem_read(counter_addr,4))[0]==0x2000-len(freed)
  assert len(calls)==(0 if query else 2+len(freed))
  assert all(u.reg_read(reg)==value for reg,value in saved.items())
  checks+=9;tests.append(dict(old_bytes=old,request=request,new_bytes=new,freed_pfns=len(freed),query_only=query))
dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(Path(__file__)),capture_sha256=sha(k/'capture004.json'),function_sha256=hashlib.sha256(body).hexdigest(),function_bytes=length,unicorn_version=unicorn.__version__,cases=len(tests),checks=checks,tests=tests,limits='Captured x86 arithmetic with mocked lock/free callees and host memory. Does not execute guest allocator, validate actual page freeing, transfer ownership, prove RAMIN physical alias or qualify a GPU operation.'),indent=2)+'\n',encoding='utf-8')
print('Captured claim arithmetic:',len(tests),'cases',checks,'checks PASS')
