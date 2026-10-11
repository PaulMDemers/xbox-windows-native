"""Copy an immutable prepared source; never copy or relaunch a used runtime disk."""
import hashlib,json,os,shutil,sys
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent;old=k.parent/'rebalance002';assert sys.argv[1]=='veto'
assert os.environ.get('XWN_BUILD_LEASE')=='held'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
source=old/'veto001/artifacts/source.qcow2';f=read(old/'veto001/fixture.json')
assert read(k/'preflight001.json')['passed'] and sha(source)==f['source_sha256']
out=k/'veto001';assert not out.exists();art=out/'artifacts';art.mkdir(parents=True)
shutil.copyfile(source,art/'source.qcow2');assert sha(art/'source.qcow2')==f['source_sha256']
for name in ['before-'+x for x in ('system','software','default','sam','security')]+['startup.cmd']:
    src=old/'veto001/artifacts'/name;shutil.copyfile(src,art/name);assert sha(src)==sha(art/name)
b=k/'artifacts/build001';b.mkdir(parents=True)
manifest=read(old/'build001.json')
for row in manifest['files']:
    src=old/'artifacts/build001'/row['name'];assert sha(src)==row['sha256'];shutil.copyfile(src,b/row['name'])
f.update(scope=__doc__,debugger_case=True,ordinary_qualified=False,source_parent=str(source),source_parent_fixture_sha256=sha(old/'veto001/fixture.json'),source_copy_exact=True)
(out/'fixture.json').write_text(json.dumps(f,indent=2)+'\n')
assert sha(source)==f['source_sha256']
print('Fresh reopen008 veto fixture copied exactly; no guest/policy changes')
