"""Preserve failed no-growth preparation; add fresh audited E: growth fixtures."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent
assert json.loads((k/'pipeline001.json').read_text())[-1]['result']=='failed'
for name in ('prepare-emulator','run-emulator','audit-emulator','review-pnp'):
    p=k/(name+'002.py');assert not p.exists()
    s=(k/(name+'.py')).read_text().replace("variant+'001'","variant+'002'")
    if name=='prepare-emulator':
        s=s.replace('from restore import restore','from restore import restore\nfrom e_allocation import scan_e')
        s=s.replace("m.target=source;io=m.SliceIO(source);ew=", "e_before=scan_e(source,art/'e-before.json')\nm.target=source;io=m.SliceIO(source);ew=")
        s=s.replace("assert restore(ew,'Applications/XWNFBoot/loader/halxboxnt5.dll',hal_path.read_bytes())=='in-place','Reject E allocation growth'", "e_restore=restore(ew,'Applications/XWNFBoot/loader/halxboxnt5.dll',hal_path.read_bytes())")
        s=s.replace('io.seek(ew.p.partition_offset);assert io.read(len(e_meta))==e_meta','e_after=scan_e(source,art/\'e-prepared.json\')\nio.seek(ew.p.partition_offset);e_meta=io.read(len(e_meta))')
        s=s.replace('allocation_unchanged=True','allocation_unchanged=e_before[\'metadata_sha256\']==e_after[\'metadata_sha256\'],restore_method=e_restore')
        s=s.replace('e_metadata=e_metadata,','e_metadata=e_metadata,e_before=e_before,e_prepared=e_after,')
    if name=='audit-emulator':
        s=s.replace('from inventory import snapshot','from inventory import snapshot\nfrom e_allocation import scan_e')
        s=s.replace("r['integrity_passed']=bool(","r['e_allocation']=scan_e(disk,art/'e-after.json')\nr['integrity_passed']=bool(r['e_allocation']['allocation_consistent'] and ")
    p.write_text(s,newline='\n')
p=k/'Continue-002.ps1';assert not p.exists()
s=(k/'Continue-001.ps1').read_text().replace('pipeline001.json','pipeline002.json')
start=s.index("Stage 'build'");end=s.index('foreach($variant',start)
s=s[:start]+"# Existing reviewed build001 is unchanged; attempt002 modifies fixture preparation only.\n"+s[end:]
for name in ('prepare-emulator','run-emulator','audit-emulator','review-pnp'):s=s.replace(name+'.py',name+'002.py')
s=s.replace("$variant+'001/pnp-review.json'","$variant+'002/pnp-review.json'")
p.write_text(s,newline='\n')
(k/'preparation001-failure.json').write_text(json.dumps(dict(launched=False,closed=True,do_not_relaunch=True,path='control001',failure='No-growth guard rejected HAL replacement requiring a larger E file chain. Guard ran after restore wrote private file/directory blocks but before FAT flush; partial fixture is not bootable/qualified. Original seed untouched.',continuation='Fresh control002/candidate002 use complete E allocation audits before/after replacement and after guest closure; same build001 package and HAL hashes.'),indent=2)+'\n')
(k/'attempt002-inputs.json').write_text(json.dumps(dict(build_manifest_sha256=hashlib.sha256((k/'build001.json').read_bytes()).hexdigest(),sources={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in k.iterdir() if p.suffix in ('.py','.ps1')},scope='Fresh preparation and cold audit only; helper/driver/HAL binaries unchanged.'),indent=2)+'\n')
