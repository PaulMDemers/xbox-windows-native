"""Second GPU setup boot explicitly requested after the user's interrupted wizard/reboot; never repeat launch."""
import argparse,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;sys.path.insert(0,str(k.parent/'fatx0101-physical'));import physical as m
p=argparse.ArgumentParser();p.add_argument('action',choices=['launch','collect']);a=p.parse_args();case=k/'002';record=case/'physical.json';first=json.loads((k/'physical.json').read_text());review=json.loads((k/'first-setup-review.json').read_text());assert first.get('collected_utc')
with m.connect() as f:
 m.owner(f);checks=m.checks(f,True);assert m.passed(checks)
 assert m.sha(m.get(f,m.startup))==first['before']['startup.cmd']['sha256']
 if a.action=='launch':
  assert not record.exists();assert all(v['structural_walk_passed'] for v in review['hives'].values());assert len(review['gpu'])==1
  g=review['gpu'][0];assert g['values']['ConfigFlags']==0 and g['values']['Service']=='XboxVnt5' and g['driver_key']['InfPath']=='oem2.inf'
  for name,row in first['after'].items():assert m.sha(m.get(f,row['path']))==row['sha256'],'Changed collected state: '+name
  inf=m.get(f,'/F/winnt/inf/oem2.inf');assert inf==(k/'artifacts/xwnvideo.inf').read_bytes()
  assert m.get(f,first['remote']+'/software.bak')==(k/'artifacts/before-software').read_bytes()
  case.mkdir(exist_ok=True);out=case/'artifacts';out.mkdir(exist_ok=True);(out/'before-oem2.inf').write_bytes(inf)
  r=dict(scope=__doc__,created_utc=m.utc(),authorization='User reports reboot after difficulty selecting GPU driver and explicitly requests relaunch. Prior keyboard readiness confirmed; reminded to keep it unplugged through Xromwell.',first_run_review_sha256=m.sha((k/'first-setup-review.json').read_bytes()),checks=checks,before=first['after'],oem_inf_sha256=m.sha(inf),launch_attempted=True,launch_utc=m.utc(),command='SITE EXEC E:\\Applications\\XWNFBoot\\default.xbe',automatic_restart=False,physical_writes=False,first_run_caveat='GPU binding installed, but new SetupAPI log has92 non-ASCII bytes; cause unresolved. First reboot method not independently established.')
  m.save(r,record)
  try:r['launch_reply']=f.sendcmd(r['command'])
  except Exception as e:r['launch_reply_uncertain']=type(e).__name__
  m.save(r,record);print('Authorized second boot requested once; installed GPU INF and baseline verified')
 else:
  r=json.loads(record.read_text());assert r['launch_attempted'] and not r.get('collected_utc');out=case/'artifacts';r['after']={}
  for name,row in r['before'].items():
   data=m.get(f,row['path']);target=out/('after-'+name)
   if target.exists():assert target.read_bytes()==data
   else:target.write_bytes(data)
   r['after'][name]=dict(path=row['path'],bytes=len(data),sha256=m.sha(data))
  r.update(collected_utc=m.utc(),qualification='Pending logs, binding, event and integrity review; no PASS inferred from return');m.save(r,record);print('Second boot artifacts collected once')
