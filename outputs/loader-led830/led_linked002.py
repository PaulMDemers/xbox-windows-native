"""Execute the actual full-image post-transaction LED path with modeled I/O.
Admission and transaction returns are injected here; their linked instructions
are tested separately. This does not prove a physical LED or display result.
"""
from pathlib import Path
import os,sys,json,hashlib,struct,re
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('C:/xwn830/firmware001')
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
out=K/'led-linked002.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((K/'firmware/build001.json').read_text());assert b['passed']
for n,h in b['source_pins'].items():assert sha(K/'firmware'/n)==h
for n,v in b['artifacts'].items():assert sha(B/n)==v['sha256']
sym={a[2]:int(a[0],16) for l in (B/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}
dis=(B/'disassembly.stdout').read_text();part=dis.split('<XcalEntry826>:')[1].split('\n\n')[0]
halt=int(re.findall(r'^\s*([0-9a-f]+):\s+f4\s+hlt',part,re.M)[0],16)
pack=lambda *a:struct.pack('<'+'I'*len(a),*a)
r={'passed':False,'physical_access':False,'scope':__doc__,'firmware_sha256':sha(B/'image-crom.bin'),'cases':[]}
try:
 specs=[('phase'+str(ph),ph,er) for ph,er in [(0,3),(1,5),(2,6),(3,7),(4,8),(5,9),(6,10),(7,11),(8,12),(9,13),(10,14),(11,1)]]
 specs += [(n,5,9) for n in ['dirty','busy','bus-error','final-dirty','busy-terminal','timer-backwards']]
 for name,ph,er in specs:
  c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0,0x4000000);c.mem_write(0x2600000,(B/'image-crom.bin').read_bytes())
  sp=0x27fe000;c.reg_write(x.UC_X86_REG_ESP,sp);c.mem_write(sp,pack(0x26ff000));c.reg_write(x.UC_X86_REG_EFLAGS,2)
  s=dict(status=0x10 if name=='dirty' else 8 if name=='busy' else 0,address=0,reg=0,data=0,ticks=0xfffffe00,frames=0,halt=False,transaction=0)
  commands=[];io=[];acks=[]
  def ret(value):
   esp=c.reg_read(x.UC_X86_REG_ESP);dst=struct.unpack('<I',c.mem_read(esp,4))[0];c.reg_write(x.UC_X86_REG_ESP,esp+4);c.reg_write(x.UC_X86_REG_EAX,value);c.reg_write(x.UC_X86_REG_EIP,dst)
  def collect(c,a,z,_):ret(1)
  def transaction(c,a,z,_):
   esp=c.reg_read(x.UC_X86_REG_ESP);args=struct.unpack('<4I',c.mem_read(esp+4,16))
   assert args==(sym['XcalState826']+128,0xfd000000,0x03700000,sym['XcalState826']+192)
   c.mem_write(args[3],pack(ph,er));s['transaction']+=1;ret(er)
  def frame(c,a,z,_):
   esp=c.reg_read(x.UC_X86_REG_ESP);args=struct.unpack('<5I',c.mem_read(esp+4,20));assert args[2:]==(0,ph,er)
   s['frames']+=1
   if s['frames']==3:c.emu_stop()
  def stop(c,a,z,_):s['halt']=True;c.emu_stop()
  def inp(c,p,w,_):
   if p==0xc000:assert w==2;v=s['status']
   elif p==0x8008:
    assert w==4;s['ticks']=(s['ticks']+(-1 if name=='timer-backwards' else 1687500))&0xffffffff;v=s['ticks']
   else:raise AssertionError(('unexpected input',p,w))
   io.append(['in',p,w,v]);return v
  def output(c,p,w,v,_):
   io.append(['out',p,w,v])
   if p==0xc004:assert w==1 and v==0x20;s['address']=v
   elif p==0xc008:assert w==1 and v in (7,8);s['reg']=v
   elif p==0xc006:assert w==2 and v<=255;s['data']=v
   elif p==0xc002:
    assert w==1 and v==10 and s['status']==0 and s['address']==0x20
    commands.append([s['reg'],s['data']]);s['status']=0x11 if name=='bus-error' else 0x18 if name=='busy-terminal' else 0x10
   elif p==0xc000:
    assert w==2 and not s['status']&0x808 and v==s['status']&0x37
    acks.append(v);s['status']=0x10 if name=='final-dirty' else 0
   else:raise AssertionError(('unexpected output',p,w,v))
  c.hook_add(u.UC_HOOK_CODE,collect,None,sym['XcalCollect826'],sym['XcalCollect826'])
  c.hook_add(u.UC_HOOK_CODE,transaction,None,sym['native_transaction704'],sym['native_transaction704'])
  c.hook_add(u.UC_HOOK_CODE,frame,None,sym['led_frame830'],sym['led_frame830'])
  c.hook_add(u.UC_HOOK_CODE,stop,None,halt,halt)
  c.hook_add(u.UC_HOOK_INSN,inp,None,1,0,x.UC_X86_INS_IN);c.hook_add(u.UC_HOOK_INSN,output,None,1,0,x.UC_X86_INS_OUT)
  c.emu_start(sym['XcalEntry826'],0x26ff000,timeout=15000000,count=10000000)
  assert s['transaction']==1 and not c.reg_read(x.UC_X86_REG_EFLAGS)&0x200
  if name.startswith('phase'):
   expected=[[8,255],[7,1],[8,0]]+[[8,v] for i in range(ph) for v in (240,0)]+[[8,v] for i in range(er) for v in (15,0)]
   assert commands==expected*2 and acks==[16]*len(commands) and s['frames']==3 and not s['halt']
  else:
   assert s['halt'] and s['frames']==1
   expected_status={'dirty':3,'busy':2,'bus-error':5,'final-dirty':7,'busy-terminal':4,'timer-backwards':4}[name]
   assert struct.unpack('<I',c.mem_read(sym['LedStatus830'],4))[0]==expected_status
   if name in ('dirty','busy'):assert not commands and not acks
   elif name=='busy-terminal':assert len(commands)==1 and not acks
   elif name=='timer-backwards':assert len(commands)==2 and len(acks)==2
   else:assert len(commands)==1 and len(acks)==1
  r['cases'].append(dict(name=name,phase=ph,error=er,state=s,commands=commands,acks=acks,io_sha256=hashlib.sha256(json.dumps(io).encode()).hexdigest()))
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS',len(r['cases']),'actual linked LED reporting paths')
