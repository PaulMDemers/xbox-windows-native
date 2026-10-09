"""Read-only baseline/startup/SYSTEM/payload/rollback verification after trial, no launch."""
import importlib.util,json,sys
from pathlib import Path
base=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['control001','candidate001'];k=base/case
sys.argv=['physical-controller.py','inspect',case]
spec=importlib.util.spec_from_file_location('controller',base/'physical-controller.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
dest=k/'restored-verification.json';assert not dest.exists();r=c.read(c.record)
assert r['baseline_restored'] and not r['startup_enabled']
with c.m.connect() as f:
    c.m.owner(f);rows=c.fixed_checks(f);payloads=[]
    for path,_,_ in c.changes:
        old=r['before_payloads'][path]
        matched=c.absence(f,path.rsplit('/',1)[0],path.rsplit('/',1)[1]) if old is None else c.sha(c.m.get(f,path))==old['sha256']
        payloads.append(dict(path=path,matched=matched,originally_absent=old is None))
    rollback=c.sha(c.m.get(f,'/F/'+c.rollback_dir+'/current-rollback202.zip'))==r['rollback_sha256']
result=dict(scope=__doc__,utc=c.m.utc(),read_only=True,files=rows,payloads=payloads,console_rollback_exact=rollback,
    passed=rollback and all(v['matched'] for v in payloads),physical_qualified=False,launches_issued=0)
dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(restored_verified=result['passed'],fixed_files=len(rows),payloads=payloads)))
