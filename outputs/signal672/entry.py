"""Fresh isolated i386 integration executions. CPU/PCI/NIC/SMC are models.
Actual codec, lifecycle, native inspection, admission, sender and hold execute.
No physical networking, closed runtime, XBE, boot, or DMA/coherency proof.
"""
import datetime,hashlib,json,re,struct,sys,zlib
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('C:/xwn672/build001')
out=K/'entry001.json';assert not out.exists()
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
sha=lambda b:hashlib.sha256(b).hexdigest()
build=json.loads((K/'build001.json').read_text());blob=(B/'image-crom.bin').read_bytes()
assert build['status']=='compiled-host-only-unqualified' and sha(blob)==build['artifacts']['image-crom.bin']['sha256']
sym={a[2]:int(a[0],16) for line in (B/'symbols.stdout').read_text().splitlines() if len(a:=line.split())==3}
dis=(B/'disassembly.stdout').read_text()
ins=lambda name:[int(m[1],16) for m in re.finditer(r'^\s*([0-9a-f]+):[^\n]*\t'+name+r'\b',dis,re.M)]
halt=sym['irq_hold669']+1
assert bytes(blob[halt-0x02600000:halt-0x02600000+1])==b'\xf4'
r=dict(passed=False,physical_access=False,new_XBE=True,source_sha256=sha(Path(__file__).read_bytes()),binary_sha256=sha(blob),cases=[])
def save():out.write_text(json.dumps(r,indent=2)+'\n')
def pack(*v):return struct.pack('<'+'I'*len(v),*v)
def words(uc,a,n=1):return struct.unpack('<'+'I'*n,uc.mem_read(a,n*4))
def csum(b):
 v=sum(struct.unpack('>'+'H'*(len(b)//2),b))
 while v>>16:v=(v&65535)+(v>>16)
 return v
identity=bytes(range(1,49));data=[0,1]+[0x13570000+i for i in range(174)]
expected=b'XWN655U1'+pack(1,772)+identity+pack(*data);expected+=pack(zlib.crc32(expected))
assert len(expected)==772
save()
try:
 cases=['success-if-set','success-if-clear','display-failure','unsupported','cpu-features','cache-default','pci-id','cleanup-command','invalid-codec','export-reentry','freeze-if-corruption','freeze-sample-corruption','smc-busy','smc-error','smc-timeout','timer-frozen','timer-backwards']
 for case in cases:
  uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32)
  uc.mem_map(0x02600000,0x200000);uc.mem_write(0x02600000,blob);uc.mem_map(0xa0000,0x1000);uc.mem_map(0xfef00000,0x1000)
  uc.mem_write(0xa0000,bytes(16)+pack(0xffff,0xcf9a00,0xffff,0xcf9200,0xffff,0xcf9200))
  uc.reg_write(x.UC_X86_REG_GDTR,(0,0xa0000,39,0));uc.reg_write(x.UC_X86_REG_CR0,1)
  for reg,val in [(x.UC_X86_REG_CS,0x10),(x.UC_X86_REG_DS,0x18),(x.UC_X86_REG_ES,0x18),(x.UC_X86_REG_SS,0x18)]:uc.reg_write(reg,val)
  uc.reg_write(x.UC_X86_REG_EFLAGS,2 if case=='success-if-clear' else 0x202)
  identity=bytes(uc.mem_read(sym['Identity657'],48));data=[0xffffffff if case=='display-failure' else 0 if case=='unsupported' else 1,2 if case=='display-failure' else 1]+[0x13570000+i for i in range(174)]
  data[86]=data[87]=data[133]=data[134]=0x202
  expected=b'XWN655U1'+pack(1,772)+identity+pack(*data);expected+=pack(zlib.crc32(expected))
  uc.mem_write(sym['xbox_ram'],pack(32 if case=='cpu-ram' else 64))
  ident=0x027e0000;datum=ident+0x100;cfg=ident+0x500;end=0x027ef000
  uc.mem_write(ident,identity);uc.mem_write(datum,pack(*data));uc.mem_write(cfg,bytes([2,0,0,0,0,1,192,0,2,1])+struct.pack('<H',50657))
  if case=='invalid-codec':uc.mem_write(sym['Identity657'],bytes(48))
  if case=='invalid-config':uc.mem_write(cfg,b'\x01')
  state=dict(regs={},pci=7,tick=0,frames=[],pci_reads=0,pci_writes=[],mmio_reads=0,mmio_writes=0,cache_syncs=0,timer_reads=0,native_calls=0,held=False,smc=[],smb_reads=0)
  def call(name,args=(),terminal=False):
   sp=0x027be000 if case=='cpu-stack' and terminal else 0x027fe000
   uc.mem_write(sp,pack(end,*args));uc.reg_write(x.UC_X86_REG_ESP,sp)
   uc.emu_start(sym[name],end,timeout=45000000,count=150000000)
   assert state['held'] if terminal else uc.reg_read(x.UC_X86_REG_EIP)==end,(case,name,hex(uc.reg_read(x.UC_X86_REG_EIP)))
   return uc.reg_read(x.UC_X86_REG_EAX)
  def cpuid(uc,a,size,user):
   assert uc.reg_read(x.UC_X86_REG_EAX)==1
   for reg,val in [(x.UC_X86_REG_EAX,0),(x.UC_X86_REG_EBX,0),(x.UC_X86_REG_ECX,0),(x.UC_X86_REG_EDX,0 if case=='cpu-features' else 0x1020)]:uc.reg_write(reg,val)
   uc.reg_write(x.UC_X86_REG_EIP,a+size)
  for a in ins('cpuid'):uc.hook_add(u.UC_HOOK_CODE,cpuid,None,a,a)
  def msr(uc,a,size,user):
   index=uc.reg_read(x.UC_X86_REG_ECX)
   pairs=[(6,0),(0xf8000800,15),(0xf0000001,0),(0xf8000800,15),(0xfff00000,0),(0xfff00800,15)]+[(0,0)]*10
   if index==0xfe:v=(0 if case=='cache-cap' else 8,0)
   elif index==0x2ff:v=(0 if case=='cache-default' else 0x800,0)
   else:
    assert 0x200<=index<0x210;v=pairs[index-0x200]
    if case=='cache-pair' and index==0x208:v=(1,0)
   uc.reg_write(x.UC_X86_REG_EAX,v[0]);uc.reg_write(x.UC_X86_REG_EDX,v[1]);uc.reg_write(x.UC_X86_REG_EIP,a+size)
  for a in ins('rdmsr'):uc.hook_add(u.UC_HOOK_CODE,msr,None,a,a)
  def sync(uc,a,size,user):state['cache_syncs']+=1
  for a in ins('wbinvd'):uc.hook_add(u.UC_HOOK_CODE,sync,None,a,a)
  def native(uc,a,size,user):
   state['native_calls']+=1
   if case=='if-corruption':uc.reg_write(x.UC_X86_REG_EFLAGS,uc.reg_read(x.UC_X86_REG_EFLAGS)|512)
   if case=='packet-corruption':uc.mem_write(sym['Record670']+68+772,b'!')
  uc.hook_add(u.UC_HOOK_CODE,native,None,sym['NativeSend656'],sym['NativeSend656'])
  def admission(uc,a,size,user):
   if case=='dma-corruption':
    address=words(uc,uc.reg_read(x.UC_X86_REG_ESP)+4)[0];uc.mem_write(address+56*4,pack(1))
  uc.hook_add(u.UC_HOOK_CODE,admission,None,sym['admission656'],sym['admission656'])
  def inp(uc,port,size,user):
   if port==0xcfc:
    state['pci_reads']+=1;reg=state.get('pci_address',0)-0x80002000
    if reg==4:
     assert size==2;return 0 if case=='pci-command' else state['pci']
    assert size==4 and reg in [0,16],(case,reg,size)
    return (0 if case=='pci-id' else 0x01c310de) if reg==0 else (0 if case=='pci-bar' else 0xfef00000)
   if port==0x8008:
    assert size==4;state['timer_reads']+=1
    state['tick']=(state['tick']+(-1 if case=='timer-backwards' else 0 if case=='timer-frozen' else 5000))&0xffffffff
    return state['tick']
   assert port==0xc000 and size in [1,2],(case,port,size)
   state['smb_reads']+=1
   return 0x800 if case=='smc-busy' else 0x26 if case=='smc-error' else 0 if case=='smc-timeout' else 0x10
  def output(uc,port,size,value,user):
   if port==0xcf8:
    assert size==4 and value in [0x80002000,0x80002004,0x80002010];state['pci_address']=value;return
   if port==0xcfc:
    assert size==2 and state['pci_address']==0x80002004 and value in [3,7]
    state['pci_writes'].append(value)
    if not(case=='cleanup-command' and len(state['pci_writes'])==3):state['pci']=value
    return
   assert port in [0xc004,0xc008,0xc006,0xc000,0xc002];state['smc'].append([port,size,value])
  uc.hook_add(u.UC_HOOK_INSN,inp,None,1,0,x.UC_X86_INS_IN);uc.hook_add(u.UC_HOOK_INSN,output,None,1,0,x.UC_X86_INS_OUT)
  def read(uc,access,address,size,value,user):
   reg=address-0xfef00000;assert size==4 and not reg%4 and reg<0x270;state['mmio_reads']+=1
   v=state['regs'].get(reg,0)
   if reg==0x130:v=0 if case=='setup-stuck' else 0x80000000
   if reg==0x190 and case=='mii-stuck':v=0x10000
   if reg in [0x88,0x98] and case=='stop-stuck':v=1
   uc.mem_write(address,pack(v))
  def write(uc,access,address,size,v,user):
   reg=address-0xfef00000;assert size==4 and not reg%4 and reg<0x270;state['mmio_writes']+=1
   if reg in [0,0x180]:state['regs'][reg]=state['regs'].get(reg,0)&~v
   else:state['regs'][reg]=v
   if reg==0x190 and v&0x10000:
    phy=(v>>5)&31;nr=v&31;state['regs'][0x190]=0;result=0xffff
    if phy==1 and case!='no-phy':result={2:0x1234,3:0x5678,1:0 if case=='no-link' else 0x24,4:0x1e0,5:0x1e0}.get(nr,0xffff)
    state['regs'][0x194]=result
   if reg==0x84 and v==1 and case=='descriptor-owned':uc.mem_write(sym['Dma656']+6,struct.pack('<H',0x8000))
   if reg==0x144 and v==1:
    dma=sym['Dma656'];index=len(state['frames'])%2
    assert state['pci']&4 and state['regs'][0x84]==1
    assert state['regs'][0x100]==dma and state['regs'][0x104]==dma+32
    address,length,flags=struct.unpack('<IHH',uc.mem_read(dma+index*8,8))
    assert address==dma+64+index*1536 and length==813 and flags==0x8001
    frame=bytes(uc.mem_read(address,814));assert frame[42:]==(expected if case!='packet-corruption' else b'!'+expected[1:])
    assert csum(frame[14:34])==65535 and csum(frame[26:34]+b'\0\x11'+struct.pack('>H',780)+frame[34:])==65535
    assert frame[:6]==b'\xff'*6 and frame[6:12]==bytes([2,0,0,0,0,1])
    state['frames'].append(sha(frame))
    if case=='irq-error':state['regs'][0]=state['regs'].get(0,0)|8
    if case!='tx-stuck':uc.mem_write(dma+index*8+6,struct.pack('<H',0x4000 if case=='tx-error' else 1))
  uc.hook_add(u.UC_HOOK_MEM_READ,read,None,0xfef00000,0xfef0026f);uc.hook_add(u.UC_HOOK_MEM_WRITE,write,None,0xfef00000,0xfef0026f)
  def hold(uc,a,size,user):state['held']=True;assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&512;uc.emu_stop()
  uc.hook_add(u.UC_HOOK_CODE,hold,None,halt,halt)
  # Export consumes saved producer RAM; no hardware capture is rerun here.
  uc.mem_write(sym['eeprom']+0x40,bytes([2,0,0,0,0,1]))
  if case=='export-reentry':uc.mem_write(sym['Owner671'],pack(1))
  source_before=bytes(uc.mem_read(datum,704));steps=[]
  def bridge(uc,a,size,user):
   assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&512
   before=words(uc,sym['FreezeBefore671'])[0];after=words(uc,sym['FreezeAfter671'])[0]
   assert after==(before&~512) and bool(before&512)==(case!='success-if-clear')
   assert words(uc,sym['Phase671'])[0]==2;steps.append('bridge')
  def prepare(uc,a,size,user):
   assert steps==['bridge'] and not uc.reg_read(x.UC_X86_REG_EFLAGS)&512
   assert bytes(uc.mem_read(sym['Frozen671'],704))==pack(*data)
   steps.append('prepare')
  uc.hook_add(u.UC_HOOK_CODE,bridge,None,sym['xwn652_bridge'],sym['xwn652_bridge'])
  uc.hook_add(u.UC_HOOK_CODE,prepare,None,sym['prepare670'],sym['prepare670'])
  export_dis=dis.split('<XwnExport657>:',1)[1].split('\n\n',1)[0]
  callsite=re.search(r'^\s*([0-9a-f]+):[^\n]*\tcall[^\n]*<irq_enter669>',export_dis,re.M)
  assert callsite;after_enter=int(callsite[1],16)+5
  def inject(uc,a,size,user):
   if case=='freeze-if-corruption':uc.reg_write(x.UC_X86_REG_EFLAGS,uc.reg_read(x.UC_X86_REG_EFLAGS)|512)
   if case=='freeze-sample-corruption':uc.mem_write(sym['FreezeAfter671'],pack(words(uc,sym['FreezeAfter671'])[0]^1))
  uc.hook_add(u.UC_HOOK_CODE,inject,None,after_enter,after_enter)
  args=[data[0],datum+8,datum+40,datum+76,datum+328,datum+516]
  call('XwnExport657',args,True)
  assert bytes(uc.mem_read(datum,704))==source_before
  record=sym['Record670'];rec=words(uc,record,17);result=words(uc,sym['NativeResult656'],16)
  phase=words(uc,sym['Phase671'])[0];before=words(uc,sym['FreezeBefore671'])[0];after=words(uc,sym['FreezeAfter671'])[0]
  if case in ['export-reentry','freeze-if-corruption','freeze-sample-corruption']:
   assert not steps and not state['native_calls'] and not state['smc'] and rec==tuple([0]*17)
   assert phase==(0 if case=='export-reentry' else 1)
  elif case=='invalid-codec':
   assert steps==['bridge','prepare'] and phase==3 and words(uc,sym['PrepareError671'])[0]==2
   assert not state['native_calls'] and not state['smc'] and rec==tuple([0]*17)
  elif case in ['smc-busy','smc-error','smc-timeout','timer-frozen','timer-backwards']:
   assert steps==['bridge','prepare'] and phase==3 and rec[0]==2
   assert not state['native_calls'] and not state['mmio_reads'] and not state['pci_writes']
   assert not words(uc,sym['Entry672']+20)[0] and words(uc,sym['EntryError672'])[0]
   assert words(uc,sym['Final672'],6)==(0,0,0,0,0,0)
  else:
   assert steps==['bridge','prepare'] and phase==4 and rec[0]==4 and rec[3:6]==(1,1,1)
   assert not rec[6]&512 and rec[7]==rec[6] and not rec[8]&512
   assert bytes(uc.mem_read(record+68,772))==bytes(uc.mem_read(record+840,772))==expected
   assert state['native_calls']==1
   if case in ['cpu-features','cache-default','pci-id']:
    assert rec[1]==4 and rec[11]=={'cpu-features':1,'cache-default':3,'pci-id':4}[case]
    assert not result[0] and not state['mmio_reads'] and not state['pci_writes']
   elif case=='cleanup-command':assert rec[1]==7 and not result[6] and result[2]==3
   else:assert rec[1]==11 and result[4:7]==(3,3,1) and len(state['frames'])==3
  ledvalues=[v for port,width,v in state['smc'] if port==0xc006 and width==2]
  if phase==4:
   assert words(uc,sym['Entry672'],6)==(1,0,4,2,10000,1)
   code=words(uc,sym['Code672'],2)
   expected_code=(1,{'cpu-features':1,'cache-default':3,'pci-id':4}[case]) if case in ['cpu-features','cache-default','pci-id'] else (4,3) if case=='cleanup-command' else (5,0)
   assert code==expected_code
   mask=[0x50,0xa5,0x55,0x5f,0xf5,0x0f,0xf0][code[0]]
   assert ledvalues==[0,1,5,0]+[0,1]+([mask,0]+[0xf0,0]*(code[1]+1))*2+[mask]
   assert words(uc,sym['Final672']+20)[0]==1
  counts=(state['native_calls'],state['pci_reads'],len(state['pci_writes']),state['mmio_reads'],state['mmio_writes'],len(state['smc']),state['timer_reads'])
  frozen=bytes(uc.mem_read(record,1612));state['held']=False;old_steps=list(steps)
  call('XwnExport657',args,True)
  assert steps==old_steps and frozen==bytes(uc.mem_read(record,1612))
  assert counts==(state['native_calls'],state['pci_reads'],len(state['pci_writes']),state['mmio_reads'],state['mmio_writes'],len(state['smc']),state['timer_reads'])
  r['cases'].append(dict(name=case,led_values=ledvalues,marker=list(words(uc,sym['Entry672'],6)),phase=phase,freeze_before=before,freeze_after=after,transport_original_flags=rec[6],transport_flags=rec[7],status=rec[1],admission=rec[11],input_capture_unchanged=True,copy_encode_steps=steps,held=True,repeat_export_no_io=True,frames=state['frames'],result=list(result)));save()
  print(case,'PASS',flush=True)
 r['passed']=True
except BaseException as e:r['failure']=repr(e);r['failed_case']=case;raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
