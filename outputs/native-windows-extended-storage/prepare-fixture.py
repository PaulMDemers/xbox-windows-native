"""Build a private 250 GB F-boot fixture from the verified FATX Windows tree."""
import pathlib,sys,subprocess,struct,hashlib,json,os,re,shutil
root=pathlib.Path('/home/paul/xbox-windows-native');ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
kit=ws/'outputs/native-windows-extended-storage';runtime=root/'toolchains/offline-disk/root'
sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),str(runtime/'usr/lib/python3/dist-packages'),str(ws/'outputs/native-windows-nt5-kernel'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import hivex,fatx_stage_boot as fatx
from bulk_fatx import Writer
from nt5_hive_indexes import normalize
temp=root/'fixtures/extended-storage-001';target=kit/'artifacts/windows2000-f-001.qcow2'
assert not temp.exists() and not target.exists();temp.mkdir()
source=ws/'work/runs/nt5-fatx-boot-persistence-002/hdd.qcow2';dashboard=ws/'work/unleashx-ftp-fixture.qcow2'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
r={'scope':'Private synthetic emulator F boot; never use formatter on physical media','source_sha256':sha(source),'dashboard_sha256':sha(dashboard),'files':[]}
assert r['source_sha256']=='76dd23ea5a87447ef918551a74b4d646b8267183168ccedb2aa0e4bbb52aebd1'
try:
 old=temp/'old.raw';new=temp/'new.raw'
 subprocess.run(['qemu-img','convert','-O','raw',str(source),str(old)],check=True)
 subprocess.run(['qemu-img','convert','-O','raw',str(dashboard),str(new)],check=True)
 with old.open('rb') as inf,new.open('r+b') as outf:
  reader=Writer(inf,fatx.open_partition(inf,old,'E'))
  outf.truncate(250059350016)
  starts=[5633024,4609024,1024,1537024,3073024,15633072];counts=[10000048,1024000,1536000,1536000,1536000,472764096]
  table=bytearray(512);table[:16]=b'****PARTINFO****'
  for i,(start,count) in enumerate(zip(starts,counts)):struct.pack_into('<IIII',table,48+i*32+16,0x80000000,start,count,0)
  outf.seek(0);outf.write(table)
  fbase=starts[5]*512;fsize=counts[5]*512;cluster=65536;fatbytes=((fsize//cluster*4+4095)//4096)*4096
  outf.seek(fbase);outf.write(struct.pack('<4sIII',b'FATX',0x58574e46,128,1).ljust(4096,b'\0'))
  outf.write(struct.pack('<II',0xfffffff8,0xffffffff).ljust(fatbytes,b'\0'));outf.write(b'\xff'*cluster)
  fatx.PARTITIONS['F']=(fbase,fsize);part=fatx.open_partition(outf,new,'F');writer=Writer(outf,part)
  # Reserve the high-LBA sentinel before allocating the Windows tree.
  cid=2100000;writer.fat[cid]=writer.end;data=bytes((i*37+(i>>8)+0x5a)&255 for i in range(4097))
  writer.write_cluster(cid,data);writer.add(1,'xwn-high.bin',32,cid,len(data))
  r['sentinel_offset']=part.cluster_offset(cid);assert r['sentinel_offset']>2**28*512
  hive=temp/'SYSTEM';hive.write_bytes(reader.read('/WINNT/system32/config/system'))
  h=hivex.Hivex(str(hive),write=True)
  def node(path,create=False):
   at=h.root()
   for component in path.split('\\'):
    nxt=h.node_get_child(at,component)
    if not nxt and create:nxt=h.node_add_child(at,component)
    assert nxt,path;at=nxt
   return at
  def setval(n,key,kind,value):h.node_set_value(n,{'key':key,'t':kind,'value':value})
  for child in h.node_children(h.root()):
   name=h.node_name(child)
   if not re.fullmatch('ControlSet[0-9]{3}',name):continue
   params=node(name+'\\Services\\Atapi\\Parameters',True)
   setval(params,'EnableBigLba',4,struct.pack('<I',1))
  mounted=node('MountedDevices');oldmap=struct.pack('<IQ',0xaa55,5633024*512);newmap=struct.pack('<IQ',0xaa55,fbase);changed=[]
  for key,kind,value in [(h.value_key(v),*h.value_value(v)) for v in h.node_values(mounted)]:
   if value==oldmap:setval(mounted,key,kind,newmap);changed.append(key)
  assert '\\DosDevices\\C:' in changed
  h.commit(str(hive));del h
  fixed,conversion=normalize(hive.read_bytes());r['hive']={'mounted_devices_updated':changed,'EnableBigLba':1,'normalization':conversion}
  overrides={'/winnt/system32/config/system':fixed,
   '/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd':b'@echo off\r\nC:\\xwnlarge.exe\r\nnotepad C:\\xwn-large.log\r\n'}
  def copydir(cid,path):
   for name,(_,_,entry) in reader.directory(cid)['entries'].items():
    rel=path+'/'+name;start=struct.unpack_from('<I',entry,44)[0]
    if entry[1]&16:
     writer.mkdir(rel);copydir(start,rel)
    else:
     data=overrides.get(rel.lower())
     if data is None:data=reader.read(rel)
     r['files'].append(writer.write(rel,data))
     if len(r['files'])%500==0:print('Copied',len(r['files']),flush=True)
  for name in ['winnt','documents and settings','program files']:
   entry=reader.directory(1)['entries'].get(name)
   if entry:writer.mkdir('/'+name);copydir(struct.unpack_from('<I',entry[2],44)[0],'/'+name)
  r['files'].append(writer.write('/xwnlarge.exe',(kit/'artifacts/xwnlarge.exe').read_bytes()))
  writer.flush();cold=Writer(outf,part)
  for item in r['files']:
   data=cold.read(item['path']);assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256']
  assert cold.read('/xwn-high.bin')==bytes((i*37+(i>>8)+0x5a)&255 for i in range(4097))
  r['cold_readback_verified']=len(r['files']);r['driver_sha256']=hashlib.sha256(cold.read('/winnt/system32/drivers/xwnfatx.sys')).hexdigest()
  assert r['driver_sha256']=='a10cfaac19a526f48e0a85ebab961140130ba4e7e4a3660dad2f56fa2841d183'
 subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(new),str(target)],check=True)
 r['target_sha256']=sha(target);r['check']=subprocess.check_output(['qemu-img','check',str(target)],text=True)
 assert sha(source)==r['source_sha256'] and sha(dashboard)==r['dashboard_sha256'];r['sources_preserved']=True
finally:
 assert temp.resolve().parent==(root/'fixtures').resolve();shutil.rmtree(temp)
 (kit/'fixture-001.json').write_text(json.dumps(r,indent=2)+'\n')
print('F-boot fixture prepared',r.get('cold_readback_verified'),flush=True)
