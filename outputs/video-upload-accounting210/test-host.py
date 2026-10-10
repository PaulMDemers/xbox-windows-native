"""ASan/UBSan host-only bounded accounting tests, unique artifact directory."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'artifacts/host001';assert not out.exists();out.mkdir(parents=True)
assert sys.platform=='linux'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False,guest_launch=False,source_pins={p.name:sha(p) for p in [k/'host-test.c',k/'upload_account.h',Path(__file__)]},runs=[])
try:
 for mode in [0,1]:
  exe=out/('test%d'%mode)
  cmd=['gcc','-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-fsanitize=address,undefined','-fno-omit-frame-pointer','-DXWN_UPLOAD_ACCOUNTING='+str(mode),str(k/'host-test.c'),'-o',str(exe)]
  subprocess.run(cmd,check=True);p=subprocess.run([str(exe)],check=True,text=True,capture_output=True)
  (out/('mode%d.txt'%mode)).write_text(p.stdout+p.stderr)
  r['runs'].append(dict(mode=mode,command=cmd,binary_sha256=sha(exe),output=p.stdout,stderr=p.stderr,exit_code=p.returncode))
 r['passed']=True
finally:(k/'host-tests001.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
