"""Construct fresh compiled-COFF model using reviewed loader and independent727 behaviors."""
from pathlib import Path
import textwrap,re
K=Path(__file__).resolve().parent
old=(K.parent/'kernel-prefix723/model.py').read_text()
native=(K.parent/'native-interaction727/integration003.py').read_text()
loader=old[old.index(' machine,nsec'):old.index('\n for base in')]
loader=textwrap.dedent(loader).replace('u=Uc(','c=u.Uc(').replace('UC_ARCH_X86,UC_MODE_32','u.UC_ARCH_X86,u.UC_MODE_32').replace('u.mem_','c.mem_')
loader=re.sub(r'\bname\b','symbol_name',loader)
start=native[native.index(" state={'selector'"):native.index(' def pin(')]
start=start.replace("if fault=='selector' and off==0x6013d4 and value==9", "if fault=='selector' and off==0x6013d4 and value==0x67")
output=native[native.index(' def pout('):native.index(' def ramwrite(')]
output=output[:output.index('  assert port==0xcf8')]+"  raise AssertionError('unexpected port')\n"
checks=native[native.index(" assert state['nmm']=="):native.index(' for lo,hi')]
vectors=native[native.index('  if nmm==2:'):native.index(' expected_image=')]
vectors=textwrap.dedent(vectors)
cases=native[native.index(" for behavior,want"):native.index(' for stage,sel,val')]
script='''"""Actual nxdk728 COFF, bounded independent MMIO fault/behavior models.
Simulated CR reads validate guards; they are not physical kernel context evidence.
"""
import datetime,hashlib,json,struct,sys,os,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn728/build001')
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'model001.json';assert not out.exists()
b=(P/'probe.obj').read_bytes()
R={'passed':False,'scope':__doc__,'object_sha256':sha(P/'probe.obj'),'harness_sha256':sha(Path(__file__)),'cases':[]}
GPU=0xfd000000;deadline=time.monotonic()+120
def run(name,want=0x728,nmm=2,ncr=1,nunlock=1,flags=0x202,cpu0=0x80010031,cpu3=0xf000,cpu4=0x610,behavior='reassert',fault='',cr_bad=None,mm_bad=None,seq=1):
 assert time.monotonic()<deadline
'''+textwrap.indent(loader,' ')+'''
 c.mem_write(0x200000,b'G'*0x40000);c.mem_map(GPU,0x1000000)
 c.mem_write(0x208000,struct.pack('<II',0x20ff00,0x201000))
 c.reg_write(x.UC_X86_REG_ESP,0x208000);c.reg_write(x.UC_X86_REG_EFLAGS,flags)
 FB=0x3000000
'''+start+output+'''
 steps=[0,0]
 regs=[x.UC_X86_REG_EAX,x.UC_X86_REG_ECX,x.UC_X86_REG_EDX,x.UC_X86_REG_EBX,x.UC_X86_REG_ESP,x.UC_X86_REG_EBP,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI]
 def code(uc,pc,n,_):
  steps[0]+=1;raw=bytes(uc.mem_read(pc,n));assert raw[:2]!=b'\\x0f\\x22'
  if raw[:2]==b'\\x0f\\x20':
   mod=raw[2];assert mod>>6==3;reg=(mod>>3)&7;assert reg in (0,3,4)
   uc.reg_write(regs[mod&7],{0:cpu0,3:cpu3,4:cpu4}[reg]);uc.reg_write(x.UC_X86_REG_EIP,pc+n)
  if not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200:steps[1]+=1
 def ramwrite(uc,kind,addr,size,value,_):
  if GPU<=addr<GPU+0x1000000:return
  assert (0x201000<=addr and addr+size<=0x2010d8) or (0x207000<=addr and addr+size<=0x208008),(hex(addr),size)
 c.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,access,None,GPU,GPU+0xffffff)
 c.hook_add(u.UC_HOOK_MEM_WRITE,ramwrite);c.hook_add(u.UC_HOOK_CODE,code)
 c.hook_add(u.UC_HOOK_INSN,pout,None,1,0,x.UC_X86_INS_OUT)
 c.emu_start(symbols['_probe728'],0x20ff00,timeout=2000000,count=15000)
 assert c.reg_read(x.UC_X86_REG_EIP)==0x20ff00 and c.reg_read(x.UC_X86_REG_ESP)==0x208004
 v=list(struct.unpack('<54I',c.mem_read(0x201000,216)))
 assert v[0]==want,(name,hex(v[0]),hex(want))
 assert v[2]==v[4] and not v[3]&0x200 and v[2]&0x200==flags&0x200
 assert v[5:8]==[cpu0,cpu3,cpu4]
 assert c.reg_read(x.UC_X86_REG_EFLAGS)&0x200==flags&0x200
 assert sels==original_sels
 assert bytes(c.mem_read(0x200000,0x1000))==b'G'*0x1000
 assert bytes(c.mem_read(0x2010d8,0x5f28))==b'G'*0x5f28
 assert bytes(c.mem_read(0x208008,0xff8))==b'G'*0xff8
'''+checks+textwrap.indent(vectors,' ')+'''
 R['cases'].append({'name':name,'code':v[0],'raw_result':v,'mmio_writes':mw,'crtc_data_writes':cw,'direct_indexed_order_exact':bool(ncr),'steps':steps[0],'critical_instructions':steps[1]})
try:
 for f in (0x202,0x246,2):run('reassert-flags-'+hex(f),flags=f)
'''+cases+'''
 for cr0 in (0,1,0x40000001,0x80000000):run('cpu0-'+hex(cr0),cpu0=cr0,want=0x7281,nmm=0,ncr=0,nunlock=0)
 run('PAE-refused',cpu4=0x630,want=0x7281,nmm=0,ncr=0,nunlock=0)
 run('other-kernel-CR3',cpu3=0x23000)
 R['passed']=True;R['case_count']=len(R['cases'])
except BaseException as e:R['failure']=repr(e);raise
finally:R['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(R,indent=2)+'\\n')
print('PASS compiled728 cases',len(R['cases']))
'''
script=script.replace('727','728')
(K/'model.py').write_text(script,newline='\n')
