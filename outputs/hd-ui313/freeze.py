"""Pin the new combined test and inherited parser/cold-I/O sources before launch."""
import ast
import hashlib
import json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
dest=k/'emulator-frozen.json';assert not dest.exists()
files=list(k.glob('*.py'))+list(k.glob('*.ps1'))+list(k.glob('*.c'))+list(k.glob('*.h'))+list(k.glob('*.inc'))
files += [k/'build001.json',k/'build-review001.json',k/'source-review001.json']
files += [k/'candidate001/fixture.json',ws/'outputs/hd-reservation300/binary-review001.json',ws/'outputs/hd-reservation300/source-review002.json',ws/'outputs/surface-bridge260/atomic_json.py']
for folder in ['video-text-oracle206','fatx-mapped-eof','native-windows-paint-save','native-windows-fatx-runtime','setup-wizard-automation201','gpu-reset-banner152']:
    files+=list((ws/'outputs'/folder).glob('*.py'))
files += [ws/'outputs/hd-surface303/binary-review003.json',ws/'outputs/hd-surface303/build003.json',ws/'outputs/hd-surface303/source-review003.json',ws/'outputs/hd-surface303/host001.json',ws/'outputs/hd-surface303/0119-hd-surface-bounds003.patch']
files += list((ws/'outputs/hd-loader311').glob('*.json'))+list((ws/'outputs/hd-loader311').glob('*.c'))+list((ws/'outputs/hd-loader311').glob('*.h'))+list((ws/'outputs/hd-loader311').glob('*.py'))+list((ws/'outputs/hd-loader311/integrated').glob('*'))
files += [k/'profile.json']+list((ws/'outputs/hd-reservation300').glob('*.patch'))+[ws/'outputs/hd-reservation300/build001.json',ws/'outputs/hd-reservation300/host001.json']
files += [ws/'outputs/native-windows-physical-f/decode-legacy-events.py',ws/'outputs/native-windows-prebuild/monitor_capture.py']
pins={}
for p in files:
    if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
    pins[p.relative_to(ws).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
dest.write_text(json.dumps(pins,indent=2)+'\n')
print('Frozen sources and prepared fixture:',len(pins))

host=Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts')
(k/'host-frozen.json').write_text(json.dumps({str(host/n):hashlib.sha256((host/n).read_bytes()).hexdigest() for n in ['start_xemu_instance.ps1','complete_xemu_instance.ps1','with_xbox_resource.ps1','lib/xemu_instance.ps1','lib/test_storage.ps1']},indent=2)+'\n')

hostpins=json.loads((k/'host-frozen.json').read_text());eeprom=Path('E:/xwn289/fixture001/hd.bin');hostpins[str(eeprom)]=hashlib.sha256(eeprom.read_bytes()).hexdigest();(k/'host-frozen.json').write_text(json.dumps(hostpins,indent=2)+'\n')
