"""Reject corrupted recorded mappings and pairings; synthetic mutations only."""
import copy,hashlib,importlib.util,json
from pathlib import Path
k=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('verify_trace',k/'verify-trace.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=m.read(k/'candidate001/trace.json');s=m.read(k/'sites.json');assert len(m.validate(r,s))==3
def mutate(which,data):
 if which==0:data['armed_breakpoints_remaining']=[1]
 elif which==1:data['samples'][0]['copy_arguments'][0]+=4
 elif which==2:data['samples'][0]['source']['rows'][0]['points'][0]['physical']+=4096
 elif which==3:data['samples'][0]['source']['rows'][0]['points'][0]['pcd']=not data['samples'][0]['source']['rows'][0]['points'][0]['pcd']
 elif which==4:data['samples'][0]['rep_after']['ECX']=1
 elif which==5:data['samples'][0]['destination_after']='00'*768
 elif which==6:data['events'][6]['registers']['ESP']+=4
 elif which==7:data['samples'][0]['source']['rows'].pop()
for i in range(8):
 altered=copy.deepcopy(r);mutate(i,altered)
 try:m.validate(altered,s)
 except AssertionError:pass
 else:raise AssertionError('Mutation accepted: '+str(i))
result=dict(passed=True,synthetic_only=True,failure_gates=8,pins={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['verify-trace.py','test-verifier.py']})
(k/'verifier-tests.json').write_text(json.dumps(result,indent=2)+'\n');print('Eight trace corruption/teardown failures rejected')
