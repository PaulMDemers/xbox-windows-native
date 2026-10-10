"""Describe closed actual phase bytes; no timing, redundancy or speed inference."""
import hashlib,json,statistics
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'producer-analysis.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
results={};inputs={}
for scope in ['emulator','physical']:
 pair=k/(scope+'-pair-review.json');assert read(pair)['passed'];inputs[pair.name]=sha(pair)
 root=k/('emu-candidate001' if scope=='emulator' else 'candidate001')
 audit=root/('audit.json' if scope=='emulator' else 'physical-audit.json');a=read(audit)
 assert read(root/'closure.json')['closed'] and a['scoped_display_passed'] and read(root/'sequence-review.json')['passed']
 inputs[audit.relative_to(k).as_posix()]=sha(audit)
 inputs[(root/'sequence-review.json').relative_to(k).as_posix()]=sha(root/'sequence-review.json')
 phases={}
 for phase in ['move','paint','readback']:
  totals=read(pair)['candidate_phase_totals'][phase]
  total=sum(row['bytes'] for row in totals.values())
  actual=[sum(row['bytes'] for row in step['phases'][phase]) for sample in a['upload_samples'] for step in sample['steps']]
  assert len(actual)==200 and sum(actual)==total
  phases[phase]=dict(bytes=total,bytes_per_step=dict(min=min(actual),median=statistics.median(actual),max=max(actual)),
   null_request_bytes=sum(row['null_bytes'] for row in totals.values()),fallbacks=sum(row['fallbacks'] for row in totals.values()),
   producers={name:dict(**row,byte_share=(row['bytes']/total if total else 0)) for name,row in totals.items() if row['requests'] or row['bytes']})
 results[scope]=dict(steps=200,samples=5,phases=phases,
  scoped_pixels_passed=True,strict_whole_boot_passed=False,performance_qualified=False)
r=dict(passed=True,source_sha256=sha(Path(__file__)),input_pins=inputs,results=results,
 limits='Completed device-global uploads during 200 controlled phase windows per platform. Chrome/exposure/background included. Explicit bounds do not prove optimal bytes; NULL requests do not prove waste. No timings, FPS, application performance or generalized desktop claim.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(results,indent=2))
