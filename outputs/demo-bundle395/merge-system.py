"""Private E payload reconstruction from343 plus qualified376 demo add-on.
This is not a fresh console capture, generic installer or tested full restore.
"""
import hashlib,json,shutil,zipfile
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];O=Path('C:/xwn395/system001')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda b:hashlib.sha256(b).hexdigest()
assert not O.exists() and not (K/'system001.json').exists()
assert read(K.parent/'demo-runtime377/control001/audit.json')['scoped_combined_passed']
base=Path('E:/xwn343/bundle002/stock-e-1080i-001.zip');expected='e79771fbf5eaf10c3e30e80e0d04e622dfd443448e24fa4eb76deac01d1b3e83'
with base.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==expected
assert shutil.disk_usage('C:/').free-base.stat().st_size-128*1024**2>=20*1024**3
validation=read(K.parent/'fatx-physical394/candidate001/audit.json');assert read(K.parent/'fatx-physical394/candidate001/final-state.json')['closed'] and validation['diagnostic_workload_completed'] and validation['scoped_combined_passed'] and validation['cmd_persistence_passed'] and validation['tested_fatx_verified']
assert read(K/'accepted-state.json')['accepted']
O.mkdir(parents=True);pkg=read(K.parent/'demo-settings376/package001.json');P=Path(pkg['package_root'])
overrides={'payload/E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd':(P/'demo-startup.cmd').read_bytes()}
for n,v in pkg['files'].items():
    b=(P/n).read_bytes();assert sha(b)==v['sha256'];overrides['payload/E/xwndemo372/'+n]=b
launcher=Path('E:/xwn374/build001/default.xbe').read_bytes();assert sha(launcher)==read(W/'tools/e-display-policy.json')['profiles']['720p']['sha256']
overrides['payload/E/Applications/XWNEBoot/default.xbe']=launcher
fatx=Path('E:/xwn390/build001/xwnfatx.sys').read_bytes();assert sha(fatx)==read(K/'accepted-state.json')['candidate_sha256']
overrides['payload/E/winnt/system32/drivers/xwnfatx.sys']=fatx
out=O/'xwn-private-E-720p-demo-20261014.zip';manifest={}
def write(z,n,b):
    assert n not in manifest
    info=zipfile.ZipInfo(n,(2026,10,14,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
    z.writestr(info,b);manifest[n]=dict(bytes=len(b),sha256=sha(b))
with zipfile.ZipFile(base) as src,zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as dest:
    for n in sorted(src.namelist()):
        if n.startswith('payload/'):
            assert n.startswith('payload/E/') and '..' not in n.split('/')
            write(dest,n,overrides.pop(n) if n in overrides else src.read(n))
    for n,b in sorted(overrides.items()):write(dest,n,b)
    write(dest,'QUICKSTART.md',(K/'QUICKSTART.md').read_bytes())
    write(dest,'BASE-MANIFEST.json',src.read('MANIFEST.json'))
    write(dest,'VALIDATION.json',(json.dumps({n:validation[n] for n in ['display_workload_passed','mode720p_passed','audio_probe_passed','file_persistence_passed','cmd_persistence_passed','tested_fatx_verified','integrity_passed','normal_shutdown_count','scoped_combined_passed','strict_qualification_passed']},indent=2)+'\n').encode())
    for n in ['DEMO','DEMO-SETUP','DISPLAY','RECOVERY','BUILD','PUBLIC-RELEASE']:write(dest,'docs/'+n+'.md',(W/'docs'/(n+'.md')).read_bytes())
    write(dest,'READ-ME-FIRST.txt',b'PRIVATE E DEMO PAYLOAD - NOT FOR PUBLIC DISTRIBUTION\r\nContains owned Windows/user files inherited from the verified343 payload.\r\nMerged changes:376 drag controls/startup,374 E720p launcher and390 FATX exact-name enumeration fix. Menu380 is documented; no dashboard C files included.\r\nThis is not a fresh backup, empty-disk installer or full restore qualification.\r\nDo not overwrite an occupied installation or its user data with this ZIP.\r\nUse the guarded add-on deployment for the existing console.\r\nOnly dashboard E payload is included. Keep original F rollback separately.\r\nHost resolution controls are in the separate demo-preview bundle.\r\n')
    r=dict(kind='private-reconstructed-E-demo',base_archive_sha256=expected,source='343 verified E payload +376 add-on +374 E720p launcher +390 FATX',fresh_console_capture=False,generic_installer=False,restore_tested=False,public_ready=False,contains_owned_windows_and_user_data=True,files=manifest)
    # Exclude the manifest itself from its nonrecursive file list.
    info=zipfile.ZipInfo('MANIFEST.json',(2026,10,14,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;dest.writestr(info,(json.dumps(r,indent=2)+'\n').encode())
with zipfile.ZipFile(out) as z:
    assert set(z.namelist())==set(manifest)|{'MANIFEST.json'}
    for n,v in manifest.items():
        b=z.read(n);assert len(b)==v['bytes'] and sha(b)==v['sha256']
with out.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
r=dict(archive=str(out),bytes=out.stat().st_size,sha256=digest,entries=len(manifest)+1,payload_files=sum(n.startswith('payload/') for n in manifest),readback_verified=True,base_archive_sha256=expected,public_ready=False,restore_tested=False,fresh_console_capture=False)
(K/'system001.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
