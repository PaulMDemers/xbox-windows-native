"""Separate build with original generated version metadata, not a new revision claim."""
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
record=K/'build002.json';assert not record.exists()
base=Path('/home/paul/xbox-windows-native')
canonical=str(base/'build/stock-boot334-build001/reactos')
stem=str(base/'loader416002');out=Path(stem+'x'*(len(canonical)-len(stem+'/source')))
boot=base/'release-readiness403-bootstrap001'
space=require_space(base)
assert all(v['free_bytes']-1024**3>=20*1024**3 for v in space['checks'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original=base/'build/stock-boot334-build001/nt5/sdk/include/reactos/buildno.h'
expected=original.read_bytes()
assert b'20261013-unknown-revision' in expected
manifest=json.loads((W/'upstream/components.json').read_text())
p=copy.deepcopy(next(p for p in manifest['profiles'] if p['name']=='loader'))
r=dict(status='building',output=str(out),space=space,physical_access=False,guest_launch=False,
       started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
       original_generated_header_sha256=sha(original),
       source_date_epoch=int(datetime.datetime(2026,10,13,tzinfo=datetime.timezone.utc).timestamp()),
       purpose='Reconstruct original version metadata solely for binary correspondence',
       input_script_sha256=sha(K/'build-loader002.py'))
def save():record.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
    source,src=xwn.materialize(p,base/'release-readiness403-dependencies001/reactos',out)
    assert len(str(source))==len(canonical)
    p['build']['definitions'].update(CMAKE_C_FLAGS='-fmacro-prefix-map='+str(source)+'='+canonical,
                                     CMAKE_DISABLE_FIND_PACKAGE_Git='ON')
    os.environ['SOURCE_DATE_EPOCH']=str(r['source_date_epoch'])
    result=xwn.build(p,source,out,boot/'RosBE-2.2.1',None,manifest,4,boot/'toolchain.json')
    generated=out/'build/sdk/include/reactos/buildno.h'
    r.update(result=result,generated_header_sha256=sha(generated),generated_header_exact=generated.read_bytes()==expected,
             log_sha256=sha(out/'build.log'))
    assert r['generated_header_exact']
    assert xwn.run(['git','-C',source,'write-tree'])==src['tree']
    assert not xwn.run(['git','-C',source,'diff','--name-only'])
    dest=K/'loader002';dest.mkdir()
    for name in ['source.json','build.json','build-command.json']:
        shutil.copyfile(out/name,dest/name)
    r['status']='compiled'
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:
    r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
    print(json.dumps(dict(status=r['status'],header_exact=r.get('generated_header_exact'))),flush=True)
