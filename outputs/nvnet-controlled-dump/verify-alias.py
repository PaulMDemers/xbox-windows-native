"""Validate exact intended dump at the wrong 28-bit alias, never declare PASS."""
import hashlib,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'crash003';a=json.loads((out/'audit.json').read_text());before=(out/'artifacts/before-alias.bin').read_bytes();after=(out/'artifacts/after-alias.bin').read_bytes()
assert after[:8]==b'PAGEDUMP' and [hex(v) for v in struct.unpack_from('<5I',after,0x28)]==['0xe058d103','0x44554d50','0x103','0x10000','0x1']
assert a['pagefile_disk_offset']-a['lba28_alias_offset']==1<<37 and a['alias_writes'] and not a['alias_unchanged']
assert a['pagefiles'][1]['header8']==b'PAGEPAGE'.hex() and not a['dump_write_evidence_passed']
r=dict(physical_access=False,intended_header_at_wrong_address=True,intended_disk_offset=a['pagefile_disk_offset'],actual_alias_offset=a['lba28_alias_offset'],difference_bytes=1<<37,changed_alias_bytes=sum(x!=y for x,y in zip(before,after)),before_sha256=hashlib.sha256(before).hexdigest(),after_sha256=hashlib.sha256(after).hexdigest(),writes=a['alias_writes'],dump_qualified=False,recovery_allowed=False,limits='Cold header and block trace prove wrong destination. Precise truncation producer remains unlocalized. Metadata/protected-file audit does not establish all file contents were unaffected.')
(k/'alias-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
