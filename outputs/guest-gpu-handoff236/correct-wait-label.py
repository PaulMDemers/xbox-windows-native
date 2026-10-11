"""Retain failed report interpretation; label wait bits from exact compiled source."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
dest=k/'wait-label-review002.json';assert not dest.exists()
parent=k.parent/'xemu-wait-snapshot234';pins=read(parent/'candidate001-source-pins.json')
sources={}
for name in ['hw/xbox/nv2a/pgraph/pgraph.c','hw/xbox/nv2a/pfifo.c']:
 p=parent/'artifacts/build001/source'/name;assert sha(p)==pins[name];sources[name]=sha(p)
 text=p.read_text();assert ('NV_PGRAPH_FIFO_ACCESS) ? 1 : 0' in text or '!can_fifo_access(d) ? 1 : 0' in text)
 assert 'waiting_for_nop ? 2 : 0' in text or 'waiting_for_nop) ? 2 : 0' in text
 assert 'waiting_for_context_switch ? 8 : 0' in text or 'waiting_for_context_switch) ? 8 : 0' in text
failed=dict(passed=False,reason='Report mislabeled wait bit1 as context-switch; actual compiled mapping bit1=FIFO-access-disabled, context-switch=bit8. Numeric raw trace was correct.',compiled_source_pins=sources,physical_access=False)
(k/'wait-label-review001-failure.json').write_text(json.dumps(failed,indent=2)+'\n')
before={}
for kit in [k.parent/'guest-gpu-handoff235',k]:
 p=kit/'REPORT.md';raw=p.read_bytes();before[p.relative_to(ws).as_posix()]=sha(p);(kit/'REPORT-before-wait-label-correction.md').write_bytes(raw)
 text=raw.decode().replace('context-switch wait remains','FIFO access remains disabled')
 assert text!=raw.decode()
 text+='\nWait-label source review corrected the original report: bit1 denotes disabled\nPGRAPH FIFO access; context-switch wait is bit8 and is NOT set in waits1.\nOriginal report bytes and failed interpretation record remain preserved.\n'
 p.write_text(text)
p=ws/'outputs/engineering-notes/CONTINUATION.md';raw=p.read_bytes();meta=read(k/'continuation001.json');oldprefix=raw[:meta['new_prefix_bytes']];tail=raw[meta['new_prefix_bytes']:]
assert hashlib.sha256(tail).hexdigest()==meta['previous_tail_sha256'];(k/'continuation-prefix-before-wait-label-correction.md').write_bytes(oldprefix)
prefix=oldprefix.decode().replace('waits3->1/context\nwait remains','waits3->1/FIFO\naccess disabled; context wait(bit8) not set')
assert prefix!=oldprefix.decode();prefix+=''
p.write_bytes(prefix.encode()+tail)
p=k/'NEXT.md';p.write_text(p.read_text()+'\nMask correction from pinned compiled source: bit1=FIFO access disabled, bit2=NOP,\nbit4=flip, bit8=context-switch. waits1 has NO context-switch flag. Preserve\nold report interpretation failure; phase snapshots should record actual FIFO\naccess gating, not diagnose a nonexistent context wait.\n')
dest.write_text(json.dumps(dict(passed=True,compiled_source_pins=sources,wait_bit_names={'1':'FIFO_ACCESS_DISABLED','2':'NOP','4':'FLIP','8':'CONTEXT_SWITCH'},actual_ack_waits=[3,1],context_switch_set_after=False,corrected_reports_previous_sha256=before,new_continuation_prefix_bytes=len(prefix.encode()),previous_tail_sha256=hashlib.sha256(tail).hexdigest(),raw_runtime_unchanged=True,source_sha256=sha(Path(__file__)),physical_access=False),indent=2)+'\n')
print('Wait label corrected from exact compiled source; originals preserved')
