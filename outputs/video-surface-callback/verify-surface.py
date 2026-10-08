"""Independently correlate exact logged callback addresses with live row mappings."""
import collections,hashlib,json
from pathlib import Path
from surface_trace import decode,MAX_SEGMENT,MAX_TOTAL,MAX_RECORDS
k=Path(__file__).resolve().parent;out=k/'candidate001';ws=k.parents[1]
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def correlate(events,sample):
 counts=collections.Counter();bases=collections.Counter();addresses=collections.defaultdict(set);rows=collections.defaultdict(set)
 ranges={side:[(r['points'][0]['physical'],r['points'][1]['physical'],i) for i,r in enumerate(sample[side]['rows'])] for side in ['source','destination']}
 for kind,base,offset in events:
  physical=base+offset;hits=[];bases[(kind,base)]+=1
  for side,rr in ranges.items():
   for low,high,index in rr:
    if low<=physical<=high:hits.append(side);rows[(kind,side)].add(index)
  assert len(hits)<=1,'Overlapping captured source/destination rows'
  side=hits[0] if hits else 'other';counts[(kind,side)]+=1;addresses[(kind,side)].add(physical)
 return dict(events=len(events),addresses=[dict(kind=a,side=b,records=n,unique_addresses=len(addresses[(a,b)]),rows=sorted(rows[(a,b)]),min_address=min(addresses[(a,b)]),max_address=max(addresses[(a,b)])) for (a,b),n in sorted(counts.items())],surfaces=[dict(kind=a,base=b,records=n) for (a,b),n in sorted(bases.items())])

def validate(r,loader):
 s=r['surface'];assert s['prelaunch_state_verified'] and s['events_disabled']
 assert not r.get('surface_teardown_error') and r['guest_resumed'] and not r['armed_breakpoints_remaining']
 assert len(s['windows'])==15 and s['total_bytes']<=MAX_TOTAL and s['total_records']<=MAX_RECORDS
 totals=[[],[],[]];bytes_total=0;last=None
 for i,w in enumerate(s['windows']):
  assert w['sample']==i//5 and w['after_stop']==['upload_entry','copy_call','rep_movsd','after_rep','copy_return'][i%5]
  assert w['artifact']=='%02d.log'%i and w['bytes']==w['end_offset']-w['start_offset']<=MAX_SEGMENT
  assert 0<=w['duration_seconds']<=30
  if last is not None:assert last<=w['start_offset']
  last=w['end_offset'];data=loader(w);assert len(data)==w['bytes'] and hashlib.sha256(data).hexdigest()==w['sha256']
  ev=decode(data);assert len(ev)==w['records'];totals[w['sample']].extend(ev);bytes_total+=len(data)
 assert bytes_total==s['total_bytes'] and sum(map(len,totals))==s['total_records']
 expected=[False,True,False]+[v for _ in range(15) for v in (True,False)]+[False]
 assert [v['enabled'] for v in s['state_checks']]==expected
 return [dict(sample=i,rect=r['samples'][i]['rect'],**correlate(ev,r['samples'][i])) for i,ev in enumerate(totals)]

if __name__=='__main__':
 dest=k/'surface-verification.json';assert not dest.exists()
 r=read(out/'trace.json');rows=validate(r,lambda w:(out/'artifacts/surface-windows'/w['artifact']).read_bytes())
 log=ws/'work/runs/nt5-vsurface-candidate001/cpu-trace.log'
 with log.open('rb') as f:
  for w in r['surface']['windows']:
   f.seek(w['start_offset']);assert hashlib.sha256(f.read(w['bytes'])).hexdigest()==w['sha256']
 assert read(k/'trace-verification.json')['passed'] and read(out/'verification.json')['passed']
 result=dict(passed=True,ordinary_qualified=False,timing_qualified=False,physical_qualified=False,samples=rows,total_records=r['surface']['total_records'],total_bytes=r['surface']['total_bytes'],trace_events_disabled=True,
  pins={str(p):sha(p) for p in [Path(__file__),k/'surface_trace.py',k/'backend.json',k/'trace-verification.json',out/'trace.json',log]},
  limits='Selected upload windows only. Events prove callback overlap, not time spent, draw_dirty downloads, exclusive causality or physical-console behavior.')
 dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(rows,indent=2))
