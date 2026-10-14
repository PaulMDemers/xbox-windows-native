"""Read-only setup-order and matched-control analysis; no gate waiver/adoption."""
from pathlib import Path
import json,sys,hashlib
K=Path(__file__).resolve().parent;O=K/'candidate001';A=K/'artifacts/candidate001/E/xwndemo398candidate001'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
c=read(O/'collection.json');a=read(O/'audit.json');assert c['completed']
sys.path.insert(0,str(K.parent/'video-text-oracle206'))
from runner_analysis import helper
trace=(A/'file-trace.log').read_text().splitlines() if (A/'file-trace.log').exists() else []
r=dict(scope='Physical398 candidate390 paired with original397 setup-first control',physical_release_qualified=False)
try:r['gate_helper']=helper((A/'gate/wizard201.log').read_bytes(),0)
except (OSError,AssertionError,ValueError) as e:r['gate_failure']=repr(e)
r['setup_before_files_passed']=trace[:4]==['BEGIN','GATE_START','GATE_EXIT 0','FILE_API_START'] and r.get('gate_helper',{}).get('passed',False)
r['all_children_returned']=all(trace.count(v)==1 for v in ['FILE_API_EXIT 0','CMD_EXIT 0','RUNNER_RETURN 0'])
r['candidate_file_scope_passed']=r['setup_before_files_passed'] and r['all_children_returned'] and a['file_persistence_passed'] and a['cmd_persistence_passed']
r['scoped_combined_passed']=r['candidate_file_scope_passed'] and a['scoped_combined_passed']
r['strict_qualification_passed']=r['scoped_combined_passed'] and a['strict_qualification_passed']
r['normal_shutdown_count']=a['normal_shutdown_count'];r['warnings_errors']=a['warnings_errors']
prior=K.parent/'setup-retry397/control001/control-analysis.json';r['control397_sha256']=sha(prior);r['control397']=read(prior)
r['limits']='Distinct physical runs, matched helpers/order and protected baseline; no attribution of394 failure, no full disk-content/1080i/performance/audibility qualification. Ft49 retained. No adoption or bundle.'
p=O/'candidate-analysis.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:v for k,v in r.items() if k!='control397'},indent=2))
