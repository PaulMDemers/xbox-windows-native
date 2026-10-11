"""Retain every changed in-flight buffer and its cold target association."""
import bisect,hashlib,importlib.util,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['emu001','emu002']
out=k/case;run=k.parents[1]/('work/runs/nt5storxfer-'+case)
spec=importlib.util.spec_from_file_location('p',k/'parse-transfer.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
d=m.records(run/'transfer.dma.bin');b=m.records(run/'transfer.backend.bin')
analysis=m.analyze(d,b);cold=json.loads((out/'cold-ranges.json').read_text())
starts=sorted(map(int,cold['clusters']));sha=lambda v:hashlib.sha256(v).hexdigest()
def read(offset,n,label):
    data=bytearray()
    while n:
        at=bisect.bisect_right(starts,offset)-1
        if at<0:return None
        base=starts[at];size=cold['clusters'][str(base)]['bytes'];within=offset-base
        if within>=size:return None
        take=min(n,size-within)
        chunk=(out/'artifacts/cold-clusters'/(str(base)+'-'+label+'.bin')).read_bytes()
        assert sha(chunk)==cold['clusters'][str(base)][label+'_sha256']
        data.extend(chunk[within:within+take]);offset+=take;n-=take
    return bytes(data)
rows=[]
for c in analysis['chunks']:
    if c['all_four_bytes_equal'] is not False:continue
    frames={name:next(r for r in group if r['sequence']==c[name+'_sequence'])
            for name,group in [('dma_submit',d),('dma_completion',d),('backend_submit',b),('backend_completion',b)]}
    first=frames['dma_submit']['data'];before=read(c['offset'],c['bytes'],'before');after=read(c['offset'],c['bytes'],'after')
    row=dict(c);row['frames']={name:{key:r[key] for key in ['monotonic_us','sha256','payload_bytes','status','artifact_offset']} for name,r in frames.items()}
    row['changed_bytes_from_dma_submit']={name:sum(x!=y for x,y in zip(first,r['data'])) for name,r in frames.items()}
    row['first_changed_byte']={name:next((i for i,(x,y) in enumerate(zip(first,r['data'])) if x!=y),None) for name,r in frames.items()}
    row['equals_cold_after']={name:r['data']==after if after is not None else None for name,r in frames.items()}
    row['equals_cold_before']={name:r['data']==before if before is not None else None for name,r in frames.items()}
    row['cold_targets']=[path for path,target in cold['targets'].items() if any(span['offset']<c['offset']+c['bytes'] and span['offset']+span['bytes']>c['offset'] for span in target['ranges'])]
    rows.append(row)
result=dict(physical_access=False,changed_chunks=rows,limits='Buffers differ between snapshots while the request is outstanding. This identifies a changing buffer, not the agent that changed it or a causal link to a failed hive. A final cold mismatch can also reflect later writes.')
(out/'phase-differences.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
