"""Execute newly linked32-bit encoder-only code against an independent port oracle.
No actual hardware I/O, GPU model, display initialization or timing proof.
"""
from pathlib import Path
import sys,json,hashlib,struct,re,datetime
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn700/build001')
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
out=K/'cpu001.json';assert not out.exists()
build=json.loads((K/'build001.json').read_text());assert build['passed']
for n,h in build['files'].items():assert hashlib.sha256((P/n).read_bytes()).hexdigest()==h
for n,h in build['sources'].items():assert hashlib.sha256((K/n).read_bytes()).hexdigest()==h
blob=(P/'native.bin').read_bytes()
syms={a[2]:int(a[0],16) for line in (P/'symbols.stdout').read_text().splitlines() if len(a:=line.split())==3}
# Oracle table read separately from frozen681; compare actual little-endian bytes
# with source table's big-endian wire representation, not production swap().
table=[int(v,16) for v in re.findall(r'0x[0-9a-fA-F]+', (W/'outputs/xcal681/xcal_table.h').read_text().split('= {')[1])]
assert len(table)==144
ops=[(True,4,None),(False,4,bytes([0,0,0,15])),(True,0,None),(False,0,bytes(4))]+[(False,i,v.to_bytes(4,'big')) for i,v in enumerate(table)]
pack=lambda *v:struct.pack('<'+'I'*len(v),*v)
request=[3,1,3,8,64<<20,55<<20,9<<20,316160,1]
r={'passed':False,'scope':__doc__,'physical_access':False,'image_sha256':hashlib.sha256(blob).hexdigest(),'cases':[]}
def run(name,fail=None,kind=None,delay=None,clock='normal',bad=None,if_set=False):
 uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);uc.mem_map(0x100000,0x10000);uc.mem_write(0x100000,blob)
 uc.mem_map(0x200000,0x10000);end=0x10ff00;sp=0x208000;rp=0x201000;pp=0x202000
 req=request.copy()
 if bad is not None:req[bad[0]]=bad[1]
 uc.mem_write(rp,pack(*req));uc.mem_write(pp-16,b'\xa5'*100)
 uc.mem_write(sp,pack(end,rp,pp));uc.reg_write(x.UC_X86_REG_ESP,sp);uc.reg_write(x.UC_X86_REG_EFLAGS,0x202 if if_set else 2)
 state={'index':-1,'phase':'entry','fifo':0,'polls':0,'tick_reads':0,'this_delay':0,'ticks':0xffffff00}
 writes=[];reads=0
 def pin(uc,port,width,_):
  nonlocal reads
  reads+=1
  if port==0x8008:
   assert width==4
   di=state['index']-4;first=state['this_delay']==0;state['this_delay']+=1;state['tick_reads']+=1
   if not first:
    step=0 if delay==di and clock=='stall' else -1 if delay==di and clock=='backwards' else 1688
    state['ticks']=(state['ticks']+step)&0xffffffff
   return state['ticks']
  if (port,width)==(0xc000,2):
   phase=state['phase'];i=state['index']
   if phase=='entry':return 8 if fail==i+1 and kind=='entry_busy' else 0
   if phase=='poll':
    state['polls']+=1
    if fail==i:
     if kind=='bus_error':return 0x11
     if kind=='timeout':return 8
    return 0x10
   assert phase=='final'
   state['phase']='entry'
   return 8 if fail==i and kind=='final_busy' else 0
  if (port,width)==(0xc006,2):return 3 if fail==state['index'] and kind=='short' else 4
  if (port,width)==(0xc009,1):
   value=bytes([0x12,0x34,0x56,0x78])[state['fifo']];state['fifo']+=1;return value
  raise AssertionError(('unexpected read',port,width))
 def pout(uc,port,width,value,_):
  assert port in (0xc000,0xc002,0xc004,0xc006,0xc008,0xc009)
  if port==0xc004:
   assert state['phase']=='entry';state['index']+=1;state['fifo']=0;state['polls']=0;state['this_delay']=0
  if port==0xc002:state['phase']='poll';assert value==0x0d and width==1
  if port==0xc000:assert state['phase']=='poll';state['phase']='final'
  writes.append([port,width,value])
 uc.hook_add(u.UC_HOOK_INSN,pin,None,1,0,x.UC_X86_INS_IN);uc.hook_add(u.UC_HOOK_INSN,pout,None,1,0,x.UC_X86_INS_OUT)
 uc.emu_start(syms['native_profile'],end,timeout=15000000,count=20000000)
 assert uc.reg_read(x.UC_X86_REG_EIP)==end,name
 ret=uc.reg_read(x.UC_X86_REG_EAX);v=list(struct.unpack('<9I',uc.mem_read(pp,36)))
 expected=1001 if if_set else 0 if bad else 0xffffffff if fail is not None or delay is not None else 1
 assert ret==expected,(name,ret,expected)
 assert bool(uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200)==if_set
 assert uc.mem_read(pp-16,16)==b'\xa5'*16 and uc.mem_read(pp+68,16)==b'\xa5'*16
 if if_set or bad:
  assert not writes and reads==0
  assert uc.mem_read(pp,68)==(b'\xa5'*68 if if_set else bytes(68))
 else:
  attempts=fail+1 if fail is not None else delay+5 if delay is not None else 148
  completed=fail if fail is not None else attempts
  tables=max(0,completed-4);delays=tables-1 if delay is not None else tables
  phase=1 if fail is not None and fail<4 else 2 if expected!=1 else 3
  error={'bus_error':5,'entry_busy':2,'final_busy':7,'timeout':4,'short':6}.get(kind,102 if clock=='stall' else 103) if expected!=1 else 0
  assert v[:6]==[attempts,completed,tables,delays,phase,error],(name,v)
  ew=[]
  for i in range(attempts):
   isread,reg,data=ops[i]
   if fail==i and kind=='entry_busy':break
   ew.extend([[0xc004,1,0xe1 if isread else 0xe0],[0xc008,1,reg]])
   if not isread:ew.extend([[0xc009,1,b] for b in data]+[[0xc006,2,4]])
   ew.append([0xc002,1,0x0d])
   if fail==i and kind=='timeout':break
   ew.append([0xc000,2,0x11 if fail==i and kind=='bus_error' else 0x10])
  assert writes==ew,(name,'write trace mismatch')
  assert v[6:8]==[ops[attempts-1][1],int(ops[attempts-1][0])]
  if fail is None:assert v[8]==0x78563412
  if delay is not None:
   obs=struct.unpack('<4I',uc.mem_read(pp+52,16))
   assert obs[3]==(100001 if clock=='stall' else 2)
 r['cases'].append({'name':name,'return':ret,'progress':v,'reads':reads,'writes':len(writes),'write_sha256':hashlib.sha256(json.dumps(writes).encode()).hexdigest(),'expected_write_trace_equal':True,'guard_bytes_unchanged':True,'IF_unchanged':True})
try:
 run('complete_sequence_with_timer_wrap')
 run('IF_refused',if_set=True)
 for i,v in enumerate([0,0,1,0,128<<20,54<<20,8<<20,0,0]):run('bad_request_'+str(i),bad=(i,v))
 for kind in ('bus_error','entry_busy','final_busy'):
  for i in range(148):run(kind+'_'+str(i),fail=i,kind=kind)
 for i in range(144):run('delay_backwards_'+str(i),delay=i,clock='backwards')
 for i in [0,1,2,3,4,147]:run('timeout_'+str(i),fail=i,kind='timeout')
 for i in [0,2]:run('short_'+str(i),fail=i,kind='short')
 run('delay_stalled',delay=0,clock='stall')
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS',len(r['cases']),'linked encoder-only modeled cases; no GPU or hardware proof')
