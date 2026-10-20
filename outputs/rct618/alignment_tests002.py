"""Separate-read timestamps: preserve order, reject wrong pairing or windows."""
import copy,json,hashlib
from pathlib import Path
from alignment_oracle002 import alignment
K=Path(__file__).resolve().parent;out=K/'alignment-tests002.json';assert not out.exists()
rejected=[]
parsed=dict(phase_ends=[[1,3,128]],phase_rows=[[1,32,3]],calls={i:dict(api=11,phase=0 if i<=32 else 1) for i in range(1,65)})
extra=[('COST_PID',[12,20,0]),('COST_CREATED',[40,50,0])]
for phase,first,count in [(0,1000,35),(1,40100,160)]:
 step=10 if not phase else 125
 extra.extend([('COST_HIT_START',[phase,first,count]),('COST_HIT_END',[phase,first+(count-1)*step,count])])
 for j in range(count):extra.append(('COST_HIT',[phase,j,first+j*step]))
 for j in range(32):
  ident=1+j+phase*32;tick=first+j*step
  extra.extend([('COST_CALL',[ident,phase,tick]),('COST_RETURN',[ident,phase,tick+1])])
args=(parsed,extra,[12,20,30,40,50],40000,60000,[40000,40000,40100],195)
assert alignment(*args)['strict_interior_hits']==160
variants2=[]
for name,kind,mut in [
 ('missing_entry','COST_HIT',lambda v:[v[0],v[1]+1,v[2]]),
 ('wrong_entry_tick','COST_HIT',lambda v:[v[0],v[1],90000]),
 ('wrong_hit_count','COST_HIT_START',lambda v:[v[0],v[1],v[2]-1]),
 ('late_return','COST_RETURN',lambda v:[v[0],v[1],60001]),
 ('wrong_subject','COST_PID',lambda v:[13,v[1],v[2]]),
 ('wrong_creation','COST_CREATED',lambda v:[41,v[1],v[2]])]:
 e=copy.deepcopy(extra)
 index=next(i for i,(k,v) in enumerate(e) if k==kind and (kind in ['COST_PID','COST_CREATED'] or (v[0]==1 if kind.startswith('COST_HIT') else v[1]==1)))
 e[index]=(kind,mut(e[index][1]));variants2.append((name,(parsed,e,*args[2:])))
variants2.extend([
 ('request_before_start',(parsed,extra,*args[2:5],[39999,40000,40100],195)),
 ('ack_after_end',(parsed,extra,*args[2:5],[40000,40000,60001],195)),
 ('wrong_copy_total',(*args[:-1],194)),
 ('missing_sample_stamp',(parsed,extra[:-1],*args[2:]))])
for name,a in variants2:
 try:alignment(*a)
 except (AssertionError,ValueError,KeyError):rejected.append(name)
 else:raise AssertionError(name)

e=copy.deepcopy(extra)
for i,(kind,v) in enumerate(e):
 if kind in ['COST_CALL','COST_RETURN'] and v[0]==33:
  e[i]=(kind,[v[0],v[1],v[2]+16])
assert alignment(parsed,e,*args[2:])['passed']
for name,call,ret in [('call_before_entry',40099,40101),('return_before_call',40116,40115),('call_after_next_entry',40226,40227)]:
 bad=copy.deepcopy(extra)
 for i,(kind,v) in enumerate(bad):
  if kind=='COST_CALL' and v[0]==33:bad[i]=(kind,[33,1,call])
  if kind=='COST_RETURN' and v[0]==33:bad[i]=(kind,[33,1,ret])
 try:alignment(parsed,bad,*args[2:])
 except AssertionError:rejected.append(name)
 else:raise AssertionError(name)
out.write_text(json.dumps(dict(passed=True,rejected=rejected,positive_separate_reads_16ms=True,
 oracle_sha256=hashlib.sha256((K/'alignment_oracle002.py').read_bytes()).hexdigest(),
 scope='Ordered entry/call/return association; phase/window/identity/count gates retained. No guest or source binary changes.'),indent=2)+'\n')
print('Ordered timestamp tests passed',len(rejected),'negative cases')
