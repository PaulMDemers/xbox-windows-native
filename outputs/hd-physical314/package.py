"""Assemble exact tested six-file720p chain and previously qualified physical helpers."""
from common001 import *
dest=k/'package.json';assert not dest.exists()
emu=read(k.parent/'hd-ui313/final-review.json')
assert emu['mode_passed'] and emu['combined']['scoped_combined_passed'] and emu['integrity_passed'] and emu['normal_shutdown_count']==1
assert not emu['activation']['passed'] and not emu['strict_passed'] # Retain failures, do not promote new helper.
baseline=read(k.parent/'hd-ui313/candidate001/fixture.json')['files']
mapping={'/E/Applications/XWNFBoot/default.xbe':pathlib.Path('D:/xwn311/build001/candidate001/default.xbe'),
 '/E/Applications/XWNFBoot/freeldr.sys':pathlib.Path('E:/xwn300/build001/candidate001/freeldr.sys'),
 '/E/Applications/XWNFBoot/rosload.exe':pathlib.Path('E:/xwn300/build001/candidate001/rosload.exe'),
 '/E/Applications/XWNFBoot/loader/xboxbvid.dll':pathlib.Path('E:/xwn300/build001/candidate001/xboxbvid.dll'),
 '/F/winnt/system32/drivers/xboxvnt5.sys':pathlib.Path('E:/xwn300/build001/candidate001/xboxvnt5.sys'),
 '/F/winnt/system32/xwnown.dll':pathlib.Path('D:/xwn303/build003/candidate001/xwnown.dll')}
payload=k/'artifacts/payload';assert not payload.exists();payload.mkdir(parents=True)
rows=[]
for remote,p in mapping.items():
 data=p.read_bytes();assert sha(data)==baseline[remote[1:]],remote
 (payload/p.name).write_bytes(data);rows.append(dict(path=remote,name=p.name,source=str(p),bytes=len(data),sha256=sha(data)))
helpers=read(k.parent/'demo-physical253/package.json')['helpers']
for row in helpers:
 data=pathlib.Path(row['source']).read_bytes();assert sha(data)==row['sha256']
 (payload/row['name']).write_bytes(data)
assert next(v['sha256'] for v in helpers if v['name']=='wizard.exe')=='b3a42114e2d083d3d124cb54199a8d6c3fd63fee5a9ef6b196e4599d28b84fbb'
save(dest,dict(video=rows,helpers=helpers,registry_edits=False,emulator720p_workload_passed=True,emulator_activation_covered=False,strict_emulator_passed=False,physical_qualified=False,release_qualified=False))
print('Exact six-file720p chain and five original physical helpers prepared')
