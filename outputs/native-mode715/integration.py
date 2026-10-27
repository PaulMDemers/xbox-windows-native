"""715 exact relocated read-only setup capture. No GPU programming/data-port writes.
Independent register-order, result/mismatch and whole-framebuffer optical oracle.
"""
import datetime,hashlib,json,os,struct,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn715/host001')
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
OUT=K/'integration001.json';assert not OUT.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
pack=lambda *v:struct.pack('<'+'I'*len(v),*v)
b=json.loads((K/'host001.json').read_text());assert b['passed']
for n,h in b['files'].items():assert sha((P/n).read_bytes())==h
for n,h in b['sources'].items():assert sha((K/n).read_bytes())==h
ps={a[2]:int(a[0],16)-0x100000 for line in Path('C:/xwn715/payload002/symbols.stdout').read_text().splitlines() if len(a:=line.split())==3}
code_end=min(int(a[0],16)-0x100000 for line in Path('C:/xwn715/payload002/symbols.stdout').read_text().splitlines() if len(a:=line.split())==3 and a[1] in ('t','T') and int(a[0],16)-0x100000>ps['native_transaction704'])
sy=b['bridge_symbols'];FB=0x3000000;SIZE=3686400;GPU=0xfd000000
R={'passed':False,'scope':__doc__,'physical_access':False,'harness_sha256':sha(Path(__file__).read_bytes()),'cases':[]}
deadline=time.monotonic()+240
SELECT=[0x80010000,0x80010004,0x80010010,0x80000900,0x80000904,0x80000914,0x80000800,0x80000804,0x80000810,0x80000884]
VALUES=[0x02a010de,2,0xfd000000,0x01b410de,1,0xc001,0x01b210de,1,0,0x8001]
SETUP=[0x680884,0x680888,0x68088c,0x680890,0x680894,0x680898,0x68089c,0x680880,0x680630,0x68084c,0x6808c4]
def run(name,page,refusal=None,pci_bad=None,req_bad=None,timer='normal',cr_bad=None,mm_bad=None,direct=False,null=None,flags=2,want=0x715,pattern=0x12345678,mismatch=0):
 assert time.monotonic()<deadline
 base=struct.unpack_from('<I',page,0x844)[0];sp=base+0x8000;end=base+sy['bridge_hold'];op=base+0x5100
 c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32)
 c.mem_map(base-4096,40960);c.mem_write(base-4096,b'G'*40960);c.mem_write(base,page)
 c.mem_map(FB-4096,SIZE+8192);c.mem_write(FB-4096,b'Z'*(SIZE+8192));c.mem_map(GPU,0x800000)
 if req_bad:c.mem_write(base+0x5000+4*req_bad[0],pack(req_bad[1]))
 data=bytes(c.mem_read(base,0x6000));total=sum(struct.unpack_from('<I',data,i)[0] for i in range(0,0x6000,4) if i!=0x854 and not 0x880<=i<0x900)&0xffffffff
 c.mem_write(base+0x854,pack(total));initial=bytes(c.mem_read(base,32768))
 c.reg_write(x.UC_X86_REG_GDTR,(0,base+0x800,31,0));c.reg_write(x.UC_X86_REG_CR0,0x40000011)
 for reg,val in [(x.UC_X86_REG_CS,0x10),(x.UC_X86_REG_DS,0x18),(x.UC_X86_REG_ES,0x18),(x.UC_X86_REG_SS,0x18)]:c.reg_write(reg,val)
 c.reg_write(x.UC_X86_REG_EBP,base);c.reg_write(x.UC_X86_REG_ESP,sp);c.reg_write(x.UC_X86_REG_EFLAGS,flags)
 pci=dict(zip(SELECT,VALUES))
 if pci_bad:pci[pci_bad[0]]=pci_bad[1]
 state={'selector':0x12345678,'timer_reads':0,'payload_blocks':0};trace=[];reads=[];writes=[];setup_reads=[]
 cr=bytearray([0xa5]*256);cr[9]=0x25;cr[0x11]=9;cr[0x21]=255;cr[0x44]=0;cr[0x39]=255;cr[0x13]=0x80;cr[0x19]=0x51;cr[0x25]=0x10;cr[0x28]=0x83;cr[0x2d]=0xe0
 if cr_bad:cr[cr_bad[0]]=cr_bad[1]
 original_cr=bytes(cr)
 sels={0x6013d4:0x67,0xc03c4:0x72,0xc03ce:0x91};original_sels=dict(sels)
 mm={0x680508:0x3c20d,0x68050c:0x100a0400,0x680880:0x21101100,0x100200:0x3070003,0x600804:3,0x600800:FB,0x680838:1279,0x680818:719}
 values=[(pattern^(i*0x01020408))&0xffffffff for i in range(11)];values[7]=0x21101100
 for off,value in zip(SETUP,values):mm[off]=value
 if mm_bad:mm[mm_bad[0]]=mm_bad[1]
 setup_counts={off:0 for off in SETUP}
 def access(c,kind,addr,width,value,_):
  off=addr-GPU
  if kind==u.UC_MEM_WRITE:
   assert width==1
   writes.append([off,value])
   assert off in sels,'GPU data/register write forbidden'
   sels[off]=value
  else:
   reads.append([off,width])
   if off in sels:assert width==1;value=sels[off]
   elif off==0x6013d5:assert width==1 and sels[0x6013d4]!=0x1f,'CR1f readback is not a write-key oracle';value=cr[sels[0x6013d4]]
   else:
    assert off in mm and width==4,'unexpected GPU read';value=mm[off]
    if off in SETUP and struct.unpack('<I',c.mem_read(op,4))[0]==2:
     n=setup_counts[off];assert n<2;setup_counts[off]+=1;setup_reads.append(off)
     if n==1 and mismatch&(1<<SETUP.index(off)):value^=0x80000001
   c.mem_write(addr,value.to_bytes(width,'little'))
 def pin(c,port,width,_):
  assert width==4
  if port==0xcf8:trace.append(['read',port]);return state['selector']
  if port==0xcfc:trace.append(['read',port,state['selector']]);return pci[state['selector']]
  assert port==0x8008,'unexpected device I/O read'
  n=state['timer_reads'];state['timer_reads']+=1
  first=0xfffffff0 if timer=='wrap' else 0x1000
  step={'normal':200,'wrap':200,'stall':0,'backwards':-1,'jump':33751,'minimum':1688,'maximum':33750}[timer]
  return (first+n*step)&0xffffffff
 def pout(c,port,width,value,_):
  assert port==0xcf8 and width==4,'forbidden device I/O write'
  trace.append(['write',port,value]);state['selector']=value
 def block(c,pc,size,_):
  if base+0x1000<=pc<base+0x1000+9916:
   state['payload_blocks']+=1
   assert pc<base+0x1000+code_end,'encoder/programming helper executed'
 c.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,access,None,GPU,GPU+0x7fffff)
 c.hook_add(u.UC_HOOK_INSN,pin,None,1,0,x.UC_X86_INS_IN)
 c.hook_add(u.UC_HOOK_INSN,pout,None,1,0,x.UC_X86_INS_OUT)
 c.hook_add(u.UC_HOOK_BLOCK,block)
 start=base+sy['bridge_post']
 if direct:
  args=[base+0x5000,GPU,FB,op]
  if null is not None:args[null]=0
  c.reg_write(x.UC_X86_REG_ESP,sp-20);c.mem_write(sp-20,pack(end,*args))
  start=base+0x1000+ps['native_transaction704']
 c.emu_start(start,end,timeout=10000000,count=50000000)
 assert c.reg_read(x.UC_X86_REG_EIP)==end,(name,'execution bound')
 assert c.reg_read(x.UC_X86_REG_ESP)==(sp-16 if direct else sp)
 assert c.reg_read(x.UC_X86_REG_EFLAGS)&0x200==flags&0x200
 assert sels==original_sels,'indexed selectors not restored'
 final=bytes(c.mem_read(base,32768))
 for begin,last in [(0,0x880),(0x900,0x5100),(0x5200,0x6000)]:assert final[begin:last]==initial[begin:last]
 for ptr in (base-4096,base+32768):assert c.mem_read(ptr,4096)==b'G'*4096
 for ptr in (FB-4096,FB+SIZE):assert c.mem_read(ptr,4096)==b'Z'*4096
 expected=bytearray(b'Z'*SIZE)
 captured=not refusal and want in (0x715,0x7152)
 if captured:
  for y in range(104,640):expected[y*5120+112*4:y*5120+1168*4]=pack(0x404040)*1056
  optical=[0x7150000b,mismatch,*values]
  for row,value in enumerate(optical):
   # MSB first independent binary string, no copied bitmask loop.
   for bit,char in enumerate(f'{value:032b}'):
    for y in range(120+row*40,140+row*40):
     x0=128+32*bit;expected[y*5120+x0*4:y*5120+(x0+20)*4]=pack(0xffffff if char=='1' else 0)*20
 if not direct:
  expected_trace=[['read',0xcf8]]
  for sel in SELECT:expected_trace.extend([['write',0xcf8,sel],['read',0xcfc,sel]])
  expected_trace.append(['write',0xcf8,0x12345678]);assert trace==expected_trace and state['selector']==0x12345678
  color=({1:0xff0000,2:0xffff00,3:0xff00ff,4:0xff8000,5:0xffffff}[refusal] if refusal else 0x00ff00 if want==0x715 else 0xff8000)
  for row0,rgb in [(8,0x00ff00),(48,color)]:
   for row in range(row0,row0+32):expected[row*5120+32:row*5120+5088]=pack(rgb)*1264
  assert struct.unpack_from('<I',final,0x880)[0]==(2 if refusal else 4)
  if refusal:
   assert not reads and not writes and not state['payload_blocks']
   assert struct.unpack_from('<I',final,0x8d0)[0]==refusal
  else:assert struct.unpack_from('<I',final,0x8d4)[0]==want
 else:assert not trace and not state['timer_reads'] and c.reg_read(x.UC_X86_REG_EAX)==want
 assert setup_reads==(SETUP*2 if captured else []),'exact two ordered capture passes'
 assert bytes(cr)==original_cr,'no CRTC data changes'
 if not refusal:
  assert state['payload_blocks']>0
  if null!=3:
   result=struct.unpack('<64I',c.mem_read(op,256));assert result[1]==want,(name,result)
   assert result[0]==(3 if captured else 1 if want==5 else 0)
   assert result[2:11]==(0,)*9 and result[19:52]==(0,)*33
   if captured or want==5:
    assert result[11:19]==(original_cr[0x11],original_cr[0x21],original_cr[3]&0xe0,original_cr[5]&0x60,original_cr[9]&0x9f,original_cr[0x16]&0x80,original_cr[0x2d]&0xe0,original_cr[0x11]&0x7f)
   elif want in (2,3,4):assert not reads and not writes
   assert result[52:64]==tuple(values+[mismatch]) if captured else result[52:64]==(0,)*12
 assert c.mem_read(FB,SIZE)==expected,'whole framebuffer oracle'
 R['cases'].append({'name':name,'direct_call':direct,'refusal':refusal,'return':None if refusal else want,
  'payload_blocks':state['payload_blocks'],'GPU_reads':len(reads),'selector_writes':len(writes),
  'selector_trace_sha256':sha(json.dumps(writes).encode()),'selectors_restored':True,
  'GPU_data_writes':0,'capture_read_offsets':setup_reads,'first_values':values if captured else None,
  'mismatch':mismatch if captured else None,'whole_framebuffer_guards_pass':True})
