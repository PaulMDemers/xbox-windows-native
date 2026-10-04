import io,json,struct
from pathlib import Path
from types import SimpleNamespace
from bulk_fatx import Writer

results=[]
for entry in [2,4]:
    cluster=512;count=256;fat_size=4096;data_start=8192
    p=SimpleNamespace(entry_size=entry,cluster_size=cluster,cluster_count=count,
      partition_offset=0,partition_size=data_start+(count-1)*cluster,
      fat_offset=4096,fat_size=fat_size,cluster1_offset=data_start,
      cluster_offset=lambda c:data_start+(c-1)*cluster)
    f=io.BytesIO(bytes(p.partition_size));f.seek(p.fat_offset+entry);f.write(bytes([255])*entry)
    w=Writer(f,p);expected={}
    for i in range(37):
        name=f'WINNT/system32/file{i:03}.bin';data=bytes([i])*((i*71)%1900)
        expected[name]=data;w.write(name,data)
    w.mkdir('empty');w.write('forty-two-'+('x'*32),b'exact maximum name')
    try:w.write('x'*43,b'bad')
    except AssertionError:pass
    else:raise AssertionError('Accepted overlong name')
    try:w.write('WINNT/system32/file000.bin',b'overwrite')
    except AssertionError:pass
    else:raise AssertionError('Overwrote file')
    w.flush();cold=Writer(f,p)
    for name,data in expected.items():assert cold.read(name)==data
    directory=cold.mkdir('WINNT/system32');assert len(list(cold.chain(directory)))==5
    before=cold.fat[:]
    try:cold.allocate(10000)
    except RuntimeError:assert cold.fat==before
    else:raise AssertionError('Accepted oversized allocation')
    cold.fat[directory]=directory
    try:list(cold.chain(directory))
    except AssertionError:pass
    else:raise AssertionError('Accepted cycle')
    results.append({'fat_bits':entry*8,'files':37,'chained_directory_clusters':5,'cold_readback':True,'maximum_name_boundary':True,'overwrite_rejected':True,'allocation_failure_atomic':True,'cycle_rejected':True})
Path(__file__).with_name('bulk-writer-tests.json').write_text(json.dumps(results,indent=2)+'\n')
print('Chained FAT16/FAT32 directory and cold readback tests passed')
