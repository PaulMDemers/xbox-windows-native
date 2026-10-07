"""Test the actual constructor's 64-bit offsets and signed-overflow rejection."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((k/'map-tests.json').read_text())
for n,d in old['source_sha256'].items():assert sha(k/n)==d
exe=k/'artifacts/test-large-map';cmd=['/usr/bin/gcc','-std=gnu11','-Wall','-Wextra','-Werror','-Wno-multichar','-fsanitize=address,undefined','-fno-omit-frame-pointer','-g',str(k/'test-large-map.c'),'-o',str(exe)]
subprocess.run(cmd,check=True);out=subprocess.check_output([str(exe)],text=True)
r=dict(scope=__doc__,source_sha256={n:sha(k/n) for n in ['test-large-map.c','test-map.c','dump-map.inc','artifacts/paging-builder.inc']},command=cmd,output=out,passed=True,physical_access=False,limits='Additional host test, not NT ABI or disk/controller dump-write coverage.')
p=k/'large-map-tests.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n');print(out)
