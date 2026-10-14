"""Import exact maintained overlays from the independently replayed401 object stores."""
import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
old=json.loads((W/'outputs/public-source401/export/components.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
mapping={'fatx390':('fatx','src/drivers/fatx'),'hd300':('framebuffer','src/drivers/video/framebuffer'),
 'boot-e334':('loader','src/boot/loader'),'display303':('display','src/drivers/video/display'),
 'launcher-e720p374':('launcher','src/boot/xromwell'),'audio004':('audio','src/drivers/audio')}
artifacts={
 'fatx':{'drivers/filesystems/vfatfs/vfatfs.sys':'xwnfatx.sys'},
 'framebuffer':{'win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.sys':'xboxvnt5.sys','drivers/base/bootvid/xboxbvidnt5.dll':'xboxbvid.dll'},
 'loader':{'boot/freeldr/freeldr/freeldr.sys':'freeldr.sys','boot/freeldr/freeldr/rosload.exe':'rosload.exe'},
 'display':{'win32ss/drivers/displays/framebuf/xwnown.dll':'xwnown.dll'},
 'launcher':{'xbe/xromwell.xbe':'default.xbe'},
 'audio':{'drivers/wdm/audio/drivers/ac97/ac97xnt5.sys':'xwnaci207.sys'}}
if (W/'src').exists() or (W/'upstream').exists():raise RuntimeError('Import requires fresh src and upstream')
(W/'src').mkdir();(W/'upstream').mkdir()
profiles=[];report=[]
for c in old['components']:
    name,overlay=mapping[c['name']];repo=Path('/mnt/c/xwn401/reconstruct001')/c['name']
    def git(*args):return subprocess.check_output(['git','-C',str(repo),*args])
    entries=[]
    changes=git('diff','--name-only','--no-renames','-z',c['base_commit'],c['result_tree']).split(b'\0')
    for raw in changes:
        if not raw:continue
        path=raw.decode();listing=git('ls-tree',c['result_tree'],'--',path).decode().strip()
        if not listing:entries.append(dict(path=path,action='delete'));continue
        header,_=listing.split('\t',1);mode,kind,oid=header.split()
        if kind!='blob' or mode not in ('100644','100755'):raise RuntimeError('Unsupported source entry')
        data=git('cat-file','blob',oid)
        if b'\0' in data:raise RuntimeError('Binary source entry')
        dest=W/overlay/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        entries.append(dict(path=path,action='write',mode=mode,sha256=sha(data)))
    build=c['build']
    if name=='framebuffer':
        if build['targets']!=['xboxvnt5','xboxbvid']:raise RuntimeError('Unexpected401 target')
        build['targets']=['xboxvnt5','xboxbvidnt5']
    profiles.append(dict(name=name,upstream='cromwell' if name=='launcher' else 'reactos',
        base_commit=c['base_commit'],reference_tree=c['result_tree'],overlay=overlay,files=entries,
        build=build,artifacts=artifacts[name],checkout_byte_rules=c['checkout_byte_rules']))
    report.append(dict(profile=name,source_tree=c['result_tree'],entries=len(entries)))
    print(name,len(entries),flush=True)
(W/'upstream/components.json').write_text(json.dumps(dict(schema=1,profiles=profiles,
    rosbe_tool_pins=old['rosbe_tool_pins'],locations=old['upstream_locations_as_recorded'],
    scope='Maintained source overlays, one independent upstream tree per profile; not a complete OS installer'),indent=2)+'\n')
utility=W/'src/utilities/display-settings';utility.mkdir(parents=True)
(utility/'settings.c').write_bytes((W/'outputs/demo-settings376/settings.c').read_bytes())
licenses=W/'LICENSES';licenses.mkdir()
for p in (W/'outputs/public-source401/export/licenses').rglob('*'):
    if p.is_file():
        dest=licenses/p.relative_to(W/'outputs/public-source401/export/licenses');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
(K/'import001.json').write_text(json.dumps(dict(profiles=report,physical_access=False,
    exception='Corrected framebuffer build target xboxbvid to actual xboxbvidnt5; source bytes unchanged'),indent=2)+'\n')
