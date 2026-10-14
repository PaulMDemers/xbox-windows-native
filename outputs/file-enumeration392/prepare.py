"""Fresh copy of never-executed391 preparation, never its failed staging disk."""
import hashlib,json,os,shutil,sys
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]; case=sys.argv[1]
assert case=='candidate001' and os.environ.get('XWN_BUILD_LEASE')=='held'
old=K.parent/'file-enumeration391'/case; out=K/case
source=Path('/mnt/c/xwn391/candidate001/source.qcow2'); dest=Path('/mnt/c/xwn392/candidate001/source.qcow2')
assert not out.exists() and not dest.parent.exists()
f=json.loads((old/'fixture.json').read_text()); c=json.loads((old/'closure.json').read_text())
assert c['closed'] and not c['guest_started']
assert not Path('/mnt/c/xwn391/runs/nt5-enumeration391-candidate001/instance.json').exists()
def sha(p):
 with p.open('rb') as fp:return hashlib.file_digest(fp,'sha256').hexdigest()
assert sha(source)==f['fixture_sha256']
assert shutil.disk_usage('/mnt/c').free-source.stat().st_size-2*1024**3>=20*1024**3
out.mkdir();dest.parent.mkdir(parents=True);shutil.copyfile(source,dest)
assert sha(dest)==f['fixture_sha256']
shutil.copytree(old/'artifacts',out/'artifacts');shutil.copytree(old/'before-allocation',out/'before-allocation')
f.update(fixture_path_linux=str(dest),fixture_path_windows='C:/xwn392/candidate001/source.qcow2')
(out/'fixture.json').write_text(json.dumps(f,indent=2)+'\n')
r=json.loads((old/'preparation.json').read_text())
r.update(copy_of_never_executed_preparation=str(source),copied_preparation_sha256=sha(old/'preparation.json'),new_raw_conversion=False,source_sha256=sha(dest))
(out/'preparation.json').write_text(json.dumps(r,indent=2)+'\n')
print('Fresh392 exact unused seed copy; workload namespace remains xwnenumeration391')
