"""Independent context validity/channel/hardware-switch truth table; synthetic."""
import hashlib,importlib.util,itertools,json
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'interpret-tests.json';assert not dest.exists()
p=k/'interpret-state.py';spec=importlib.util.spec_from_file_location('interpret216',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checks=0
for valid,hardware,fifo,graph in itertools.product([False,True],[False,True],range(32),range(32)):
 values={n:0 for n in ['00003204','00400148','00400144','0040008c','00003200','00003250','00400720','00100200','0010020c']}
 values['00003204']=fifo;values['00400148']=graph<<24;values['00400144']=int(valid)<<16;values['0040008c']=int(hardware)<<2
 r=m.context_facts(values);expected=not valid or fifo!=graph
 assert r['model_switch_request_needed']==expected and r['model_hardware_switch_assertion_if_request']==(expected and hardware)
 assert r['pgraph_context_valid']==valid and r['hardware_context_switch']==hardware
 assert r['fifo_channel']==fifo and r['pgraph_channel']==graph and not r['gpu_submission_authorized'];checks+=1
dest.write_text(json.dumps(dict(passed=True,cases=checks,synthetic=True,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),interpreter_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),guest_launch=False,physical_access=False),indent=2)+'\n',encoding='utf-8');print('Context truth-table PASS:',checks)
