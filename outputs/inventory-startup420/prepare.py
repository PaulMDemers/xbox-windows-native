import hashlib,json,pathlib,shutil,socket,subprocess
K=pathlib.Path(__file__).resolve().parent
root=pathlib.Path('E:/xwn420/emu001')
assert not root.exists()
assert all(shutil.disk_usage(d).free-64*1024**2>=20*1024**3 for d in ['C:/','E:/'])
with socket.socket() as s:s.bind(('127.0.0.1',5420))
root.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={'base.qcow2':pathlib.Path('C:/Emulators/xemu/system/xbox_hdd.qcow2'),
 'eeprom.bin':pathlib.Path('C:/Emulators/xemu/eeprom.bin'),
 'bios.bin':pathlib.Path('C:/Emulators/xemu/system/bios/Complex_4627.bin'),
 'mcpx.bin':pathlib.Path('C:/Emulators/xemu/system/mcpx/mcpx_1.0.bin'),
 'utility.iso':pathlib.Path('E:/xwn420/build001/hardware-report.iso')}
r={'inputs':{},'root':str(root),'physical_access':False}
for n,p in inputs.items():
 shutil.copy2(p,root/n);h=sha(p);assert sha(root/n)==h
 r['inputs'][n]={'source':str(p),'sha256':h}
exe=pathlib.Path('C:/Users/Paul/AppData/Local/ogxbox-linux/instances/windows-native/392C3FEE86E47A54/xemu-windows-native.exe')
r['emulator']={'source':str(exe),'sha256':sha(exe)}
subprocess.run(['wsl','-d','Ubuntu','--','qemu-img','create','-f','qcow2','-F','qcow2','-b','base.qcow2','/mnt/e/xwn420/emu001/hdd.qcow2'],check=True)
c="[general]\nshow_welcome=false\n[general.updates]\ncheck=false\n[sys.files]\n"
for field,n in [('bootrom_path','mcpx.bin'),('flashrom_path','bios.bin'),('eeprom_path','eeprom.bin'),('hdd_path','hdd.qcow2')]:c+=field+"='"+(root/n).as_posix()+"'\n"
(root/'config.toml').write_text(c)
(K/'prepared001.json').write_text(json.dumps(r,indent=2)+'\n')
