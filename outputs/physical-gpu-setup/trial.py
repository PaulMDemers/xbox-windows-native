"""Launch the staged GPU setup once after confirmed keyboard readiness, or collect after user restart."""
import argparse,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;sys.path.insert(0,str(k.parent/'fatx0101-physical'));import physical as m
p=argparse.ArgumentParser();p.add_argument('action',choices=['launch','collect']);p.add_argument('--keyboard-unplugged',action='store_true');a=p.parse_args()
record=k/'physical.json';r=json.loads(record.read_text());assert r['staged'];art=k/'artifacts'
with m.connect() as f:
 m.owner(f);assert m.passed(m.checks(f,True));assert m.sha(m.get(f,m.startup))==r['before']['startup.cmd']['sha256']
 assert m.get(f,r['remote']+'/software.bak')==(art/'before-software').read_bytes()
 assert m.sha(m.get(f,r['remote']+'/xwnvideo.inf'))==r['inf_sha256']
 if a.action=='launch':
  assert a.keyboard_unplugged,'Require actual human confirmation; do not infer readiness'
  assert not r['launch_attempted'],'Never repeat recorded launch'
  assert m.sha(m.get(f,r['before']['software']['path']))==r['software_after_sha256']
  r.update(launch_attempted=True,launch_utc=m.utc(),keyboard_readiness='Human confirmed unplugged before this launch',command='SITE EXEC E:\\Applications\\XWNFBoot\\default.xbe',automatic_restart=False)
  m.save(r,record)
  try:r['launch_reply']=f.sendcmd(r['command'])
  except Exception as e:r['launch_reply_uncertain']=type(e).__name__
  m.save(r,record);print('One GPU setup boot requested; leave desktop running for setup')
 else:
  assert r['launch_attempted'] and not r.get('collected_utc')
  r['after']={}
  for name,row in r['before'].items():
   data=m.get(f,row['path']);target=art/('after-'+name)
   if target.exists():assert target.read_bytes()==data
   else:target.write_bytes(data)
   r['after'][name]=dict(path=row['path'],bytes=len(data),sha256=m.sha(data))
  r.update(collected_utc=m.utc(),qualification='Pending SetupAPI/device-binding/event review; FTP return alone is not PASS')
  m.save(r,record);print('Post-setup artifacts preserved; review GPU binding and event deltas')
