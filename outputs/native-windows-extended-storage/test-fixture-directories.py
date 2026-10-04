"""Regression: FATX directory tails use ff on creation and chain extension."""
import io,pathlib,sys,struct,types
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent/'native-windows-fatx-runtime'))
from bulk_fatx import Writer
size=512;p=types.SimpleNamespace(entry_size=4,cluster_size=size,fat_offset=0,fat_size=1024,cluster_count=256,partition_offset=0,partition_size=4096+255*size,cluster1_offset=4096,cluster_offset=lambda c:4096+(c-1)*size)
f=io.BytesIO(bytes(p.partition_size));f.write(struct.pack('<II',0xfffffff8,0xffffffff));f.seek(4096);f.write(b'\xff'*size)
w=Writer(f,p);directory=w.mkdir('/test');assert w.read_cluster(directory)==b'\xff'*size
for n in range(20):w.write('/test/file'+str(n),bytes([n]))
w.flush();cold=Writer(f,p);chain=list(cold.chain(directory));assert len(chain)==3
for c in chain:
 b=cold.read_cluster(c)
 assert all(b[i]!=0 for i in range(0,len(b),64)), 'Zero marker disagrees with native FATX driver'
for n in range(20):assert cold.read('/test/file'+str(n))==bytes([n])
print('PASS: new directory, two extensions, 20 files and ff tails after cold reopen')
