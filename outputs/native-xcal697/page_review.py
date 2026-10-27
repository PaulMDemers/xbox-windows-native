"""Actual nxdk COFF arithmetic under Unicorn; harness memcpy helper; no kernel/API/physical execution."""
import hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn697/build001')
sys.path.insert(0,str(W/'work/python-packages'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_EIP
out=K/'page-review001.json';assert not out.exists()
b=(P/'page.obj').read_bytes();r={'passed':False,'object_sha256':hashlib.sha256(b).hexdigest(),'scope':__doc__,'cases':[]}
try:
 machine,nsec,_,symptr,nsyms,optsz,_=struct.unpack_from('<HHLLLHH',b);assert machine==0x14c and not optsz
 strings=b[symptr+18*nsyms:];sections=[];symbols={};indices={};i=0
 for j in range(nsec):
  h=struct.unpack_from('<8sLLLLLLHHL',b,20+40*j)
  sections.append({'base':0x100000+j*0x10000,'size':h[3],'raw':h[4],'reloc':h[5],'count':h[7]})
 while i<nsyms:
  name,value,sec,typ,storage,aux=struct.unpack_from('<8sLhHBB',b,symptr+18*i)
  name=(strings[struct.unpack('<L',name[4:])[0]:] if name[:4]==b'\0'*4 else name).split(b'\0')[0].decode()
  if sec>0:indices[i]=sections[sec-1]['base']+value;symbols[name]=indices[i]
  elif name=='_memcpy':indices[i]=0x300000
  i+=aux+1
 u=Uc(UC_ARCH_X86,UC_MODE_32)
 u.mem_map(0x300000,4096)
 # Harness cdecl memcpy, preserves ESI/EDI. This is not the nxdk libc implementation.
 u.mem_write(0x300000,bytes.fromhex('57568b7c240c8b7424108b4c241489f8fcf3a45e5fc3'))
 for s in sections:
  u.mem_map(s['base'],0x10000)
  if s['size']:u.mem_write(s['base'],b[s['raw']:s['raw']+s['size']])
 for s in sections:
  for j in range(s['count']):
   off,idx,typ=struct.unpack_from('<LLH',b,s['reloc']+j*10);assert idx in indices
   addr=s['base']+off;old=struct.unpack('<L',u.mem_read(addr,4))[0]
   assert typ in (6,20)
   value=old+indices[idx]-(addr+4 if typ==20 else 0)
   u.mem_write(addr,struct.pack('<L',value&0xffffffff))
 u.mem_map(0x200000,0x10000)
 steps=[0]
 def step(uc,pc,n,user):steps[0]+=1
 u.hook_add(UC_HOOK_CODE,step)
 def call(name,args,want,label):
  u.reg_write(UC_X86_REG_ESP,0x208000)
  u.mem_write(0x208000,struct.pack('<'+'L'*(len(args)+1),0x20ff00,*args))
  steps[0]=0
  u.emu_start(symbols[name],0x20ff00,count=100000)
  r['latest']={'case':label,'instructions':steps[0],'stopped_eip':u.reg_read(UC_X86_REG_EIP)}
  assert u.reg_read(UC_X86_REG_EIP)==0x20ff00
  actual=u.reg_read(UC_X86_REG_EAX);assert actual==want&0xffffffff,(label,actual,want)
  r['cases'].append({'case':label,'actual':actual,'instructions':steps[0]})
 blob=(P/'stub.bin').read_bytes();meta=json.loads((K/'extract001.json').read_text());o=meta['offsets']
 codeptr=0x203000;outptr=0x201000;u.mem_write(codeptr,blob)
 good=[outptr,codeptr,4096,o['code_end'],o['flat'],o['fault'],0x1eff000,0x3000000]
 for name,updates,want in [('dual',{},1),('relocated',{6:0x1edc000},1),('bad size',{2:4095},0),('code overlaps tables',{3:1217},0),('bad flat',{4:o['code_end']},0),('bad fault',{5:o['code_end']},0),('unaligned target',{6:0x1eff001},0),('fb wrap',{7:0xfffff000},0),('fb overlap',{7:0x1eff000},0)]:
  args=good.copy()
  for i,v in updates.items():args[i]=v
  u.mem_write(outptr-64,b'\xa5'*4224)
  call('_page697',args,want,name)
  assert bytes(u.mem_read(outptr-64,64))==bytes(u.mem_read(outptr+4096,64))==b'\xa5'*64
  if want:
   expected=(Path('C:/xwn697/cpu001')/name/'page.bin').read_bytes()
   assert bytes(u.mem_read(outptr,4096))==expected,'nxdk page builder differs from CPU fixture page'
  else:assert bytes(u.mem_read(outptr,4096))==b'\xa5'*4096
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS nxdk page-builder output equals tested CPU pages; rejection outputs and guards unchanged')
