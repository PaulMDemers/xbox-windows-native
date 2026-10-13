"""Prepare the exact recovered HD overlay plus emulator-qualified large probe."""
import zipfile
from common001 import *
dest=k/'package.json';assert not dest.exists()
emu=read(k.parent/'hd-large-runtime330/emu001/final-review.json')
assert emu['scoped_passed'] and emu['large_passed'] and emu['integrity_passed'] and emu['normal_shutdown_count']==1
baseline=read(k.parent/'hd-large-runtime330/emu001/fixture.json')['files']
archive=pathlib.Path('E:/Codex-archive/xbox-windows-native/0.2.0-recovered329/xwn-0.2.0-hd-overlay.zip')
assert sha(archive.read_bytes())=='474957aa6d2eb4cd8c3818a26ad0568e4b9c104b8159891c065b1491c8f6930d'
payload=k/'artifacts/payload';assert not payload.exists();payload.mkdir(parents=True)
rows=[]
with zipfile.ZipFile(archive) as z:
 for n in z.namelist():
  if not n.startswith('1080i/'):continue
  remote='/'+n[len('1080i/'):];data=z.read(n);name=remote.rsplit('/',1)[1]
  assert sha(data)==baseline[remote[1:]],remote
  (payload/name).write_bytes(data)
  rows.append(dict(path=remote,name=name,source=str(archive)+'!'+n,bytes=len(data),sha256=sha(data)))
assert len(rows)==6
helpers=read(k.parent/'demo-physical253/package.json')['helpers']
probe=pathlib.Path('E:/xwn327/build003/replay.exe');review=read(k.parent/'hd-large327/build-review003.json')
assert review['passed'] and sha(probe.read_bytes())==review['binary_sha256']
for row in helpers:
 if row['name']=='replay.exe':
  row.update(source=str(probe),bytes=probe.stat().st_size,sha256=review['binary_sha256'])
 data=pathlib.Path(row['source']).read_bytes();assert len(data)==row['bytes'] and sha(data)==row['sha256']
 (payload/row['name']).write_bytes(data)
assert next(v['sha256'] for v in helpers if v['name']=='wizard.exe')=='b3a42114e2d083d3d124cb54199a8d6c3fd63fee5a9ef6b196e4599d28b84fbb'
save(dest,dict(video=rows,helpers=helpers,registry_edits=False,
 emulator1080i_workload_passed=True,emulator_large_probe_passed=True,
 helper_from_original_physical201=True,strict_emulator_passed=emu['strict_passed'],
 physical_qualified=False,release_qualified=False,physical_writes=False))
print('Exact HD overlay and new327 replay prepared; original physical helper retained')
