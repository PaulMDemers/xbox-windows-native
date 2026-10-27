"""Fresh linked-image entry fixtures. PCI/SMBus are explicit models, not hardware."""
import hashlib,json,re,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('C:/xwn689/build001')
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=json.loads((K/'build001.json').read_text());assert build['passed']
for n,v in build['artifacts'].items():assert sha(B/n)==v['sha256']
blob=(B/'image-crom.bin').read_bytes()
sym={a[2]:int(a[0],16) for line in (B/'symbols.stdout').read_text().splitlines() if len(a:=line.split())==3}
dis=(B/'disassembly.stdout').read_text();part=dis.split('<XcalEntry689>:')[1].split('\n\n')[0]
halt=int(re.findall(r'^\s*([0-9a-f]+):\s+f4\s+hlt',part,re.M)[0],16)
out=K/'compiled001.json';assert not out.exists()
r={'passed':False,'physical_access':False,'image_sha256':sha(B/'image-crom.bin'),
   'scope':'Actual linked entry/config/block code; modeled PCI and W1C SMBus. Does not execute prior assembly startup or validate hardware.', 'cases':[]}
pack=lambda *a:struct.pack('<'+'I'*len(a),*a)
try:
 cases=['normal','ntsc-j','if-set','wrong-cs','wrong-ds','wrong-id','wrong-bar','io-disabled','busy','dirty','bad-cable','pal','unknown-standard','480-disabled','short-block','final-dirty']
 cases+=['error'+str(i) for i in range(1,8)]+['timeout1','timeout7','boot-normal','boot-error','boot-led-busy','boot-led-error1','boot-led-error2','boot-led-timeout1','boot-led-timeout2']
 for name in cases:
  uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);uc.mem_map(0x2600000,0x100000);uc.mem_write(0x2600000,blob)
  uc.mem_map(0x27f0000,0x10000);uc.mem_map(0x300000,0x1000)
  gdt=[0,0x00cf9a000000ffff,0x00cf9a000000ffff,0x00cf92000000ffff,0x00cf92000000ffff]
  uc.mem_write(0x300000,struct.pack('<5Q',*gdt));uc.reg_write(x.UC_X86_REG_GDTR,(0,0x300000,39,0))
  uc.reg_write(x.UC_X86_REG_CR0,0x60010033)
  for reg,value in [(x.UC_X86_REG_CS,8 if name=='wrong-cs' else 16),(x.UC_X86_REG_DS,32 if name=='wrong-ds' else 24),(x.UC_X86_REG_ES,24),(x.UC_X86_REG_SS,24)]:uc.reg_write(reg,value)
  uc.reg_write(x.UC_X86_REG_EFLAGS,0x202 if name=='if-set' else 2)
  ptr=sym['XcalState689'];end=0x26ff000;sp=0x27fe000
  uc.reg_write(x.UC_X86_REG_ESP,sp);uc.mem_write(sp,pack(end,ptr))
  state={'selector':0x87654320,'status':0x800 if name=='busy' else 0x10 if name=='dirty' else 0,'address':0,'reg':0,'transactions':0,'index':0,'halted':False,'after_block':0}
  trace=[];commands=[];writes=[]
  def inp(uc,p,w,_):
   if p==0xcf8:assert w==4;v=state['selector']
   elif p==0xcfc:
    assert w==4
    v={0x80000900:0xffffffff if name=='wrong-id' else 0x01b410de,
       0x80000904:0 if name=='io-disabled' else 1,0x80000914:0xc101 if name=='wrong-bar' else 0xc001}[state['selector']]
   elif p==0xc000:
    assert w in [1,2];v=state['status']
    if state['index']==4 and w==2:
     state['after_block']+=1
     if name=='boot-led-busy' and state['after_block']==2:v=0x800
    if name=='final-dirty' and state['transactions']==7 and state['index']==4 and w==2:v=0x10
   elif p==0xc006:
    if w==2:v=3 if name=='short-block' else 4
    else:
     assert w==1
     std=0x00800300 if name=='pal' else 0x12400100 if name=='unknown-standard' else 0x00400200 if name=='ntsc-j' else 0x00400100
     a,reg=state['address'],state['reg']
     if a==0x21:assert reg==4;v=6 if name=='bad-cable' else 1
     else:
      assert a==0xa9 and reg in [0x58,0x59,0x5a,0x5b,0x96]
      v=(0 if name=='480-disabled' else 8) if reg==0x96 else (std>>((reg-0x58)*8))&255
   elif p==0xc009:
    assert w==1;v=[0x12,0x34,0x56,0x78][state['index']];state['index']+=1
   else:raise AssertionError(('unreviewed input',p,w))
   trace.append(['in',p,w,v]);return v
  def output(uc,p,w,v,_):
   trace.append(['out',p,w,v]);writes.append([p,w,v])
   if p==0xcf8:assert w==4;state['selector']=v
   elif p==0xc004:assert w==1 and v in [0x21,0xa9,0xe1,0x20];state['address']=v
   elif p==0xc008:assert w==1;state['reg']=v
   elif p==0xc006:assert w==2 and [state['address'],state['reg'],v] in [[0x20,8,0x5f],[0x20,7,1]]
   elif p==0xc002:
    assert w==1 and v in [0x0a,0x0d,0x1a];state['transactions']+=1;t=state['transactions'];commands.append([state['address'],state['reg'],v])
    state['status']=0 if name=='timeout'+str(t) or name=='boot-led-timeout'+str(t-7) else 0x36 if name=='error'+str(t) or name=='boot-led-error'+str(t-7) or (name=='boot-error' and t==1) else 0x10
   elif p==0xc000:
    assert w==2 and v==state['status'] and v in [0x10,0x36];state['status']&=~v
   else:raise AssertionError(('unreviewed output',p,w,v))
  def stopped(uc,a,size,_):state['halted']=True;uc.emu_stop()
  def forbidden(uc,a,size,_):raise AssertionError(('legacy startup reached',hex(a)))
  uc.hook_add(u.UC_HOOK_INSN,inp,None,1,0,x.UC_X86_INS_IN)
  uc.hook_add(u.UC_HOOK_INSN,output,None,1,0,x.UC_X86_INS_OUT)
  uc.hook_add(u.UC_HOOK_CODE,stopped,None,halt,halt)
  for n in ['BootPciPeripheralInitialization','BootEepromReadEntireEEPROM','BootVgaInitializationKernelNG','BootFromDevice']:
   uc.hook_add(u.UC_HOOK_CODE,forbidden,None,sym[n],sym[n])
  boot=name.startswith('boot-');uc.emu_start(sym['BootResetAction' if boot else 'XcalCollect689'],end,timeout=10000000,count=10000000)
  assert state['halted'] if boot else uc.reg_read(x.UC_X86_REG_EIP)==end
  result=list(struct.unpack('<23I',uc.mem_read(ptr,92)));magic,phase,error,completed=result[:4]
  assert magic==0x584e0689 and bool(uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200)==(name=='if-set')
  expected=2001 if name in ['if-set','wrong-cs','wrong-ds'] else 2002 if name=='wrong-id' else 2003 if name in ['wrong-bar','io-disabled'] else 2 if name=='busy' else 3 if name in ['dirty','final-dirty'] else 2004 if name in ['bad-cable','pal','unknown-standard','480-disabled'] else 6 if name=='short-block' else 5 if name.startswith('error') or name=='boot-error' else 4 if name.startswith('timeout') else 0
  assert error==expected,(name,result)
  if not boot:assert uc.reg_read(x.UC_X86_REG_EAX)==int(expected==0)
  if expected==0:assert phase==6 and completed==7 and result[20]==0x78563412
  if expected==2001:assert not trace
  else:assert state['selector']==0x87654320
  if name.startswith('error'):assert state['transactions']==int(name[5:]) and completed==state['transactions']-1
  if name.startswith('timeout'):
   assert state['transactions']==int(name[7:]) and completed==state['transactions']-1
   assert sum(1 for a in trace if a[:3]==['in',0xc000,1])==100000+completed
  if expected in [2002,2003,2] or name=='dirty':assert all(p==0xcf8 for p,_,_ in writes)
  if commands:
   expected_commands=[[0x21,4,0xa]]+[[0xa9,i,0xa] for i in [0x58,0x59,0x5a,0x5b,0x96]]+[[0xe1,0,0xd],[0x20,8,0x1a],[0x20,7,0x1a]]
   assert commands==expected_commands[:len(commands)]
  indicator=list(struct.unpack('<3I',uc.mem_read(sym['XcalIndicator689'],12)))
  if name=='boot-normal':assert indicator==[2,2,0] and len(commands)==9
  elif name=='boot-led-busy':assert indicator==[1,0,2] and len(commands)==7
  elif name.startswith(('boot-led-error','boot-led-timeout')):
   n=int(name[-1]);err=5 if name.startswith('boot-led-error') else 4
   assert indicator==[n,n-1,err] and len(commands)==7+n
  else:assert indicator==[0,0,0]
  r['cases'].append({'name':name,'result':result,'indicator':indicator,'halted':state['halted'],'transactions':commands,'port_operations':len(trace),'trace_sha256':hashlib.sha256(json.dumps(trace).encode()).hexdigest(),'writes':writes,'IF_preserved':True,'pci_selector_restored':state['selector']==0x87654320})
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS',len(r['cases']),'linked-image entry fixtures; no hardware')
