"""Dispatch an explicitly recorded action list inside WSL, preserving backslashes."""
import hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent
p=Path(sys.argv[1]).resolve();assert p.is_relative_to(K) and p.suffix=='.json'
plan=json.loads(p.read_text());out=p.with_name(p.stem+'-receipt.json');assert not out.exists()
r={'plan_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'steps':[],'complete':False}
out.write_text(json.dumps(r,indent=2)+'\n')
for args in plan:
 assert args and args[0] in ('screen','key','type','mouse','status','block','eject')
 row={'args':args,'requested':True};r['steps'].append(row);out.write_text(json.dumps(r,indent=2)+'\n')
 run=subprocess.run([sys.executable,'-B',str(K/'vm.py'),'604']+args,capture_output=True,text=True,timeout=60)
 row.update(returncode=run.returncode,stdout=run.stdout,stderr=run.stderr);out.write_text(json.dumps(r,indent=2)+'\n')
 print(run.stdout,end='');assert run.returncode==0,run.stderr
r['complete']=True;out.write_text(json.dumps(r,indent=2)+'\n')
