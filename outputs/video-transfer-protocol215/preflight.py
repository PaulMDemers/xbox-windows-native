"""Explain why the retained observed fixture cannot satisfy submission authority."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'preflight.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
a=read(ws/'outputs/video-gpu-state214/state-observations.json');r=read(k/'review.json')
assert a['passed'] and r['passed'] and not a['gpu_ownership_proven']
out=dict(passed=True,source_sha256=sha(Path(__file__)),review_sha256=sha(k/'review.json'),
 observations_sha256=sha(ws/'outputs/video-gpu-state214/state-observations.json'),
 submission_authorized=False,guest_launch=False,physical_access=False,
 current_control_mapping_bytes=0x681000,required_model_regions=dict(pramin_start=0x700000,user_start=0x800000),
 observed_channels=dict(pfifo=a['observations'][0]['model_bits']['cache1_channel_id'],pgraph=a['observations'][0]['model_bits']['pgraph_context_channel_id']),
 missing_contracts=['No proven resident DMA/command/completion allocations for this protocol.',
  'No instance-region ownership grant or proven physical PRAMIN backing/reservation.',
  'No exclusive quiescent context grant, context-valid/debug state or software context-switch handler.',
  'No mappings for PRAMIN/USER, actual NT5 DMA-address/ordering adapter or completion visibility proof.',
  'No verified global token namespace, serialization, bounded worker/crash drain or restoration witness.'],
 known_limits=['xemu independently backs RAMIN; hardware alias remains unresolved.',
  'Model ignores DMA classes/targets and uses limit without plus1; host success cannot validate hardware descriptor ABI.',
  'Model blit performs CPU copies; no GPU speed conclusion.',
  'Original physical baseline and strict Ftdisk49 gates remain unchanged.'],
 limits='This is a refusal of GPU submission based on actual source and prior observations, not a guest failure or a prompt for permission. Continue resolving concrete contracts.')
dest.write_text(json.dumps(out,indent=2)+'\n');print('Retained fixture submission held: actual ownership/address/drain contracts are missing.')
