"""Derive review and audit, with fresh bundle schema. No console access."""
from pathlib import Path
import re
K=Path(__file__).resolve().parent;O=K.parent/'crtc-linecompare-low812'
for n in ['controller_review003.py','audit_collection002.py']:
 s=(O/n).read_text();parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 s=''.join(re.sub(r'^0x812(?=[0-9a-f]{0,2}$)','0x814',p) if i%2 else p.replace('812','814') for i,p in enumerate(parts))
 s=s.replace('review003.json','review001.json').replace('model005.json','prefix001.json').replace('controller-review003.json','controller-review001.json')
 if n=='controller_review003.py':n='controller_review001.py'
 else:
  n='audit_collection001.py';s=s.replace("out=K/'audit002.json'","out=K/'audit001.json'")
  s=s.replace('crtc_linecompare_low_control','crtc_mode_controls').replace('len(v)==820','len(v)==917')
  s=s.replace('horizontal_prefix_seven_vertical_words_diagnostic=True','four_remaining_controls_kernel_only=True')
 (K/n).write_text(s)
print('814 controller review and audit prepared')
