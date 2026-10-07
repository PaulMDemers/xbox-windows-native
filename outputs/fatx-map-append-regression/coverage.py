"""Report actual planned boundaries independently of runtime completion claims."""
from common import *
events=[]
for index,prefix in enumerate(PREFIXES):
    old=prefix
    for j,size in enumerate(CHUNKS):
        end=old+size;maximum=end+35
        events.append(dict(index=index,append=j,old=old,new=end,mapping_max=maximum,size=size,crosses_sector=old//512!=(end-1)//512,crosses_page=old//4096!=(end-1)//4096,crosses_cluster=old//65536!=(end-1)//65536,shrink_releases_cluster=(maximum+65535)//65536>(end+65535)//65536))
        old=end
r=dict(helper_sha256=read(k/'build-review.json')['probe_sha256'],prefixes=PREFIXES,chunks=CHUNKS,appended_bytes_per_file=sum(CHUNKS),rounds=4,events_per_round=len(events),events_total=len(events)*4,counts={name:sum(v[name] for v in events)*4 for name in ['crosses_sector','crosses_page','crosses_cluster','shrink_releases_cluster']},target111_109_cases=[v for v in events if v['old']==270225 and v['size']==220],events=events,limits='Planned coverage, not completion. No concurrent writer or volume flusher. Prefix flushes and per-case log flushes are present in both modes. Explicit-flush mode changes calls only within append lifecycle.')
save(k/'coverage.json',r);print(json.dumps({n:r[n] for n in ['events_total','counts','target111_109_cases']},indent=2))
