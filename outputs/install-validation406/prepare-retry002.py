"""Record pre-mutation space refusal, allocate a distinct preparation ID."""
import json
from pathlib import Path
K=Path(__file__).resolve().parent
with (K/'stage001-refusal.json').open('x') as f:json.dump(dict(stage='preflight',created_disk=False,guest_launched=False,reason='C backing volume 21267304448 bytes; required 21491613696',no_gate_change=True),f,indent=2)
s=(K/'stage001.py').read_text().replace('assembly001','assembly002')
with (K/'stage002.py').open('x',newline='\n') as f:f.write(s)
for name in ['Run001.ps1','Invoke001.ps1']:
    p=K/name;p.write_text(p.read_text().replace('assembly001','assembly002'),newline='\n')
