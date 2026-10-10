"""One bounded resident Xbox kernel read at dashboard; never invoke its allocator."""
import datetime,ftplib,hashlib,json,os,socket,struct,sys,time
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/instance217-runs/nt5-instance217-dashboard003')
dest=k/'capture003.json';assert not dest.exists()
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
 deadline=time.monotonic()+90
 while True:
  try:
   with ftplib.FTP() as ftp:
    ftp.connect('127.0.0.1',4596,timeout=2);ftp.login(os.environ['XWN_EMULATOR_FTP_USER'],os.environ['XWN_EMULATOR_FTP_PASSWORD']);ftp.voidcmd('NOOP')
   r['dashboard_ftp_ready']=True;break
  except ftplib.all_errors:
   assert time.monotonic()<deadline,'Dashboard readiness bound';time.sleep(1)
 lock=acquire_monitor_lock(4594);command(4594,'stop');stopped=True;g=Reader();r['features']=g.ask('qSupported');r['stop_reply']=g.ask('?');assert r['stop_reply'].startswith(('T','S'))
 r['registers']=command(4594,'info registers')
 base=0x80010000;header=g.read(base,4096);assert header[:2]==b'MZ'
 pe=struct.unpack_from('<I',header,0x3c)[0];assert pe<1024 and header[pe:pe+4]==b'PE\0\0'
 opt=pe+24;assert struct.unpack_from('<H',header,opt)[0]==0x10b
 size=struct.unpack_from('<I',header,opt+56)[0];assert 4096<=size<=4*1024*1024
 data=bytearray();deadline=time.monotonic()+90;r['unmapped_pages']=[]
 for offset in range(0,size,4096):
  assert time.monotonic()<deadline,'Resident capture bound'
  n=min(4096,size-offset);page=g.read(base+offset,n,allow_unmapped=True)
  if isinstance(page,tuple):r['unmapped_pages'].append(dict(rva=offset,bytes=n,reply=page[1]));data+=bytes(n)
  else:data+=page
 assert data[:4096]==header
 art=k/'artifacts/dashboard003';art.mkdir(exist_ok=False);p=art/'kernel-resident.bin';p.write_bytes(data)
 export_rva,export_size=struct.unpack_from('<II',data,opt+96);assert 0<export_rva and export_rva+export_size<=size
 fields=struct.unpack_from('<IIHHIIIIIII',data,export_rva);ordinal_base,count,names,func_table=fields[5],fields[6],fields[7],fields[8]
 assert ordinal_base<=168<ordinal_base+count and count<1024 and func_table+count*4<=size
 rva=struct.unpack_from('<I',data,func_table+(168-ordinal_base)*4)[0];assert 0<rva<size and not export_rva<=rva<export_rva+export_size
 window=g.read(base+rva,min(1024,size-rva));assert window==bytes(data[rva:rva+len(window)])
 (art/'claim-window.bin').write_bytes(window)
 r.update(passed=True,kernel_base=base,kernel_size=size,kernel_resident_sha256=sha(p),ordinal_base=ordinal_base,export_count=count,export_names=names,claim_ordinal=168,claim_rva=rva,claim_address=base+rva,claim_window_sha256=hashlib.sha256(window).hexdigest(),instance_sha256=sha(run/'instance.json'))
except Exception as e:r['error']=repr(e);raise
finally:
 if g:g.s.close()
 if stopped:
  try:command(4594,'cont');r['resumed']=True
  except Exception as e:r['resume_error']=repr(e)
 if lock:lock.close()
 r['closed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
 (run/'capture-complete.signal').write_text('bounded dashboard capture closed\n')
print(json.dumps({n:r[n] for n in ['passed','kernel_size','claim_rva','claim_address','resumed']},indent=2))
