"""Read-only cold report and complete allocation audit of the owned smoke child."""
import hashlib,json,pathlib,struct,subprocess,sys
K=pathlib.Path(__file__).resolve().parent;W=K.parent.parent
sys.path[:0]=[str(W/'outputs/fatx-mapped-eof'),str(W/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
from coldio import ColdIO
from bulk_fatx import Writer
import fatx_stage_boot as fatx
root=pathlib.Path('/mnt/e/xwn417/emu001')
assert json.loads((K/'closure001.json').read_text(encoding='utf-8-sig'))['closed']
assert not (K/'smoke001.json').exists()
r={'physical_access':False,'read_only':True,'checks':{}}
def sha(b):return hashlib.sha256(b).hexdigest()
try:
 for n in ['base.qcow2','hdd.qcow2']:
  p=subprocess.run(['qemu-img','check','--output=json',str(root/n)],capture_output=True,text=True,timeout=60)
  r['checks'][n]={'code':p.returncode,'stdout':p.stdout};assert p.returncode==0
 fatx.PARTITIONS['E']=(5633024*512,10000048*512)
 with ColdIO(root/'base.qcow2') as a,ColdIO(root/'hdd.qcow2') as b:
  before=Writer(a,fatx.open_partition(a,root/'base.qcow2','E'))
  after=Writer(b,fatx.open_partition(b,root/'hdd.qcow2','E'))
  prior=before.directory(1)['entries'];current=after.directory(1)['entries']
  r['root_before']=sorted(prior);r['root_after']=sorted(current)
  data=after.read('xwn-report-00.json');r['report']=json.loads(data)
  (K/'emulator-hardware-report.json').write_bytes(data)
  r['report_sha256']=sha(data);r['report_bytes']=len(data)
  assert set(current)==set(prior)|{'xwn-report-00.json'}
  todo=[(1,'')];used=set();files={};dirs=[]
  while todo:
   start,path=todo.pop();d=after.directory(start)
   chain=set(d['chain']);assert not used&chain;used|=chain;dirs.append(path)
   for name,(_,_,e) in d['entries'].items():
    p=path+'/'+name;cl,size=struct.unpack_from('<II',e,44)
    if e[1]&16:todo.append((cl,p))
    else:
     chain=set(after.chain(cl)) if cl else set();assert not chain&used;used|=chain
     assert len(chain)*after.p.cluster_size>=size
     files[p]=sha(after.read(p))
  allocated={i for i in range(1,after.limit) if after.fat[i]}
  assert allocated==used,('allocation mismatch',len(allocated-used),len(used-allocated))
  r['allocation']={'directories':len(dirs),'files':len(files),'owned_clusters':len(used),'orphans':0,'errors':0}
  for p,h in files.items():
   if p!='/xwn-report-00.json':assert sha(before.read(p))==h
  mapping=json.loads(subprocess.check_output(['qemu-img','map','--output=json',str(root/'hdd.qcow2')]))
  last=0;outside=[]
  for e in mapping:
   assert e['start']==last;last+=e['length']
   if e['depth']!=0:continue
   for start in range(e['start'],e['start']+e['length'],65536):
    n=min(65536,e['start']+e['length']-start);a.seek(start);b.seek(start);x=a.read(n);y=b.read(n)
    outside.extend(start+i for i,(u,v) in enumerate(zip(x,y)) if u!=v and not 5633024*512<=start+i<(5633024+10000048)*512)
  assert last==8589934592
  r['changed_offsets_outside_E']=outside
  r['only_E_changed']=not outside
 r['eeprom_unchanged']=sha((root/'eeprom.bin').read_bytes())==json.loads((K/'prepared001.json').read_text())['inputs']['eeprom.bin']['sha256']
 r['report_scope_passed']=True
except Exception as e:
 r['error']=repr(e);r['report_scope_passed']=False
finally:
 (K/'smoke001.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
assert r['report_scope_passed']
