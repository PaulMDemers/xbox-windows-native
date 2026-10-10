"""Freeze one new prepared225 child and all actual executable/source dependencies."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'emulator-frozen.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
pins=read(k.parent/'video-fifo-retirement224/emulator-frozen.json')
for name,h in pins.items():assert sha(ws/name)==h,name
assert read(k/'inventory002.json')['passed'] and read(k/'fixture-trace001.json')['prepared']
for p in k.iterdir():
 if p.is_file() and p.suffix in ['.py','.ps1','.md','.json']:
  if p.suffix=='.py':ast.parse(p.read_text(),filename=str(p))
  pins[str(p.relative_to(ws)).replace('\\','/')]=sha(p)
for row in read(k/'inventory002.json')['binaries'].values():
 p=ws/row['path'];assert sha(p)==row['sha256'];pins[row['path'].replace('\\','/')]=sha(p)
f=read(k/'fixture-trace001.json');assert sha(Path(f['fixture_path_windows']))==f['fixture_sha256'] and not f['inherited_null_policy']
for name,key in [('E/Applications/XWNFBoot/default.xbe','xromwell.xbe'),('E/Applications/XWNFBoot/freeldr.sys','freeldr.sys')]:
 assert f['files'][name]==read(k/'inventory002.json')['binaries'][key]['sha256']
assert set(read(k/'inventory002.json')['sites'])=={'producer_exit_entry','usb_stopped','interrupts_revoked','multiboot_transfer','freeldr_entry'}
# Runtime kit must preserve exact native namespace and the reviewed binaries.
assert f['files']['F/xwnret224/resident.sys']==read(k.parent/'video-fifo-retirement224/build-review002.json')['binaries']['candidate001']['sha256']
assert 'g.write(' not in (k/'trace.py').read_text() and 'ordinary_qualified=False' in (k/'audit-emulator.py').read_text()
dest.write_text(json.dumps(pins,indent=2)+'\n');print('Frozen225 inputs',len(pins))
