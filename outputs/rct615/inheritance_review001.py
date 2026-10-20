"""Read-only source provenance, preserving the closed controls' actual evidence."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'inheritance-review001.json';assert not out.exists()
src=json.loads((K/'source001.json').read_text());rows=[]
for n in ['load_dialog002.h','park_reference.h','assets.h','verify.c','welcome.h',
          'title_signature.h','scene_compare.py','serial_host.py']:
 old=614 if n=='serial_host.py' else 612;p=K.parent/f'rct{old}'/n
 s=p.read_text()
 for prefix in ['xwn','XWN','rct','run','RUN','verify','VERIFY','trace','TRACE']:
  s=s.replace(prefix+str(old),prefix+'615')
 assert (K/n).read_text()==s,n
 assert sha(p)==src['sources'][n]['sha256']
 rows.append(dict(name=n,source=str(p),sha256=sha(p),candidate_sha256=sha(K/n)))
assert sha(K.parent/'rct614/sampler.c')==src['counter_source_sha256']
out.write_text(json.dumps(dict(passed=True,rows=rows,counter_primitives_checked_by='host-tests001.json',
 scope='Namespace-normalized unchanged load/capture reference, verifier and bounded host reader sources. No runtime reopened.'),indent=2)+'\n')
