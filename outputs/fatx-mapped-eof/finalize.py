"""Summarize both ordinary attempts without suppressing control failures."""
import array,hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sha=lambda data:hashlib.sha256(data).hexdigest()
def reserved(case):
    meta=(k/case/'artifacts/fat-metadata.bin').read_bytes();fat=array.array('I');fat.frombytes(meta[4096:])
    if sys.byteorder!='little':fat.byteswap()
    ids=array.array('I',(i for i,v in enumerate(fat) if v==0xfffffff7))
    if sys.byteorder!='little':ids.byteswap()
    return dict(count=len(ids),positions_sha256=sha(ids.tobytes()))
base=json.loads((k/'before/allocation.json').read_text());assert base['allocation_consistent']
reservations=reserved('before');cases=[]
for case in ['old','fixed']:
    a=json.loads((k/case/'audit.json').read_text());alloc=json.loads((k/case/'allocation.json').read_text())
    cleanup=json.loads((ws/('work/runs/nt5-fatx-mapped-eof-'+case+'/cleanup.json')).read_text())
    fixture=json.loads((k/('fixture-'+case+'.json')).read_text())
    r=dict(case=case,driver_sha256=fixture['fatx_sha256'],probe_completed=a['probe_completed'],mapping_checks=a['mapping_checks'],
           mapping_failures=len(a['mapping_failures']),input_tail_failures=sum(v['kind']=='INPUT' for v in a['mapping_failures']),
           content_mismatches=sum(v['content_mismatches'] for v in a['mapping_failures']),persistence_passed=a['persistence_passed'],
           allocation_consistent=alloc['allocation_consistent'],reserved_marks=reserved(case),
           reservations_unchanged=reserved(case)==reservations,normal_shutdowns=a['normal_shutdown_count'],
           popup_records=a['popup_records'],unexpected_errors=a['unexpected_errors'],
           ordinary_run_valid=a['ordinary_run_valid'],mapped_checks_passed=a['mapped_checks_passed'],cleanup=cleanup)
    r['all_fixed_gates_passed']=case=='fixed' and a['mapped_eof_passed'] and r['allocation_consistent'] and r['reservations_unchanged']
    cases.append(r)
r=dict(scope=__doc__,physical_access=False,driver_change_this_turn=False,candidate='0098',
       cases=cases,negative_control_detected=cases[0]['probe_completed'] and cases[0]['mapping_failures']>0 and cases[0]['content_mismatches']==0,
       fixed_mapping_regression_passed=cases[1]['mapped_checks_passed'],fixed_strict_passed=cases[1]['all_fixed_gates_passed'],
       hardware_qualified=False,physical_baseline='video0093/FATX0088; release0.1.0 unchanged',
       limits='Bounded serial mapping/replacement workload in synthetic-resource xemu; no concurrent mapped truncation, mapped writes, long soak, arbitrary PnP lifetime or physical video performance qualification.')
(k/'summary.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
