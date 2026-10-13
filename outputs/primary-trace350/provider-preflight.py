"""Read exact five module bytes from NEVER-executed prepared child before trace."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'candidate001';dest=K/'provider-preflight001.json';assert not dest.exists()
sys.path.insert(0,str(K.parent/'video-text-oracle206'));from common import ColdIO
from stock_io002 import readers
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
f=read(out/'fixture.json');image=Path(f['fixture_path_linux']);assert sha(image.read_bytes())==f['fixture_sha256'];rows={}
with ColdIO(image) as disk:
    volume=readers(disk,image)['E']
    for name,m in read(K/'sites002.json')['modules'].items():
        path=(f['namespace']+'/' if name=='replay.exe' else 'winnt/system32/')+name
        data=volume.read(path);assert sha(data)==m['sha256'],name
        rows[name]=dict(path=path,bytes=len(data),sha256=sha(data))
dest.write_text(json.dumps(dict(passed=True,prepared_fixture_sha256=f['fixture_sha256'],modules=rows,read_only=True,physical_access=False),indent=2)+'\n')
print('All five actual prepared fixture modules match local binary pins')
