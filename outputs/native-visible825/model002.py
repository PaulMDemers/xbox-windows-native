"""Linked704 instructions with independent indexed-VGA, MMIO and wire oracles.
These are host models, not NV2A timing, ACPI gating or physical display proof.
"""
from pathlib import Path
import sys,os,json,hashlib,struct,random,re,datetime,time
K=Path(__file__).resolve().parent; W=K.parents[1]; P=Path('C:/xwn825/payload008')
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
OUT=K/'model002.json';assert not OUT.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
b=json.loads((K/'payload008.json').read_text());assert b['passed']
for n,h in b['files'].items():assert sha((P/n).read_bytes())==h
for n,h in b['sources'].items():assert sha((K/n).read_bytes())==h
blob=(P/'native.bin').read_bytes()
syms={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}
pack=lambda *v:struct.pack('<'+'I'*len(v),*v)
BASE=0xfd000000;FB=0x03c5c000;ALLOC=3686400;RP=0x201000;OP=0x202000;SP=0x208000;END=0x10ff00
DEFAULT=[0x4000000,0x3c5c000,ALLOC,ALLOC,1,1,1280,720,5120,32,1,1,0x80000,3375000,1]
CONTEXT={0x680508:0x3c20d,0x68050c:0x100a0400,0x680880:0x21101100,0x100200:0x3070003,0x600804:3}
TIMING={0x680800:479,0x680804:524,0x680808:479,0x68080c:489,0x680810:492,
 0x680814:0,0x680818:479,0x680820:719,0x680824:779,0x680828:719,
 0x68082c:738,0x680830:770,0x680834:0,0x680838:719}
SETUP={0x680884:0,0x680888:0,0x68088c:0x10001000,0x680890:0x10000000,
 0x680894:0x10000000,0x680898:0x10000000,0x68089c:0x10000000,
 0x680880:0x21101100,0x680630:2,0x68084c:0x00801080,0x6808c4:0x40801080}
CS={0x14:0,0x17:0xe3,0x19:0x10}
MASKS={0:(255,0x5c),1:(255,0x59),2:(255,0x59),3:(31,0),4:(255,0x5d),
 5:(0x9f,0x9e),6:(255,0x0c),7:(255,0x3e),9:(0x60,0x40),0x10:(255,0xe9),
 0x12:(255,0xdf),0x13:(255,0x68),0x15:(255,0xdf),0x16:(0x7f,0x0c),
 0x17:(255,0xe3),0x18:(255,255),0x19:(255,0x30),0x1a:(255,0x3c),0x25:(255,0x10),
 0x28:(255,0x83),0x2d:(31,0),0x39:(255,255)}
PROTECTED=[0x100,0x140,0x600100,0x600140,0x608000,0x8000,0x680500,0x680504,0x680514]
SEQ=[3,0x21,15,0,6];GR=[0,0,0,0,0,0x40,5,15,255];ATTR=list(range(1,16))+[1,0x4a,15,0,0]
table=[int(v,16) for v in re.findall(r'0x[0-9a-fA-F]+',(W/'outputs/xcal681/xcal_table.h').read_text().split('= {')[1])]
assert len(table)==144
OPS=[(True,4,None),(False,4,bytes([0,0,0,15])),(True,0,None),(False,0,bytes(4))]+[(False,i,v.to_bytes(4,'big')) for i,v in enumerate(table)]
R={'passed':False,'scope':__doc__,'physical_access':False,'image_sha256':sha(blob),
 'harness_sha256':sha(Path(__file__).read_bytes()),'cases':[]}
deadline=time.monotonic()+600

