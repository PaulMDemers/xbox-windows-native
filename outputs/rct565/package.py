"""MIT. Freeze the verified private retail payload and owned physical controller."""
import ast,hashlib,importlib.util,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
host=lambda s:Path(s.replace('/mnt/c/','C:/'))
out=K/'package001.json';assert not out.exists()
t=read(K.parent/'rct566/transfer001.json');assert t['passed'] and t['game_without_original_disc']
assert read(K.parent/'rct566/final001.json')['closed']
assert read(K.parent/'rct566/observations003.json')['windowed_park_rendered_without_original_disc']
b=read(K/'runner-build004.json');assert b['status']=='compiled' and b['exit_code']==0
for n,r in b['files'].items():assert sha(host(n))==r['sha256']
assert sha(K/'runner.c')==b['files']['/mnt/c/xwn565/runner-build004/runner.c']['sha256']
review=read(K/'source-review001.json');assert review['passed'] and review['runner_sha256']==sha(K/'runner.c')
h=read(K/'controller-host003.json');assert h['passed'] and h['source_sha256']==sha(K/'controller.py')
files={n:dict(row,path=str(host(row['path']))) for n,row in t['files'].items()}
row=b['rows'][0];files['run565.exe']=dict(row,path=str(host(row['path'])))
sys.path.insert(0,str(W/'tools'));from fatx_names import check_path
for n,r in files.items():check_path('xwn565-kit/'+n,437);assert sha(Path(r['path']))==r['sha256']
assert len({n.lower() for n in files})==len(files)
for n in t['directories']:check_path('xwn565-kit/'+n,437)
for p in K.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
s=importlib.util.spec_from_file_location('rct565package',K/'controller.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c);c.pair.verify();c.boot_work_closed()
pins={str(p.resolve()):sha(p) for p in K.iterdir() if p.is_file()}
pins.update(read(K.parent/'windows-pair532/preflight001.json')['pins'])
for module in list(sys.modules.values()):
 n=getattr(module,'__file__',None)
 if n:
  p=Path(n).resolve()
  if p.is_relative_to(W) and p.is_file():pins[str(p)]=sha(p)
for n in ['outputs/rct566/transfer001.json','outputs/rct566/observations003.json','outputs/rct566/ntfs-cold1-002.json','outputs/rct566/final001.json','outputs/context-adapter490/package001.json','outputs/perspective558/final001.json']:
 p=W/n;pins[str(p.resolve())]=sha(p)
modules=read(K.parent/'context-adapter490/package001.json')['runtime_module_pins']
r=dict(passed=True,files=files,directories=t['directories'],total_bytes=sum(v['bytes'] for v in files.values()),pins=pins,runtime_module_pins=modules,physical_access=False,allowed_launches=1,game_seconds=180,windowed=True,game_executable_modified=False,original_disc_data_added=True,graphics_qualified=False,audio_qualified=False,registry_values_temporarily_set=['Path','Language','SetupPath'],scope='Private supplied-media package. PC success admits one watched Xbox startup test; it does not establish Xbox compatibility.')
out.write_text(json.dumps(r,indent=2)+'\n');print('Frozen',len(files),'files,',r['total_bytes'],'bytes;',len(pins),'source pins')
