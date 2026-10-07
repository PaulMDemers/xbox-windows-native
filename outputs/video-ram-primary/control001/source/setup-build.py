"""Adapt the pinned reconstruction pipeline; no guest launch."""
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'video-direct-ddi'
s=(old/'build.py').read_text().replace('Fresh direct-only display DDI','Fresh RAM-primary display DDI').replace('0107-direct-nt5-display.patch','0108-ram-primary.patch').replace('xwndir','xwnram')
needle="  assert subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()==review['parent_tree']"
assert s.count(needle)==1
s=s.replace(needle,"  run(['git','-C',str(src),'apply','--index',str(k.parent/'video-direct-ddi/0107-direct-nt5-display.patch')],stdout=log,stderr=log)\n"+needle)
(k/'build.py').write_text(s,newline='\n')
s=(old/'Build.ps1').read_text().replace('video-direct-ddi-002','video-ram-primary-001').replace('Fresh direct display','Fresh RAM-primary display')
(k/'Build.ps1').write_text(s,newline='\n')
s=(old/'verify-source.py').read_text().replace('video-direct-ddi-002','video-ram-primary-001').replace('0107-direct-nt5-display.patch','0108-ram-primary.patch')
(k/'verify-source.py').write_text(s,newline='\n')
