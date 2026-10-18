"""Read actual runtime module files twice after hook removal; console E only."""
import hashlib,importlib.util,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];sys.path.insert(0,str(W/'tools'));import graphics_triangle as g
sys.path.insert(0,str(W/'work/python-packages'));import pefile
spec=importlib.util.spec_from_file_location('physical475',K/'physical.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
out=K/'module-review001.json';P=Path('C:/xwn475/modules001');assert not out.exists() and not P.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
c=read(K/'physical001-collection.json');assert c['completed'] and c['hook_removed']
v=read(K/'runtime-review001.json');assert v['all_allowed_cases_passed']
pins=read(K/'package001.json')['runtime_module_pins'];P.mkdir();rows=[]
with m.connect() as ftp:
 for case in v['rows']:
  modules=[]
  for j,name in enumerate(case['review']['modules']):
   low=name.lower()
   if low=='c:\\xwn475\\d3d.exe':
    p=Path(c['files']['/E/xwn475/d3d.exe']['path']);data=p.read_bytes();expected=read(K/'package001.json')['files']['d3d.exe']['sha256']
   else:
    assert low.startswith('c:\\winnt\\system32\\') and low.count('\\')==3
    basename=low.rsplit('\\',1)[-1];assert basename in pins
    data=m.get(ftp,'/E/winnt/system32/'+basename);assert data==m.get(ftp,'/E/winnt/system32/'+basename)
    expected=pins[basename];p=P/basename
    if p.exists():assert p.read_bytes()==data
    else:p.write_bytes(data)
   h=hashlib.sha256(data).hexdigest();assert h==expected
   pe=pefile.PE(data=data);size=pe.OPTIONAL_HEADER.SizeOfImage;assert size==int(case['fields'][f'module{j}.bytes'])
   modules.append(dict(path=str(p),runtime_path=name,sha256=h,bytes=len(data),image_bytes=size))
  rows.append(dict(case=case['name'],modules=modules))
out.write_text(json.dumps(dict(passed=True,rows=rows,console_C_accessed=False,scope='Actual live module snapshots joined to double-read installed bytes and prelaunch pins. Not an unloaded-module trace.'),indent=2)+'\n');print('Physical live module provenance:',[len(r['modules']) for r in rows])
