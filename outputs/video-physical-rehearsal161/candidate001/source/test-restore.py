"""Exercise cold reopen, neighbor integrity and allocation ownership transitions."""
import io,json,struct,sys
from pathlib import Path
from types import SimpleNamespace
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/native-windows-fatx-runtime'))
from bulk_fatx import Writer
from restore import restore
p=SimpleNamespace(entry_size=4,cluster_size=512,fat_offset=0,fat_size=512,
                  cluster_count=80,partition_offset=0,partition_size=80*512,
                  cluster1_offset=512,cluster_offset=lambda c:c*512)
fp=io.BytesIO(bytes(80*512));fp.seek(0);fp.write(struct.pack('<II',0xffffffff,0xffffffff))
fp.seek(512);fp.write(b'\xff'*512)
w=Writer(fp,p);w.write('neighbor.bin',b'N'*777);w.flush()
checks=0
for data in [b'A',b'B'*512,b'C'*513,b'D'*1700,b'E'*31,b'',b'F'*4097]:
    previous=set(w.chain(struct.unpack_from('<I',w.directory(1)['entries']['sample.bin'][2],44)[0])) if 'sample.bin' in w.directory(1)['entries'] else set()
    mode=restore(w,'sample.bin',data);w.flush();w=Writer(fp,p)
    assert w.read('sample.bin')==data;assert w.read('neighbor.bin')==b'N'*777;checks+=2
    current=set(w.chain(struct.unpack_from('<I',w.directory(1)['entries']['sample.bin'][2],44)[0]))
    if mode=='reallocated':assert not previous&current and all(w.fat[c]==0 for c in previous);checks+=1
    allocated={c for c in range(2,w.limit) if w.fat[c]}
    neighbor=set(w.chain(struct.unpack_from('<I',w.directory(1)['entries']['neighbor.bin'][2],44)[0]))
    assert not current&neighbor and allocated==current|neighbor;checks+=1
before=fp.getvalue();fat=w.fat[:]
try:restore(w,'sample.bin',b'X'*(100*512))
except RuntimeError:pass
else:raise AssertionError('Full disk must reject replacement')
assert fp.getvalue()==before and w.fat==fat;checks+=1
restore(w,'new/sub.bin',b'Z'*513);w.flush();w=Writer(fp,p)
assert w.read('new/sub.bin')==b'Z'*513 and w.read('neighbor.bin')==b'N'*777;checks+=1
(k/'restore-tests.json').write_text(json.dumps(dict(passed=True,checks=checks,
    scope='Offline disposable writer only; not guest storage or power-loss qualification'),indent=2)+'\n',encoding='utf-8')
print('Offline restore allocation/readback checks:',checks)
