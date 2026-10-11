"""New user-authorized audible repeat, with unchanged drivers and a unique test directory."""
from common001 import *
import ast,shutil
parent=canonical/'outputs/demo-audition255';assert read(parent/'accepted-state.json')['passed']
assert read(parent/'playback001/audit.json')['scoped_runtime_passed']
dest=k/'capture002.json';assert not dest.exists() and not (k/'artifacts/before002').exists()
prior=read(parent/'playback001/collection.json');assert prior['completed'] and prior['startup_restored']
r=dict(passed=False,physical_writes=False,physical_access=False,files={},inventories=prior['inventories'],source='Exact accepted255 cold collection, validated again by hardware preflight',source_collection_sha256=sha((parent/'playback001/collection.json').read_bytes()))
for path,row in prior['files'].items():
    if row is None:continue
    data=(parent/'artifacts/playback001'/path.lstrip('/')).read_bytes();assert sha(data)==row['sha256']
    r['files'][path]=keep(k/'artifacts/before002',path,data)
r['passed']=True;save(dest,r)
shutil.copyfile(parent/'providers001.json',k/'providers001.json')
shutil.copytree(canonical/'outputs/demo-physical252/artifacts/payload',k/'artifacts/payload')
review=read(k/'helper-review001.json');assert review['passed']
probe=k/'artifacts/build003/probe.exe';assert sha(probe.read_bytes())==review['binary_sha256']
shutil.copyfile(probe,k/'artifacts/payload/verify/probe.exe')
manifest=read(k/'artifacts/payload/MANIFEST.json')
manifest['files']['verify/probe.exe']=dict(bytes=probe.stat().st_size,sha256=sha(probe.read_bytes()))
manifest['new_helper']='demo-audio-level256/build003';save(k/'artifacts/payload/MANIFEST.json',manifest)
helpers()
frozen={}
for p in [*k.glob('*.py'),*k.glob('*.c'),*k.glob('*.h'),*k.glob('*.ps1'),k/'helper-review001.json',k/'build003.json',k/'PLAN.md',k/'capture002.json',k/'providers001.json',*list((k/'artifacts/payload').rglob('*')),parent/'playback001/audit.json',parent/'accepted-state.json',parent/'playback001/collection.json',canonical/'outputs/demo-physical253/package.json',canonical/'outputs/demo-physical253/combined001/binding-transition-review.json',canonical/'outputs/native-windows-fatx-preflight/artifacts/default.xbe']:
    if not p.is_file():continue
    if p.suffix=='.py':ast.parse(p.read_text())
    frozen[str(p)]=sha(p.read_bytes())
save(k/'frozen001.json',frozen)
print('Fresh level256 prepared; no driver/configuration changes and no launch yet')
