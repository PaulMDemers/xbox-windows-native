"""Fresh bounded overlay of the immutable, never-executed466 Windows seed."""
import hashlib,json,os,subprocess,sys,struct
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/c/xwn636/preparation002')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not P.exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
space=require_space(P,20.1875) #192MiB projected staging/runtime/capture allowance
sys.path.insert(0,str(W/'work/python-packages'));import pefile
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,STARTUP
sys.path.insert(0,str(W/'outputs/fresh-assembly405'));from writeio001 import WriteIO
sys.path.insert(0,str(W/'outputs/demo-runtime377'));from stock_io002 import scan
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
S=Path('/mnt/c/xwn466/preparation001/seed.qcow2');old=json.loads((K/'seed-inventory001.json').read_text());assert old['never_executed'] and sha(S)==old['seed_sha256']
installed=json.loads((K/'installed-inputs001.json').read_text())['files']
for row in installed:assert sha(Path(row['source'].replace('E:', '/mnt/e').replace(chr(92),'/')))==row['sha256']
build=json.loads((K.parent/'windows480p635/build001.json').read_text());X=Path(build['output_linux']);assert build['compiled'] and not build['warnings'] and sha(X)==build['binary_sha256']
assert sha(K/'probe.c')==build['source_pins']['probe.c']
candidate=Path('/mnt/c/xwn633/build001/default.xbe');cr=json.loads((K.parent/'native480p633/final-review001.json').read_text());assert cr['native_initialization_passed'] and sha(candidate)==cr['xbe_sha256']
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
P.mkdir(parents=True);(P/'before').mkdir();out=K/'preparation002.json'
r=dict(prepared=False,physical_access=False,seed_never_executed=True,parent=str(S),parent_sha256=sha(S),space=space,changes=[],protected={},imports={},providers={})
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
def replace_existing(w,path,data):
 parent=1;parts=w.parts(path)
 for part in parts[:-1]:parent=struct.unpack_from('<I',w.directory(parent)['entries'][part.lower()][2],44)[0]
 dc,off,e=w.directory(parent)['entries'][parts[-1].lower()];chain=list(w.chain(struct.unpack_from('<I',e,44)[0]))
 assert len(chain)==(len(data)+w.p.cluster_size-1)//w.p.cluster_size,'Replacement must use exactly the existing allocation'
 before=m.sha(w.read(path))
 for i,c in enumerate(chain):w.write_cluster(c,data[i*w.p.cluster_size:(i+1)*w.p.cluster_size])
 b=bytearray(w.read_cluster(dc));struct.pack_into('<I',b,off+48,len(data));w.write_cluster(dc,b);w.dirs={};assert w.read(path)==data
 return dict(path=path,bytes=len(data),sha256=m.sha(data),previous_sha256=before,clusters=len(chain),existing_allocation_retained=True)

try:
 with ColdIO(S) as io:
  wr=m.Writer(io,m.fatx.open_partition(io,S,'E'));p=pefile.PE(str(X));assert p.FILE_HEADER.Machine==0x14c
  assert (p.OPTIONAL_HEADER.MajorSubsystemVersion,p.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
  for imp in p.DIRECTORY_ENTRY_IMPORT:
   name=imp.dll.decode().lower();assert name in ['kernel32.dll','user32.dll','advapi32.dll','gdi32.dll','ddraw.dll']
   data=wr.read('winnt/system32/'+name);dll=pefile.PE(data=data);exports={e.name for e in dll.DIRECTORY_ENTRY_EXPORT.symbols if e.name}
   assert all(e.name in exports for e in imp.imports),name
   r['imports'][name]=[e.name.decode() for e in imp.imports];r['providers'][name]=m.sha(data)
  for name,row in old['files'].items():
   if row['present']:
    data=wr.read(name);assert m.sha(data)==row['sha256'];r['protected'][name]=m.sha(data)
  for name in ['system','software','default','sam','security','SysEvent.Evt','AppEvent.Evt']:
   data=wr.read('winnt/system32/config/'+name);(P/'before'/name).write_bytes(data)
 subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b','../../xwn466/preparation001/seed.qcow2',str(P/'seed.qcow2')],check=True,timeout=30)
 with WriteIO(P/'seed.qcow2',10000000000,P) as io:
  wr=m.Writer(io,m.fatx.open_partition(io,P/'seed.qcow2','E'))
  hook=b'@echo off\r\nC:\\xwn480p635\\probe.exe\r\nexit\r\n'
  for name,data in [('xwn480p635/probe.exe',X.read_bytes()),(STARTUP,hook),('Applications/XWN480p635/default.xbe',candidate.read_bytes())]:r['changes'].append(wr.write(name,data))
  for row in installed:
   data=Path(row['source'].replace('E:', '/mnt/e').replace(chr(92),'/')).read_bytes()
   if wr.read(row['path'])!=data:r['changes'].append(replace_existing(wr,row['path'],data))
   r['protected'][row['path']]=row['sha256']
  r['installed_stack_inputs']=installed
  wr.flush();io.flush()
 with ColdIO(P/'seed.qcow2') as io:
  wr=m.Writer(io,m.fatx.open_partition(io,P/'seed.qcow2','E'))
  for row in r['changes']:assert m.sha(wr.read(row['path']))==row['sha256']
  for name,h in r['protected'].items():assert m.sha(wr.read(name))==h
  for name in ['system','software','default','sam','security']:assert wr.read('winnt/system32/config/'+name)==(P/'before'/name).read_bytes()
 scan(P/'seed.qcow2',P/'allocation-before/artifacts')
 alloc=json.loads((P/'allocation-before/allocation.json').read_text());assert alloc['allocation_consistent']
 (K/'allocation-before002.json').write_text(json.dumps(alloc,indent=2)+'\n')
 assert sha(S)==old['seed_sha256']
 q=json.loads(subprocess.check_output(['qemu-img','check','--output=json',str(P/'seed.qcow2')],timeout=30));assert not q.get('corruptions',0) and not q.get('leaks',0)
 r.update(prepared=True,seed=str(P/'seed.qcow2'),seed_sha256=sha(P/'seed.qcow2'),qcow=q,allocation_consistent=True,hives_unchanged=True,selected_installed_inputs_readback_exact=True,source_pins={p.name:sha(p) for p in K.glob('*.py')},probe_source_sha256=sha(K/'probe.c'))
except BaseException as e:r['error']=repr(e);raise
finally:save()
print('Fresh636 matched-stack seed prepared, no runtime launch')
