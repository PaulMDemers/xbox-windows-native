"""New physicalE matched packet351 test; no console access during preparation."""
import ast,difflib,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;P=K.parent/'hd-phase-physical347';assert not (K/'physical.py').exists()
changes={}
for n in ['physical.py','scan.py','audit.py','typed-state001.py','installed-binding001.py','final-state.py','review-pair.py','closeout.py']:
 old=(P/n).read_text();s=old.replace('xwnphase347','xwneligible353').replace('XWNPhase347','XWNEligible353').replace('xwn347','xwn353').replace('xwn345','xwn351').replace('hd-profile345','eligible-copy351')
 if n=='audit.py':
  s=s.replace("mode=int(case=='candidate001')","mode=1")
  s=s.replace('from phase_analysis import analyze as large_phase',"sys.path.insert(0,str(repo/'outputs/eligible-runtime352'))\nfrom phase352_analysis import analyze as large_phase\nfrom primary_analysis import analyze as primary_analysis")
  s=s.replace('large_phase(v,mode)','large_phase(v,int(case==\'candidate001\'))')
  needle="r['display_workload_passed'] &= all(v['passed'] for v in r['large_phase_samples'])"
  assert s.count(needle)==1;s=s.replace(needle,needle+"\nr['primary_samples']=[primary_analysis(v,int(case=='candidate001')) for v in texts]\nr['display_workload_passed'] &= all(v['passed'] for v in r['primary_samples'])")
 if n=='physical.py':
  needle='    pins();out=K/case;dest=out/\'trial.json\';'
  assert needle in s;s=s.replace(needle,"    assert all(read(K.parent/'eligible-runtime352'/v/'audit.json')['scoped_combined_passed'] for v in ['control001','candidate001'])\n"+needle)
 if n=='review-pair.py':s=s.replace("sample['mode']==mode","sample['mode']==1").replace("'EngCopyBits'","'selected_CopyBits_body'")
 ast.parse(s);(K/n).write_text(s)
 (K/(n+'.patch')).write_text(''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='347/'+n,tofile='353/'+n)))
 changes[n]={'parent_sha256':hashlib.sha256((P/n).read_bytes()).hexdigest(),'sha256':hashlib.sha256((K/n).read_bytes()).hexdigest()}
(K/'source-review.json').write_text(json.dumps(dict(files=changes,physical_access=False,changes='Fresh353 namespaces;351 drivers/probe; both profileON; new eligible352 decoder/strict old functional/event/integrity gates. Actual352 scoped pair required before launch. Original startup then driver restored before collection.'),indent=2)+'\n')
(K/'.gitignore').write_text('artifacts/\n')
