import sys,pathlib,subprocess,json,hashlib
root=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');temp=pathlib.Path('/home/paul/xbox-windows-native/fixtures/storage-preflight.raw')
sys.path.insert(0,'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts')
import fatx_stage_boot as fatx
src=root/'work/unleashx-ftp-fixture.qcow2';target=root/'work/storage-preflight-fixture.qcow2';assert not temp.exists() and not target.exists()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
record={'source_sha256':sha(src)}
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(src),str(temp)],check=True)
 with temp.open('r+b') as fp:
  part=fatx.open_partition(fp,temp,'E');data=(root/'outputs/native-windows-physical-storage-preflight/artifacts/default.xbe').read_bytes()
  result=fatx.write_path_file(fp,part,'Apps/XWNStorage/default.xbe',data);record['file']=result.__dict__
  assert fatx.read_path_file(fp,part,'Apps/XWNStorage/default.xbe')==data
 subprocess.run(['qemu-img','convert','-O','qcow2',str(temp),str(target)],check=True)
 record['sha256']=sha(target);assert sha(src)==record['source_sha256'];record['source_preserved']=True
finally:
 assert temp.parent==pathlib.Path('/home/paul/xbox-windows-native/fixtures');temp.unlink(missing_ok=True)
(root/'outputs/native-windows-physical-storage-preflight/fixture.json').write_text(json.dumps(record,indent=2)+'\n');print(record)
