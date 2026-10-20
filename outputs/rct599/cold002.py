"""One closed-phase read-only audit; no raw conversion, mounting, or source writes."""
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'crypto-persistence423'))
from ntfs_read002 import Reader,sha
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'work/python-packages'))

K=Path(__file__).resolve().parent;P=Path('/mnt/c/xwn599/pc001')
sys.path.insert(0,str(K.parent/'clean-media404'));from hive_audit004 import audit
p=argparse.ArgumentParser();p.add_argument('--phase',type=int,choices=[0,1],required=True);a=p.parse_args()
out=K/f'ntfs-cold{a.phase}-002.json';target=P/f'cold{a.phase}-002';assert not out.exists() and not target.exists()
prep=json.loads((K/'ntfs-preparation001.json').read_text());disk=P/'disk.qcow2';before=sha(disk)
if a.phase:
 state=json.loads((K/f'ntfs-phase{a.phase}.json').read_text());assert state['closed'] and before==state['disk_sha256']
else:assert before==prep['child_sha256']
assert not list(P.glob('phase*/qmp.sock'))
target.mkdir();check=subprocess.run(['qemu-img','check','--output=json',str(disk)],capture_output=True,text=True)
(target/'qcow-check.json').write_text(check.stdout);assert not check.returncode,check.stderr
manifest={};saved={};dirs=set();excluded=[]
with Reader(disk) as reader:
 todo=[('',reader.fs.mft.get('/'))]
 while todo:
  base,node=todo.pop();assert node.segment not in dirs;dirs.add(node.segment);assert len(dirs)<=2000
  for name,child in sorted(node.listdir(dereference=True,ignore_dos=True).items()):
   if name in ('.','..'):continue
   path=base+'/'+name if base else name;assert len(path)<1024
   if not base and (name.startswith('$') or name.lower() in ['pagefile.sys','hiberfil.sys','system volume information','recycler']):excluded.append(path);continue
   assert not child.is_symlink() and not child.is_mount_point(),path
   if child.is_dir():todo.append((path,child));continue
   assert len(manifest)<12000
   data=reader.read(path);lower=path.lower();assert lower not in manifest
   manifest[lower]={'path':path,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
   if lower.startswith('xwn599-kit/') and lower.endswith(('.txt','.flag')) or lower.endswith('ntuser.dat') or lower.startswith('xwn599/') or lower.endswith(('.exe','.ini','.cfg','.sv4','.sv6')) and ('rollercoaster' in lower or lower.startswith(('games/','xwn599-kit/')))  or lower in ['winnt/system32/config/'+n for n in ['system','software','sam','security','default','sysevent.evt','appevent.evt']]:
    dest=target/'files'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);saved[lower]=dest
 nbd_bytes=reader.raw.read_bytes
(target/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
hives=[audit(saved['winnt/system32/config/'+n]) for n in ['system','software','sam','security','default']]
events={}
for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
 dest=target/(label+'-events.json');subprocess.run([sys.executable,str(K.parent/'native-windows-physical-f/decode-legacy-events.py'),str(saved['winnt/system32/config/'+name]),'--output',str(dest)],check=True,stdout=subprocess.DEVNULL)
 events[label]=json.loads(dest.read_text())['records']
previous=K/f'ntfs-cold{a.phase-1}-002.json' if a.phase else None
normal=sum(r['source']=='EventLog' and r['event_id']==6006 for r in events['system'])
report={'phase':a.phase,'disk_sha256':before,'source_unchanged':sha(Path(prep['source']))==prep['source_sha256'],'audit_unchanged':sha(disk)==before,'files':len(manifest),'directories':len(dirs),'manifest_sha256':sha(target/'manifest.json'),'excluded_metadata_paging_restore':excluded,'hives':hives,'qcow_check':json.loads(check.stdout),'normal_shutdown_count':normal,'normal_shutdown_delta':0,'nbd_bytes_read':nbd_bytes,'private_path':str(target),'complete':False,'scope':'All enumerated non-metadata/non-paging file contents hashed, five hives parsed. Not an independent NTFS allocation-bitmap/ownership audit.'}
if a.phase:
 prev=json.loads(previous.read_text());report['normal_shutdown_delta']=normal-prev['normal_shutdown_count']
 old=json.loads((Path(prev['private_path'])/'manifest.json').read_text());changes={'added':[],'removed':[],'changed':[]}
 for n in sorted(set(old)|set(manifest)):
  if n not in old:changes['added'].append(n)
  elif n not in manifest:changes['removed'].append(n)
  elif old[n]['sha256']!=manifest[n]['sha256']:changes['changed'].append(n)
 (target/'changes.json').write_text(json.dumps(changes,indent=2)+'\n');report['changes']={k:len(v) for k,v in changes.items()}
 report['namespace_changes']={k:[n for n in v if '/microsoft/crypto/' in n or '/microsoft/protect/' in n or n.startswith('xwn599/')] for k,v in changes.items()}
 report['runner_present']='xwn599/runner.txt' in saved
 old_events=json.loads((Path(prev['private_path'])/'system-events.json').read_text())['records'];boundary=max(r['record'] for r in old_events)
 report['new_system_events']=[{'record':r['record'],'source':r['source'],'event_id':r['event_id'],'type':r['type']} for r in events['system'] if r['record']>boundary]
 assert all(n in manifest and manifest[n]['sha256']==old[n]['sha256'] for n in old if n.endswith(('.dll','.exe','.sys')) and n.startswith('winnt/')),'protected OS binary changed'
report['complete']=True
assert report['source_unchanged'] and report['audit_unchanged']
out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['phase','files','directories','complete','normal_shutdown_delta']}))
