"""Prepare one never-launched Windows runtime; reuse executable bytes by hardlink."""
import hashlib,json,os,shutil,socket,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn636/emu001');assert not P.exists()
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert shutil.disk_usage('C:/').free-192*1024**2>=20*1024**3
prep=json.loads((K/'preparation002.json').read_text());S=Path('C:/xwn636/preparation002/seed.qcow2');assert prep['prepared'] and sha(S)==prep['seed_sha256']
for port in [5668]:
 with socket.socket() as s:s.bind(('127.0.0.1',port))
P.mkdir();r=dict(physical_access=False,debugger=False,root=str(P),inputs={},projected_allowance_bytes=192*1024**2,allocation='128MiB overlay maximum + 32MiB captures/logs + 32MiB buffer; existing immutable executable hardlink')
inputs={'bios.bin':Path('C:/Emulators/xemu/system/bios/Complex_4627.bin'),'mcpx.bin':Path('C:/Emulators/xemu/system/mcpx/mcpx_1.0.bin'),'eeprom.bin':Path('E:/xwn289/fixture001/hd.bin'),'boot.iso':Path('C:/xwn633/build001/hd633.iso')}
old=json.loads((K.parent/'native480p633/emu004/prepared.json').read_text())['inputs']
for n,p in inputs.items():
 expected=old['control.iso' if n=='boot.iso' else n]['sha256'];assert sha(p)==expected
 shutil.copyfile(p,P/n);assert sha(P/n)==expected;r['inputs'][n]=dict(source=str(p),sha256=expected)
exe=Path('C:/xwn377/instances/windows-native-demo377-control001/EA3473314E6C0EA0/xemu-windows-native-demo377-control001.exe')
assert json.loads((K.parent/'demo-runtime377/control001/closure.json').read_text())['closed']
expected='ea3473314e6c0ea068de4202cde46b1405da7553240cadea738c29c16d74c7a3';assert sha(exe)==expected
dest=Path('C:/xwn636/instances/windows-native-480p636/EA3473314E6C0EA0/xemu-windows-native-480p636.exe');dest.parent.mkdir(parents=True);os.link(exe,dest);assert sha(dest)==expected
r['emulator']=dict(source=str(exe),private=str(dest),sha256=expected,hardlinked=True)
subprocess.run(['wsl','-d','Ubuntu','--','qemu-img','create','-f','qcow2','-F','qcow2','-b','../preparation002/seed.qcow2','/mnt/c/xwn636/emu001/hdd.qcow2'],check=True,timeout=30)
r['chain']=json.loads(subprocess.check_output(['wsl','-d','Ubuntu','--','qemu-img','info','--backing-chain','--output=json','/mnt/c/xwn636/emu001/hdd.qcow2'],timeout=30))
r['parents']={str(S):sha(S),str(Path('C:/xwn466/preparation002/seed.qcow2')):prep['parent_sha256']}
assert len(r['chain'])==3
c='[general]\nshow_welcome=false\n[general.updates]\ncheck=false\n[sys]\nmem_limit="64"\n[sys.files]\n'
for field,n in [('bootrom_path','mcpx.bin'),('flashrom_path','bios.bin'),('eeprom_path','eeprom.bin'),('hdd_path','hdd.qcow2')]:c+=field+"='"+(P/n).as_posix()+"'\n"
(P/'config.toml').write_text(c)
r['dependencies']={str(p.resolve()):sha(p) for p in [K/'Run.ps1',K/'observe.py',K/'runtime.py',K.parent/'native480p633/protocol.py']}
r['initial']={str(p):sha(p) for p in P.iterdir() if p.is_file()}
(K/'runtime001.json').write_text(json.dumps(r,indent=2)+'\n');print('Prepared636 runtime, no launch')
