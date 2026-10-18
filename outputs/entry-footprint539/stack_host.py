# SPDX-License-Identifier: MIT
"""Execute each actual five-byte entry path with bounded modeled SMBus/TSC."""
from pathlib import Path
import datetime,hashlib,json,struct,sys
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'))
import capstone,unicorn
from unicorn import x86_const as x
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
q=read(K/'prepared001.json');s=read(K.parent/'busy-handoff471/build001.json')['stub_symbols']
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
out=K/'stack-host001.json';assert not out.exists()
cases=[];r=dict(status='running',physical_access=False,SMBus_and_TSC='explicit host models, not actual device behavior',cases=cases)
def save():out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
save()
regs=[x.UC_X86_REG_EAX,x.UC_X86_REG_EBX,x.UC_X86_REG_ECX,x.UC_X86_REG_EDX,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI,x.UC_X86_REG_EBP]
try:
 for name in ('a','b'):
  image=Path(q['images'][name]['path']).read_bytes();assert sha(image)==q['images'][name]['sha256']
  payload=image[0x3000:0x3000+524862]
  for flags in [0x2,0x202,0x402,0x602]:
   for mode in ['complete','busy-then-complete','busy-budget','status-error','clock-deadline']:
    u=unicorn.Uc(unicorn.UC_ARCH_X86,unicorn.UC_MODE_32)
    u.mem_map(0x2600000,0x100000);u.mem_write(0x2600000,payload)
    u.mem_map(0x27ff000,4096);u.mem_write(0x27ff000,b'\xa5'*4096)
    for i,reg in enumerate(regs):u.reg_write(reg,0x11110000+i*0x101)
    u.reg_write(x.UC_X86_REG_ESP,0xdead0000);u.reg_write(x.UC_X86_REG_EFLAGS,flags)
    initial=[u.reg_read(reg) for reg in regs];initial_record=bytes(u.mem_read(s['after_stack_record'],96))
    row=dict(image=name,mode=mode,initial_flags=flags,endpoint=None,instructions=0,port_reads=0,port_writes=[],tsc_reads=0,device_io_real=False)
    state={'status':0,'busy':4 if mode=='busy-then-complete' else 0,'tsc':1000}
    def write(uc,access,address,size,value,_):
     assert 0x27ff000<=address and address+size<=0x2800000 or s['after_stack_record']<=address and address+size<=s['after_stack_record']+96,(hex(address),size)
    def code(uc,address,size,_):
     if address==0x26000f5:
      row['endpoint']='original-continuation';uc.emu_stop();return
     if address==s['after_stack_failed']:
      row['endpoint']='marker-failure-before-halt';uc.emu_stop();return
     row['instructions']+=1
     assert address==0x26000f0 or 0x2680000<=address<0x2680000+574,hex(address)
     ins=next(md.disasm(bytes(uc.mem_read(address,size)),address));m=ins.mnemonic
     if m=='rdtsc':
      row['tsc_reads']+=1;state['tsc']+=64000001 if mode=='clock-deadline' else 10
      uc.reg_write(x.UC_X86_REG_EAX,state['tsc']&0xffffffff);uc.reg_write(x.UC_X86_REG_EDX,state['tsc']>>32);uc.reg_write(x.UC_X86_REG_EIP,address+size)
     elif m=='in':
      port=uc.reg_read(x.UC_X86_REG_EDX)&65535;assert port==0xc000 and ins.op_str=='ax, dx'
      row['port_reads']+=1
      value=2 if mode=='status-error' else 8 if mode=='busy-budget' or state['busy'] else state['status']
      state['busy']=max(0,state['busy']-1)
      uc.reg_write(x.UC_X86_REG_EAX,(uc.reg_read(x.UC_X86_REG_EAX)&0xffff0000)|value);uc.reg_write(x.UC_X86_REG_EIP,address+size)
     elif m=='out':
      port=uc.reg_read(x.UC_X86_REG_EDX)&65535;assert port in [0xc000,0xc002,0xc004,0xc006,0xc008]
      value=uc.reg_read(x.UC_X86_REG_EAX)&(0xffff if ins.op_str.endswith('ax') else 0xff)
      row['port_writes'].append(dict(port=port,value=value))
      if port==0xc002:assert value==0x1a;state['status']=0x10
      if port==0xc000:assert value==0x10;state['status']=0
      uc.reg_write(x.UC_X86_REG_EIP,address+size)
    u.hook_add(unicorn.UC_HOOK_CODE,code);u.hook_add(unicorn.UC_HOOK_MEM_WRITE,write)
    u.emu_start(0x26000f0,0xdeadbeef,timeout=5_000_000,count=200_000)
    assert row['endpoint'] is not None,'bounded execution ended without endpoint'
    words=struct.unpack('<24I',u.mem_read(s['after_stack_record'],96));row['marker_result']=words[5];row['marker_transactions']=words[6]
    if name=='b':
     assert row['endpoint']=='original-continuation' and row['instructions']==1
     assert not row['port_reads'] and not row['port_writes'] and not row['tsc_reads']
     assert bytes(u.mem_read(s['after_stack_record'],96))==initial_record
     assert bytes(u.mem_read(0x27ff000,4096))==b'\xa5'*4096
    elif mode in ('complete','busy-then-complete'):
     assert row['endpoint']=='original-continuation' and words[5]==1 and words[6]==2
     assert len(row['port_writes'])==9
    else:
     assert row['endpoint']=='marker-failure-before-halt' and words[5]=={'busy-budget':3,'status-error':5,'clock-deadline':6}[mode]
     assert not row['port_writes']
    if row['endpoint']=='original-continuation':
     assert [u.reg_read(reg) for reg in regs]==initial
     assert u.reg_read(x.UC_X86_REG_EFLAGS)==flags
     assert u.reg_read(x.UC_X86_REG_ESP)==0x2800000
    cases.append(row);save()
 r.update(status='passed',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),case_count=len(cases),
    source_sha256=sha(Path(__file__).read_bytes()),unicorn_version=unicorn.__version__,capstone_version=capstone.__version__,
    scope='Exact candidate bytes at original stack-setup boundary only. Caller/paging/device/timing and complete physical boot remain unproved. Restored case executes no diagnostic or fabricated success record.')
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:save()
print(json.dumps({n:r[n] for n in ['status','case_count']}))
