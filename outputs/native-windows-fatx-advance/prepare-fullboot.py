"""Replace only the research FATX driver in a disposable full-FATX fixture."""
import pathlib,sys,subprocess,hashlib,json,struct,shutil
root=pathlib.Path('/home/paul/xbox-windows-native');ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');out=ws/'outputs/native-windows-fatx-advance'
sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
source=ws/'outputs/native-windows-fatx-runtime/artifacts/windows2000-fatx-boot-001.qcow2';target=out/'artifacts/windows2000-fatx-full-advance-001.qcow2';driver=out/'artifacts/xwnfatx.sys'
temp=root/'fixtures/fatx-full-advance-001';assert not temp.exists() and not target.exists();temp.mkdir()
def sha(p):
 with p.open('rb') as fp:return hashlib.file_digest(fp,'sha256').hexdigest()
r={'scope':'Private emulator full-FATX derivative; replace filesystem driver only. No hardware access.','source_sha256':sha(source),'driver_sha256':sha(driver)}
try:
 raw=temp/'disk.raw';subprocess.run(['qemu-img','convert','-O','raw',str(source),str(raw)],check=True)
 with raw.open('r+b') as fp:
  part=fatx.open_partition(fp,raw,'E');w=Writer(fp,part);path='/WINNT/system32/drivers/xwnfatx.sys';names=w.parts(path);at=1
  for name in names[:-1]:
   e=w.directory(at)['entries'][name.lower()][2];assert e[1]&16;at=struct.unpack_from('<I',e,44)[0]
  cluster,offset,e=w.directory(at)['entries'][names[-1].lower()];data=driver.read_bytes();chain=list(w.chain(struct.unpack_from('<I',e,44)[0]));assert len(data)<=len(chain)*part.cluster_size
  for i,c in enumerate(chain):w.write_cluster(c,data[i*part.cluster_size:(i+1)*part.cluster_size])
  block=bytearray(w.read_cluster(cluster));struct.pack_into('<I',block,offset+48,len(data));w.write_cluster(cluster,block);w.flush();assert Writer(fp,part).read(path)==data;r['cold_readback_equal']=True
 subprocess.run(['qemu-img','convert','-O','qcow2',str(raw),str(target)],check=True);r['check']=subprocess.check_output(['qemu-img','check',str(target)],text=True);r['sha256']=sha(target);assert sha(source)==r['source_sha256'];r['source_preserved']=True
finally:
 assert temp.resolve().parent==(root/'fixtures').resolve();shutil.rmtree(temp);r['temporary_raw_removed']=True;(out/'fatx-full-advance-disk-001.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
