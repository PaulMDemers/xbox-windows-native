"""Original synthetic counter/transport checks before any guest launch."""
import copy,hashlib,json
from pathlib import Path
from cost_oracle import validate
from serial_host import Lines
K=Path(__file__).resolve().parent;out=K/'host-tests001.json';assert not out.exists()
def row(tag,i,ms,cpu=10000,ws=12*1024**2,index=0):
 return f'{tag} {i} {index} {ms:016x} {ms} 0000000000002710 {cpu:016x} {ws} {ws} {ws}'
# Use the scalar-verified613 2^25-step affine block32 times.
mod=2**32;mul=pow(1664525,33554432,mod);add=(3523215361-mul)%mod;checksum=1
for _ in range(32):checksum=(mul*checksum+add)%mod
p=['FREQ 00000000000003e8'];children=[];host=dict(connected=True,closed=True,rows=[])
for i in range(6):
 base=10000+i*10000;duration=5000 if i<2 else 2000;cpu=10000 if i<2 else 15010000
 p += [row('START',i,base),row('END',i,base+duration+200,cpu),row('OBSERVER_START',i,base+1),row('OBSERVER_END',i,base+duration+201)]
 periodic=i in [1,3,4]
 if periodic:
  p += [row('SAMPLE',i,base+100+j*100,index=j) for j in range(6)]
 p += [f'CASE {i} {int(periodic)} {6 if periodic else 0} 0 0']
 c=['FREQ 00000000000003e8',row('ALLOC_BEFORE',i,base-20,ws=4*1024**2),
    row('READY',i,base-10),row('WORK_START',i,base+10),row('WORK_END',i,base+duration+10,cpu),
    f'RESULT {i} {0 if i<2 else 1073741824} {1 if i<2 else checksum}','PASS']
 children.append('\n'.join(c)+'\n')
 host['rows'] += [dict(case=i,kind=kind,tick=ms,monotonic_ns=ms*1000000) for kind,ms in [('START',base+10),('END',base+duration+10)]]
p+=['CONTROL_PASS','RESTART'];parent='\n'.join(p)+'\n'
assert validate(parent,children,host)['passed']
bad={}
for name,edit in [
 ('missing_marker',lambda h:h['rows'].pop()),
 ('wrong_case',lambda h:h['rows'][0].update(case=1)),
 ('wrong_tick',lambda h:h['rows'][0].update(tick=99)),
 ('host_elapsed_mismatch',lambda h:h['rows'][1].update(monotonic_ns=h['rows'][0]['monotonic_ns']+1000000)),
 ('host_reversed',lambda h:h['rows'][1].update(monotonic_ns=1)),
 ('reader_error',lambda h:h.update(error='transport error')),
 ('not_connected',lambda h:h.update(connected=False)),
 ('reader_open',lambda h:h.update(closed=False))]:
 h=copy.deepcopy(host);edit(h);bad[name]=(parent,children,h)
c=copy.copy(children);c[2]=c[2].replace(f'1073741824 {checksum}','1073741824 0');bad['checksum']=(parent,c,host)
c=copy.copy(children);c[2]=c[2].replace(f'{15010000:016x}',f'{10000:016x}');bad['short_busy_cpu']=(parent,c,host)
c=copy.copy(children);c[0]=c[0].replace(str(12*1024**2),str(4*1024**2));bad['no_memory_growth']=(parent,c,host)
bad['missing_sample']=(parent.replace('CASE 3 1 6 0 0','CASE 3 1 5 0 0'),children,host)
rejected=[]
for name,args in bad.items():
 try:validate(*args)
 except (AssertionError,ValueError,KeyError):rejected.append(name)
 else:raise AssertionError('accepted '+name)
framing=Lines();framing.feed(b'MARK STA',100);framing.feed(b'RT 0 10\r',200);assert not framing.rows
framing.feed(b'\nMARK END 0 5010\r\n',300);framing.finish()
assert len(framing.rows)==2 and all(r['monotonic_ns']==300 for r in framing.rows)
framing_rejected=[]
for name,data,finish in [('malformed',b'bad\n',False),('bad_case',b'MARK START 9 0\n',False),('overflow',b'x'*4096,False),('partial',b'MARK START 0',True)]:
 f=Lines()
 try:
  f.feed(data,1)
  if finish:f.finish()
 except (AssertionError,ValueError):framing_rejected.append(name)
 else:raise AssertionError(name)
out.write_text(json.dumps(dict(passed=True,rejected=rejected,framing_rejected=framing_rejected,checksum=checksum,
 sources={n:hashlib.sha256((K/n).read_bytes()).hexdigest() for n in ['cost_oracle.py','serial_host.py']},
 scope='Host parser/framing checks only; no timing result.'),indent=2)+'\n')
print('614 host tests passed:',len(rejected),len(framing_rejected))
