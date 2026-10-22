"""Execute exact build002 wrapper instructions with explicitly modeled callees.
No console, firmware, disk, timing or physical LED proof.
"""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
B=Path('C:/xwn648/build002');record=read(K/'build002.json')
assert record['status']=='compiled'
blob=(B/'image-crom.bin').read_bytes();assert sha(blob)==record['outputs']['image-crom.bin']['sha256']
text=subprocess.check_output(['wsl','-d','Ubuntu','--','nm','-n','/mnt/c/xwn648/build002/image-crom.elf'],text=True,timeout=25)
symbols={a[2]:int(a[0],16) for line in text.splitlines() if len(a:=line.split())==3}
required=('XwnHdTry720','XwnHdState311','XwnDiag648Status','xbox_ram','xwn_hd_apply','xwn_hd_smb_write','hd_delay','XwnTrace648')
assert all(n in symbols for n in required)
rows=[(1,5,0,5),(0,0,0,80),(-1,255,11,245),(-1,255,12,245),(-1,255,13,245),
      (-1,255,21,255),(-1,255,22,165),(-1,255,23,95),(-1,255,24,95),
      (1,4,0,0),(0,1,0,0),(-1,255,0,0),(-1,4,22,0),(2,5,0,0)]
results=[]
out=K/'compiled-wrapper001.json';assert not out.exists()
cases=[(*row,0) for row in rows if row[2]!=22]+[(-1,255,22,165,p) for p in range(8)]+[(-1,4,22,0,0)]
for result,stage,error,mask,phase in cases:
 for fail in range(6 if error==22 and stage==255 else 4):
  uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);uc.mem_map(0x02600000,0x100000);uc.mem_write(0x02600000,blob)
  uc.mem_map(0x027f0000,0x10000);esp=0x027fe000;end=0x026ff000;mode=0x026f0000
  uc.mem_write(esp,struct.pack('<5I',end,mode,0,3,8));uc.mem_write(symbols['xbox_ram'],struct.pack('<I',64))
  uc.reg_write(x.UC_X86_REG_ESP,esp)
  for reg in (x.UC_X86_REG_EBX,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI,x.UC_X86_REG_EBP):uc.reg_write(reg,0x12345678)
  events=[];delays=[];setup=[0];halt=[False]
  def words(address,count):return struct.unpack('<'+'I'*count,uc.mem_read(address,4*count))
  def ret(value):
   sp=uc.reg_read(x.UC_X86_REG_ESP);dest=words(sp,1)[0]
   uc.reg_write(x.UC_X86_REG_EAX,value&0xffffffff);uc.reg_write(x.UC_X86_REG_ESP,sp+4);uc.reg_write(x.UC_X86_REG_EIP,dest)
  def hook(uc,address,size,unused):
   if address==symbols['xwn_hd_apply']:
    setup[0]+=1;assert setup[0]==1 and not events
    io,request,state=words(uc.reg_read(x.UC_X86_REG_ESP)+4,3)
    assert words(request,8)==(3,64*1024**2,55*1024**2,9*1024**2,316160,0,3,8)
    assert state==symbols['XwnHdState311']
    uc.mem_write(state,struct.pack('<9I',stage,error,int(result!=0),19,19,1,2,0,0));uc.mem_write(symbols['XwnTrace648']+8,struct.pack('<I',phase));ret(result)
   elif address==symbols['xwn_hd_smb_write']:
    io,a,r,v=words(uc.reg_read(x.UC_X86_REG_ESP)+4,4);events.append((a,r,v))
    assert a==0x10 and r in (8,7,2)
    ret(1 if r!=2 and len(events)==fail else 0)
   elif address==symbols['hd_delay']:
    context,us=words(uc.reg_read(x.UC_X86_REG_ESP)+4,2);assert us==1000000
    delays.append(us);assert len(delays)<=18;ret(0)
   elif bytes(uc.mem_read(address,1))==b'\xf4':halt[0]=True;uc.emu_stop()
  uc.hook_add(u.UC_HOOK_CODE,hook)
  uc.emu_start(symbols['XwnHdTry720'],end,count=50000)
  detailed=result==-1 and stage==255 and error==22
  masks=[0,80,5,85,165,245,95,0]
  writes=[(0x10,8,mask),(0x10,7,1)]
  if detailed:writes.extend([(0x10,8,0),(0x10,8,masks[phase])])
  writes.append((0x10,7,0))
  expected=writes[:fail or len(writes)]
  if result<=0:expected.append((0x10,2,1))
  assert events==expected,(result,stage,error,phase,fail,events,expected)
  count=(0 if fail in (1,2) else 8)
  if detailed:count=(0 if fail in (1,2) else 8 if fail==3 else 10 if fail==4 else 18)
  assert len(delays)==count
  status=fail if detailed or fail<3 else 5
  assert words(symbols['XwnDiag648Status'],1)[0]==status
  assert halt[0]==(result<=0)
  if result>0:
   assert uc.reg_read(x.UC_X86_REG_EIP)==end and uc.reg_read(x.UC_X86_REG_EAX)==result
   assert uc.reg_read(x.UC_X86_REG_ESP)==esp+4
   assert all(uc.reg_read(reg)==0x12345678 for reg in (x.UC_X86_REG_EBX,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI,x.UC_X86_REG_EBP))
   if result==1:assert words(mode+16,4)==(720,480,0,0)
  if result==0:assert words(symbols['XwnHdState311']+4,1)[0]==30
  results.append(dict(result=result,stage=stage,error=error,mask=mask,failed_diagnostic_write=fail,phase=phase,
                      smc_calls=events,delay_calls=len(delays),original_reset_path=halt[0]))
with out.open('x') as f:json.dump(dict(passed=True,cases=len(results),physical_access=False,
 scope='Exact compiled wrapper; xwn_hd_apply (including trace phase), SMBus send and delay are mocked. Original profile code executes on success. No physical marker/timing/boot proof.',
 image_sha256=sha(blob),symbols={n:symbols[n] for n in required},results=results),f,indent=2);f.write('\n')
print('PASS',len(results),'compiled wrapper outcomes')
