"""Strict ordered desktop protocol and independent RGB oracle."""
import struct
CASES=list(range(9));HOOKS=[]
def fnv(data):
 v=2166136261
 for b in data:v=((v^b)*16777619)&0xffffffff
 return v
def expected_bytes(index):
 assert 0<=index<9
 return b''.join(struct.pack('<I',(((x*3+y*5+index*17)&255)<<16)|(((x*7+y*11+index*29)&255)<<8)|((x*13+y*17+index*43)&255)) for y in range(96) for x in range(128))
def validate_log(data,candidate=True):
 r=dict(passed=False,cases=[],desktop_cycles=[])
 if data is None:return r
 try:
  lines=data.decode('ascii').splitlines();at=0
  def take(label,exact=None):
   nonlocal at
   w=lines[at].split();at+=1;assert len(w)==4 and w[0]==label,(label,w)
   n=list(map(int,w[1:]));assert all(0<=v<=0xffffffff for v in n)
   if exact is not None:assert n==exact,(label,n,exact)
   return n
  def shot(index):
   take('SHOT',[index,12288,0]);digest=fnv(expected_bytes(index));take('DIGEST',[digest,digest,49152]);take('DRIVER',[109,1024,576]);take('COHERENCE',[0,1,0]);take('SHOT_RELEASE',[index,1,1]);r['cases'].append(dict(index=index,reference_hash=digest,passed=True,pixels=12288))
  take('ATTEMPT_ONCE',[126,3,110592]);take('INSTALL_IDLE_START',[0,0,0])
  for i in range(3):
   take('ABSENT_BEFORE',[i,2,0]);shot(i*3);n,h,e=take('CREATED');assert n==i and h and e==0
   take('ATTACHED',[i,1,0]);take('SWITCHED',[i,1,0]);shot(i*3+1);take('RESTORED',[i,1,1]);take('CLOSED',[i,1,0]);take('ABSENT_AFTER',[i,2,0]);shot(i*3+2);take('CYCLE_COMPLETE',[i,3,0]);r['desktop_cycles'].append(dict(index=i,handle=h,created=True,switched=True,restored=True,closed=True,name_absent_after=True))
  for label in ['INPUT_RESTORED','INPUT_CLOSED','CLASS_CLOSED']:take(label,[1,0,0])
  take('COMPLETE',[0,3,110592]);take('INSTALL_IDLE_END',[0,0,0]);take('NORMAL_RESTART_REQUEST',[0,0,0]);assert at==len(lines)
  r.update(passed=True,completed=True,compared_pixels=110592,callback_totals={},unobserved_hooks=['surface/PDEV lifecycle unobserved'])
 except (ValueError,IndexError,AssertionError,UnicodeError) as e:r['error']=repr(e)
 return r
