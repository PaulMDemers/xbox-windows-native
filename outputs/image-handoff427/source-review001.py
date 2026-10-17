# SPDX-License-Identifier: MIT
"""Pin complete403 source paths and compare present public overlays read-only."""
from pathlib import Path
import hashlib
import json
import subprocess
K = Path(__file__).resolve().parent
R = K.parent.parent
assert not (K/'source-review001.json').exists()
spec = {
 'hal': {
  'hal/halx86/xbox/halinit.c': ['HalpInitPhase0(', 'HalpXboxInitPartIo();'],
  'hal/halx86/generic/halinit.c': ['HalInitSystem(', 'BootPhase == 0', 'HalpInitPhase0(LoaderBlock);'],
  'hal/halx86/xbox/part_xbox.c': ['HalpXboxIoReadPartitionTable(', 'PARTITION_SIGNATURE   0xaa55', 'HalIoReadPartitionTable = HalpXboxIoReadPartitionTable;', 'return STATUS_ACCESS_DENIED;'],
  'hal/halx86/generic/drive.c': ['IoAssignDriveLetters HALDISPATCH', 'return IoReadPartitionTable('],
  'hal/halx86/xboxnt5/fmutex.c': ['HalIoReadPartitionTable) == 0x1c'],
 },
 'loader': {
  'boot/freeldr/freeldr/ntldr/winldr.c': ['WinLdrInitializePhase1(', 'LoaderBlock->ArcBootDeviceName', 'LoaderBlock->ArcHalDeviceName', 'WinLdrLoadBootDrivers('],
  'boot/freeldr/freeldr/ntldr/wlregistry.c': ['BootFileSystem = FsGetServiceName(FileId);', 'CmpFindDrivers(', 'CmpSortDriverList(', 'CmpResolveDriverDependencies('],
  'boot/freeldr/freeldr/disk/disk.c': ['Signature = 0xAA55;', 'Checksum = ~Checksum + 1;', 'AddReactOSArcDiskInfo('],
  'boot/freeldr/freeldr/disk/part_brfr.c': ['DiskGetBrfrPartitionEntry(', 'Store , E:', 'System, C:'],
  'boot/freeldr/freeldr/lib/fs/fs.c': ['NtfsMount,'],
  'boot/freeldr/freeldr/lib/fs/ntfs.c': ['L"ntfs"', 'NtfsMount(ULONG DeviceId)', 'ArcRead(DeviceId'],
 }
}
trees = {profile: json.loads((R/'outputs/release-readiness403/compiled-records001'/profile/'source.json').read_text())['tree'] for profile in spec}
code = '''import sys,json,subprocess,hashlib
from pathlib import Path
spec=json.loads(sys.argv[1]); trees=json.loads(sys.argv[2]); rows=[]
for profile,files in spec.items():
 root=Path("/home/paul/xbox-windows-native/release-readiness403-"+profile+"001/source")
 for name,anchors in files.items():
  b=(root/name).read_bytes()
  assert b==subprocess.check_output(["git","-C",str(root),"show",trees[profile]+":"+name]),name
  lines=b.decode().splitlines()
  found={a:[i+1 for i,l in enumerate(lines) if a in l] for a in anchors}
  assert all(found.values()),(name,found)
  rows.append(dict(profile=profile,path=name,tree=trees[profile],sha256=hashlib.sha256(b).hexdigest(),recorded_tree_exact=True,anchors=found))
print(json.dumps(rows))
'''
rows = json.loads(subprocess.check_output(['wsl','-d','Ubuntu','--','python3','-B','-c',code,
                                          json.dumps(spec),json.dumps(trees)], text=True))
for row in rows:
    prefix = 'src/platform/nt5' if row['profile']=='hal' else 'src/boot/loader'
    p = R/prefix/row['path']
    if p.exists():
        actual = hashlib.sha256(p.read_bytes()).hexdigest()
        assert actual == row['sha256'], str(p)
        row['overlay'] = p.relative_to(R).as_posix()
        row['overlay_exact'] = True
    else:
        assert row['path'] == 'hal/halx86/xbox/halinit.c'
        row['overlay'] = None
        row['note'] = 'Inherited complete upstream file, absent from partial overlay'
others = ['outputs/fresh-assembly405/provision002.py',
          'outputs/native-windows-ntfs-shutdown/REPORT.txt',
          'outputs/native-windows-ntfs-shutdown/validation-002.json',
          'outputs/native-windows-physical-hooks/validation.json',
          'outputs/image-volume426/model.py']
result = dict(passed=True, sources=rows,
              context_only={n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in others},
              native_source_modified=False, old_runtime_recollected=False)
with (K/'source-review001.json').open('x',encoding='utf-8',newline='\n') as f:
    f.write(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(full_sources_exact=len(rows),public_overlays_exact=sum(bool(r.get('overlay_exact')) for r in rows))))
