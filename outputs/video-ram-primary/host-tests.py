"""Compile exact driver source using a host API shim, retaining all inputs."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;root=Path('/home/paul/xbox-windows-native/build/video-ram-primary-host002')
assert not root.exists() and not (k/'host-tests.json').exists();root.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={}
for path in [k/'display/surface.c',k/'display/shadow.c',k/'tests-body.c',*sorted((k/'tests').iterdir())]:
 shutil.copyfile(path,root/path.name);pins[str(path.relative_to(k))]=sha(path)
args=['gcc','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-fsanitize=address,undefined','-g',str(root/'tests-body.c'),'-o',str(root/'surface-test')]
subprocess.run(args,check=True)
text=subprocess.check_output([str(root/'surface-test')],env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1'),text=True)
r=json.loads(text);assert r['passed'] and r['cases']==46 and r['rop_truth_tables']==65536
(k/'artifacts').mkdir(exist_ok=True);shutil.copyfile(root/'surface-test',k/'artifacts/surface-test')
r.update(pins=pins,compiler=subprocess.check_output(['gcc','--version'],text=True),command=args,binary_sha256=sha(root/'surface-test'),source_sha256=sha(Path(__file__)),sanitizers='ASan/UBSan with leak detection; exit0')
(k/'host-tests.json').write_text(json.dumps(r,indent=2)+'\n');print(text)
