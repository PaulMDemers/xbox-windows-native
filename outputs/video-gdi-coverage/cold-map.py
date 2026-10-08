"""Read an owned closed/immutable disk's pagefile chain without guest driver code."""
import struct,sys
from common import *
case,phase=sys.argv[1:];assert case in ['control001','candidate001'] and phase in ['before','after']
out=k/case/(phase+'-pagefile-map.json');assert not out.exists()
f=read(k/('fixture-'+case+'.json'))
disk=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'] if phase=='before' else ws/('work/runs/nt5-vgdi-'+case+'/hdd.qcow2')
if phase=='before':assert sha(disk)==f['fixture_sha256']
else:assert (disk.parent/'cleanup.json').exists()
with ColdIO(disk) as io:
    w=readers(io,disk)['F'];dc,off,entry=w.directory(1)['entries']['pagefile.sys']
    first,size=struct.unpack_from('<II',entry,44);assert size==96*1024*1024 and not entry[1]&16
    chain=list(w.chain(first));assert len(chain)==(size+w.p.cluster_size-1)//w.p.cluster_size
    def extents(length):
        rows=[];remaining=length
        for cluster in chain:
            if not remaining:break
            n=min(remaining,w.p.cluster_size);at=w.p.cluster_offset(cluster)-w.p.partition_offset
            assert 0<=at<at+n<=w.p.partition_size
            if rows and rows[-1]['volume_byte_offset']+rows[-1]['byte_length']==at:rows[-1]['byte_length']+=n
            else:rows.append(dict(byte_length=n,volume_byte_offset=at))
            remaining-=n
        assert not remaining
        return rows+[dict(byte_length=0,volume_byte_offset=0)]
    r=dict(scope=__doc__,case=case,phase=phase,physical_access=False,file='pagefile.sys',file_size=size,first_cluster=first,clusters=chain,cluster_size=w.p.cluster_size,partition_offset=w.p.partition_offset,partition_size=w.p.partition_size,first_cluster_disk_offset=w.p.cluster_offset(first),directory_entry_hex=entry.hex(),directory_cluster=dc,directory_offset=off,requested_65536=extents(65536),whole_file=extents(size),oracle_sha256={n:sha(p) for n,p in [('script',Path(__file__)),('bulk_fatx',ws/'outputs/native-windows-fatx-runtime/bulk_fatx.py'),('fatx_stage_boot',Path('/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts/fatx_stage_boot.py'))]})
save(out,r);print(case,phase,'pagefile clusters',len(chain),'64KiB map',r['requested_65536'])

