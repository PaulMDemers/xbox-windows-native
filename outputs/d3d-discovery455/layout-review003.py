"""Review existing compile-only layout001; never rerun its compiler."""
import hashlib,json,struct
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('/home/paul/xbox-windows-native/discovery455-layout001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'layout-review003.json';assert not out.exists() and not (K/'layout001.json').exists()
b=json.loads((K/'sample-build001.json').read_text());assert sha(Path(b['compiler']))==b['compiler_sha256']
assert (P/'compile.log').read_bytes()==b'' and struct.unpack_from('<H',(P/'layout001.o').read_bytes())[0]==0x14c
assert (P/'layout001.c').read_bytes()==(K/'layout001.c').read_bytes()
deps=(P/'headers.d').read_text().replace('\\\n','').split(': ',1)[1].split();headers={n:sha(Path(n)) for n in sorted(set(deps)) if Path(n)!=P/'layout001.c'}
extra={}
for p,h in headers.items():
 if p in b['headers']:assert b['headers'][p]==h,p
 else:extra[p]=h
assert len(extra)==2 and all(p.endswith('/include/stddef.h') for p in extra)
r=dict(passed=True,compile_repeated=False,assertions=12,original_failure='layout001 post-compile metadata KeyError on additional stddef.h; actual compile reached exit_code==0 branch',source_sha256=sha(P/'layout001.c'),object_sha256=sha(P/'layout001.o'),log_sha256=sha(P/'compile.log'),headers=headers,additional_headers=extra,host_executed=False)
out.write_text(json.dumps(r,indent=2)+'\n');print('Existing compiled12 layout assertions reviewed; SDK and GCC stddef headers pinned.')
