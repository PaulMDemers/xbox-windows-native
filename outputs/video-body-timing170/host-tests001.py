"""Actual counter arithmetic under ASan/UBSan; does not qualify NT clock/DDI."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'host-tests.json';assert not dest.exists()
exe=Path('/tmp/xwn-profile170-math');subprocess.run(['clang','-std=c99','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-g',str(k/'math-tests.c'),'-o',str(exe)],check=True)
result=subprocess.run([str(exe)],check=True,capture_output=True,text=True)
count=int(result.stdout.split()[0]);assert count==4142,count
dest.write_text(json.dumps(dict(passed=True,checks=count,stdout=result.stdout,asan_ubsan=True,clock_runtime_qualified=False,
 pins={str(p.relative_to(k)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [k/'display/profile_math.h',k/'math-tests.c',k/'host-tests.py']}),indent=2)+'\n');print(result.stdout)
