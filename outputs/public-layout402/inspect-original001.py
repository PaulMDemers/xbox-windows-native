import json,struct,hashlib
from pathlib import Path
old=Path('/home/paul/xbox-windows-native/build/fatx-enumeration390-001/out/drivers/filesystems/vfatfs/vfatfs.sys')
new=Path('/home/paul/xbox-windows-native/build/public-layout402-fatx001/artifacts/xwnfatx.sys')
root=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
# Discover the recorded artifact path instead of assuming the build directory name.
record=json.loads((root/'outputs/fatx-enumeration390/build-report.json').read_text())
print(json.dumps({k:v for k,v in record.items() if any(s in k for s in ['artifact','output','binary'])},indent=2))
print('candidate_old_exists',old.exists())
