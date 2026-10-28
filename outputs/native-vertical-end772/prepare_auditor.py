"""Prepare local-only collection auditor; no closed runtime access."""
from pathlib import Path
K=Path(__file__).resolve().parent
s=(K.parent/'native-crtc-stridelow770/audit_collection.py').read_text().replace('770','772').replace('payload001','payload002')
s=s.replace('[0x80,0x68,0x80]','[719,479,719]').replace('native_CR13','native_NVVDISPEND')
p=K/'audit_collection.py';assert not p.exists();p.write_text(s,newline='\n')
print('Prepared772 local-only collection auditor')
