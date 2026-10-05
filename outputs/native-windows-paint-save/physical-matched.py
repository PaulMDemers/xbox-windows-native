"""One physical Paint-shaped replay; preserve the old test directory by rename."""
import argparse,importlib,json,os,pathlib
m=importlib.import_module('physical-replay');k=m.k
record=k/'physical-matched.json';m.folder=k/'artifacts/physical-matched'
load=lambda p:json.loads(p.read_text())
old=load(k/'physical-replay.json')
root='/F/xwnpaint';backup='/F/xwnpaint64';archive='/F/xwnpaint16'
oldfiles={**old['payloads'],**{n:v for n,v in old['collected'].items() if n in ('attempt.log','replay.log') or (n.startswith('replay') and n.endswith('.bmp'))}}
def names(f,path):
 f.cwd(path)
 return {n.replace('\\','/').rstrip('/').split('/')[-1].lower() for n in f.nlst() if n not in ('.','..')}
def verify_old(f,path):
 assert names(f,path)==set(oldfiles),'Unexpected files in previous owned test'
 for n,v in oldfiles.items():assert m.sha(m.get(f,path+'/'+n))==v['sha256'],n
def save():record.write_text(json.dumps(r,indent=2)+'\n')
def restore_names(f):
 # No deletes: retain this run separately and put the original directory back.
 current=names(f,'/F')
 if 'xwnpaint64' in current:
  if 'xwnpaint' in current:
   assert 'xwnpaint16' not in current
   f.rename(root,archive);r['results_archived']=True;save()
  f.rename(backup,root)
 verify_old(f,root);r['previous_directory_restored']=True;save()
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['launch','collect']);a=p.parse_args()
 m.folder.mkdir(parents=True,exist_ok=True)
 with m.FTP() as f:
  f.connect('192.168.50.242',timeout=30);f.login('xbox',os.environ['XWN_FTP_PASSWORD'])
  assert json.loads(m.get(f,'/F/xwn-deploy-v1.json'))==load(m.physical/'physical-cache-preflight.json')['ownership_marker']
  if a.action=='launch':
   assert not record.exists(),'Never repeat an existing launch record'
   assert load(k/'physical-replay-qualification.json')['passed']
   assert load(k/'matched-emulator-validation.json')['passed']
   fixture=load(k/'matched-fixture.json');build=load(k/'matched-build-review.json')
   assert m.sha((k/'matched.c').read_bytes())==build['source_sha256']
   m.verify(f);baseline=m.get(f,m.startup);assert m.sha(baseline)==old['previous_startup_sha256']
   assert not {'xwnpaint64','xwnpaint16'} & names(f,'/F');verify_old(f,root)
   payloads={}
   for row in fixture['helpers']:
    name=pathlib.PurePosixPath(row['path']).name
    data=(k/'artifacts'/('matched.exe' if name=='replay.exe' else name)).read_bytes()
    assert m.sha(data)==row['sha256'];payloads[name]=data
   payloads['scribble.bmp']=(k/'artifacts/images/scribble.bmp').read_bytes()
   assert m.sha(payloads['scribble.bmp'])==old['payloads']['scribble.bmp']['sha256']
   script=b'@echo off\r\nC:\\xwnpaint\\runner.exe\r\nexit\r\n';assert m.sha(script)==fixture['startup_sha256']
   r=dict(scope=__doc__,created_utc=m.utc(),launch_attempted=False,startup_restart_enabled=False,
          startup_sha256=m.sha(script),previous_startup_sha256=m.sha(baseline),expected_drivers=m.checks,
          filesystem_sha256=old['filesystem_sha256'],miniport_sha256=old['miniport_sha256'],
          preserved={},payloads={n:dict(bytes=len(b),sha256=m.sha(b)) for n,b in payloads.items()},old_directory_hashes=oldfiles)
   r['preserved']['startup.cmd']=m.preserve('before-startup.cmd',baseline)
   for n,path in m.logs.items():r['preserved'][n]=m.preserve('before-'+n,m.get(f,path))
   save()
   try:
    f.cwd('/F');f.rename(root,backup);r['previous_directory_renamed']=True;save()
    f.mkd(root)
    for n,data in payloads.items():m.put(f,root+'/'+n,data)
    m.put(f,m.trace,b'XWN-VID-TRACE01\n'+bytes(4080));m.put(f,m.startup,script)
    r['startup_restart_enabled']=True;save();m.verify(f)
    r.update(launch_attempted=True,launch_utc=m.utc(),command='SITE EXEC E:\\Applications\\XWNFBoot\\default.xbe');save()
    try:r['reply']=f.sendcmd(r['command'])
    except (EOFError,OSError) as e:r['uncertain_reply']=repr(e)
    save();print('Single matched hardware replay launched:',r.get('reply',r.get('uncertain_reply')))
   except Exception as e:
    r['error']=repr(e);save()
    if not r['launch_attempted']:
     m.put(f,m.startup,baseline);r['startup_restart_enabled']=False;save()
     if r.get('previous_directory_renamed'):restore_names(f)
    raise
  else:
   r=load(record);assert r['launch_attempted'] and not r.get('collected_utc')
   baseline=(m.folder/'before-startup.cmd').read_bytes();assert m.sha(baseline)==r['previous_startup_sha256']
   current=m.get(f,m.startup);assert m.sha(current) in (r['startup_sha256'],r['previous_startup_sha256'])
   if current!=baseline:m.put(f,m.startup,baseline)
   r['startup_restart_enabled']=False;save()
   try:
    current=names(f,'/F');source=archive if 'xwnpaint16' in current else root
    r['collected']={}
    paths={**m.logs,'attempt.log':source+'/attempt.log','matched.log':source+'/matched.log',
           **{f'match{i:02d}.bmp':source+f'/match{i:02d}.bmp' for i in range(16)}}
    for n,path in paths.items():
     data=m.get(f,path,optional=n.startswith('match') or n=='attempt.log')
     r['collected'][n]=None if data is None else m.preserve('after-'+n,data);save()
    r['driver_checks']={path:m.sha(m.get(f,path))==h for path,h in m.checks.items()}
    r['payload_checks']={n:m.sha(m.get(f,source+'/'+n))==v['sha256'] for n,v in r['payloads'].items()}
    def text(n):return (m.folder/('after-'+n)).read_bytes().decode('ascii',errors='replace') if r['collected'][n] else ''
    r['runner_log']=text('attempt.log');r['matched_log']=text('matched.log')
    expected=r['payloads']['scribble.bmp']['sha256']
    r['all_images_match']=all(r['collected'][f'match{i:02d}.bmp'] and r['collected'][f'match{i:02d}.bmp']['sha256']==expected for i in range(16))
    r['user_partial_unchanged']=r['collected']['user-partial.bmp']==r['preserved']['user-partial.bmp']
    log=r['matched_log']
    r['workload_passed']=bool(r['all_images_match'] and log.count('CASE_PASS ')==16 and '\nPASS 16 ' in log and 'FAIL_' not in log
       and log.count('WRITE_BEGIN ')==8*29 and all(f'CASE_BEGIN_QUIET {i} 0 {i&1} ' in log and f'SEQUENCE_DONE {i} 29 29 ' in log for i in range(16))
       and r['runner_log']=='ATTEMPT_ONCE\r\nREPLAY_EXIT_ZERO\r\nNORMAL_RESTART_REQUEST\r\n'
       and all(r['driver_checks'].values()) and all(r['payload_checks'].values()) and r['user_partial_unchanged'])
    restore_names(f)
    r.update(collected_utc=m.utc(),qualification_pending='Event review and separate allocation/binary/hive checks');save()
    print('Collected; startup disabled, old directory restored; workload passed:',r['workload_passed'])
   except Exception as e:r['collection_error']=repr(e);save();raise
