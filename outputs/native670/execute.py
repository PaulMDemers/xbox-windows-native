"""Fresh isolated i386 integration executions. CPU/PCI/NIC/SMC are models.
Actual codec, lifecycle, native inspection, admission, sender and hold execute.
No physical networking, closed runtime, XBE, boot, or DMA/coherency proof.
"""
import datetime,hashlib,json,re,struct,sys,zlib
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('C:/xwn670/host003')
out=K/'execute001.json';assert not out.exists()
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
sha=lambda b:hashlib.sha256(b).hexdigest()
build=json.loads((K/'host003.json').read_text());blob=(B/'integration.bin').read_bytes()
assert build['passed'] and sha(blob)==build['artifacts']['integration.bin']['sha256']
sym={a[2]:int(a[0],16) for line in (B/'symbols.stdout').read_text().splitlines() if len(a:=line.split())==3}
dis=(B/'disassembly.stdout').read_text()
ins=lambda name:[int(m[1],16) for m in re.finditer(r'^\s*([0-9a-f]+):[^\n]*\t'+name+r'\b',dis,re.M)]
assert len(ins('hlt'))==1 and not ins('sti') and not ins('popf') and not ins('wrmsr')
r=dict(passed=False,physical_access=False,new_XBE=False,source_sha256=sha(Path(__file__).read_bytes()),binary_sha256=sha(blob),cases=[])
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
 cases=['success-if-set','success-if-clear','cpu-features','cpu-cr0','cpu-ram','cpu-stack','segment-selector','segment-table','cache-cap','cache-default','cache-pair','pci-id','pci-bar','pci-command','dma-corruption','invalid-config','null-config','sender-used','timer-frozen','timer-backwards','no-phy','no-link','setup-stuck','mii-stuck','tx-stuck','tx-error','irq-error','descriptor-owned','stop-stuck','cleanup-command','smc-busy','smc-error','smc-timeout','packet-corruption','if-corruption','invalid-codec','unprepared','claimed-reentry','held-reentry']
 for case in cases:
  uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32)
  uc.mem_map(0x02600000,0x200000);uc.mem_write(0x02600000,blob);uc.mem_map(0xa0000,0x1000);uc.mem_map(0xfef00000,0x1000)
  uc.mem_write(0xa0000,bytes(16)+pack(0xffff,0xcf9a00,0xffff,0xcf9200,0xffff,0xcf9200))
  uc.reg_write(x.UC_X86_REG_GDTR,(0,0xa0000,39,0));uc.reg_write(x.UC_X86_REG_CR0,1)
  for reg,val in [(x.UC_X86_REG_CS,0x10),(x.UC_X86_REG_DS,0x18),(x.UC_X86_REG_ES,0x18),(x.UC_X86_REG_SS,0x18)]:uc.reg_write(reg,val)
  uc.reg_write(x.UC_X86_REG_EFLAGS,2 if case=='success-if-clear' else 0x202)
  uc.mem_write(sym['xbox_ram'],pack(32 if case=='cpu-ram' else 64))
  ident=0x027e0000;datum=ident+0x100;cfg=ident+0x500;end=0x027ef000
  uc.mem_write(ident,identity);uc.mem_write(datum,pack(*data));uc.mem_write(cfg,bytes([2,0,0,0,0,1,192,0,2,1])+struct.pack('<H',50657))
  if case=='invalid-codec':uc.mem_write(ident,bytes(48))
  if case=='invalid-config':uc.mem_write(cfg,b'\x01')
  state=dict(regs={},pci=7,tick=0,frames=[],pci_reads=0,pci_writes=[],mmio_reads=0,mmio_writes=0,cache_syncs=0,timer_reads=0,native_calls=0,held=False,smc=[],smb_reads=0)
  def call(name,args=(),terminal=False):
   sp=0x027be000 if case=='cpu-stack' and terminal else 0x027fe000
   uc.mem_write(sp,pack(end,*args));uc.reg_write(x.UC_X86_REG_ESP,sp)
   uc.emu_start(sym[name],end,timeout=45000000,count=150000000)
   assert state['held'] if terminal else uc.reg_read(x.UC_X86_REG_EIP)==end,(case,name,hex(uc.reg_read(x.UC_X86_REG_EIP)))
   return uc.reg_read(x.UC_X86_REG_EAX)
  def ret(value):
   sp=uc.reg_read(x.UC_X86_REG_ESP);pc=words(uc,sp)[0];uc.reg_write(x.UC_X86_REG_EAX,value);uc.reg_write(x.UC_X86_REG_ESP,sp+4);uc.reg_write(x.UC_X86_REG_EIP,pc)
  def pci(uc,a,size,user):
   args=words(uc,uc.reg_read(x.UC_X86_REG_ESP)+4,5 if a==sym['PciWriteWord'] else 4)
   assert args[:3]==(0,4,0)
   if a==sym['PciWriteWord']:
    assert args[3]==4 and args[4] in [3,7];state['pci_writes'].append(args[4])
    if not(case=='cleanup-command' and len(state['pci_writes'])==3):state['pci']=args[4]
    ret(0)
   else:
    state['pci_reads']+=1
    if a==sym['PciReadWord']:
     assert args[3]==4;ret(0 if case=='pci-command' else state['pci'])
    elif args[3]==0:ret(0 if case=='pci-id' else 0x01c310de)
    else:assert args[3]==0x10;ret(0 if case=='pci-bar' else 0xfef00000)
  for n in ['PciReadDword','PciReadWord','PciWriteWord']:uc.hook_add(u.UC_HOOK_CODE,pci,None,sym[n],sym[n])
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
   if port==0x8008:
    assert size==4;state['timer_reads']+=1
    state['tick']=(state['tick']+(-1 if case=='timer-backwards' else 0 if case=='timer-frozen' else 5000))&0xffffffff
    return state['tick']
   assert port==0xc000 and size in [1,2],(case,port,size)
   state['smb_reads']+=1
   return 0x800 if case=='smc-busy' else 0x26 if case=='smc-error' else 0 if case=='smc-timeout' else 0x10
  def output(uc,port,size,value,user):
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
  uc.hook_add(u.UC_HOOK_CODE,hold,None,ins('hlt')[0],ins('hlt')[0])
  rc=call('prepare670',[ident,datum]);record=sym['Record670']
  if case=='invalid-codec':assert rc==2 and bytes(uc.mem_read(record,1612))==bytes(1612)
  else:
   assert rc==0 and words(uc,record)[0]==2
   assert bytes(uc.mem_read(record+68,772))==expected and bytes(uc.mem_read(record+840,772))==expected
   prior=bytes(uc.mem_read(record,1612));assert call('prepare670',[ident,datum])==1 and bytes(uc.mem_read(record,1612))==prior
  if case=='cpu-cr0':uc.reg_write(x.UC_X86_REG_CR0,0x40000001)
  if case=='segment-selector':uc.reg_write(x.UC_X86_REG_DS,0x20)
  if case=='segment-table':uc.reg_write(x.UC_X86_REG_GDTR,(0,0xa0000,23,0))
  if case=='sender-used':uc.mem_write(sym['NativeResult656'],pack(1))
  if case in ['unprepared','claimed-reentry','held-reentry']:uc.mem_write(record,pack({'unprepared':0,'claimed-reentry':3,'held-reentry':4}[case]))
  before=bytes(uc.mem_read(record,1612))
  call('terminal670',[0 if case=='null-config' else cfg],True)
  rec=words(uc,record,17);result=words(uc,sym['NativeResult656'],16)
  error=words(uc,sym['NativeAdmissionError656'])[0]
  if case in ['invalid-codec','unprepared','claimed-reentry','held-reentry']:
   assert bytes(uc.mem_read(record,1612))==before and not state['native_calls'] and not state['smc']
  else:
   assert rec[0]==4 and rec[3:6]==(1,1,1) and rec[7]==(rec[6]&~512)
   assert bytes(uc.mem_read(record+68,772))==expected and state['native_calls']==1
   assert rec[11:17]==(error,result[0],result[6],result[5],result[1],result[2])
   if case.startswith('success') or case.startswith('smc-'):assert rec[1]==11 and result[4:7]==(3,3,1) and len(state['frames'])==3
   elif case.startswith('cpu-'):assert rec[1]==4 and error==1 and not result[0]
   elif case.startswith('segment-'):assert rec[1]==4 and error==2 and not result[0]
   elif case.startswith('cache-'):assert rec[1]==4 and error==3 and not result[0]
   elif case.startswith('pci-'):assert rec[1]==4 and error==4 and not result[0]
   elif case=='dma-corruption':assert rec[1]==4 and error==5 and not result[0]
   elif case in ['invalid-config','null-config']:assert rec[1]==5 and not result[0]
   elif case in ['sender-used','stop-stuck','cleanup-command']:assert rec[1]==7 and rec[2]&8 and not result[6]
   elif case=='packet-corruption':assert rec[1]==8 and rec[2]&2
   elif case=='if-corruption':assert rec[1]==9 and rec[2]&4 and not result[0] and not state['smc']
   else:assert rec[1]==6 and result[0] and result[1] and not result[2] and result[6]
   if not result[0]:assert not state['mmio_reads'] and not state['mmio_writes'] and not state['pci_writes']
   if result[6]:assert state['pci']==3 and all(state['regs'].get(a,0)==0 for a in [4,0x84,0x94])
  signal=words(uc,sym['SignalError670'])[0]
  if case.startswith('smc-'):assert signal=={'smc-busy':2,'smc-error':3,'smc-timeout':4}[case]
  elif case not in ['timer-frozen','timer-backwards']:assert signal==0
  r['cases'].append(dict(name=case,status=rec[1],faults=rec[2],admission=error,result=list(result),held=True,IF_at_hold=0,native_calls=state['native_calls'],frames=state['frames'],pci_reads=state['pci_reads'],pci_writes=state['pci_writes'],mmio_reads=state['mmio_reads'],mmio_writes=state['mmio_writes'],timer_reads=state['timer_reads'],cache_syncs=state['cache_syncs'],signal_error=signal,smc_transactions=words(uc,sym['Signal670'])[0]));save()
  print(case,'PASS',flush=True)
 r['passed']=True
except BaseException as e:r['failure']=repr(e);r['failed_case']=case;raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
