"""Run actual shared geometry under ASan/UBSan with independent byte oracle."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'host-tests.json';assert not dest.exists()
exe=Path('/tmp/xwn-dib182-recorded-tests')
commands=[['gcc','-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(k/'plan-tests.c'),'-o',str(exe)],[str(exe)]]
subprocess.run(commands[0],check=True);r=subprocess.run(commands[1],check=True,capture_output=True,text=True)
count=int(r.stdout.split()[1]);assert count==321785
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest.write_text(json.dumps(dict(passed=True,checks=count,byte_oracle_cases=30000,stdout=r.stdout,asan_ubsan=True,commands=commands,compiler_version=subprocess.check_output(['gcc','--version'],text=True),pins={p.name:sha(p) for p in [k/'dib_plan.h',k/'plan-tests.c',k/'host-tests.py']},compiled_host_sha256=sha(exe),guest_qualified=False),indent=2)+'\n')
print(r.stdout)
