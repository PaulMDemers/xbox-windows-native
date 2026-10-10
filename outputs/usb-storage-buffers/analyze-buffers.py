"""Compare identified request lifecycles and preserved MDL bytes with cold sectors."""
import collections, hashlib, json, sys
from pathlib import Path

k=Path(__file__).resolve().parent;case=sys.argv[1]
assert case in ['emu001','emu002']
out=k/case;trace=json.loads((out/'trace.json').read_text())
f=json.loads((out/'forensics.json').read_text());payload=f['files']['payload2.txt']
base=payload['chain'][0]['byte_offset'];art=out/'artifacts'
sha=lambda b:hashlib.sha256(b).hexdigest()
def data(ref):
    if 'sha256' not in ref:return None
    b=(art/ref['artifact']).read_bytes();assert sha(b)==ref['sha256'] and len(b)==ref['bytes'];return b
def cold(offset,n,label):
    result=bytearray()
    while n:
        sector=offset//512*512;within=offset%512;take=min(n,512-within)
        p=art/'sectors'/(str(sector)+'-'+label+'.bin')
        if not p.exists():return None
        b=p.read_bytes();assert len(b)==512;result.extend(b[within:within+take]);n-=take;offset+=take
    return bytes(result)
def classify(b,offset,known_end):
    if b is None:return dict(unobserved=True)
    logical=offset-base;valid=max(0,min(len(b),known_end-logical))
    before=cold(offset,len(b),'before');after=cold(offset,len(b),'after')
    expected=bytes(33+((logical+i)*17+22)%90 for i in range(valid)) if logical>=0 else b''
    return dict(sha256=sha(b),bytes=len(b),logical_offset=logical,
                requested_pattern_prefix_bytes=valid,
                requested_pattern_prefix_exact=b[:valid]==expected if valid and logical>=0 else None,
                equals_before_sector=before==b if before is not None else None,
                equals_after_sector=after==b if after is not None else None,
                requested_prefix_equals_cold_after=b[:valid]==after[:valid] if after is not None and valid else None)
requests={};outstanding={};known_end=0;source=[];returns={};issues=[]
for expected_seq,event in enumerate(trace['events']):
    assert event['sequence']==expected_seq
    kind=event['kind']
    if kind=='source_entry' and not event['irp_flags']&2:
        known_end=max(known_end,event['file_offset']+event['length'])
        ref=event['buffer'];raw=data(ref.get('virtual',ref))
        expected=bytes(33+((event['file_offset']+i)*17+22)%90 for i in range(event['length']))
        source.append(dict(sequence=expected_seq,parent_irp=event['parent_irp'],context=event['context'],
                           file_offset=event['file_offset'],bytes=event['length'],exact_requested_pattern=raw==expected))
    elif kind in ['read_submit','write_submit']:
        ident=event['request_id'];child=event['child_irp'];assert ident not in requests and child not in outstanding
        outstanding[child]=ident
        buffer=event['buffer'];offset=event['expected_absolute_offset']
        row=dict(id=ident,operation=kind,child_irp=child,context=event['context'],parent_irp=event['parent_irp'],
                 submitted_sequence=expected_seq,submit_thread=event['thread'],disk_offset=offset,bytes=event['length'],
                 known_requested_end=known_end,wait=event['wait'],pfns=buffer['pfns'],
                 submitted_virtual=classify(data(buffer['virtual']),offset,known_end),
                 submitted_physical=classify(data(buffer['physical']),offset,known_end),
                 submitted_virtual_equals_physical=buffer['virtual_equals_physical'])
        requests[ident]=row
    elif kind=='completion':
        ident=event['request_id'];row=requests[ident];assert outstanding.pop(event['child_irp'])==ident
        assert row['context']==event['context'] and row['operation']==event['operation']
        buffer=event['buffer'];row.update(completed_sequence=expected_seq,completion_thread=event['thread'],
            status=event['status'],information=event['information'],completion_pfns=buffer['pfns'],
            completed_physical=classify(data(buffer['physical']),row['disk_offset'],row['known_requested_end']),
            completed_virtual=classify(data(buffer['virtual']),row['disk_offset'],row['known_requested_end']),
            completion_virtual_equals_physical=buffer['virtual_equals_physical'])
        row['physical_changed_during_request']=row['submitted_physical']['sha256']!=row['completed_physical']['sha256']
        row['pfn_mapping_unchanged']=row['pfns']==row['completion_pfns']
    elif kind=='dispatch_return':
        ident=event['request_id'];assert ident in requests and ident not in returns
        returns[ident]=event
        requests[ident].update(dispatch_return_sequence=expected_seq,dispatch_return_status=event['status'],
                              completion_observed_before_dispatch_return=event['completion_already_observed'])
for ident,row in requests.items():
    if 'completed_sequence' not in row:issues.append(dict(request=ident,missing='completion'))
    if ident not in returns:issues.append(dict(request=ident,missing='dispatch return'))
writes=[v for v in requests.values() if v['operation']=='write_submit']
result=dict(case=case,physical_access=False,trace_status=trace['status'],trace_error=trace.get('error'),
    events=len(trace['events']),sources=source,requests=list(requests.values()),missing=issues,
    counts=dict(requests=len(requests),writes=len(writes),completed_writes=sum('completed_sequence' in v for v in writes),
                pending_dispatch_returns=sum(v.get('dispatch_return_status')==0x103 for v in requests.values()),
                cross_thread_completions=sum(v.get('completion_thread')!=v['submit_thread'] for v in requests.values() if 'completed_sequence' in v),
                submitted_write_virtual_physical_mismatches=sum(not v['submitted_virtual_equals_physical'] for v in writes),
                submitted_write_old_sectors=sum(v['submitted_physical']['equals_before_sector'] is True for v in writes),
                submitted_write_expected_prefixes=sum(v['submitted_physical']['requested_pattern_prefix_exact'] is True for v in writes)),
    limits='Requested-pattern prefix is derived from observed nonpaging write requests, not a guest API-success claim. '
           'Completion statuses belong to FATX child IRPs; they do not expose IDE scatter/gather bytes. '
           'Debugger pauses can change the failure. Matching submitted data cannot prove all later writes stayed correct.')
(out/'buffer-analysis.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(status=result['trace_status'],counts=result['counts'],missing=issues)))
