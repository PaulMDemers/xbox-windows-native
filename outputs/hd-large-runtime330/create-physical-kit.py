"""Create distinct331 physical measurement; no deployment by this generator."""
import ast,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
assert json.loads((K/'emu001/final-review.json').read_text())['scoped_passed']
old=K.parent/'hd-physical324';new=K.parent/'hd-large-physical331'
assert not new.exists();new.mkdir()
names=['common001.py','capture.py','physical.py','audit.py','preflight.py','freeze.py','test-rollback.py','scan001.py','closeout.py','typed-state001.py','installed-binding001.py']
rows={}
for name in names:
 b=(old/name).read_bytes();s=b.decode('utf-8-sig')
 s=s.replace('xwnhd324','xwnhd331').replace('XWNHD324scan','XWNHD331scan').replace('physical324','physical331')
 if name=='physical.py':s=s.replace('deadline=time.monotonic()+600','deadline=time.monotonic()+1200')
 if name=='freeze.py':
  s=s.replace("k.parent/'hd-emulator323'","k.parent/'hd-large-runtime330'").replace('candidate001/','emu001/')
  s=s.replace('pins={}\n',"files+=list((k.parent/'hd-large327').glob('*.py'))+[k.parent/'hd-large327/build-review003.json']\npins={}\n")
 if name=='audit.py':
  marker="r['checkpoint_history_preserved']=";index=s.index(marker)
  s=s[:index]+"sys.path.insert(0,str(repo/'outputs/hd-large327'))\nfrom large_analysis import analyze as large_analysis\nr['large_samples']=[large_analysis(v) for v in texts]\nr['display_workload_passed'] &= all(v['passed'] for v in r['large_samples'])\n"+s[index:]
 if name=='closeout.py':
  s=s.replace('First Windows1080i hardware trial','New large-area Windows1080i measurement')
 ast.parse(s)
 (new/name).write_bytes(s.encode())
 rows[name]=dict(parent_sha256=hashlib.sha256(b).hexdigest(),sha256=hashlib.sha256(s.encode()).hexdigest())
(new/'source-review.json').write_text(json.dumps(dict(parent='hd-physical324',files=rows,
 changes=['new331 namespace and scan ID','1200second bounded dashboard observer','five327 large parser verdicts added; all original gates retained','new330 emulator evidence'],
 physical_writes=False),indent=2)+'\n')
