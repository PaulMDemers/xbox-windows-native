"""Correct descriptive mask names from expanded header; numeric layout unchanged."""
from pathlib import Path
import json,re,hashlib,datetime
K=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((K/'optical-schema001.json').read_text());fields=[]
for d in re.findall(r'uint32_t\s+([^;]+);',(K/'probe.h').read_text()):
 for p in d.split(','):
  m=re.fullmatch(r'\s*(\w+)(?:\[(\d+)\])?\s*',p);assert m
  fields.extend([m[1]] if m[2] is None else [m[1]+'['+str(i)+']' for i in range(int(m[2]))])
assert len(fields)==820
s['names']=['signature','final_code']+[fields[i] for i in s['word_indices'][2:]]
s['supersedes_labels_only']='optical-schema001.json';s['prior_sha256']=sha(K/'optical-schema001.json')
s['numeric_layout_unchanged']=True;s['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (K/'optical-schema002.json').open('x') as f:json.dump(s,f,indent=2);f.write('\n')
print('PASS expanded820-field optical names; numeric mapping unchanged')
