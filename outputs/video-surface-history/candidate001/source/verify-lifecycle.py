"""Independently parse sparse lifecycle intervals and correlate retained surfaces."""
import hashlib,json,re
from pathlib import Path
from lifecycle import EVENTS,parse,MAX_BYTES,MAX_EVENTS
from surface_trace import decode
k=Path(__file__).resolve().parent;out=k/'candidate001';ws=k.parents[1]
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def summarize(events,boundaries,windows,samples,window_data):
 assert boundaries['before']<=boundaries['after']<=boundaries['first_marker']
 bases=sorted({base for w in windows for kind,base,offset in decode(window_data(w))})
 result=[]
 for base in bases:
  hits=[w for w in windows if any(b==base for _,b,_ in decode(window_data(w)))]
  first=min(w['start_offset'] for w in hits);last=max(w['end_offset'] for w in hits)
  creates=[e for e in events if e['kind']=='create' and e['base']==base and e['end_offset']<=first]
  assert creates,'No recorded creation for accessed surface'
  creation=creates[-1]
  intervening=[e for e in events if e['base']==base and creation['end_offset']<=e['offset']<last and e['kind'] in ['create','invalidated']]
  assert not intervening,'Creation/replacement/invalidation inside observed lifetime'
  transfers=[e for e in events if e['base']==base and creation['end_offset']<=e['offset']<last and e['kind'] in ['upload','download']]
  initial=[e for e in transfers if e['end_offset']<=first]
  bpps={e['bytes_per_pixel'] for e in initial if all(e[f]==creation[f] for f in ['width','height','pitch','normalized_layout'])}
  assert len(bpps)==1,'Exact extent requires matching recorded transfer geometry/BPP'
  bpp=bpps.pop();size=creation['height']*max(creation['pitch'],creation['width']*bpp)
  assert 0<size<=64*1024*1024 and base+size<=64*1024*1024
  per_sample=[]
  for sample in samples:
   ev=[(kind,b,o) for w in windows if w['sample']==sample['sample'] for kind,b,o in decode(window_data(w)) if b==base]
   expected=set()
   for row in sample['destination']['rows']:
    low,high=[p['physical'] for p in row['points']]
    for addr in range(low,high+1,4):
     if base<=addr<base+size:expected.add(addr)
   observed=[b+o for kind,b,o in ev if kind=='write']
   assert len(observed)==len(set(observed)) and set(observed)==expected,'Dense write addresses do not match recorded extent'
   per_sample.append(dict(sample=sample['sample'],expected_overlapping_writes=len(expected),observed_writes=len(observed),exact=True))
  result.append(dict(base=base,creation=creation,created_before_launch_request=creation['end_offset']<=boundaries['before'],inferred_extent_bytes=size,inferred_end_exclusive=base+size,bytes_per_pixel=bpp,
    no_invalidation_or_replacement_through_last_callback=True,transfers=transfers,
    transfers_during_upload_windows=[e for e in transfers if any(w['start_offset']<=e['offset']<w['end_offset'] for w in windows)],
    per_sample=per_sample))
 return result

if __name__=='__main__':
 dest=k/'lifecycle-verification.json';assert not dest.exists()
 r=read(out/'trace.json');life=r['lifecycle'];data=(out/'artifacts/lifecycle.log').read_bytes()
 assert len(data)==life['bytes']<=MAX_BYTES and hashlib.sha256(data).hexdigest()==life['sha256']
 events=parse(data);assert events==life['events_observed'] and len(events)==life['event_count']<=MAX_EVENTS
 assert life['events_disabled'] and not r.get('lifecycle_teardown_error') and r['guest_resumed'] and not r['armed_breakpoints_remaining']
 assert [s['expected'] for s in life['states']]==[True,False]
 for state in life['states']:
  assert not state['errors'] and [x['event'] for x in state['records']]==list(EVENTS)
  for row in state['records']:assert re.search(re.escape(row['event'])+r' : state '+str(int(state['expected']))+r'\b',row['response'])
 marks=life['markers'];assert len(marks)==7 and marks[0]['name']=='before_launch_armed'
 assert [(v['sample'],v['phase']) for v in marks[1:]]==[(s,p) for s in range(3) for p in range(2)]
 assert [v['offset'] for v in marks]==sorted(v['offset'] for v in marks)
 launch=read(out/'launch.json')['cycles'];assert len(launch)==1 and launch[0]['dashboard_return'];launch=launch[0]
 bounds=dict(before=launch['trace_before_launch_offset'],after=launch['trace_after_launch_reply_offset'],first_marker=marks[1]['offset'])
 assert marks[0]['offset']<=bounds['before'] and marks[-1]['offset']<=len(data)
 windows=r['surface']['windows'];summaries=summarize(events,bounds,windows,r['samples'],lambda w:(out/'artifacts/surface-windows'/w['artifact']).read_bytes())
 original=ws/'work/runs/nt5-vlife-candidate001/cpu-trace.log'
 with original.open('rb') as f:assert f.read(len(data))==data
 assert read(k/'surface-verification.json')['passed'] and read(k/'trace-verification.json')['passed'] and read(out/'verification.json')['passed']
 result=dict(passed=True,ordinary_qualified=False,timing_qualified=False,physical_qualified=False,boundaries=bounds,lifecycle_events=len(events),log_bytes=len(data),surfaces=summaries,
   pins={str(p):sha(p) for p in [Path(__file__),k/'lifecycle.py',k/'backend.json',out/'trace.json',out/'launch.json',k/'surface-verification.json',original]},
   limits='Recorded creation/lifetime and transfer calls only; not lock/wait durations, GPU reset semantics, an optimization or physical speed qualification.')
 dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,lifecycle_events=len(events),surfaces=summaries),indent=2))
