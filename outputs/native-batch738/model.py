"""Actual738 fresh native ELF with deferred-prefix readback and cleanup fault injection.
Control-flow and access contracts only; no modeled transition proves hardware behavior.
"""
import datetime,hashlib,json,struct,sys,os,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn738/payload001')
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'model001.json';assert not out.exists()
b=(P/'payload.bin').read_bytes()
sy={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}
assert json.loads((K/'payload001.json').read_text())['passed']
R={'passed':False,'scope':__doc__,'ELF_sha256':sha(P/'native.elf'),'harness_sha256':sha(Path(__file__)),'cases':[]}
GPU=0xfd000000;deadline=time.monotonic()+90

SETUP=[(0x680884,0),(0x680888,0),(0x68088c,0x10001000),(0x680890,0x10000000),(0x680894,0x10000000),(0x680898,0x10000000),(0x68089c,0x10000000),(0x680880,0x21101100),(0x680630,2),(0x68084c,0x00801080),(0x6808c4,0x40801080)]
CS=[(0x14,0),(0x17,0xe3),(0x19,0x10),(0x1b,5)]
def run(name,flags=0x46,cpu0=0x4001003b,cpu3=0,cpu4=0x610,fault="",baseline=""):
 assert time.monotonic()<deadline
 c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,b)
 c.mem_map(0x200000,0x40000)

 c.mem_write(0x200000,b'G'*0x40000);c.mem_map(GPU,0x1000000)
 c.mem_write(0x208000,struct.pack('<II',0x20ff00,0x201000))
 c.reg_write(x.UC_X86_REG_ESP,0x208000);c.reg_write(x.UC_X86_REG_EFLAGS,flags)
 sels={0x6013d4:0x67,0xc03c4:0x72,0xc03ce:0x91};original=sels.copy()
 mm=dict(SETUP);mm[0x680630]=3
 cr={0x11:9,0x14:0,0x17:0xe3,0x19:0x51,0x1b:0x85,0x22:0xfe,0x33:0x11,0x1f:0}
 sq=1;gr=0
 if baseline=='gr':gr=1
 if baseline=='cr22':cr[0x22]=0xff
 if baseline=='cr33':cr[0x33]=0
 if baseline=='seq':sq=0
 if baseline=='cr11':cr[0x11]=0x89
 if baseline=='mm':mm[0x680884]=1
 if baseline=='cr':cr[0x19]=0
 state={'sq':sq,'gr':gr,'recovering':False,'unlock':False}
 writes=[];reads=[];ports=[];steps=[0,0]
 word=lambda n:struct.unpack('<I',c.mem_read(0x201000+n*4,4))[0]
 def access(uc,kind,addr,width,value,_):
  off=addr-GPU;assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200
  if off in sels:
   assert width==1
   if kind==u.UC_MEM_WRITE:sels[off]=value;return
   val=sels[off]
   if fault=='selector' and state['recovering'] and val==original[off]:val^=1
  elif off==0x6013d5:
   assert width==1;idx=sels[0x6013d4];assert idx in cr
   if kind==u.UC_MEM_WRITE:
    assert idx in [0x1f,0x14,0x17,0x19,0x1b]
    assert value==dict(CS).get(idx) or (idx,value) in [(0x1f,0x57),(0x19,0x51)]
    writes.append(['cr',idx,value])
    if idx==0x1f:state['unlock']=True
    if idx==0x19 and value==0x51:
     state['recovering']=True
     if fault=='cleanup-13':return
    cr[idx]=value;return
   val=cr[idx]
   if fault=='unlock' and state['unlock'] and idx==0x11 and not state['recovering']:val^=1
   if word(1)==0x7388 and not state['recovering'] and idx in dict(CS):
    n=11+[i for i,_ in CS].index(idx)
    if fault=='check-'+str(n):val^=1
    if fault=='cr1b85' and idx==0x1b:val=0x85
    assert word(2)==11 and word(3)==4
   if state['recovering']:
    bit={0x11:16,0x22:18,0x33:19}.get(idx)
    if bit is not None and fault=='cleanup-'+str(bit):val^=1
  elif off==0xc03c5:
   assert width==1 and sels[0xc03c4]==1
   if kind==u.UC_MEM_WRITE:
    assert value in [1,0x21];writes.append(['sq',1,value])
    if value==0x21 and fault=='blank':return
    if value==1 and fault=='cleanup-15':return
    state['sq']=value;return
   val=state['sq']
  elif off==0xc03cf:
   assert width==1 and kind==u.UC_MEM_READ and sels[0xc03ce]==4
   val=state['gr']^(1 if state['recovering'] and fault=='cleanup-17' else 0)
  else:
   assert off in mm and width==4
   if kind==u.UC_MEM_WRITE:
    assert value==dict(SETUP)[off] or (off,value)==(0x680630,3)
    writes.append(['mm',off,value])
    if (off,value)==(0x680630,3):
     state['recovering']=True
     if fault!='cleanup-14':cr[0x1b]=0x85
     if fault=='cleanup-8':return
    mm[off]=value;return
   val=mm[off]
   n=[i for i,_ in SETUP].index(off)
   if word(1)==0x7388 and not state['recovering']:
    assert word(2)==11 and word(3)==4
    if fault=='check-'+str(n):val^=1
   if state['recovering'] and fault=='cleanup-'+str(n) and n!=8:val^=1
  if off==0x6013d5 and state['recovering'] and fault in ['cleanup-11','cleanup-12']:
   if sels[0x6013d4]==CS[int(fault.split('-')[1])-11][0]:val^=1
  reads.append([off,sels.get(off-1),val,word(1),bool(state['recovering'])])
  uc.mem_write(addr,val.to_bytes(width,'little'))
 regs=[x.UC_X86_REG_EAX,x.UC_X86_REG_ECX,x.UC_X86_REG_EDX,x.UC_X86_REG_EBX,x.UC_X86_REG_ESP,x.UC_X86_REG_EBP,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI]
 def code(uc,pc,n,_):
  steps[0]+=1;raw=bytes(uc.mem_read(pc,n));assert raw[:2]!=b'\x0f\x22'
  if raw[:2]==b'\x0f\x20':
   mod=raw[2];assert mod>>6==3;reg=(mod>>3)&7;assert reg in (0,3,4)
   uc.reg_write(regs[mod&7],{0:cpu0,3:cpu3,4:cpu4}[reg]);uc.reg_write(x.UC_X86_REG_EIP,pc+n)
  if not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200:steps[1]+=1
 def ramwrite(uc,kind,addr,size,val,_):
  if GPU<=addr<GPU+0x1000000:return
  assert 0x201000<=addr and addr+size<=0x201130 or 0x207000<=addr and addr+size<=0x208008,(hex(addr),size)
 def pout(uc,port,size,val,_):
  assert (port,size)==(0x80d3,1) and val in [4,5]
  assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200
  ports.append(val)
  if val==4:state['recovering']=True
 def pin(*args):raise AssertionError('Unexpected input port')
 c.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,access,None,GPU,GPU+0xffffff)
 c.hook_add(u.UC_HOOK_MEM_WRITE,ramwrite);c.hook_add(u.UC_HOOK_CODE,code)
 c.hook_add(u.UC_HOOK_INSN,pout,None,1,0,x.UC_X86_INS_OUT)
 c.hook_add(u.UC_HOOK_INSN,pin,None,1,0,x.UC_X86_INS_IN)
 c.emu_start(sy['probe738'],0x20ff00,timeout=2000000,count=15000)
 assert c.reg_read(x.UC_X86_REG_EIP)==0x20ff00 and c.reg_read(x.UC_X86_REG_ESP)==0x208004
 v=list(struct.unpack('<76I',c.mem_read(0x201000,304)))
 assert v[8]==v[10] and not v[9]&0x200 and v[8]&0x200==flags&0x200
 assert v[11:14]==[cpu0,cpu3,cpu4] and c.reg_read(x.UC_X86_REG_EFLAGS)&0x200==flags&0x200
 assert bytes(c.mem_read(0x200000,4096))==b'G'*4096
 assert bytes(c.mem_read(0x201130,0x5ed0))==b'G'*0x5ed0
 assert bytes(c.mem_read(0x208008,0xff8))==b'G'*0xff8 and sels==original
 cpu_bad=(cpu0&0xe0000001)!=0x40000001 or cpu3!=0 or flags&0x200 or cpu4&0x20
 if cpu_bad:
  assert v[0:2]==[0x7381]*2 and not writes and not ports and not reads
 elif baseline:
  assert v[0:2]==[0x7382]*2 and not writes and not ports and v[28]==1
 else:
  assert ports==[5,4]
  forward=0x7383 if fault=='blank' else 0x7384 if fault=='unlock' else 0x7388 if fault.startswith('check-') or fault=='cr1b85' else 0x738
  assert v[1]==forward,(name,v)
  if forward in [0x738,0x7388]:
   assert v[2:4]==[11,4]
   assert writes==[['sq',1,0x21],['cr',0x1f,0x57]]+[['mm',a,b] for a,b in SETUP]+[['cr',a,b] for a,b in CS]+[['cr',0x19,0x51],['mm',0x680630,3],['sq',1,1]]
   fail=int(fault.split('-')[1]) if fault.startswith('check-') else 14 if fault=='cr1b85' else None
   assert v[4]==(fail if fail is not None else 0xffffffff) and v[7]==(fail+1 if fail is not None else 15)
   checked=v[42:53]+v[68:72];expected=[b for _,b in SETUP+CS]
   for n,value in enumerate(checked):
    assert value==(0xffffffff if fail is not None and n>fail else expected[n]^((0x80 if fault=='cr1b85' else 1) if n==fail else 0)),(name,n,value)
   if fail is not None:assert v[5:7]==[expected[fail],expected[fail]^(0x80 if fault=='cr1b85' else 1)]
  else:assert v[2:4]==[0,0] and v[7]==0
  mask=(1<<int(fault.split('-')[1])) if fault.startswith('cleanup-') else 0
  assert v[30]==mask and v[29]==(not mask),(name,v[30],mask)
  assert v[0]==(0x7386 if fault=='selector' else 0x7385 if mask else forward)
  assert v[28]==(fault!='selector')
 R['cases'].append({'name':name,'raw_result':v,'writes':writes,'ports':ports,'reads':reads,'instructions':steps[0],'critical_instructions':steps[1]})
try:
 run('baseline-deferred-read-success')
 run('CR1b85-before-cleanup',fault='cr1b85')
 for flags in [2,0x202,0x246]:run('flags-'+hex(flags),flags=flags)
 for n in range(15):run('first-mismatch-'+str(n),fault='check-'+str(n))
 for n in range(20):run('cleanup-bit-'+str(n),fault='cleanup-'+str(n))
 for fault in ['blank','unlock','selector']:run(fault,fault=fault)
 for bline in ['gr','cr22','cr33','seq','cr11','mm','cr']:run('baseline-refused-'+bline,baseline=bline)
 for value in [0,1,0x80010031,0x80000000]:run('CPU-refused-'+hex(value),cpu0=value)
 run('PAE-refused',cpu4=0x630)
 run('alternate-CR3',cpu3=0x23000)
 R['passed']=True;R['case_count']=len(R['cases'])
except BaseException as e:R['failure']=repr(e);raise
finally:R['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(R,indent=2)+'\n')
print('PASS actual738 ELF',len(R['cases']),'cases; no physical timing/semantics claim')
