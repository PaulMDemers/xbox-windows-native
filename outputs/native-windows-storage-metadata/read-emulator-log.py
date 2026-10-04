import pathlib,subprocess,sys,json,hashlib
root=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');src=root/'work/runs/storage-metadata-001/hdd.qcow2';assert (src.parent/'cleanup.json').exists();temp=pathlib.Path('/home/paul/xbox-windows-native/fixtures/read-storage-metadata.raw');assert not temp.exists()
sys.path.insert(0,'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts');import fatx_stage_boot as fatx
out=root/'outputs/native-windows-storage-metadata/evidence';out.mkdir(exist_ok=True)
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(src),str(temp)],check=True)
 with temp.open('rb') as fp:
  part=fatx.open_partition(fp,temp,'E');data=fatx.read_path_file(fp,part,'Apps/XWNMetadata/xwn-storage-metadata.txt')
 (out/'xemu-metadata.txt').write_bytes(data);print(data.decode())
finally:
 assert temp.parent==pathlib.Path('/home/paul/xbox-windows-native/fixtures');temp.unlink(missing_ok=True)
