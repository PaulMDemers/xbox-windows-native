"""Independent read-only raw hive validation of the private captured installation."""
from pathlib import Path
import json,sys,hashlib
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));sys.path.insert(0,str(K.parent/'clean-media404'))
from hive_audit004 import audit
from Registry import Registry
P=Path('/mnt/c/xwn587/windows-capture001/E');out=K/'windows-hives001.json';assert not out.exists()
paths=[P/'winnt/system32/config'/n for n in ('system','software','sam','security','default')]
paths+=list((P/'documents and settings').rglob('ntuser.dat'))
assert len(paths)>=6
r={'passed':False,'hives':{},'physical_writes':False,'mutations':False}
for p in paths:
    before=hashlib.sha256(p.read_bytes()).hexdigest();a=audit(p);assert before==hashlib.sha256(p.read_bytes()).hexdigest()
    r['hives'][p.relative_to(P).as_posix()]={'sha256':before,**a}
r['passed']=all(x['header_valid'] and x['clean'] and x['independent_raw_values_agree'] for x in r['hives'].values())
system=Registry.Registry(str(P/'winnt/system32/config/system'))
select=system.open('Select').value('Current').value();cs='ControlSet%03d'%select
r['current_control_set']=cs
r['paging_files']=system.open(cs+'\\Control\\Session Manager\\Memory Management').value('PagingFiles').value()
r['drive_mappings']={v.name():v.raw_data().hex() for v in system.open('MountedDevices').values()}
out.write_text(json.dumps(r,indent=2)+'\n');assert r['passed']
print(json.dumps({'passed':True,'hives':len(paths),'paging_files':r['paging_files']}))
