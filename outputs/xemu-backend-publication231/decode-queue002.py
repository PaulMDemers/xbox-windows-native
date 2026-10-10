"""Decode actual terminal telemetry against compiled register masks; preserve raw words."""
import hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'queue-review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=read(k/'trace001/trace.json');p=t['preserve_result']
assert t['closed'] and p['publication_version']==231 and p['tuple_published']==int(p['state'] in [3,4,6])
regs=k/'artifacts/build001/source/hw/xbox/nv2a/nv2a_regs.h'
pins=read(k/'candidate001-source-pins.json');assert sha(regs)==pins['hw/xbox/nv2a/nv2a_regs.h']
text=regs.read_text()
def mask(name):
    values=re.findall(r'^#\s*define\s+'+name+r'\s+([^\r\n]+)',text,re.M)
    assert len(values)==1,(name,values)
    raw=values[0].strip()
    if re.fullmatch(r'0x[0-9A-Fa-f]+',raw):return int(raw,16)
    m=re.fullmatch(r'\(1\s*<<\s*(\d+)\)',raw)
    assert m and 0<=int(m[1])<32,(name,raw)
    return 1<<int(m[1])
def extract(value,name):
    m=mask(name);return (value&m)//(m&-m)
names=['GET','PUT','DMA_STATE','PUSH0','PUSH1','DMA_PUSH','PULL0','STATUS','SUBROUTINE','PGRAPH_FIFO']
phases={}
for phase in ['request','gate']:
    if phase=='gate' and not p['tuple_published']:continue
    words=[p[phase+str(i)] for i in range(10)]
    phases[phase]=dict(raw={n:f'0x{v:08x}' for n,v in zip(names,words)},
        get_equals_put=words[0]==words[1],
        parser_method_count=extract(words[2],'NV_PFIFO_CACHE1_DMA_STATE_METHOD_COUNT'),
        parser_error=extract(words[2],'NV_PFIFO_CACHE1_DMA_STATE_ERROR'),
        push_access=extract(words[3],'NV_PFIFO_CACHE1_PUSH0_ACCESS'),
        dma_push_access=extract(words[5],'NV_PFIFO_CACHE1_DMA_PUSH_ACCESS'),
        dma_push_status=extract(words[5],'NV_PFIFO_CACHE1_DMA_PUSH_STATUS'),
        pull_access=extract(words[6],'NV_PFIFO_CACHE1_PULL0_ACCESS'),
        pgraph_fifo_access=extract(words[9],'NV_PGRAPH_FIFO_ACCESS'))
if p['tuple_published'] and p['reason']==1:
    g=phases['gate'];assert not g['get_equals_put'] or g['parser_method_count'] or g['parser_error']
rawbytes=0
for phase in ['before','after']:
    for row in t[phase]:
        path=ws/row['path'];assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256'];rawbytes+=row['bytes']
assert rawbytes==212992 and t['physical_mode_restored'] and not t['remaining_breakpoints']
dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(Path(__file__)),trace_sha256=sha(k/'trace001/trace.json'),compiled_register_definitions_sha256=sha(regs),state=p['state'],reason=p['reason'],tuple_published=p['tuple_published'],old_halt=p['old_halt'],phases=phases,raw_read_bytes=rawbytes,reserved_bytes_unchanged=t['reserved_bytes_unchanged'],actual_queue_consumption=False,backend_preservation_qualified=False,physical_access=False),indent=2)+'\n')
print(json.dumps(phases,indent=2))
