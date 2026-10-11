"""Add one worker close/release within acknowledged UI closure; failure cleanup."""
from pathlib import Path
k=Path(__file__).resolve().parent;p=k/'trace.py';s=p.read_text()
assert 'worker_requested' not in s
s=s.replace('frontend_requested=False;frontend_reopened=False','frontend_requested=False;frontend_reopened=False\nworker_requested=False;worker_released=False')
anchor=" # No new frame may start throughout this interval. Keep all shared objects."
assert s.count(anchor)==1
s=s.replace(anchor,''' # Worker admission is separate. Request while CPU stopped/UI acknowledged.
 worker_requested=True;r['worker_request_may_be_accepted']=True;save()
 reply=cmd('qom-set '+r['nv2a_qom_path']+' xwn-worker247-close true');assert 'Error' not in reply
 deadline=time.monotonic()+8
 while True:
  reply=cmd('qom-get '+r['nv2a_qom_path']+' xwn-worker247-report')
  state=int(re.search(r'(?<![a-z_])state=(\\d+)',reply)[1])
  if state in [3,5,6]:break
  assert time.monotonic()<deadline;time.sleep(.025)
 r['worker_closed_report']=reply;save()
 assert state==3,'Worker explicitly refused/expired; preserve evidence, never retry'
 time.sleep(.2)
 r['worker_closed_reread']=cmd('qom-get '+r['nv2a_qom_path']+' xwn-worker247-report');save()
 assert r['worker_closed_reread']==reply
 reply=cmd('qom-set '+r['nv2a_qom_path']+' xwn-worker247-close false');assert 'Error' not in reply
 worker_released=True;r['worker_release_requested']=True;save()
 deadline=time.monotonic()+8
 while True:
  reply=cmd('qom-get '+r['nv2a_qom_path']+' xwn-worker247-report')
  state=int(re.search(r'(?<![a-z_])state=(\\d+)',reply)[1])
  if state in [5,6]:break
  assert time.monotonic()<deadline;time.sleep(.025)
 r['worker_released_report']=reply;save();assert state==5
 r['worker_scope_passed']=True;save()
''' +anchor)
anchor=' if frontend_requested and not frontend_reopened:'
assert s.count(anchor)==1
s=s.replace(anchor,''' if worker_requested and not r.get('worker_scope_passed'):
  try:
   reply=cmd('qom-get '+r['nv2a_qom_path']+' xwn-worker247-report')
   state=int(re.search(r'(?<![a-z_])state=(\\d+)',reply)[1])
   if state in [1,2,3] and not worker_released:
    reply=cmd('qom-set '+r['nv2a_qom_path']+' xwn-worker247-close false')
    r['worker_failure_release_reply']=reply;worker_released='Error' not in reply
   deadline=time.monotonic()+8
   while True:
    reply=cmd('qom-get '+r['nv2a_qom_path']+' xwn-worker247-report')
    state=int(re.search(r'(?<![a-z_])state=(\\d+)',reply)[1])
    r['worker_failure_terminal']=reply;save()
    if state in [0,5,6]:break
    assert time.monotonic()<deadline;time.sleep(.025)
   r['worker_failure_released_or_refused']=True
  except Exception as exc:r['worker_failure_cleanup_error']=repr(exc);quarantined=True
''' +anchor)
p.write_text(s)
print('247 one request/release and acknowledged failure cleanup prepared')
