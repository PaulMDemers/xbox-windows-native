"""Compare successful backend write snapshots with exact final allocated bytes."""
import hashlib,importlib.util,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['emu001','emu002']
run=k.parents[1]/('work/runs/nt5setup-'+case);out=k/case
spec=importlib.util.spec_from_file_location('transfer_parser',k/'parse-transfer.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
records=p.records(run/'transfer.backend.bin');submitted={};writes=[]
for r in records:
    if r['phase']==4:submitted[r['id']]=r
    else:
        begin=submitted.pop(r['id']);writes.append((begin,r))
cold=json.loads((out/'cold-ranges.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
result=dict(physical_access=False,targets={},uncompleted_backend_ids=list(submitted))
for path,target in cold['targets'].items():
    compared=0;equal=0;old=0;written=set();matched=set();mismatches=[];overlap=[];no_write=0
    for span in target['ranges']:
        base=span['offset'];n=span['bytes'];cluster=cold['clusters'][str(base)];art=out/'artifacts/cold-clusters'
        before=(art/(str(base)+'-before.bin')).read_bytes();after=(art/(str(base)+'-after.bin')).read_bytes()
        assert sha(before)==cluster['before_sha256'] and sha(after)==cluster['after_sha256']
        candidates=[(a,b) for a,b in writes if a['offset']<base+n and a['offset']+a['bytes']>base]
        for sector in range(0,n,512):
            lo=base+sector;length=min(512,n-sector);hi=lo+length
            relevant=[(a,b) for a,b in candidates if a['offset']<hi and a['offset']+a['bytes']>lo]
            final=bytearray(before[sector:sector+length]);covered=bytearray(length);used=[]
            for a,b in sorted(relevant,key=lambda pair:pair[1]['monotonic_us']):
                matched.add(a['id'])
                if b['status']!=0 or a['payload_bytes']!=a['bytes'] or a['flags']>>62:continue
                start=max(lo,a['offset']);end=min(hi,a['offset']+a['bytes']);i=start-lo;j=end-lo
                final[i:j]=a['data'][start-a['offset']:end-a['offset']];covered[i:j]=b'\1'*(j-i);used.append(a['id']);written.add(a['id'])
            for i,(a,b) in enumerate(relevant):
                for c,d in relevant[i+1:]:
                    if max(a['monotonic_us'],c['monotonic_us'])<min(b['monotonic_us'],d['monotonic_us']):overlap.append(dict(offset=lo,ids=[a['id'],c['id']]))
            count=sum(covered);compared+=count
            actual=after[sector:sector+length];prior=before[sector:sector+length]
            equal+=sum(bool(covered[i]) and final[i]==actual[i] for i in range(length))
            old+=sum(bool(covered[i]) and final[i]==prior[i] for i in range(length))
            no_write+=length-count
            if any(covered[i] and final[i]!=actual[i] for i in range(length)):
                mismatches.append(dict(offset=lo,bytes=length,successful_write_ids=used,submitted_composite_sha256=sha(final),cold_sha256=sha(actual),before_sha256=sha(prior)))
    result['targets'][path]=dict(bytes=target['bytes'],overlapping_backend_requests=len(matched),successful_write_requests=len(written),
        compared_written_bytes=compared,submitted_bytes_equal_cold=equal,submitted_bytes_equal_before=old,
        bytes_without_observed_successful_write=no_write,mismatching_sectors=mismatches,overlapping_inflight_requests=overlap)
result['limits']='Last successful submission snapshots applied in completion order. Overlapping in-flight ranges make ordering ambiguous and are reported. Endpoint buffer captures do not exclude transient changes between snapshots. Equality only covers observed successful writes, not untouched bytes, flush durability, or ordinary restart.'
(out/'transfer-cold-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
