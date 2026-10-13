"""Read-only failure localization, not a replacement or weakened qualifier."""
import hashlib,json,statistics,sys
from pathlib import Path
K=Path(__file__).resolve().parent;dest=K/'coverage-diagnosis001.json';assert not dest.exists()
sys.path.insert(0,str(K.parent/'hd-phase344'));from phase_analysis import analyze as legacy
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r={'qualified':False,'hardware_promotion':False,'cases':{},'limits':'Clock projection below is diagnostic only. The348 full-requested-fast-byte gate remains FAILED for candidate. Mixed engine/fast calls do not identify their rectangles, clipping or reason; do not infer a cursor/window cause.'}
for case in ['control001','candidate001']:
    out=K/case;a=json.loads((out/'audit.json').read_text());samples=[]
    for i in range(5):
        p=out/f'artifacts/sample{i}/gdi-baseline.txt';text=p.read_text();lines=[v.split() for v in text.splitlines()]
        projected='\n'.join(' '.join(v) for v in lines if not v[0].startswith('PRIMARY348_'))
        phase=legacy(projected,1);assert phase['passed']
        rows=[]
        for id in [2,3,7,8,12,13]:
            pairs=[]
            for side in ['BEFORE','AFTER']:
                values=[v for v in lines if v[:2]==['PRIMARY348_'+side,str(id)]]
                assert len(values)==32 and [int(v[2]) for v in values]==list(range(32))
                pairs.append([int(v[3]) for v in values])
            b,e=pairs;calls=[e[n]-b[n] for n in range(4,9)];actual=(e[9]+(e[10]<<32))-(b[9]+(b[10]<<32))
            v=phase['intervals'][id];requested=v['operations']*v['size'][0]*v['size'][1]*4
            rows.append(dict(id=id,operations=v['operations'],attempts=calls[0],eligible=calls[1],fast=calls[2],empty=calls[3],fallback=calls[4],fast_bytes=actual,full_requested_bytes=requested,fast_byte_deficit=requested-actual,deficit_per_operation=(requested-actual)/v['operations'],fast_calls_per_operation=calls[2]/v['operations'],fallback_calls_per_operation=calls[4]/v['operations'],wall_ms_per_operation=v['wall_ms']/v['operations'],selected_body_ms_per_operation=v['elapsed_ms'][1]/v['operations'],upload_body_ms_per_operation=v['elapsed_ms'][2]/v['operations']))
        samples.append(dict(index=i,log_sha256=sha(p),intervals=rows))
    r['cases'][case]=dict(samples=samples,legacy_pixel_checks_passed=all(v['probe_passed'] and v['copy_checks_passed'] for v in a['samples']),other_copy_text_window_checks_passed=all(v['passed'] for group in ['dib_samples','phase_samples','window_samples','text_samples'] for v in a[group]),integrity_passed=a['integrity_passed'],normal_shutdown_count=a['normal_shutdown_count'],orderly_host_exit=a['orderly_host_exit'])
c=r['cases']['candidate001']['samples'];large=[v for s in c for v in s['intervals'] if v['id'] in [12,13]]
assert all(v['fast_calls_per_operation']==8 and v['fallback_calls_per_operation']==5 and v['deficit_per_operation']==6036 for v in large)
assert all(v['fast_byte_deficit']==0 and v['fallback']==0 for s in c for v in s['intervals'] if v['id']<12)
r['observed_failure']=dict(affected_intervals=10,deficit_per_operation_bytes=6036,expected_bytes_per_operation=2073600,fast_bytes_per_operation=2067564,fast_calls_per_operation=8,fallback_calls_per_operation=5,unexplained_pixels_equivalent=1509)
r['emulator_diagnostic_medians']={case:{str(id):{name:statistics.median(v[name] for s in data['samples'] for v in s['intervals'] if v['id']==id) for name in ['wall_ms_per_operation','selected_body_ms_per_operation','upload_body_ms_per_operation']} for id in [12,13]} for case,data in r['cases'].items()}
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['observed_failure']));print(json.dumps(r['emulator_diagnostic_medians']))
