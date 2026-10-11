"""New user-authorized audible repeat, with unchanged drivers and a unique test directory."""
from common001 import *
import ast,shutil
parent=canonical/'outputs/demo-physical253';assert read(parent/'accepted-state.json')['passed']
assert read(parent/'combined001/binding-transition-review.json')['supplemental_scoped_combined_passed']
dest=k/'capture002.json';assert not dest.exists() and not (k/'artifacts/before002').exists()
prior=read(parent/'combined001/collection.json');assert prior['completed'] and prior['startup_restored']
r=dict(passed=False,physical_writes=False,physical_access=False,files={},inventories=prior['inventories'],source='Exact accepted253 cold collection, validated again by hardware preflight',source_collection_sha256=sha((parent/'combined001/collection.json').read_bytes()))
for path,row in prior['files'].items():
    if row is None:continue
    data=(parent/'artifacts/combined001'/path.lstrip('/')).read_bytes();assert sha(data)==row['sha256']
    r['files'][path]=keep(k/'artifacts/before002',path,data)
r['passed']=True;save(dest,r)
shutil.copyfile(parent/'providers001.json',k/'providers001.json')
shutil.copytree(canonical/'outputs/demo-physical252/artifacts/payload',k/'artifacts/payload')
helpers()
frozen={}
for p in [*k.glob('*.py'),k/'PLAN.md',k/'capture002.json',k/'providers001.json',*list((k/'artifacts/payload').rglob('*')),parent/'combined001/audit.json',parent/'accepted-state.json',parent/'combined001/collection.json',parent/'package.json',parent/'combined001/binding-transition-review.json',canonical/'outputs/native-windows-fatx-preflight/artifacts/default.xbe']:
    if not p.is_file():continue
    if p.suffix=='.py':ast.parse(p.read_text())
    frozen[str(p)]=sha(p.read_bytes())
save(k/'frozen001.json',frozen)
print('Fresh audition255 prepared; no driver/configuration changes and no launch yet')
