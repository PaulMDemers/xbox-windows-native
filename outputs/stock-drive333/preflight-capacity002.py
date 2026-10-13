"""Pin every active harness dependency and media before launch."""
import hashlib,json,ast
from pathlib import Path
K=Path(__file__).resolve().parent;dest=K/'capacity-emu002/preflight.json';assert not dest.exists()
paths=[K/n for n in ['RunCapacity002.ps1','InvokeCapacity002.ps1','close-capacity002.py','observe-capacity002.py','audit-capacity003.py','capacity.c','capacity-build001.json']]
paths += [K.parent/'native-windows-prebuild/monitor_capture.py',K.parent/'surface-bridge260/atomic_json.py',K.parent/'gpu-reset-banner152/ftp_deadline.py']
paths += [Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts')/n for n in ['with_xbox_resource.ps1','start_xemu_instance.ps1','complete_xemu_instance.ps1']]
paths += [Path('C:/Emulators/xemu/system/bios/Complex_4627.bin'),Path('C:/Emulators/xemu/system/mcpx/mcpx_1.0.bin'),Path('E:/xwn289/fixture001/hd.bin'),K.parent/'native-windows-extended-storage/artifacts/f-boot-length-004.iso',Path('E:/xwn329/retained-builds001/xemu-hd322.exe'),Path('E:/xwn333/capacity-emu001/source.qcow2')]
pins={}
for p in paths:
    assert p.is_file(),p
    if p.suffix=='.py':ast.parse(p.read_text())
    with p.open('rb') as f:pins[str(p.resolve())]=hashlib.file_digest(f,'sha256').hexdigest()
f=json.loads((K/'capacity-emu001/fixture.json').read_text());assert pins[str(Path(f['fixture_path_windows']).resolve())]==f['fixture_sha256']
assert 'close-capacity002.py' in (K/'InvokeCapacity002.ps1').read_text()
assert 'port==5113' in (K/'close-capacity002.py').read_text()
dest.write_text(json.dumps(dict(passed=True,pins=pins,control_channel_only=True,physical_access=False),indent=2)+'\n')
print('All active host dependencies and media pinned')
