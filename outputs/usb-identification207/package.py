"""Package only the reviewed original descriptor collector, never deploy it."""
import hashlib,json,zipfile
from pathlib import Path
k=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_text())
build=read(k/'build-review.json');audit=read(k/'emu003/audit.json')
assert build['passed'] and audit['descriptor_scope_observed'] and audit['protected_exact']
assert audit['allocation_consistent'] and not audit['allocation_errors'] and not audit['orphan_cluster_count']
assert all(h['sequences_equal'] and h['checksum_valid'] for h in audit['hives'].values())
assert audit['setup_history_prefix']
assert audit['only_expected_driver_key_absence']
assert sha((k/'probe.c').read_bytes())==build['source_sha256']
exe=k/build['binary'];assert sha(exe.read_bytes())==build['binary_sha256']
files={'usbprobe.exe':exe.read_bytes()}
for name in ['probe.c','analyze.py','HARDWARE-PROTOCOL.md','REFERENCES.md','REPORT.md','build-review.json','parser-tests.json','emu003/audit.json','emu003/runtime-review.json']:
 files[name]=(k/name).read_bytes()
manifest=dict(purpose='Read-only physical descriptor collection by coordinator; not a USB/gamepad driver',
 source_sha256=build['source_sha256'],binary_sha256=build['binary_sha256'],
 build_review_sha256=sha((k/'build-review.json').read_bytes()),emulator_audit_sha256=sha((k/'emu003/audit.json').read_bytes()),
 files={n:sha(b) for n,b in files.items()},physical_tested=False,driver_support=False,deploys=False,
 limits='No binding/registry changes; ordinary cold-boot persistence and physical XID input remain unqualified. Coordinator must pin fresh baseline/rollback and unique output path.')
files['manifest.json']=(json.dumps(manifest,indent=2)+'\n').encode()
out=k/'artifacts/usb207-collector.zip';assert not out.exists()
with zipfile.ZipFile(out,'x',zipfile.ZIP_DEFLATED) as z:
 for name,data in files.items():
  info=zipfile.ZipInfo(name,date_time=(2026,10,9,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
with zipfile.ZipFile(out) as z:
 assert set(z.namelist())==set(files)
 for name,data in files.items():assert z.read(name)==data
manifest['package_path']=str(out);manifest['package_sha256']=sha(out.read_bytes())
(k/'package-review.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Reviewed diagnostic collector package, no deployment')
