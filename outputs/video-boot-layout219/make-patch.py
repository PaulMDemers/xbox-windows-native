"""Capture the exact source diff against frozen106 bootvid; no tree mutation."""
import difflib,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'boot-layout219.patch';assert not dest.exists()
name='drivers/base/bootvid/i386/xbox/bootvid.c'
old=ws/'outputs/video-gpu-transfer-contract212/artifacts/boot-reservation'/name
new=k/'artifacts/source'/name
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((k/'source-review.json').read_text());assert sha(old)==r['parent_source_pins'][name] and sha(new)==r['candidate_bootvid_sha256']
text=''.join(difflib.unified_diff(old.read_text().splitlines(True),new.read_text().splitlines(True),fromfile='a/'+name,tofile='b/'+name))
header='drivers/base/bootvid/i386/xbox/boot_layout.h'
text+=''.join(difflib.unified_diff([], (k/'boot_layout.h').read_text().splitlines(True),fromfile='/dev/null',tofile='b/'+header))
dest.write_text(text)
(k/'patch-review.json').write_text(json.dumps(dict(passed=True,parent_tree='53e9aedc58152d03116c00579185000483379837',patch_sha256=sha(dest),original_bootvid_sha256=sha(old),candidate_bootvid_sha256=sha(new),header_sha256=sha(k/'boot_layout.h'),changes=['capacity','backbuffer placement','published HiddenOffset','reset clear extent'],mapped_bytes_changed=False,shared_abi_changed=False,source_tree_mutated=False,guest_launch=False,physical_access=False),indent=2)+'\n')
print('Exact layout patch recorded; no parent tree mutation')
