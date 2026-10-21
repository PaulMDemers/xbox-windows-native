"""One cold readback of634 after owned host closure; no runtime restart."""
import hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/c/xwn634/emu001');A=P/'cold001'
assert not A.exists() and not (K/'audit001.json').exists()
closure=json.loads((K/'closure001.json').read_text(encoding='utf-8-sig'));assert closure['closed']
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,hive,STARTUP
sys.path.insert(0,str(W/'outputs/demo-runtime377'));from stock_io002 import scan
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
prep=json.loads((K/'preparation001.json').read_text());rt=json.loads((K/'runtime001.json').read_text());obs=json.loads((K/'observation001.json').read_text())
A.mkdir();r=dict(physical_access=False,closed=True,host=closure,stop_reason=obs.get('stop_reason'),probe_present=False,protected=[],hives=[],new_events={},history_preserved=True)
def save():(K/'audit001.json').write_text(json.dumps(r,indent=2)+'\n')
try:
 for name,h in rt['parents'].items():assert sha(Path(name.replace('C:\\','/mnt/c/').replace('\\','/')))==h
 r['parents_unchanged']=True
 with ColdIO(P/'hdd.qcow2') as io:
  wr=m.Writer(io,m.fatx.open_partition(io,P/'hdd.qcow2','E'))
  try:log=wr.read('xwn480p634/result.txt')
  except KeyError:log=None
  if log is not None:
   (A/'result.txt').write_bytes(log);r['probe_present']=True;r['probe_log']=log.decode('ascii','backslashreplace')
  for name,h in prep['protected'].items():
   data=wr.read(name);actual=m.sha(data)
   if name.endswith('xwn-video-trace.bin'):(A/'video-trace.bin').write_bytes(data);r['trace_sha256']=actual
   else:r['protected'].append(dict(path=name,expected=h,actual=actual,matched=h==actual))
  for row in prep['changes']:r['protected'].append(dict(path=row['path'],expected=row['sha256'],actual=m.sha(wr.read(row['path'])),matched=m.sha(wr.read(row['path']))==row['sha256']))
  for name in ['system','software','default','sam','security']:
   f=A/name;f.write_bytes(wr.read('winnt/system32/config/'+name))
   try:parsed=hive(f)
   except Exception as e:parsed=dict(parsed=False,error=repr(e))
   r['hives'].append(dict(name=name,**parsed))
  for name in ['SysEvent.Evt','AppEvent.Evt']:(A/name).write_bytes(wr.read('winnt/system32/config/'+name))
 for name,label in [('SysEvent.Evt','system'),('AppEvent.Evt','application')]:
  records=[]
  for phase,src in [('before',Path('/mnt/c/xwn634/preparation001/before')/name),('after',A/name)]:
   dest=A/(phase+'-'+label+'.json')
   subprocess.run([sys.executable,str(W/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(src),'--output',str(dest)],check=True,stdout=subprocess.DEVNULL)
   records.append(json.loads(dest.read_text())['records'])
  before,after=records;by={v['record']:v for v in after};r['history_preserved'] &= all(by.get(v['record'])==v for v in before)
  boundary=max((v['record'] for v in before),default=0);r['new_events'][label]=[v for v in after if v['record']>boundary]
 r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
 r['warnings_errors']=[v for group in r['new_events'].values() for v in group if v['type'] in [1,2]]
 scan(P/'hdd.qcow2',A/'allocation/artifacts');alloc=json.loads((A/'allocation/allocation.json').read_text());r['allocation']=alloc
 r['qcow_check']=json.loads(subprocess.check_output(['qemu-img','check','--output=json',str(P/'hdd.qcow2')],timeout=30))
 from result_parser import analyze
 r['probe_analysis']=analyze(log)
 pairs=[]
 if log is not None:
  for line in log.decode('ascii').splitlines():key,value=line.split('=');pairs.append((key,int(value)))
  values=dict(pairs)
  expected={'case':634,'mode.width':720,'mode.height':480,'mode.bpp':32,'primary.width':720,'primary.height':480,'primary.pitch':2880,'primary.bpp':32,'pass0.mismatches':0,'pass1.mismatches':0,'pass2.mismatches':0,'failures':0,'complete':1,'restart.accepted':1}
  r['expected_fields']=expected;r['probe_passed']=r['probe_analysis']['passed'] and all(values.get(k)==v for k,v in expected.items())
 else:r['probe_passed']=False
 r['integrity_passed']=all(v['matched'] for v in r['protected']) and all(v['parsed'] for v in r['hives']) and r['history_preserved'] and alloc['allocation_consistent'] and not r['qcow_check'].get('corruptions',0)
 r['scoped_passed']=r['probe_passed'] and r['integrity_passed'] and r['normal_shutdown_count']==1 and not closure['fallback_kill'] and closure['host_exit']==0
 r['strict_passed']=r['scoped_passed'] and not r['warnings_errors']
 r['cold_collection_complete']=True;r['runtime_sha256']=sha(P/'hdd.qcow2')
except BaseException as e:r['audit_error']=repr(e);raise
finally:save()
print(json.dumps({k:r[k] for k in ['probe_present','probe_passed','normal_shutdown_count','integrity_passed','scoped_passed','strict_passed']}))
