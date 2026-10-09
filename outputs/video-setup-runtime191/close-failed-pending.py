"""Supplement incomplete frozen audit; preserve missing workload, never repeat a launch."""
from common import *
case='pending001';out=k/case;dest=out/'failed-audit.json';assert not dest.exists() and not (out/'audit.json').exists()
f=read(k/('fixture-'+case+'.json'));run=ws/('work/runs/nt5-preflight191-'+case);assert (run/'cleanup.json').exists()
for name,digest in read(k/'frozen-inputs.json').items():assert sha(ws/name)==digest
for row in f['parents']:assert sha(Path(row['path']))==row['sha256']
r=dict(physical_access=False,debugger=False,workload_passed=False,diagnostic_usable=False,ordinary_qualified=False,
 failure='Frozen audit rejected absent/malformed ATTEMPT_ONCE/WAITING_FOR_SETUP_IDLE; no attempt.log was present',files=[],hives=[],new_events={})
with ColdIO(run/'hdd.qcow2') as io:
 rr=readers(io,run/'hdd.qcow2')
 for name,digest in f['protected'].items():
  volume,path=name.split('/',1);actual=m.sha(rr[volume].read(path));r['files'].append(dict(path=name,before_sha256=digest,after_sha256=actual,matched=actual==digest))
 r['startup_unchanged']=m.sha(rr['F'].read(STARTUP))==f['files']['F/'+STARTUP]
 for name in ['attempt.log']+['sample%d/gdi-baseline.txt'%i for i in range(5)]:
  try:rr['F'].read('xwnpre191/'+name)
  except KeyError:pass
  else:raise AssertionError('Expected actual absent workload log')
r['all_workload_logs_absent']=True
for name in HIVES:r['hives'].append(dict(name=name,**hive(out/'artifacts'/('after-'+name))))
for label in ['system','application']:
 a=read(out/('before-'+label+'-events.json'))['records'];b=read(out/('after-'+label+'-events.json'))['records'];boundary=max((v['record'] for v in a),default=0)
 r['new_events'][label]=[v for v in b if v['record']>boundary]
r['setupapi_unchanged']=(out/'artifacts/before-setupapi.log').read_bytes()==(out/'artifacts/after-setupapi.log').read_bytes()
r['video_trace_unchanged']=False
with ColdIO(ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name']) as io:
 rr=readers(io,ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name']);r['video_trace_unchanged']=rr['F'].read('winnt/system32/xwn-video-trace.bin')==(out/'artifacts/after-video-trace.bin').read_bytes()
scan(run/'hdd.qcow2',out/'artifacts');a=read(out/'allocation.json');r['allocation_passed']=a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
r['integrity_passed']=r['allocation_passed'] and all(v['matched'] for v in r['files']) and all(v['parsed'] for v in r['hives']) and r['startup_unchanged']
r['limits']='No helper runtime evidence. Unchanged event/SetupAPI/video records do not identify the stopped boot stage. No screen was captured. Host stop is not normal guest shutdown. Supplement completes only the incomplete integrity audit, never replays failed workload.'
save(dest,r);save(out/'closure.json',dict(closed=True,never_relaunch_or_recollect=True,workload_passed=False,diagnostic_usable=False,ordinary_qualified=False,physical_access=False,failed_audit_sha256=sha(dest),cleanup_sha256=sha(run/'cleanup.json'),hdd_sha256=sha(run/'hdd.qcow2')))
print(json.dumps({v:r[v] for v in ['workload_passed','integrity_passed','all_workload_logs_absent','setupapi_unchanged','video_trace_unchanged','new_events']},indent=2))
