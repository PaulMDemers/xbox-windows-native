"""Fresh isolated linked guard fixtures, no peripherals or physical access."""
import datetime,hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('C:/xwn672/build001')
out=K/'guards001.json';assert not out.exists()
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((K/'build001.json').read_text());blob=(B/'image-crom.bin').read_bytes()
assert sha(B/'image-crom.bin')==b['artifacts']['image-crom.bin']['sha256']
sym={v[2]:int(v[0],16) for line in (B/'symbols.stdout').read_text().splitlines() if len(v:=line.split())==3}
pack=lambda *v:struct.pack('<'+'I'*len(v),*v)
r=dict(passed=False,physical_access=False,source_sha256=sha(Path(__file__)),binary_sha256=sha(B/'image-crom.bin'),cases=[])
try:
 for case in ['terminal-no-marker','terminal-marker-error','entry-if-set','entry-unprepared','entry-reentry','entry-missing-callback-contract']:
  uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);uc.mem_map(0x02600000,0x200000);uc.mem_write(0x02600000,blob)
  end=0x027ef000;sp=0x027fe000;halt=sym['irq_hold669']+1;state=dict(held=False)
  uc.reg_write(x.UC_X86_REG_EFLAGS,0x202 if case=='entry-if-set' else 2)
  uc.mem_write(sym['Record670'],pack(0 if case=='entry-unprepared' else 2))
  if case=='terminal-marker-error':
   uc.mem_write(sym['Entry672']+20,pack(1));uc.mem_write(sym['EntryError672'],pack(3))
  if case=='entry-reentry':uc.mem_write(sym['Entry672'],pack(1))
  def forbidden(*args):raise AssertionError(case+' touched peripheral or native sender')
  uc.hook_add(u.UC_HOOK_INSN,forbidden,None,1,0,x.UC_X86_INS_IN)
  uc.hook_add(u.UC_HOOK_INSN,forbidden,None,1,0,x.UC_X86_INS_OUT)
  uc.hook_add(u.UC_HOOK_CODE,forbidden,None,sym['NativeSend656'],sym['NativeSend656'])
  def hold(uc,a,size,user):
   assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&512;state['held']=True;uc.emu_stop()
  uc.hook_add(u.UC_HOOK_CODE,hold,None,halt,halt)
  if case=='entry-missing-callback-contract':
   # Direct lower-level API rejects NULL callbacks without claiming or I/O.
   name='marker672';args=(0,sym['Entry672']);expected=5
  else:name='terminal670' if case.startswith('terminal') else 'entry672';args=(0,);expected=6 if case=='entry-reentry' else 5
  uc.mem_write(sp,pack(end,*args));uc.reg_write(x.UC_X86_REG_ESP,sp)
  uc.emu_start(sym[name],end,timeout=1000000,count=100000)
  if name=='terminal670':assert state['held']
  else:assert uc.reg_read(x.UC_X86_REG_EIP)==end and uc.reg_read(x.UC_X86_REG_EAX)==expected
  r['cases'].append(dict(name=case,no_io=True,native_calls=0,held=state['held']))
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS',len(r['cases']),'linked guard fixtures')
