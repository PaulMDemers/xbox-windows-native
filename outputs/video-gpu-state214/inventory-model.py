"""Pin reviewed observational MMIO registers against the actual compiled xemu source."""
import hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'model-inventory.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=ws/'outputs/xemu-cpu-surface-evict/build003';build=read(b/'build.json');manifest=read(b/'candidate-source-pins.json')
assert sha(b/'candidate-source-pins.json')==next(r for r in build['builds'] if r['case']=='candidate')['source_manifest_sha256']
src=Path('/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet');art=k/'artifacts/model';art.mkdir(parents=True,exist_ok=False)
names=['nv2a_regs.h','pmc.c','pfifo.c','pcrtc.c','pgraph/pgraph.c','pgraph/pgraph.h'];pins={};bodies={}
for name in names:
 n='hw/xbox/nv2a/'+name;p=src/n;assert sha(p)==manifest[n]
 q=art/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes());pins[name]=sha(q)
 if name.endswith('.c'):
  t=q.read_text();fn=name.split('/')[-1][:-2]+'_read';start=t.index('uint64_t '+fn+'(');end=t.index('\n}',start)+2
  bodies[fn]=dict(start_line=t[:start].count('\n')+1,body=t[start:end])
regs=(art/'nv2a_regs.h').read_text()
groups=[(0,'PMC',['BOOT_0','INTR_0','INTR_EN_0']),
 (0x2000,'PFIFO',['RAMHT','RAMFC','RAMRO','INTR_0','INTR_EN_0','CACHE1_PUSH0','CACHE1_PUSH1','CACHE1_DMA_PUSH','CACHE1_DMA_STATE','CACHE1_DMA_PUT','CACHE1_DMA_GET','CACHE1_PULL0']),
 (0x400000,'PGRAPH',['INTR','INTR_EN','CTX_USER','FIFO']),
 (0x600000,'PCRTC',['INTR_0','INTR_EN_0','START'])]
rows=[]
for base,group,names in groups:
 for name in names:
  symbol='NV_'+group+'_'+name;m=re.search(r'^#define '+symbol+r'\s+(0x[0-9a-fA-F]+)\b',regs,re.M);assert m,symbol
  local=int(m.group(1),16);offset=base+local;assert not offset%4 and offset+4<=0x681000
  rows.append(dict(symbol=symbol,block=group,local_offset=local,offset=offset))
assert len(rows)==22 and len({r['offset'] for r in rows})==22
assert 'd->pcrtc.raster++' in bodies['pcrtc_read']['body']
assert 'NV_PGRAPH_RDI_DATA' in bodies['pgraph_read']['body'] and 'address + 1' in bodies['pgraph_read']['body']
assert all(r['symbol'] not in ['NV_PCRTC_RASTER','NV_PGRAPH_RDI_DATA'] for r in rows)
header='/* SPDX-License-Identifier: GPL-2.0-or-later\n * Reviewed214 observational offsets, sourced from pinned xemu model.\n * No read has GPU ownership or physical fidelity authority. */\n#ifndef XGN_REGISTERS_H\n#define XGN_REGISTERS_H\n#define XGN_REGISTER_COUNT 22u\n#define XGN_MAPPED_LENGTH 0x681000u\nstatic const ULONG XgnOffsets[XGN_REGISTER_COUNT] = {\n'
header+=''.join('    0x%08xu, /* %s */\n'%(r['offset'],r['symbol']) for r in rows)
header+='};\n#endif\n';(k/'registers.h').write_text(header)
r=dict(passed=True,source_sha256=sha(Path(__file__)),source_pins=pins,registers=rows,reader_bodies=bodies,
 source_manifest_sha256=sha(b/'candidate-source-pins.json'),xemu_sha256=next(r['sha256'] for r in build['builds'] if r['case']=='candidate'),
 header_sha256=sha(k/'registers.h'),excluded_side_effect_reads=['NV_PCRTC_RASTER','NV_PGRAPH_RDI_DATA'],
 physical_access=False,guest_launch=False,physical_read_safety_proven=False,gpu_ownership_proven=False,
 limits='Source-matched emulator read paths only. No status register invented from an absent symbol, no default PMC_ENABLE capability claim, no RAMIN reads. Per-register reads are not one atomic snapshot or exclusive ownership.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Read-only register/model pins PASS:',len(rows))
