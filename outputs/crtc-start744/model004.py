"""Actual744 COFF with horizontal transaction, pre-enable recovery and fault injection.
Control-flow and access contracts only; no modeled transition proves hardware behavior.
"""
import datetime,hashlib,json,struct,sys,os,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn744/build001')
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'model004.json';assert not out.exists()
b=(P/'probe.obj').read_bytes()
R={'passed':False,'scope':__doc__,'object_sha256':sha(P/'probe.obj'),'harness_sha256':sha(Path(__file__)),'cases':[]}
GPU=0xfd000000;deadline=time.monotonic()+90

SETUP=[(0x680884,0),(0x680888,0),(0x68088c,0x10001000),(0x680890,0x10000000),(0x680894,0x10000000),(0x680898,0x10000000),(0x68089c,0x10000000),(0x680880,0x21101100),(0x680630,2),(0x68084c,0x00801080),(0x6808c4,0x40801080)]
H=[(0x680820,719),(0x680824,779),(0x680828,719),(0x680834,0),(0x68082c,738),(0x680830,770),(0x680838,719)]
HB=[1279,1649,1279,0,1389,1429,1279]
CS=[(0x14,0),(0x17,0xe3),(0x19,0x10),(0x1b,0x85)]
def run(name,flags=0x246,cpu0=0x80010031,cpu3=0xf000,cpu4=0x610,fault="",baseline=""):
 assert time.monotonic()<deadline
 machine,nsec,_,symptr,nsyms,optsz,_=struct.unpack_from('<HHLLLHH',b);assert machine==0x14c and not optsz
 strings=b[symptr+18*nsyms:];sections=[];symbols={};indices={};i=0
 for j in range(nsec):
  h=struct.unpack_from('<8sLLLLLLHHL',b,20+40*j)
  sections.append({'base':0x100000+j*0x10000,'size':h[3],'raw':h[4],'reloc':h[5],'count':h[7]})
 while i<nsyms:
  symbol_name,value,sec,typ,storage,aux=struct.unpack_from('<8sLhHBB',b,symptr+18*i)
  symbol_name=(strings[struct.unpack('<L',symbol_name[4:])[0]:] if symbol_name[:4]==b'\0'*4 else symbol_name).split(b'\0')[0].decode()
  if sec>0:indices[i]=sections[sec-1]['base']+value;symbols[symbol_name]=indices[i]
  elif symbol_name=='_memcpy':indices[i]=0x300000
  elif symbol_name=='_memset':indices[i]=0x300100
  i+=aux+1
 c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32)
 c.mem_map(0x300000,4096)
 # Harness cdecl memcpy, preserves ESI/EDI. This is not the nxdk libc implementation.
 c.mem_write(0x300000,bytes.fromhex('57568b7c240c8b7424108b4c241489f8fcf3a45e5fc3'))
 c.mem_write(0x300100,bytes.fromhex('578b7c24088b44240c8b4c241089fafcf3aa89d05fc3'))
 for s in sections:
  c.mem_map(s['base'],0x10000)
  if s['size']:c.mem_write(s['base'],b[s['raw']:s['raw']+s['size']])
 for s in sections:
  for j in range(s['count']):
   off,idx,typ=struct.unpack_from('<LLH',b,s['reloc']+j*10);assert idx in indices
   addr=s['base']+off;old=struct.unpack('<L',c.mem_read(addr,4))[0]
   assert typ in (6,20)
   value=old+indices[idx]-(addr+4 if typ==20 else 0)
   c.mem_write(addr,struct.pack('<L',value&0xffffffff))
 c.mem_map(0x200000,0x40000)

 c.mem_write(0x200000,b'G'*0x40000);c.mem_map(GPU,0x1000000)
 c.mem_write(0x208000,struct.pack('<II',0x20ff00,0x201000))
 c.reg_write(x.UC_X86_REG_ESP,0x208000);c.reg_write(x.UC_X86_REG_EFLAGS,flags)
 sels={0x6013d4:0x67,0xc03c4:0x72,0xc03ce:0x91};original=sels.copy()
 mm=dict(SETUP);mm[0x680630]=3;mm.update(dict(zip([a for a,_ in H],HB)));hw={a:0 for a,_ in H};hr=[]
 cr={4:0xa7,5:0x31,0x11:9,0x14:0,0x17:0xe3,0x19:0x51,0x1b:0x85,0x22:0xfe,0x33:0x11,0x1f:0}
 sq=1;gr=0
 if baseline=='c4':cr[4]^=1
 if baseline=='c5':cr[5]^=1
 if baseline=='gr':gr=1
 if baseline=='cr22':cr[0x22]=0xff
 if baseline=='cr33':cr[0x33]=0
 if baseline=='seq':sq=0
 if baseline=='cr11':cr[0x11]=0x89
 if baseline=='mm':mm[0x680884]=1
 if baseline=='cr':cr[0x19]=0
 if baseline=='cr1b':cr[0x1b]=5
 if baseline.startswith('h-'):mm[H[int(baseline[2:])][0]]^=1
 state={'c4writes':0,'sq':sq,'gr':gr,'recovering':False,'unlock':False}
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
    assert idx in [4,0x1f,0x14,0x17,0x19]
    if idx==4:
     state['c4writes']+=1;assert state['c4writes']<=2
     assert value==(93 if state['c4writes']==1 else 0xa7)
     assert state['sq']==0x21 and ports==[5] and not (cr[0x11]&0x80)
     assert word(98)==7 and word(99)==0xffffffff and not hr
     writes.append(['cr',4,value])
     if fault==('c4-write' if state['c4writes']==1 else 'c4-restore-write'):return
     cr[4]=value
     if state['c4writes']==1 and fault=='c5-coupling':cr[5]^=1
     return
    assert value==dict(CS).get(idx) or (idx,value) in [(0x1f,0x57),(0x19,0x51)]
    writes.append(['cr',idx,value])
    if idx==0x1f:state['unlock']=True
    if idx==0x19 and value==0x51:
     state['recovering']=True
     if fault=='cleanup-13':return
    cr[idx]=value;return
   val=cr[idx]
   if idx==4 and state['c4writes']==1 and fault=='c4-read':val^=1
   if idx==4 and state['c4writes']==2 and fault=='c4-restore-read':val^=1
   if idx==5 and state['c4writes']==1 and fault=='c5-read':val^=1
   if idx==5 and state['c4writes']==2 and fault=='c5-restore-read':val^=1
   if fault=='unlock' and state['unlock'] and idx==0x11 and not state['recovering']:val^=1
   if word(1)==0x7448 and not state['recovering'] and idx in dict(CS):
    n=11+[i for i,_ in CS].index(idx)
    if fault=='check-'+str(n):val^=1
    assert word(2)==11 and word(3)==3
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
  elif off in dict(H):
   assert width==4;n=[a for a,_ in H].index(off)
   if kind==u.UC_MEM_WRITE:
    hw[off]+=1;assert hw[off]<=2
    target=H[n][1] if hw[off]==1 else HB[n]
    assert value==target and state['sq']==0x21 and ports==[5]
    writes.append(['h',off,value])
    if hw[off]==2:hr.append(n)
    if fault==('h-write-' if hw[off]==1 else 'h-restore-write-')+str(n):return
    mm[off]=value;return
   val=mm[off]
   if word(1)==0x7449 and word(98)<=6 and not hr and fault=='h-read-'+str(n):val^=1
   if hr and fault=='h-restore-read-'+str(n):val^=1
   # When no horizontal writes occurred, recovery still checks all seven words.
   if not hw[off] and state['unlock'] and word(1)==0x7448 and fault=='h-pre-restore-'+str(n):val^=1
  else:
   assert off in mm and width==4
   if kind==u.UC_MEM_WRITE:
    assert value==dict(SETUP)[off] or (off,value)==(0x680630,3)
    writes.append(['mm',off,value])
    if (off,value)==(0x680630,3):
     state['recovering']=True
     if fault=='cleanup-14':cr[0x1b]^=1
     if fault=='cleanup-8':return
    mm[off]=value;return
   val=mm[off]
   n=[i for i,_ in SETUP].index(off)
   if word(1)==0x7448 and not state['recovering']:
    assert word(2)==11 and word(3)==3
    if fault=='check-'+str(n):val^=1
   if state['recovering'] and fault=='cleanup-'+str(n) and n!=8:val^=1
  if off==0x6013d5 and state['recovering'] and fault in ['cleanup-11','cleanup-12']:
   if sels[0x6013d4]==CS[int(fault.split('-')[1])-11][0]:val^=1
  reads.append([off,sels.get(off-1),val,word(1),bool(state['recovering'])])
  uc.mem_write(addr,val.to_bytes(width,'little'))
 regs=[x.UC_X86_REG_EAX,x.UC_X86_REG_ECX,x.UC_X86_REG_EDX,x.UC_X86_REG_EBX,x.UC_X86_REG_ESP,x.UC_X86_REG_EBP,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI]
 def code(uc,pc,n,_):
  steps[0]+=1
  if n>15:raise AssertionError(('invalid-instruction',hex(pc),n,bytes(uc.mem_read(pc,16)).hex()))
  raw=bytes(uc.mem_read(pc,n));assert raw[:2]!=b'\x0f\x22'
  if raw[:2]==b'\x0f\x20':
   mod=raw[2];assert mod>>6==3;reg=(mod>>3)&7;assert reg in (0,3,4)
   uc.reg_write(regs[mod&7],{0:cpu0,3:cpu3,4:cpu4}[reg]);uc.reg_write(x.UC_X86_REG_EIP,pc+n)
  if not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200:steps[1]+=1
 def ramwrite(uc,kind,addr,size,val,_):
  if GPU<=addr<GPU+0x1000000:return
  assert 0x201000<=addr and addr+size<=0x2011c0 or 0x207000<=addr and addr+size<=0x208008,(hex(addr),size)
 def pout(uc,port,size,val,_):
  assert (port,size)==(0x80d3,1) and val in [4,5]
  assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200
  ports.append(val)
  if val==4:
   assert word(108)==0 and cr[4]==0xa7 and cr[5]==0x31
   assert word(106)==0xa7 and word(111)==0x31
   assert word(100)==0 and word(97) in [0,7]
   assert list(mm[a] for a,_ in H)==HB, 'output enabled with wrong timing'
   assert list(c.mem_read(0x201000+90*4,28))==list(struct.pack('<7I',*HB))
   state['recovering']=True
 def pin(*args):raise AssertionError('Unexpected input port')
 c.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,access,None,GPU,GPU+0xffffff)
 c.hook_add(u.UC_HOOK_MEM_WRITE,ramwrite);c.hook_add(u.UC_HOOK_CODE,code)
 c.hook_add(u.UC_HOOK_INSN,pout,None,1,0,x.UC_X86_INS_OUT)
 c.hook_add(u.UC_HOOK_INSN,pin,None,1,0,x.UC_X86_INS_IN)
 def invalid(uc,access,addr,size,value,_):
  raise AssertionError(('unmapped',hex(uc.reg_read(x.UC_X86_REG_EIP)),hex(addr),size,hex(uc.reg_read(x.UC_X86_REG_ESP))))
 c.hook_add(u.UC_HOOK_MEM_INVALID,invalid)
 try:c.emu_start(symbols['_probe744'],0x20ff00,timeout=2000000,count=15000)
 except Exception as exc:
  raise AssertionError((name,str(exc),hex(c.reg_read(x.UC_X86_REG_EIP)),hex(c.reg_read(x.UC_X86_REG_ESP)),steps,writes[-5:])) from exc
 assert c.reg_read(x.UC_X86_REG_EIP)==0x20ff00 and c.reg_read(x.UC_X86_REG_ESP)==0x208004
 v=list(struct.unpack('<112I',c.mem_read(0x201000,448)))
 assert v[8]==v[10] and not v[9]&0x200 and v[8]&0x200==flags&0x200
 assert v[11:14]==[cpu0,cpu3,cpu4] and c.reg_read(x.UC_X86_REG_EFLAGS)&0x200==flags&0x200
 assert bytes(c.mem_read(0x200000,4096))==b'G'*4096
 assert bytes(c.mem_read(0x2011c0,0x5e40))==b'G'*0x5e40
 assert bytes(c.mem_read(0x208008,0xff8))==b'G'*0xff8 and sels==original
 cpu_bad=(cpu0&0x80000001)!=0x80000001 or cpu4&0x20
 if cpu_bad:
  assert v[0:2]==[0x7441]*2 and not writes and not ports and not reads
 elif baseline:
  assert v[0:2]==[0x7442]*2 and not writes and not ports and v[28]==1
 else:
  hbad=fault.startswith(('h-restore-read-','h-restore-write-'))
  cbad=fault in ['c4-restore-read','c4-restore-write','c5-restore-read','c5-coupling']
  assert ports==([5] if hbad or cbad else [5,4]),(name,ports)
  forward=0x7443 if fault=='blank' else 0x7444 if fault=='unlock' else 0x7448 if fault.startswith('check-') else 0x7449 if fault.startswith(('h-read-','h-write-')) else 0x744b if fault in ['c4-read','c4-write','c5-read','c5-coupling'] else 0x744
  assert v[1]==forward,(name,v)
  fullprefix=forward in [0x744,0x7448,0x7449,0x744b]
  if fullprefix:
   assert v[2:4]==[11,3]
   fail=int(fault.split('-')[1]) if fault.startswith('check-') else None
   assert v[4]==(fail if fail is not None else 0xffffffff) and v[7]==(fail+1 if fail is not None else 15)
   checked=v[42:53]+v[68:72];expected=[b for _,b in SETUP+CS]
   for n,value in enumerate(checked):
    assert value==(0xffffffff if fail is not None and n>fail else expected[n]^(1 if n==fail else 0)),(name,n,value)
   if fail is not None:assert v[5:7]==[expected[fail],expected[fail]^1]
  else:assert v[2:4]==[0,0] and v[7]==0
  horizontal_ran=forward in [0x744,0x7449,0x744b]
  expectedwrites=[['sq',1,0x21]]
  if fault!='blank':expectedwrites+=[['cr',0x1f,0x57]]
  if fullprefix:expectedwrites += [['mm',a,b] for a,b in SETUP]+[['cr',a,b] for a,b in CS[:3]]
  if horizontal_ran:
   expectedwrites += [['h',a,b] for a,b in H]
   if forward!=0x7449:expectedwrites += [['cr',4,93],['cr',4,0xa7]]
   expectedwrites += [['h',H[i][0],HB[i]] for i in range(6,-1,-1)]
   assert v[97]==7 and hr==list(range(6,-1,-1))
   hf=int(fault.rsplit('-',1)[1]) if forward==0x7449 else None
   assert v[98]==(7 if hf is None else hf+1) and v[99]==(0xffffffff if hf is None else hf)
   target=[b for _,b in H];got=v[83:90]
   assert got[:(7 if hf is None else hf)]==target[:(7 if hf is None else hf)]
   if hf is not None:
    assert got[hf]!=target[hf] and v[102:104]==[target[hf],got[hf]]
    assert got[hf+1:]==[0xffffffff]*(6-hf)
  else:
   assert v[97:100]==[0,0,0xffffffff] and v[83:90]==[0xffffffff]*7
  if fullprefix:expectedwrites += [['cr',0x19,0x51],['mm',0x680630,3]]
  if not (hbad or cbad):expectedwrites += [['sq',1,1]]
  assert writes==expectedwrites,(name,writes,expectedwrites)
  mask=(1<<int(fault.split('-')[1])) if fault.startswith('cleanup-') else (1<<15 if hbad or cbad else 0)
  assert v[30]==mask and v[29]==(not mask),(name,v[30],mask)
  hm=1<<int(fault.rsplit('-',1)[1]) if hbad else 0
  assert v[100:102]==[hm,int(not (hbad or cbad))],(name,v[100:102])
  assert v[76:83]==HB
  for n,val in enumerate(v[90:97]):assert (val!=HB[n])==bool(hm&(1<<n))
  assert v[0]==(0x7446 if fault=='selector' else 0x744c if cbad else 0x744a if hbad else 0x7445 if mask else forward)
  assert v[28]==(fault!='selector')
  assert v[104]==0xa7 and v[109]==0x31
  cran=horizontal_ran and forward!=0x7449
  assert v[107]==int(cran) and state['c4writes']==(2 if cran else 0)
  assert v[108]==(1 if fault in ['c4-restore-read','c4-restore-write'] else 2 if fault in ['c5-restore-read','c5-coupling'] else 0)
  assert v[106]==(0xa6 if fault=='c4-restore-read' else 93 if fault=='c4-restore-write' else 0xa7)
  assert v[111]==(0x30 if fault in ['c5-restore-read','c5-coupling'] else 0x31)
  if cran:
   assert v[105]==(92 if fault=='c4-read' else 0xa7 if fault=='c4-write' else 93)
   assert v[110]==(0x30 if fault in ['c5-read','c5-coupling'] else 0x31)
  else:assert v[105]==v[110]==0xffffffff
 R['cases'].append({'name':name,'raw_result':v,'writes':writes,'ports':ports,'reads':reads,'instructions':steps[0],'critical_instructions':steps[1]})
