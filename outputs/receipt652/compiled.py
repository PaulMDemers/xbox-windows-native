"""Execute linked i386 protocol with modeled callbacks, never real disk I/O."""
import hashlib,json,struct,sys,datetime
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
from decode import decode
B=Path('C:/xwn652/linked001');h=json.loads((K/'linked001.json').read_text());assert h['passed']
for p in B.iterdir():assert hashlib.sha256(p.read_bytes()).hexdigest()==h['artifacts'][p.name]['sha256']
symbols={a[2]:int(a[0],16) for line in (B/'symbols.stdout').read_text().splitlines() if len(a:=line.split())==3}
blob=(B/'receipt.bin').read_bytes();expected=Path('C:/xwn652/host001/synthetic-record.bin').read_bytes()
identity=expected[16:64]
out=K/'compiled001.json';assert not out.exists()
r=dict(passed=False,physical_access=False,scope='Exact linked i386 protocol; modeled read/write/flush callbacks, not hardware qualification',results=[],source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 for fail,after in [(0,False)]+[(i,a) for i in range(1,14) for a in (False,True)]:
  uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);uc.mem_map(0x100000,0x10000);uc.mem_write(0x100000,blob)
  uc.mem_map(0x200000,0x10000);uc.mem_map(0x300000,0x10000)
  guard,io,idp,data,scratch,stubs,end=0x200000,0x200100,0x200200,0x200300,0x201000,0x108000,0x109000
  stack=0x30f000;uc.mem_write(idp,identity);uc.mem_write(data,expected[64:768])
  uc.mem_write(io,struct.pack('<4I',0x1234,stubs,stubs+16,stubs+32))
  uc.mem_write(stack,struct.pack('<6I',end,guard,io,idp,data,scratch));uc.reg_write(x.UC_X86_REG_ESP,stack)
  uc.reg_write(x.UC_X86_REG_EFLAGS,0x202)
  saved=(x.UC_X86_REG_EBX,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI,x.UC_X86_REG_EBP)
  for reg in saved:uc.reg_write(reg,0x12345678)
  # Generate fresh seeds through the compiled seed routine itself. The store
  # path is checked against the independent Python payload oracle below.
  for i in range(3):
   uc.mem_write(stack,struct.pack('<4I',end,idp,i,scratch+i*512))
   uc.emu_start(symbols['xwn652_seed'],end,count=1000000)
   assert uc.reg_read(x.UC_X86_REG_EIP)==end
   uc.reg_write(x.UC_X86_REG_ESP,stack)
  state=dict(cache=bytearray(uc.mem_read(scratch,1536)),disk=bytearray(uc.mem_read(scratch,1536)),calls=0,sequence='')
  uc.mem_write(scratch,b'\xcc'*2048)
  uc.mem_write(stack,struct.pack('<6I',end,guard,io,idp,data,scratch))
  def callback(uc,address,size,unused):
   which=(address-stubs)//16;assert which in (0,1,2) and address==stubs+16*which
   sp=uc.reg_read(x.UC_X86_REG_ESP)
   dest,context,sector,buffer=struct.unpack('<4I',uc.mem_read(sp,16));assert context==0x1234
   state['calls']+=1;state['sequence']+='RWF'[which]
   failed=state['calls']==fail
   if not failed or after:
    if which<2:assert sector<3
    if which==0:uc.mem_write(buffer,bytes(state['cache'][512*sector:512*(sector+1)]))
    elif which==1:state['cache'][512*sector:512*(sector+1)]=uc.mem_read(buffer,512)
    else:state['disk'][:]=state['cache']
   uc.reg_write(x.UC_X86_REG_EAX,int(failed));uc.reg_write(x.UC_X86_REG_ESP,sp+4);uc.reg_write(x.UC_X86_REG_EIP,dest)
  uc.hook_add(u.UC_HOOK_CODE,callback,begin=stubs,end=stubs+32)
  uc.emu_start(symbols['xwn652_store'],end,count=4000000)
  assert uc.reg_read(x.UC_X86_REG_EIP)==end and uc.reg_read(x.UC_X86_REG_ESP)==stack+4
  assert all(uc.reg_read(reg)==0x12345678 for reg in saved)
  assert uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200
  result=uc.reg_read(x.UC_X86_REG_EAX);assert bool(result)==bool(fail)
  assert state['sequence']=='RRRWWFRRWFRRR'[:fail or 13]
  if not fail:assert bytes(state['disk'])==expected
  valid=True
  try:decode(bytes(state['disk']),identity[:16],identity[16:])
  except ValueError:valid=False
  assert valid==(not fail or fail>10 or (fail==10 and after))
  calls=state['calls'];uc.mem_write(stack,struct.pack('<6I',end,guard,io,idp,data,scratch));uc.reg_write(x.UC_X86_REG_ESP,stack)
  uc.emu_start(symbols['xwn652_store'],end,count=100000)
  assert uc.reg_read(x.UC_X86_REG_EAX)==2 and state['calls']==calls
  r['results'].append(dict(fail_call=fail,after=after,result=result,calls=calls,modeled_durable_format_valid=valid,retry_refused=True));save()
 r['passed']=True;r['cases']=len(r['results'])
except BaseException as e:r['failure']=repr(e);raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps(dict(passed=r['passed'],cases=len(r['results']))))