def run(label,expected=1,seed=0,pre=None,drop=None,fault=None,bad=None,flags=2,
        fail_bus=None,bus_kind=None,fail_delay=None,delay_kind=None,fb_fault=False,
        alias_bad=False,enable_drop=False,ext_lock=False,null=None,drop_phase=None,high_alias=False,force_palette_pas=False):
 assert time.monotonic()<deadline,'whole suite deadline'
 c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,blob)
 c.mem_map(0x200000,0x10000);c.mem_map(BASE,0x800000);c.mem_map(FB-4096,ALLOC+8192)
 c.mem_write(FB-4096,b'G'*4096);c.mem_write(FB,b'Z'*(ALLOC+4096))
 req=DEFAULT.copy()
 if bad is not None:req[bad[0]]=bad[1]
 c.mem_write(RP,pack(*req));c.mem_write(OP-16,b'X'*(160+32))
 c.mem_write(SP,pack(END,0 if null=='req' else RP,0 if null=='gpu' else BASE,
                    0 if null=='fb' else FB+0x80000000 if high_alias else FB+4096 if alias_bad else FB,0 if null=='out' else OP))
 c.reg_write(x.UC_X86_REG_ESP,SP);c.reg_write(x.UC_X86_REG_EFLAGS,flags)
 rng=random.Random(seed);cr=bytearray(rng.randrange(256) for _ in range(256))
 cr[0x1a]=0x38;cr[0x1b]=0x85;cr[0x22]=0xfe;cr[0x33]=0x11;cr[9]&=0x7f;cr[0x13]=0x80;cr[0x19]=0x51;cr[0x25]=0;cr[0x28]=0x83;cr[0x39]=255
 cr[0x21]=0xff;cr[0x44]=0;cr[0x11]&=0x7f
 sq=bytearray([0xa5]*256);sq[1]=1;gr=bytearray([0xa5]*256);at=bytearray([0xa5]*32)
 mm={off:0xa5a50000+seed for off in PROTECTED};mm.update({off:0xdeadbeef for off in SETUP|TIMING})
 mm.update(CONTEXT);mm.update({0x600800:req[1],0x680838:1279,0x680818:719})
 banks={'cr':cr,'sq':sq,'gr':gr,'at':at,'mm':mm}
 if pre:banks[pre[0]][pre[1]]=pre[2]
 originals={k:bytes(v) if k!='mm' else dict(v) for k,v in banks.items()}
 sels={'cr':0x67,'sq':0x72,'gr':0x91,'at':0};initial=dict(sels)
 state={'pas':True,'attr_data':bool(seed&1),'index':-1,'bus':'entry','fifo':0,'ticks':0xffffff00,
        'delay':-1,'delay_reads':0,'tick_reads':0,'unlocked':not ext_lock,'geometry_done':False}
 writes=[];ports=[];reads=0
 def phase():return struct.unpack('<I',c.mem_read(OP,4))[0]
 def access(c,kind,addr,size,v,_):
  nonlocal reads
  off=addr-BASE;ph=phase()
  indices={0x6013d4:'cr',0xc03c4:'sq',0xc03ce:'gr'}
  data={o+1:n for o,n in indices.items()}
  if kind==u.UC_MEM_WRITE:
   writes.append([ph,off,size,v])
   if off in indices:assert size==1;sels[indices[off]]=v;return
   if off==0x6013c0:
    assert size==1
    if state['attr_data']:
     key=('at',sels['at']);state['attr_data']=False
     if sels['at']<16 and state['pas']:return
    else:
     assert v&0x20 or (ph in (7,9) and (v&31)<16 and sq[1]&0x20),'unblanked palette access'
     state['pas']=bool(v&0x20) or force_palette_pas
     sels['at']=v&31;state['attr_data']=True;return
   elif off in data:
    assert size==1;n=data[off];key=(n,sels[n])
    if n=='cr':
     assert key[1] not in (0x11,0x1b,0x22,0x33),'preserved register write prohibited'
     if key[1]==0x1f:
      if drop!=key:state['unlocked']=v==0x57
      return
     if key[1]>=0x19 and not state['unlocked']:return
     if key[1]<8 and cr[0x11]&0x80:return
   else:
    assert size==4 and off in (SETUP|TIMING|{0x600800:0}),hex(off);key=('mm',off)
   if (drop==key and (drop_phase is None or ph==drop_phase)) or (enable_drop and ph==10 and key==('sq',1)):return
   banks[key[0]][key[1]]=v
   if key==('mm',0x600800):
    state['geometry_done']=True;cr[0x19]=(cr[0x19]&0xe0)|((v>>18)&31)
  else:
   reads+=1
   if off in indices:assert size==1;c.mem_write(addr,bytes([sels[indices[off]]]));return
   if off==0x6013da:assert size==1;state['attr_data']=False;c.mem_write(addr,b'\0');return
   if off==0x6013c1:key=('at',sels['at']);assert size==1
   elif off in data:key=(data[off],sels[data[off]]);assert size==1
   else:key=('mm',off);assert size==4 and off in mm,hex(off)
   val=banks[key[0]][key[1]]
   if fault and key==fault[:2] and ph==fault[3] and (ph!=5 or state['geometry_done']):val^=fault[2]
   c.mem_write(addr,bytes([val]) if size==1 else pack(val))
 def pin(c,port,width,_):
  nonlocal reads
  reads+=1
  if port==0x8008:
   assert width==4
   di=144 if phase()==9 else state['index']-4
   if state['delay']!=di:state['delay']=di;state['delay_reads']=0
   if state['delay_reads']:
    step=0 if fail_delay==di and delay_kind=='stall' else -1 if fail_delay==di else 1688
    state['ticks']=(state['ticks']+step)&0xffffffff
   state['delay_reads']+=1;state['tick_reads']+=1;return state['ticks']
  if (port,width)==(0xc000,2):
   p=state['bus'];i=state['index']
   if p=='entry':return 8 if fail_bus==i+1 and bus_kind=='entry_busy' else 0x10 if fail_bus==i+1 and bus_kind=='dirty' else 0
   if p=='poll':return (0x11 if bus_kind=='error' else 8 if bus_kind=='timeout' else 0x10) if fail_bus==i else 0x10
   assert p=='final';state['bus']='entry';return 8 if fail_bus==i and bus_kind=='final_busy' else 0
  if (port,width)==(0xc006,2):return 3 if fail_bus==state['index'] and bus_kind=='short' else 4
  if (port,width)==(0xc009,1):v=bytes([0x12,0x34,0x56,0x78])[state['fifo']];state['fifo']+=1;return v
  raise AssertionError(('unreviewed port read',port,width))
 def pout(c,port,width,v,_):
  ph=phase();ports.append([ph,port,width,v])
  if port in (0x80d3,0x80d6,0x80d8):
   assert width==1 and v in ([4,5] if port==0x80d3 else [5] if port==0x80d6 else [4]);return
  assert port in (0xc000,0xc002,0xc004,0xc006,0xc008,0xc009) and ph==6
  if port==0xc004:assert state['bus']=='entry';state['index']+=1;state['fifo']=0
  if port==0xc002:state['bus']='poll';assert v==13 and width==1
  if port==0xc000:assert state['bus']=='poll';state['bus']='final'
 def corrupt(c,kind,addr,size,v,_):
  if fb_fault and phase()==8:c.mem_write(addr,b'\0'*size)
 c.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,access,None,BASE,BASE+0x7fffff)
 c.hook_add(u.UC_HOOK_INSN,pin,None,1,0,x.UC_X86_INS_IN)
 c.hook_add(u.UC_HOOK_INSN,pout,None,1,0,x.UC_X86_INS_OUT)
 if fb_fault:c.hook_add(u.UC_HOOK_MEM_READ,corrupt,None,FB,FB+3)
 c.emu_start(syms['native_transaction704'],END,timeout=10000000,count=50000000)
 assert c.reg_read(x.UC_X86_REG_EIP)==END,(label,'execution bound')
 ret=c.reg_read(x.UC_X86_REG_EAX);assert ret==expected,(label,ret,expected,phase(),[(hex(k),cr[k],v) for k,(m,v) in MASKS.items() if cr[k]&m!=(0x20|((req[1]>>18)&31) if k==0x19 else v)],[(hex(k),mm[k],v) for k,v in (TIMING|SETUP).items() if mm[k]!=v])
 assert c.reg_read(x.UC_X86_REG_EFLAGS)&0x200==flags&0x200
 assert c.mem_read(OP-16,16)==b'X'*16 and c.mem_read(OP+160,16)==b'X'*16,label
 assert c.mem_read(RP,60)==pack(*req) and c.mem_read(0x100000,len(blob))==blob
 assert c.mem_read(FB-4096,4096)==b'G'*4096
 assert c.mem_read(FB+1382400,ALLOC+4096-1382400)==b'Z'*(ALLOC+4096-1382400)
 assert all(mm[k]==originals['mm'][k] for k in PROTECTED+[0x680508,0x68050c,0x100200,0x600804])
 assert all(sels[k]==initial[k] for k in ('cr','sq','gr'))
 vals=list(struct.unpack('<24I',c.mem_read(OP,96))) if null!='out' else []
 if expected in (2,3,4):assert not writes and not ports and not reads
 elif expected==5:
  assert not ports and all(off in (0x6013d4,0xc03c4,0xc03ce) for _,off,_,_ in writes)
 else:
  assert ports[0][1:]==[0x80d3,1,5]
  enables=[p for p in ports if p[1:]==[0x80d3,1,4]]
  assert len(enables)==(1 if expected in (1,14) else 0),(label,enables)
  if expected!=1:
   assert ports[-1][1:]==[0x80d3,1,5]
   if drop!=('sq',1):assert sq[1]&0x20,label
  if expected==1:
   assert vals[:11]==[11,1,0,1,345600,720,480,2880,req[1],0x83,255],(label,vals)
   assert all(mm[k]==v for k,v in (TIMING|SETUP).items())
   assert all(cr[k]&m==(0x20|((req[1]>>18)&31) if k==0x19 else v) for k,(m,v) in MASKS.items())
   assert state['pas']
   assert list(sq[:5])==[3,1,15,0,6] and list(gr[:9])==GR and list(at[:20])==ATTR
   # Independent image oracle: rectangles/slices, not production pixel().
   row=bytearray(pack(0xffffffff)*720);expected_image=bytearray()
   for y in range(480):
    colors=[0xffff0000 if y<240 else 0xff0000ff]*360+[0xff00ff00 if y<240 else 0xffffffff]*360
    if y<64:colors=[0xff00ff00]*720
    if 360<=y<440:
     for col in range(160,560):colors[col]=0xffffffff if ((col//8)^(y//8))&1 else 0xff000000
    colors[:4]=colors[-4:]=[0xffffffff]*4
    expected_image.extend(row if y<4 or y>=476 else pack(*colors))
   assert c.mem_read(FB,1382400)==expected_image
  # Exact wire sequence, independent table endian oracle. No retry after fault.
  actual=[p[1:] for p in ports if p[1]>=0xc000]
  if phase()>=6:
   count=fail_bus+1 if fail_bus is not None else fail_delay+5 if fail_delay is not None and fail_delay<144 else 148
   ew=[]
   for i in range(count):
    read,reg,data=OPS[i]
    if fail_bus==i and bus_kind in ('entry_busy','dirty'):break
    ew.extend([[0xc004,1,0xe1 if read else 0xe0],[0xc008,1,reg]])
    if not read:ew.extend([[0xc009,1,z] for z in data]+[[0xc006,2,4]])
    ew.append([0xc002,1,13])
    if fail_bus==i and bus_kind=='timeout':break
    ew.append([0xc000,2,0x11 if fail_bus==i and bus_kind=='error' else 0x10])
   assert actual==ew,(label,'wire trace')
  else:assert not actual
 R['cases'].append({'name':label,'return':ret,'phase':phase() if null!='out' else None,
  'reads':reads,'mmio_writes':len(writes),'port_writes':len(ports),
  'mmio_sha256':sha(json.dumps(writes).encode()),'ports_sha256':sha(json.dumps(ports).encode()),
  'IF_and_protected_state_unchanged':True,'guards_unchanged':True,'selectors_restored':True})

try:
 run('complete-sequence-pattern-wrap',ext_lock=True)
 run('opposite-attribute-flipflop-state',seed=1)
 run('display-owned-palette-refusal',force_palette_pas=True,expected=11)
 for ph,err in [(5,9),(7,11),(9,11)]:
  for bit in range(8):run('CR19-bit-'+str(ph)+'-'+str(bit),fault=('cr',0x19,1<<bit,ph),expected=err)
 for i in range(15):run('invalid-request-'+str(i),bad=(i,0),expected=3)
 run('small703-buffer',bad=(2,1228800),expected=3)
 run('invalid-framebuffer-address',alias_bad=True,expected=3)
 run('kernel-high-alias-refused',high_alias=True,expected=3)
 for n in ('req','gpu','fb','out'):run('null-'+n,null=n,expected=2)
 run('IF-enabled',flags=0x202,expected=4)
 for off in CONTEXT:run('context-'+hex(off),pre=('mm',off,CONTEXT[off]^1),expected=5)
 for key,value in [(0x21,5),(0x44,3),(9,0x80),(0x28,0x81),(0x39,0)]:run('baseline-cr-'+hex(key),pre=('cr',key,value),expected=5)
 for i,v in [(0x1a,0),(0x1b,5),(0x22,255),(0x33,0)]:run('preserving-baseline-'+hex(i),pre=('cr',i,v),expected=5)
 run('blank-write-dropped',drop=('sq',1),expected=6)
 run('locked-base-refused',pre=('cr',0x11,0x80),expected=5)
 run('base-state-drift',fault=('cr',0x11,1,3),expected=7)
 run('extended-unlock-dropped',drop=('cr',0x1f),ext_lock=True,expected=8)
 for off in SETUP:
  if off!=0x680880:run('setup-drop-'+hex(off),drop=('mm',off),expected=8)
 for i in CS:run('setup-cr-drop-'+hex(i),drop=('cr',i),expected=8)
 for off in TIMING:run('geometry-drop-'+hex(off),drop=('mm',off),expected=9)
 for i in [0,1,2,4,6,7,0x13,0x25]:run('geometry-cr-drop-'+hex(i),drop=('cr',i),expected=9)
 for i in [3,5,9,0x16,0x2d,0x11]:run('preserved-bit-drift-'+hex(i),fault=('cr',i,0x80 if i in (3,9,0x16,0x2d) else 0x20 if i==5 else 1,5),expected=9)
 for kind in ('error','entry_busy','dirty','final_busy'):
  for i in range(148):run(kind+'-'+str(i),fail_bus=i,bus_kind=kind,expected=10)
 for i in range(144):run('delay-backwards-'+str(i),fail_delay=i,delay_kind='backwards',expected=10)
 for i in [0,147]:run('bus-timeout-'+str(i),fail_bus=i,bus_kind='timeout',expected=10)
 for i in [0,2]:run('short-read-'+str(i),fail_bus=i,bus_kind='short',expected=10)
 run('delay-stall',fail_delay=0,delay_kind='stall',expected=10)
 for bank,values in [('sq',SEQ),('gr',GR),('at',ATTR)]:
  for i in range(len(values)):
   if bank=='sq' and i==1:continue # Already21 from the earlier confirmed blank.
   run('vga-drop-'+bank+str(i),drop=(bank,i),drop_phase=7,expected=11)
 for off in TIMING|CONTEXT:run('final-readback-'+hex(off),fault=('mm',off,1,7),expected=11)
 run('pixel-readback-failure',fb_fault=True,expected=12)
 run('settle-backwards',fail_delay=144,delay_kind='backwards',expected=13)
 run('post-settle-drift',fault=('mm',0x680508,1,9),expected=11)
 run('enable-dropped-reblank',enable_drop=True,expected=14)
 # Independent unbounded-integer allocation oracle over every64MiB page.
 c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,blob)
 c.mem_map(0x200000,0x10000);n=0
 for base in range(0,0x4001000,4096):
  for size in (3686400,0xffffffff):
   assert time.monotonic()<deadline,'bounds deadline'
   req=DEFAULT.copy();req[1]=base;req[2]=size
   c.mem_write(RP,pack(*req));c.mem_write(SP,pack(END,RP));c.reg_write(x.UC_X86_REG_ESP,SP)
   c.emu_start(syms['bounds704'],END,count=1500)
   want=base>=0x2000000 and base+size<=0x4000000 and not (base<0x2800000 and base+size>0x2600000)
   assert c.reg_read(x.UC_X86_REG_EIP)==END and c.reg_read(x.UC_X86_REG_EAX)==int(want),(base,size)
   n+=1
 R['bounds_cases']=n;R['passed']=True
except BaseException as e:R['failure']=repr(e);raise
finally:
 R['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 OUT.write_text(json.dumps(R,indent=2)+'\n',encoding='utf8')
print('PASS',len(R['cases']),'linked complete-transaction model cases; no physical launch')
