"""Fresh isolated execution of unchanged704 through phase4 only.
Measured731 read-plane values plus explicitly counterfactual CR22 write policies.
The original compiled predicate is unchanged; physical write effects remain unknown.
No old runtime, physical connection, firmware, disk or GPU driver patch.
"""
import datetime,hashlib,json,os,struct,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn732/build002')
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'model002.json';assert not out.exists()
bld=json.loads((K/'build002.json').read_text());assert bld['passed']
for n,h in bld['files'].items():assert sha(P/n)==h
blob=(P/'native.bin').read_bytes()
syms={a[2]:int(a[0],16) for line in (P/'symbols.stdout').read_text().splitlines() if len(a:=line.split())==3}
BASE=0xfd000000;CODE=0x100000;RP=0x201000;OP=0x202000;SP=0x208000;END=0x10ff00
pack=lambda *v:struct.pack('<'+'I'*len(v),*v)
SETUP={0x680884:0,0x680888:0,0x68088c:0x10001000,0x680890:0x10000000,0x680894:0x10000000,0x680898:0x10000000,0x68089c:0x10000000,0x680880:0x21101100,0x680630:2,0x68084c:0x00801080,0x6808c4:0x40801080}
CS={0x14:0,0x17:0xe3,0x19:0x10,0x1b:5,0x22:255,0x33:0x11}
R={'passed':False,'scope':__doc__,'physical_access':False,'image_sha256':sha(P/'native.bin'),'harness_sha256':sha(Path(__file__)),'cases':[]}
evidence=json.loads((K.parent/'latch-select731/audit001.json').read_text())
assert evidence['passed'] and evidence['probe_passed']
MEASURED=evidence['CR22_first']
assert MEASURED==evidence['CR22_direct']==evidence['CR22_reselected']==[0xfe,0xe7,0x5a,0xff]
R['measured_read_evidence']={'path':'outputs/latch-select731/audit001.json','sha256':sha(K.parent/'latch-select731/audit001.json'),'values':MEASURED,'write_effects':'unknown'}
deadline=time.monotonic()+90
def run(name,expected,plane=0,policy="ignored",read33=None,read1b=None,initial33=0x11,drop_mm=None):
 assert time.monotonic()<deadline
 c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(CODE,0x10000);c.mem_write(CODE,blob)
 c.mem_map(0x200000,0x10000);c.mem_map(BASE,0x800000)
 req=[0x4000000,0x3c5c000,3686400,3686400,1,1,1280,720,5120,32,1,1,0x80000,3375000,1]
 c.mem_write(RP,pack(*req));c.mem_write(OP-16,b'G'*256);c.mem_write(SP,pack(END,RP,BASE,0x3c5c000,OP))
 c.reg_write(x.UC_X86_REG_ESP,SP);c.reg_write(x.UC_X86_REG_EFLAGS,2)
 cr={i:0 for i in range(256)};cr.update({9:0x25,0x11:9,0x13:0x80,0x14:0,0x17:0xe3,0x19:0x51,0x1b:0x85,0x21:255,0x22:0xfe,0x25:0x10,0x28:0x83,0x2d:0xe0,0x33:initial33,0x39:255,0x44:0})
 latches=list(MEASURED);initial_latches=latches.copy()
 sq={1:1};gr={4:plane};banks={'cr':cr,'sq':sq,'gr':gr}
 mm={a:0xdeadbeef for a in SETUP};mm.update({0x680508:0x3c20d,0x68050c:0x100a0400,0x680880:0x21101100,0x100200:0x3070003,0x600804:3,0x600800:0x3c5c000,0x680838:1279,0x680818:719,0x680630:3})
 sels={'cr':0x67,'sq':0x72,'gr':0x91};initial=sels.copy();trace=[];writes=[];ports=[];steps=[0]
 indices={0x6013d4:'cr',0xc03c4:'sq',0xc03ce:'gr'};data={o+1:n for o,n in indices.items()}
 phase=lambda:struct.unpack('<I',c.mem_read(OP,4))[0]
 def access(uc,kind,addr,size,val,_):
  off=addr-BASE;ph=phase()
  if off in indices:
   assert size==1
   if kind==u.UC_MEM_WRITE:sels[indices[off]]=val
   else:uc.mem_write(addr,bytes([sels[indices[off]]]))
   return
  if off in data:
   assert size==1;bank=data[off];idx=sels[bank];key=(bank,idx)
   if kind==u.UC_MEM_WRITE:
    assert (bank=='cr' and idx in [0x1f,*CS]) or key==('sq',1),(name,key)
    writes.append([ph,bank,idx,val])
    if bank=='cr' and idx==0x1f:assert val==0x57;return
    if key==('cr',0x22):
     assert policy in ['ignored','selected-latch','all-latches']
     if policy=='selected-latch':latches[gr[4]]=val
     if policy=='all-latches':latches[:]=[val]*4
     return
    if key==('cr',0x33) and read33 is not None:return
    banks[bank][idx]=val;return
   value=latches[gr[4]] if key==('cr',0x22) else banks[bank][idx]
   if ph==4 and bank=='cr':
    if idx==0x33 and read33 is not None:value=read33
    if idx==0x1b and read1b is not None:value=read1b
   trace.append([ph,bank,idx,value]);uc.mem_write(addr,bytes([value]));return
  assert size==4 and off in mm,(name,hex(off),size)
  if kind==u.UC_MEM_WRITE:
   assert ph==4 and off in SETUP and val==SETUP[off];writes.append([ph,'mm',off,val])
   if off!=drop_mm:mm[off]=val
  else:trace.append([ph,'mm',off,mm[off]]);uc.mem_write(addr,pack(mm[off]))
 def pout(uc,port,size,val,_):
  assert (port,size,val)==(0x80d3,1,5);ports.append([phase(),port,size,val])
 def insn(uc,addr,size,_):
  steps[0]+=1
  if phase()==5:uc.emu_stop()
 c.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,access,None,BASE,BASE+0x7fffff)
 c.hook_add(u.UC_HOOK_INSN,pout,None,1,0,x.UC_X86_INS_OUT)
 c.hook_add(u.UC_HOOK_CODE,insn)
 c.emu_start(syms['native_transaction704'],END,timeout=3000000,count=30000)
 v=struct.unpack('<5I',c.mem_read(OP,20));passed=phase()==5
 assert passed==expected,(name,v)
 if passed:assert len(ports)==1
 else:
  assert c.reg_read(x.UC_X86_REG_EIP)==END and v[0:2]==(4,8) and v[2]==1 and v[3]==0
  assert sels==initial and len(ports)==2
 assert c.mem_read(OP-16,16)==b'G'*16 and c.mem_read(OP+160,80)==b'G'*80
 assert c.mem_read(RP,60)==pack(*req) and c.mem_read(CODE,len(blob))==blob
 assert c.reg_read(x.UC_X86_REG_EFLAGS)&0x200==0
 assert gr[4]==plane and not any(w[1]=='gr' for w in writes)
 assert [w[2:] for w in writes if w[1]=='mm']==[[a,v] for a,v in SETUP.items()]
 assert [w[2:] for w in writes if w[1]=='cr']==[[0x1f,0x57]]+[[a,v] for a,v in CS.items()]
 capture=list(struct.unpack('<72I',c.mem_read(syms['setup_trace732'],288)))
 assert capture[0]==0x732 and capture[1]==0 and 1<=capture[2]<=17
 if passed:assert capture[2:4]==[17,0xffffffff]
 else:assert capture[3]==capture[2]-1
 R['cases'].append({'name':name,'phase4_accepted':passed,'stopped_before_geometry':passed,'result_prefix':list(v),'register_data_writes':writes,'reads':trace,'ports':ports,'instructions':steps[0],'failure_selectors_restored':not passed and sels==initial,'capture':capture,'initial_GR04':plane,'final_GR04':gr[4],'CR22_write_policy_counterfactual':policy,'initial_latches':initial_latches,'final_latches':latches.copy()})
try:
 for policy in ['ignored','selected-latch','all-latches']:
  for plane in range(4):
   label=policy+'-plane'+str(plane)
   run(label,policy!='ignored' or plane==3,plane=plane,policy=policy)
   run(label+'-early-CR1b85',False,plane=plane,policy=policy,read1b=0x85)
   run(label+'-early-MMIO',False,plane=plane,policy=policy,drop_mm=0x680884)
   run(label+'-CR33-zero',False,plane=plane,policy=policy,read33=0,initial33=0)
 for r in R['cases']:
  reads=[v for v in r['reads'] if v[0]==4]
  if '-early-' in r['name']:
   assert not any(v[1]=='cr' and v[2] in [0x22,0x33] for v in reads)
  elif r['CR22_write_policy_counterfactual']=='ignored' and r['initial_GR04']!=3:
   assert not any(v[1]=='cr' and v[2]==0x33 for v in reads)
 R['passed']=True;R['case_count']=len(R['cases'])
except BaseException as e:R['failure']=repr(e);raise
finally:
 R['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(R,indent=2)+'\n')
print('PASS',len(R['cases']),'fresh phase4 cases; measured reads, counterfactual writes; no hardware access')
