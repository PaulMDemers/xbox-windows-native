"""Normalize unused directory tails in a fresh, owned emulator fixture only."""
import pathlib,sys,subprocess,struct,json,hashlib
root=pathlib.Path('/home/paul/xbox-windows-native');ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-extended-storage'
sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
source=k/'artifacts/windows2000-f-reboot-001.qcow2';target=k/'artifacts/windows2000-f-reboot-002.qcow2';raw=root/'fixtures/f-normalize-002.raw'
assert not target.exists() and not raw.exists()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
r={'scope':'Fresh private emulator fixture; no physical access','source_sha256':sha(source),'changed_directories':[]}
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(source),str(raw)],check=True)
 with raw.open('r+b') as f:
  fatx.PARTITIONS['F']=(15633072*512,472764096*512);w=Writer(f,fatx.open_partition(f,raw,'F'));files={}
  def walk(c,path):
   entries=list(w.directory(c)['entries'].items())
   ended=False;changed=False
   for dc in w.chain(c):
    b=bytearray(w.read_cluster(dc));end=0 if ended else next((i for i in range(0,len(b),64) if b[i] in (0,255)),len(b))
    if end<len(b):ended=True
    assert all(v in (0,255) for v in b[end:]),path
    if b[end:]!=b'\xff'*(len(b)-end):
     b[end:]=b'\xff'*(len(b)-end);w.write_cluster(dc,b);changed=True
   if changed:r['changed_directories'].append(path)
   for name,(_,_,e) in entries:
    p=path.rstrip('/')+'/'+name;start=struct.unpack_from('<I',e,44)[0]
    if e[1]&16:walk(start,p)
    else:files[p]=hashlib.sha256(w.read(p)).hexdigest()
  walk(1,'/');w.dirs={}
  for p,h in files.items():assert hashlib.sha256(w.read(p)).hexdigest()==h
  r['files_unchanged']=len(files)
 subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(raw),str(target)],check=True)
 r['target_sha256']=sha(target);assert sha(source)==r['source_sha256'];r['source_preserved']=True
finally:raw.unlink(missing_ok=True)
(k/'normalized-fixture-002.json').write_text(json.dumps(r,indent=2)+'\n');print('Normalized',len(r['changed_directories']),'directories; preserved',r['files_unchanged'],'files')
