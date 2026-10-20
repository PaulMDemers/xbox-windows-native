"""Review one cold export; all instruction fractions remain location observations."""
import hashlib,json,re
from pathlib import Path
from sample_oracle import validate_case
K=Path(__file__).resolve().parent;P=Path('C:/xwn622/pc001/cold1-002')
out=K/'review001.json';assert not out.exists();r=dict(passed=False,physical_access=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
def lcg(count):
 # Independent affine exponentiation modulo2^32 for original assembly work.
 a,c,x=1664525,1013904223,1
 while count:
  if count&1:x=(a*x+c)&0xffffffff
  c=c*(a+1)&0xffffffff;a=a*a&0xffffffff;count>>=1
 return x
try:
 state=read('ntfs-phase1.json');cold=read('ntfs-cold1-002.json');build=read('build001.json')
 assert state['closed'] and state['exit_code']==0 and cold['complete']
 assert not any(state.get(n) for n in ['host_quit','host_terminate','host_kill','deadline','space_stop'])
 assert cold['audit_unchanged'] and cold['source_unchanged'] and cold['normal_shutdown_delta']==1
 assert all(h['clean'] and h['header_valid'] and h['independent_raw_values_agree'] for h in cold['hives'])
 manifest=json.loads((P/'manifest.json').read_text());logs=P/'files/xwn622'
 for row in build['rows']:assert manifest['xwn622-kit/'+Path(row['path']).name]['sha256']==row['sha256']
 log=(logs/'sampler.txt').read_text();subjects=[(logs/f'subject{i}.txt').read_text() for i in range(8)]
 host=json.loads(Path('C:/xwn622/pc001/phase1/serial-host.json').read_text())
 (K/'serial-host001.json').write_text(json.dumps(host,indent=2)+'\n')
 (K/'raw-control-logs001.json').write_text(json.dumps(dict(sampler=log,subjects=subjects),indent=2)+'\n')
 assert log.count('CONTROL_PASS')==1 and log.count('RESTART')==1
 assert not any(x in log for x in ['CONTROL_FAIL','OWNED_TERMINATE','SUSPEND_FAIL'])
 rows={};mods={i:[] for i in range(8)};samples={i:[] for i in range(8)}
 for line in log.splitlines():
  v=line.split();tag=v[0]
  if tag=='FREQ':assert len(v)==2;continue
  if tag in ['CONTROL_PASS','RESTART']:continue
  i=int(v[1]);assert i in range(8)
  if tag=='MODULE':mods[i].append([int(v[2],16),int(v[3],16),' '.join(v[4:])]);continue
  if tag=='SAMPLE':
   assert len(v)==11
   samples[i].append([int(v[2]),int(v[3]),*[int(x,16) for x in v[4:8]],*[int(x) for x in v[8:]]]);continue
  assert (tag,i) not in rows;rows[tag,i]=v[2:]
 # SerialRecorder preserves monotonic host markers independently of guest clock.
 hrows=host['rows'] if 'rows' in host else host['lines']
 assert host['closed'] and not host.get('error') and len(hrows)==18
 assert [(v['kind'],v['case']) for v in hrows]==[(kind,case) for case in range(9) for kind in ['START','END']]
 sa=rows['SLEEP_START',0];sb=rows['SLEEP_END',0]
 sleep=(int(sb[2])-int(sa[2]))/1000
 sleep_host=(hrows[1]['monotonic_ns']-hrows[0]['monotonic_ns'])/1e9
 assert 4.9<=sleep<=5.2 and abs(sleep-sleep_host)<.25
 r['sleep']=dict(ticks_seconds=sleep,host_seconds=sleep_host)
 r['host_shape']=list(host)
 cases={};r['cases']=cases
 for i in range(8):
  a=rows['SUBJECT_START',i];b=rows['SUBJECT_END',i];oa=rows['OBSERVER_START',i];ob=rows['OBSERVER_END',i]
  assert len(a)==len(b)==len(oa)==len(ob)==8
  ticks=[int(a[2]),int(b[2])]
  cpu=lambda x,y:sum(int(y[j],16)-int(x[j],16) for j in [3,4])/1e7
  ta=rows['THREAD_START',i];tb=rows['THREAD_END',i];tr=rows['THREAD_READY',i]
  assert len(ta)==len(tb)==3 and ta[0]==tb[0]==tr[0]
  thread=sum(int(tb[j],16)-int(ta[j],16) for j in [1,2])/1e7
  ident=rows['IDENTITY',i];assert len(ident)==4
  identity=[*[int(v) for v in ident[:3]],int(ident[3],16)]
  case=rows['CASE',i];assert len(case)==2 and int(case[1])==0
  ss=subjects[i].splitlines();assert len(ss)==1
  v=ss[0].split();assert len(v)==22 and v[0]=='TIMER' and int(v[1])==i
  assert v[2::2]==['MODE','PID','TID','CALLS','FIRST','LAST','CHANGES','START','END','PASS']
  mode,pid,tid,loops,first,last,changes,subject_start,subject_end,passed=map(int,v[3::2]);assert mode==i%4 and [pid,tid]==identity[:2] and passed==1
  start=[x for x in hrows if x['line'].split()[:3]==['MARK','START',str(i+1)]]
  end=[x for x in hrows if x['line'].split()[:3]==['MARK','END',str(i+1)]]
  assert len(start)==len(end)==1
  for x,t in zip([start[0],end[0]],ticks):assert int(x['line'].split()[3])==t
  elapsed=(end[0]['monotonic_ns']-start[0]['monotonic_ns'])/1e9
  c=dict(identity=identity,ticks=ticks,host_seconds=elapsed,cpu=cpu(a,b),thread_cpu=thread,observer_cpu=cpu(oa,ob),modules=mods[i],changes=changes,timer_values=[first,last],subject_ticks=[subject_start,subject_end],mode=mode,loops=loops,subject_pass=True,exit_code=0,observed=i>=4,samples=samples[i])
  if i>=4:assert len(samples[i])==int(case[0])==int(b[0])
  cases[str(i)]=validate_case(c);cases[str(i)]['mode']=mode;cases[str(i)]['loops']=loops
 r.update(passed=True,cases=cases,normal_shutdown_delta=1,exact_tools=True,cleanup_passed=True)
except BaseException as e:r['error']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
