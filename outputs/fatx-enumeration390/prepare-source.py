import difflib,hashlib,json,os,subprocess,tempfile
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];prior=K.parent/'fatx-directory-order'
src=Path('/home/paul/xbox-windows-native/build/fatx-directory-order-001/source')
m=json.loads((prior/'manifest.json').read_text());tree=m['result_tree']
assert tree=='8e12297ca0ed53383fe9aaebef152c26aee5a43b'
rel='drivers/filesystems/vfatfs/create.c'
old=subprocess.check_output(['git','-C',str(src),'show',tree+':'+rel]).decode()
assert hashlib.sha256(old.encode()).hexdigest()=='025d3bc54e6a7f7f9f1a8564d8fd00017322df27359203d332493e982240f400'
a='                DirContext->StartIndex = rcFcb->startIndex;\n                DirContext->DirIndex = rcFcb->dirIndex;'
b=a+'''
                /* Cached FATX FCB indices are physical slots. Directory queries
                 * use logical indices including the two synthetic dot entries,
                 * as the uncached FATX directory-entry path does. */
                if (IsFatX && !vfatFCBIsRoot(Parent))
                {
                    DirContext->StartIndex += 2;
                    DirContext->DirIndex += 2;
                }'''
assert old.count(a)==1;new=old.replace(a,b)
patch=K/'0390-vfat-cached-fatx-logical-indices.patch';assert not patch.exists()
patch.write_bytes(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel)).encode())
with tempfile.TemporaryDirectory() as t:
    env=dict(os.environ,GIT_INDEX_FILE=t+'/index')
    subprocess.run(['git','-C',str(src),'read-tree',tree],env=env,check=True)
    subprocess.run(['git','-C',str(src),'apply','--cached',str(patch)],env=env,check=True)
    result=subprocess.check_output(['git','-C',str(src),'write-tree'],env=env,text=True).strip()
m.update(previous_tree=tree,result_tree=result,scope='Candidate0390 cached FATX query index normalization; no runtime or physical qualification yet',working_tree_matches_chain=False,caveat='Source-only isolated-index application; full reconstruction and guest tests required. Host388 models ancillary helpers only.')
m['patches'].append(patch.relative_to(W).as_posix());(K/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
l=json.loads((prior/'inputs.json').read_text())
l.update(result_tree=result,manifest=(K/'manifest.json').relative_to(W).as_posix(),manifest_json_sha256=hashlib.sha256(json.dumps(m,sort_keys=True,separators=(',',':')).encode()).hexdigest())
l['patch_sha256'][patch.relative_to(W).as_posix()]=hashlib.sha256(patch.read_bytes()).hexdigest()
(K/'inputs.json').write_text(json.dumps(l,indent=2)+'\n')
(K/'build.py').write_bytes((prior/'build.py').read_bytes().replace(b'outputs/fatx-directory-order/inputs.json',b'outputs/fatx-enumeration390/inputs.json'))
(K/'source-review.json').write_text(json.dumps({'prior_tree':tree,'candidate_tree':result,'only_changed_path':rel,'before_sha256':hashlib.sha256(old.encode()).hexdigest(),'after_sha256':hashlib.sha256(new.encode()).hexdigest(),'shared_working_source_changed':False,'temporary_index_only':True,'driver_built':False,'physical_access':False},indent=2)+'\n')
print(result)
