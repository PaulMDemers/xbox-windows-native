import sys,pathlib,subprocess,json,hashlib,struct
root=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');temp=pathlib.Path('/home/paul/xbox-windows-native/fixtures/storage-metadata.raw')
sys.path.insert(0,'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts')
import fatx_stage_boot as fatx
src=root/'work/unleashx-ftp-fixture.qcow2';target=root/'work/storage-metadata-fixture.qcow2';assert not temp.exists() and not target.exists()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
record={'source_sha256':sha(src)}
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(src),str(temp)],check=True)
 with temp.open('r+b') as fp:
  part=fatx.open_partition(fp,temp,'E');data=(root/'outputs/native-windows-storage-metadata/artifacts/default.xbe').read_bytes()
  result=fatx.write_path_file(fp,part,'Apps/XWNMetadata/default.xbe',data);record['file']=result.__dict__
  assert fatx.read_path_file(fp,part,'Apps/XWNMetadata/default.xbe')==data
 subprocess.run(['qemu-img','convert','-O','qcow2',str(temp),str(target)],check=True)
 # Expand only this owned sparse fixture, then populate minimal extended metadata.
 subprocess.run(['qemu-img','resize',str(target),'250059350016'],check=True)
 starts=[5633024,4609024,1024,1537024,3073024,15633072]
 counts=[10000048,1024000,1536000,1536000,1536000,472764096]
 table=bytearray(512);table[:16]=b'****PARTINFO****'
 for i,(start,count) in enumerate(zip(starts,counts)):
  struct.pack_into('<IIII',table,48+i*32+16,0x80000000,start,count,0)
 fbase=starts[5]*512;fsize=counts[5]*512;cluster=65536
 fatbytes=((fsize//cluster*4+4095)//4096)*4096
 header=struct.pack('<4sIII',b'FATX',0x58574e46,128,1).ljust(4096,b'\0')
 fat=struct.pack('<II',0xfffffff8,0xffffffff).ljust(4096,b'\0')
 for label,offset,data in [('partinfo',0,table),('f-header',fbase,header),('f-fat',fbase+4096,fat),('f-root',fbase+4096+fatbytes,b'\xff'*cluster)]:
  payload=temp.with_name('storage-metadata-'+label+'.bin');payload.write_bytes(data)
  try:subprocess.run(['qemu-io','-f','qcow2','-c',f'write -s {payload} {offset} {len(data)}',str(target)],check=True,stdout=subprocess.DEVNULL)
  finally:payload.unlink()
 record.update(disk_bytes=250059350016,f_start_lba=starts[5],f_sector_count=counts[5],f_cluster_bytes=cluster,synthetic_partinfo=True)
 record['sha256']=sha(target);assert sha(src)==record['source_sha256'];record['source_preserved']=True
finally:
 assert temp.parent==pathlib.Path('/home/paul/xbox-windows-native/fixtures');temp.unlink(missing_ok=True)
(root/'outputs/native-windows-storage-metadata/fixture.json').write_text(json.dumps(record,indent=2)+'\n');print(record)
