"""Run only the reviewed repair or its independent read-only rescan on the owned Xbox."""
import argparse,datetime,ftplib,hashlib,io,json,os,pathlib,socket
k=pathlib.Path(__file__).resolve().parent;pre=k.parent/'native-windows-fatx-preflight';physical=k.parent/'native-windows-physical-f'
p=argparse.ArgumentParser();p.add_argument('operation',choices=['repair','postscan','postrestore','posttrial','postsoak','postlong','postpaint','postreplay','postmatched']);p.add_argument('action',choices=['launch','collect']);p.add_argument('--resume-upload',action='store_true');a=p.parse_args()
sha=lambda b:hashlib.sha256(b).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
plan=json.loads((k/'repair-plan.json').read_text());assert plan['rehearsal_allocation_consistent'] and not plan['fat_changed'] and not plan['unrelated_entries_changed']
assert json.loads((k/'physical-backup.json').read_text())['snapshot_completed']
assert sha((k/'artifacts/physical-001/cluster-data.bin').read_bytes())==plan['backup_sha256']
for case in ['apply','reject','resume']:
 v=json.loads((k/f'engine-{case}-validation.json').read_text());assert v['passed'] and not v['unplanned_F_changes']
 assert sha((k/'artifacts/repair.xbe').read_bytes())==v['xbe_sha256']
if a.operation=='repair':
 remote='/E/Applications/XWNFatFix';outputs=['repair.txt']
 payloads={'default.xbe':(k/'artifacts/repair.xbe').read_bytes(),'plan.bin':(k/'artifacts/physical-plan.bin').read_bytes(),'rollback-plan.bin':(k/'artifacts/rollback-plan.bin').read_bytes(),'fat-before.bin':(k/'artifacts/physical-001/fat-metadata.bin').read_bytes()}
 assert sha(payloads['plan.bin'])==plan['plan_sha256'] and sha(payloads['rollback-plan.bin'])==plan['rollback_sha256'] and sha(payloads['fat-before.bin'])==plan['metadata_sha256']
else:
 guards={'postscan':('physical-repair.json','completed','XWNFatPost'),'postrestore':('restoration.json','complete','XWNFatFinal'),'posttrial':('physical-trial.json','collected_utc','XWNFatTrial'),'postsoak':('physical-soak.json','collected_utc','XWNFatSoak'),'postlong':('physical-long.json','collected_utc','XWNFatLong')}
 guards['postpaint']=('physical-paint.json','collected_utc','XWNFatPaint')
 guards['postreplay']=('../native-windows-paint-save/physical-replay.json','collected_utc','XWNFatReplay')
 guards['postmatched']=('../native-windows-paint-save/physical-matched.json','collected_utc','XWNFatMatch')
 priorfile,guard,folder=guards[a.operation];prior=json.loads((k/priorfile).read_text());assert prior.get(guard)
 if a.operation in ('posttrial','postsoak','postlong','postpaint','postreplay','postmatched'):assert not prior['startup_restart_enabled']
 remote='/E/Applications/'+folder;outputs=['snapshot.txt','fat-metadata.bin','directories.bin'];payloads={'default.xbe':(pre/'artifacts/default.xbe').read_bytes()}
 assert sha(payloads['default.xbe'])==json.loads((pre/'validation.json').read_text())['xbe_sha256']
record=k/f'physical-{a.operation}.json'
def get(f,path,limit=200*1024*1024):
 b=io.BytesIO()
 def receive(data):
  assert b.tell()+len(data)<=limit;b.write(data)
 f.retrbinary('RETR '+path,receive);return b.getvalue()
def save():record.write_text(json.dumps(r,indent=2)+'\n')
owner=dict(project='xbox-windows-native',purpose=a.operation,xbe_sha256=sha(payloads['default.xbe']),plan_sha256=plan['plan_sha256'])
class FTP(ftplib.FTP):
 def ntransfercmd(self,*args,**kwargs):
  sock,n=super().ntransfercmd(*args,**kwargs);sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1);return sock,n
with FTP() as f:
 f.connect('192.168.50.242',timeout=30);f.login('xbox',os.environ['XWN_FTP_PASSWORD'])
 assert json.loads(get(f,'/F/xwn-deploy-v1.json',65536))==json.loads((physical/'physical-cache-preflight.json').read_text())['ownership_marker']
 cycle=json.loads((physical/'physical-cycle-013.json').read_text());assert not cycle['startup_restart_enabled']
 assert sha(get(f,'/F/Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd',65536))==cycle['current_startup_sha256']
 if a.action=='launch':
  payloads['owner.json']=json.dumps(owner).encode()
  if a.resume_upload:
   r=json.loads(record.read_text());assert not r['launch_attempted'] and r['owner']==owner and r['remote']==remote
   f.cwd(remote);names=[n.replace('\\','/').rstrip('/').split('/')[-1] for n in f.nlst() if n not in ('.','..')];assert set(names)<=set(payloads)
   for name in names:
    partial=get(f,remote+'/'+name);assert payloads[name].startswith(partial),'Unexpected staged bytes'
   r['upload_resumed_utc']=utc();save()
  else:
   assert not record.exists(),'Do not blindly repeat an existing operation'
   f.cwd('/E/Applications');assert remote.rsplit('/',1)[1].lower() not in [n.replace('\\','/').rstrip('/').split('/')[-1].lower() for n in f.nlst()]
   r=dict(operation=a.operation,created_utc=utc(),remote=remote,owner=owner,launch_attempted=False);save();f.mkd(remote)
  for name,data in payloads.items():
   if a.resume_upload:
    try: current=get(f,remote+'/'+name)
    except ftplib.error_perm: current=None
    if current==data:
     print('Already verified',name,len(data),flush=True);continue
   for offset in range(0,max(1,len(data)),32768):
    f.storbinary(('STOR ' if offset==0 else 'APPE ')+remote+'/'+name,io.BytesIO(data[offset:offset+32768]),blocksize=1024)
   assert get(f,remote+'/'+name)==data
   print('Verified',name,len(data),flush=True)
  r.update(launch_attempted=True,launch_utc=utc(),command='SITE EXEC '+remote[1].upper()+':'+remote[2:].replace('/','\\')+'\\default.xbe');save()
  try:r['reply']=f.sendcmd(r['command'])
  except (EOFError,OSError) as e:r['uncertain_reply']=repr(e)
  save();print(r['command'],r.get('reply',r.get('uncertain_reply')))
 else:
  r=json.loads(record.read_text());assert r['launch_attempted'] and not r.get('collected_utc');assert json.loads(get(f,remote+'/owner.json'))==owner
  assert sha(get(f,remote+'/default.xbe'))==owner['xbe_sha256']
  out=k/'artifacts'/a.operation;out.mkdir(exist_ok=True);r['files']=[]
  for name in outputs:
   data=get(f,remote+'/'+name);target=out/name
   if target.exists():assert target.read_bytes()==data
   else:target.write_bytes(data)
   r['files'].append(dict(name=name,bytes=len(data),sha256=sha(data)))
  report=(out/outputs[0]).read_text();r.update(report=report,collected_utc=utc(),completed=('REPAIR_COMPLETE success=1' if a.operation=='repair' else 'SNAPSHOT_COMPLETE success=1') in report);save();print(report)
