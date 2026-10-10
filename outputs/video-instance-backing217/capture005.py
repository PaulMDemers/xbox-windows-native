"""One bounded resident Xbox kernel read at dashboard; never invoke its allocator."""
import datetime,ftplib,hashlib,json,os,socket,struct,sys,time
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/instance217-runs/nt5-instance217-map005')
dest=k/'capture005.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs=json.loads((k/'inputs.json').read_text())
for n,h in inputs['inputs'].items():assert sha(Path(n) if Path(n).is_absolute() else ws/n)==h,n
assert sha(Path(inputs['parent']))==inputs['parent_sha256']
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists()
sys.path.insert(0,str(ws/'outputs/native-windows-prebuild'))
from monitor_capture import command,acquire_monitor_lock

class Reader:
 def __init__(self):self.s=socket.create_connection(('127.0.0.1',4595),timeout=5);self.s.settimeout(5)
 def recv(self):
  while True:
   c=self.s.recv(1)
   if not c:raise EOFError()
   if c!=b'$':continue
   b=bytearray()
   while True:
    c=self.s.recv(1)
    if not c:raise EOFError()
    if c==b'#':break
    b+=c
   h=self.s.recv(2);assert len(h)==2 and int(h,16)==sum(b)%256
   self.s.sendall(b'+');return b.decode('ascii')
 def ask(self,text):
  b=text.encode('ascii');self.s.sendall(b'$'+b+b'#'+f'{sum(b)%256:02x}'.encode());return self.recv()
 def interrupt(self):self.s.sendall(b'\x03');return self.recv()
 def read(self,a,n,allow_unmapped=False):
  assert 0x80010000<=a and a+n<=0x80410000 and 0<n<=4096
  answer=self.ask(f'm{a:x},{n:x}')
  if answer.startswith('E') and allow_unmapped:return None,answer
  assert not answer.startswith('E'),answer
  data=bytes.fromhex(answer);assert len(data)==n;return data

r=dict(source_sha256=sha(Path(__file__)),physical_access=False,debugger=True,ordinary_qualified=False,
 nt5_launched=False,allocator_invoked=False,gpu_writes=False,breakpoints_installed=0,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),passed=False)
g=None;stopped=False;lock=None
try:
 time.sleep(25)
 r['dashboard_ftp_ready']=False;r['ftp_not_required_for_static_kernel_capture']=True
 lock=acquire_monitor_lock(4594);command(4594,'stop');stopped=True;g=Reader();r['features']=g.ask('qSupported');r['stop_reply']=g.ask('?');assert r['stop_reply'].startswith(('T','S'))
 r['registers']=command(4594,'info registers')
 base=0x80010000;header=g.read(base,4096);assert header[:2]==b'MZ'
 pe=struct.unpack_from('<I',header,0x3c)[0];assert pe<1024 and header[pe:pe+4]==b'PE\0\0'
 opt=pe+24;assert struct.unpack_from('<H',header,opt)[0]==0x10b
 size=struct.unpack_from('<I',header,opt+56)[0];assert 4096<=size<=4*1024*1024
 prior=json.loads((k/'capture004.json').read_text());assert size==prior['kernel_size']
 window=g.read(prior['claim_address'],1024);assert hashlib.sha256(window).hexdigest()==prior['claim_window_sha256']
 current_size=struct.unpack('<I',g.read(0x800360d0,4))[0];assert current_size==0x5000
 import re
 text=r['registers'];cr3=int(re.search(r'CR3=([0-9a-fA-F]+)',text).group(1),16)
 assert cr3&0xfff==0 and cr3<0x4000000
 def phys32(address):
  assert address&3==0 and 0<=address<=0x4000000-4
  answer=command(4594,f'xp /1wx 0x{address:x}')
  match=re.search(r'(?:0x)?[0-9a-fA-F]{8,16}:\s+0x([0-9a-fA-F]{8})',answer);assert match,answer
  return int(match.group(1),16),answer
 walks=[]
 for va in [0x83feb000,0x83feffff,0x83ff0000,0x83ffffff]:
  pde_address=cr3+4*(va>>22);pde,raw=phys32(pde_address);assert pde&1
  row=dict(virtual=va,cr3=cr3,pde_address=pde_address,pde=pde,pde_raw=raw)
  if pde&128:
   assert 'CR4=00000610' in text
   physical=(pde&0xffc00000)+(va&0x3fffff);row['large_page']=True
  else:
   address=(pde&0xfffff000)+4*((va>>12)&1023);pte,pte_raw=phys32(address);assert pte&1
   physical=(pte&0xfffff000)+(va&4095);row.update(large_page=False,pte_address=address,pte=pte,pte_raw=pte_raw)
  assert physical<0x4000000
  row['physical']=physical;row['direct_alias_matches']=physical==va-0x80000000;walks.append(row)
 assert all(v['direct_alias_matches'] for v in walks)
 r.update(passed=True,reference_capture_sha256=sha(k/'capture004.json'),claim_window_sha256=hashlib.sha256(window).hexdigest(),global_claim_size=current_size,page_walks=walks,cpu_alias_proven=True,gpu_ramin_alias_proven=False,nt5_ownership_granted=False,instance_sha256=sha(run/'instance.json'))

except Exception as e:r['error']=repr(e);raise
finally:
 if g:g.s.close()
 if stopped:
  try:command(4594,'cont');r['resumed']=True
  except Exception as e:r['resume_error']=repr(e)
 if lock:lock.close()
 r['closed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
 (run/'capture-complete.signal').write_text('bounded dashboard capture closed\n')
print(json.dumps({n:r[n] for n in ['passed','cpu_alias_proven','global_claim_size','resumed']},indent=2))
