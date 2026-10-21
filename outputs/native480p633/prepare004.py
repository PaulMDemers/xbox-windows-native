"""Prepare one isolated standalone child from the owned unused blank disk."""
import datetime,hashlib,json,re,shutil,socket,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case=='emu004';out=k/case;root=Path('C:/xwn633')/case
assert not out.exists() and not root.exists()
assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
assert shutil.disk_usage('C:/').free-128*1024**2>=20*1024**3
for port in (5638,5639):
    with socket.socket() as s:s.bind(('127.0.0.1',port))
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
out.mkdir();root.mkdir(parents=True);(root/'private').mkdir()
inputs={
 'base.qcow2':Path('C:/Emulators/xemu/system/xbox_hdd.qcow2'),
 'eeprom.bin':Path('E:/xwn289/fixture001/hd.bin'),
 'bios.bin':Path('C:/Emulators/xemu/system/bios/Complex_4627.bin'),
 'mcpx.bin':Path('C:/Emulators/xemu/system/mcpx/mcpx_1.0.bin'),
 'default.xbe':Path('C:/xwn633/build001/default.xbe'),
 'control.iso':Path('C:/xwn633/build001/hd633.iso'),
 'image-crom.elf':Path('C:/xwn633/build001/image-crom.elf'),
 'xemu.exe':Path('C:/Emulators/xemu/xemu.exe')}
review=json.loads((k/'review001.json').read_text());assert review['passed']
expected={'default.xbe':review['xbe_sha256'],'control.iso':review['iso_sha256'],'xemu.exe':'7da537938ea2ac09f894186ba793c9ae51dff37c95903b0002273b8d363818b7'}
for name,entry in json.loads((k.parent/'hd-timing-capture307/emu001/prepared.json').read_text())['inputs'].items():
    if name in ('base.qcow2','eeprom.bin','bios.bin','mcpx.bin'):expected[name]=entry['sha256']
assert json.loads((k/'host001.json').read_text())['passed']
assert review['compiled_boot_mode']==3
pins={}
for name,p in inputs.items():
    digest=sha(p)
    if name in expected:assert digest==expected[name]
    shutil.copyfile(p,root/name);assert sha(root/name)==digest
    pins[name]=dict(source=str(p),sha256=digest,bytes=p.stat().st_size)
subprocess.run(['wsl','-d','Ubuntu','--','qemu-img','create','-f','qcow2','-F','qcow2','-b','base.qcow2',f'/mnt/c/xwn633/{case}/hdd.qcow2'],check=True,timeout=30)
info=subprocess.check_output(['wsl','-d','Ubuntu','--','qemu-img','info','--output=json',f'/mnt/c/xwn633/{case}/base.qcow2'],timeout=30)
assert json.loads(info)['virtual-size']==8589934592
(root/'base-info.json').write_bytes(info)
config="[general]\nshow_welcome = false\n[general.updates]\ncheck = false\n[sys.files]\n"
for field,name in [('bootrom_path','mcpx.bin'),('flashrom_path','bios.bin'),('eeprom_path','eeprom.bin'),('hdd_path','hdd.qcow2')]:config+=field+" = '"+(root/name).as_posix()+"'\n"
(root/'config.toml').write_text(config)
dependencies={str(p.resolve()):sha(p) for p in list(k.glob('*.py'))+list(k.glob('*.ps1'))+[k/'review001.json',Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts/start_xemu_instance.ps1'),Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts/lib/xemu_instance.ps1'),Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts/lib/test_storage.ps1'),Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1'),k.parent/'surface-bridge260/atomic_json.py',k.parent/'owned-runtime272/model.py',k.parent/'fatx-mapped-eof/coldio.py',k/'xwn_hd_native.c',k/'xwn_hd_adapter.c',k/'xwn_hd_profile.c',k/'DESIGN.md']}
r=dict(projected_host_allowance_bytes=128*1024**2, allocation_reason='Input copies total below32MiB plus96MiB for overlay/logs; no Windows runtime', prepared_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),root=str(root),inputs=pins,dependencies=dependencies,ports=dict(monitor=5638,gdb=5639),guest_launch=False,physical_access=False,release_installed=False,observer_operation=False,parent='Owned unused official blank8GiB; fresh copied base, never an executed/interrupted Windows runtime',scope='Native480p initialization stopped at wrapper return; no Windows boot or normal shutdown proof')
(out/'prepared.json').write_text(json.dumps(r,indent=2)+'\n')
print('Prepared unique633 child; no launch')
