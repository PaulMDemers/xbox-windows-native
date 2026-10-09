"""Describe completed ordinary elapsed diagnostic; never waive strict failures."""
import hashlib,json,statistics
from pathlib import Path
k=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();dest=k/'pair-analysis.json';assert not dest.exists()
r=dict(physical_access=False,debugger=False,physical_qualified=False,performance_qualified=False,cases={},medians=[])
for case,mode in [('control001',0),('candidate001',1)]:
 out=k/case;a=read(out/'audit.json');c=read(out/'closure.json')
 assert c['closed'] and a['workload_passed'] and a['integrity_passed'] and a['profile_contract_passed']
 assert len(a['samples'])==len(a['profiles'])==5 and all(v['passed'] and v['mode']==mode for v in a['profiles'])
 freqs={v['frequency'] for v in a['profiles']};assert len(freqs)==1
 samples=[]
 for sample,p in zip(a['samples'],a['profiles']):
  for t,v in zip(sample['timed_loops'],p['intervals']):
   assert t[1]==v['kind'];count,ms=t[2:];assert count>0 and ms>0
   samples.append(dict(kind=v['kind'],operations=count,ms=ms,operations_per_second=count*1000/ms,
     body_calls=v['body_calls'],body_ms=v['elapsed_ms'],body_ms_per_operation=[n/count for n in v['elapsed_ms']],
     counter_interval=sample['intervals'][v['kind']]))
 r['cases'][case]=dict(workload_passed=True,integrity_passed=True,strict_qualified=a['strict_qualification_passed'],frequency=next(iter(freqs)),
   calibration_ranges=[dict(minimum=v['overhead_min_ticks'],maximum=v['overhead_max_ticks']) for v in a['profiles']],
   samples=samples,popups=[v for v in a['new_events']['system'] if v['source']=='Application Popup'],warnings_errors=a['warnings_errors'],
   pins={n:sha(out/n) for n in ['audit.json','closure.json','launch.json']})
assert r['cases']['control001']['frequency']==r['cases']['candidate001']['frequency']
for kind,label in enumerate(['fill','upload','readback','overlap_right_down','overlap_left_up']):
 control=[v for v in r['cases']['control001']['samples'] if v['kind']==kind];candidate=[v for v in r['cases']['candidate001']['samples'] if v['kind']==kind]
 old=statistics.median(v['operations_per_second'] for v in control);new=statistics.median(v['operations_per_second'] for v in candidate)
 r['medians'].append(dict(kind=kind,label=label,control_ops_per_second=old,candidate_ops_per_second=new,candidate_over_control=new/old,
   candidate_body_ms_per_operation=[statistics.median(v['body_ms_per_operation'][i] for v in candidate) for i in range(4)],
   body_labels=['EngBitBlt','EngCopyBits','upload_copy_body','complete_upload_wrapper']))
r['functional_timer_contract_passed']=True;r['strict_qualification_passed']=all(v['strict_qualified'] for v in r['cases'].values())
r['limits']='Elapsed device-global totals include background and preemption; nested upload bookkeeping is included in wrapper. Control retains call-count bookkeeping; ON adds clock queries AND enabled tick/read accounting. Ratio measures the enabled-profile increment, not clock queries alone or all bookkeeping versus untouched112. Calibration covers direct DDI queries, not whole profiler wrappers. No physical extrapolation, optimization or release qualification. All popup/warning/error evidence retained.'
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['medians'],indent=2))
