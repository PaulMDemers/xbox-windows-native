import hashlib,json,shutil,socket,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('C:/xwn527/emu002');assert not O.exists()
assert shutil.disk_usage('C:/').free-768*1024**2>=20*1024**3
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prep=json.loads((K/'preparation002.json').read_text());assert prep['status']=='prepared' and prep['seed_never_executed']
assert sha(Path('C:/xwn527/preparation002/seed.qcow2'))==prep['seed_sha256']
with socket.socket() as s:s.bind(('127.0.0.1',6277))
O.mkdir();inputs={'eeprom.bin':Path('E:/xwn289/fixture001/hd.bin'),'bios.bin':Path('C:/Emulators/xemu/system/bios/Complex_4627.bin'),'mcpx.bin':Path('C:/Emulators/xemu/system/mcpx/mcpx_1.0.bin'),'utility.iso':Path('C:/xwn527/build001/dispatch527.iso')}
r=dict(root=str(O),physical_access=False,inputs={})
for n,p in inputs.items():
 shutil.copyfile(p,O/n);h=sha(p);assert sha(O/n)==h;r['inputs'][n]=dict(source=str(p),sha256=h)
exe=Path('E:/xwn329/retained-builds001/xemu-hd322.exe');h=sha(exe);assert h=='ea3473314e6c0ea068de4202cde46b1405da7553240cadea738c29c16d74c7a3'
r['emulator']=dict(source=str(exe),sha256=h)
# New task path hardlinks one closed private executable; bytes are never edited.
import os
old=Path('C:/xwn527/instances/dispatch527-emu001/EA3473314E6C0EA0/xemu-dispatch527-emu001.exe')
assert json.loads((K/'closure001.json').read_text(encoding='utf-8-sig'))['closed'] and sha(old)==h
new=Path('C:/xwn527/instances/dispatch527-emu002/EA3473314E6C0EA0/xemu-dispatch527-emu002.exe')
assert not new.parent.exists();new.parent.mkdir(parents=True);os.link(old,new);assert sha(new)==h
r['private_executable']=dict(path=str(new),closed_source=str(old),sha256=h,hardlink=True)

subprocess.run(['wsl','-d','Ubuntu','--','qemu-img','create','-f','qcow2','-F','qcow2','-b','../preparation002/seed.qcow2','/mnt/c/xwn527/emu002/hdd.qcow2'],check=True,timeout=30)
c='[general]\nshow_welcome=false\n[general.updates]\ncheck=false\n[sys.files]\n'
for field,n in [('bootrom_path','mcpx.bin'),('flashrom_path','bios.bin'),('eeprom_path','eeprom.bin'),('hdd_path','hdd.qcow2')]:c+=field+"='"+(O/n).as_posix()+"'\n"
(O/'config.toml').write_text(c)
r['runtime_initial']={str(p):sha(p) for p in O.iterdir() if p.is_file()}
chain=json.loads(subprocess.check_output(['wsl','-d','Ubuntu','--','qemu-img','info','--backing-chain','--output=json','/mnt/c/xwn527/emu002/hdd.qcow2'],timeout=30))
r['chain']=chain
for row in chain:
 name=row['filename'];assert name.startswith('/mnt/c/')
 win=Path('C:/'+name[7:]);assert win.is_file()
 if 'backing-filename' in row:
  assert not row['backing-filename'].startswith(('/', '\\'))
  backing=(win.parent/row['backing-filename']).resolve();assert backing.is_file()
  r.setdefault('cross_host_backings',[]).append(dict(path=str(backing),sha256=sha(backing)))
(K/'runtime-prepared002.json').write_text(json.dumps(r,indent=2)+'\n')
