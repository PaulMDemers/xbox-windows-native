"""Record exact installed FATX source leads without changing a driver."""
import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=read(W/'outputs/fatx-directory-order/build-report.json')
capsule=read(W/'outputs/fatx-enumeration388/source001.json')
baseline=read(K/'baseline001.json')['critical']['/E/winnt/system32/drivers/xwnfatx.sys']
assert baseline['sha256']==capsule['binary_sha256']==build['artifacts'][0]['sha256']
assert capsule['source_tree']==build['verified_source_tree']
for name,v in capsule['files'].items():assert sha(Path(capsule['private_capsule'])/name)==v['sha256']
root='/home/paul/xbox-windows-native/build/fatx-directory-order-001/source'
assert subprocess.check_output(['wsl','-d','Ubuntu','--','git','-C',root,'write-tree'],text=True).strip()==capsule['source_tree']
assert not subprocess.check_output(['wsl','-d','Ubuntu','--','git','-C',root,'diff','--name-only'])
r={'physical_access':False,'driver_changed':False,'installed_driver_sha256':baseline['sha256'],
 'exact_source_tree':capsule['source_tree'],'source_path':root,'source_only_reuse':True,
 'findings':[
  'vfatMakeRootFCB publishes one cluster for FATX root FileSize, ValidDataLength and AllocationSize.',
  'NextCluster, OffsetToCluster and read/write paths treat FirstCluster1 as a fixed FAT12/16 root, including FATX.',
  'FATXGetNextDirEntry checks requested page offset against RFCB.FileSize before CcMapData. Therefore root truncation alone does not establish the observed bugcheck path.',
  'Photo fault is MmMapViewInSystemCache+0xfb reading [edi+0x18] after following [edi+0x1c]; bugcheck address18 implies EDI zero at this instruction.',
  'Historical rename-boundary004 reached the identical instruction with invalid cache offsetfffff000 through FATXDelEntry; this is a comparison only, not evidence that836 has the same caller.',
 ],'next':[
  'Authenticate dashboard after user power off/on, collect836 once and preserve installed metadata/binary changes before repair.',
  'Establish offending cache operation and file/offset using retained logs or a fresh bounded diagnostic/reproduction before attributing this crash to root sizing.',
  'Any FATX root-chain candidate must cover root size, cluster dispatch, read/write routing and cache extent consistently; preserve FAT12/16 fixed roots and validate fragmented root handling.',
 ],'evidence_limit':'No physical kernel dump or call stack. No candidate driver built or deployed. Fixed720p retained boot reached Windows kernel; desktop not reached.'}
(K/'storage-review001.json').write_text(json.dumps(r,indent=2)+'\n')
note='''Source review836: exact installed FATX build8e12297c/binaryba62acbb confirmed.
Root-size and FirstCluster1 fixed-root assumptions are real source limitations,
but FATX enumeration bounds its cache maps. They do not by themselves establish
the STOP0A cause. Historical same-PC rename failure used invalid cache offset;
836 has no stack/offset capture. No driver patched/built/deployed. Next collect
836 after authenticated dashboard return, preserve file/log changes, then obtain
an offending operation/offset or controlled reproducer. See storage-review001.json.

'''
for p in [K/'NEXT.md',W/'outputs/engineering-notes/CONTINUATION.md',W/'outputs/engineering-notes/STATUS.md',W/'docs/current-status.md']:p.write_bytes(note.encode()+p.read_bytes())
print('Exact installed FATX source reviewed; no driver mutation or launch')
