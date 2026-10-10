"""Check every observational offset and model limitation before compiling224."""
import hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'inventory.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=k.parent/'video-transfer-protocol215';m=json.loads((old/'inventory.json').read_text())
src=old/'artifacts/source/hw/xbox/nv2a'
for n,h in m['source_pins'].items():assert sha(src/n)==h
names=['CACHE1_PUSH0','CACHE1_PUSH1','CACHE1_PUT','CACHE1_STATUS','CACHE1_DMA_PUSH','CACHE1_DMA_STATE','CACHE1_DMA_SUBROUTINE','CACHE1_DMA_PUT','CACHE1_DMA_GET','CACHE1_PULL0','CACHE1_GET','RUNOUT_STATUS','INTR_0']
symbols=['NV_PFIFO_'+n for n in names]+['NV_PGRAPH_INTR','NV_PGRAPH_CTX_CONTROL','NV_PGRAPH_CTX_USER']
regs=(src/'nv2a_regs.h').read_text();rows=[]
for name in symbols:
    match=re.search(r'^#define '+name+r'\s+(0x[0-9a-fA-F]+)\b',regs,re.M);assert match,name
    local=int(match[1],16);offset=local+(0x2000 if 'PFIFO' in name else 0x400000)
    rows.append(dict(symbol=name,offset=offset))
h=(k/'retirement.h').read_text();table=h[h.index('X224Offsets'):h.index('void x224_sample')]
offsets=[int(s,16) for s in re.findall(r'0x[0-9a-fA-F]+',table)]
assert offsets==[r['offset'] for r in rows]
fifo=(src/'pfifo.c').read_text();graph=(src/'pgraph/pgraph.c').read_text()
assert 'TODO: should we become busy here??' in fifo and '// NV_PFIFO_CACHE1_DMA_PUSH_STATE _BUSY' in fifo
assert 'if (dma_get_v == dma_put_v) break;' in fifo
assert 'r = NV_PFIFO_RUNOUT_STATUS_LOW_MARK; /* low mark empty */' in fifo
assert 'NV_PGRAPH_STATUS' not in graph and 'r = pgraph_reg_r(pg, addr);' in graph
assert not any(x in (k/'driver.c').read_text() for x in ['WRITE_REGISTER','NV_PGRAPH_INTR_CONTEXT_SWITCH_RESET'])
r=dict(passed=True,offsets=rows,source_manifest_sha256=m['source_manifest_sha256'],xemu_sha256=m['xemu_sha256'],source_pins=m['source_pins'],
       limits=['Pusher does not maintain DMA busy field; guest-written stored bits are not engine activity.',
               'RUNOUT read returns constant empty in this model.',
               'No PGRAPH_STATUS read implementation in pinned graph body; do not invent an idle predicate.',
               'GET==PUT can coexist with residual method_count, as equality is tested before method execution.',
               'Sequential samples cannot establish atomicity, backend retirement, CPU producer revocation or instance ownership.'],
       physical_access=False,gpu_ownership_proven=False)
dest.write_text(json.dumps(r,indent=2)+'\n');print('224 observational model inventory PASS',len(rows))
