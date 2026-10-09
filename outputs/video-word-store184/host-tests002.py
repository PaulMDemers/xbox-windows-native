"""Actual row-store helper with ASan/UBSan independent memmove byte oracle."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'host-tests002.json';assert not dest.exists();exe=Path('/tmp/xwn-word184-recorded-tests002')
commands=[['gcc','-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(k/'row-tests002.c'),'-o',str(exe)],[str(exe)]]
subprocess.run(commands[0],check=True);r=subprocess.run(commands[1],check=True,capture_output=True,text=True);count=int(r.stdout.split()[1]);assert count==45641
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest.write_text(json.dumps(dict(passed=True,checks=count,byte_oracle_cases=16544,stdout=r.stdout,asan_ubsan=True,commands=commands,compiler_version=subprocess.check_output(['gcc','--version'],text=True),pins={p.name:sha(p) for p in [k/'row_store.h',k/'row-tests002.c',k/'host-tests002.py']},compiled_host_sha256=sha(exe),guest_qualified=False,limits='Host RAM bytes/guards only, not UC throughput/hardware ordering qualification'),indent=2)+'\n');print(r.stdout)
