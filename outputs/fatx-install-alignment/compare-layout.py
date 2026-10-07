"""Compare saved FATX log topology; no physical access and no first-boot topology inference."""
import array,hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['001','002']
out=k/case;dest=out/'layout-comparison.json';assert not dest.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
def layout(folder,report):
 meta=(folder/'fat-metadata.bin').read_bytes();blob=(folder/'directories.bin').read_bytes()
 assert sha(meta)==report['metadata_sha256'] and sha(blob)==report['directory_records_sha256']
 assert report['allocation_consistent'] and not report['errors']
 assert struct.unpack_from('<II',meta,8)==(128,1)
 fat=array.array('I');fat.frombytes(meta[4096:])
 if sys.byteorder!='little':fat.byteswap()
 entries={}
 for off in range(0,len(blob),80):
  typ,head,cluster,slot=struct.unpack_from('<4I',blob,off)
  if typ==2:
   e=blob[off+16:off+80];entries.setdefault(head,{})[e[2:2+e[0]].decode('latin1').lower()]=e
 at=1
 for part in ['winnt','setupapi.log']:
  e=entries[at][part];at,size=struct.unpack_from('<II',e,44)
 chain=[]
 while at!=0xffffffff:
  assert 1<=at<len(fat) and at not in chain;chain.append(at);at=fat[at]
 target=270225;assert size>target+111
 ci,co=divmod(target,65536);cluster=chain[ci]
 absolute=15633072*512+len(meta)+(cluster-1)*65536+co
 return dict(log_bytes=size,chain=chain,target_log_offset=target,target_cluster=cluster,offset_in_cluster=co,absolute_byte_offset=absolute,lba=absolute//512,sector_offset=absolute%512,above_28bit_lba=absolute//512>=2**28,metadata_sha256=sha(meta),directory_records_sha256=sha(blob))
physical=k.parent/'physical-gpu-setup/002'
r=dict(case=case,physical_access=False,emulator_after=layout(out/'artifacts',json.loads((out/'allocation.json').read_text())),saved_physical_second_boot=layout(physical/'artifacts/scan',json.loads((physical/'allocation.json').read_text())),limits='Physical topology is from the saved scan after the second GPU boot, not the instant of the first malformed write. Matching logical offset does not imply identical disk sector, allocator history, controller or memory layout.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
