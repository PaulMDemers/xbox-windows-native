"""Verify actual232 report and raw reads; decode reason without inferring ownership."""
import hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'consume-review001.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
t=read(k/'trace001/trace.json');assert t['closed'];p=t.get('preserve_result',{})
assert p.get('publication_version')==232 and p['tuple_published']==int(p['state'] in [3,4,6])
registers=k/'artifacts/build001/source/hw/xbox/nv2a/nv2a_regs.h';pins=read(k/'candidate001-source-pins.json');assert sha(registers)==pins['hw/xbox/nv2a/nv2a_regs.h']
text=registers.read_text()
def mask(name):
    values=re.findall(r'^#\s*define\s+'+name+r'\s+([^\r\n]+)',text,re.M);assert len(values)==1
    raw=values[0].strip()
    if re.fullmatch(r'0x[0-9A-Fa-f]+',raw):return int(raw,16)
    m=re.fullmatch(r'\(1\s*<<\s*(\d+)\)',raw);assert m and 0<=int(m[1])<32;return 1<<int(m[1])
def field(v,name):m=mask(name);return (v&m)//(m&-m)
phases={};names=['GET','PUT','DMA_STATE','PUSH0','PUSH1','DMA_PUSH','PULL0','STATUS','SUBROUTINE','PGRAPH_FIFO']
for phase in ['request','gate']:
    if phase=='gate' and not p['tuple_published']:continue
    w=[p[phase+str(i)] for i in range(10)]
    phases[phase]=dict(raw={n:f'0x{v:08x}' for n,v in zip(names,w)},numerical_put_minus_get=w[1]-w[0],get_equals_put=w[0]==w[1],parser_method_count=field(w[2],'NV_PFIFO_CACHE1_DMA_STATE_METHOD_COUNT'),parser_error=field(w[2],'NV_PFIFO_CACHE1_DMA_STATE_ERROR'))
names={0:'empty_queue_and_parser',1:'expired_or_cancelled',2:'word_budget',3:'iteration_budget',4:'wait_or_puller_refusal',5:'disabled_or_suspended_access',6:'parser_error',7:'invalid_dma_range_or_alignment',8:'invalid_puller_count',9:'incomplete_queue_or_parser'}
rawbytes=0
for phase in ['before','after']:
    for v in t.get(phase,[]):
        f=ws/v['path'];assert f.stat().st_size==v['bytes'] and sha(f)==v['sha256'];rawbytes+=v['bytes']
assert rawbytes==212992 and t['physical_mode_restored'] and not t['remaining_breakpoints']
if p['tuple_published']:
    assert p['consume_steps']<=32768 and p['consume_words']<=32768
    assert p['consume_stop'] in names
    if p['consume_stop']==0:
        assert phases['gate']['get_equals_put'] and phases['gate']['parser_method_count']==phases['gate']['parser_error']==0
    waits={phase:[label for bit,label in [(1,'PGRAPH_FIFO_access_off'),(2,'nop'),(4,'flip'),(8,'context')] if p['wait_'+phase]&bit] for phase in ['before','after']}
else:waits={}
dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(Path(__file__)),trace_sha256=sha(k/'trace001/trace.json'),registers_sha256=sha(registers),terminal_state=p['state'],reason=p['reason'],tuple_published=p['tuple_published'],consume_stop=names.get(p.get('consume_stop')) if p['tuple_published'] else 'withheld_timeout_tuple',consume_steps=p.get('consume_steps') if p['tuple_published'] else None,consume_words=p.get('consume_words') if p['tuple_published'] else None,actual_words_consumed=p['tuple_published'] and p['consume_words']>0,waits=waits,phases=phases,reserved_bytes_unchanged=t['reserved_bytes_unchanged'],raw_read_bytes=rawbytes,guest_resumed=t.get('guest_resumed',False),quarantined=t.get('quarantine_retained_until_owned_process_exit',False),backend_preservation_qualified=False,physical_access=False),indent=2)+'\n')
print(json.dumps(read(dest),indent=2))
