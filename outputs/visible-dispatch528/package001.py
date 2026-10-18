"""Freeze existing528 candidate for one watched test; never connect or launch."""
import ast
import hashlib
import json
import shutil
from pathlib import Path

K=Path(__file__).resolve().parent
W=K.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'package001.json'
assert not out.exists()
assert not (K/'physical001-stage.json').exists()
assert not Path('C:/xwn528/physical001').exists()
for name in ['host001','ui-host001','controller-host001','supervisor-host001','emu-audit002']:
    assert read(K/(name+'.json'))['passed'],name
host=read(K/'host001.json')
assert host['actual_engine'] and host['OS_services']=='MODELED'
assert host['engine_scenarios']==19 and host['transport_rejections']==112
ui=read(K/'ui-host001.json')
assert ui['actual_main_and_engine'] and ui['SDK_services']=='MODELED' and ui['scenarios']==30
for name,h in ui['source_sha256'].items():
    assert sha(K/name)==h,name
controller=read(K/'controller-host001.json')
assert len(controller['cases'])==30 and controller['source_sha256']==sha(K/'physical.py')
supervisor=read(K/'supervisor-host001.json')
assert supervisor['all_children_closed'] and supervisor['source_sha256']==sha(K/'supervise.py')
a=read(K/'emu-audit002.json')
assert a['actual_runtime_entry'] and a['begin_pipeline_completed'] and a['source_seed_unchanged']
assert a['source_inputs_unchanged'] and a['private_eeprom_unchanged']
assert a['closure']['closed'] and a['closure']['natural_exit'] and a['closure']['exit']==0
assert not a['closure']['fallback'] and not a['closure']['deadline_reached']
assert a['after']['orphans']==a['after']['errors']==0
assert a['whole_disk_equal'] is False and a['changed_offsets_outside_E']==[1540]
assert not a['entry_own_close_proved'] and not a['physical_qualification']
b=read(K/'build001.json');pre=read(K/'prebuild001.json')
assert b['compiled'] and b['sdk_unchanged']
p=Path('C:/xwn528/build001/bin/default.xbe')
expected='d2f32d69247358bddb7dad4274789c8645e496bfe60476ccd41889a39fc24499'
assert p.stat().st_size==110592 and sha(p)==expected
assert expected==b['outputs']['bin\\default.xbe']['sha256']
assert expected==read(K/'preparation002.json')['candidate_sha256']
assert expected==a['before']['files']['/applications/xwndispatch528/default.xbe']
assert expected==a['after']['files']['/applications/xwndispatch528/default.xbe']
for name,h in pre['sources'].items():
    assert sha(K/name)==h and sha(Path('C:/xwn528/build001')/name)==h,name
for name,h in pre['tools'].items():
    assert sha(Path(name))==h,name
for name,h in pre['sdk'].items():
    assert sha(Path('C:/nxdk')/name)==h,name
for name,row in b['outputs'].items():
    assert sha(Path('C:/xwn528/build001')/name)==row['sha256'],name
runtime=read(K/'runtime-prepared002.json')
assert sha(Path(runtime['inputs']['utility.iso']['source']))==runtime['inputs']['utility.iso']['sha256']
old=(K.parent/'dispatch-control527/physical-closeout001.py').read_bytes()
assert (K/'physical-closeout001.py').read_bytes()==old.replace(b'527',b'528')
for path in K.glob('*.py'):
    ast.parse(path.read_text(encoding='utf-8'))
deps=list(K.glob('*.py'))+list(K.glob('*.c'))+list(K.glob('*.h'))
deps += [K/n for n in ['Makefile','DESIGN.md','PACKAGE.md','.gitattributes',
    'host001.json','ui-host001.json','controller-host001.json','supervisor-host001.json',
    'build001.json','prebuild001.json','preparation002.json','runtime-prepared002.json',
    'emu-audit002.json','closure001.json','final-review.json',
    'capture-failure001.json','capture-failure002.json']]
deps += [W/n for n in ['outputs/field-scanout428/physical.py',
    'outputs/demo-audio-level256/common001.py','outputs/surface-bridge260/atomic_json.py',
    'tools/configure-e-display.py','tools/e-display-policy.json',
    'outputs/demo-integration399/accepted-state.json',
    'outputs/native-windows-physical-f/physical-cache-preflight.json',
    'outputs/device-hardware220/state/demo251-claimed.json',
    'outputs/clean-media404/hive_audit004.py',
    'outputs/native-windows-physical-f/decode-legacy-events.py']]
free=shutil.disk_usage('C:/').free
assert free-64*1024**2>=20*1024**3
r=dict(passed=True,files={'default.xbe':dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))},
    dependencies={str(p.resolve()):sha(p) for p in sorted(set(deps))},
    capacity_free_C=free,projected_C_bytes=64*1024**2,E_allocation=0,
    controller_cases=30,actual_supervisor_children=3,engine_host_scenarios=19,
    UI_host_scenarios=30,SDK_pins_rehashed=len(pre['sdk']),
    physical_access=False,physical_launch_queued=False,observer_confirmation_pending=True,
    scope='Exact existing candidate; modeled SDK/FTP controls and actual emulator receipts. Rendered output and physical execution unverified.',
    emulator_disk_strict=False,emulator_changed_offset_outside_E=[1540],
    no_disk_gate_waiver=True,visual_output_qualified=False,windows_boot_qualified=False,
    physical_closeout_source='Exact527 namespace-only adaptation; prepared, not executed')
with out.open('x',encoding='utf-8',newline='\n') as f:
    json.dump(r,f,indent=2);f.write('\n')
print('PASS',len(r['dependencies']),'frozen inputs; package prepared, no stage/launch')
