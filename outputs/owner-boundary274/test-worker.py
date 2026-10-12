"""Run exact compiled transaction source with counted lock/GL/CPU models."""
import hashlib,json,re,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;out=Path('E:/Codex-archive/xbox-windows-native/boundary274-host002');out.mkdir(exist_ok=False)
dest=k/'host-tests002.json';assert not dest.exists()
art=Path('E:/Codex-archive/xbox-windows-native/boundary274-build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=json.loads((k/'renderer-source-pins001.json').read_text());name='hw/xbox/nv2a/pgraph/gl/renderer.c';assert sha(art/'source'/name)==pins[name]
source=(art/'source'/name).read_text()
def extract(name):
    m=re.search(r'(?m)^(?:static )?(?:bool|void|unsigned) '+name+r'\([^)]*\)\s*\{',source);assert m,name
    n=m.end();depth=1
    while depth:depth+=(source[n]=='{')-(source[n]=='}');n+=1
    return source[m.start():n]
functions=(k/'boundary.h').read_text()+'\n'+'\n'.join(extract(n) for n in ['x274_pending','x274_check','x274_context_match','pgraph_gl_ledger265_worker'])
for n in ['worker-test.c','test-worker.py']:(out/n).write_bytes((k/n).read_bytes())
(out/'test.c').write_text((k/'worker-test.c').read_text().replace('/* INSERT_ACTUAL_FUNCTIONS */',functions))
base='/mnt/e/Codex-archive/xbox-windows-native/boundary274-host002'
c=subprocess.run(['wsl','-d','Ubuntu','-u','root','--','gcc','-std=c11','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer',base+'/test.c','-o',base+'/test'],capture_output=True,timeout=60)
r=dict(passed=False,compile_exit=c.returncode,compile_output=(c.stdout+c.stderr).decode(errors='replace'),guest_executed=False,scope='Actual end-worker body with modeled locks, CPU acknowledgments, graph and GL functions')
if not c.returncode:
    t=subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/test'],capture_output=True,timeout=60)
    r.update(test_exit=t.returncode,test_output=(t.stdout+t.stderr).decode(errors='replace'),passed=t.returncode==0)
r['actual_functions_sha256']=hashlib.sha256(functions.encode()).hexdigest()
r['files']={p.name:sha(p) for p in out.iterdir() if p.is_file()}
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({x:y for x,y in r.items() if x!='files'},indent=2));assert r['passed']
