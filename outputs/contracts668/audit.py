"""Read-only source/linked contract audit with fresh isolated CPU executions.
No physical connection, new XBE, old guest runtime or system-state mutation.
I/O, CPUID and selected external C calls are explicitly modeled below.
"""
import datetime,hashlib,json,re,struct,subprocess,sys,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];S=Path('C:/xwn667/source001');B=Path('C:/xwn667/build001');P=Path('C:/xwn668/audit001')
out=K/'audit001.json';assert not out.exists() and not P.exists()
assert shutil.disk_usage('C:/').free-32*1024**2>20*1024**3
P.mkdir(parents=True);sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
sha=lambda b:hashlib.sha256(b).hexdigest()
build=json.loads((W/'outputs/memory667/build001.json').read_text());blob=(B/'image-crom.bin').read_bytes()
assert sha(blob)==build['artifacts']['image-crom.bin']['sha256']
r=dict(passed=False,physical_access=False,source_sha256=sha(Path(__file__).read_bytes()),image_sha256=sha(blob),source_tree=build['tree'],static_checks=[],handler_cases=[],sender_cases=[],scope='Fresh isolated linked-function executions; not a boot or interrupt-delivery simulation. No closed runtime reopened.')
def save():out.write_text(json.dumps(r,indent=2)+'\n')
def check(name,value):assert value,name;r['static_checks'].append(name)
def words(uc,address,count=1):return struct.unpack('<'+'I'*count,uc.mem_read(address,count*4))
save()
try:
 elf='/mnt/c/xwn667/build001/image-crom.elf'
 check('ELF pin',sha((B/'image-crom.elf').read_bytes())==build['artifacts']['image-crom.elf']['sha256'])
 nm=subprocess.check_output(['wsl','-d','Ubuntu','--','nm','-n',elf],text=True,timeout=25)
 sym={a[2]:int(a[0],16) for line in nm.splitlines() if len(a:=line.split())==3}
 names=['BootResetAction','BootInterruptsWriteIdt','intel_interrupts_on','BootPciPeripheralInitialization','BootDetectMemorySize','malloc','free','NativeSend656','IntHandlerCTimer0','IntHandler3VsyncC','IntHandler4C','IntHandlerCSmc','XwnHdTry720']
 dis={}
 for n in names:
  dis[n]=subprocess.check_output(['wsl','-d','Ubuntu','--','objdump','-d','--disassemble='+n,elf],text=True,timeout=25)
  (P/(n+'.txt')).write_text(dis[n])
 apic=dis['intel_interrupts_on']
 check('misleading name: APIC MSR read/write, no STI', '\trdmsr' in apic and '\twrmsr' in apic and not re.search(r'\b(?:sti|cli|popf\w*)\b',apic))
 check('IDT setup calls APIC helper', '<intel_interrupts_on>' in dis['BootInterruptsWriteIdt'])
 check('PCI setup executes CLI','\tcli' in dis['BootPciPeripheralInitialization'])
 reset=dis['BootResetAction']
 order=['BootInterruptsWriteIdt','BootPciPeripheralInitialization','BootAGPBUSInitialization','cache_disable','display_cpuid_update_microcode','cache_enable','XwnMemoryBoundary667','BootEepromReadEntireEEPROM','BootVgaInitializationKernelNG','BootPciInterruptEnable']
 check('linked reset order', [reset.index('<'+n+'>') for n in order]==sorted(reset.index('<'+n+'>') for n in order))
 check('memory detection calls allocation and release','<malloc>' in dis['BootDetectMemorySize'] and '<free>' in dis['BootDetectMemorySize'])
 check('allocator contains unconditional CLI/STI',all('\tcli' in dis[n] and '\tsti' in dis[n] for n in ['malloc','free']))
 check('diagnostic export before ordinary continuation','<XwnExport657>' in dis['XwnHdTry720'])
 sources=['boot/BootResetAction.c','boot/BootStartup.S','drivers/pci/BootInterrupts.c','drivers/pci/pci.c','drivers/cpu/cputools.c','lib/misc/BootLibrary.c','drivers/diag656/native.c','drivers/diag656/admission.c','drivers/diag656/nic.c','drivers/video/xwn_hd_native.c','drivers/video/BootVgaInitialization.c']
 r['source_pins']={n:sha((S/n).read_bytes()) for n in sources}
 source=(S/'drivers/pci/BootInterrupts.c').read_text()
 check('PIC master mask zero and Xromwell slave af','IoOutputByte(0x21, 0x00)' in source and 'IoOutputByte(0xa1, 0xaf)' in source)
 check('C handlers software guard is not CPU IF','if(!nInteruptable) return;' in source)
 r['allocation_call_inventory']=[]
 for folder in ['boot','drivers/pci','drivers/cpu','drivers/video','drivers/diag656','drivers/diag657']:
  for p in (S/folder).rglob('*.c'):
   for line,text in enumerate(p.read_text().splitlines(),1):
    if re.search(r'\b(?:malloc|free)\s*\(',text):r['allocation_call_inventory'].append(dict(path=p.relative_to(S).as_posix(),line=line,text=text.strip()))
 def fresh(args=(),flags=2):
  uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);uc.mem_map(0x02600000,0x100000);uc.mem_write(0x02600000,blob);uc.mem_map(0x027f0000,0x10000)
  esp=0x027fe000;end=0x026ff000;uc.mem_write(esp,struct.pack('<'+'I'*(1+len(args)),end,*args));uc.reg_write(x.UC_X86_REG_ESP,esp);uc.reg_write(x.UC_X86_REG_EFLAGS,flags)
  return uc,end
 for flag in [0,1]:
  for kind in ['timer','vsync','guarded4','smc-none','smc-av','smc-power']:
   uc,end=fresh();uc.mem_write(sym['nInteruptable'],struct.pack('<I',flag));uc.mem_map(0xfd600000,4096)
   uc.mem_write(sym['VIDEO_AV_MODE'],b'\xff');calls=[];ports=[];ticks=[0]
   fn={'timer':'IntHandlerCTimer0','vsync':'IntHandler3VsyncC','guarded4':'IntHandler4C'}.get(kind,'IntHandlerCSmc')
   reason={'smc-none':0,'smc-av':8,'smc-power':1}.get(kind,0)
   def inp(uc,port,size,user):assert port==0x8000 and size==2;ports.append(['in',port,size,0]);return 0
   def output(uc,port,size,value,user):raise AssertionError(('unexpected direct port write',port,size,value))
   def external(uc,address,size,user):
    name=next(n for n in external_names if sym[n]==address);sp=uc.reg_read(x.UC_X86_REG_ESP);ret=words(uc,sp)[0];value=0
    arg_count=2 if name.startswith('I2C') else 1 if name in ['BootVgaInitializationKernelNG','bprintf'] else 0
    args=list(words(uc,sp+4,arg_count));calls.append(dict(name=name,args=args))
    if name=='I2CTransmitByteGetReturn':
     assert args[0]==0x10 and args[1] in [0x11,4];value=reason if args[1]==0x11 else 1
    if name=='GetTimerTicks':ticks[0]+=1000000;value=ticks[0]
    uc.reg_write(x.UC_X86_REG_EAX,value);uc.reg_write(x.UC_X86_REG_ESP,sp+4);uc.reg_write(x.UC_X86_REG_EIP,ret)
   external_names=['I2CTransmitByteGetReturn','I2CTransmitWord','BootVgaInitializationKernelNG','GetTimerTicks','bprintf']
   for n in external_names:uc.hook_add(u.UC_HOOK_CODE,external,None,sym[n],sym[n])
   uc.hook_add(u.UC_HOOK_INSN,inp,None,1,0,x.UC_X86_INS_IN);uc.hook_add(u.UC_HOOK_INSN,output,None,1,0,x.UC_X86_INS_OUT)
   uc.emu_start(sym[fn],end,timeout=1000000,count=10000);assert uc.reg_read(x.UC_X86_REG_EIP)==end
   c=[v['name'] for v in calls]
   if kind=='timer':assert words(uc,sym['BIOS_TICK_COUNT'])[0]==1 and not c
   if kind=='vsync':assert words(uc,0xfd600100)[0]==1 and not c
   if kind=='guarded4':assert c==(['bprintf'] if flag else [])
   if kind.startswith('smc-'):assert c.count('I2CTransmitByteGetReturn')==(2 if kind=='smc-av' else 1) and words(uc,sym['nCountInterruptsSmc'])[0]==1
   if kind=='smc-av':assert c.count('BootVgaInitializationKernelNG')==2 and c.count('GetTimerTicks')==4
   if kind=='smc-power':assert [v['args'][1] for v in calls if v['name']=='I2CTransmitWord']==[0x200,0x104,0x504,0x604,0x904,0xa04,0xb04,0xd04,0xe04,0xf04,0x1004,0x1204,0x1304,0x1404,0x1504,0x1604,0x1704,0x1804]
   r['handler_cases'].append(dict(handler=fn,kind=kind,nInteruptable=flag,returned=True,modeled_calls=calls,modeled_ports=ports,vsync_model_value=words(uc,0xfd600100)[0]));save()
 native=dis['NativeSend656']
 cpuid=int(re.search(r'^\s*([0-9a-f]+):[^\n]*\tcpuid',native,re.M)[1],16)
 sgdt=int(re.search(r'^\s*([0-9a-f]+):[^\n]*\tsgdt',native,re.M)[1],16)
 for label,ifbit,features,cr0 in [('if-set',1,0x1020,1),('if-set-no-features',1,0,1),('if-clear',0,0x1020,1),('if-clear-no-features',0,0,1),('if-clear-bad-cr0',0,0x1020,0x40000001)]:
  uc,end=fresh([0x026f0000,772,0x026f0400,0x026f0500,50657],2|(ifbit<<9));uc.reg_write(x.UC_X86_REG_CR0,cr0);uc.mem_write(sym['xbox_ram'],struct.pack('<I',64));reached=[];hw=[]
  def cpu(uc,a,size,user):
   assert uc.reg_read(x.UC_X86_REG_EAX)==1;uc.reg_write(x.UC_X86_REG_EAX,0);uc.reg_write(x.UC_X86_REG_EBX,0);uc.reg_write(x.UC_X86_REG_ECX,0);uc.reg_write(x.UC_X86_REG_EDX,features);uc.reg_write(x.UC_X86_REG_EIP,a+2)
  def later(uc,a,size,user):reached.append('sgdt');uc.emu_stop()
  def forbidden(uc,a,size,user):raise AssertionError(('native reached forbidden callback',hex(a)))
  def badin(uc,port,size,user):hw.append(port);raise AssertionError('native IN')
  def badout(uc,port,size,value,user):hw.append(port);raise AssertionError('native OUT')
  uc.hook_add(u.UC_HOOK_CODE,cpu,None,cpuid,cpuid);uc.hook_add(u.UC_HOOK_CODE,later,None,sgdt,sgdt)
  for n in ['PciReadDword','PciReadWord','PciWriteWord','send656']:uc.hook_add(u.UC_HOOK_CODE,forbidden,None,sym[n],sym[n])
  uc.hook_add(u.UC_HOOK_INSN,badin,None,1,0,x.UC_X86_INS_IN);uc.hook_add(u.UC_HOOK_INSN,badout,None,1,0,x.UC_X86_INS_OUT)
  uc.emu_start(sym['NativeSend656'],end,timeout=1000000,count=10000)
  values=words(uc,sym['NativeAdmission656'],5);assert (values[1]>>9)&1==ifbit and values[3:]==(0x4000000,features)
  assert words(uc,sym['NativeResult656'])[0]==0 and not hw
  if label=='if-clear':assert reached==['sgdt']
  else:assert not reached and uc.reg_read(x.UC_X86_REG_EIP)==end and words(uc,sym['NativeAdmissionError656'])[0]==1 and uc.reg_read(x.UC_X86_REG_EAX)==1
  assert (uc.reg_read(x.UC_X86_REG_EFLAGS)>>9)&1==ifbit
  r['sender_cases'].append(dict(name=label,incoming_IF=ifbit,modeled_cpuid=features,modeled_cr0=cr0,stopped_before_segment_read=bool(reached),admission_error=words(uc,sym['NativeAdmissionError656'])[0],transport_used=0,hardware_io=0,IF_preserved=True));save()
 r['disassembly_pins']={p.name:sha(p.read_bytes()) for p in P.iterdir()}
 r['limits']='Handlers invoked as C functions, not delivered IRQs. Timer, SMC replies, video calls and CPUID modeled. IF-clear native case stops before SGDT and does not qualify later gates. Closed667 source/binary artifacts read only; no physical runtime opened.'
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print('PASS',len(r['static_checks']),'static checks,',len(r['handler_cases']),'handler cases,',len(r['sender_cases']),'native entry cases')
