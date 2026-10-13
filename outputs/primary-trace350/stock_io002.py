"""Capture all reachable F: directory entries for the existing allocation analyzer."""
import importlib,json,struct,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'fatx-mapped-eof'))
from coldio import ColdIO
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/fatx-mapped-eof'));sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
def scan(disk,out):
    out.mkdir(parents=True,exist_ok=True)
    with ColdIO(disk) as io:
        part=m.fatx.open_partition(io,disk,'E');w=m.Writer(io,part)
        # Compare transport with the established independent qemu range reader.
        check=m.SliceIO(disk);transport=[]
        for offset,size in [(part.partition_offset,4096),(part.fat_offset,512),(part.cluster_offset(1),65536)]:
            io.seek(offset);check.seek(offset);a=io.read(size);assert a==check.read(size)
            transport.append(dict(offset=offset,size=size,sha256=m.sha(a)))
        io.seek(part.partition_offset);meta=io.read(part.cluster1_offset-part.partition_offset)
        (out/'fat-metadata.bin').write_bytes(meta)
        pending=[1];seen=set();records=bytearray();dirs=entries=0
        for first in pending:
            if not first:continue
            assert first not in seen,'Shared directory root';seen.add(first);ended=False
            for cluster in w.chain(first):
                dirs+=1;records.extend(struct.pack('<4I',1,first,cluster,w.fat[cluster])+bytes(64))
                data=w.read_cluster(cluster)
                for offset in range(0,len(data),64):
                    e=data[offset:offset+64];marker=e[0]
                    if marker in (0,255):ended=True
                    if ended or marker==229:continue
                    assert 1<=marker<=42
                    entries+=1;records.extend(struct.pack('<4I',2,first,cluster,offset)+e)
                    if e[1]&16:pending.append(struct.unpack_from('<I',e,44)[0])
        records.extend(struct.pack('<4I',5,dirs,entries,0)+bytes(64))
        (out/'directories.bin').write_bytes(records)
        (out/'snapshot.txt').write_text('SNAPSHOT_COMPLETE success=1 source=owned_closed_qcow2_readonly_nbd\n')
        report=dict(read_only=True,physical_access=False,transport_crosschecks=transport,bytes_read=io.read_bytes)
    subprocess.run([sys.executable,str(k/'analyze-allocation002.py'),'--capture',str(out),'--output',str(out.parent/'allocation.json')],check=True)
    report['nbd_process_closed']=True
    (out.parent/'allocation-capture.json').write_text(json.dumps(report,indent=2)+'\n')

def readers(io,disk):
    return {'E':m.Writer(io,m.fatx.open_partition(io,disk,'E'))}
