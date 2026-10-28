"""Source-only clock harness update using independently inspected784 disassembly."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;O=K.parent/'vertical-sync-end782/clock_model.py'
s=O.read_text().replace('782','784')
s=s.replace('899424640d0000898424600d0000','899424540e0000898424500e0000').replace('0x208d60','0x208e50').replace('0x208d68','0x208e58')
with (K/'clock_model.py').open('x',newline='\n') as f:f.write(s)
with (K/'clock-lineage001.json').open('x') as f:json.dump({'source_sha256':hashlib.sha256(O.read_bytes()).hexdigest(),'reason':'430-word result and copied words grow main stack; independently inspected objdump shows locals esp+e50/e54, instruction offsets unchanged','runtime_reused':False},f,indent=2)
