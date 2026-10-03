"""Export a verified compressed base, then use a small private working overlay."""
import hashlib,json,os,pathlib,subprocess
if os.environ.get('XWN_BUILD_LEASE')!='held':raise SystemExit('Use the build resource wrapper for image compression')
r=pathlib.Path('/home/paul/xbox-windows-native/fixtures/pc-win2000').resolve()
out=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-nt5')
disk=r/'win2000.qcow2';overlay=r/'new-working-overlay.qcow2';base=out/'artifacts/windows2000-pc-base.qcow2'
assert not (r/'qmp.sock').exists(),'Owned VM must be stopped'
assert not base.exists() and not overlay.exists(),'Refusing to overwrite an export'
assert disk.resolve().is_relative_to(r) and overlay.resolve().is_relative_to(r)
subprocess.run(['qemu-img','convert','-c','-f','qcow2','-O','qcow2','-o','compat=1.1',str(disk),str(base)],check=True)
subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(disk),str(base)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(overlay)],check=True)
subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(disk),str(overlay)],check=True)
# Atomic replacement only after both logical-content comparisons passed.
os.replace(overlay,disk)
with base.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
report={'base':str(base),'sha256':digest,'bytes':base.stat().st_size,'virtual_bytes':2147483648,
        'working_overlay':str(disk),'logical_content_comparisons_passed':2,
        'retention_reason':'Golden installed Windows 2000 PC fixture plus a small writable overlay for follow-on development.',
        'source_extraction':'pc-extraction.json records the original full-disk container hash before export; logical contents match this base.'}
(out/'pc-base-image.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
