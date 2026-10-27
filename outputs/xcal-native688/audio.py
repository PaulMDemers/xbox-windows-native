"""Fresh isolated execution of the retained legacy pre-video audio command."""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
out=K/'audio001.json';assert not out.exists()
r={'passed':False,'physical_access':False,'scope':'Compiled legacy I2CTransmitWord audio call; W1C status model, not actual boot','cases':[]}
try:
 blob=Path('C:/xwn687/handoff001/legacy.bin').read_bytes();r['image_sha256']=hashlib.sha256(blob).hexdigest()
 assert r['image_sha256']=='d7f888986277343883e45604b46fcd92db7b4692009f392de58dec034736e33a'
 raw=subprocess.check_output(['wsl','-d','Ubuntu','--','cat','/home/paul/xbox-windows-native/launcher677-validation002/default720/symbols.txt'],text=True,timeout=20)
 sym={a[2]:int(a[0],16) for l in raw.splitlines() if len(a:=l.split())==3}
 for terminal in [0x10,0x36]:
  uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);uc.mem_map(0x2600000,0x100000);uc.mem_write(0x2600000,blob)
  uc.mem_map(0x27f0000,0x10000);sp=0x27fe000;end=0x26ff000;trace=[];state={'status':0}
  uc.reg_write(x.UC_X86_REG_ESP,sp);uc.reg_write(x.UC_X86_REG_EFLAGS,2);uc.mem_write(sp,struct.pack('<3I',end,0x10,0x0b00))
  def inp(uc,p,w,_):
   assert p==0xc000 and w in [1,2];v=state['status'];trace.append(['in',p,w,v]);return v
  def output(uc,p,w,v,_):
   trace.append(['out',p,w,v])
   if p==0xc000:assert w==2;state['status']&=~v
   elif p==0xc002:assert (w,v)==(1,0x1a);state['status']=terminal
   else:assert [p,w,v] in [[0xc004,1,0x20],[0xc008,1,0x0b],[0xc006,2,0]]
  uc.hook_add(u.UC_HOOK_INSN,inp,None,1,0,x.UC_X86_INS_IN);uc.hook_add(u.UC_HOOK_INSN,output,None,1,0,x.UC_X86_INS_OUT)
  uc.emu_start(sym['I2CTransmitWord'],end,timeout=1000000,count=100000)
  assert uc.reg_read(x.UC_X86_REG_EIP)==end and uc.reg_read(x.UC_X86_REG_EAX)==0 and state['status']==terminal
  r['cases'].append({'terminal':terminal,'return':0,'status_retained':state['status'],'trace':trace})
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS two legacy audio outcomes; retained status and combined-error acceptance modeled')
