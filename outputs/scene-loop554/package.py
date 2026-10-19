"""MIT. Freeze matched554 workload and tested ordinary-launcher transport."""
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
b=read(K/'runner-build002.json');assert b['status']=='compiled' and b['exit_code']==0 and b['source_namespace_only']
for n,row in b['files'].items():assert sha(host(n))==row['sha256'] and host(n).stat().st_size==row['bytes']
assert read(K.parent/'scene-loop553/runtime-review002.json')['all_allowed_cases_passed']
files={}
for row in b['rows']:
    p=host(row['path']);files[p.name]=dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
assert set(files)=={'run554.exe','scene.exe'}
assert files['scene.exe']['sha256']==read(K.parent/'scene-loop553/sample-build001.json')['executable_sha256']
assert read(K/'checker-review002.json')['passed']
assert read(K/'checker-review002.json')['source_sha256']==sha(W/'tools/graphics_sceneloop.py')
assert read(K/'checker-review002.json')['tests_sha256']==sha(W/'tests/test_graphics_sceneloop.py')
assert sha(W/'tools/graphics_scene.py')=='1f1efbce5033280293000eba0761c637fb2fdae6fd63ffcf84006bdc6b035127'
for p in K.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
s=importlib.util.spec_from_file_location('scene554package',K/'controller.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
c.pair.verify()
pins={str(p.resolve()):sha(p) for p in K.iterdir() if p.is_file()}
pins.update(read(K.parent/'windows-pair532/preflight001.json')['pins'])
for module in list(sys.modules.values()):
    n=getattr(module,'__file__',None)
    if n:
        p=Path(n).resolve()
        if p.is_relative_to(W) and p.is_file():pins[str(p)]=sha(p)
for n in ['outputs/scene-loop553/dynamic-import001.json','outputs/scene-loop553/sample-build001.json','outputs/scene-loop553/build001.json','outputs/scene-loop553/runtime-review002.json','outputs/scene-loop553/final-review.json','outputs/context-adapter490/package001.json','outputs/clean-media404/hive_audit004.py','outputs/native-windows-physical-f/decode-legacy-events.py','outputs/surface-bridge260/atomic_json.py','tools/graphics_sceneloop.py','tests/test_graphics_sceneloop.py','tools/graphics_scenepresent.py','tools/graphics_scene.py','tools/graphics_scene_oracle.py','tools/graphics_texture.py','tools/graphics_depth.py','tools/graphics_discovery.py','tools/graphics_d3dpresent.py','src/samples/graphics-ladder/sceneloop.c']:
    p=W/n;pins[str(p.resolve())]=sha(p)
for p,h in pins.items():assert sha(Path(p))==h,p
modules=read(K.parent/'context-adapter490/package001.json')['runtime_module_pins'];assert len(modules)==10
modules=dict(modules);modules['psapi.dll']=read(K.parent/'scene-loop553/dynamic-import001.json')['dll_sha256']
c.boot_work_closed()
out.write_text(json.dumps(dict(passed=True,pins=pins,files=files,runtime_module_pins=modules,physical_access=False,launches_allowed=1,ordinary_launcher=True,staging_requires_boot_work_closed=True,controller_model_cases=16,matched553_sample=True,graphics_qualified=False),indent=2)+'\n',encoding='utf-8')
print('PASS frozen554 package:',len(pins),'pins')
