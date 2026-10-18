# SPDX-License-Identifier: MIT
"""Run real first-C/heap/IDT bytes and candidate marker in a bounded flat model."""
import datetime,hashlib,json,re,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'))
import capstone,unicorn
from unicorn import x86_const as x
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
q=read(K/'prepared001.json');md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
out=K/'c-host001.json';assert not out.exists()
cases=[];r=dict(status='running',cases=cases,physical_access=False,
 scope='Actual C prologue, memcpy, heap/IDT generation, stack and marker bytes. APIC MSR, PIC/SMBus ports and TSC explicitly modeled; no physical interrupt/cache/mapping proof.')
def save():out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
save()
mp=Path('E:/xwn374/build001/image-crom.map');assert sha(mp)=='fcf5aec3505d0177f0725931d85e6108c716b355eee7eb0a69bf6941b9eb41f2'
symbols={name:int(addr,16) for addr,name in re.findall(r'^\s+(0x[0-9a-f]+)\s+(\w+)\s*$',mp.read_text(),re.M)}
names=[f'IntHandlerException{i:X}' for i in range(17)]+['IntHandlerTimer0']+[f'IntHandler{i}' for i in range(1,8)]+['IntHandler8','IntHandler9','IntHandler10','IntHandlerI2C','IntHandlerSmc','IntHandler13','IntHandlerIde','IntHandler15']
vectors=list(range(17))+list(range(0x20,0x28))+list(range(0x70,0x78));assert len(names)==len(vectors)==33
handlers=dict(zip(vectors,[symbols[n] for n in names]))
expected_idt=b''.join(struct.pack('<HHHH',handlers.get(i,symbols['IntHandlerUnused'])&65535,0x10,0x8e00,handlers.get(i,symbols['IntHandlerUnused'])>>16) for i in range(256))
ranges=[(0x2600420,0x26004fd),(0x260efe0,0x260f007),(0x260f3a0,0x260f3c5),(0x260f9b0,0x260fafa),(0x260f6c0,0x260f6cd),(0x2625fc6,0x2625fce),(0x2680000,0x268023e)]
regs=[x.UC_X86_REG_EAX,x.UC_X86_REG_EBX,x.UC_X86_REG_ECX,x.UC_X86_REG_EDX,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI,x.UC_X86_REG_EBP]
try:
 for name in ('original374','candidate542'):
  p=Path('E:/xwn374/build001/image-crom.bin') if name=='original374' else Path(q['images']['1']['path'])
  assert sha(p)==('49f1332526c4155bd16bc2d16d138d7cb67f8498c80bc19ad0b64cd4ab671301' if name=='original374' else q['images']['1']['sha256'])
  payload=p.read_bytes() if name=='original374' else p.read_bytes()[0x3000:0x3000+524862]
  for config,apic,negative in [(0,0xfee00900,None),(1,0xfee00900,None),(0,0xfee00100,None),(1,0xfee00100,None),(0,0xfee00900,'missing-heap'),(0,0xfee00900,'DF-set')]:
   u=unicorn.Uc(unicorn.UC_ARCH_X86,unicorn.UC_MODE_32)
   u.mem_map(0x2600000,0x100000);u.mem_write(0x2600000,payload)
   u.mem_map(0xaf000,0x3000);u.mem_write(0xaf000,b'\xa5'*0x3000)
   u.mem_map(0x27fc000,0x4000);u.mem_write(0x27fc000,b'\xa5'*0x4000)
   if negative!='missing-heap':u.mem_map(0x15ff000,0x6000);u.mem_write(0x15ff000,b'\xa5'*0x6000)
   u.mem_write(0x264663c,bytes(0x18a0c));u.mem_write(0x2600020,struct.pack('<4I',config,2,3,4))
   for i,reg in enumerate(regs):u.reg_write(reg,0x11110000+i*0x101)
   u.reg_write(x.UC_X86_REG_ESP,0x2800000);u.reg_write(x.UC_X86_REG_EFLAGS,0x402 if negative=='DF-set' else 2)
   row=dict(image=name,config=config,apic_input=apic,negative=negative,endpoint=None,port_writes=[],msr_reads=[],msr_writes=[],writes=0,min_esp=0x2800000,marker_started=False)
   state={'status':0,'tsc':1000};bad=[];frame={}
   def mem_write(uc,access,address,size,value,_):
    valid=any(lo<=address and address+size<=hi for lo,hi in [(0x264663c,0x265f048),(0xb0000,0xb0800),(0x1600000,0x1604000),(0x27fc000,0x2800000),(0x2680028,0x2680088)])
    if not valid:bad.append(dict(address=address,size=size));uc.emu_stop();return
    if row['marker_started'] and 0x27fc000<=address<0x2800000:assert address+size<=frame['esp']
    row['writes']+=1
   def code(uc,address,size,_):
    assert any(lo<=address<hi for lo,hi in ranges),hex(address)
    row['min_esp']=min(row['min_esp'],uc.reg_read(x.UC_X86_REG_ESP))
    if address==0x26004f8:
     frame.update(esp=uc.reg_read(x.UC_X86_REG_ESP),gprs=[uc.reg_read(reg) for reg in regs],flags=uc.reg_read(x.UC_X86_REG_EFLAGS))
     frame['bytes']=bytes(uc.mem_read(frame['esp'],0x2800000-frame['esp']))
     assert frame['esp']==0x27fdf84
     if name=='original374':row['endpoint']='before-PCI';uc.emu_stop();return
     row['marker_started']=True
    if address==0x2680020:row['endpoint']='late-marker-before-HLT';uc.emu_stop();return
    assert address!=0x2680024,'unexpected marker failure'
    ins=next(md.disasm(bytes(uc.mem_read(address,size)),address));m=ins.mnemonic;op=ins.op_str;modeled=False
    if m=='rdmsr':
     assert uc.reg_read(x.UC_X86_REG_ECX)==0x1b;row['msr_reads'].append(0x1b)
     uc.reg_write(x.UC_X86_REG_EAX,apic);uc.reg_write(x.UC_X86_REG_EDX,0);modeled=True
    elif m=='wrmsr':
     row['msr_writes'].append([uc.reg_read(x.UC_X86_REG_ECX),uc.reg_read(x.UC_X86_REG_EAX),uc.reg_read(x.UC_X86_REG_EDX)]);modeled=True
    elif m=='rdtsc':
     assert row['marker_started'];state['tsc']+=10;uc.reg_write(x.UC_X86_REG_EAX,state['tsc']);uc.reg_write(x.UC_X86_REG_EDX,0);modeled=True
    elif m=='in':
     assert row['marker_started'] and op=='ax, dx' and uc.reg_read(x.UC_X86_REG_EDX)&65535==0xc000
     uc.reg_write(x.UC_X86_REG_EAX,(uc.reg_read(x.UC_X86_REG_EAX)&0xffff0000)|state['status']);modeled=True
    elif m=='out':
     port=(uc.reg_read(x.UC_X86_REG_EDX)&65535) if op.startswith('dx,') else int(op.split(',')[0],16)
     width=16 if op.endswith(' ax') else 8;value=uc.reg_read(x.UC_X86_REG_EAX)&((1<<width)-1)
     assert port in ([0xc000,0xc002,0xc004,0xc006,0xc008] if row['marker_started'] else [0x20,0x21,0xa0,0xa1])
     row['port_writes'].append([port,value])
     if port==0xc002:assert value==0x1a;state['status']=0x10
     if port==0xc000:assert value==0x10;state['status']=0
     modeled=True
    if modeled:uc.reg_write(x.UC_X86_REG_EIP,address+size)
   u.hook_add(unicorn.UC_HOOK_MEM_WRITE,mem_write);u.hook_add(unicorn.UC_HOOK_CODE,code)
   error=None
   try:u.emu_start(0x2600420,0xdeadbeef,timeout=8_000_000,count=150_000)
   except unicorn.UcError as e:error=e.errno
   if negative:
    assert row['endpoint'] is None
    if negative=='missing-heap':assert error==unicorn.UC_ERR_WRITE_UNMAPPED
    else:assert bad==[dict(address=0x15fffff,size=1)] and error is None
    row['expected_negative_detected']=True
   else:
    assert not bad and error is None
    assert row['endpoint']==('before-PCI' if name=='original374' else 'late-marker-before-HLT')
    assert bytes(u.mem_read(0xb0000,2048))==expected_idt
    assert bytes(u.mem_read(0x1600000,0x4000))==b'\xff'+bytes(0x3fff)
    assert bytes(u.mem_read(0x15ffffc,4))==b'\xa5'*4 and bytes(u.mem_read(0x1604000,4))==b'\xa5'*4
    assert bytes(u.mem_read(0xafffc,4))==b'\xa5'*4 and bytes(u.mem_read(0xb0800,4))==b'\xa5'*4
    assert struct.unpack('<I',u.mem_read(0x264697c,4))[0]==0x1600000
    assert row['msr_reads']==[0x1b] and row['msr_writes']==[[0x1b,apic&~0x800,0]]
    pic=[[0x20,0x15],[0x21,0x20],[0x21,4],[0x21,1],[0x21,0],[0xa0,0x15],[0xa1,0x70],[0xa1,2],[0xa1,1],[0xa1,0 if config==1 else 0xaf]]
    assert row['port_writes'][:10]==pic
    assert bytes(u.mem_read(frame['esp'],len(frame['bytes'])))==frame['bytes']
    assert u.reg_read(x.UC_X86_REG_ESP)==frame['esp'] and [u.reg_read(reg) for reg in regs]==frame['gprs']
    assert u.reg_read(x.UC_X86_REG_EFLAGS)==frame['flags']&~0x200
    if name=='candidate542':
     words=struct.unpack('<24I',u.mem_read(0x2680028,96));assert words[5:7]==(1,2)
     assert len(row['port_writes'])==19 and [v for p,v in row['port_writes'][10:] if p==0xc006]==[0xf5,1]
    else:assert len(row['port_writes'])==10
    row.update(checkpoint_esp=frame['esp'],checkpoint_flags=frame['flags'],C_frame_preserved=True,heap_and_all256_gates_match_independent_spec=True)
   cases.append(row);save()
 r.update(status='passed',case_count=len(cases),source_sha256=sha(Path(__file__)),utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),map_sha256=sha(mp),unicorn_version=unicorn.__version__)
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:save()
print(json.dumps(dict(status=r['status'],cases=len(cases))))
