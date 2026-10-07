"""Actual enable/disable/render source with registration exhaustion and alien operands."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;root=Path('/home/paul/xbox-windows-native/build/video-ram-ownership-lifecycle001')
assert not root.exists() and not (k/'lifecycle-tests.json').exists();root.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={}
for p in [k/'display/ownership.c',k/'display/surface.c',k/'display/shadow.c',k/'lifecycle-tests.c',k/'tests-body.c',*sorted((k/'tests').iterdir())]:
 shutil.copyfile(p,root/p.name);pins[str(p.relative_to(k))]=sha(p)
args=['gcc','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-fsanitize=address,undefined','-g','-pthread',str(root/'lifecycle-tests.c'),'-o',str(root/'lifecycle-test')]
subprocess.run(args,check=True)
s=subprocess.check_output([str(root/'lifecycle-test')],env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1'),text=True)
lines=s.splitlines();r=json.loads(lines[-1]);assert r['passed'] and r['additional_cases']==7
shutil.copyfile(root/'lifecycle-test',k/'artifacts/lifecycle-test')
r.update(base_tests=json.loads(lines[0]),pins=pins,command=args,compiler=subprocess.check_output(['gcc','--version'],text=True),binary_sha256=sha(root/'lifecycle-test'),verifier_sha256=sha(Path(__file__)))
(k/'lifecycle-tests.json').write_text(json.dumps(r,indent=2)+'\n');print(s)
