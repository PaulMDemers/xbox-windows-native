"""Freeze reviewed launcher, namespace-only runner and complete controller inputs."""
import ast,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'package001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'))
host=lambda n:Path(n.replace('/mnt/c/','C:/'))
b=read(K/'runner-build001.json');assert b['status']=='compiled' and b['prebuild_inputs_unchanged']
for n,v in b['files'].items():assert sha(host(n))==v['sha256'] and host(n).stat().st_size==v['bytes']
assert read(K/'imports001.json')['passed']
for name,count in [('controller-host001.json',17),('entry-host002.json',23)]:
 r=read(K/name);assert r['passed'] and len(r['cases'])==count and r['source_sha256']==sha(K/'physical.py')
s=read(K/'supervisor-host001.json');assert s['passed'] and s['all_children_closed'] and s['source_sha256']==sha(K/'supervise.py')
assert read(K.parent/'entry-launch499/review002.json')['passed']
assert read(K.parent/'d3d-scene496/runtime-review002.json')['all_allowed_cases_passed']
assert (K/'entry_decode.py').read_bytes()==(K.parent/'entry-receipt498/decode.py').read_bytes()
files={}
for name,p in [('default.xbe',Path('C:/xwn499/build001/default.xbe')),('run501.exe',Path('C:/xwn501/runner-build001/run501.exe')),('d3d.exe',Path('C:/xwn501/runner-build001/d3d.exe'))]:
 files[name]=dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
assert files['default.xbe']['sha256']=='22d3a9224965159a53cb188be9530f1b211aff8480d3d5773405d7e2974cf6d9'
assert files['d3d.exe']['sha256']=='7cbf053f41ef256e812cc732a306679a21b2a5087920541474fc71d133c85c64'
assert sha(W/'tools/graphics_scene.py')=='1f1efbce5033280293000eba0761c637fb2fdae6fd63ffcf84006bdc6b035127'
modules=read(K.parent/'context-adapter490/package001.json')['runtime_module_pins'];assert len(modules)==10
deps=list(K.glob('*.py'))+list(K.glob('*.c'))+[K/n for n in ['DESIGN.md','launcher-input.json','runner-build001.json','imports001.json','controller-host001.json','entry-host001.json','entry-host002.json','supervisor-host001.json','source-derivation001.json','test-derivation001.json']]
deps += [W/n for n in ['outputs/field-scanout428/physical.py','outputs/demo-audio-level256/common001.py','outputs/surface-bridge260/atomic_json.py','tools/configure-e-display.py','tools/e-display-policy.json','outputs/demo-integration399/accepted-state.json','tools/graphics_scene.py','tools/graphics_scene_oracle.py','tools/graphics_texture.py','tools/graphics_depth.py','tools/graphics_discovery.py','tools/graphics_d3dpresent.py','src/samples/graphics-ladder/scene.c','outputs/d3d-scene496/final-review.json','outputs/d3d-scene496/runtime-review002.json','outputs/d3d-scene496/oracle-tests002.json','outputs/clean-media404/hive_audit004.py','outputs/native-windows-physical-f/decode-legacy-events.py','outputs/context-adapter490/package001.json','outputs/entry-launch499/review002.py','outputs/entry-launch499/review002.json','outputs/entry-launch499/build001.json','outputs/entry-receipt498/decode.py','outputs/entry-receipt498/host001.json']]
for p in K.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
r=dict(passed=True,files=files,dependencies={str(p.resolve()):sha(p) for p in deps},runtime_module_pins=modules,physical_access=False,attempt=501,controller_cases=40,host_remote_interfaces='MODELED',actual_supervisor_children=3,sample_byte_identical_to_PC=True,entry_receipt_not_close_or_boot_authority=True,failed_host001='offline model activated during launch instead of observation; original retained;002 scopes offline to observation only')
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps(dict(passed=True,dependencies=len(r['dependencies']),files=files)))
