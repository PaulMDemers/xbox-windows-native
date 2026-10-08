"""Preserve the incomplete diagnostic; successful cleanup is not qualification."""
import hashlib,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'candidate001';read=lambda p:json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def validate(t,a,v):
 assert t['status']=='capture_incomplete' and 'ConnectionResetError' in t['error'] and 'ConnectionResetError' in t['resume_error'] and not t.get('guest_resumed')
 assert len(t['desktop_stages'])==5 and t['desktop_calls']==[]
 for phase,stage in enumerate(t['desktop_stages']):assert stage['args']==[0,phase,920 if phase else 0,int(phase!=0)] and len(stage['ownership']['slots'])==1
 assert len({s['ownership']['raw'] for s in t['desktop_stages']})==1
 assert len(t['armed_breakpoints_remaining'])==1
 log=a['log'];assert 'CLOSED 0 1 0\r\nABSENT_AFTER 0 0 0\r\nHARNESS_FAILURE 0 0 4\r\n' in log
 assert 'COMPLETE 1 0 0' in log and 'NORMAL_RESTART_REQUEST 0 0 0' in log
 assert a['normal_shutdown_count']==1 and a['dashboard_return'] and a['integrity_passed'] and a['strict_events_passed']
 assert not a['strict_qualification_passed'] and not a['protocol_exact'] and not v['cold_diagnostic_workload_passed'] and not v['ordinary_qualified']
 assert [f['matched'] for f in a['files']]==[True,True]+[False]*7
 assert v['pagefile_unchanged'];return True
t=read(out/'trace.json');a=read(out/'audit.json');v=read(k/'verification.json');assert validate(t,a,v)
closure=read(out/'closure.json');assert sha(Path(closure['private_disk']))==closure['private_disk_sha256'];assert (Path(closure['private_disk']).parent/'cleanup.json').exists()
for n,h in read(out/'preflight.json')['sources'].items():assert sha(out/'source'/n)==h
for n,h in t['dependencies'].items():assert sha(Path(n))==h
mutations=[]
import copy
for field,value in [('strict_qualification_passed',True),('integrity_passed',False),('normal_shutdown_count',0)]:
 b=copy.deepcopy(a);b[field]=value
 try:validate(t,b,v)
 except AssertionError:mutations.append(field)
 else:raise AssertionError('Mutation accepted')
b=copy.deepcopy(t);b['guest_resumed']=True
try:validate(b,a,v)
except AssertionError:mutations.append('invented breakpoint teardown/resume')
else:raise AssertionError('Mutation accepted')
r=dict(failure_preserved=True,diagnostic_qualified=False,ordinary_qualified=False,physical_qualified=False,markers=5,watched_driver_calls=0,partial_ownership_identical=True,exact_cold_images=2,normal_shutdown=True,clean_cold_integrity=True,breakpoints_removed_before_exit=False,owned_vm_closed=True,mutations_rejected=mutations,pins={n:sha(out/n) for n in ['trace.json','audit.json','closure.json','preflight.json','allocation.json']},cold_verification_sha256=sha(k/'verification.json'),limits='No whole interval or PDEV lifecycle qualification. ABSENT_AFTER zero alone cannot distinguish a nonnull returned handle from NULL with last-error0; capture actual API return next. No driver-fault conclusion.')
dest=k/'failure-verification.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,indent=2))
