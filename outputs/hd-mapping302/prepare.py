"""Copy only the unused301 candidate preparation; never parent a runtime disk."""
import hashlib,json,shutil,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
old=k.parent/'hd-reservation301/candidate001';f=json.loads((old/'fixture.json').read_text())
src=Path(f['fixture_path_windows']);assert src==Path('D:/xwn301/fixtures/candidate001/source.qcow2')
assert sha(src)==f['fixture_sha256'] and not (k/'candidate001').exists()
assert shutil.disk_usage('C:/').free>20*1024**3+64*1024**2
assert shutil.disk_usage('D:/').free>20*1024**3+src.stat().st_size*2+512*1024**2
private=Path('D:/xwn302/fixtures/candidate001');private.mkdir(parents=True,exist_ok=False)
target=private/'source.qcow2';shutil.copyfile(src,target);assert sha(target)==f['fixture_sha256']
out=k/'candidate001';out.mkdir();shutil.copytree(old/'artifacts',out/'artifacts',ignore=shutil.ignore_patterns('*'))
for n in ['system','software','default','sam','security']:
    shutil.copyfile(old/'artifacts'/('before-'+n),out/'artifacts'/('before-'+n))
f.update(parent='/mnt/d/xwn301/fixtures/candidate001/source.qcow2',parent_sha256=f['fixture_sha256'],
         fixture_path_windows=target.as_posix(),fixture_path_linux='/mnt/d/xwn302/fixtures/candidate001/source.qcow2',
         debugger=True,ordinary_qualified=False,physical_access=False,
         preparation_source_manifest_sha256=sha(old/'fixture.json'),
         limits='Byte-exact unused301 candidate preparation. One bounded read-only physical snapshot; diagnostic, not ordinary qualification.')
(out/'fixture.json').write_text(json.dumps(f,indent=2)+'\n')
print('Fresh byte-exact candidate preparation copied and hashed')
