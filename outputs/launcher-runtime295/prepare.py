"""Fresh blank fixture for bounded relocation checkpoints; no Windows payload."""
import pathlib,sys,json,hashlib,subprocess,shutil,socket,datetime
K=pathlib.Path(__file__).resolve().parent;case=sys.argv[1];assert case in ('control001','candidate001')
R=pathlib.Path('E:/xwn295')/case;O=K/case;assert not R.exists() and not O.exists()
assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3 and shutil.disk_usage('E:/').free-512*1024**2>=20*1024**3
for port in (4954,4955):
 with socket.socket() as s:s.bind(('127.0.0.1',port))
review=json.loads((K.parent/'launcher-relocation293/binary-review004.json').read_text());assert review['passed']
mode=case.replace('001','004');build=pathlib.Path('E:/xwn293')/mode
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
R.mkdir(parents=True);O.mkdir();(R/'private').mkdir();iso_dir=R/'disc';iso_dir.mkdir();shutil.copyfile(build/'default.xbe',iso_dir/'default.xbe')
assert sha(iso_dir/'default.xbe')==review['rows'][mode]['xbe_sha256']
xiso=pathlib.Path('C:/nxdk/tools/extract-xiso/build/extract-xiso.exe')
p=subprocess.run([str(xiso),'-c',str(iso_dir),str(R/'control.iso')],capture_output=True,text=True,timeout=30);(O/'iso.log').write_text(p.stdout+p.stderr);assert p.returncode==0
inputs={'base.qcow2':pathlib.Path('C:/Emulators/xemu/system/xbox_hdd.qcow2'),'eeprom.bin':pathlib.Path('E:/xwn289/fixture001/hd.bin'),'bios.bin':pathlib.Path('C:/Emulators/xemu/system/bios/Complex_4627.bin'),'mcpx.bin':pathlib.Path('C:/Emulators/xemu/system/mcpx/mcpx_1.0.bin'),'default.xbe':build/'default.xbe','image-crom.elf':build/'image-crom.elf','xemu.exe':pathlib.Path('E:/Codex-archive/xbox-windows-native/reuse269-build005/xemu-reuse269.exe')}
pins={}
for n,p in inputs.items():
 h=sha(p)
 if n=='xemu.exe':assert h=='489c9af75c8734c47ce8b67231bedb7b10d15dc98617902350514252e5fcc295'
 shutil.copyfile(p,R/n);assert sha(R/n)==h;pins[n]=dict(source=str(p),sha256=h,bytes=p.stat().st_size)
subprocess.run(['wsl','-d','Ubuntu','--','qemu-img','create','-f','qcow2','-F','qcow2','-b','base.qcow2',f'/mnt/e/xwn295/{case}/hdd.qcow2'],check=True,timeout=30)
info=subprocess.check_output(['wsl','-d','Ubuntu','--','qemu-img','info','--output=json',f'/mnt/e/xwn295/{case}/base.qcow2']);assert json.loads(info)['virtual-size']==8589934592;(R/'base-info.json').write_bytes(info)
config='[general]\nshow_welcome = false\n[general.updates]\ncheck = false\n[sys.files]\n'
for f,n in [('bootrom_path','mcpx.bin'),('flashrom_path','bios.bin'),('eeprom_path','eeprom.bin'),('hdd_path','hdd.qcow2')]:config+=f+" = '"+(R/n).as_posix()+"'\n"
(R/'config.toml').write_text(config)
deps={str(p.resolve()):sha(p) for p in list(K.glob('*.py'))+list(K.glob('*.ps1'))+[K.parent/'launcher-relocation293/review.py',K.parent/'launcher-relocation293/binary-review004.json',K.parent/'surface-bridge260/atomic_json.py',K.parent/'fatx-mapped-eof/coldio.py',xiso,R/'control.iso',R/'config.toml',pathlib.Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts/start_xemu_instance.ps1'),pathlib.Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts/lib/xemu_instance.ps1'),pathlib.Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts/lib/test_storage.ps1'),pathlib.Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1')]}
(O/'prepared.json').write_text(json.dumps(dict(prepared_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),root=str(R),inputs=pins,dependencies=deps,mode=mode,ports={'monitor':4954,'gdb':4955},parent='Fresh unused official blank8GiB; no Windows or FreeLdr payload',scope='Relocation checkpoint diagnostic, not Windows boot or HD mode qualification'),indent=2)+'\n')
