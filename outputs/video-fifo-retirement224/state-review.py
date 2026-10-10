"""Decode actual224 channel/context fields against pinned model; no new observation or grant."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'state-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pair=read(k/'pair-review.json');assert pair['passed'];v=pair['cases']['candidate001']['raw_words'];assert len(v)==8 and all(len(x)==16 for x in v)
src=k.parent/'video-transfer-protocol215/artifacts/source/hw/xbox/nv2a';pins=read(k/'model-review002.json')['source_pins']
for n,h in pins.items():assert sha(src/n)==h,n
regs=(src/'nv2a_regs.h').read_text();graph=(src/'pgraph/pgraph.c').read_text()
assert '#   define NV_PGRAPH_CTX_CONTROL_CHID                          (1 << 16)' in regs
assert '#   define NV_PGRAPH_CTX_USER_CHID                            0x1F000000' in regs
assert '#   define NV_PFIFO_CACHE1_PUSH1_CHID                         0x0000001F' in regs
assert 'bool valid = channel_valid && pgraph_channel_id == channel_id;' in graph
states=[]
for row in v:
    states.append(dict(pfifo_channel=row[1]&31,pgraph_channel=(row[15]>>24)&31,
        current_context_valid=bool(row[14]&0x10000),cache_push_enabled=bool(row[0]&1),dma_push_enabled=bool(row[4]&1),
        cache_pull_enabled=bool(row[9]&1),dma_get=row[8],dma_put=row[7],pgraph_irq=row[13],pfifo_irq=row[12]))
dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(Path(__file__)),pair_sha256=sha(k/'pair-review.json'),
    raw_log_sha256=pair['cases']['candidate001']['log_sha256'],model_pins=pins,states=states,all_equal=all(x==states[0] for x in states),
    inference='Pinned pgraph_context_switch requires a valid matching channel; these snapshots do not provide one. No context-switch request was issued or observed by224.',
    limits='Disabled push/pull and zero pointers/IRQs are observations, not producer/backend retirement. No ownership or GPU submission grant. Hardware context-switch mode is not among224 sampled words.',
    gpu_ownership_qualified=False,physical_access=False),indent=2)+'\n');print(json.dumps(states[0],indent=2))
