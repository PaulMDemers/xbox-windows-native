import hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;out=Path('/mnt/e/xwn357/host001');dest=K/'host001.json'
assert sys.platform=='linux' and not out.exists() and not dest.exists();out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['host.c','wrapper_host.c','host.py','capture.h','memory_warm.c']:(out/n).write_bytes((K/n).read_bytes())
assert (K/'capture.h').read_bytes()==(K.parent/'memory-state354/capture.h').read_bytes()
s=(K/'memory_warm.c').read_text();body=s[s.index('ULONG XwnMemoryState357'):];(out/'actual_wrapper.inc').write_text(body)
r=dict(status='started',inputs={p.name:sha(p) for p in out.iterdir()},scope='Actual collector core and extracted actual dual wrapper; privileged reads/GDI pixels/lifetime/SEH modeled')
try:
 r['compiler']=subprocess.check_output(['gcc','--version'],text=True).splitlines()[0]
 cmd=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(out/'wrapper_host.c'),'-o',str(out/'host')]
 p=subprocess.run(cmd,capture_output=True,text=True);(out/'compile.log').write_text(p.stdout+p.stderr);p.check_returncode()
 p=subprocess.run([str(out/'host'),str(out/'synthetic-dual.bin')],capture_output=True,text=True,timeout=120);(out/'run.log').write_text(p.stdout+p.stderr);p.check_returncode()
 r.update(status='passed',command=cmd,results=[json.loads(v) for v in p.stdout.splitlines()])
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:r['files']={p.name:sha(p) for p in out.iterdir()};dest.write_text(json.dumps(r,indent=2)+'\n');print(r['status'])
