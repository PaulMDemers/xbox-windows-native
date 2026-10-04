"""Apply the exact physical launcher/probe files to a private emulator disk."""
import pathlib,sys,subprocess,struct,json,hashlib,argparse
root=pathlib.Path('/home/paul/xbox-windows-native');ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-physical-f'
sys.path[:0]=[str(k.parent/'native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
p=argparse.ArgumentParser();p.add_argument('--revision',choices=['001','002','003'],default='001');a=p.parse_args()
source=k.parent/'native-windows-extended-storage/artifacts/windows2000-f-reboot-002.qcow2';target=k/('artifacts/physical-f-'+a.revision+'.qcow2');raw=root/'fixtures'/('physical-f-'+a.revision+'.raw')
assert not target.exists() and not raw.exists()
r={'scope':'Exact launcher/probe in private F emulator fixture','files':[]}
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(source),str(raw)],check=True)
 with raw.open('r+b') as f:
  fatx.PARTITIONS['E']=(5633024*512,10000048*512);fatx.PARTITIONS['F']=(15633072*512,472764096*512)
  for drive in ['E','F']:
   w=Writer(f,fatx.open_partition(f,raw,drive))
   paths=list((k/'package/E').rglob('*')) if drive=='E' else [k/'package/F/xwnphysical.exe',k/'package/F/xwn-physical.bin',k/'package/F/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd']
   for p in paths:
    if not p.is_file():continue
    rel=p.relative_to(k/('package/'+drive)).as_posix();data=p.read_bytes()
    if a.revision!='001' and p.name=='freeldr.sys':data=(k/'artifacts/freeldr.sys').read_bytes()
    if drive=='F' and rel.endswith('xwnsetup.cmd'):
     at=1;parts=w.parts(rel)
     for name in parts[:-1]:at=struct.unpack_from('<I',w.directory(at)['entries'][name][2],44)[0]
     c,off,e=w.directory(at)['entries'][parts[-1]];chain=list(w.chain(struct.unpack_from('<I',e,44)[0]));assert len(chain)==1
     w.write_cluster(chain[0],data);b=bytearray(w.read_cluster(c));struct.pack_into('<I',b,off+48,len(data));w.write_cluster(c,b);w.dirs={}
    else:w.write(rel,data)
    assert w.read(rel)==data;r['files'].append({'path':drive+'/'+rel,'sha256':hashlib.sha256(data).hexdigest()})
   w.flush()
  # Harness's launch alias invokes exactly the physical XBE, which loads its E path.
  e=fatx.open_partition(f,raw,'E');data=(k/'artifacts/default.xbe').read_bytes();fatx.write_path_file(f,e,'Apps/XWN/default.xbe',data)
  assert fatx.read_path_file(f,e,'Apps/XWN/default.xbe')==data
 subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(raw),str(target)],check=True)
 with target.open('rb') as f:r['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
finally:raw.unlink(missing_ok=True)
(k/('emulator-fixture-'+a.revision+'.json')).write_text(json.dumps(r,indent=2)+'\n');print(r['sha256'])
