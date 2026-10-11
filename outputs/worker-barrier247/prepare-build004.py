"""Fresh corrected enum build; preserve compiled003 failure/source capsule."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;assert not (k/'build004.py').exists()
read=lambda p:json.loads(p.read_text())
assert not read(k/'build003.json')['passed'] and read(k/'build003.json')['borrowed_sources_restored']
(k/'build003-failure.json').write_text(json.dumps(dict(error='Incorrect renderer enum; parent uses CONFIG_DISPLAY_RENDERER_OPENGL',log='outputs/worker-barrier247/build001.log',log_sha256=hashlib.sha256((k/'build001.log').read_bytes()).hexdigest(),capsule='E:/Codex-archive/xbox-windows-native/phase247-build003',guest_launch=False),indent=2)+'\n')
s=(k/'build003.py').read_text().replace('build003','build004').replace('candidate003-source-pins','candidate004-source-pins').replace('delta003.patch','delta004.patch').replace("k/'build001.log'","k/'build004.log'")
(k/'build004.py').write_text(s)
for name in ['Run.ps1','freeze.py','test-worker.py']:
 p=k/name;p.write_text(p.read_text().replace('artifacts/build003','artifacts/build004').replace('build003.json','build004.json'))
(k/'Build004.ps1').write_text((k/'Build003.ps1').read_text().replace('/build003.py','/build004.py'))
print('Corrected004 enum,003 failure preserved')
