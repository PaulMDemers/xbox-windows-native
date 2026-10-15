import hashlib,json,subprocess,shutil
from pathlib import Path
root=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
cache=Path('/home/paul/xbox-windows-native/build/reconstruction-005/source')
old=json.loads((root/'outputs/reproducible-build/inputs.json').read_text())
base=old['base_commit'];tree=old['result_tree']
assert subprocess.check_output(['git','-C',str(cache),'cat-file','-t',tree],text=True).strip()=='tree'
archive=root/'outputs/release-readiness403/prior402';archive.mkdir(exist_ok=False)
shutil.copyfile(root/'upstream/components.json',archive/'components.json')
shutil.copyfile(root/'tools/xwn.py',archive/'xwn.py')
overlay=root/'src/platform/nt5';overlay.mkdir(parents=True,exist_ok=False)
entries=[]
for p in subprocess.check_output(['git','-C',str(cache),'diff','--name-only','--no-renames','-z',base,tree]).decode().strip('\0').split('\0'):
    info=subprocess.check_output(['git','-C',str(cache),'ls-tree',tree,'--',p]).decode().strip()
    if not info:entries.append({'path':p,'action':'delete'});continue
    mode,kind,obj=info.split('\t')[0].split();assert kind=='blob' and mode in ['100644','100755']
    data=subprocess.check_output(['git','-C',str(cache),'cat-file','blob',obj]);assert b'\0' not in data
    dest=overlay/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);dest.chmod(0o755 if mode=='100755' else 0o644)
    entries.append({'path':p,'action':'write','mode':mode,'sha256':hashlib.sha256(data).hexdigest()})
manifest=json.loads((root/'upstream/components.json').read_text())
for name,oldprofile,target,artifact in [('hal','boot','halxboxnt5','hal/halx86/xboxnt5/halxboxnt5.dll'),('network','support','nvnetnt5','drivers/network/dd/nvnet/nvnetnt5.sys')]:
    defs=old['profiles'][oldprofile]['definitions']
    manifest['profiles'].append({'name':name,'upstream':'reactos','base_commit':base,'reference_tree':tree,'overlay':'src/platform/nt5','files':entries,'build':{'definitions':defs,'targets':[target]},'artifacts':{artifact:Path(artifact).name},'checkout_byte_rules':[]})
(root/'upstream/components.json').write_text(json.dumps(manifest,indent=2)+'\n')
(root/'outputs/release-readiness403/platform-import001.json').write_text(json.dumps({'source_tree':tree,'files':len(entries),'prior_manifest_sha256':hashlib.sha256((archive/'components.json').read_bytes()).hexdigest(),'scope':'Source inventory and recorded configurations; HAL binary differences remain to investigate'},indent=2)+'\n')
print(len(entries),tree)
