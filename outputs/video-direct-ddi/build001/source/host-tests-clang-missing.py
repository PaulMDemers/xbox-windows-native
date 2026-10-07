"""Compile the exact authored surface.c against a host-only API fault shim."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent
root=Path('/home/paul/xbox-windows-native/build/video-direct-ddi-host001')
assert not root.exists() and not (k/'host-tests.json').exists();root.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins={}
for path in [k/'display/surface.c',k/'tests/framebuf.h',k/'tests/surface-test.c']:
 shutil.copyfile(path,root/path.name);pins[str(path.relative_to(k))]=sha(path)
args=['clang','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-g',str(root/'surface.c'),str(root/'surface-test.c'),'-o',str(root/'surface-test')]
subprocess.run(args,check=True)
text=subprocess.check_output([str(root/'surface-test')],env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1'),text=True)
r=json.loads(text);assert r['passed'] and r['cases']==17
shutil.copyfile(root/'surface-test',k/'artifacts/surface-test')
r.update(pins=pins,compiler=subprocess.check_output(['clang','--version'],text=True),command=args,
 binary_sha256=sha(root/'surface-test'),source_sha256=sha(Path(__file__)),sanitizers='ASan/UBSan and leak detection; exit0')
(k/'host-tests.json').write_text(json.dumps(r,indent=2)+'\n');print(text)
