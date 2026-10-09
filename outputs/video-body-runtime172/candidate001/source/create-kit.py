"""Fresh successor of host-blocked171; no reused launch or edited frozen code."""
import ast,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'video-body-runtime171';assert not (k/'Run.ps1').exists()
for p in list(old.glob('*.py'))+list(old.glob('*.ps1'))+[old/'gdi-probe.c',old/'DESIGN.md',old/'build-review.json']:
 if p.name=='create-kit.py':continue
 text=p.read_text().replace('video-body-runtime171','video-body-runtime172').replace('vbody171','vbody172').replace('xwnvt171','xwnvt172')
 text=text.replace("[ValidateSet('candidate001')]","[ValidateSet('control001','candidate001')]")
 if p.suffix=='.py':ast.parse(text)
 (k/p.name).write_bytes(text.encode())
shutil.copytree(old/'artifacts',k/'artifacts')
print('Fresh172; both PowerShell case validators corrected,171 preserved')
