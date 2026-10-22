"""Read exact664 linked allocator instructions; no console or closed runtime execution."""
import datetime,hashlib,json,re,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn664/linked-audit001');P.mkdir()
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
sha=lambda b:hashlib.sha256(b).hexdigest()
b=json.loads((K/'build001.json').read_text());B=Path('C:/xwn664/build001');elf='/mnt/c/xwn664/build001/image-crom.elf'
assert sha((B/'image-crom.elf').read_bytes())==b['artifacts']['image-crom.elf']['sha256']
blob=(B/'image-crom.bin').read_bytes();assert sha(blob)==b['artifacts']['image-crom.bin']['sha256']
out=K/'linked-audit001.json';assert not out.exists()
r=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),passed=False,physical_access=False,source_sha256=sha(Path(__file__).read_bytes()),elf_sha256=b['artifacts']['image-crom.elf']['sha256'],cases=[],scope='Static linked call ordering plus isolated allocator execution. t_malloc/t_free effects modeled; no interrupt delivery or hardware execution.')
try:
 nm=subprocess.check_output(['wsl','-d','Ubuntu','--','nm','-n',elf],text=True,timeout=25)
 sym={a[2]:int(a[0],16) for line in nm.splitlines() if len(a:=line.split())==3}
 dis={}
 for n in ['BootResetAction','BootDetectMemorySize','malloc','free','XwnHdTry720']:
  d=subprocess.check_output(['wsl','-d','Ubuntu','--','objdump','-d','--disassemble='+n,elf],timeout=25);(P/(n+'.txt')).write_bytes(d);dis[n]=d.decode()
 assert dis['BootResetAction'].index('<BootDetectMemorySize>')<dis['BootResetAction'].index('<BootVgaInitializationKernelNG>')<dis['BootResetAction'].index('<BootPciInterruptEnable>')
 assert '<malloc>' in dis['BootDetectMemorySize'] and '<free>' in dis['BootDetectMemorySize']
 assert '<XwnExport657>' in dis['XwnHdTry720']
 r['linked_findings']=['BootResetAction calls memory detection at0x2602e21 before video at0x2602e48; explicit interrupt enable is later at0x2602e9e.','BootDetectMemorySize calls malloc at0x2603c39 and free on its return branches.','malloc contains STI at0x26122d6; valid free contains STI at0x26122fe.','XwnHdTry720 calls noreturn XwnExport657.']
 for fn in ['malloc','free-valid','free-null','free-invalid']:
  for initial in [0,1]:
   uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);uc.mem_map(0x02600000,0x100000);uc.mem_write(0x02600000,blob);uc.mem_map(0x027f0000,0x10000)
   esp=0x027fe000;end=0x026ff000;block=0x026e0000;ptr=block+0x100;calls=[]
   if fn.startswith('free'):
    uc.mem_write(ptr-8,struct.pack('<II',block,0x1234567 if fn=='free-valid' else 0));arg=0 if fn=='free-null' else ptr
   else:arg=512
   uc.mem_write(esp,struct.pack('<II',end,arg));uc.reg_write(x.UC_X86_REG_ESP,esp);uc.reg_write(x.UC_X86_REG_EFLAGS,2|(initial<<9))
   def helper(uc,a,size,user):
    calls.append('t_malloc' if a==sym['t_malloc'] else 't_free')
    sp=uc.reg_read(x.UC_X86_REG_ESP);ret=struct.unpack('<I',uc.mem_read(sp,4))[0]
    uc.reg_write(x.UC_X86_REG_EAX,block if a==sym['t_malloc'] else 0);uc.reg_write(x.UC_X86_REG_ESP,sp+4);uc.reg_write(x.UC_X86_REG_EIP,ret)
   for n in ['t_malloc','t_free']:uc.hook_add(u.UC_HOOK_CODE,helper,None,sym[n],sym[n])
   uc.emu_start(sym['malloc' if fn=='malloc' else 'free'],end,timeout=1000000,count=1000)
   assert uc.reg_read(x.UC_X86_REG_EIP)==end
   actual=(uc.reg_read(x.UC_X86_REG_EFLAGS)>>9)&1;expected=0 if fn=='free-null' else 1;assert actual==expected
   assert calls==(['t_malloc'] if fn=='malloc' else ['t_free'] if fn=='free-valid' else [])
   r['cases'].append(dict(function=fn,incoming_IF=initial,outgoing_IF=actual,modeled_calls=calls))
 r['disassembly_pins']={p.name:sha(p.read_bytes()) for p in P.iterdir()}
 r['source_pins']={n:sha((Path('C:/xwn664/source001')/n).read_bytes()) for n in ['boot/BootResetAction.c','drivers/pci/pci.c','lib/misc/BootLibrary.c']}
 r.update(passed=True,limits='Supports a specific earlier IF-enabling path. Does not prove physical flag history, first writer, survival to inspect, interrupt delivery, or cause of Windows boot/display failures. No patch, state mutation or new launch.')
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS exact linked ordering and',len(r['cases']),'allocator IF cases')
