"""Native ASan/UBSan bounds/pixel-set/saturation tests, no NT5 font claim."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'host-tests.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
exe=Path('/tmp/text203-host');assert not exe.exists()
cmd=['cc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-parentheses','-fsanitize=address,undefined',str(k/'host-tests.c'),'-o',str(exe)]
r=dict(passed=False,host_only=True,commands=[cmd],pins={n:sha(k/n) for n in ['text_bounds.h','host-tests.c']})
try:
    subprocess.run(cmd,check=True);p=subprocess.run([str(exe)],check=True,capture_output=True,text=True)
    assert p.stdout=='CHECKS 20013\n' and not p.stderr
    r.update(passed=True,checks=20013,stdout=p.stdout,stderr=p.stderr,limits='Synthetic rectangle/pixel-set oracle, signed extrema, unsupported pointer paths and64bit saturating accounting. No runtime glyph/driver qualification.')
finally:
    r['compiler']=subprocess.check_output(['cc','--version'],text=True).splitlines()[0]
    dest.write_text(json.dumps(r,indent=2)+'\n');exe.unlink(missing_ok=True)
print(r['passed'],r.get('checks'))
