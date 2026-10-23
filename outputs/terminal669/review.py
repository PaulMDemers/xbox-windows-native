"""Review host-only qualification boundaries and exact prototype bytes."""
import datetime,hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;B=Path('C:/xwn669/host001');out=K/'review001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False,new_XBE=False,checks=[])
def check(n,v):assert v,n;r['checks'].append(n)
try:
 b=json.loads((K/'host001.json').read_text());l=json.loads((K/'linked001.json').read_text())
 check('host sanitizer lifecycle cases',b['passed'] and b['tests']['lifecycle_cases']==40 and b['tests']['argument_and_phase_checks']==15)
 check('isolated linked helpers',l['passed'] and len(l['cases'])==6 and l['source_sha256']==sha(K/'linked.py'))
 check('linked executable pin',l['binary_sha256']==b['artifacts']['irq.bin']['sha256']==sha(B/'irq.bin'))
 for n,h in b['source_pins'].items():check('source '+n,sha(K/n)==h==sha(B/'source'/n))
 check('no XBE artifact',not any(p.suffix.lower()=='.xbe' for p in B.rglob('*')))
 check('native transport untouched',sha(Path('C:/xwn667/source001/drivers/diag656/native.c'))==json.loads((K.parent/'contracts668/audit001.json').read_text())['source_pins']['drivers/diag656/native.c'])
 check('retained667 source clean',not subprocess.check_output(['git','-C','C:/xwn667/source001','diff','--name-only'],timeout=25))
 s=(K/'phase.c').read_text()
 check('single send invocation',s.count('o->send(o->p,')==1)
 check('original packet never sent', 'o->send(o->p,r->transport,BYTES669' in s)
 check('all claimed exits held','goto held;' in s and s.count('return status;')==1 and '__sync_lock_test_and_set(&r->phase,HELD669)' in s)
 check('no existing admission replacement',not (K/'admission.c').exists())
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS',len(r['checks']),'prototype provenance/scope checks')
