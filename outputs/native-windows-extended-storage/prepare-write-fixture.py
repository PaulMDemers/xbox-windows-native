"""Private derivative for exactly two high-LBA overwrite/shutdown cycles."""
import pathlib,sys,subprocess,struct,json,hashlib,argparse
root=pathlib.Path('/home/paul/xbox-windows-native');ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-extended-storage'
sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
p=argparse.ArgumentParser();p.add_argument('--reboot',action='store_true');a=p.parse_args()
label='reboot' if a.reboot else 'write'
source=k/'artifacts/windows2000-f-001.qcow2';target=k/('artifacts/windows2000-f-'+label+'-001.qcow2');raw=root/'fixtures'/('f-'+label+'-001.raw')
assert not target.exists() and not raw.exists()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
r={'source_sha256':sha(source),'scope':'Private emulator-only bounded overwrite and normal shutdown'}
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(source),str(raw)],check=True)
 with raw.open('r+b') as f:
  fatx.PARTITIONS['F']=(15633072*512,472764096*512);w=Writer(f,fatx.open_partition(f,raw,'F'))
  path='/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd';names=w.parts(path);at=1
  for name in names[:-1]:at=struct.unpack_from('<I',w.directory(at)['entries'][name][2],44)[0]
  c,offset,e=w.directory(at)['entries'][names[-1]];chain=list(w.chain(struct.unpack_from('<I',e,44)[0]))
  data=b'@echo off\r\nC:\\xwnlargewrite.exe\r\n';assert len(chain)==1
  w.write_cluster(chain[0],data);block=bytearray(w.read_cluster(c));struct.pack_into('<I',block,offset+48,len(data));w.write_cluster(c,block);w.dirs={}
  r['probe']=w.write('/xwnlargewrite.exe',(k/('artifacts/xwnlargereboot.exe' if a.reboot else 'artifacts/xwnlargewrite.exe')).read_bytes());w.flush()
  assert w.read(path)==data
 subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(raw),str(target)],check=True)
 assert sha(source)==r['source_sha256'];r.update(source_preserved=True,target_sha256=sha(target))
finally:raw.unlink(missing_ok=True)
(k/(label+'-fixture-001.json')).write_text(json.dumps(r,indent=2)+'\n');print(r)
