"""Independent native917-word success schema and full820-word prefix failure regression."""
from pathlib import Path
import json,hashlib,datetime
from prefix_audit import validate as prefix_validate
from audit_logic import validate
K=Path(__file__).resolve().parent;out=K/'schema-review001.json';assert not out.exists()
r={'passed':False,'physical_access':False,'counts':{}}
try:
 for name in ['prefix002.json','tail003.json','integration001.json']:
  m=json.loads((K/name).read_text());assert m['passed'];count=0;success=0
  for c in m['cases']:
   if 'raw_result' not in c:continue
   if name=='integration001.json' and (c.get('refusal') or c['name'].startswith('null-') or c['name'] in ['IF-refusal','wrapper-baseline']):continue
   v=c['raw_result']
   if name=='prefix002.json':prefix_validate(v[:820]);count+=1
   if len(v)==917 and v[:2]==[0x817,0x817]:validate(v);success+=1;base=v
  r['counts'][name]={'prefix_results':count,'complete_success_results':success}
 rejected=[]
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,917)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:rejected.append(i)
  else:raise AssertionError(('accepted corruption',i))
 assert len(rejected)==823
 r.update(passed=True,rejected_mutations=rejected,limits=['Tail negative outcomes independently checked by tail003 trace/array validator; complete-success schema deliberately rejects them','Models are not physical execution evidence'])
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();r['sources']={n:hashlib.sha256((K/n).read_bytes()).hexdigest() for n in ['prefix_schema.py','prefix_audit.py','audit_logic.py','schema_review001.py']};out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS independent917 schema and823 corruptions',r['counts'])
