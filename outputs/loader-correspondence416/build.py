"""Fresh-compiler canonical-path discriminator; no guest or console access."""
import copy
import datetime
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'tools'))
import xwn
from build_space import require_space

assert os.environ.get('XWN_BUILD_LEASE')=='held'
record=K/'build001.json';assert not record.exists()
base=Path('/home/paul/xbox-windows-native')
boot=base/'release-readiness403-bootstrap001'
cache=base/'release-readiness403-dependencies001/reactos'
manifest=json.loads((W/'upstream/components.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
originals={'hal':'/home/paul/xbox-windows-native/sources/reactos-extended',
           'loader':'/home/paul/xbox-windows-native/build/stock-boot334-build001/reactos'}
space=require_space(base)
for item in space['checks']:
    assert item['free_bytes']-2*1024**3>=20*1024**3,'Projected 2GiB build reserve'
r=dict(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='building',
       physical_access=False,guest_launch=False,projected_reserve_bytes=2*1024**3,
       space=space,cases={},inputs={str(p.relative_to(W)):sha(p) for p in
       [K/'build.py',W/'tools/xwn.py',W/'tools/build_space.py',W/'tools/toolchain_receipt.py',W/'upstream/components.json']})
def save():record.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
    for name,canonical in originals.items():
        stem=str(base/(name+'416001'))
        padding=len(canonical)-len(stem+'/source')
        assert padding>=0
        out=Path(stem+'x'*padding)
        p=copy.deepcopy(next(p for p in manifest['profiles'] if p['name']==name))
        source,s=xwn.materialize(p,cache,out)
        assert len(str(source))==len(canonical)
        flags='-fmacro-prefix-map='+str(source)+'='+canonical
        p['build']['definitions']['CMAKE_C_FLAGS']=flags
        r['cases'][name]=dict(output=str(out),source=str(source),canonical=canonical,
                              source_path_bytes=len(str(source)),flags=flags,status='building')
        save()
        result=xwn.build(p,source,out,boot/'RosBE-2.2.1',None,manifest,4,boot/'toolchain.json')
        dest=K/(name+'001');dest.mkdir()
        for filename in ['source.json','build.json','build-command.json']:
            shutil.copyfile(out/filename,dest/filename)
        r['cases'][name].update(status='compiled',result=result,log_sha256=sha(out/'build.log'))
        assert xwn.run(['git','-C',source,'write-tree'])==s['tree']
        assert not xwn.run(['git','-C',source,'diff','--name-only'])
        save()
    r['status']='compiled'
except BaseException as e:
    r.update(status='failed',error=repr(e));raise
finally:
    r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
    print(json.dumps(dict(status=r['status'],cases={k:v['status'] for k,v in r['cases'].items()})),flush=True)
