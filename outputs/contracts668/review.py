"""Validate audit inputs and boundaries without reopening or rerunning anything."""
import datetime,hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;S=Path('C:/xwn667/source001');B=Path('C:/xwn667/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((K/'audit001.json').read_text());out=K/'review001.json';assert not out.exists()
v=dict(passed=False,physical_access=False,checks=[])
def check(n,b):assert b,n;v['checks'].append(n)
try:
 check('all17 new isolated cases passed',r['passed'] and len(r['handler_cases'])==12 and len(r['sender_cases'])==5 and len(r['static_checks'])==10)
 check('audit source pin',r['source_sha256']==sha(K/'audit.py'))
 check('artifact binary pin',r['image_sha256']==sha(B/'image-crom.bin'))
 check('retained tree pin',subprocess.check_output(['git','-C',str(S),'write-tree'],text=True,timeout=25).strip()==r['source_tree'])
 check('retained source clean',not subprocess.check_output(['git','-C',str(S),'diff','--name-only'],timeout=25))
 for n,h in r['source_pins'].items():check(n,sha(S/n)==h)
 for n,h in r['disassembly_pins'].items():check(n,sha(Path('C:/xwn668/audit001')/n)==h)
 check('IF-clear stops before later admission',next(c for c in r['sender_cases'] if c['name']=='if-clear')['stopped_before_segment_read'])
 check('all sender cases avoid transport',all(c['transport_used']==0 and c['hardware_io']==0 and c['IF_preserved'] for c in r['sender_cases']))
 v['passed']=True
except BaseException as e:v['failure']=repr(e);raise
finally:v['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(v,indent=2)+'\n')
print('PASS',len(v['checks']),'audit provenance and scope checks')
