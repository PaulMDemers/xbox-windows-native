"""Read-only verification of closed214 inputs, lifecycle and cold evidence."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'evidence-review.json'
assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checked=0
def pin(p,digest):
 global checked
 assert sha(p)==digest,str(p);checked+=1
for name,digest in read(k/'emulator-frozen.json').items():pin(ws/name,digest)
for filename,script in [('native-input-review.json','review-native-inputs.py'),
 ('build-review.json','review-build.py'),('source-review002.json','review-source002.py'),
 ('model-inventory.json','inventory-model.py'),('emulator-pair-review.json','compare-pair.py'),
 ('state-observations.json','interpret-state.py')]:
 r=read(k/filename);assert r['passed'],filename;pin(k/script,r['source_sha256'])
for name,digest in read(k/'source-review002.json')['source_pins'].items():pin(k/name,digest)
for name,digest in read(k/'model-inventory.json')['source_pins'].items():pin(k/'artifacts/model'/name,digest)
b=read(k/'build001.json');assert b['status']=='compiled'
pin(k/'build001.json',read(k/'native-input-review.json')['build_sha256'])
pin(k/'build001.json',read(k/'build-review.json')['build_sha256'])
art=k/'artifacts/build001';ros=Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1')
old=Path('/home/paul/xbox-windows-native/build/video-shared-framebuffer-001/candidate001')
pin(ros/'i386/bin/i686-w64-mingw32-gcc',b['compiler_sha256'])
pin(old/'host-tools/bin/pefixup',b['pefixup_sha256'])
for name,digest in b['dependency_pins'].items():pin(Path(name),digest)
for name,digest in b['copied_inputs'].items():pin(art/'inputs'/name,digest)
for name,row in b['materialized_thin'].items():
 pin(art/'inputs'/Path(name).parent/('regular-'+Path(name).name),row['regular_sha256'])
 pin(ros/'i386/bin/i686-w64-mingw32-ar',row['ar_sha256'])
 pin(ros/'i386/bin/i686-w64-mingw32-ranlib',row['ranlib_sha256'])
 for number,(original,digest) in enumerate(row['members'].items()):
  pin(art/'thin-members'/str(number)/Path(original).name,digest)
mini=art/'source/win32ss/drivers/miniport/xboxvmp/nt5'
for name in ['gpu_snapshot.c','registers.h']:
 pin(mini/name,b['source_pins']['new/'+name]);assert (mini/name).read_bytes()==(k/name).read_bytes()
original=old.parent/'source/win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.c'
pin(original,b['source_pins']['win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.c'])
text=original.read_text()
for needle,phase in [('    V->Ready = TRUE;',0),('            Result.FrameBufferBase = Result.VideoRamBase;',1)]:
 indent=needle[:len(needle)-len(needle.lstrip())]
 text=text.replace(needle,indent+'{ VOID NTAPI XgnSnapshot(PVOID,ULONG,ULONG); XgnSnapshot(V->Control,0x681000,%d); }\n'%phase+needle)
assert (mini/'xboxvnt5.c').read_text()==text
assert sha(art/'control001/main.obj')==sha(art/'candidate001/main.obj')
for row in b['builds']:pin(art/row['case']/'xboxvnt5.sys',row['sha256'])
for filename in ['host-tests001.json','host-tests002.json']:
 h=read(k/filename);assert h['passed']
 for name,digest in h['source_pins'].items():pin(k/name,digest)
 for row in h['runs']:pin(Path(row['command'][-1]),row['binary_sha256'])
p=read(k/'host002-provenance.json');assert p['passed']
pin(k/'host-tests002.json',p['result_sha256'])
pin(k/p['executed_script'],p['executed_script_sha256'])
pin(k/p['compiled_source'],p['compiled_source_sha256'])
assert read(k/'parser-tests.json')['passed']
cases={}
for name in ['control001','candidate001']:
 out=k/('emu-'+name);host=read(out/'host-state.json');c=read(out/'closure.json');a=read(out/'audit.json');launch=read(out/'launch.json')
 assert host['closed'] and c['closed'] and a['scoped_display_passed'] and a['integrity_passed']
 assert host['status']=='cold_audited_closed' and host['audit_exit_code']==0
 pin(out/'audit.json',c['audit_sha256'])
 run=Path('/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/gstate214-runs/nt5-gstate214-'+name)
 pin(run/'cleanup.json',c['cleanup_sha256']);pin(run/'instance.json',host['instance_sha256'])
 assert len(launch['cycles'])==1 and launch['cycles'][0]['dashboard_return'] and launch['cycles'][0]['status']=='accepted'
 assert a['gpu_snapshot']['passed'] and a['gpu_snapshot']['missed']==0
 assert a['gpu_snapshot']['mode']==int(name=='candidate001')
 assert a['normal_shutdown_count']==1 and not a['new_events']['application']
 assert not a['physical_access'] and not a['debugger'] and not a['gpu_transfer_qualified']
 assert not a['strict_qualification_passed'] and not a['ordinary_qualified']
 assert [(v['source'],v['event_id']) for v in a['warnings_errors']]==[('Ftdisk',49)]
 for refusal in host['resource_attempts']:
  assert refusal['resource_busy'] and not refusal['runner_start_exists'] and not refusal['run_exists']
  pin(out/('resource-attempt%d-console.txt'%refusal['attempt']),refusal['log_sha256'])
 for row in a['hives']:pin(out/'artifacts'/('after-'+row['name']),row['sha256'])
 pin(out/'artifacts/after-xwn-video-trace.bin',a['gpu_snapshot']['sha256'])
 pin(out/'audit.json',read(k/'emulator-pair-review.json')['cases'][name]['audit_sha256'])
 cases[name]=dict(host_status=host['status'],audit_sha256=sha(out/'audit.json'),closure_sha256=sha(out/'closure.json'),
  new_read_count=44 if name=='candidate001' else 0,strict_qualification_passed=False)
pin(k/'emu-candidate001/audit.json',read(k/'state-observations.json')['audit_sha256'])
pin(k/'model-inventory.json',read(k/'state-observations.json')['model_inventory_sha256'])
r=dict(passed=True,source_sha256=sha(Path(__file__)),checked_pins=checked,cases=cases,
 frozen_inputs_unchanged=True,physical_access=False,gpu_transfer_qualified=False,
 performance_qualified=False,strict_qualification_passed=False,
 limits='One ordinary launch per fresh child, full cold audit each; original host test counter race and parser oracle failures retained. Read-only GPU state scope, no ownership/idle/address/completion/physical qualification.106 donor target build is not full clean source reconstruction.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Closed214 evidence pins PASS:',checked)
