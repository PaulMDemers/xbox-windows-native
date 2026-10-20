"""Verify the output branch is the sole observer-helper behavior change."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;S=K.parent/'rct605';out=K/'source-review001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
b=read('build002.json');assert b['status']=='compiled'
for n,v in b['files'].items():
 p=Path(n.replace('/mnt/c/','C:/'));assert sha(p)==v['sha256']
 if p.suffix in ['.c','.h'] and p.name!='target_iat.h':assert p.read_bytes()==(K/p.name).read_bytes()
for n in ['calls.h','dib_header.h','phase.h','host_calls.c','host_dib.c','host_phase.c']:
 assert (K/n).read_bytes()==(S/n).read_bytes(),n
a=(S/'trace.c').read_text();t=(K/'trace.c').read_text()
for x,y in [('xwn607','xwn605'),('XWN607','XWN605'),('subject607','subject605')]:t=t.replace(x,y)
addition='if(f->api==4&&!address){event("OUTPUT_ABSENT",f->id,f->api,0);return !failed;}\n        '
assert t.count(addition)==1 and t.replace(addition,'')==a
assert 'if(!address||!readmem(address,&pointer,4))return FALSE;' in t
assert "if api==4 and value and args[ident][3]:assert outputs[ident]" in (K/'trace_oracle.py').read_text()
out.write_text(json.dumps(dict(passed=True,exact_parent_sha256=sha(S/'trace.c'),candidate_sha256=sha(K/'trace.c'),scope='Only absent-output branch plus attempt namespace in observer. Exact qualified headers/core retained; runtime original control still required.'),indent=2)+'\n')
print('607 frozen source and narrow diagnostic change passed')
