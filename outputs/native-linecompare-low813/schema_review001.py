"""Validate all complete compiled results independently, plus corruptions."""
from pathlib import Path
import json,hashlib,datetime
from audit_logic import validate
K=Path(__file__).resolve().parent; out=K/'schema-review001.json';assert not out.exists()
r={'passed':False,'physical_access':False,'counts':{}}
try:
 for name in ['tail001.json','prefix001.json','integration001.json']:
  m=json.loads((K/name).read_text());assert m['passed'];count=0
  for c in m['cases']:
   if 'raw_result' not in c:continue
   try:validate(c['raw_result'])
   except AssertionError as e:raise AssertionError((name,c['name'],'schema rejected')) from e
   count+=1
  r['counts'][name]=count
 base=json.loads((K/'tail001.json').read_text())['cases'][0]['raw_result'];rejected=[]
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,820)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:rejected.append(i)
  else:raise AssertionError(('accepted corruption',i))
 r.update(passed=True,rejected_mutations=rejected)
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();r['source_sha256']={n:hashlib.sha256((K/n).read_bytes()).hexdigest() for n in ['audit_logic.py','prefix_schema.py','schema_review001.py']};out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS complete native result schema and mutation checks',r['counts'])
