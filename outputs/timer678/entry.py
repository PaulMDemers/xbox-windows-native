"""Fresh full-image function fixtures; explicit synthetic timer/SMC, no hardware."""
import datetime,hashlib,json,re,struct,sys,zlib
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('C:/xwn678/build001')
out=K/'entry001.json';assert not out.exists()
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
sha=lambda b:hashlib.sha256(b).hexdigest()
build=json.loads((K/'build001.json').read_text());blob=(B/'image-crom.bin').read_bytes()
assert build['passed'] and sha(blob)==build['artifacts']['image-crom.bin']['sha256']
sym={v[2]:int(v[0],16) for line in (B/'symbols.stdout').read_text().splitlines() if len(v:=line.split())==3}
dis=(B/'disassembly.stdout').read_text();ed=dis.split('<XwnExport657>:',1)[1].split('\n\n',1)[0]
after_enter=int(re.search(r'^\s*([0-9a-f]+):[^\n]*\tcall[^\n]*<irq_enter669>',ed,re.M)[1],16)+5
pack=lambda *v:struct.pack('<'+'I'*len(v),*v)
words=lambda uc,a,n=1:struct.unpack('<'+'I'*n,uc.mem_read(a,n*4))
r=dict(passed=False,physical_access=False,firmware_execution='isolated functions, not boot',source_sha256=sha(Path(__file__).read_bytes()),binary_sha256=sha(blob),cases=[])
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 cases=['advance','if-clear','display-failure','unsupported','slow','frozen','backward','jump','wrap32','hypothetical-wrap24','if-after-entry','if-after-timer','export-reentry','freeze-if-corruption','freeze-sample-corruption','invalid-codec']
 cases += [f'smc-{t}-{m}' for t in [1,2,3] for m in ['busy','pending','error']]
 for case in cases:
  uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);uc.mem_map(0x02600000,0x200000);uc.mem_write(0x02600000,blob)
  uc.mem_map(0xa0000,0x1000);uc.mem_write(0xa0000,bytes(16)+pack(0xffff,0xcf9a00,0xffff,0xcf9200,0xffff,0xcf9200))
  uc.reg_write(x.UC_X86_REG_GDTR,(0,0xa0000,39,0));uc.reg_write(x.UC_X86_REG_CR0,1)
  for reg,val in [(x.UC_X86_REG_CS,0x10),(x.UC_X86_REG_DS,0x18),(x.UC_X86_REG_ES,0x18),(x.UC_X86_REG_SS,0x18)]:uc.reg_write(reg,val)
  uc.reg_write(x.UC_X86_REG_EFLAGS,2 if case=='if-clear' else 0x202)
  identity=bytes(uc.mem_read(sym['Identity657'],48))
  data=[0xffffffff if case=='display-failure' else 0 if case=='unsupported' else 1,2 if case=='display-failure' else 1]+[0x13570000+i for i in range(174)]
  data[86]=data[87]=data[133]=data[134]=0x202
  expected=b'XWN655U1'+pack(1,772)+identity+pack(*data);expected+=pack(zlib.crc32(expected));assert len(expected)==772
  datum=0x027e0100;end=0x027ef000;uc.mem_write(datum,pack(*data))
  if case=='invalid-codec':uc.mem_write(sym['Identity657'],bytes(48))
  if case=='export-reentry':uc.mem_write(sym['Owner671'],pack(1))
  failtx,mode=(int(case.split('-')[1]),case.split('-')[2]) if case.startswith('smc-') else (0,'none')
  tick=0xffffff00 if case=='wrap32' else 0x00ffff00 if case=='hypothetical-wrap24' else 100000 if case=='backward' else 0
  step=0 if case=='frozen' else -1 if case=='backward' else 3579546 if case=='jump' else 1 if case=='slow' else 100
  mask=0xffffff if case=='hypothetical-wrap24' else 0xffffffff
  state=dict(reads=0,ports=0,tx=0,pending_reg=0,pending_value=0,commands=[],flags_calls=0,held=False,first=[],last=0,steps=[])
  def inp(uc,port,width,user):
   global tick
   state['ports']+=1
   if port==0x8008:
    assert width==4;tick=(tick+step)&mask;state['reads']+=1;state['last']=tick
    if len(state['first'])<64:state['first'].append(tick)
    return tick
   assert port==0xc000 and width in [1,2]
   if width==2 and state['tx']+1==failtx and mode=='busy':return 0x800
   if width==1 and state['tx']==failtx:return 0 if mode=='pending' else 0x26 if mode=='error' else 0x10
   return 0x10
  def output(uc,port,width,value,user):
   state['ports']+=1
   if port==0xc008:assert width==1;state['pending_reg']=value
   elif port==0xc006:assert width==2;state['pending_value']=value
   elif port==0xc002:
    assert width==1 and value==0x1a;state['tx']+=1;state['commands'].append([state['pending_reg'],state['pending_value']])
   else:assert port==0xc004 and width==1 and value==0x20 or port==0xc000 and width==2
  def flags(uc,a,size,user):
   state['flags_calls']+=1
   if case=='if-after-entry' and state['flags_calls']==2 or case=='if-after-timer' and state['flags_calls']==3:uc.reg_write(x.UC_X86_REG_EFLAGS,uc.reg_read(x.UC_X86_REG_EFLAGS)|512)
  def forbidden(*args):raise AssertionError('unexpected sender/old indication/transport call')
  def hold(uc,a,size,user):
   assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&512;state['held']=True;uc.emu_stop()
  def bridge(uc,a,size,user):
   before=words(uc,sym['FreezeBefore671'])[0];after=words(uc,sym['FreezeAfter671'])[0]
   assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&512 and after==(before&~512) and bool(before&512)==(case!='if-clear')
   assert words(uc,sym['Phase671'])[0]==2;state['steps'].append('bridge')
  def prepare(uc,a,size,user):
   assert state['steps']==['bridge'] and not uc.reg_read(x.UC_X86_REG_EFLAGS)&512
   assert bytes(uc.mem_read(sym['Frozen671'],704))==pack(*data);state['steps'].append('prepare')
  def terminal(uc,a,size,user):
   assert state['steps']==['bridge','prepare'] and words(uc,sym['Phase671'])[0]==4;state['steps'].append('probe')
  def inject(uc,a,size,user):
   if case=='freeze-if-corruption':uc.reg_write(x.UC_X86_REG_EFLAGS,uc.reg_read(x.UC_X86_REG_EFLAGS)|512)
   if case=='freeze-sample-corruption':uc.mem_write(sym['FreezeAfter671'],pack(words(uc,sym['FreezeAfter671'])[0]^1))
  uc.hook_add(u.UC_HOOK_INSN,inp,None,1,0,x.UC_X86_INS_IN);uc.hook_add(u.UC_HOOK_INSN,output,None,1,0,x.UC_X86_INS_OUT)
  for name,fn in [('flags',flags),('xwn652_bridge',bridge),('prepare670',prepare),('terminal675',terminal)]:uc.hook_add(u.UC_HOOK_CODE,fn,None,sym[name],sym[name])
  for name in ['NativeSend656','send656','frame656','terminal670','entry672']:uc.hook_add(u.UC_HOOK_CODE,forbidden,None,sym[name],sym[name])
  uc.hook_add(u.UC_HOOK_CODE,hold,None,sym['irq_hold669']+1,sym['irq_hold669']+1)
  uc.hook_add(u.UC_HOOK_CODE,inject,None,after_enter,after_enter)
  def call():
   uc.reg_write(x.UC_X86_REG_ESP,0x027fe000);uc.mem_write(0x027fe000,pack(end,data[0],datum+8,datum+40,datum+76,datum+328,datum+516))
   uc.emu_start(sym['XwnExport657'],end,timeout=45000000,count=100000000);assert state['held']
  call();raw=bytes(uc.mem_read(sym['Record675'],404));v=struct.unpack('<101I',raw);rec=words(uc,sym['Record670'],17)
  assert bytes(uc.mem_read(datum,704))==pack(*data)
  assert v[10]==state['reads'] and v[11]==len(state['first']) and list(v[12:12+v[11]])==state['first'] and v[76]==state['last'] and v[94]==state['reads'] and v[85]==0
  assert all(c!=[8,0] for c in state['commands'])
  early=case in ['export-reentry','freeze-if-corruption','freeze-sample-corruption','invalid-codec']
  if early:
   assert raw==bytes(404) and rec==tuple([0]*17) and state['ports']==0
   assert state['steps']==(['bridge','prepare'] if case=='invalid-codec' else [])
   assert words(uc,sym['Phase671'])[0]==(3 if case=='invalid-codec' else 0 if case=='export-reentry' else 1)
  else:
   assert state['steps']==['bridge','prepare','probe'] and rec[0]==2 and rec[3:6]==(0,0,0)
   assert bytes(uc.mem_read(sym['Record670']+68,772))==bytes(uc.mem_read(sym['Record670']+840,772))==expected
   assert bytes(uc.mem_read(sym['Frozen671'],704))==pack(*data)
   if case.startswith('if-after'):
    assert v[1]==3 and not v[4] and state['tx']==2 and state['reads']==(37 if case=='if-after-timer' else 0)
   elif failtx:
    assert v[1]==(5 if failtx==3 else 4) and not v[4] and v[79]==(0 if mode=='error' else 1)
    assert state['tx']==(failtx-1 if mode=='busy' else failtx) and state['reads']==(37 if failtx==3 else 0)
   else:
    err=4 if case in ['frozen','backward','jump','hypothetical-wrap24'] else 0
    assert v[0]==5 and v[1]==0 and v[4]==1 and v[9]==err and not v[79]
    assert state['commands']==[[8,0x5f],[7,1],[8,0xa5 if err else 0x0f]]
    assert state['reads']=={'slow':3581,'frozen':200001,'backward':2,'jump':2,'hypothetical-wrap24':3}.get(case,37)
  saved=[bytes(uc.mem_read(sym[n],s)) for n,s in [('Record675',404),('Record670',1612),('Frozen671',704)]]
  counts=(state['ports'],state['reads'],list(state['steps']));state['held']=False;call()
  assert saved==[bytes(uc.mem_read(sym[n],s)) for n,s in [('Record675',404),('Record670',1612),('Frozen671',704)]]
  assert counts==(state['ports'],state['reads'],state['steps'])
  r['cases'].append(dict(name=case,error=v[1],timer_error=v[9],samples=v[10],raw_prefix=state['first'],last_sample=v[76],commands=state['commands'],steps=state['steps'],input_unchanged=True,packet_unchanged=not early,held=True,repeat_no_io=True));save();print(case,'PASS',flush=True)
 r['passed']=True
except BaseException as e:r['failure']=repr(e);r['failed_case']=case;raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
