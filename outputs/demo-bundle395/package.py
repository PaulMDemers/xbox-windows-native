"""Assemble a private, source-pinned demo add-on/config bundle; no Windows media."""
import hashlib,json,zipfile
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];O=Path('C:/xwn395/preview001')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda b:hashlib.sha256(b).hexdigest()
assert not O.exists() and not (K/'package001.json').exists()
audit=read(K.parent/'demo-runtime377/control001/audit.json');assert audit['scoped_combined_passed'] and audit['outline_settings_passed']
validation=read(K.parent/'fatx-physical394/candidate001/audit.json');closure=read(K.parent/'fatx-physical394/candidate001/final-state.json');assert closure['closed'] and validation['diagnostic_workload_completed'] and validation['scoped_combined_passed'] and validation['cmd_persistence_passed'] and validation['tested_fatx_verified']
assert read(K/'accepted-state.json')['accepted']
O.mkdir(parents=True);entries={}
entries['QUICKSTART.md']=(K/'QUICKSTART.md').read_bytes()
entries['VALIDATION.json']=(json.dumps({n:validation[n] for n in ['display_workload_passed','mode720p_passed','audio_probe_passed','file_persistence_passed','cmd_persistence_passed','tested_fatx_verified','integrity_passed','normal_shutdown_count','scoped_combined_passed','strict_qualification_passed','warnings_errors']},indent=2)+'\n').encode()
for n in ['DEMO','DEMO-SETUP','DISPLAY','RECOVERY','BUILD','PUBLIC-RELEASE']:entries['docs/'+n+'.md']=(W/'docs'/(n+'.md')).read_bytes()
for n in ['configure-e-display.py','e-display-policy.json']:entries['tools/'+n]=(W/'tools'/n).read_bytes()
pkg=read(K.parent/'demo-settings376/package001.json')
for n,v in pkg['files'].items():
    b=(Path(pkg['package_root'])/n).read_bytes();assert sha(b)==v['sha256'];entries['addon/xwndemo372/'+n]=b
entries['addon/demo-startup.cmd']=(Path(pkg['package_root'])/'demo-startup.cmd').read_bytes()
fatx=Path('E:/xwn390/build001/xwnfatx.sys').read_bytes();assert sha(fatx)==read(K/'accepted-state.json')['candidate_sha256']
entries['addon/winnt/system32/drivers/xwnfatx.sys']=fatx
entries['rollback/xwnfatx-0101.sys']=(K.parent/'fatx-physical394/artifacts/candidate001-before/E/winnt/system32/drivers/xwnfatx.sys').read_bytes()
for n in ['0390-vfat-cached-fatx-logical-indices.patch','manifest.json','build-report.json','binary-review.json','final-review.json']:entries['source/fatx390/'+n]=(K.parent/'fatx-enumeration390'/n).read_bytes()
entries['source/display-settings.c']=(K.parent/'demo-settings376/settings.c').read_bytes()
entries['source/e-720p-path.patch']=(K.parent/'resolution-e374/cromwell.patch').read_bytes()
policy=read(W/'tools/e-display-policy.json')
for mode,p in [('720p',Path('E:/xwn374/build001/default.xbe')),('1080i',Path('E:/xwn334/build001/default.xbe'))]:
    b=p.read_bytes();assert sha(b)==policy['profiles'][mode]['sha256'];entries['resolution/'+mode+'/default.xbe']=b
entries['README.txt']=('PRIVATE DEMO PREVIEW - existing owned E installation only\r\n\r\nRead docs/DEMO.md first, then docs/DISPLAY.md.\r\nThe physical demo selects720p, original303 video/audio004 and testedFATX390.\r\nUser confirms clean720p text/full dragging. See VALIDATION.json for final test results. 1080i output remains unresolved.\r\nThis package is an add-on and mode selector, NOT a Windows installer.\r\nNo Windows media, hives, EEPROM or firmware is included.\r\nDo not publish until source/license and public-export review is complete.\r\nImmutable0.1.0/0.2.0 remain unchanged.\r\n\r\nCurrent owned console already has FATX390 installed and verified; rollback0101 included.\r\nDo not blindly deploy the storage driver to other consoles.\r\nAddon: copy addon/xwndemo372 to dashboard E/xwndemo372.\r\nRun its Outline dragging.cmd inside Windows. The guarded demo deployment\r\ncan apply it once at startup; do not overwrite startup without its backup.\r\nResolution: see docs/DISPLAY.md for inspect/apply/restore.\r\nDo not use the old F selector. See docs/DEMO-SETUP.md for the menu-only C exception and backup.\r\n').encode()
r=dict(kind='private-demo-preview-not-release',contains_windows_firmware_eeprom_hives=False,
       file_manifest={n:dict(bytes=len(b),sha256=sha(b)) for n,b in entries.items()},
       storage_runtime='fatx-physical394/candidate001',storage_driver_sha256=sha(fatx),settings_runtime='demo-runtime377/control001',settings_scoped_passed=True,
       E720p='user confirmed clean text/dragging; actual final trial results included',E1080i='unresolved output issue, diagnostic profile only',
       strict_events_passed=False,public_ready=False,source_release_gate='docs/PUBLIC-RELEASE.md',
       full_system_bundle=dict(path='E:/xwn343/bundle002/stock-e-1080i-001.zip',sha256='e79771fbf5eaf10c3e30e80e0d04e622dfd443448e24fa4eb76deac01d1b3e83',scope='Existing private owned-console migration archive, not included or newly restore-tested'))
with Path(r['full_system_bundle']['path']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['full_system_bundle']['sha256']
entries['MANIFEST.json']=(json.dumps(r,indent=2)+'\n').encode()
for n,b in entries.items():p=O/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
zpath=O/'xwn-demo-720p-preview-20261014.zip'
with zipfile.ZipFile(zpath,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for n,b in sorted(entries.items()):
        info=zipfile.ZipInfo(n,(2026,10,14,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,b)
with zipfile.ZipFile(zpath) as z:
    assert set(z.namelist())==set(entries)
    for n,b in entries.items():assert z.read(n)==b
r.update(archive=str(zpath),archive_sha256=sha(zpath.read_bytes()),archive_bytes=zpath.stat().st_size,readback_verified=True)
(K/'package001.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['archive','archive_sha256','archive_bytes','readback_verified']},indent=2))
