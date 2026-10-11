"""Fresh build004, explicitly fix both immutable parent paths after renaming."""
from pathlib import Path
k=Path(__file__).resolve().parent
s=(k/'build003.py').read_text(encoding='utf-8').replace('build003','build004').replace('candidate003-source-pins','candidate004-source-pins')
s=s.replace("prior/'artifacts/build004/source'","prior/'artifacts/build001/source'")
assert "prior/'candidate001-source-pins.json'" in s and "prior/'artifacts/build001/source'" in s
(k/'build004.py').write_text(s,encoding='utf-8')
s=(k/'Build003.ps1').read_text(encoding='utf-8').replace('build003','build004');(k/'Build004.ps1').write_text(s,encoding='utf-8')
for name in ['Run.ps1','test-consume.py','freeze.py']:
 p=k/name;s=p.read_text(encoding='utf-8').replace('build003','build004').replace('candidate003-source-pins','candidate004-source-pins');p.write_text(s,encoding='utf-8')
s=(k/'test-inventory003.py').read_text(encoding='utf-8').replace('build003','build004').replace('test003','test004');(k/'test-inventory004.py').write_text(s,encoding='utf-8')
