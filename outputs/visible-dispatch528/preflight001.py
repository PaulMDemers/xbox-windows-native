"""Exact actual inputs before the sole fresh emulator launch."""
import hashlib,json,shutil,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (K/'preflight001.json').exists() and not (K/'emu-frozen001.json').exists()
for n in ['host001','ui-host001','controller-host001','supervisor-host001']:assert read(K/(n+'.json'))['passed']
assert read(K/'supervisor-host001.json')['all_children_closed']
for n,h in read(K/'ui-host001.json')['source_sha256'].items():assert sha(K/n)==h
pre=read(K/'prebuild001.json');build=read(K/'build001.json');runtime=read(K/'runtime-prepared002.json')
assert build['compiled'] and build['sdk_unchanged']
for n,h in pre['sdk'].items():assert sha(Path('C:/nxdk')/n)==h
for n,h in pre['tools'].items():assert sha(Path(n))==h
for n,h in pre['sources'].items():assert sha(K/n)==h
for n,v in build['outputs'].items():assert sha(Path('C:/xwn528/build001')/n)==v['sha256']
assert runtime['inputs']['utility.iso']['sha256']==build['outputs']['dispatch528.iso']['sha256']
assert read(K/'preparation002.json')['candidate_sha256']==build['outputs']['bin\\default.xbe']['sha256']
for n,v in runtime['inputs'].items():assert sha(Path(v['source']))==v['sha256'] and sha(Path(runtime['root'])/n)==v['sha256']
assert sha(Path(runtime['private_executable']['path']))==runtime['emulator']['sha256']
assert read(K/'capacity-apply002.json')['all_bytes_paths_identity_preserved']
free=shutil.disk_usage('C:/').free;assert free-768*1024**2>=20*1024**3
live=subprocess.run(['pwsh','-NoProfile','-Command','Get-Process -Name xemu* -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True,timeout=20);assert not live.stdout.strip()
paths=[p for p in K.iterdir() if p.is_file() and p.suffix in ('.py','.ps1','.c','.h','.md')]
paths += [K/n for n in ['Makefile','.gitattributes','build001.json','prebuild001.json','preparation002.json','runtime-prepared002.json','host001.json','ui-host001.json','controller-host001.json','supervisor-host001.json']]
paths += list(Path('C:/xwn528/emu001').iterdir())+[Path('C:/xwn528/preparation002/seed.qcow2')]
paths += [Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts')/p for p in ['with_xbox_resource.ps1','lib/xemu_instance.ps1','lib/test_storage.ps1','fatx_stage_boot.py']]
paths += [W/'outputs/fatx-mapped-eof/coldio.py',W/'outputs/native-windows-fatx-runtime/bulk_fatx.py']
pins={str(p.resolve()):sha(p) for p in paths};(K/'emu-frozen001.json').write_text(json.dumps(pins,indent=2)+'\n',encoding='utf-8')
r=dict(passed=True,frozen_inputs=len(pins),actual_sdk_pins=len(pre['sdk']),all_build_outputs_exact=True,ISO_matches_actual_build=True,application_source_matches_host_and_Xbox_build=True,capacity_C=free,projected_bytes=768*1024**2,no_live_emulator=True,no_physical_access=True,observer_question_pending=True,physical_launch_queued=False)
(K/'preflight001.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print('PASS',len(pins),'frozen inputs; physical launch NOT queued')
