"""Add only the runtime-demonstrated NT5 paging-file dump mapping contract."""
import difflib,hashlib,json,os,subprocess,tempfile
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];prior=k.parent/'hal-dump-path'
src=Path('/home/paul/xbox-windows-native/build/hal-dump-path-002/source')
m=json.loads((prior/'manifest.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
assert subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()==m['result_tree']
subprocess.run(['git','-C',str(src),'diff','--quiet'],check=True)
rel='drivers/filesystems/vfatfs/fsctl.c';old=(src/rel).read_text()
assert sha((src/rel).read_bytes())==json.loads((k.parent/'dump-fsctl-trace/contract-review.json').read_text())['owned_source_sha256'][rel]
fragment=(k/'dump-map.inc').read_text();needle='static\nNTSTATUS\nVfatGetRetrievalPointers('
assert old.count(needle)==1;new=old.replace(needle,fragment+'\n'+needle)
needle='''                case FSCTL_GET_RETRIEVAL_POINTERS:
                    Status = VfatGetRetrievalPointers(IrpContext);
                    break;'''
assert new.count(needle)==1
new=new.replace(needle,'''                case FSCTL_QUERY_RETRIEVAL_POINTERS:
                    Status = VfatQueryRetrievalPointers(IrpContext);
                    break;

'''+needle)
patch=k/'0103-vfat-paging-dump-mapping.patch';assert not patch.exists()
patch.write_bytes(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel)).encode())
with tempfile.TemporaryDirectory() as tmp:
    env=dict(os.environ,GIT_INDEX_FILE=tmp+'/index')
    subprocess.run(['git','-C',str(src),'read-tree',m['result_tree']],env=env,check=True)
    subprocess.run(['git','-C',str(src),'apply','--cached',str(patch)],env=env,check=True)
    tree=subprocess.check_output(['git','-C',str(src),'write-tree'],env=env,text=True).strip()
m.update(scope=__doc__,previous_tree=m['result_tree'],result_tree=tree,caveat='Experimental dump extent query only; successful configuration is not real crash-dump write/recovery qualification.')
m['patches'].append(str(patch.relative_to(ws)));(k/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
l=json.loads((prior/'inputs.json').read_text());l.update(result_tree=tree,manifest=str((k/'manifest.json').relative_to(ws)),manifest_json_sha256=sha(json.dumps(m,sort_keys=True,separators=(',',':')).encode()))
l['patch_sha256'][str(patch.relative_to(ws))]=sha(patch.read_bytes())
l['profiles']=json.loads((k.parent/'fatx-directory-order/inputs.json').read_text())['profiles']
(k/'inputs.json').write_text(json.dumps(l,indent=2)+'\n')
c=json.loads((prior/'inputs.json').read_text());c['profiles']=l['profiles'];(k/'control-inputs.json').write_text(json.dumps(c,indent=2)+'\n')
for name,lock in [('build.py','inputs.json'),('build-control.py','control-inputs.json')]:
    (k/name).write_text((prior/'build.py').read_text().replace('outputs/hal-dump-path/inputs.json','outputs/fatx-dump-map/'+lock))
(k/'artifacts').mkdir(exist_ok=True);(k/'artifacts/fsctl.c').write_text(new)
print(tree)
