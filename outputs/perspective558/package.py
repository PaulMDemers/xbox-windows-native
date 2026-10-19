"""MIT. Freeze matched558 workload and tested ordinary-launcher transport."""
import ast,hashlib,importlib.util,json,shutil,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def host(s):return Path(s.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
out=K/'package001.json';assert not out.exists()
assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
r=read(K/'controller-host001.json');assert r['passed'] and r['case_count']==16 and r['source_sha256']==sha(K/'controller.py')
assert read(K/'imports002.json')['passed']
admission=read(K/'admission-host001.json')
assert admission['passed'] and admission['controller_sha256']==sha(K/'controller.py')
b=read(K/'runner-build002.json');assert b['status']=='compiled' and b['exit_code']==0 and b['source_namespace_only']
for n,row in b['files'].items():assert sha(host(n))==row['sha256'] and host(n).stat().st_size==row['bytes']
assert read(K.parent/'perspective556/runtime-review002.json')['all_allowed_cases_passed']
files={}
for row in b['rows']:
    p=host(row['path']);files[p.name]=dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
assert set(files)=={'run558.exe','d3d.exe'}
assert files['d3d.exe']['sha256']==read(K.parent/'perspective556/sample-build001.json')['executable_sha256']
assert read(K.parent/'perspective556/oracle-tests002.json')['passed']
qualified=read(K.parent/'perspective556/runtime-review002.json')['frozen_dependencies']
for relative in ['tools/graphics_perspective.py','tools/graphics_perspective_oracle.py','tests/test_graphics_perspective.py','tests/test_graphics_perspective_oracle.py','src/samples/graphics-ladder/perspective.c']:
    key=next(n for n in qualified if n.replace(chr(92),'/').endswith('/'+relative))
    assert sha(W/relative)==qualified[key],relative
assert read(K.parent/'perspective556/final-review.json')['scoped_perspective_passed']

for p in K.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
s=importlib.util.spec_from_file_location('scene558package',K/'controller.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
c.pair.verify()
pins={str(p.resolve()):sha(p) for p in K.iterdir() if p.is_file()}
pins.update(read(K.parent/'windows-pair532/preflight001.json')['pins'])
for module in list(sys.modules.values()):
    n=getattr(module,'__file__',None)
    if n:
        p=Path(n).resolve()
        if p.is_relative_to(W) and p.is_file():pins[str(p)]=sha(p)
for n in ['outputs/perspective556/oracle-tests002.json','outputs/perspective556/sample-build001.json','outputs/perspective556/build001.json','outputs/perspective556/runtime-review002.json','outputs/perspective556/final-review.json','outputs/context-adapter490/package001.json','outputs/clean-media404/hive_audit004.py','outputs/native-windows-physical-f/decode-legacy-events.py','outputs/surface-bridge260/atomic_json.py','tools/graphics_perspective.py','tools/graphics_perspective_oracle.py','tests/test_graphics_perspective.py','tests/test_graphics_perspective_oracle.py','tools/graphics_texture.py','tools/graphics_depth.py','tools/graphics_discovery.py','tools/graphics_d3dpresent.py','src/samples/graphics-ladder/perspective.c']:
    p=W/n;pins[str(p.resolve())]=sha(p)
for p,h in pins.items():assert sha(Path(p))==h,p
modules=read(K.parent/'context-adapter490/package001.json')['runtime_module_pins'];assert len(modules)==10
modules=dict(modules)
c.boot_work_closed()
for p in [K.parent/'perspective557/final001.json',K.parent/'boot-primer543/final001.json',K.parent/'warm-pre-pci544/final001.json',K.parent/'warm-pre-pci544/cancelled001.json']:
    if p.exists():pins[str(p.resolve())]=sha(p)
out.write_text(json.dumps(dict(passed=True,pins=pins,files=files,runtime_module_pins=modules,physical_access=False,launches_allowed=1,ordinary_launcher=True,staging_requires_boot_work_closed=True,controller_model_cases=16,matched556_sample=True,graphics_qualified=False),indent=2)+'\n',encoding='utf-8')
print('PASS frozen558 package:',len(pins),'pins')
