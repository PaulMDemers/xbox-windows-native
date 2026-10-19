"""MIT. Read back every helper ISO payload before admitting a fresh guest."""
import hashlib,io,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));import pycdlib
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
out=K/'media-review001.json'; assert not out.exists()
media=json.loads((K/'media001.json').read_text()); p=Path(media['path'])
assert sha(p)==media['sha256']
package=K.parent/'rct565/package001.json'; assert sha(package)==media['source_package_sha256']
expected={n:r['sha256'] for n,r in json.loads(package.read_text())['files'].items() if n.startswith('game/')}
expected.update({'RUN574.EXE':media['runner_sha256'],'PREP.CMD':hashlib.sha256(media['copy_script'].encode('ascii')).hexdigest()})
assert len({n.lower() for n in expected})==len(expected)
iso=pycdlib.PyCdlib(); iso.open(str(p)); observed={}
try:
    for root,dirs,files in iso.walk(joliet_path='/'):
        for name in files:
            path=(root.rstrip('/')+'/'+name).lstrip('/')
            assert path in expected,path
            fp=io.BytesIO();iso.get_file_from_iso_fp(fp,joliet_path='/'+path)
            observed[path]=hashlib.sha256(fp.getbuffer()).hexdigest()
finally:iso.close()
assert observed==expected
out.write_bytes((json.dumps(dict(passed=True,files=len(observed),media_sha256=media['sha256'],source_package_sha256=media['source_package_sha256'],payloads=observed,physical_access=False),indent=2)+'\n').encode())
print('Every helper ISO payload matches:',len(observed))
