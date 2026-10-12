"""Prepare one isolated standalone child from the owned unused blank disk."""
import datetime,hashlib,json,re,shutil,socket,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case=='emu002';out=k/case;root=Path('E:/xwn272')/case
assert not out.exists() and not root.exists()
assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
assert shutil.disk_usage('E:/').free-512*1024**2>=20*1024**3
for port in (4724,4725):
    with socket.socket() as s:s.bind(('127.0.0.1',port))
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
out.mkdir();root.mkdir(parents=True);(root/'private').mkdir()
inputs={
 'base.qcow2':Path('C:/Emulators/xemu/system/xbox_hdd.qcow2'),
 'eeprom.bin':Path('C:/Emulators/xemu/eeprom.bin'),
 'bios.bin':Path('C:/Emulators/xemu/system/bios/Complex_4627.bin'),
 'mcpx.bin':Path('C:/Emulators/xemu/system/mcpx/mcpx_1.0.bin'),
 'default.xbe':Path('E:/xwn271/build005/bin/default.xbe'),
 'control.iso':Path('E:/xwn271/build005/owned-texture271.iso'),
 'main.map':Path('E:/xwn271/build005/main.map'),
 'xemu.exe':Path('E:/Codex-archive/xbox-windows-native/reuse269-build005/xemu-reuse269.exe')}
expected={'default.xbe':'4ada3d6c337360d14f67b6fe88ee8d42640a22849f6b2d310d884ef04a41dec1','control.iso':'2d2e19cc59db8ffa023407475fdb0ec38f9ac7b5f657e0720d2bf958bd90c714','xemu.exe':'489c9af75c8734c47ce8b67231bedb7b10d15dc98617902350514252e5fcc295'}
pins={}
for name,p in inputs.items():
    digest=sha(p)
    if name in expected:assert digest==expected[name]
    shutil.copyfile(p,root/name);assert sha(root/name)==digest
    pins[name]=dict(source=str(p),sha256=digest,bytes=p.stat().st_size)
subprocess.run(['wsl','-d','Ubuntu','--','qemu-img','create','-f','qcow2','-F','qcow2','-b','base.qcow2',f'/mnt/e/xwn272/{case}/hdd.qcow2'],check=True,timeout=30)
info=subprocess.check_output(['wsl','-d','Ubuntu','--','qemu-img','info','--output=json',f'/mnt/e/xwn272/{case}/base.qcow2'],timeout=30)
assert json.loads(info)['virtual-size']==8589934592
(root/'base-info.json').write_bytes(info)
config="[general]\nshow_welcome = false\n[general.updates]\ncheck = false\n[sys.files]\n"
for field,name in [('bootrom_path','mcpx.bin'),('flashrom_path','bios.bin'),('eeprom_path','eeprom.bin'),('hdd_path','hdd.qcow2')]:config+=field+" = '"+(root/name).as_posix()+"'\n"
(root/'config.toml').write_text(config)
symbols={m[1]:int(m[2],16) for m in re.finditer(r'^\s+[0-9a-f]+:[0-9a-f]+\s+(\S+)\s+([0-9a-f]{16})', (root/'main.map').read_text(),re.M)}
(out/'symbols.json').write_text(json.dumps(symbols,indent=2)+'\n')
dependencies={str(p.resolve()):sha(p) for p in list(k.glob('*.py'))+list(k.glob('*.ps1'))+[k.parent/'owned-texture271/oracle.py',k.parent/'owned-texture271/binary-review005.json',Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts/start_xemu_instance.ps1'),Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts/lib/xemu_instance.ps1'),Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts/lib/test_storage.ps1'),Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1')]}
r=dict(prepared_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),root=str(root),inputs=pins,dependencies=dependencies,ports=dict(monitor=4724,gdb=4725),guest_launch=False,physical_access=False,release_installed=False,observer_operation=False,parent='Owned unused official blank8GiB; fresh copied base, never an executed/interrupted Windows runtime',scope='Standalone nxdk control, no Windows restart/event qualification')
(out/'prepared.json').write_text(json.dumps(r,indent=2)+'\n')
print('Prepared unique272 child; no launch')
