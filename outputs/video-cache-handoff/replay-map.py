"""Isolated actual NT5 code replay; modeled allocation/TLB helpers, no guest changes."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'))
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP
from walk import read_virtual,scan_directory,ranges
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
t=read(k/'trace002/trace.json');sites=read(k/'map-sites.json');mod=sites['modules']['ntoskrnl.exe'];binary=Path(mod['path']);assert sha(binary)==mod['sha256']
K=t['kernel_base'];p=pefile.PE(str(binary));p.relocate_image(K);image=p.get_memory_mapped_image();start=0x37d78;end=0x37f1a
snap=Path(t['early_snapshot']['path']);assert sha(snap)==t['early_snapshot']['sha256'];raw=snap.read_bytes();cr3=t['early_snapshot']['control_registers']['CR3']
code=read_virtual(raw,cr3,K+start,end-start);assert code==image[start:end]
early=scan_directory(raw,cr3);early_ranges=ranges(early['matches'])
observed=[dict(phase='bootvid',**t['mapping_calls'][0]['kernel_cache_globals']),dict(phase='desktop',**t['mapping_calls'][-1]['kernel_cache_globals'])]
assert observed[0]['MiWriteCombiningPtes']=='00' and observed[1]['MiWriteCombiningPtes']=='01'
for g in observed:
 assert g['KeFeatureBits']&0x400 and g['ValidKernelPte']==355
stack=0x10000000;stop=0x11000000;pt=0xc03e0000;cases=[]
for g in observed:
 for cache in [0,2]:
  u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(K,(len(image)+4095)&~4095);u.mem_write(K,image)
  u.mem_map(stack,0x10000);u.mem_map(stop,4096);u.mem_map(pt,8192)
  u.mem_write(K+0x73cfc,struct.pack('<I',g['KeFeatureBits']));u.mem_write(K+0x73d50,bytes.fromhex(g['MiWriteCombiningPtes']))
  u.mem_write(K+0x72eb0,struct.pack('<I',g['ValidKernelPte']));u.mem_write(K+0x73d44,bytes(4))
  calls=[]
  def hook(uc,address,size,user):
   helpers={K+0x6c1c0:('reserve',20,pt),K+0x6c6b0:('release',12,0),K+0x69098:('invalidate_caches',0,1),K+0x63d14:('flush_tlb',4,0)}
   if address not in helpers:return
   name,n,result=helpers[address];esp=uc.reg_read(UC_X86_REG_ESP);frame=bytes(uc.mem_read(esp,n+4));ret=struct.unpack_from('<I',frame)[0]
   calls.append(dict(helper=name,arguments=list(struct.unpack('<'+'I'*(n//4),frame[4:]))))
   if name=='reserve':assert calls[-1]['arguments']==[1024,0,0,0,0]
   if name=='release':assert calls[-1]['arguments']==[pt,1024,0]
   if name=='flush_tlb':assert calls[-1]['arguments']==[1]
   from unicorn.x86_const import UC_X86_REG_EIP
   uc.reg_write(UC_X86_REG_EAX,result);uc.reg_write(UC_X86_REG_ESP,esp+n+4);uc.reg_write(UC_X86_REG_EIP,ret)
  u.hook_add(UC_HOOK_CODE,hook);esp=stack+0xf000;u.mem_write(esp,struct.pack('<5I',stop,0x03c00000,0,0x400000,cache));u.reg_write(UC_X86_REG_ESP,esp)
  u.emu_start(K+start,stop,count=100000)
  from unicorn.x86_const import UC_X86_REG_EIP
  assert u.reg_read(UC_X86_REG_EIP)==stop and u.reg_read(UC_X86_REG_ESP)==esp+20
  result=u.reg_read(UC_X86_REG_EAX);entries=list(struct.unpack('<1024I',u.mem_read(pt,4096)));rejected=g['phase']=='bootvid' and cache==2
  if rejected:assert result==0 and not any(entries) and [c['helper'] for c in calls]==['reserve','release']
  else:
   flags=0x17b if cache==0 else 0x16b
   assert result==0xf8000000 and entries==[0x03c00000+i*4096+flags for i in range(1024)]
   assert [c['helper'] for c in calls]==(['reserve'] if cache==0 else ['reserve','invalidate_caches','flush_tlb'])
  cases.append(dict(phase=g['phase'],cache_argument=cache,returned=result,rejected=rejected,first_pte=entries[0],last_pte=entries[-1],modeled_helpers=calls))
dest=k/'map-replay.json';assert not dest.exists();dest.write_text(json.dumps(dict(passed=True,scope=__doc__,source_sha256=sha(Path(__file__)),kernel_sha256=mod['sha256'],trace_sha256=sha(k/'trace002/trace.json'),early_snapshot_sha256=sha(snap),resident_function_sha256=hashlib.sha256(code).hexdigest(),function_rva=start,function_bytes=end-start,early_current_root=dict(cr3=cr3,ranges=early_ranges,pdes=early['pdes_examined'],ptes=early['ptes_examined']),observed_globals=observed,cases=cases,limits='CPU instruction replay uses actual pinned resident NT5 code and observed globals but modeled allocation/cache/TLB helpers. No real guest WC request, cache transition or runtime speed claim. Early aliases cover only current CR3, not all active roots/TLBs.'),indent=2)+'\n')
print('Actual-code replay PASS:',len(cases),'cases; early aliases',early_ranges)
