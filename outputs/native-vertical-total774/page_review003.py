"""Actual nxdk COFF arithmetic under Unicorn; harness memcpy helper; no kernel/API/physical execution."""
import hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn774/build002')
sys.path.insert(0,str(W/'work/python-packages'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_EIP
out=K/'page-review001.json';assert not out.exists()
b=(P/'page002.obj').read_bytes();r={'passed':False,'object_sha256':hashlib.sha256(b).hexdigest(),'scope':__doc__,'cases':[]}
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
  elif name=='_memset':indices[i]=0x300100
  i+=aux+1
 u=Uc(UC_ARCH_X86,UC_MODE_32)
 u.mem_map(0x300000,4096)
 # Harness cdecl memcpy, preserves ESI/EDI. This is not the nxdk libc implementation.
 u.mem_write(0x300000,bytes.fromhex('57568b7c240c8b7424108b4c241489f8fcf3a45e5fc3'))
 u.mem_write(0x300100,bytes.fromhex('578b7c24088b44240c8b4c241089fafcf3aa89d05fc3'))
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
 u.mem_map(0x200000,0x40000)
 steps=[0]
 def step(uc,pc,n,user):steps[0]+=1
 u.hook_add(UC_HOOK_CODE,step)
 def call(name,args,want,label):
  u.reg_write(UC_X86_REG_ESP,0x208000)
  u.mem_write(0x208000,struct.pack('<'+'L'*(len(args)+1),0x20ff00,*args))
  steps[0]=0
  u.emu_start(symbols[name],0x20ff00,timeout=3000000,count=2000000)
  r['latest']={'case':label,'instructions':steps[0],'stopped_eip':u.reg_read(UC_X86_REG_EIP)}
  assert u.reg_read(UC_X86_REG_EIP)==0x20ff00
  actual=u.reg_read(UC_X86_REG_EAX);assert actual==want&0xffffffff,(label,actual,want)
  r['cases'].append({'case':label,'actual':actual,'instructions':steps[0]})
 h=Path('C:/xwn774/host002');build=json.loads((K/'host002.json').read_text())
 codeptr=0x201000;metaptr=0x202000;payloadptr=0x203000;relptr=0x207000;outptr=0x210000
 u.mem_write(codeptr,(h/'bridge.bin').read_bytes());u.mem_write(payloadptr,(h/'payload.bin').read_bytes())
 meta=build['metadata'];rels=[v for v in build['relocations'] if v['type']=='R_386_32']
 relbytes=b''.join(struct.pack('<II',v['offset'],v['value']) for v in rels)
 def reset():
  u.mem_write(metaptr,struct.pack('<5I',*meta));u.mem_write(relptr,relbytes);u.mem_write(outptr-64,b'G'*(32768+128))
 good=[outptr,codeptr,metaptr,payloadptr,14080,relptr,13,0x1ef0000,0x3000000]
 cases=[('dual',{},1),('relocated',{7:0x1ed8000},1),('size',{4:14079},0),('count',{6:14},0)]
 for i,v in enumerate([0,0x1000001,0x1ff9000,0xfffff000]):cases.append(('base'+str(i),{7:v},0))
 for i,v in enumerate([0,0x1fff000,0x2600000,0x3fff000,0xfffff000]):cases.append(('fb'+str(i),{8:v},0))
 for name,updates,want in cases:
  reset();args=good.copy()
  for i,v in updates.items():args[i]=v
  call('_page705',args,want,name)
  assert bytes(u.mem_read(outptr-64,64))==bytes(u.mem_read(outptr+32768,64))==b'G'*64
  assert bytes(u.mem_read(outptr,32768))==((h/name/'page.bin').read_bytes() if want else b'G'*32768)
 for i in range(5):
  reset();u.mem_write(metaptr+4*i,struct.pack('<I',0xffffffff));call('_page705',good,0,'meta'+str(i));assert bytes(u.mem_read(outptr-64,32896))==b'G'*32896
 for i in range(13):
  reset();u.mem_write(relptr+8*i+4,struct.pack('<I',rels[i]['value']^1));call('_page705',good,0,'reloc'+str(i));assert bytes(u.mem_read(outptr-64,32896))==b'G'*32896
 reset();args=good.copy();args[6]=0;call('_page705',args,0,'zero-count');assert bytes(u.mem_read(outptr-64,32896))==b'G'*32896
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS nxdk774 page-builder cases:',len(r['cases']))
