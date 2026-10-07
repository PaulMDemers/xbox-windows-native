"""Sanitized concurrent tests of exact registry implementation, with POSIX lock shim."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;root=Path('/home/paul/xbox-windows-native/build/video-ram-ownership-registry001')
assert not root.exists() and not (k/'ownership-tests.json').exists();root.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={}
for p in [k/'display/ownership.c',k/'ownership-tests.c',k/'tests/framebuf.h',k/'tests/semaphore-shim.inc']:
 shutil.copyfile(p,root/p.name);pins[str(p.relative_to(k))]=sha(p)
args=['gcc','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-g','-pthread',str(root/'ownership-tests.c'),'-o',str(root/'ownership-test')]
subprocess.run(args,check=True)
s=subprocess.check_output([str(root/'ownership-test')],env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1'),text=True)
r=json.loads(s);assert r['passed'] and r['register_lookup_remove_cycles']==80000
(k/'artifacts').mkdir(exist_ok=True);shutil.copyfile(root/'ownership-test',k/'artifacts/ownership-test')
r.update(pins=pins,command=args,compiler=subprocess.check_output(['gcc','--version'],text=True),binary_sha256=sha(root/'ownership-test'),verifier_sha256=sha(Path(__file__)))
(k/'ownership-tests.json').write_text(json.dumps(r,indent=2)+'\n');print(s)
