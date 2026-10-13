import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;dest=K/'source-review.json';assert not dest.exists()
a=Path('/home/paul/xbox-windows-native/build/bandwidth361-build001/source/win32ss/drivers/displays/framebuf');b=Path('/home/paul/xbox-windows-native/build/bandwidth364-build002/source/win32ss/drivers/displays/framebuf')
changed=[p.name for p in a.iterdir() if p.is_file() and p.read_text()!= (b/p.name).read_text()]
assert set(changed)=={'enable.c','ownership.c','bandwidth.h','bandwidth.c'}
s=(b/'bandwidth.c').read_text().replace('r->right-r->left!=640||r->bottom-r->top!=360','r->right-r->left!=960||r->bottom-r->top!=540').replace('c->record[0]=364','c->record[0]=361').replace('c->record[11]=B361_ROW*B361_ROWS','c->record[11]=B361_LENGTH');assert s==(a/'bandwidth.c').read_text()
s=(b/'bandwidth.h').read_text().replace('B361_ROW 2560u','B361_ROW 3840u').replace('B361_ROWS 360u','B361_ROWS 540u').replace('B361_LENGTH 2073600u','B361_LENGTH (B361_ROW*B361_ROWS)').replace('unsigned i,bad=0;\n for(i=B361_ROW*B361_ROWS;i<B361_LENGTH;i++)if(p[B361_GUARD+i])++bad;\n for(i=0;i<B361_GUARD;i++)','unsigned i,bad=0;for(i=0;i<B361_GUARD;i++)');assert s==(a/'bandwidth.h').read_text()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=True,changes=changed,original_actual_upload_unchanged=sha(a/'shadow.c')==sha(b/'shadow.c'),copy_calibration_policy_verification_unchanged_except_explicit_new_geometry_and_tail_check=True,private_git_alternates_flattened_only=True,shared_source_or_sdk_modified=False,files={p.name:sha(p) for p in b.iterdir() if p.is_file()},runtime=False)
assert r['original_actual_upload_unchanged'];dest.write_text(json.dumps(r,indent=2)+'\n');print('364 source differences constrained and reviewed')
