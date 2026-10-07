"""Preserve rejected first build; remove the matching pageable declaration too."""
import difflib,hashlib,json,os,subprocess,tempfile
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];src=Path('/home/paul/xbox-windows-native/build/fatx-dump-map-001/source')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
saved=k/'preliminary-build001';assert not saved.exists();saved.mkdir()
for n in ['prepare-source.py','inputs.json','manifest.json','0104-nvnet-resident-shutdown-helper.patch','review-nvnet.py','nvnet-build-candidate001.json']:
    (saved/n).write_bytes((k/n).read_bytes())
(saved/'rejection.json').write_text(json.dumps(dict(reason='Binary residency gate rejected candidate001: declaration in nvnet.h still CODE_SEG PAGE. No guest launched with this build.',binary_sha256=sha(k/'artifacts/nvnet-candidate001.sys'),build='/home/paul/xbox-windows-native/build/nvnet-shutdown-resident-001',physical_access=False),indent=2)+'\n')
(k/'artifacts/nvnet-rejected-build001.sys').write_bytes((k/'artifacts/nvnet-candidate001.sys').read_bytes())
(k/'artifacts/nvnet-candidate001.sys').unlink()
rel='drivers/network/dd/nvnet/nvnet.h';old=(src/rel).read_text();needle='CODE_SEG("PAGE")\nVOID\nNvNetIdleTransmitter('
assert old.count(needle)==1;new=old.replace(needle,'VOID\nNvNetIdleTransmitter(')
patch=k/'0104-nvnet-resident-shutdown-helper.patch'
data=patch.read_bytes()+''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel)).encode();patch.write_bytes(data)
m=read(k/'manifest.json')
with tempfile.TemporaryDirectory() as tmp:
    env=dict(os.environ,GIT_INDEX_FILE=tmp+'/index');subprocess.run(['git','-C',str(src),'read-tree',m['previous_tree']],env=env,check=True);subprocess.run(['git','-C',str(src),'apply','--cached',str(patch)],env=env,check=True);tree=subprocess.check_output(['git','-C',str(src),'write-tree'],env=env,text=True).strip()
m['result_tree']=tree;(k/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
l=read(k/'inputs.json');l.update(result_tree=tree,manifest_json_sha256=hashlib.sha256(json.dumps(m,sort_keys=True,separators=(',',':')).encode()).hexdigest());l['patch_sha256'][str(patch.relative_to(ws))]=sha(patch);(k/'inputs.json').write_text(json.dumps(l,indent=2)+'\n')
(k/'artifacts/nvnet.h').write_text(new);print(tree)
