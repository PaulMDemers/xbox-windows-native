"""Review actual phase ownership, source/entry/fixture pins before any launch."""
import ast,hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'prelaunch-review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(k/'test001.json')['passed'] and read(k/'host-close-test001.json')['passed']
for name in ['snapshot','guard','connection']:assert read(k/(name+'-test001.json'))['passed']
trace=(k/'trace.py').read_text();ast.parse(trace)
assert trace.count("qom-set '+path+' xwn-snapshot238 true")==1
assert trace.count('SITE EXEC')==1 and "arm(2," not in trace
assert "phase=='dashboard'" in trace and "phase=='xbe'" in trace and "phase=='freeldr'" in trace
assert trace.index("if phase=='xbe'")>trace.index("name='actual_xromwell_xbe_entry'")
assert trace.index("if phase=='freeldr'")>trace.index("name='actual_freeldr_multiboot_entry'")
assert "terminal_state=state" in trace and trace.index('terminal_state=state')<trace.index("assert state==3")
assert 'repeat==report' in trace and "remaining_breakpoints=armed.copy()" in trace
assert "Qqemu.PhyMemMode:1" not in trace and "restore_physical_mode" in trace
assert read(k/'snapshot-test001.json')['source_sha256']==sha(k/'trace.py')
assert read(k/'guard-test001.json')['source_sha256']==sha(k/'trace.py')
assert read(k/'connection-test001.json')['source_sha256']==sha(k/'supervise-emulator.py')
for p in k.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
inv=read(k/'inventory001.json');original=ws/inv['inherited_inventory_path'];assert sha(original)==inv['inherited_inventory_sha256']
from parsing import xbe,span
for name,key in [('dashboard','dashboard'),('xromwell','launcher')]:
 raw=(k/'artifacts/inputs'/(name+'.xbe')).read_bytes();assert xbe(raw)==inv[key]
 assert len(span(raw,inv[key],inv[key]['entry'],32))==32
expected={'dashboard.xbe':inv['files']['C/evoxdash.xbe'],'xromwell.xbe':inv['files']['E/Applications/XWNFBoot/default.xbe'],'freeldr.sys':inv['files']['E/Applications/XWNFBoot/freeldr.sys']}
for name,digest in expected.items():assert sha(k/'artifacts/inputs'/name)==digest
seed=read(k/'fixture-seed001.json');fixtures=[]
for case,phase in [('dashboard001','dashboard'),('xbe001','xbe'),('freeldr001','freeldr')]:
 f=read(k/('fixture-'+case+'.json'));assert f['phase']==phase and f['shared_immutable_seed'] and f['fixture_sha256']==seed['fixture_sha256']
 assert not f['inherited_null_policy'] and f['gpu_writes']==False and f['files']==seed['files'] and f['protected']==seed['protected']
 assert not (k/case/'runner-start.json').exists() and not (k/case/'host-state.json').exists()
 fixtures.append(dict(case=case,phase=phase,immutable_seed_sha256=f['fixture_sha256']))
exe=k/'artifacts/build001/xemu-reference238.exe';assert sha(exe)==read(k/'build001.json')['executable_sha256']
pg=k/'artifacts/build001/source/hw/xbox/nv2a/pgraph/pgraph.c'
s=pg.read_text();assert 'NV_PGRAPH_FIFO_ACCESS' in s and '? 1 : 0' in s and 'waiting_for_nop ? 2' in s and 'waiting_for_flip ? 4' in s and 'waiting_for_context_switch ? 8' in s
record=dict(passed=True,source_sha256=sha(Path(__file__)),fixtures=fixtures,compiled_wait_source_sha256=sha(pg),wait_mask={'1':'FIFO access disabled','2':'NOP','4':'flip','8':'context-switch'},executable_sha256=sha(exe),guest_launch=False,physical_access=False,dirty_surface_coverage=False,ownership_qualified=False)
dest.write_text(json.dumps(record,indent=2)+'\n');print('238 prelaunch review PASS')
