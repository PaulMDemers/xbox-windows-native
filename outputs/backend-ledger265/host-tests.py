"""Small bounded host tests; no source borrowing and no guest process."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent
out=Path('E:/Codex-archive/xbox-windows-native/ledger265-host001')
assert not out.exists();out.mkdir()
base='/mnt/e/Codex-archive/xbox-windows-native/ledger265-host001'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['ledger-core.h','test-core.c']:(out/name).write_bytes((k/name).read_bytes())
command=['wsl','-d','Ubuntu','-u','root','--','gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',base+'/test-core.c','-o',base+'/test']
r=dict(guest_executed=False,physical_access=False,inputs={n:sha(k/n) for n in ['host-tests.py','ledger-core.h','test-core.c']},command=command)
c=subprocess.run(command,capture_output=True,timeout=60)
r.update(compile_exit=c.returncode,compile_output=(c.stdout+c.stderr).decode(errors='replace'))
if not c.returncode:
    t=subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/test'],capture_output=True,timeout=60)
    r.update(test_exit=t.returncode,test_output=(t.stdout+t.stderr).decode(errors='replace'))
r['passed']=r.get('test_exit')==0
r['files']={p.name:sha(p) for p in out.iterdir() if p.is_file()}
with (k/'host-tests001.json').open('x',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')
print(json.dumps(r,indent=2));assert r['passed']
