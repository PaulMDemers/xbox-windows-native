"""Single temporary1080i hardware boot; preserve staged results then restore six files."""
from common001 import *
action=sys.argv[1];assert action in ['launch','observe','collect']
case='physical001';out=k/case;art=k/'artifacts'/case;record=out/'trial.json';remote='/F/xwnhd331'
test_startup=b'@echo off\r\nC:\\xwnhd331\\runner.exe /physical\r\nexit\r\n'
package=read(k/'package.json')
def rollback(f,r,prelaunch_partial=False):
 put(f,startup,incoming(startup));r['startup_enabled']=False;save(record,r)
 for row in package['video']:
  current=get(f,row['path'])
  own_partial=prelaunch_partial and not r['launch_requested'] and any(v.get('path')==row['path'] for v in r['writes'])
  assert own_partial or sha(current) in [row['sha256'],sha(incoming(row['path']))],'Unexpected rollback target'
  put(f,row['path'],incoming(row['path']))
 check_fixed(f);r['baseline_restored']=True;save(record,r)
def launch():
 pins();assert read(k/'capture001.json')['completed'] and not out.exists()
 out.mkdir();art.mkdir(parents=True);r=dict(created_utc=utc(),physical_access=True,launch_requested=False,startup_enabled=False,writes=[],payloads=[],baseline_restored=False);save(record,r)
 with connect(timeout=8) as f:
  check_fixed(f);assert get(f,startup)==incoming(startup)
  for n in ['system','software','sam','security','default']:assert get(f,'/F/winnt/system32/config/'+n)==incoming('/F/winnt/system32/config/'+n)
  for row in package['video']:assert get(f,row['path'])==incoming(row['path'])
  assert remote.rsplit('/',1)[1].lower() not in {n.lower() for n in names(f,'/F')}
  try:
   r['writes'].append(dict(action='mkdir',path=remote));save(record,r);f.mkd(remote)
   for row in package['helpers']:
    p=remote+'/'+row['name'];data=(k/'artifacts/payload'/row['name']).read_bytes();assert sha(data)==row['sha256']
    r['writes'].append(dict(path=p,sha256=sha(data)));save(record,r);put(f,p,data);r['payloads'].append(dict(path=p,sha256=sha(data)));save(record,r)
   for row in package['video']:
    data=(k/'artifacts/payload'/row['name']).read_bytes();assert sha(data)==row['sha256']
    r['writes'].append(dict(path=row['path'],sha256=sha(data)));save(record,r);put(f,row['path'],data)
   r['writes'].append(dict(path=startup,sha256=sha(test_startup)));save(record,r);put(f,startup,test_startup);r['startup_enabled']=True;save(record,r)
   r['staged_protected']=check_fixed(f,True);save(record,r)
  except BaseException as exc:
   r['prelaunch_failure']=type(exc).__name__;save(record,r);rollback(f,r,prelaunch_partial=True);raise
  r.update(launch_requested=True,launch_utc=utc(),command=r'SITE EXEC E:\Applications\XWNFBoot\default.xbe');save(record,r)
  f.sock.settimeout(20)
  try:r['launch_reply']=f.sendcmd(r['command'])
  except ftplib.all_errors as exc:r['launch_reply_uncertain']=type(exc).__name__
  save(record,r)
 print('One physical1080i launch recorded; never relaunch',flush=True)
def observe():
 ticket();r=read(record);assert r['launch_requested'] and not (out/'return.json').exists()
 result=dict(dashboard_return=False,offline_observed=False,samples=[],new_launches=0,observer_pid=os.getpid());deadline=time.monotonic()+1200
 while time.monotonic()<deadline:
  row=dict(utc=utc(),dashboard=False)
  try:
   with connect(timeout=3) as f:row['dashboard']=True
  except Exception as exc:row['error_type']=type(exc).__name__;result['offline_observed']=True
  result['samples'].append(row);result['dashboard_return']=row['dashboard'] and result['offline_observed'];save(out/'return.json',result)
  if result['dashboard_return']:break
  time.sleep(min(5,max(0,deadline-time.monotonic())))
 result.update(closed=True,closed_utc=utc());save(out/'return.json',result);print('Dashboard return:',result['dashboard_return'],flush=True)
def collect():
 pins();trial=read(record);assert trial['launch_requested']
 dest=out/'collection.json';assert not dest.exists();r=dict(created_utc=utc(),completed=False,files={},inventories={},startup_restored=False);save(dest,r)
 with connect(timeout=8) as f:
  assert get(f,startup) in [incoming(startup),test_startup]
  put(f,startup,incoming(startup));r['startup_restored']=True;trial['startup_enabled']=False;save(record,trial);save(dest,r)
  # Preserve actual candidate bytes BEFORE restoring the baseline. No registry rollback.
  for row in package['video']:
   p=row['path'];data=get(f,p);r['files'][p]=keep(art,p,data);save(dest,r)
   assert sha(data)==row['sha256'],'Candidate file changed'
  rollback(f,trial);r['baseline_restored']=True;save(dest,r)
  logs=['attempt.log','wizard201.log','setup-before.log','setup-after.log','state207.log','audio207.log']+['sample%d/gdi-baseline.txt'%i for i in range(5)]
  for n in logs:
   p=remote+'/'+n;data=get(f,p,optional=True);r['files'][p]=None if data is None else keep(art,p,data);save(dest,r)
  paths=list(fixed())+[startup,'/F/winnt/setupapi.log','/F/winnt/system32/xwn-video-trace.bin']
  for n in ['system','software','sam','security','default','sysevent.evt','appevent.evt']:paths.append('/F/winnt/system32/config/'+n)
  r['inventories']['/F/winnt/inf']=names(f,'/F/winnt/inf')
  for n,row in r['inventories']['/F/winnt/inf'].items():
   if not row['directory']:paths.append('/F/winnt/inf/'+n)
  for p in dict.fromkeys(paths):
   if p in r['files']:continue # Staged candidate bytes already captured; retain them.
   data=get(f,p);r['files'][p]=keep(art,p,data)
   if '/config/' in p:assert get(f,p)==data
   save(dest,r)
  for row in trial['payloads']:assert sha(get(f,row['path']))==row['sha256']
  expected=dict(fixed());expected.update({v['path']:v['sha256'] for v in package['video']})
  r['protected_files_unchanged']=all(r['files'][p]['sha256']==h for p,h in expected.items())
  r['restored_payloads']={v['path']:sha(get(f,v['path']))==sha(incoming(v['path'])) for v in package['video']};assert all(r['restored_payloads'].values())
  r.update(completed=True,completed_utc=utc(),dashboard_available=True);save(dest,r)
 print('Evidence collected; normal startup and all six baseline files restored',flush=True)
globals()[action]()
