"""Actual216 bits plus pinned context-switch source; never authorize GPU writes."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'))

def context_facts(values):
 v={int(n,16):value for n,value in values.items()}
 channel=v[0x3204]&31;ctx_channel=(v[0x400148]>>24)&31
 valid=bool(v[0x400144]&0x10000);hardware=bool(v[0x40008c]&4)
 return dict(fifo_channel=channel,pgraph_channel=ctx_channel,pgraph_context_valid=valid,
  hardware_context_switch=hardware,model_switch_request_needed=(not valid or channel!=ctx_channel),
  model_hardware_switch_assertion_if_request=hardware and (not valid or channel!=ctx_channel),
  fifo_push_access=bool(v[0x3200]&1),fifo_pull_access=bool(v[0x3250]&1),pgraph_fifo_access=bool(v[0x400720]&1),
  declared_memory_cfg0='%08x'%v[0x100200],model_vram_bytes=v[0x10020c],
  exclusive_ownership_proven=False,engine_idle_proven=False,gpu_submission_authorized=False)

def main():
 dest=k/'state-observations.json';assert not dest.exists()
 a=read(k/'emu-candidate001/audit.json');assert a['scoped_display_passed'] and a['gpu_snapshot']['passed']
 model=k.parent/'video-transfer-protocol215/artifacts/source/hw/xbox/nv2a/pgraph/pgraph.c'
 text=model.read_text();assert 'NV_PGRAPH_CTX_CONTROL_CHID' in text and 'pg->waiting_for_context_switch = true;' in text
 assert 'pg->pending_interrupts |= NV_PGRAPH_INTR_CONTEXT_SWITCH;' in text
 native=k/'artifacts/handoff002/nt5-106/win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.c'
 assert 'HwInterrupt' not in native.read_text()
 rows=[dict(phase=s['phase'],facts=context_facts(s['values']),raw=s['values']) for s in a['gpu_snapshot']['snapshots']]
 dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(Path(__file__)),audit_sha256=sha(k/'emu-candidate001/audit.json'),
  context_source_sha256=sha(model),miniport_source_sha256=sha(native),observations=rows,
  snapshots_equal=rows[0]['raw']==rows[1]['raw'],observed_registers=26,actual_new_reads=52,
  physical_access=False,gpu_submission_authorized=False,
  hold_reasons=['No native instance-memory backing/reservation grant.','No native bounded context acquisition/interrupt/drain implementation.','No resident215 submit/completion adapter or proven DMA ordering.'],
  limits='Observed declared bits evaluated against exact compiled-model context branch. Snapshot equality and disabled FIFO access are not quiescence or a context grant; no physical alias/ownership or GPU writing authority.'),indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(passed=True,facts=[r['facts'] for r in rows]),indent=2))

if __name__=='__main__':main()
