"""Full826 linked entry and actual assembly startup with explicit device models.
No hardware/cache/timing proof. Stops at transaction entry; transaction_model001
separately executes its linked instructions against independent wire/MMIO oracles.
"""
from pathlib import Path
import hashlib,json,struct,sys,os,re
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('C:/xwn826/build003')
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'entry-model002.json';assert not out.exists()
r={'passed':False,'physical_access':False,'scope':__doc__,'cases':[]}
b=json.loads((K/'build003.json').read_text());assert b['passed']
for n,h in b['source_pins'].items():assert sha(K/n)==h
for n,h in b['artifacts'].items():assert sha(B/n)==h['sha256']
sym={a[2]:int(a[0],16) for l in (B/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}
blob=(B/'image-crom.bin').read_bytes();pack=lambda *a:struct.pack('<'+'I'*len(a),*a)
dis=(B/'disassembly.stdout').read_text();part=dis.split('<XcalEntry826>:')[1].split('\n\n')[0]
halt=int(re.findall(r'^\s*([0-9a-f]+):\s+f4\s+hlt',part,re.M)[0],16)
cases=['normal','ntsc-j','if-set','wrong-cs','wrong-ds','wrong-ss','cache-enabled','pae','bad-framebuffer','wrong-width','timer-stall','timer-backwards','busy8','busy800','dirty1','dirty10','bad-cable','pal','480-disabled','short-block','final-dirty','assembly-startup','boot-normal','boot-dirty','pitch-mismatch','format-mismatch','framebuffer-overlaps-firmware']
cases+=['pci'+str(i) for i in range(10)]+['error'+str(i) for i in range(1,8)]+['timeout1','timeout7','busy-terminal1']
try:
 for name in cases:
  c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0,0x4000000);c.mem_map(0xfd000000,0x800000);c.mem_write(0x2600000,blob)
  c.mem_write(0xa0000,struct.pack('<5Q',0,0x00cf9a000000ffff,0x00cf9a000000ffff,0x00cf92000000ffff,0x00cf92000000ffff))
  c.reg_write(x.UC_X86_REG_GDTR,(0,0xa0000,39,0));c.reg_write(x.UC_X86_REG_CR0,0x10033 if name=='cache-enabled' else 0x60010033)
  c.reg_write(x.UC_X86_REG_CR3,0x800);c.reg_write(x.UC_X86_REG_CR4,0x20 if name=='pae' else 0)
  for reg,value in [(x.UC_X86_REG_CS,8 if name=='wrong-cs' else 16),(x.UC_X86_REG_DS,32 if name=='wrong-ds' else 24),(x.UC_X86_REG_ES,24),(x.UC_X86_REG_SS,32 if name=='wrong-ss' else 24)]:c.reg_write(reg,value)
  c.reg_write(x.UC_X86_REG_EFLAGS,0x202 if name=='if-set' else 2)
  ptr=sym['XcalState826'];end=0x26ff000;sp=0x27fe000;c.reg_write(x.UC_X86_REG_ESP,sp);c.mem_write(sp,pack(end,ptr))
  pci={0x80010000:0x02a010de,0x80010004:2,0x80010010:0xfd000008,0x80000900:0x01b410de,0x80000904:1,0x80000914:0xc001,0x80000800:0x01b210de,0x80000804:1,0x80000810:0,0x80000884:0x8001}
  if name.startswith('pci'):pci[list(pci)[int(name[3:])]]=0xffffffff if name not in ['pci1','pci4','pci7'] else 0
  mm={0x600800:0x03fff000 if name=='bad-framebuffer' else 0x02600000 if name=='framebuffer-overlaps-firmware' else 0x03c5c000,0x680838:639 if name=='wrong-width' else 1279,0x680818:719}
  for off,v in mm.items():c.mem_write(0xfd000000+off,pack(v))
  state={'selector':0x87654320,'status':8 if name=='busy8' else 0x800 if name=='busy800' else 1 if name=='dirty1' else 0x10 if name in ['dirty10','boot-dirty'] else 0,'address':0,'reg':0,'count':0,'fifo':0,'ticks':0xfffffe00,'halt':False,'transaction':False}
  trace=[];commands=[];writes=[]
  cr={0x13:0x81 if name=='pitch-mismatch' else 0x80,0x19:0x51,0x25:0,0x28:0x81 if name=='format-mismatch' else 0x83};sel=[0x67]
  def indexed(c,kind,a,size,value,_):
   assert size==1
   if kind==u.UC_MEM_WRITE:assert a==0xfd6013d4;sel[0]=value
   elif a==0xfd6013d4:c.mem_write(a,bytes(sel))
   else:c.mem_write(a,bytes([cr[sel[0]]]))
  c.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,indexed,None,0xfd6013d4,0xfd6013d5)
  def inp(c,p,w,_):
   if p==0xcf8:assert w==4;v=state['selector']
   elif p==0xcfc:assert w==4;v=pci[state['selector']]
   elif p==0x8008:
    assert w==4;state['ticks']=(state['ticks']+(0 if name=='timer-stall' else -1 if name=='timer-backwards' else 1688))&0xffffffff;v=state['ticks']
   elif p==0xc000:
    assert w==2;v=state['status']
    if name=='final-dirty' and state['count']==7 and state['fifo']==4:v=0x10
   elif p==0xc006:
    if w==2:v=3 if name=='short-block' else 4
    else:
     assert w==1;std=0x00800300 if name=='pal' else 0x00400200 if name=='ntsc-j' else 0x00400100
     v=(6 if name=='bad-cable' else 1) if state['address']==0x21 else (0 if name=='480-disabled' else 8) if state['reg']==0x96 else (std>>((state['reg']-0x58)*8))&255
   elif p==0xc009:assert w==1;v=[0x12,0x34,0x56,0x78][state['fifo']];state['fifo']+=1
   else:raise AssertionError(('unreviewed input',p,w))
   trace.append(['in',p,w,v]);return v
  def output(c,p,w,v,_):
   trace.append(['out',p,w,v]);writes.append([p,w,v])
   if p==0xcf8:assert w==4;state['selector']=v
   elif p==0xc004:assert w==1 and v in [0x21,0xa9,0xe1];state['address']=v
   elif p==0xc008:assert w==1;state['reg']=v
   elif p==0xc002:
    assert w==1 and v in [10,13];state['count']+=1;t=state['count'];commands.append([state['address'],state['reg'],v])
    state['status']=0 if name=='timeout'+str(t) else 0x18 if name=='busy-terminal1' and t==1 else 0x37 if name=='error'+str(t) else 0x10
   elif p==0xc000:assert w==2 and v==state['status'] and v in [0x10,0x37];state['status']&=~v
   else:raise AssertionError(('unreviewed output',p,w,v))
  def stop(c,a,size,_):state['halt']=True;c.emu_stop()
  def transaction(c,a,size,_):
   state['transaction']=True;esp=c.reg_read(x.UC_X86_REG_ESP);args=struct.unpack('<4I',c.mem_read(esp+4,16))
   req=list(struct.unpack('<16I',c.mem_read(args[0],64)))
   assert req==[0x4000000,0x3700000,0x900000,3686400,1,1,1280,720,5120,32,1,1,0x80000,3375000,1,0x3c5c000]
   assert args[1:3]==(0xfd000000,0x3700000);c.emu_stop()
  def forbid(c,a,size,_):raise AssertionError(('legacy code reached',hex(a)))
  c.hook_add(u.UC_HOOK_INSN,inp,None,1,0,x.UC_X86_INS_IN);c.hook_add(u.UC_HOOK_INSN,output,None,1,0,x.UC_X86_INS_OUT)
  c.hook_add(u.UC_HOOK_CODE,stop,None,halt,halt);c.hook_add(u.UC_HOOK_CODE,transaction,None,sym['native_transaction704'],sym['native_transaction704'])
  for n in ['BootPciPeripheralInitialization','BootEepromReadEntireEEPROM','BootVgaInitializationKernelNG','BootFromDevice']:
   c.hook_add(u.UC_HOOK_CODE,forbid,None,sym[n],sym[n])
  entry='start_linux' if name=='assembly-startup' else 'BootResetAction' if name.startswith('boot-') else 'XcalCollect826'
  c.emu_start(sym[entry],end,timeout=15000000,count=20000000)
  vals=list(struct.unpack('<34I',c.mem_read(ptr,136)))
  expected=2001 if name in ['if-set','wrong-cs','wrong-ds','wrong-ss','cache-enabled','pae'] else 2002 if name.startswith('pci') else 2003 if name in ['bad-framebuffer','wrong-width','pitch-mismatch','format-mismatch','framebuffer-overlaps-firmware'] else 2004 if name.startswith('timer-') else 2 if name in ['busy8','busy800'] else 3 if name in ['dirty1','dirty10','boot-dirty'] else 2005 if name in ['bad-cable','pal','480-disabled'] else 6 if name=='short-block' else 7 if name=='final-dirty' else 5 if name.startswith('error') else 4 if name.startswith('timeout') or name=='busy-terminal1' else 0
  assert vals[0]==0x584e0826 and vals[2]==expected,(name,vals)
  if entry=='XcalCollect826':assert c.reg_read(x.UC_X86_REG_EIP)==end and c.reg_read(x.UC_X86_REG_EAX)==int(expected==0)
  elif name=='boot-dirty':
   assert state['halt'] and not state['transaction']
   assert c.mem_read(0x03c5c000+8*5120+8*4,4)==pack(0xffff8000)
   assert c.mem_read(0x03c5c000+128*5120+90*4,4)==pack(0xff000000)
   assert c.mem_read(0x03c5c000,8*5120)==bytes(8*5120)
  else:assert state['transaction'] and not state['halt']
  assert bool(c.reg_read(x.UC_X86_REG_EFLAGS)&0x200)==(name=='if-set')
  assert state['selector']==0x87654320
  if expected==2001:assert not trace
  if name.startswith('busy') or name.startswith('dirty') or name=='boot-dirty':assert not any(p==0xc000 for p,_,_ in writes)
  r['cases'].append({'name':name,'state':vals,'entry':entry,'transaction_reached':state['transaction'],'commands':commands,'trace_sha256':hashlib.sha256(json.dumps(trace).encode()).hexdigest(),'selector_restored':True,'IF_unchanged':True})
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS',len(r['cases']),'full-image entry/assembly fixtures')
