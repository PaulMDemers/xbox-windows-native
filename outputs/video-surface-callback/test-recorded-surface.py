"""Reject corrupted recorded windows/state; read-only after diagnostic capture."""
import copy,hashlib,importlib.util,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'candidate001'
sp=importlib.util.spec_from_file_location('verify_surface',k/'verify-surface.py');v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v)
r=v.read(out/'trace.json');loader=lambda w:(out/'artifacts/surface-windows'/w['artifact']).read_bytes()
assert len(v.validate(r,loader))==3
for check in r['surface']['state_checks']:
 assert len(check['replies'])==2
 for n,row in enumerate(check['replies']):
  name=r['surface']['events'][n];assert row['event']==name
  assert re.search(re.escape(name)+r' : state '+str(int(check['enabled']))+r'\b',row['state'])
def mutate(i,x):
 s=x['surface']
 if i==0:s['events_disabled']=False
 elif i==1:s['windows'].pop()
 elif i==2:s['windows'][10]['sample']=0
 elif i==3:s['windows'][12]['sha256']='0'*64
 elif i==4:s['total_records']+=1
 elif i==5:s['windows'][0]['after_stop']='marker'
 elif i==6:s['state_checks'][4]['enabled']=True
 elif i==7:x['armed_breakpoints_remaining']=[1]
 elif i==8:s['windows'][0]['duration_seconds']=31
for i in range(9):
 x=copy.deepcopy(r);mutate(i,x)
 try:v.validate(x,loader)
 except AssertionError:pass
 else:raise AssertionError('Mutation accepted: '+str(i))
dest=k/'recorded-surface-tests.json';assert not dest.exists()
dest.write_text(json.dumps(dict(passed=True,synthetic_mutations=9,raw_hmp_states_checked=True,pins={str(p):v.sha(p) for p in [Path(__file__),k/'verify-surface.py',out/'trace.json']}),indent=2)+'\n')
print('Nine recorded-window/teardown mutations rejected; raw HMP states verified')
