"""Fresh immutable host capsule; actual candidate adapter, modeled DDI ownership."""
import hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent
assert sys.platform=='linux'
out=Path('/mnt/e/xwn348/host002');dest=K/'host002.json'
assert not out.exists() and not dest.exists();out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['primary_copy.c','primary_plan.h','host002.c','host002.py']:(out/n).write_bytes((K/n).read_bytes())
(out/'framebuf.h').write_bytes((K/'host-framebuf.h').read_bytes())
r={'status':'started','scope':'Actual adapter/planner; modeled SURFOBJ/PDEV membership and host libc memmove, not NT5 or device execution','inputs':{p.name:sha(p) for p in out.iterdir()},'cases':{}}
try:
    r['compiler']=subprocess.check_output(['gcc','--version'],text=True).splitlines()[0]
    for enabled in [0,1]:
        exe=out/f'host-{enabled}';cmd=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',f'-DXWN_PRIMARY_COPY={enabled}',str(out/'host002.c'),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True,text=True);(out/f'compile-{enabled}.log').write_text(p.stdout+p.stderr);p.check_returncode()
        p=subprocess.run([str(exe)],capture_output=True,text=True,timeout=120);(out/f'run-{enabled}.log').write_text(p.stdout+p.stderr);p.check_returncode()
        r['cases'][str(enabled)]={'command':cmd,'sha256':sha(exe),'result':json.loads(p.stdout)}
    r['status']='passed'
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:
    r['files']={p.name:sha(p) for p in out.iterdir() if p.is_file()};dest.write_text(json.dumps(r,indent=2)+'\n');print(r['status'])
