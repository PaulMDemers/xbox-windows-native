"""Exact owned closed portable protocol for247/248, backing chains unchanged."""
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'portable-offload.ps1';assert not dest.exists()
s=(k.parent/'frontend-close246/portable-offload.ps1').read_text()
s=s.replace('closed-portable-246','closed-portable-247248').replace('foreach($phase in 246)','foreach($phase in 247,248)').replace('outputs/frontend-close246/portable-offload001.json','outputs/worker-barrier248/portable-offload001.json').replace('Closed246 portable','Closed247/248 portables')
dest.write_text(s);print('Closed portable offload protocol prepared, source boundaries/readback retained')
