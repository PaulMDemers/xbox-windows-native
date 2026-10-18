# SPDX-License-Identifier: MIT
"""Execute exact entry prefixes with explicit modeled allocation APIs only."""
from pathlib import Path
import datetime,hashlib,json,struct,sys
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn
from unicorn import x86_const as x
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
prepared=read(K/'prepared001.json');symbols=read(K.parent/'context-adapter490/build001.json')['wrapper_symbols']
out=K/'prefix-host002.json';assert not out.exists()
images={'ordinary':Path('E:/xwn374/build001/default.xbe'),'diagnostic':Path(prepared['images']['a']['path'])}
cases=[];record=dict(status='running',physical_access=False,kernel_memory_and_API_results='MODELED; no Xbox kernel executes',cases=cases)
def save():out.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
save()
try:
 for label,path in images.items():
  binary=path.read_bytes()
  for mode in ['normal','df-at-copy','null-kernel','null-loader','virtual-failure']:
   u=unicorn.Uc(unicorn.UC_ARCH_X86,unicorn.UC_MODE_32)
   u.mem_map(0x10000,(len(binary)+4095)&~4095);u.mem_write(0x10000,binary)
   u.mem_map(0x81f00000,0x100000);u.mem_map(0x82000000,0x1000)
   u.mem_map(0xd0000000,0x10000);u.reg_write(x.UC_X86_REG_ESP,0xd0008000)
   u.reg_write(x.UC_X86_REG_EFLAGS,0x202)
   u.mem_map(0x10000000,0x1000)
   for i in range(3):u.mem_write(0x11000+i*4,struct.pack('<I',0x10000000+i*16))
   row=dict(image=label,mode=mode,sha256=sha(binary),calls=[],boundary=None,invalid_memory=[],privileged_loader_executed=False)
   counts={'alloc':0,'phys':0}
   def code(uc,address,size,_):
    if label=='diagnostic' and address in (symbols['diag_verify'],symbols['diag_finish']):
     row['boundary']='prepared-before-diagnostics' if address==symbols['diag_verify'] else 'refused-before-report'
     row['phase']=struct.unpack('<I',uc.mem_read(symbols['diag_record']+20,4))[0];uc.emu_stop();return
    if address==0x2000000:
     assert bytes(uc.mem_read(address,1))==b'\xfa';row['boundary']='original-loader-before-cli';uc.emu_stop();return
    if address in (0x10000000,0x10000010,0x10000020):
     sp=uc.reg_read(x.UC_X86_REG_ESP);n=5 if address!=0x10000010 else 1
     stack=struct.unpack('<'+'I'*(n+1),uc.mem_read(sp,4*(n+1)));args=list(stack[1:])
     if address==0x10000000:
      counts['alloc']+=1;value=0x81f00000 if counts['alloc']==1 else 0x82000000
      if mode==('null-kernel' if counts['alloc']==1 else 'null-loader'):value=0
      name='MmAllocateContiguousMemoryEx'
     elif address==0x10000010:
      counts['phys']+=1;value=args[0]&0x7fffffff;name='MmGetPhysicalAddress'
      if mode=='df-at-copy' and counts['phys']==1:uc.reg_write(x.UC_X86_REG_EFLAGS,uc.reg_read(x.UC_X86_REG_EFLAGS)|0x400)
     else:
      name='NtAllocateVirtualMemory';value=0xc0000017 if mode=='virtual-failure' else 0
      low=struct.unpack('<I',uc.mem_read(args[0],4))[0]
      if value==0 and low:u.mem_map(low,4096)
     call=dict(api=name,args=args,result=value)
     if name=='NtAllocateVirtualMemory':
      assert all(0x11000 <= args[n] < 0x13000 for n in (0,2))
      call['pointed_values']=[struct.unpack('<I',uc.mem_read(args[n],4))[0] for n in (0,2)]
     row['calls'].append(call)
     uc.reg_write(x.UC_X86_REG_EAX,value);uc.reg_write(x.UC_X86_REG_ESP,sp+4*(n+1));uc.reg_write(x.UC_X86_REG_EIP,stack[0])
   def invalid(uc,access,address,size,value,_):
    row['invalid_memory'].append(dict(access=access,address=address,bytes=size));return False
   u.hook_add(unicorn.UC_HOOK_CODE,code);u.hook_add(unicorn.UC_HOOK_MEM_INVALID,invalid)
   try:u.emu_start(0x11100,0xdeadbeef,timeout=10_000_000,count=2_000_000)
   except unicorn.UcError as e:
    assert row['invalid_memory'],str(e);row['boundary']='unmapped-access';row['unicorn_error']=str(e)
   assert row['boundary'] is not None,'Host execution bound reached without observed endpoint'
   if mode=='normal':
    assert row['boundary']==('original-loader-before-cli' if label=='ordinary' else 'prepared-before-diagnostics')
    assert len(row['calls'])==5
    n=struct.unpack_from('<I',binary,0x1084)[0];assert bytes(u.mem_read(0x81f00000,n))==binary[0x3000:0x3000+n]
    row['copied_payload_bytes']=n
   elif label=='ordinary':assert row['boundary']=='unmapped-access'
   else:assert row['boundary']=='refused-before-report' and row['phase']=={'null-kernel':1,'null-loader':2,'virtual-failure':3,'df-at-copy':5}[mode]
   cases.append(row);save()
 normal=[r for r in cases if r['mode']=='normal'];a,b=[r['calls'] for r in normal]
 assert a[:4]==b[:4]
 assert a[4]['api']==b[4]['api'] and a[4]['result']==b[4]['result']
 assert [a[4]['args'][i] for i in (1,3,4)]==[b[4]['args'][i] for i in (1,3,4)]
 assert a[4]['pointed_values']==b[4]['pointed_values']==[0x2000000,4096]
 record.update(status='passed',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),cases_count=len(cases),normal_allocation_requests_equivalent_after_pointer_dereference=True,
  scope='Actual unmodified prefix instructions; address space, allocations, API returns and DF injection modeled. No proof that any injected failure happened on Xbox. Stops before file IO, LED marker, CLI or paging transition.',unicorn_version=unicorn.__version__,source_sha256=sha(Path(__file__).read_bytes()))
except BaseException as e:record.update(status='failed',error=repr(e));raise
finally:save()
print(json.dumps({n:record[n] for n in ['status','cases_count','normal_allocation_requests_equivalent_after_pointer_dereference']}))
