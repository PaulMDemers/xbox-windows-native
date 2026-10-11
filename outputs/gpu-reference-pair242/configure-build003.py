"""002 stopped before source borrowing: preserve path-generation failure."""
import json
from pathlib import Path
k=Path(__file__).resolve().parent
assert not (k/'build002.json').exists()
assert not Path('E:/Codex-archive/xbox-windows-native/phase242-build002').exists()
s=(k/'build002.py').read_text(encoding='utf-8').replace('build002','build003').replace('candidate002-source-pins','candidate003-source-pins')
s=s.replace("prior/'candidate003-source-pins.json'","prior/'candidate001-source-pins.json'")
(k/'build003.py').write_text(s,encoding='utf-8')
s=(k/'Build002.ps1').read_text(encoding='utf-8').replace('build002','build003');(k/'Build003.ps1').write_text(s,encoding='utf-8')
for name in ['Run.ps1','test-consume.py','freeze.py']:
 p=k/name;s=p.read_text(encoding='utf-8').replace('build002','build003').replace('candidate002-source-pins','candidate003-source-pins');p.write_text(s,encoding='utf-8')
s=(k/'test-inventory002.py').read_text(encoding='utf-8').replace('build002','build003').replace('test002','test003')
(k/'test-inventory003.py').write_text(s,encoding='utf-8')
(k/'setup-failure002.json').write_text(json.dumps(dict(stage='build002 preparation',error='Generator rewrote prior241 candidate001 source manifest to nonexistent candidate002',compiler_started=False,sources_borrowed=False,artifact_directory_created=False,guest_launch=False,repeat=False,next='unique build003'),indent=2)+'\n',encoding='utf-8')
