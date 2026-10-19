"""Drop only verified duplicate staging bytes after preserving the private ZIP."""
from pathlib import Path
import hashlib,json,shutil,sys,zipfile
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'tools'));import tester_bundle as b
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
r=json.loads((K/'windows-package001.json').read_text());assert r['completed']
archive=Path(r['destination']);assert sha(archive)==r['sha256'];b.verify(archive)
base=Path('C:/xwn587').resolve();capture=base/'windows-capture001';stage=base/'windows-staging001'
assert capture.resolve()==capture and stage.resolve()==stage
assert capture.parent==base and stage.parent==base
assert all(not p.is_symlink() and not p.is_junction() for root in (capture,stage) for p in [root,*root.rglob('*')])
manifest=json.loads((capture/'CAPTURE-MANIFEST.json').read_text())
keep=base/'source-exclusions001';keep.mkdir(exist_ok=False)
with zipfile.ZipFile(archive) as z:
    for name,meta in manifest['files'].items():
        p=capture/name.lstrip('/');assert sha(p)==meta['sha256']
        if name.lower().endswith(('.sys.422used','.exe.422used')):
            dst=keep/p.name;shutil.copyfile(p,dst);assert sha(dst)==meta['sha256']
        else:assert hashlib.sha256(z.read(name.lstrip('/'))).hexdigest()==meta['sha256']
dest=base/'capture-manifest001.json';assert not dest.exists();shutil.copyfile(capture/'CAPTURE-MANIFEST.json',dest)
out=K/'staging-cleanup001.json';assert not out.exists()
result={'completed':False,'before_c_free':shutil.disk_usage('C:/').free,'retained_zip':str(archive),'zip_sha256':r['sha256'],'retained_original_exclusions':str(keep),'retained_capture_manifest':str(dest),'removed':[],'scope':'Only two newly created delivery587 duplicate host staging trees. No guest disk, console file or historical recovery capture.'}
def save():out.write_text(json.dumps(result,indent=2)+'\n')
save()
for root in (stage,capture):
    assert root.resolve()==root and root.parent==base and root.name in ('windows-staging001','windows-capture001')
    shutil.rmtree(root);result['removed'].append(str(root));save()
result.update(completed=True,after_c_free=shutil.disk_usage('C:/').free);save();print(json.dumps(result))
