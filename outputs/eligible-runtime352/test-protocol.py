"""Use actual closed349 rows only as transport models, never requalify old runs."""
import hashlib,json
from pathlib import Path
from phase352_analysis import analyze
K=Path(__file__).resolve().parent;dest=K/'protocol001.json';assert not dest.exists();checks=0
def req(v):
 global checks
 checks+=1;assert v
old=K.parent/'primary-runtime349/candidate001/artifacts/sample0/gdi-baseline.txt'
rows=old.read_text().splitlines();out=[];fast={}
for row in rows:
 v=row.split()
 if v and v[0] in ['PRIMARY348_BEFORE','PRIMARY348_AFTER'] and int(v[2]) in [9,10]:fast[(v[0],v[1],v[2])]=v[3]
for row in rows:
 v=row.split()
 if v and v[0] in ['PRIMARY348_BEFORE','PRIMARY348_AFTER']:
  if v[2]=='1':v[3]='351'
  if v[2] in ['12','13']:v[3]=fast[(v[0],v[1],str(int(v[2])-3))]
  row=' '.join(v)
 out.append(row.replace('PRIMARY348_','PRIMARY351_'))
text='\n'.join(out);req(analyze(text,1)['passed'])
for i,row in enumerate(out):
 if row.startswith('PRIMARY351_'):
  bad=out.copy();bad[i]=row+' 0';req(not analyze('\n'.join(bad),1)['passed'])
for prefix in ['PHASE344_AFTER 2 31 ','LARGE_TIMING 2 ','LARGE_RESULT 2 ']:
 found=[i for i,v in enumerate(out) if v.startswith(prefix)]
 if found:
  bad=out.copy();del bad[found[0]];req(not analyze('\n'.join(bad),1)['passed'])
# Exact adjacency cannot be silently projected away.
i=next(i for i,v in enumerate(out) if v=='PRIMARY351_PACKET 2 0 1')
bad=out.copy();bad.insert(i,'INJECTED_UNKNOWN 0 0 0');req(not analyze('\n'.join(bad),1)['passed'])
dest.write_text(json.dumps(dict(passed=True,checks=checks,model_source_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),scope='Actual349 rows projected into a synthetic351 transport model only; eligible bytes injected from fast totals, NOT actual351 evidence or historical requalification',parser_sha256=hashlib.sha256((K/'phase352_analysis.py').read_bytes()).hexdigest()),indent=2)+'\n');print(checks,'protocol controls')
