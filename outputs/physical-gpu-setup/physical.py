"""Prepare a reversible GPU PnP setup using unchanged video0093; no Windows launch."""
import argparse,hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;sys.path.insert(0,str(k.parent/'fatx0101-physical'));import physical as m
remote='/F/xwninf102';software='/F/winnt/system32/config/software';art=k/'artifacts';record=k/'physical.json'
def main(action):
 with m.connect() as f:
  m.owner(f);checks=m.checks(f,True);assert m.passed(checks)
  if action=='prepare':
   assert not record.exists();m.missing(f,remote);art.mkdir(exist_ok=True)
   r=dict(scope=__doc__,prepared_utc=m.utc(),checks=checks,staged=False,launch_attempted=False,before={},remote=remote)
   for name,path in [('software',software),('system','/F/winnt/system32/config/system'),('setupapi.log','/F/winnt/setupapi.log'),('system.evt','/F/winnt/system32/config/sysevent.evt'),('application.evt','/F/winnt/system32/config/appevent.evt'),('startup.cmd',m.startup),('xboxvnt5.sys','/F/winnt/system32/drivers/xboxvnt5.sys')]:
    data=m.get(f,path);(art/('before-'+name)).write_bytes(data);r['before'][name]=dict(path=path,sha256=m.sha(data),bytes=len(data))
   inf=(k.parent/'shutdown-device-install/xwnvideo.inf').read_bytes();(art/'xwnvideo.inf').write_bytes(inf);r['inf_sha256']=m.sha(inf);m.save(r,record);print('Baseline preserved; no remote writes')
  else:
   r=json.loads(record.read_text());assert not r['staged'] and not r['launch_attempted'];m.missing(f,remote)
   proof=json.loads((k/'software-edit.json').read_text());assert proof['only_expected_value_changed']
   before=(art/'before-software').read_bytes();after=(art/'edited-software').read_bytes()
   assert m.sha(before)==proof['before_sha256']==r['before']['software']['sha256'] and m.sha(after)==proof['after_sha256']
   for name,row in r['before'].items():assert m.sha(m.get(f,row['path']))==row['sha256'],name+' changed'
   inf=(art/'xwnvideo.inf').read_bytes();binary=(art/'before-xboxvnt5.sys').read_bytes();assert m.sha(inf)==r['inf_sha256'] and m.sha(binary)==r['before']['xboxvnt5.sys']['sha256']
   m.save(dict(project='xbox-windows-native',purpose='gpu-setup',inf_sha256=m.sha(inf)),art/'owner.json')
   f.mkd(remote)
   for name,data in [('owner.json',(art/'owner.json').read_bytes()),('software.bak',before),('xwnvideo.inf',inf),('xboxvnt5.sys',binary)]:m.put(f,remote+'/'+name,data)
   r['hive_write_attempted']=True;m.save(r,record)
   try:m.put(f,software,after)
   except Exception:
    m.put(f,software,before);r['rolled_back_after_error']=True;m.save(r,record);raise
   assert m.get(f,software)==after and m.passed(m.checks(f,True))
   r.update(staged=True,staged_utc=m.utc(),software_after_sha256=m.sha(after));m.save(r,record);print('GPU package and one DevicePath value staged/readback verified; Windows not launched')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','stage']);main(p.parse_args().action)
