"""Copy retained exact qualified outputs to E; never build or modify originals."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path('/mnt/e/xwn329/retained-builds001')
assert not ROOT.exists(), 'Consumed output'
assert shutil.disk_usage('/mnt/c').free > 20 * 1024**3
assert shutil.disk_usage('/mnt/e').free > 2 * 1024**3
BASE = Path('/home/paul/xbox-windows-native/build')
INPUTS = {
    '720p-default.xbe': (BASE/'hd-loader311-build001/candidate001/xbe/xromwell.xbe', 'c2bd899182caf0f076f8999feac1f48457fc4e6ad201ec358c06781f5740945f'),
    '1080i-default.xbe': (BASE/'hd-interlace316-build001/candidate001/xbe/xromwell.xbe', 'bd8e58f2e1c934074b15d3df1208f9caa7acb22243325083f26a7fe9fd30daf6'),
    'xwnown.dll': (BASE/'hd-surface303-build003/candidate001/win32ss/drivers/displays/framebuf/xwnown.dll', 'b23b94ac12c9f507e3d905d9de905dcff9a8fd53c2fba4336fb830e97666101d'),
    'xemu-hd322.exe': (Path('/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet/build/qemu-system-i386w.exe'), 'ea3473314e6c0ea068de4202cde46b1405da7553240cadea738c29c16d74c7a3'),
}

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

for source, expected in INPUTS.values():
    assert sha(source) == expected, source
ROOT.mkdir(parents=True)
rows = []
for name, (source, expected) in INPUTS.items():
    target = ROOT/name
    with source.open('rb') as src, target.open('xb') as dst:
        shutil.copyfileobj(src, dst)
    assert sha(target) == sha(source) == expected
    rows.append(dict(source=str(source), destination=str(target), bytes=target.stat().st_size, sha256=expected))
result = dict(passed=True, copies=rows, rebuilt=False, guest_launched=False, physical_access=False)
(ROOT/'receipt.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
