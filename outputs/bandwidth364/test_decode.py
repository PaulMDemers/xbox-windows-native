import json,struct,hashlib
from pathlib import Path
from decode import decode,REC,BYTES
k=Path(__file__).resolve().parent;dest=k/'transport001.json';assert not dest.exists()
p=next((k.parent/'memory-physical359/artifacts/candidate001/E/xwnmemory359candidate001/sample0').glob('memory-before.bin.cold'))
o=list(struct.unpack('<16640I',p.read_bytes()));rows=[o[256+i*4:260+i*4] for i in range(o[14])]
o[9:14]=[960,540,3840,32,2073600]
selected=[]
for role in (0,1):
 base=o[7+role]
 selected += [r for r in rows if r[0]==role and (base&~4095)<=r[1]<=((base+2073600-1)&~4095)]
o[14]=len(selected);o[256:]=[x for row in selected for x in row]+[0]*(16384-4*len(selected))
w=[0]*(BYTES//4);w[:5]=[0x42575758,364,BYTES,4,15]
for slot in range(4):
 r=[0]*REC;r[:4]=[364,slot,0,slot&1];r[4:7]=[o[4],o[7],o[8]];r[7:13]=[0,7680,2560,360,921600,o[7]]
 r[14]=1000000;r[16]=100 if not slot&1 else 300;r[18]=200 if not slot&1 else 400;r[20]=300 if not slot&1 else 100;r[22]=400 if not slot&1 else 200
 r[24]=32;r[25]=1;r[27]=2;r[32]=1;r[64:64+16640]=o;r[64+16640:]=o;w[16+slot*REC:16+(slot+1)*REC]=r
pack=lambda a:struct.pack('<%dI'%len(a),*a)
blob=pack(w);assert decode(blob)['passed'];rejected=0
changes=[(0,1),(1,360),(2,BYTES-4),(3,3),(4,7),(5,1)]
for slot in range(4):
 base=16+slot*REC
 changes += [(base+n,v) for n,v in [(0,360),(1,9),(2,1),(3,2),(4,0),(7,7680*721),(8,7679),(9,3839),(10,539),(11,2073599),(12,0),(13,1),(14,0),(18,0),(22,0),(24,31),(25,3),(29,1),(30,1),(31,1),(32,0),(33,1),(64+3,16),(64+7,0),(64+16640+3,16)]]
for at,value in changes:
 a=w.copy();a[at]=value
 try:decode(pack(a))
 except ValueError:rejected+=1
 else:raise AssertionError((at,value))
for n in [0,1,4,BYTES-4,BYTES+4]:
 try:decode((blob+b'\0'*4)[:n])
 except ValueError:rejected+=1
 else:raise AssertionError(n)
dest.write_text(json.dumps(dict(passed=True,mutations=rejected,source_packet_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),scope='Synthetic364 envelope and geometry-reduced copies of immutable359 memory evidence; not new guest evidence'),indent=2)+'\n');print(rejected)