try:
 run('baseline-deferred-read-success')
 for flags in [2,0x202,0x246]:run('flags-'+hex(flags),flags=flags)
 for n in range(15):run('first-mismatch-'+str(n),fault='check-'+str(n))
 for n in range(20):run('cleanup-bit-'+str(n),fault='cleanup-'+str(n))
 for fault in ['blank','unlock','selector']:run(fault,fault=fault)
 for bline in ['gr','cr22','cr33','seq','cr11','mm','cr','cr1b']:run('baseline-refused-'+bline,baseline=bline)
 for value in [0,1,0x40000001,0x80000000]:run('CPU-refused-'+hex(value),cpu0=value)
 run('PAE-refused',cpu4=0x630)
 run('alternate-CR3',cpu3=0x23000)
 for bline in ['c4','c5']:run('crtc-baseline-'+bline,baseline=bline)
 for fault in ['c4-read','c4-write','c4-restore-read','c4-restore-write','c5-read','c5-restore-read','c5-coupling']:run(fault,fault=fault)
 for n in range(7):
  run('horizontal-read-'+str(n),fault='h-read-'+str(n))
  run('horizontal-recovery-read-'+str(n),fault='h-restore-read-'+str(n))
  run('horizontal-baseline-'+str(n),baseline='h-'+str(n))
  if n!=3: # HVALIDSTART is already zero, so dropping that write is unobservable.
   run('horizontal-dropped-write-'+str(n),fault='h-write-'+str(n))
   run('horizontal-dropped-restore-'+str(n),fault='h-restore-write-'+str(n))
 R['passed']=True;R['case_count']=len(R['cases'])
except BaseException as e:R['failure']=repr(e);raise
finally:R['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(R,indent=2)+'\n')
print('PASS actual744 COFF',len(R['cases']),'cases; no physical timing/semantics claim')
