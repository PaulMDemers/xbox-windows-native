"""Fresh cold-start769, namespace-only guest delta from closed768 source."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'crtc-stride-low768'
def ns(s):return re.sub(r'(?<![0-9])768(?![0-9])','769',re.sub(r'0x768(?=[0-9a-f]*\b)','0x769',s))
names=['main.c','layout.c','layout.h','probe.c','probe.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','clock_model.py','delta001.json']
assert not (K/'main.c').exists()
for n in names:(K/n).write_text(ns((O/n).read_text()),newline='\n')
mapping={'physical.py':'physical003.py','audit_collection.py':'audit_collection003.py','review_prepare.py':'review_prepare005.py'}
for dest,source in mapping.items():
 s=ns((O/source).read_text())
 for a,b in [('review005.json','review001.json'),('sources005.json','sources001.json'),('model002.json','model001.json'),('schema005.json','schema001.json'),('schema-validation005.json','schema-validation001.json'),('source-review005.json','source-review001.json')]:s=s.replace(repr(a),repr(b))
 if dest=='review_prepare.py':
  a=s.index("checks+=['schema001.json'");b=s.index('\n',a)
  s=s[:a]+"checks+=['schema001.json','lineage001.json','delta001.json']"+s[b:]
  # Independently prove the unchanged guest and guard against the refused768.
  pos=s.index(" for f in K.glob('*.py')")
  s=s[:pos]+" for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:\n  original=(K.parent/'crtc-stride-low768'/n).read_text()\n  converted=re.sub(r'(?<![0-9])768(?![0-9])','769',re.sub(r'0x768(?=[0-9a-f]*\\b)','0x769',original))\n  assert (K/n).read_text()==converted,n\n"+s[pos:]
 (K/dest).write_text(s,newline='\n')
p=K/'model.py';s=p.read_text().replace('json.dumps(R,indent=2)',"json.dumps(R,separators=(',',':'))");p.write_text(s,newline='\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'guest_delta':'namespace only from768; original CR22FE baseline and all recovery guards unchanged','condition_changed':'user Ready after requested full10second cold power cycle','parent768':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names+list(mapping.values())},'prior_refusal_sha256':hashlib.sha256((O/'closed001.json').read_bytes()).hexdigest(),'prior_cr22_comparison_sha256':hashlib.sha256((O/'comparison001.json').read_bytes()).hexdigest(),'model_serialization':'compact JSON from initial execution; no data omitted'},indent=2)+'\n')
