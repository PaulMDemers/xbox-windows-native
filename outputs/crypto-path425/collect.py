"""Cold FATX persistence audit, once per closed phase; no repair or verdict waiver."""
import argparse,ast,json,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
p=argparse.ArgumentParser();p.add_argument('--phase',type=int,choices=[1,2],required=True);a=p.parse_args();case=f'emu{a.phase:03d}';out=K/case;run=Path('/mnt/e/xwn425/runs')/('nt5-crypto425-'+case);P=Path('/mnt/e/xwn425')/('cold'+str(a.phase))
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,sha,HIVES,STARTUP
sys.path.insert(0,str(W/'outputs/install-validation406'));from oem_reader import OemReader
sys.path.insert(0,str(W/'outputs/release-readiness403'));from stock_io002 import scan
sys.path.insert(0,str(W/'work/python-packages'));sys.path.insert(0,str(W/'outputs/clean-media404'));from hive_audit004 import audit as hiveaudit
sys.path.insert(0,str(W/'outputs/crypto-persistence423'));from results import decode
dest=out/'audit.json';assert not dest.exists() and not P.exists() and (run/'cleanup.json').exists()
host=json.loads((run/'host-exit.json').read_text());assert host['closed']
assembly=json.loads((K/'assembly001.json').read_text())
source=Path(assembly['fixture_path_linux']) if a.phase==1 else Path('/mnt/e/xwn425/runs/nt5-crypto425-emu001/hdd.qcow2')
source_sha=assembly['fixture_sha256'] if a.phase==1 else json.loads((K/'emu001/audit.json').read_text())['disk_sha256']
assert sha(source)==source_sha;disk=run/'hdd.qcow2';disk_before=sha(disk)
for name,h in json.loads((out/'frozen.json').read_text()).items():assert sha(W/name)==h,name
P.mkdir();m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
tree=ast.parse((W/'outputs/fresh-assembly405/normal-stage006.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='inventory');exec(compile(ast.Module(body=[fn],type_ignores=[]),'original405-inventory','exec'))
r={'phase':a.phase,'physical_access':False,'host_exit':host,'files':{},'events':{},'hives':[]};inventories={}
for phase,path in [('before',source),('after',disk)]:
 folder=P/phase;folder.mkdir()
 with ColdIO(path) as io:
  wr=OemReader(io,m.fatx.open_partition(io,path,'E'));files=inventory(wr);inventories[phase]=files
  assert STARTUP.lower() not in files
  (folder/'files.json').write_text(json.dumps(files,indent=2)+'\n');r['files'][phase]=len(files)
  for name in HIVES+['sysevent.evt','appevent.evt']:(folder/name).write_bytes(wr.read('winnt/system32/config/'+name))
  if phase=='after':
   name='create.log' if a.phase==1 else 'reopen.log'
   try:(folder/name).write_bytes(wr.read('XWN423/'+name))
   except KeyError:pass
   r['probe_files']={n:h for n,h in files.items() if n.startswith('xwn423/')}
 if phase=='after':r['hives']=[hiveaudit(folder/name) for name in HIVES]
 for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
  target=folder/(label+'-events.json');subprocess.run([sys.executable,str(W/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(folder/name),'--output',str(target)],stdout=subprocess.DEVNULL,check=True)
  r['events'].setdefault(label,{})[phase]=json.loads(target.read_text())['records']
changes={'added':[],'removed':[],'changed':[]};before,after=inventories['before'],inventories['after']
for n in sorted(set(before)|set(after)):
 if n not in before:changes['added'].append(n)
 elif n not in after:changes['removed'].append(n)
 elif before[n]!=after[n]:changes['changed'].append(n)
(P/'changes.json').write_text(json.dumps(changes,indent=2)+'\n');r['changes']={k:len(v) for k,v in changes.items()}
r['namespace_changes']={k:[n for n in v if '/microsoft/crypto/' in n or '/microsoft/protect/' in n or n.startswith('xwn423/')] for k,v in changes.items()}
protected=[n for n in before if n.startswith('winnt/') and n.endswith(('.exe','.dll','.sys'))]
r['protected_os_files']=len(protected);r['protected_os_exact']=all(after.get(n)==before[n] for n in protected)
r['staged_exact']=all(after.get(v['path'].lower())==v['sha256'] for v in assembly['changes'])
new=[];history=True
for label,phases in r['events'].items():
 by={v['record']:v for v in phases['after']};history &= all(by.get(v['record'])==v for v in phases['before']);boundary=max([v['record'] for v in phases['before']],default=0);delta=[v for v in phases['after'] if v['record']>boundary];new+=delta
 r['events'][label]={'before_count':len(phases['before']),'after_count':len(phases['after']),'new':delta}
r['normal_shutdown_delta']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in new);r['event_history']=history;r['warning_error_events']=[v for v in new if v['type'] in [1,2]]
log=P/'after'/('create.log' if a.phase==1 else 'reopen.log')
r['probe']=decode(log.read_bytes(),a.phase) if log.exists() else {'missing':True,'complete':False}
scan(disk,out/'after-allocation/artifacts');r['allocation']=json.loads((out/'after-allocation/allocation.json').read_text())
r.update(disk_sha256=disk_before,source_unchanged=sha(source)==source_sha,audit_unchanged=sha(disk)==disk_before,qcow_check=json.loads(subprocess.check_output(['qemu-img','check','--output=json',str(disk)])),strict_qualification=False,scope='Actual native API results, complete FATX E allocation and file inventory, five hives and protected binaries; inherited unsupported-device policy unchanged. No long-name fix or physical qualification.')
assert r['source_unchanged'] and r['audit_unchanged']
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'phase':a.phase,'complete':r['probe'].get('complete'),'api_errors':r['probe'].get('api_errors'),'name_errors':r['probe'].get('name_errors'),'normal_shutdown_delta':r['normal_shutdown_delta'],'allocation':r['allocation']['allocation_consistent']}))
