"""Execute only the new tiny IRQ helpers in fresh isolated CPU models."""
import datetime,hashlib,json,re,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('C:/xwn669/host001');out=K/'linked001.json';assert not out.exists()
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((K/'host001.json').read_text());assert b['passed'] and sha(B/'irq.bin')==b['artifacts']['irq.bin']['sha256']
r=dict(passed=False,physical_access=False,source_sha256=sha(Path(__file__)),binary_sha256=sha(B/'irq.bin'),cases=[],scope='Isolated x86 helper instructions; no hardware IRQ delivery, NMI/SMI, or native sender integration.')
try:
 elf='/mnt/c/xwn669/host001/irq.elf';nm=subprocess.check_output(['wsl','-d','Ubuntu','--','nm','-n',elf],text=True,timeout=25)
 sym={a[2]:int(a[0],16) for line in nm.splitlines() if len(a:=line.split())==3}
 dis=(B/'irq-disasm.stdout').read_text();core=(B/'core-disasm.stdout').read_text()
 assert not re.search(r'\b(?:sti|popf\w*|wrmsr|rdmsr|invlpg|wbinvd|in|out)\b|%cr',dis)
 assert dis.count('\tcli')==2 and dis.count('\thlt')==1
 assert 'cmpxchg' in core and not re.search(r'\b(?:sti|cli|popf\w*|wrmsr|invlpg|wbinvd)\b|%cr',core)
 halt=int(re.search(r'^\s*([0-9a-f]+):[^\n]*\thlt',dis,re.M)[1],16)
 for initial in [2,0x202,0x46,0x246,0x8d7,0xad7]:
  uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);uc.mem_map(0x100000,0x10000);uc.mem_write(0x100000,(B/'irq.bin').read_bytes());uc.mem_map(0x200000,0x10000)
  esp=0x208000;end=0x10f000;before=0x201000;after=before+4
  uc.mem_write(esp,struct.pack('<4I',end,0,before,after));uc.reg_write(x.UC_X86_REG_ESP,esp);uc.reg_write(x.UC_X86_REG_EFLAGS,initial)
  incoming=uc.reg_read(x.UC_X86_REG_EFLAGS);uc.reg_write(x.UC_X86_REG_EBX,0x12345678);uc.reg_write(x.UC_X86_REG_ESI,0x87654321)
  uc.emu_start(sym['irq_enter669'],end,timeout=1000000,count=100)
  a,c=struct.unpack('<II',uc.mem_read(before,8));assert a==incoming and c==(incoming&~512) and not(uc.reg_read(x.UC_X86_REG_EFLAGS)&512)
  assert uc.reg_read(x.UC_X86_REG_EAX)==0 and uc.reg_read(x.UC_X86_REG_ESP)==esp+4
  assert uc.reg_read(x.UC_X86_REG_EBX)==0x12345678 and uc.reg_read(x.UC_X86_REG_ESI)==0x87654321
  uc.mem_write(esp,struct.pack('<II',end,0));uc.reg_write(x.UC_X86_REG_ESP,esp);live=uc.reg_read(x.UC_X86_REG_EFLAGS)
  uc.emu_start(sym['irq_flags669'],end,timeout=1000000,count=100);assert uc.reg_read(x.UC_X86_REG_EAX)==live
  uc.reg_write(x.UC_X86_REG_EFLAGS,incoming);stopped=[]
  def stop(uc,a,size,user):stopped.append(a);uc.emu_stop()
  uc.hook_add(u.UC_HOOK_CODE,stop,None,halt,halt);uc.emu_start(sym['irq_hold669'],end,timeout=1000000,count=100)
  assert stopped==[halt] and not(uc.reg_read(x.UC_X86_REG_EFLAGS)&512)
  r['cases'].append(dict(incoming_flags=incoming,saved_original=a,saved_transport=c,return_IF=0,reader_exact=True,terminal_hold_IF=0))
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS',len(r['cases']),'linked IRQ helper cases and core instruction checks')
