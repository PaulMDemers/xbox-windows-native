"""Extract checked native F files; build a file-only, nonformatting package."""
import pathlib,sys,subprocess,struct,json,hashlib,shutil
root=pathlib.Path('/home/paul/xbox-windows-native');ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-physical-f';ext=k.parent/'native-windows-extended-storage'
sys.path[:0]=[str(k.parent/'native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
source=ext/'artifacts/windows2000-f-reboot-002.qcow2';raw=root/'fixtures/physical-f-package.raw';package=k/'package'
assert not raw.exists() and not package.exists();package.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
with source.open('rb') as f:source_hash=hashlib.file_digest(f,'sha256').hexdigest()
assert source_hash==json.loads((ext/'normalized-fixture-002.json').read_text())['target_sha256']
r={'scope':'File-only physical F deployment; no partition/format operation','source_sha256':source_hash,'files':[],'directories':[]}
def emit(name,data):
 parts=name.split('/');assert max(map(len,parts))<=42 and len(name)<240,name
 p=package/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);r['files'].append({'path':name,'bytes':len(data),'sha256':sha(data)})
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(source),str(raw)],check=True)
 with raw.open('rb') as f:
  fatx.PARTITIONS['F']=(15633072*512,472764096*512);w=Writer(f,fatx.open_partition(f,raw,'F'))
  def walk(c,path):
   (package/('F'+path)).mkdir(parents=True,exist_ok=True);r['directories'].append('F'+path)
   for name,(_,_,e) in w.directory(c)['entries'].items():
    p=path+'/'+name;start=struct.unpack_from('<I',e,44)[0]
    if e[1]&16:walk(start,p)
    else:
     data=w.read(p)
     if p=='/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd':data=b'@echo off\r\nC:\\xwnphysical.exe\r\n'
     emit('F'+p,data)
  for n in ['winnt','documents and settings','program files']:
   e=w.directory(1)['entries'][n][2];walk(struct.unpack_from('<I',e,44)[0],'/'+n)
 emit('F/xwnphysical.exe',(k/'artifacts/xwnphysical.exe').read_bytes())
 emit('F/xwn-physical.bin',bytes((i*37+(i>>8)+0x5a)&255 for i in range(65537)))
 launcher='E/Applications/XWNFBoot/'
 emit(launcher+'default.xbe',(k/'artifacts/default.xbe').read_bytes())
 for name in ['freeldr.sys','rosload.exe']:emit(launcher+name,(ext/'artifacts'/name).read_bytes())
 emit(launcher+'loader/halxboxnt5.dll',(ext/'artifacts/halxboxnt5.dll').read_bytes())
 emit(launcher+'loader/xboxbvid.dll',(k.parent/'native-windows-bootvid-framebuffer/artifacts/xboxbvid.dll').read_bytes())
 for name in ['probe.bin','freeldr.ini']:emit(launcher+name,(k.parent/'native-windows-physical-bootvideo/package'/name).read_bytes())
 r['total_bytes']=sum(x['bytes'] for x in r['files']);r['source_preserved']=True
finally:raw.unlink(missing_ok=True)
(k/'package-manifest.json').write_text(json.dumps(r,indent=2)+'\n');print(len(r['files']),'files',r['total_bytes'],'bytes')
