"""Pin the new combined test and inherited parser/cold-I/O sources before launch."""
import ast
import hashlib
import json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
dest=k/'emulator-frozen.json';assert not dest.exists()
files=list(k.glob('*.py'))+list(k.glob('*.ps1'))+list(k.glob('*.c'))+list(k.glob('*.h'))
files += [k/'emu001/fixture.json',k/'emu001/binding-edit.json',k/'runner-build001.json',k/'runner-source.json']
for folder in ['video-text-oracle206','fatx-mapped-eof','native-windows-paint-save','native-windows-fatx-runtime','setup-wizard-automation201','gpu-reset-banner152']:
    files+=list((ws/'outputs'/folder).glob('*.py'))
files += [ws/'outputs/native-windows-physical-f/decode-legacy-events.py',ws/'outputs/native-windows-prebuild/monitor_capture.py']
pins={}
for p in files:
    if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
    pins[p.relative_to(ws).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
dest.write_text(json.dumps(pins,indent=2)+'\n')
print('Frozen sources and prepared fixture:',len(pins))
