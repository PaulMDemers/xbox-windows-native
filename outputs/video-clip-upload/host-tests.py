"""Compile exact uploader with line and enumeration shims; check every pixel."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;root=Path('/home/paul/xbox-windows-native/build/video-clip-upload-host001')
assert not root.exists() and not (k/'host-tests.json').exists();root.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={}
for p in [k/'display/shadow.c',k/'tests/framebuf.h',k/'line-tests.c',k/'clip-tests.c']:
 shutil.copyfile(p,root/p.name);pins[str(p.relative_to(k))]=sha(p)
results=[]
for name,count in [('line-tests',241),('clip-tests',144)]:
 args=['gcc','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-ffunction-sections','-fdata-sections','-Wl,--gc-sections','-fsanitize=address,undefined','-g',str(root/(name+'.c')),'-o',str(root/name)]
 subprocess.run(args,check=True)
 output=subprocess.check_output([str(root/name)],env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1'),text=True)
 result=json.loads(output);assert result['passed'] and result['cases']==count
 shutil.copyfile(root/name,k/'artifacts'/name);results.append(dict(name=name,command=args,sha256=sha(root/name),**result))
r=dict(passed=True,cases=sum(v['cases'] for v in results),results=results,pins=pins,compiler=subprocess.check_output(['gcc','--version'],text=True),script_sha256=sha(Path(__file__)))
(k/'host-tests.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,indent=2))
