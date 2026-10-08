"""Compile exact shadow source with a line engine shim and sanitizer bounds tests."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;root=Path('/home/paul/xbox-windows-native/build/video-line-upload-host001')
assert not root.exists() and not (k/'host-tests.json').exists();root.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={}
for p in [k/'display/shadow.c',k/'tests/framebuf.h',k/'line-tests.c']:
 shutil.copyfile(p,root/p.name);pins[str(p.relative_to(k))]=sha(p)
args=['gcc','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-ffunction-sections','-fdata-sections','-Wl,--gc-sections','-fsanitize=address,undefined','-g',str(root/'line-tests.c'),'-o',str(root/'line-tests')]
subprocess.run(args,check=True)
text=subprocess.check_output([str(root/'line-tests')],env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1'),text=True)
r=json.loads(text);assert r['passed'] and r['cases']==241
shutil.copyfile(root/'line-tests',k/'artifacts/line-tests')
r.update(pins=pins,compiler=subprocess.check_output(['gcc','--version'],text=True),command=args,binary_sha256=sha(root/'line-tests'),script_sha256=sha(Path(__file__)))
(k/'host-tests.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(text)
