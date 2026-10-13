import hashlib,json,subprocess,sys
from pathlib import Path
assert sys.platform=='linux'
K=Path(__file__).resolve().parent;W=K.parents[1];dest=K/'source-review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
current=read(K.parent/'eligible-physical353/candidate001/final-state.json')['files']
build=read(K/'build001.json');parent=read(K.parent/'eligible-copy351/build001.json')
source=Path('/home/paul/xbox-windows-native/build/memory-state354-build001/source')
changed=subprocess.check_output(['git','-C',str(source),'diff','--name-only',parent['source_tree'],build['source_tree']],text=True).splitlines()
prefix='win32ss/drivers/displays/framebuf/'
assert set(changed)=={prefix+n for n in ['CMakeLists.txt','enable.c','framebuf.h','capture.h','memory_state.c']}
assert not subprocess.check_output(['git','-C',str(source),'diff','--name-only'])
unchanged=['surface.c','shadow.c','ownership.c','primary_copy.c','primary_plan.h','row_store.h']
for n in unchanged:
 data=(source/prefix/n).read_bytes();assert sha(data)==parent['source_files'][prefix+n]
capsule=Path('/mnt/e/xwn354/source-review001');capsule.mkdir()
hd=Path('/home/paul/xbox-windows-native/build/hd-reservation300-build001/source')
hdreview=read(K.parent/'hd-reservation300/final-review.json');hdbuild=read(K.parent/'hd-reservation300/build001.json')
paths=['drivers/base/bootvid/i386/xbox/bootvid.c','drivers/base/bootvid/xwn_fb.c','drivers/base/bootvid/xwn_fb.h','win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.c','win32ss/drivers/miniport/xboxvmp/nt5/video_shared.c','sdk/include/reactos/drivers/xbox/xwn_hd_layout.h']
pins={}
for n in paths:
 data=(hd/n).read_bytes();expected=subprocess.check_output(['git','-C',str(hd),'show',hdreview['source_trees']['reactos']+':'+n]);assert data==expected
 target=capsule/n;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);pins[n]=sha(data)
for n,remote in [('xboxvnt5.sys','/E/winnt/system32/drivers/xboxvnt5.sys'),('xboxbvid.dll','/E/Applications/XWNEBoot/loader/xboxbvid.dll')]:
 data=(Path('/mnt/e/xwn300/build001/candidate001')/n).read_bytes();assert sha(data)==current[remote]['sha256']
surface=read(K.parent/'hd-surface303/build003.json');assert surface['cases']['candidate001']['sha256']==current['/E/winnt/system32/xwnown.dll']['sha256']
assert hdbuild['cases']['candidate001']['definitions']['XBOX_NT5_HD_RESERVATION']=='ON'
r=dict(passed=True,changed=changed,unchanged_draw_upload_mapping_lifetime=unchanged,
 installed_baseline=dict(display303=current['/E/winnt/system32/xwnown.dll'],miniport300=current['/E/winnt/system32/drivers/xboxvnt5.sys'],bootvid300=current['/E/Applications/XWNEBoot/loader/xboxbvid.dll']),
 installed_mapping_source_tree=hdreview['source_trees']['reactos'],mapping_source_pins=pins,
 experimental_parent_tree=parent['source_tree'],experimental_tree=build['source_tree'],
 exact_installed_chain='303 surface IOCTL_VIDEO_MAP_VIDEO_MEMORY ->300 miniport XwnSharedMap ->300 bootvid XwnFbAcquire -> permanent MmMapIoSpace(...,MmNonCached); private ShadowBits EngAllocMem(FL_ZERO_MEMORY).',
 limits='Source/API intent and last353 installed hashes, not live354 PTE/cache state. The351 tree contains unrelated older bootvid files; those were NOT used as installed mapping evidence. Historical0094 observed obsolete GPU-aperture mapping; no transfer of its cache result to current hardware.',
 observations_only=True,physical_access=False,guest_launch=False)
dest.write_text(json.dumps(r,indent=2)+'\n');print('Installed mapping lineage and exact354 read-only source delta verified')
