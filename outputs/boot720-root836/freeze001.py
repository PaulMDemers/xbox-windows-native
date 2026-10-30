"""Freeze836 inputs and installed Windows baseline; no console access."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];A=W/'outputs/boot720-native835'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(A/'closed001.json')['state']=='CLOSED'
assert read(A/'audit001.json')['passed']
pkg=read(A/'package001.json');critical=read(A/'audit001.json')['critical_payload']
base={'archive_sha256':pkg['archive_sha256'],'installation_manifest_sha256':sha(A/'package001.json'),
 'installed_baseline_audit_sha256':sha(A/'audit001.json'),'critical':{},'support':{},
 'scope':'Existing Windows installation is the baseline; no835 runtime/recollection/relaunch. New support bytes come from immutable343 archive.'}
for p,v in critical.items():
 if not p.startswith('/E/Applications/'):
  assert v['matches_installed'];base['critical'][p]={'bytes':v['bytes'],'sha256':v['sha256']}
for p,v in pkg['files'].items():
 if p.startswith('/E/Applications/XWN16Boot835/'):
  n=p.removeprefix('/E/Applications/XWN16Boot835/')
  if n in ['freeldr.ini','probe.bin','loader/halxboxnt5.dll','loader/xboxbvid.dll']:base['support'][n]=v
assert len(base['critical'])==9 and len(base['support'])==4
cap=read(W/'outputs/boot720-capacity834/collection001.json')['e']['free_bytes']
base['projected_console_reserve']={'last_measured_free':cap,'installed_allocation':pkg['allocated_bytes'],
 'additional_owned_budget':32*1024**2,'projected_remaining':cap-pkg['allocated_bytes']-32*1024**2,
 'minimum_required':256*1024**2,'limit':'Conservative budget from capacity834 and owned installation journal; not a new free-space measurement.'}
assert base['projected_console_reserve']['projected_remaining']>base['projected_console_reserve']['minimum_required']
out=K/'baseline001.json';assert not out.exists();out.write_text(json.dumps(base,indent=2)+'\n')
pins={p.name:sha(p) for p in K.iterdir() if p.is_file() and (p.suffix in ['.py','.c','.h','.S','.ld','.patch'] or p.name in ['Makefile','.gitattributes','source001.json','baseline001.json','root001.json','qualify001.json','chain002.json','host006.json','cpu-build010.json','cpu-run010.json','build001.json'])}
out=K/'launch-source-pins001.json';assert not out.exists();out.write_text(json.dumps(pins,indent=2)+'\n')
note='''# Boot836 fixed720p FATX root fix qualified; next create-only stage and one launch

Boot835 CLOSED FAIL at FreeLoader SYSTEM.ALT error, before NT kernel. Photo and
preparation collected once; all11 critical files unchanged. Dashboard authenticated
12:02:50 UTC. No owned hook/runtime. Never relaunch/recollect/runtime-parent835.

Concrete loader defect: FatBufferDirectory treated FATX root as one fixed cluster.
E had1071 live entries (256 fit its16KiB first cluster). WINNT was newly appended;
LIST ordering is not a raw slot measurement, so physical causality remains inferred.
Actual C regression reproduces truncation, patched fragmented-root cases pass.
836 follows FATX cluster1 chain, preserving existing volume layout, and refuses
zero-size directory buffer after chain-count failure. No timing/encoder change.

Fresh source-only exports/source001.json; fatx-root.patch; root001.json (before2,
after9 cases). Chain002, retention/map14+14, page37/allocation164177, diskless CPU13
passed; all fixture VMs closed. Fresh nxdk frontend build001 passed. Pins frozen
launch-source-pins001.json. Existing Windows baseline hives/drivers/startup untouched.

Next physical.py stage (new E:/Applications/XWN16Boot836), exact readback, commit,
then ONE SITE via physical.py launch,20-second bound. Poll read-only after2min and
request actual screen. No retries after acceptance/uncertainty. On dashboard return
no hook to remove, collect836 once. Do not mistake FTP absence for Windows success.
Old automation remains paused; direct user Windows720p work authorized.
'''
(K/'NEXT.md').write_text(note)
(A/'NEXT.md').write_text('# Boot835 CLOSED FAIL\n\nSee closed001.json and audit001.json. Never relaunch or recollect.\nNext: ../boot720-root836/NEXT.md\n')
for p in [W/'outputs/engineering-notes/CONTINUATION.md',W/'outputs/engineering-notes/STATUS.md',W/'docs/current-status.md']:p.write_bytes(note.encode()+b'\n'+p.read_bytes())
print('Frozen836 sources and baseline; projected console reserve',base['projected_console_reserve']['projected_remaining'])
