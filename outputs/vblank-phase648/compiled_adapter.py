"""Execute exact linked adapter/profile instructions; all hardware callbacks modeled."""
import hashlib,json,struct,subprocess,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
B=Path('C:/xwn648/build002');record=json.loads((K/'build002.json').read_text())
blob=(B/'image-crom.bin').read_bytes();digest=hashlib.sha256(blob).hexdigest()
assert digest==record['outputs']['image-crom.bin']['sha256']
nm=subprocess.check_output(['wsl','-d','Ubuntu','--','nm','-n','/mnt/c/xwn648/build002/image-crom.elf'],text=True,timeout=25)
symbols={a[2]:int(a[0],16) for line in nm.splitlines() if len(a:=line.split())==3}
out=K/'compiled-adapter001.json';assert not out.exists()
report=dict(passed=False,physical_access=False,image_sha256=digest,results=[],scope='Exact linked adapter/profile code. Hardware callbacks are synthetic; no actual timing, register or boot proof.')
def save():out.write_text(json.dumps(report,indent=2)+'\n')
save()
try:
 cases=[('immediate',-1,0),('delayed',-2,3)]+[('timeout',i,100000) for i in range(6)]+[('last_allowed',i,99999) for i in (0,5)]
 for name,target,lag in cases:
  began=time.monotonic();uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32)
  uc.mem_map(0x02600000,0x100000);uc.mem_write(0x02600000,blob)
  uc.mem_map(0x027f0000,0x10000)
  esp=0x027fe000;end=0x026ff000;io=0x026e0000;request=io+0x100;state=io+0x200;stub=0x026f1000
  uc.mem_write(io,struct.pack('<10I',0,*[stub+16*i for i in range(9)]))
  uc.mem_write(request,struct.pack('<8I',3,64*1024**2,55*1024**2,9*1024**2,316160,0,3,8))
  uc.mem_write(esp,struct.pack('<4I',end,io,request,state));uc.reg_write(x.UC_X86_REG_ESP,esp)
  for reg in (x.UC_X86_REG_EBX,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI,x.UC_X86_REG_EBP):uc.reg_write(reg,0x12345678)
  d=dict(mmio={},crtc={},index=0,enabled=False,phase=0,at=0,calls=0,polls=0,us=0,unblank=0)
  lagv=[lag if i==target or target==-2 else 0 for i in range(6)]
  def words(a,n):return struct.unpack('<'+'I'*n,uc.mem_read(a,4*n))
  def hook(uc,address,size,unused):
   which=(address-stub)//16;assert address==stub+which*16 and which<8
   sp=uc.reg_read(x.UC_X86_REG_ESP);dest,context,a,v=words(sp,4);assert context==0
   d['calls']+=1;assert d['calls']<1300000
   result=0
   if which==0:
    result=0x3c20d if a==0x680508 else 3 if a==0x600804 else 0 if a==0x6806a0 else d['mmio'].get(a,0)
   elif which==1:d['mmio'][a]=v
   elif which==2:
    if a==0x6013da and d['enabled']:
     p=d['phase'];assert p<6;wanted=(p%2)*8
     result=0xa0|(wanted^8 if d['at']<lagv[p] else wanted)|(d['at']&1)
     d['at']+=1;d['polls']+=1
     if result&8==wanted:d['phase']+=1;d['at']=0
    elif a==0x6013d5:result=d['crtc'][d['index']]
   elif which==3:
    if a==0x6013d4:d['index']=v
    if a==0x6013d5:d['crtc'][d['index']]=v
    if a==0xc03c5 and v==1:d['enabled']=True
   elif which==4:assert a==0xc000
   elif which==5:assert a==0xc000;result=0x10
   elif which==6:pass
   elif which==7:
    if a==0x80d3 and v==4:d['unblank']+=1
   uc.reg_write(x.UC_X86_REG_EAX,result);uc.reg_write(x.UC_X86_REG_ESP,sp+4);uc.reg_write(x.UC_X86_REG_EIP,dest)
  # io order is r32,w32,r8,w8,in16,in8,out16,out8,delay (nine callbacks).
  base_hook=hook
  def callbacks(uc,address,size,unused):
   if address==stub+8*16:
    sp=uc.reg_read(x.UC_X86_REG_ESP);dest,context,us=words(sp,3)
    assert context==0 and us in (1,10);d['us']+=us;d['calls']+=1
    uc.reg_write(x.UC_X86_REG_EAX,0);uc.reg_write(x.UC_X86_REG_ESP,sp+4);uc.reg_write(x.UC_X86_REG_EIP,dest)
   else:base_hook(uc,address,size,unused)
  uc.hook_add(u.UC_HOOK_CODE,callbacks,begin=stub,end=stub+8*16)
  uc.emu_start(symbols['xwn_hd_apply'],end,timeout=60000000,count=15000000)
  assert uc.reg_read(x.UC_X86_REG_EIP)==end and uc.reg_read(x.UC_X86_REG_ESP)==esp+4
  assert all(uc.reg_read(reg)==0x12345678 for reg in (x.UC_X86_REG_EBX,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI,x.UC_X86_REG_EBP))
  values=words(symbols['XwnTrace648'],45);failed=target+1 if name=='timeout' else 0;completed=target if failed else 6
  assert values[:3]==(completed+(1 if failed else 0),completed,failed)
  for i in range(6):
   row=values[3+7*i:10+7*i]
   if i>=values[0]:assert row==(0,)*7;continue
   wanted=(i%2)*8;n=lagv[i];samples=min(n+1,100000)
   expected=(wanted,0xa0|(wanted^8 if n else wanted),0xa0|(wanted^8 if n>=100000 else wanted)|((samples-1)&1),samples,samples-1,int(n>0 and n<100000),int(n<100000))
   assert row==expected,(name,i,row,expected)
  assert words(state,2)==((255,22) if failed else (5,0))
  assert uc.reg_read(x.UC_X86_REG_EAX)==(0xffffffff if failed else 1)
  assert d['unblank']==(0 if failed else 1)
  report['results'].append(dict(name=name,target=target,lag=lag,trace=values,callback_count=d['calls'],requested_delay_us=d['us'],host_seconds=round(time.monotonic()-began,3)))
  save()
 report['passed']=True;report['cases']=len(cases)
except BaseException as e:report['failure']=repr(e);raise
finally:save()
print('PASS',len(report['results']),'exact linked adapter cases')
