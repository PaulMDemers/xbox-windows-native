"""Prepare one isolated standalone child from the owned unused blank disk."""
import datetime,hashlib,json,re,shutil,socket,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case=='emu001';out=k/case;root=Path('D:/xwn307')/case
assert not out.exists() and not root.exists()
assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
assert shutil.disk_usage('D:/').free-512*1024**2>=20*1024**3
for port in (5074,5075):
    with socket.socket() as s:s.bind(('127.0.0.1',port))
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
out.mkdir();root.mkdir(parents=True);(root/'private').mkdir()
inputs={
 'base.qcow2':Path('C:/Emulators/xemu/system/xbox_hdd.qcow2'),
 'eeprom.bin':Path('E:/xwn289/fixture001/hd.bin'),
 'bios.bin':Path('C:/Emulators/xemu/system/bios/Complex_4627.bin'),
 'mcpx.bin':Path('C:/Emulators/xemu/system/mcpx/mcpx_1.0.bin'),
 'default.xbe':Path('D:/xwn307/build001/bin/default.xbe'),
 'control.iso':Path('D:/xwn307/build001/hd307.iso'),
 'main.map':Path('D:/xwn307/build001/main.map'),
 'xemu.exe':Path('E:/Codex-archive/xbox-windows-native/reuse269-build005/xemu-reuse269.exe')}
review=json.loads((k/'binary-review001.json').read_text());assert review['passed']
expected={'default.xbe':review['xbe_sha256'],'control.iso':review['iso_sha256'],'xemu.exe':'489c9af75c8734c47ce8b67231bedb7b10d15dc98617902350514252e5fcc295'}
pins={}
for name,p in inputs.items():
    digest=sha(p)
    if name in expected:assert digest==expected[name]
    shutil.copyfile(p,root/name);assert sha(root/name)==digest
    pins[name]=dict(source=str(p),sha256=digest,bytes=p.stat().st_size)
subprocess.run(['wsl','-d','Ubuntu','--','qemu-img','create','-f','qcow2','-F','qcow2','-b','base.qcow2',f'/mnt/d/xwn307/{case}/hdd.qcow2'],check=True,timeout=30)
info=subprocess.check_output(['wsl','-d','Ubuntu','--','qemu-img','info','--output=json',f'/mnt/d/xwn307/{case}/base.qcow2'],timeout=30)
assert json.loads(info)['virtual-size']==8589934592
(root/'base-info.json').write_bytes(info)
config="[general]\nshow_welcome = false\n[general.updates]\ncheck = false\n[sys.files]\n"
for field,name in [('bootrom_path','mcpx.bin'),('flashrom_path','bios.bin'),('eeprom_path','eeprom.bin'),('hdd_path','hdd.qcow2')]:config+=field+" = '"+(root/name).as_posix()+"'\n"
(root/'config.toml').write_text(config)
symbols={m[1]:int(m[2],16) for m in re.finditer(r'^\s+[0-9a-f]+:[0-9a-f]+\s+(\S+)\s+([0-9a-f]{16})', (root/'main.map').read_text(),re.M)}
(out/'symbols.json').write_text(json.dumps(symbols,indent=2)+'\n')
dependencies={str(p.resolve()):sha(p) for p in list(k.glob('*.py'))+list(k.glob('*.ps1'))+[k/'binary-review001.json',Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts/start_xemu_instance.ps1'),Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts/lib/xemu_instance.ps1'),Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts/lib/test_storage.ps1'),Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1'),k.parent/'surface-bridge260/atomic_json.py',k.parent/'owned-runtime272/model.py',k.parent/'fatx-mapped-eof/coldio.py',k/'eeprom001.json',k/'main.c',k/'Makefile',k/'DESIGN.md',k.parent/'hd-physical292/decode.py',k.parent/'hd-physical292/expected.json']}
r=dict(prepared_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),root=str(root),inputs=pins,dependencies=dependencies,ports=dict(monitor=5074,gdb=5075),guest_launch=False,physical_access=False,release_installed=False,observer_operation=False,parent='Owned unused official blank8GiB; fresh copied base, never an executed/interrupted Windows runtime',scope='Standalone kernel API HD/SD modes, private HD-enabled EEPROM; no physical access or Windows boot')
(out/'prepared.json').write_text(json.dumps(r,indent=2)+'\n')
print('Prepared unique289 child; no launch')
