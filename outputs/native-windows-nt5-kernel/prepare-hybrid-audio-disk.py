"""Join private FATX dashboard and NTFS fixtures without modifying either input.

This is an emulator-only 12 GiB image, not a console disk conversion tool.
The FATX layout occupies the original first 8 GiB. NTFS begins at 8 GiB.
"""
import hashlib,json,os,pathlib,shutil,struct,subprocess,sys
root=pathlib.Path('/home/paul/xbox-windows-native')
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
out=ws/'outputs/native-windows-nt5-kernel';runtime=root/'toolchains/offline-disk/root'
sys.path.insert(0,str(runtime/'usr/lib/python3/dist-packages'));import hivex
dashboard=ws/'work/unleashx-ftp-fixture.qcow2'
windows=out/'artifacts/windows2000-audio-001.qcow2'

target=out/'artifacts/windows2000-unleashx-003.qcow2'
temp=root/'fixtures/hybrid-003';assert not target.exists() and not temp.exists();temp.mkdir()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
env=dict(os.environ,LD_LIBRARY_PATH=str(runtime/'usr/lib/x86_64-linux-gnu'))
def run(args):return subprocess.check_output(list(map(str,args)),env=env,stderr=subprocess.STDOUT).decode()
def prefix_hash(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  f.seek(512);left=8*1024**3-512
  while left:
   b=f.read(min(left,16*1024**2));assert b;h.update(b);left-=len(b)
 return h.hexdigest()
record={'scope':'Private emulator fixture. Original dashboard and Windows disks preserved. No physical Xbox writes.','inputs':{str(p.relative_to(ws)):sha(p) for p in [dashboard,windows]}}
try:
 dashraw=temp/'dashboard.raw';winraw=temp/'windows.raw';partition=temp/'windows.ntfs'
 run(['qemu-img','convert','-O','raw',dashboard,dashraw]);assert dashraw.stat().st_size==8*1024**3
 preserved=prefix_hash(dashraw)
 run(['qemu-img','convert','-O','raw',windows,winraw])
 with winraw.open('rb') as src:
  mbr=bytearray(src.read(512));assert mbr[510:512]==b'\x55\xaa' and mbr[450]==7
  old_start,count=struct.unpack_from('<II',mbr,454);assert old_start==63
  signature=bytes(mbr[440:444]);src.seek(old_start*512)
  with partition.open('xb') as dst:
   left=count*512
   while left:
    b=src.read(min(left,4*1024**2));assert b;dst.write(b);left-=len(b)
 hive=temp/'system';hive.write_bytes(subprocess.check_output([str(runtime/'usr/bin/ntfscat'),'-f',str(partition),'/WINNT/system32/config/system'],env=env))
 new_start=8*1024**3//512
 h=hivex.Hivex(str(hive),write=True);mounted=h.node_get_child(h.root(),'MountedDevices');assert mounted
 old=signature+struct.pack('<Q',old_start*512);new=signature+struct.pack('<Q',new_start*512);changed=[]
 mounted_values=[(h.value_key(value),*h.value_value(value)) for value in h.node_values(mounted)]
 for name,kind,data in mounted_values:
  if data==old:
   h.node_set_value(mounted,{'key':name,'t':kind,'value':new});changed.append(name)
 assert '\\DosDevices\\C:' in changed,changed
 h.commit(str(hive));del h
 from nt5_hive_indexes import normalize
 data,conversion=normalize(hive.read_bytes());assert not conversion['converted'];hive.write_bytes(data)
 run([runtime/'usr/sbin/ntfscp','-f',partition,hive,'/WINNT/system32/config/system'])
 with partition.open('r+b') as f:
  boot=f.read(512);assert boot[3:11]==b'NTFS    ' and struct.unpack_from('<I',boot,28)[0]==old_start
  total=struct.unpack_from('<Q',boot,40)[0];assert total in [count,count-1]
  backup_offset=(count-1)*512;f.seek(backup_offset);backup=f.read(512)
  assert backup==boot,'Unexpected NTFS backup boot sector'
  fixed=bytearray(boot);struct.pack_into('<I',fixed,28,new_start)
  f.seek(0);f.write(fixed);f.seek(backup_offset);f.write(fixed)
 with dashraw.open('r+b') as dst,partition.open('rb') as src:
  assert dst.read(512)==bytes(512),'Dashboard sector 0 is not empty'
  dst.truncate(12*1024**3);dst.seek(new_start*512);shutil.copyfileobj(src,dst,4*1024**2)
  struct.pack_into('<I',mbr,454,new_start);mbr[447:450]=b'\xfe\xff\xff';mbr[451:454]=b'\xfe\xff\xff'
  dst.seek(0);dst.write(mbr)
 assert prefix_hash(dashraw)==preserved
 run(['qemu-img','convert','-O','qcow2',dashraw,target]);record['check']=run(['qemu-img','check',target])
 record.update(disk_sha256=sha(target),partition_start_lba=new_start,partition_sectors=count,ntfs_hidden_sectors_updated=True,mounted_devices_updated=changed,fatx_bytes_512_through_8GiB_preserved_sha256=preserved,system_sha256=sha(hive))
 for p in [dashboard,windows]:assert sha(p)==record['inputs'][str(p.relative_to(ws))]
 record['inputs_preserved']=True
finally:
 assert temp.resolve().parent==(root/'fixtures').resolve();shutil.rmtree(temp)
 record['temporary_raws_removed']=True
 (out/'hybrid-disk-003.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))

