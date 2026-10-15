import hashlib,json,subprocess,sys
from pathlib import Path
from writeio001 import WriteIO
K=Path(__file__).resolve().parent;P=Path('/mnt/c/xwn405/write-test001');assert not P.exists();P.mkdir()
disk=P/'test.qcow2';size=16*1024**2
subprocess.run(['qemu-img','create','-f','qcow2',str(disk),str(size)],check=True)
data=bytes((i*37+11)&255 for i in range(8192));negative=0
with WriteIO(disk,size,P) as io:
    assert io.read(8192)==bytes(8192)
    for pos in [512,size-8192]:io.seek(pos);io.write(data);io.flush();io.seek(pos);assert io.read(8192)==data
    for pos,n,kind in [(1,512,0),(0,1,0),(size,512,0),(size-512,1024,1),(0,0,2)]:
        try:io.request(kind,pos,n,data[:n] if kind==1 else b'')
        except AssertionError:negative+=1
        else:raise AssertionError('Bad request accepted')
sys.path.insert(0,str(K.parent/'fatx-mapped-eof'));from coldio import ColdIO
with ColdIO(disk) as io:
    for pos in [512,size-8192]:io.seek(pos);assert io.read(8192)==data
subprocess.run(['qemu-img','check',str(disk)],check=True)
(K/'write-test001.json').write_text(json.dumps(dict(passed=True,negative=negative,independent_readonly_transport=True,scope='Actual isolated host disk IO; not Xbox runtime'))+'\n')
