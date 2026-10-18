"""Derive only ownership paths from the closed471 launcher tools; no execution."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;P=K.parent/'busy-handoff471';(K/'emu001').mkdir(exist_ok=False)
rows={}
for name in ['Invoke.ps1','Run001.ps1','start-owned.ps1','protocol003.py','close-host.py','protected001.py']:
 s=(P/name).read_text(encoding='utf-8')
 t=s.replace('xwn471','xwn502').replace('nt5-busy471','nt5-entry502').replace('windows-native-busy471','windows-native-entry502')
 for a,b in [('5714','6024'),('5715','6025'),('5716','6026'),('5717','6027')]:t=t.replace(a,b)
 (K/name).write_bytes(t.encode());rows[name]=dict(parent_sha256=hashlib.sha256((P/name).read_bytes()).hexdigest(),child_sha256=hashlib.sha256(t.encode()).hexdigest())
(K/'source-derivation001.json').write_bytes((json.dumps(rows,indent=2)+'\n').encode())