try:
 for layout in ('dual','relocated'):
  page=(P/layout/'page.bin').read_bytes()
  for timer in ('normal','wrap','minimum','maximum'):run(layout+'-'+timer,page,timer=timer)
  for timer in ('stall','backwards','jump'):run(layout+'-'+timer,page,timer=timer,refusal=5)
  run(layout+'-bridge-fb-mismatch',page,req_bad=(1,FB+4096),refusal=4)
  for idx,value,code in [(0,0,1),(1,0,1),(2,0xfc000000,1),(3,0,2),(4,0,2),(5,0xd001,2),(6,0,3),(7,0,3),(8,0x9001,3),(8,0x8001,3),(9,0,3)]:
   run(layout+'-PCI-'+str(idx)+'-'+hex(value),page,refusal=code,pci_bad=(SELECT[idx],value))
  for reg,value in [(0x11,0x80),(0x21,0),(0x44,3),(9,0x80),(0x13,0),(0x19,0),(0x25,0x20),(0x28,0),(0x39,0)]:
   run(layout+'-CR-'+hex(reg),page,cr_bad=(reg,value),want=5)
  for reg in (0x680508,0x68050c,0x680880,0x100200,0x600804,0x600800,0x680838,0x680818):
   run(layout+'-MMIO-'+hex(reg),page,mm_bad=(reg,0),want=5)
  for idx in range(15):
   run(layout+'-request-'+str(idx),page,req_bad=(idx,0),direct=True,want=3)
  for idx in range(4):run(layout+'-null-'+str(idx),page,direct=True,null=idx,want=2)
  run(layout+'-IF',page,direct=True,flags=0x202,want=4)
  run(layout+'-direct-checkpoint',page,direct=True)
  for pattern in (0,0xffffffff,0xaaaaaaaa,0x55555555,0x80000001):
   run(layout+'-optical-'+hex(pattern),page,pattern=pattern)
  for bit in range(11):run(layout+'-unstable-'+str(bit),page,mismatch=1<<bit,want=0x7152)
  run(layout+'-all-unstable',page,mismatch=0x7ff,want=0x7152)
 R['passed']=True
except BaseException as e:R['failure']=repr(e);raise
finally:
 R['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();OUT.write_text(json.dumps(R,indent=2)+'\n')
print('PASS',len(R['cases']),'read-only capture and optical models; no physical proof')
