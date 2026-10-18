# SPDX-License-Identifier: MIT
"""Execute actual clearing/arithmetic bytes; privileged effects explicitly modeled."""
import datetime,hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'))
import capstone,unicorn
from unicorn import x86_const as x
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
q=read(K/'prepared001.json');md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
out=K/'setup-host001.json';assert not out.exists()
cases=[];r=dict(status='running',cases=cases,physical_access=False,
 scope='Actual instruction bytes and memory writes in flat host model. CR3, CLTS, LIDT, WRMSR and WBINVD effects are recorded/skipped, not physically validated; no device/cache proof.')
def save():out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
save()
expected_msrs=[(0x2ff,0,0),(0x200,6,0),(0x201,0xf8000800,15),
 (0x202,0xf0000001,0),(0x203,0xf8000800,15),(0x204,0xfff00000,0),(0x205,0xfff00800,15)]
expected_msrs += [(i,0,0) for i in range(0x206,0x210)]+[(0x2ff,0x800,0)]
regs=[x.UC_X86_REG_EAX,x.UC_X86_REG_EBX,x.UC_X86_REG_ECX,x.UC_X86_REG_EDX,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI,x.UC_X86_REG_EBP]
try:
 for name in ['original374','candidate541']:
  p=Path('E:/xwn374/build001/image-crom.bin') if name=='original374' else Path(q['images']['1']['path'])
  assert sha(p)==('49f1332526c4155bd16bc2d16d138d7cb67f8498c80bc19ad0b64cd4ab671301' if name=='original374' else q['images']['1']['sha256'])
  payload=p.read_bytes() if name=='original374' else p.read_bytes()[0x3000:0x3000+524862]
  for flags in (2,0x202,0x402):
   u=unicorn.Uc(unicorn.UC_ARCH_X86,unicorn.UC_MODE_32)
   u.mem_map(0x2600000,0x100000);u.mem_write(0x2600000,payload)
   u.mem_map(0xaf000,0x7000);u.mem_write(0xaf000,b'\xa5'*0x7000)
   u.mem_write(0x264663c,b'\xa5'*0x18a0c)
   before_left=bytes(u.mem_read(0x2646638,4));before_right=bytes(u.mem_read(0x265f048,4))
   for i,reg in enumerate(regs):u.reg_write(reg,0x11110000+i*0x101)
   u.reg_write(x.UC_X86_REG_EFLAGS,flags);u.reg_write(x.UC_X86_REG_ESP,0xdead0000)
   row=dict(image=name,initial_flags=flags,endpoint=None,msrs=[],cr3_writes=[],wbinvd=0,clts=0,idt=None,writes=0)
   model={'cr3':0};bad=[]
   def write(uc,access,address,size,value,_):
    legal=(0x264663c<=address and address+size<=0x265f048) or (0xb0000<=address and address+size<=0xb5000)
    if not legal:
     bad.append(dict(address=address,size=size));uc.emu_stop();return
    assert size==4 and value==0;row['writes']+=1
   def code(uc,address,size,_):
    if address==0x2600200:row['endpoint']='before-C-detour';uc.emu_stop();return
    assert 0x26000f0<=address<0x2600200,hex(address)
    ins=next(md.disasm(bytes(uc.mem_read(address,size)),address));op=ins.op_str;m=ins.mnemonic
    modeled=False
    if m=='wrmsr':
     row['msrs'].append((uc.reg_read(x.UC_X86_REG_ECX),uc.reg_read(x.UC_X86_REG_EAX),uc.reg_read(x.UC_X86_REG_EDX)));modeled=True
    elif m=='wbinvd':row['wbinvd']+=1;modeled=True
    elif m=='clts':row['clts']+=1;modeled=True
    elif m=='lidt':
     assert op=='[0x2600080]';row['idt']=struct.unpack('<HI',uc.mem_read(0x2600080,6));modeled=True
    elif m=='mov' and op=='eax, cr3':uc.reg_write(x.UC_X86_REG_EAX,model['cr3']);modeled=True
    elif m=='mov' and op=='cr3, eax':
     model['cr3']=uc.reg_read(x.UC_X86_REG_EAX);row['cr3_writes'].append(model['cr3']);modeled=True
    if modeled:uc.reg_write(x.UC_X86_REG_EIP,address+size)
   u.hook_add(unicorn.UC_HOOK_MEM_WRITE,write);u.hook_add(unicorn.UC_HOOK_CODE,code)
   u.emu_start(0x26000f0,0xdeadbeef,timeout=8_000_000,count=100_000)
   if flags&0x400:
    assert bad==[dict(address=0x2646638,size=4)] and row['endpoint'] is None
    row['negative_result']='DF-set model caught first backward write outside BSS; no hardware state changed'
   else:
    assert not bad and row['endpoint']=='before-C-detour'
    assert row['writes']==0x6283+0x1400 and row['msrs']==expected_msrs
    assert row['cr3_writes']==[0,0x800] and row['wbinvd']==2 and row['clts']==1 and row['idt']==(2048,0xb0000)
    assert bytes(u.mem_read(0x264663c,0x18a0c))==bytes(0x18a0c)
    assert bytes(u.mem_read(0xb0000,0x5000))==bytes(0x5000)
    assert bytes(u.mem_read(0x2646638,4))==before_left and bytes(u.mem_read(0x265f048,4))==before_right
    assert bytes(u.mem_read(0xafffc,4))==b'\xa5'*4 and bytes(u.mem_read(0xb5000,4))==b'\xa5'*4
    row['final_gprs']=[u.reg_read(reg) for reg in regs]
    assert row['final_gprs']==[0x800,0x11110101,0x2ff,0,0x11110404,0xb5000,0x11110606]
    assert u.reg_read(x.UC_X86_REG_ESP)==0x2800000
    assert u.reg_read(x.UC_X86_REG_EFLAGS)==(flags|0x44)
   cases.append(row);save()
 r.update(status='passed',case_count=len(cases),source_sha256=sha(Path(__file__)),
  utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),unicorn_version=unicorn.__version__,capstone_version=capstone.__version__)
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:save()
print(json.dumps(dict(status=r['status'],cases=len(cases))))
