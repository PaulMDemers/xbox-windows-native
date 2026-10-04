"""Add one high-LBA sentinel to a private copy of the sparse metadata fixture."""
import pathlib,shutil,struct,subprocess,hashlib,json
root=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
kit=root/'outputs/native-windows-extended-partitions'
src=root/'work/storage-metadata-fixture.qcow2';dst=root/'work/extended-read-fixture.qcow2'
assert not dst.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=sha(src);subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(src),str(dst)],check=True)
fbase=15633072*512;cluster=65536;fatbytes=((472764096*512//cluster*4+4095)//4096)*4096
data_start=fbase+4096+fatbytes;cid=2100000
offset=data_start+(cid-1)*cluster
assert offset>2**28*512 and offset+cluster<250059350016
data=bytes((i*37+(i>>8)+0x5a)&255 for i in range(4097))
entry=bytearray(64);name=b'xwn-high.bin';entry[0]=len(name);entry[1]=0x20;entry[2:2+len(name)]=name
struct.pack_into('<II',entry,44,cid,len(data))
for label,off,payload in [('root',data_start,bytes(entry)+b'\xff'*(cluster-64)),('fat',fbase+4096+cid*4,struct.pack('<I',0xffffffff)),('data',offset,data.ljust(cluster,b'\0'))]:
 p=kit/('artifacts/'+label+'.bin');p.write_bytes(payload)
 subprocess.run(['qemu-io','-f','qcow2','-c',f'write -s {p} {off} {len(payload)}',str(dst)],check=True)
assert sha(src)==before
record=dict(source_sha256=before,source_preserved=True,sha256=sha(dst),file='xwn-high.bin',cluster=cid,file_bytes=len(data),file_sha256=hashlib.sha256(data).hexdigest(),absolute_byte_offset=offset,start_lba=offset//512,above_lba28=True,synthetic=True)
(kit/'read-fixture.json').write_text(json.dumps(record,indent=2)+'\n');print(record)
