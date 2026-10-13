import hashlib,json,subprocess,sys
from pathlib import Path
from integrate import transform
K=Path(__file__).resolve().parent
case=sys.argv[1];assert case=='host001'
out=Path('/mnt/e/xwn369')/case;dest=K/(case+'.json')
assert sys.platform=='linux' and not out.exists() and not dest.exists()
out.mkdir(parents=True)
parent=Path('/home/paul/xbox-windows-native/build/hd-profile345-build001/source/win32ss/drivers/displays/framebuf')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=json.loads((K.parent/'hd-profile345/build001.json').read_text())['source_files']
for n in ['shadow.c','row_store.h']:assert sha(parent/n)==pins['win32ss/drivers/displays/framebuf/'+n]
for n in ['host.py','host.c','stretch_bounds.h','integrate.py']:(out/n).write_bytes((K/n).read_bytes())
(out/'row_store.h').write_bytes((parent/'row_store.h').read_bytes())
s=transform((parent/'shadow.c').read_text())
actual=s[s.index('static BOOL XwnRopUsesSource'):s.index('ULONG XwnCheckScanout')]
actual+=s[s.index('BOOL APIENTRY XwnStretchBlt('):s.index('BOOL APIENTRY XwnPlgBlt(')]
(out/'actual.inc').write_text(actual)
r=dict(status='started',source_sha256=sha(parent/'shadow.c'),inputs={p.name:sha(p) for p in out.iterdir()},models=['Eng rasterizer','CLIPOBJ provider','PDEV ownership','profile clocks','RAM scanout'])
try:
    r['compiler']=subprocess.check_output(['gcc','--version'],text=True).splitlines()[0]
    cmd=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(out/'host.c'),'-o',str(out/'host')]
    p=subprocess.run(cmd,capture_output=True,text=True);(out/'compile.log').write_text(p.stdout+p.stderr);p.check_returncode()
    p=subprocess.run([str(out/'host')],capture_output=True,text=True,timeout=120);(out/'run.log').write_text(p.stdout+p.stderr);p.check_returncode()
    r.update(status='passed',command=cmd,result=json.loads(p.stdout))
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:
    r['files']={p.name:sha(p) for p in out.iterdir()};dest.write_text(json.dumps(r,indent=2)+'\n');print(r['status'])
