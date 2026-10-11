"""Decode private binary records; correlate generations, bytes and completions."""
import collections,hashlib,json,struct,sys
from pathlib import Path

HEADER=struct.Struct('<16Q');MAGIC=0x315246534e5758
NAMES=['magic','version','sequence','id','phase','offset','bytes','qiov','owner','status','monotonic_us','qiov_offset','payload_bytes','flags','niov','reserved']
def records(path):
    result=[];seq=0
    with path.open('rb') as f:
        while header:=f.read(HEADER.size):
            assert len(header)==HEADER.size,'Partial header'
            row=dict(zip(NAMES,HEADER.unpack(header)));seq+=1
            assert row['magic']==MAGIC and row['version']==1 and row['sequence']==seq
            assert row['payload_bytes']<=1048576 and row['reserved']==0
            row['status']=struct.unpack('<q',struct.pack('<Q',row['status']))[0]
            row['artifact_offset']=f.tell();data=f.read(row['payload_bytes'])
            assert len(data)==row['payload_bytes'],'Partial payload'
            row['sha256']=hashlib.sha256(data).hexdigest() if data else None
            row['data']=data;result.append(row)
    return result

def analyze(dma,backend):
    issues=[];requests={};chunks=[];active={};backend_active={};backends=[];backend_seen=set()
    for row in dma:
        ident=row['id'];phase=row['phase']
        if phase==0:
            assert ident not in requests and row['owner'] not in active
            requests[ident]=dict(begin=row,sg=[],chunks=[]);active[row['owner']]=ident
        else:
            assert ident in requests;req=requests[ident]
            assert req['begin']['owner']==row['owner']
            if phase==11:req['sg'].append(row)
            elif phase==1:
                assert not req['chunks'] or 'end' in req['chunks'][-1]
                chunk=dict(begin=row,dma_id=ident);req['chunks'].append(chunk);chunks.append(chunk)
            elif phase==2:
                chunk=req['chunks'][-1];assert 'end' not in chunk
                assert all(chunk['begin'][n]==row[n] for n in ['offset','bytes','qiov','owner'])
                chunk['end']=row
            elif phase==3:
                assert 'end' not in req and active.pop(row['owner'])==ident;req['end']=row
            else:raise AssertionError(('Unknown DMA phase',phase))
    for row in backend:
        key=row['id']
        if row['phase']==4:
            assert key not in backend_seen;backend_seen.add(key);backend_active[key]=dict(begin=row)
        elif row['phase']==5:
            pair=backend_active.pop(key);begin=pair['begin']
            assert all(begin[n]==row[n] for n in ['offset','bytes','qiov','qiov_offset','owner'])
            pair['end']=row;backends.append(pair)
        else:raise AssertionError(('Unknown backend phase',row['phase']))
    index=collections.defaultdict(list)
    for pair in backends:
        b=pair['begin'];index[(b['qiov'],b['offset'],b['bytes'])].append(pair)
    matched=set();summary=[]
    for chunk in chunks:
        begin=chunk['begin'];end=chunk.get('end')
        candidates=[p for p in index[(begin['qiov'],begin['offset'],begin['bytes'])]
                    if end and begin['monotonic_us']<=p['begin']['monotonic_us']<=p['end']['monotonic_us']<=end['monotonic_us']]
        if len(candidates)!=1:
            issues.append(dict(dma_id=chunk['dma_id'],sequence=begin['sequence'],backend_matches=len(candidates)));continue
        pair=candidates[0];bid=pair['begin']['id'];assert bid not in matched;matched.add(bid)
        complete=all(r['payload_bytes']==r['bytes'] and not r['flags']>>62 for r in [begin,end,pair['begin'],pair['end']])
        equal=all(r['data']==begin['data'] for r in [end,pair['begin'],pair['end']]) if complete else None
        summary.append(dict(dma_id=chunk['dma_id'],backend_id=bid,offset=begin['offset'],bytes=begin['bytes'],
            dma_submit_sequence=begin['sequence'],dma_completion_sequence=end['sequence'],
            backend_submit_sequence=pair['begin']['sequence'],backend_completion_sequence=pair['end']['sequence'],
            dma_status=end['status'],backend_status=pair['end']['status'],all_four_captures_complete=complete,
            all_four_bytes_equal=equal,submitted_sha256=begin['sha256']))
    for ident,req in requests.items():
        if 'end' not in req:issues.append(dict(dma_id=ident,missing='final completion'))
        if any('end' not in c for c in req['chunks']):issues.append(dict(dma_id=ident,missing='chunk completion'))
        begin=req['begin']
        if sum(s['bytes'] for s in req['sg'])!=begin['bytes']:issues.append(dict(dma_id=ident,error='SG total mismatch'))
        if len(req['sg'])!=begin['flags']:issues.append(dict(dma_id=ident,error='SG count mismatch'))
        if 'end' in req and req['end']['status']==0:
            if sum(c['begin']['bytes'] for c in req['chunks'])!=begin['bytes']:issues.append(dict(dma_id=ident,error='Successful request incomplete byte total'))
    return dict(dma_requests=len(requests),dma_chunks=len(chunks),backend_pairs=len(backends),
        dma_final_status_counts=dict(collections.Counter(r['end']['status'] for r in requests.values() if 'end' in r)),
        backend_completion_status_counts=dict(collections.Counter(r['end']['status'] for r in backends)),
        matched_chunks=len(summary),backend_pairs_not_dma_matched=len(backends)-len(matched),
        outstanding_dma=list(active.values()),outstanding_backend=list(backend_active),issues=issues,
        cap_or_missing_records=sum(bool(r['flags']>>62) for r in dma+backend),chunks=summary)

if __name__=='__main__':
    k=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['emu001','emu002']
    run=k.parents[1]/('work/runs/nt5setup-'+case);out=k/case
    assert (run/'cleanup.json').exists()
    rows={n:records(run/('transfer.'+n+'.bin')) for n in ['dma','backend']}
    result=analyze(rows['dma'],rows['backend'])
    for name,entries in rows.items():
        (out/(name+'-index.json')).write_text(json.dumps([{n:v for n,v in e.items() if n!='data'} for e in entries],separators=(',',':'))+'\n')
    result.update(physical_access=False,raw={name:dict(bytes=(run/('transfer.'+name+'.bin')).stat().st_size,sha256=hashlib.sha256((run/('transfer.'+name+'.bin')).read_bytes()).hexdigest()) for name in rows},limits='Byte snapshots and returned I/O status, not a power-loss/flush guarantee. Instrumentation changes host timing. No guest register or memory mutation.')
    (out/'transfer-analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({n:v for n,v in result.items() if n!='chunks'}))
