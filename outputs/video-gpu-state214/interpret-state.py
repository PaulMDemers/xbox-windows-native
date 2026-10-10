"""Describe observed bits, never derive GPU ownership or authorize submission."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'state-observations.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read(k/'emu-candidate001/audit.json');assert a['scoped_display_passed'] and a['gpu_snapshot']['passed']
inventory=read(k/'model-inventory.json');registers={r['offset']:r['symbol'] for r in inventory['registers']}
rows=[]
for snapshot in a['gpu_snapshot']['snapshots']:
 v={int(name,16):value for name,value in snapshot['values'].items()}
 rows.append(dict(phase=snapshot['phase'],raw={registers[n]:'%08x'%value for n,value in v.items()},
  model_bits=dict(cache1_push_access=bool(v[0x3200]&1),cache1_channel_id=v[0x3204]&31,
   cache1_dma_mode=bool(v[0x3204]&0x100),cache1_dma_push_access=bool(v[0x3220]&1),
   cache1_dma_push_status_bit12=bool(v[0x3220]&0x1000),cache1_pull_access=bool(v[0x3250]&1),
   pgraph_fifo_access=bool(v[0x400720]&1),pgraph_context_channel_id=(v[0x400148]>>24)&31,
   dma_get_equals_put=v[0x3244]==v[0x3240],retained_framebuffer=v[0x600800]&0x07ffffff),
  exclusive_ownership_proven=False,engine_idle_proven=False))
changes=[dict(symbol=registers[int(n,16)],before=a['gpu_snapshot']['snapshots'][0]['values'][n],after=a['gpu_snapshot']['snapshots'][1]['values'][n])
 for n in a['gpu_snapshot']['snapshots'][0]['values'] if a['gpu_snapshot']['snapshots'][0]['values'][n]!=a['gpu_snapshot']['snapshots'][1]['values'][n]]
header=(k/'artifacts/model/nv2a_regs.h').read_text()
for name,value in [('NV_PFIFO_CACHE1_PUSH0_ACCESS','(1 << 0)'),('NV_PFIFO_CACHE1_PUSH1_CHID','0x0000001F'),
 ('NV_PFIFO_CACHE1_PUSH1_MODE','0x00000100'),('NV_PFIFO_CACHE1_DMA_PUSH_STATUS','(1 << 12)'),
 ('NV_PGRAPH_FIFO_ACCESS','(1 << 0)'),('NV_PGRAPH_CTX_USER_CHID','0x1F000000')]:
 assert any(name in line and value in line for line in header.splitlines()),name
r=dict(passed=True,source_sha256=sha(Path(__file__)),audit_sha256=sha(k/'emu-candidate001/audit.json'),
 model_inventory_sha256=sha(k/'model-inventory.json'),observations=rows,changes=changes,
 observed_registers=22,actual_new_reads=44,physical_access=False,gpu_ownership_proven=False,gpu_transfer_authorized=False,
 limits='Decoded declared bits from exact pinned model header. Status bit12 kept literal; no engine STATUS read. Sequential samples,zero IRQ/equal pointers/stable configs cannot prove idle,absence of other owner,instance-memory safety,physical fidelity or completion.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=True,changes=changes,model_bits=[r['model_bits'] for r in rows]),indent=2))
