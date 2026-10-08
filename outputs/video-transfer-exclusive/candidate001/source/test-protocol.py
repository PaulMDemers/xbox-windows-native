"""Synthetic protocol mutations test gates, never count as guest evidence."""
import hashlib,json
from pathlib import Path
from protocol import *
k=Path(__file__).resolve().parent;dest=k/'protocol-tests.json';assert not dest.exists()
lines=[]
def emit(label,*values):lines.append(label+' '+' '.join(map(str,values)))
emit('ATTEMPT_ONCE',139,45,W*H);emit('INSTALL_IDLE_START',0,0,0);emit('DRIVER_REVISION_GEOMETRY',112,1024,576)
emit('CLOCK_FREQUENCY',1000000,0,0);emit('CLOCK_MIN',1,0,0);emit('CLOCK_MAX',10,0,0);emit('CLOCK_READS',8192,0,0);emit('TICK_MIN',15,0,0)
for i in range(3):emit('SLEEP_QPC',200000,0,i);emit('SLEEP_TICK',i,200,0)
for n in range(45):
 size,kind=identity(n);w,h=SIZES[size];rects=rectangles(n);emit('CASE',n,size,kind);emit('LAYOUT',w,h,len(rects));emit('CLIP_TYPE_LEFT_TOP',2,0,0);emit('CLIP_RIGHT_BOTTOM',1024,576,n)
 for target in ([1,0] if n&1 else [0,1]):
  loops=32;emit('PHASE',n,target,loops);emit('CALIBRATION',8,32,500);emit('DURATION_QPC',500000,0,0);emit('DURATION_MS',500,0,0)
  for i in range(2,19):
   after=0
   if target:
    if i==2:after=loops
    if i==16:after=loops*len(rects)
    if i==17:after=loops*w*h*4
   emit('QUIET_COUNTER',i,0,0);emit('DRAW_COUNTER',i,0,after)
  emit('COHERENCE_ACTIVE',0,1,0)
 emit('PIXELS_BAD_CHANGED',W*H,0,w*h);emit('REFERENCE_HASH_BYTES',1,W*H*4,1)
emit('RELEASED',1,0,0);emit('CLOCK_FREQUENCY_END',1000000,0,0);emit('COMPLETE',0,45,45*W*H);emit('INSTALL_IDLE_END',0,0,0);emit('NORMAL_RESTART_REQUEST',0,0,0)
data=('\n'.join(lines)+'\n').encode();r=validate_log(data);assert r['passed'] and r['timing_passed'] and r['profile_attribution_passed']
rejected=[]
for name,old,new in [('pixel',b'PIXELS_BAD_CHANGED 294912 0 ',b'PIXELS_BAD_CHANGED 294912 1 '),('bytes',b'DRAW_COUNTER 17 0 524288',b'DRAW_COUNTER 17 0 524292'),('rectangles',b'DRAW_COUNTER 16 0 32',b'DRAW_COUNTER 16 0 33'),('frequency_changed',b'CLOCK_FREQUENCY_END 1000000',b'CLOCK_FREQUENCY_END 1000001'),('completion',b'COMPLETE 0 45',b'COMPLETE 1 45'),('backwards_clock',b'CLOCK_READS 8192 0 0',b'CLOCK_READS 8192 0 1')]:
 assert old in data;assert not validate_log(data.replace(old,new,1))['passed'];rejected.append(name)
short=validate_log(data.replace(b'DURATION_MS 500 0 0',b'DURATION_MS 100 0 0',1));assert short['passed'] and not short['timing_passed']
quiet=validate_log(data.replace(b'QUIET_COUNTER 2 0 0',b'QUIET_COUNTER 2 1 0',1));assert quiet['passed'] and not quiet['profile_attribution_passed']
result=dict(passed=True,synthetic_only=True,valid_45case_protocol=True,rejected=rejected,short_batch_timing_rejected=True,quiet_contamination_attribution_rejected=True,pins={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['protocol.py','test-protocol.py']})
dest.write_text(json.dumps(result,indent=2)+'\n');print('Synthetic protocol and8 failure-gate checks passed')
