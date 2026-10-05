import json,os,subprocess,tempfile,hashlib
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
src=Path('/home/paul/xbox-windows-native/build/video-direct-ram-001/source')
m=json.loads((k/'manifest.json').read_text())
with tempfile.TemporaryDirectory() as tmp:
 env=dict(os.environ,GIT_INDEX_FILE=tmp+'/index')
 subprocess.run(['git','-C',str(src),'read-tree',m['previous_tree']],env=env,check=True)
 subprocess.run(['git','-C',str(src),'apply','--cached',str(k/'0096-video-owned-direct-ram-mapping.patch')],env=env,check=True)
 tree=subprocess.check_output(['git','-C',str(src),'write-tree'],env=env,text=True).strip()
m['result_tree']=tree;(k/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
l=json.loads((k/'inputs.json').read_text());l['result_tree']=tree;l['manifest_json_sha256']=hashlib.sha256(json.dumps(m,sort_keys=True,separators=(',',':')).encode()).hexdigest();(k/'inputs.json').write_text(json.dumps(l,indent=2)+'\n');print(tree)
