import hashlib,json,subprocess,sys,traceback
from pathlib import Path
k=Path(__file__).resolve().parent;attempt=sys.argv[1];assert attempt.isdecimal()
dest=k/('host'+attempt+'.json');assert not dest.exists()
out=Path('E:/Codex-archive/xbox-windows-native/boundary287-host'+attempt);out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['boundary.h','test.c','test-host.py']:(out/n).write_bytes((k/n).read_bytes())
original=(k.parent/'release-worker280/boundary.h').read_text()
marker='    for(unsigned i=0;i<4;i++) {\n        const X277Texture *t=&p->textures[i];'
assert original.count(marker)==1
prefix=original[:original.index(marker)]
common=prefix.replace('x280_validate(const X277Proof *p,unsigned candidate)','x287_common(const X277Proof *p)').replace('(candidate>1 || p->stage<1 || p->stage>3)','(p->stage<1 || p->stage>4)')+'    return X277_OK;\n}\n'
assert 'candidate' not in common
(out/'common.h').write_bytes(common.encode())
(out/'admission.h').write_bytes((k.parent/'release-worker280/admission.h').read_bytes())
fixture=Path('E:/Codex-archive/xbox-windows-native/cache283-host003/fixture.h')
assert sha(fixture)==json.loads((k.parent/'cache-disposal283/host003.json').read_text())['files']['fixture.h']
(out/'fixture.h').write_bytes(fixture.read_bytes())
r=dict(passed=False,host_only=True,actual_provider=False,actual_worker=False,renderer_built=False,guest_launched=False,
 original_common_source_sha256=sha(k.parent/'release-worker280/boundary.h'),models='All CPU/GL/graph/refcount/namespace booleans are explicit host facts; the validator does not collect them or authorize runtime disposal')
try:
 base='/mnt/e/Codex-archive/xbox-windows-native/boundary287-host'+attempt
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--','gcc','-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+base,base+'/test.c','-o',base+'/test'],capture_output=True,timeout=60)
 r.update(compile_exit=p.returncode,compile_output=(p.stdout+p.stderr).decode());assert p.returncode==0
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/test'],capture_output=True,timeout=60)
 r.update(test_exit=p.returncode,test_output=(p.stdout+p.stderr).decode());assert p.returncode==0;r['passed']=True
except BaseException as e:r.update(error=repr(e),traceback=traceback.format_exc())
r['files']={p.name:sha(p) for p in out.iterdir() if p.is_file()}
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:v for a,v in r.items() if a!='files'},indent=2));assert r['passed']
