import copy,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];sys.path.insert(0,str(W/'tools'));import xwn
manifest=json.loads((W/'upstream/components.json').read_text());p=copy.deepcopy(next(p for p in manifest['profiles'] if p['name']=='hal'))
out=Path('/home/paul/xbox-windows-native/hal403002xxxxxxxx')
source,record=xwn.materialize(p,Path('/home/paul/xbox-windows-native/release-readiness403-dependencies001/reactos'),out)
flags='-fmacro-prefix-map='+str(source)+'=/home/paul/xbox-windows-native/sources/reactos-extended'
p['build']['definitions']['CMAKE_C_FLAGS']=flags
r=xwn.build(p,source,out,Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1'),None,manifest,4)
(K/'hal-path-build002.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
