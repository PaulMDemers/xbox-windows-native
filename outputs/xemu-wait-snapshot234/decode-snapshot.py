"""Decode actual bounded ring; preserve missing pairs and reset/IRQ distinctions."""
import hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'snapshot-review001.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
t=read(k/'trace002/trace.json');assert t['closed']
pins=read(k/'candidate001-source-pins.json');src=k/'artifacts/build001/source/hw/xbox/nv2a/nv2a_regs.h'
assert sha(src)==pins['hw/xbox/nv2a/nv2a_regs.h']
text=src.read_text()
def mask(name):
    v=re.findall(r'^#\s*define\s+'+name+r'\s+([^\r\n]+)',text,re.M);assert len(v)==1
    raw=v[0].strip()
    if re.fullmatch(r'0x[0-9a-fA-F]+',raw):return int(raw,16)
    m=re.fullmatch(r'\(1\s*<<\s*(\d+)\)',raw);assert m and 0<=int(m[1])<32;return 1<<int(m[1])
error=mask('NV_PGRAPH_INTR_ERROR')
names=['seq','when','kind','value','pending','enabled','nsource','trapped','data','waits','fifo_valid']+[f'fifo{i}' for i in range(10)]
views={};unique={}
for name in ['wait_live_snapshot','wait_snapshot_at_stop','wait_snapshot_after_preserve']:
    if name not in t:continue
    value=t[name];reply=value['reply']
    header={a:int(b) for a,b in re.findall(r'(version|state|tuple_published|total|count|capacity|overwritten)=(\d+)',reply)}
    assert header['version']==234 and header['state']==3 and header['tuple_published']==1 and header['capacity']==256
    assert header['count']<=256 and header['total']>=header['count'] and header['overwritten']==header['total']-header['count']
    raw=re.findall(r'row=([0-9,]+)',reply);assert len(raw)==header['count']+1
    rows=[]
    for item in raw:
        vals=[int(v) for v in item.split(',')];assert len(vals)==21
        row=dict(zip(names,vals));assert row['seq']<=2**64-1 and row['when']<=2**63-1
        assert all(row[v]<=2**32-1 for v in names[2:])
        assert row['fifo_valid'] in [0,1] and row['waits']<=15
        if not row['fifo_valid']:assert all(row[f'fifo{i}']==0 for i in range(10))
        rows.append(row)
    current=rows.pop(0);assert current['seq']==0 and current['kind']==9 and current['fifo_valid']==0
    assert [r['seq'] for r in rows]==list(range(header['total']-header['count']+1,header['total']+1))
    for r in rows:
        if r['seq'] in unique:assert unique[r['seq']]==r
        unique[r['seq']]=r
    views[name]=dict(header=header,current=current,rows=rows,read_attempts=value['attempts'])
events=[unique[n] for n in sorted(unique)];producers=[];acks=[];reset=[];missing=[]
for r in events:
    nxt=unique.get(r['seq']+1)
    if r['kind'] in [1,4,7]:
        expected={1:2,4:5,7:8}[r['kind']]
        if not nxt or nxt['kind']!=expected:missing.append(dict(seq=r['seq'],expected_kind=expected));continue
        if r['kind']==1:
            assert not r['fifo_valid'] and not nxt['fifo_valid'] and r['value']==nxt['value']!=0
            assert not r['pending']&error and nxt['pending']&error and nxt['waits']&2
            assert nxt['data']==nxt['value']
            producers.append(dict(before_seq=r['seq'],after_seq=nxt['seq'],parameter=r['value'],trapped=nxt['trapped'],nsource=nxt['nsource']))
        elif r['kind']==4:
            assert r['fifo_valid'] and nxt['fifo_valid'] and r['value']==nxt['value']
            assert nxt['pending']==r['pending']&~r['value']
            cleared=bool(r['waits']&2) and not bool(nxt['waits']&2)
            if cleared:assert r['pending']&error and r['value']&error and not nxt['pending']&error
            acks.append(dict(before_seq=r['seq'],after_seq=nxt['seq'],value=r['value'],cleared_nop=cleared,pending_before=r['pending'],pending_after=nxt['pending']))
        else:reset.append(dict(before_seq=r['seq'],after_seq=nxt['seq'],waits_before=r['waits'],waits_after=nxt['waits']))
# Pair only a captured producer with a later observed guest clearing ack. A reset
# or another producer invalidates the open pairing; lost prefix remains unknown.
lifecycles=[];open_producer=None
for r in events:
    if r['kind']==2:open_producer=r
    elif r['kind'] in [7,8]:open_producer=None
    elif r['kind']==5 and not r['waits']&2:
        prev=unique.get(r['seq']-1)
        if prev and prev['kind']==4 and prev['waits']&2 and open_producer:
            lifecycles.append(dict(producer_seq=open_producer['seq'],ack_before_seq=prev['seq'],ack_after_seq=r['seq'],parameter=open_producer['value']))
        open_producer=None
dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(Path(__file__)),trace_sha256=sha(k/'trace002/trace.json'),registers_sha256=sha(src),error_mask=error,views=views,unique_events=len(events),producer_pairs=producers,ack_pairs=acks,reset_pairs=reset,complete_captured_lifecycles=lifecycles,missing_pair_boundaries=missing,
    complete_snapshot_protocol=len(views)==3 and len({v['reply'] for n,v in t.items() if n in views})==1,waited_at_stop=None,actual_preservation_wait_before=t.get('preserve_result',{}).get('wait_before'),backend_ownership_qualified=False,physical_access=False,
    limits='ONE worker-copied bounded overwritten ring, subsequent immutable reads; current PG-only row is the earlier live sample, never stopped state; no guest PC/source-handler pin. Observed INTR MMIO acknowledgements are distinct from reset and post-IRQ-update worker return. No producer-close/ownership contract follows.'),indent=2)+'\n')
print(json.dumps(dict(unique_events=len(events),producers=len(producers),acks=len(acks),clearing_acks=sum(r['cleared_nop'] for r in acks),lifecycles=len(lifecycles),missing=len(missing),reset_pairs=len(reset))))
