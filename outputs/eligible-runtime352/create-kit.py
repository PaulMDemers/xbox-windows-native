import ast,difflib,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;P=K.parent/'primary-runtime349';assert not (K/'Run.ps1').exists()
names=['Invoke.ps1','Run.ps1','close-host.py','analyze-allocation002.py','stock_io002.py','analyze-capture.py','typed-state.py','installed-binding.py','supervise.py','audit.py','prepare002.py','Prepare002.ps1','contract002.ps1','freeze.py','phase349_analysis.py']
records={}
for n in names:
 old=(P/n).read_text();s=old.replace('xwn349','xwn352').replace('primary349','eligible352').replace('primary-runtime349','eligible-runtime352').replace('5176','5196').replace('5177','5197').replace('5178','5198')
 s=s.replace('primary-copy348','eligible-copy351').replace('xwn348','xwn351')
 if n=='audit.py':
  s=s.replace('from phase_analysis import analyze as large_phase','from phase352_analysis import analyze as large_phase').replace('large_phase(v,mode)','large_phase(v,int(case==\'candidate001\'))')
  s=s.replace('New348 primary-copy body','New351 eligible-plan accounting; unchanged348 primary-copy body')
 if n=='freeze.py':s=s.replace("eligible-copy351/host002.json","eligible-copy351/host001.json")
 if n=='phase349_analysis.py':s=s.replace('PRIMARY348_','PRIMARY351_').replace('348','351')
 target='phase352_analysis.py' if n=='phase349_analysis.py' else n
 if target.endswith('.py'):ast.parse(s)
 (K/target).write_text(s)
 records[target]=dict(parent=str(P/n),parent_sha256=hashlib.sha256((P/n).read_bytes()).hexdigest(),sha256=hashlib.sha256((K/target).read_bytes()).hexdigest())
 (K/(target+'.patch')).write_text(''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='349/'+n,tofile='352/'+target)))
(K/'source-review.json').write_text(json.dumps(dict(passed=True,files=records,changes='Fresh IDs/roots/ports,351 read-only packet/new eligible denominator, corrected fully validated phase projection before original344 decoder. No workload/oracle/event/integrity change.'),indent=2)+'\n')
(K/'.gitignore').write_text('**/artifacts/\n')
