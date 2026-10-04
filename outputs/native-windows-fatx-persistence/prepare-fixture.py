"""Prepare a private FATX fixture for file and registry restart persistence."""
from pathlib import Path
import sys,subprocess,hashlib,json,struct,shutil
root=Path('/home/paul/xbox-windows-native');ws=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');out=ws/'outputs/native-windows-fatx-persistence'
sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
source=ws/'outputs/native-windows-fatx-name-boundary/artifacts/windows2000-fatx-name-boundary-001.qcow2';target=out/'artifacts/windows2000-fatx-persistence-001.qcow2';temp=root/'fixtures/fatx-persistence-001'
assert not temp.exists() and not target.exists();temp.mkdir()
def sha(p):
 with p.open('rb') as fp:return hashlib.file_digest(fp,'sha256').hexdigest()
r={'scope':'Offline emulator derivative; no physical access','source_sha256':sha(source),'files':[]}
assert r['source_sha256']=='a4005a8d560312fcd0c6ec9f4eb176c520c69b7ef1f62f627c89aa6900e8f864'
try:
 raw=temp/'disk.raw';subprocess.run(['qemu-img','convert','-O','raw',str(source),str(raw)],check=True)
 with raw.open('r+b') as fp:
  part=fatx.open_partition(fp,raw,'E');w=Writer(fp,part)
  guard=w.read('/xwn-fragment-guard.bin');guard_hash=hashlib.sha256(guard).hexdigest()
  def replace(path,data):
   at=1;names=w.parts(path)
   for name in names[:-1]:
    e=w.directory(at)['entries'][name.lower()][2];assert e[1]&16;at=struct.unpack_from('<I',e,44)[0]
   c,offset,e=w.directory(at)['entries'][names[-1].lower()];chain=list(w.chain(struct.unpack_from('<I',e,44)[0]));assert len(data)<=len(chain)*part.cluster_size
   for i,k in enumerate(chain):w.write_cluster(k,data[i*part.cluster_size:(i+1)*part.cluster_size])
   block=bytearray(w.read_cluster(c));struct.pack_into('<I',block,offset+48,len(data));w.write_cluster(c,block);w.dirs={}
   assert w.read(path)==data;r['files'].append({'path':path,'sha256':hashlib.sha256(data).hexdigest(),'cold_readback_equal':True})
  driver=ws/'outputs/native-windows-fatx-name-boundary/artifacts/xwnfatx.sys';assert sha(driver)=='a10cfaac19a526f48e0a85ebab961140130ba4e7e4a3660dad2f56fa2841d183'
  replace('/WINNT/system32/drivers/xwnfatx.sys',driver.read_bytes())
  r['driver_sha256']=sha(driver)
  replace('/Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd',b'@echo off\r\nC:\\xwncheck.exe\r\nC:\\xwnfs.exe\r\nC:\\xwnpersist.exe\r\nnotepad C:\\xwn-persist.log\r\n')
  r['files'].append(w.write('/xwnpersist.exe',(out/'artifacts/xwnpersist.exe').read_bytes()))
  w.flush();assert w.read('/xwn-fragment-guard.bin')==guard
  e=w.directory(1)['entries']['pagefile.sys'][2];chain=list(w.chain(struct.unpack_from('<I',e,44)[0]));runs=1+sum(y!=x+1 for x,y in zip(chain,chain[1:]));assert runs==384
  r['pagefile_physical_runs']=runs;r['guard_sha256']=guard_hash
 subprocess.run(['qemu-img','convert','-O','qcow2',str(raw),str(target)],check=True);r['sha256']=sha(target);r['check']=subprocess.check_output(['qemu-img','check',str(target)],text=True)
 assert sha(source)==r['source_sha256'];r['source_preserved']=True
finally:
 assert temp.resolve().parent==(root/'fixtures').resolve();shutil.rmtree(temp);r['temporary_raw_removed']=True
 (out/'persistence-fixture-001.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
