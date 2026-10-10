"""Read-only native build dependency/library and exact production-helper pins."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'native-input-review.json'
assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=read(k/'build001.json');assert r['status']=='compiled';checked=0
def pin(p,digest):
 global checked
 assert sha(p)==digest,str(p);checked+=1
art=k/'artifacts/build001';old=Path('/home/paul/xbox-windows-native/build/video-shared-framebuffer-001/candidate001')
src=old.parent/'source';ros=Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1')
pin(ros/'i386/bin/i686-w64-mingw32-gcc',r['compiler_sha256'])
pin(old/'host-tools/bin/pefixup',r['pefixup_sha256'])
for name,digest in r['dependency_pins'].items():pin(Path(name),digest)
for name,digest in r['copied_inputs'].items():pin(art/'inputs'/name,digest)
for name,row in r['materialized_thin'].items():
 pin(art/'inputs'/Path(name).parent/('regular-'+Path(name).name),row['regular_sha256'])
 pin(ros/'i386/bin/i686-w64-mingw32-ar',row['ar_sha256'])
 pin(ros/'i386/bin/i686-w64-mingw32-ranlib',row['ranlib_sha256'])
 for number,(original,digest) in enumerate(row['members'].items()):
  pin(art/'thin-members'/str(number)/Path(original).name,digest)
mini=art/'source/win32ss/drivers/miniport/xboxvmp/nt5'
pin(mini/'gpu_snapshot.c',r['source_pins']['new/gpu_snapshot.c'])
pin(mini/'registers.h',r['source_pins']['new/registers.h'])
assert (mini/'gpu_snapshot.c').read_bytes()==(k/'gpu_snapshot.c').read_bytes()
assert (mini/'registers.h').read_bytes()==(k/'registers.h').read_bytes()
original=src/'win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.c'
pin(original,r['source_pins']['win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.c'])
text=original.read_text();needle='    V->Ready = TRUE;'
text=text.replace(needle,'    { VOID NTAPI XgnSnapshot(PVOID,ULONG,ULONG); XgnSnapshot(V->Control,0x681000,0); }\n'+needle)
needle='            Result.FrameBufferBase = Result.VideoRamBase;'
text=text.replace(needle,'            { VOID NTAPI XgnSnapshot(PVOID,ULONG,ULONG); XgnSnapshot(V->Control,0x681000,1); }\n'+needle)
assert (mini/'xboxvnt5.c').read_text()==text
assert sha(art/'control001/main.obj')==sha(art/'candidate001/main.obj')
for row in r['builds']:pin(art/row['case']/'xboxvnt5.sys',row['sha256'])
for root,filename in [(k,'host-tests001.json')]:
 h=read(root/filename);assert h['passed']
 for name,digest in h['source_pins'].items():pin(root/name,digest)
 for row in h['runs']:pin(Path(row['command'][-1]),row['binary_sha256'])
result=dict(passed=True,checked_pins=checked,source_sha256=sha(Path(__file__)),build_sha256=sha(k/'build001.json'),
 main_object_sha256=sha(art/'control001/main.obj'),matched_common_miniport=True,
 physical_access=False,gpu_submission=False,
 limits='Read-only current recorded inputs/private copies, exact two observational hooks and matched common object.106 object/import-library donor,210-compatible base source; not a complete clean source reconstruction or DMA authority.')
dest.write_text(json.dumps(result,indent=2)+'\n');print('Native input/helper/library pins PASS:',checked)
