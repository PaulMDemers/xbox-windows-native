"""Source-only clock harness update from independently inspected782 disassembly."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;O=K.parent/'vertical-sync-start780/clock_model002.py'
s=O.read_text().replace('780','782').replace('clock-model002.json','clock-model001.json')
s=s.replace('899424740c0000898424700c0000','899424640d0000898424600d0000').replace('0x208c70','0x208d60').replace('0x208c78','0x208d68')
with (K/'clock_model.py').open('x',newline='\n') as f:f.write(s)
with (K/'clock-lineage001.json').open('x') as f:json.dump({'source_sha256':hashlib.sha256(O.read_bytes()).hexdigest(),'reason':'400-word result and copied words grow main stack; actual objdump shows locals esp+d60/d64, instruction offsets unchanged','runtime_reused':False},f,indent=2)
