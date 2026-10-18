"""Closed runtime only: full E graph, paired seed/runtime bytes, independent decode."""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];O=Path('/mnt/c/xwn528/cold001')
assert not O.exists() and not (K/'emu-audit001.json').exists();O.mkdir()
closure=json.loads((K/'closure001.json').read_text(encoding='utf-8-sig'));assert closure['closed']
sys.path[:0]=[str(K),str(W/'outputs/fatx-mapped-eof'),str(W/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
from coldio import ColdIO
from bulk_fatx import Writer
from entry_decode import decode
import fatx_stage_boot as fatx
fatx.PARTITIONS['E']=(5633024*512,10000048*512)
seed=Path('/mnt/c/xwn528/preparation001/seed.qcow2');child=Path('/mnt/c/xwn528/emu001/hdd.qcow2')
sha=lambda b:hashlib.sha256(b).hexdigest()
def walk(w):
 todo=[(1,'')];used=set();files={};dirs=[]
 while todo:
  start,path=todo.pop();d=w.directory(start);chain=set(d['chain'])
  assert not used&chain;used|=chain;dirs.append(path)
  for name,(_,_,e) in d['entries'].items():
   p=path+'/'+name;cl,size=struct.unpack_from('<II',e,44)
   if e[1]&16:todo.append((cl,p))
   else:
    chain=set(w.chain(cl)) if cl else set();assert not chain&used;used|=chain
    assert len(chain)*w.p.cluster_size>=size;files[p]=sha(w.read(p))
 allocated={i for i in range(1,w.limit) if w.fat[i]};assert allocated==used
 return dict(directories=sorted(dirs),files=files,owned_clusters=len(used),orphans=0,errors=0)
r=dict(passed=False,read_only=True,physical_access=False,closure=closure)
try:
 r['qcow']={}
 for p in [seed,child]:
  q=subprocess.run(['qemu-img','check','--output=json',str(p)],capture_output=True,text=True,timeout=60)
  r['qcow'][str(p)]=dict(code=q.returncode,output=q.stdout);assert q.returncode==0
 with ColdIO(seed) as a,ColdIO(child) as b:
  before=Writer(a,fatx.open_partition(a,seed,'E'));after=Writer(b,fatx.open_partition(b,child,'E'))
  r['before']=walk(before);r['after']=walk(after)
  receipts=['/applications/xwndispatch528/'+n for n in ['begin.bin','entry.bin']]
  r['receipt_present']={p:p in r['after']['files'] for p in receipts}
  assert all(r['receipt_present'].values()),'missing runtime receipt'
  assert r['after']['directories']==r['before']['directories']
  assert set(r['after']['files'])==set(r['before']['files'])|set(receipts)
  assert all(r['after']['files'][p]==h for p,h in r['before']['files'].items())
  r['decoded']=[]
  for stage,p in enumerate(receipts,1):
   data=after.read(p);(O/Path(p).name).write_bytes(data);r['decoded'].append(decode(data,stage))
  assert r['decoded'][0]['kernel']==r['decoded'][1]['kernel']
  mapping=json.loads(subprocess.check_output(['qemu-img','map','--output=json',str(child)],timeout=30));last=0;outside=[];changed=0
  for e in mapping:
   assert e['start']==last;last+=e['length']
   if e['depth']!=0:continue
   for start in range(e['start'],e['start']+e['length'],65536):
    n=min(65536,e['start']+e['length']-start);a.seek(start);b.seek(start);x=a.read(n);y=b.read(n);assert len(x)==n and len(y)==n
    for i,(u,v) in enumerate(zip(x,y)):
     if u!=v:
      changed+=1
      if not 5633024*512<=start+i<(5633024+10000048)*512:outside.append(start+i)
  assert last==8589934592
  r.update(changed_bytes=changed,changed_offsets_outside_E=outside,only_E_changed=not outside,whole_disk_equal=changed==0)
 prep=json.loads((K/'preparation001.json').read_text());assert sha(seed.read_bytes())==prep['seed_sha256']
 assert sha(Path(prep['base']).read_bytes())==prep['base_sha256']
 pins=json.loads((K/'runtime-prepared001.json').read_text())
 for n,v in pins['inputs'].items():
  src=v['source'].replace('\\','/');src='/mnt/'+src[0].lower()+src[2:]
  assert sha(Path(src).read_bytes())==v['sha256']
 r['private_eeprom_unchanged']=sha(Path('/mnt/c/xwn528/emu001/eeprom.bin').read_bytes())==pins['inputs']['eeprom.bin']['sha256']
 r.update(passed=True,source_seed_unchanged=True,source_inputs_unchanged=True,
          actual_runtime_entry=True,begin_pipeline_completed=True,entry_own_close_proved=False,
          normal_windows_restart=False,physical_qualification=False)
except BaseException as e:r['failure']=repr(e);raise
finally:(K/'emu-audit001.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:v for k,v in r.items() if k not in ['before','after','qcow']}))
