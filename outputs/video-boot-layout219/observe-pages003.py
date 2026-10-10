"""One read-only bounded page-table check of the owned candidate219 mapping."""
import datetime,hashlib,json,re,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'emu-candidate001';dest=out/'live-pages003.json';assert not dest.exists()
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/blayout219-runs/nt5-blayout219-candidate001')
sys.path.insert(0,str(ws/'outputs/native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
obs=read(out/'live-layout002.json');assert obs['passed'] and obs['closed'] and not (run/'cleanup.json').exists()
r=dict(scope=__doc__,source_sha256=sha(Path(__file__)),layout_observation_sha256=sha(out/'live-layout002.json'),instance_sha256=sha(run/'instance.json'),physical_access=False,cpu_stopped=False,guest_memory_mutated=False,passed=False)
lock=None
try:
 lock=acquire_monitor_lock(4594);assert not (run/'cleanup.json').exists();assert 'VM status: running' in command(4594,'info status')
 def words(address,count):
  assert 1<=count<=1024
  text=command(4594,'x /%dwx 0x%x'%(count,address));values=[]
  for line in text.replace('\r','').splitlines():
   match=re.match(r'^(?:0x)?[0-9a-fA-F]+:\s+((?:0x[0-9a-fA-F]{8}\s*)+)',line)
   if match:values+=list(map(lambda v:int(v,16),re.findall(r'0x([0-9a-fA-F]{8})',match.group(1))))
  assert len(values)==count,(address,count,text[-200:]);return values
 def registers():
  text=command(4594,'info registers');return {n:int(re.search(n+r'=([0-9a-fA-F]+)',text).group(1),16) for n in ['CR0','CR3','CR4']}
 before=registers();assert before['CR0']&0x80000000 and not before['CR4']&0x20
 frame=obs['cells']['_FrameBufferStart'];assert frame%4096==0
 groups=[];i=0
 while i<1024:
  va=frame+i*4096;index=va>>22;n=min(1024-i,1024-((va>>12)&1023));pdeaddr=0xc0300000+index*4;pde=words(pdeaddr,1)[0];assert pde&1 and not pde&128
  address=0xc0000000+(va>>12)*4;a=words(address,n);b=words(address,n);assert a==b and words(pdeaddr,1)[0]==pde
  for j,pte in enumerate(a):assert pte&1 and pte&16 and (pte&0xfffff000)==0x03c00000+(i+j)*4096,(i+j,hex(pte))
  groups.append(dict(first_page=i,pages=n,virtual=va,pde_address=pdeaddr,pde=pde,pte_address=address,ptes=a,second_read_equal=True));i+=n
 after=registers();assert after['CR0']&0x80000000 and not after['CR4']&0x20;assert 'VM status: running' in command(4594,'info status') and not (run/'cleanup.json').exists()
 r.update(passed=True,groups=groups,pages=1024,physical_start=0x03c00000,mapped_bytes=0x400000,physical_end=0x04000000,protected_start=0x03feb000,hidden_physical=0x03c00000+obs['hidden_offset'],before_registers=before,after_registers=after)
except Exception as exc:r['error']=repr(exc)
finally:
 if lock:lock.close()
 r.update(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),limits='Stable mapping entries read twice with CPU running, raw present/PCD bits only. Does not establish effective PAT/MTRR type, a coherent all-entry instant, GPU alias or runtime guard preservation.')
 dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['passed','closed']}))
