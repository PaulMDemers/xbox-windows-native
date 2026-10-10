"""Adapt previously reviewed typed-state checks to preserved physical snapshots."""
from pathlib import Path
import json
k=Path(__file__).resolve().parent;src=k.parent/'audio207'
s=(src/'typed-state-install001.py').read_text()
s=s.replace('preserved emulator SYSTEM only','preserved physical SYSTEM only').replace("case in ['install001']","case in ['install001','playback001']")
rows=s.splitlines();matches=[i for i,line in enumerate(rows) if line.startswith('p={phase:')];assert len(matches)==1
rows[matches[0]]="roots={'before':k/'artifacts'/('before002' if case=='install001' else 'install001'),'after':k/'artifacts'/case}\np={phase:{'system':dict(path=str((root/'F/winnt/system32/config/system').relative_to(ws)),sha256=sha((root/'F/winnt/system32/config/system').read_bytes()))} for phase,root in roots.items()}"
s='\n'.join(rows)+'\n';s=s.replace('physical_observation=False,emulator_observation=True','physical_observation=True,emulator_observation=False')
assert not (k/'typed-state001.py').exists();(k/'typed-state001.py').write_text(s)
s=(src/'installed-binding001.py').read_text().replace("['install001','installed001']","['install001','playback001']").replace("out/'artifacts/after-system'","k/'artifacts'/case/'F/winnt/system32/config/system'")
assert not (k/'installed-binding001.py').exists();(k/'installed-binding001.py').write_text(s)
