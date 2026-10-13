"""New interpretation of unchanged359 evidence, never replace its original audit."""
import collections,hashlib,json,struct
from pathlib import Path
from paired_decode import paired
K=Path(__file__).resolve().parent;W=K.parents[1];P=K.parent/'memory-physical359'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=K/'analysis001.json';assert not dest.exists() and read(K/'tests002.json')['passed']
assert read(P/'final-review.json')['closed']
a=read(P/'candidate001/audit.json');assert not a['memory_state_passed'] and not a['strict_qualification_passed']
c=read(P/'candidate001/collection.json');assert c['completed'] and c['startup_restored'] and c['driver_restored']
root=P/'artifacts/candidate001';rows=[]
for i in range(5):
 for phase in ['before','after']:
  remote='/E/xwnmemory359candidate001/sample%d/memory-%s.bin'%(i,phase)
  warm=root/remote.lstrip('/');cold=warm.with_name(warm.name+'.cold')
  for p,n in [(warm,remote),(cold,remote+'.cold')]:assert sha(p)==c['files'][n]['sha256']
  r=paired(cold.read_bytes(),warm.read_bytes());translations=r.pop('rows')
  scan=[v for v in translations if v['role']==1];shadow=[v for v in translations if v['role']==0]
  assert len(scan)==2025 and all(v['physical']==0x3700000+4096*j for j,v in enumerate(scan))
  assert r['bytes']==8294400 and all(v['physical']<0x3700000 for v in shadow)
  w=struct.unpack('<16640I',warm.read_bytes());cpu=w[16:96]
  rows.append(dict(sample=i,phase=phase,warm_sha256=sha(warm),cold_sha256=sha(cold),
       complete_translation_rows=len(translations),translation_summary_sha256=hashlib.sha256(json.dumps(translations,sort_keys=True).encode()).hexdigest(),
       register_words=list(cpu),fixed_enabled=bool(cpu[16]&0x400),mtrr_enabled=bool(cpu[16]&0x800),
       pat_indices={role:dict(collections.Counter(v['pat_index'] for v in group)) for role,group in [('shadow',shadow),('scanout',scan)]},**r))
r=dict(new_memory_interpretation_passed=all(v['passed'] for v in rows),observations=rows,
       original_audit_sha256=sha(P/'candidate001/audit.json'),original_final_review_sha256=sha(P/'final-review.json'),
       original359_memory_qualification=False,original359_combined_qualification=False,original359_strict_qualification=False,
       untouched_original_audit=True,no_new_guest_launch=True,no_hardware_writes=True,
       display_workload_passed=a['display_workload_passed'],integrity_passed=a['integrity_passed'],
       normal_shutdown_count=a['normal_shutdown_count'],warnings_errors=a['warnings_errors'],
       physical_performance_qualified=False,release_qualified=False,
       scope='Actual unchanged physical359 packets, corrected FE selection only. Current page/register samples, not exhaustive aliases/TLB/atomic residency/throughput cause; all original failures retained.')
dest.write_text(json.dumps(r,indent=2)+'\n')
print('Physical sampled policy:',rows[0]['counts'],'all pairs',len(rows),'cold complete',sum(v['cold_residency']['complete'] for v in rows))
