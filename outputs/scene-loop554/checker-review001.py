"""Post-close offline checker metadata correction; no guest or disk collection."""
import hashlib,json,subprocess,sys,os
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'tools'));import graphics_sceneloop as g
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=K.parent/'scene-loop553';r=json.loads((prior/'runtime-review002.json').read_text())
assert json.loads((prior/'final-review.json').read_text())['closed']
c=json.loads((prior/'ntfs-cold1-002.json').read_text());p=Path(c['private_path'])/'files/xwn553'
rows=[]
for case in r['rows']:
 name=case['name'];raw=(p/(name+'.txt')).read_bytes()
 actual=g.validate(raw,*[(p/(name+'-'+n+'.bin')).read_bytes() for n in g.scene.SUFFIXES],case['backend'],case['process_exit'])
 expected=dict(case['review']);expected['report_sha256']=hashlib.sha256(raw).hexdigest()
 assert actual==expected
 rows.append(dict(name=name,only_report_hash_changed=True,raw_sha256=hashlib.sha256(raw).hexdigest()))
env=os.environ.copy();env['PYTHONPATH']=os.pathsep.join([str(W/'tools'),str(W/'tests')])
t=subprocess.run([sys.executable,'-B','-m','unittest','test_graphics_sceneloop','-v'],env=env,capture_output=True,text=True,timeout=90)
out=K/'checker-review001.json';assert not out.exists()
out.write_text(json.dumps(dict(passed=t.returncode==0,rows=rows,stdout=t.stdout,stderr=t.stderr,source_sha256=sha(W/'tools/graphics_sceneloop.py'),tests_sha256=sha(W/'tests/test_graphics_sceneloop.py'),guest_runs=0,recollections=0,scope='Return actual raw report hash instead of normalized inherited report hash; all prior scene and telemetry outcomes identical'),indent=2)+'\n')
assert t.returncode==0;print('PASS two offline equivalence checks and five host tests')
