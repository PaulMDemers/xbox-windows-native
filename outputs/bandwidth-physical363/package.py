import hashlib,json,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=K.parent/'hd-phase-physical347';dest=K/'package.json';out=Path('E:/xwn363/payload');assert not dest.exists() and not out.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(K.parent/'bandwidth361/binary-review001.json')['passed']
out.mkdir(parents=True);helpers=[]
for row in read(P/'package.json')['helpers']:
 src=Path('E:/xwn347/payload')/row['name'];assert sha(src)==row['sha256']
 if row['name']=='replay.exe':src=Path('E:/xwn361/probe/build001/replay.exe');assert sha(src)==read(K.parent/'bandwidth361/probe/build-review001.json')['binary_sha256']
 target=out/row['name'];shutil.copyfile(src,target);assert target.read_bytes()==src.read_bytes()
 helpers.append(dict(name=target.name,sha256=sha(target),bytes=target.stat().st_size,source=str(src)))
dest.write_text(json.dumps(dict(prepared=True,helpers=helpers,physical_helper_original201=True,experimental_helper338_deployed=False,physical_writes=False),indent=2)+'\n')
print('Private353 package prepared; no console access')
