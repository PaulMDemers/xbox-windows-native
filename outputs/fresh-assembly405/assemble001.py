"""Fresh standard E assembly: clean404 media files + fresh403 builds + explicit settings."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/c/xwn405/assembly001');ROOT=Path('/mnt/c/xwn405/extract004/files')
sys.path.insert(0,str(W/'tools'));from build_space import require_space
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,sha,STARTUP
sys.path.insert(0,str(W/'outputs/release-readiness403'));from stock_io002 import scan
from writeio001 import WriteIO
assert not P.exists() and os.environ.get('XWN_BUILD_LEASE')=='held'
ex=json.loads((K/'extraction005.json').read_text());assert ex['status']=='extracted'
manifest=ROOT.parent/'files.json';assert sha(manifest)==ex['manifest_sha256']
files=json.loads(manifest.read_text());issues={v['path'] for v in ex['fatx_name_issues']}
payload={};origins={};excluded=[]
for row in files:
    n=row['path'];key=n.lower()
    if n in issues:
        excluded.append(dict(**row,reason='Explicit FATX component limitation; full original retained privately'));continue
    if '/' not in n:
        excluded.append(dict(**row,reason='PC boot/setup witness, not Xbox boot payload'));continue
    if key in ['winnt/system32/config/system.log','winnt/system32/config/software.log']:
        excluded.append(dict(**row,reason='Stale transaction log for explicitly changed offline hive'));continue
    m.Writer.parts(n);assert key not in payload
    payload[key]=(n,ROOT/n);origins[key]=dict(kind='clean404-installed-file',sha256=row['sha256'])
def add(name,source,kind,digest=None):
    key=name.lower();m.Writer.parts(name)
    if isinstance(source,Path):
        digest=digest or sha(source);assert sha(source)==digest
    else: digest=m.sha(source)
    payload[key]=(name,source);origins[key]=dict(kind=kind,sha256=digest)
provision=json.loads((K/'provision002.json').read_text())
for name in ['system','software']:add('WINNT/system32/config/'+name,Path('/mnt/c/xwn405/provision002')/name,'explicit fresh registry',provision['hives'][name]['result_sha256'])
builds=json.loads((W/'outputs/release-readiness403/build-verification002.json').read_text())
dest={'halxboxnt5.dll':'Applications/XWNEBoot/loader/halxboxnt5.dll','xboxbvid.dll':'Applications/XWNEBoot/loader/xboxbvid.dll',
 'xwnfatx.sys':'WINNT/system32/drivers/xwnfatx.sys','xboxvnt5.sys':'WINNT/system32/drivers/xboxvnt5.sys',
 'xwnown.dll':'WINNT/system32/xwnown.dll','nvnetnt5.sys':'WINNT/system32/drivers/nvnetnt5.sys',
 'xwnaci207.sys':'WINNT/system32/drivers/xwnaci207.sys','freeldr.sys':'Applications/XWNEBoot/freeldr.sys',
 'rosload.exe':'Applications/XWNEBoot/rosload.exe','default.xbe':'Applications/XWNEBoot/default.xbe'}
artifacts={}
for profile in builds['profiles']:
    for row in profile['artifacts']:
        p=Path('/home/paul/xbox-windows-native')/('release-readiness403-'+profile['profile']+'001')/'artifacts'/row['file']
        add(dest[row['file']],p,'fresh403 '+profile['profile'],row['sha256']);artifacts[row['file']]=p
media=json.loads((K/'media-inputs001.json').read_text())
for row in media['files']:
    name=row['name'];target='WINNT/system32/'+('drivers/' if name.endswith('.sys') else '')+name
    p=Path(row['selected']['path']);add(target,p,'same customized ISO input',row['selected']['sha256'])
add('XWN405/Audio/xwnaci207.sys',artifacts['xwnaci207.sys'],'fresh403 audio')
add('XWN405/Audio/xwnaci207.inf',W/'outputs/audio207/xwnaci207.inf','authored INF207')
add('XWN405/Network/nvnetnt5.sys',artifacts['nvnetnt5.sys'],'fresh403 network')
add('XWN405/Network/nvnetnt5.inf',W/'outputs/native-windows-nt5-kernel/nvnetnt5.inf','authored network INF')
video=(W/'outputs/video-nt5-display-package/xwnvideo.inf').read_bytes().replace(b'xwnfb',b'xwnown')
add('XWN405/Video/xwnvideo.inf',video,'authored INF with project-owned xwnown filename')
add('XWN405/Video/xwnown.dll',artifacts['xwnown.dll'],'fresh403 display')
add('XWN405/Video/xboxvnt5.sys',artifacts['xboxvnt5.sys'],'fresh403 framebuffer')
add('Applications/XWNEBoot/freeldr.ini',b'[XwnProbe]\r\nToken=XWN-SECOND-STAGE-20261003\r\n','generated loader preflight token')
add('Applications/XWNEBoot/probe.bin',bytes((i*37+(i>>8)+0x5a)&255 for i in range(131075)),'generated exact loader IO preflight')
add('WINNT/system32/xwn-video-trace.bin',(b'XWN-VID-TRACE01\n\0').ljust(4096,b'\0'),'fresh bounded trace seed')
probe=json.loads((K/'probe-build001.json').read_text());assert probe['exit_code']==0
add('XWN405/probe.exe',Path(probe['artifact']['path']),'fresh405 witness',probe['artifact']['sha256'])
add('XWN405/display-settings.exe',Path('/home/paul/xbox-windows-native/release-readiness403-settings001/display-settings.exe'),'fresh403 settings',builds['settings']['artifact']['sha256'])
add(STARTUP,b'@echo off\r\nC:\\XWN405\\probe.exe\r\n','one-shot emulator validation startup; not normal demo')
blank=Path('/mnt/c/Emulators/xemu/system/xbox_hdd.qcow2')
dashboard=Path('/mnt/e/xwn329/seed001/source.qcow2');pin=json.loads((W/'outputs/artifact-recovery329/seed001/fixture.json').read_text())
assert sha(dashboard)==pin['fixture_sha256']
logical=sum(p.stat().st_size if isinstance(p,Path) else len(p) for n,p in payload.values())
space=require_space(P,20+(logical+100*1024**2)/1024**3)
P.mkdir(parents=True);disk=P/'fresh.qcow2';r=dict(status='assembling',physical_access=False,old_windows_payload_used=False,
 source404_sha256=ex['source_sha256'],blank_sha256=sha(blank),dashboard_source_sha256=sha(dashboard),space=space,
 explicit_exclusions=excluded,files=[],sources=origins,logical_bytes=logical)
def save():(K/'assembly001.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
    subprocess.run(['qemu-img','convert','-O','qcow2',str(blank),str(disk)],check=True)
    subprocess.run(['qemu-img','resize',str(disk),'10000000000'],check=True)
    m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
    with WriteIO(disk,10000000000,P) as io,ColdIO(dashboard) as donor:
        # Only the owned emulator dashboard partition; no Windows donor content.
        start=4609024*512;length=1024000*512;dg=hashlib.sha256()
        for off in range(0,length,1024**2):
            n=min(1024**2,length-off);donor.seek(start+off);b=donor.read(n);dg.update(b)
            if b!=bytes(n):io.seek(start+off);io.write(b)
        io.flush();r['dashboard_partition_sha256']=dg.hexdigest()
        wr=m.Writer(io,m.fatx.open_partition(io,disk,'E'));assert set(wr.directory(1)['entries'])=={'tdata','udata'}
        roots={n:v[2].hex() for n,v in wr.directory(1)['entries'].items()}
        launcher='applications/xwneboot/default.xbe'
        for key in sorted(set(payload)-{launcher})+[launcher]:
            name,p=payload[key];b=p.read_bytes() if isinstance(p,Path) else p
            assert m.sha(b)==origins[key]['sha256'],name
            r['files'].append(wr.write(name,b))
            if len(r['files'])%1000==0:wr.flush();io.flush();print('Fresh files staged',len(r['files']),flush=True)
        wr.flush();io.flush();assert all(wr.directory(1)['entries'][n][2].hex()==v for n,v in roots.items())
    with ColdIO(disk) as io:
        wr=m.Writer(io,m.fatx.open_partition(io,disk,'E'))
        for row in r['files']:assert m.sha(wr.read(row['path']))==row['sha256'],row['path']
        dg=hashlib.sha256()
        for off in range(0,length,1024**2):io.seek(start+off);dg.update(io.read(min(1024**2,length-off)))
        assert dg.hexdigest()==r['dashboard_partition_sha256']
        io.seek(0);assert io.read(512)==bytes(512)
    r['qcow_check']=json.loads(subprocess.check_output(['qemu-img','check','--output=json',str(disk)]))
    scan(disk,K/'before-allocation/artifacts')
    assert json.loads((K/'before-allocation/allocation.json').read_text())['allocation_consistent']
    r.update(status='assembled-readback-verified',fixture_path_linux=str(disk),fixture_path_windows='C:'+str(disk)[6:],fixture_sha256=sha(disk),cold_files_verified=len(r['files']),factory_roots_preserved=True,
             strict_lossless_transfer=False,boot_qualified=False,final_space=require_space(P))
    assert sha(blank)==r['blank_sha256'] and sha(dashboard)==r['dashboard_source_sha256']
except BaseException as exc:r.update(status='failed',error=repr(exc));raise
finally:save()
print('Fresh assembly verified',len(r['files']),flush=True)
