"""Port source-only transaction oracle to actual full826 linked image."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;P=K.parent/'native-visible825/model003.py'
t=P.read_text();pin=hashlib.sha256(P.read_bytes()).hexdigest()
t=t.replace("P=Path('C:/xwn825/payload009')","P=Path('C:/xwn826/build002')")
t=t.replace("OUT=K/'model003.json'","OUT=K/'transaction-model001.json'")
a=t.index("b=json.loads(");z=t.index("pack=lambda",a)
t=t[:a]+'''b=json.loads((K/'build002.json').read_text());assert b['passed']
for n,v in b['artifacts'].items():assert sha((P/n).read_bytes())==v['sha256']
for n,h in b['source_pins'].items():assert sha((K/n).read_bytes())==h
blob=(P/'image-crom.bin').read_bytes()
syms={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}
'''+t[z:]
t=t.replace('FB=0x03c5c000;ALLOC=3686400','FB=0x03700000;ALLOC=0x00900000')
t=t.replace('0x3c5c000,ALLOC,ALLOC,1,1','0x03700000,ALLOC,3686400,1,1')
t=t.replace('3375000,1]','3375000,1,0x03c5c000]')
t=t.replace('c.mem_map(0x100000,0x10000);c.mem_write(0x100000,blob)','c.mem_map(0x2600000,0x100000);c.mem_write(0x2600000,blob)')
t=t.replace('0x600800:req[1]','0x600800:req[15]')
t=t.replace('c.mem_read(RP,60)','c.mem_read(RP,64)').replace('c.mem_read(0x100000,len(blob))','c.mem_read(0x2600000,len(blob))')
t=t.replace('range(15):run','range(16):run')
t=t.replace('for size in (3686400,0xffffffff):','for size in (0x00900000,0xffffffff):')
t=t.replace('want=base>=0x2000000 and base+size<=0x4000000 and not (base<0x2800000 and base+size>0x2600000)','want=base==0x03700000 and size==0x00900000')
t=t.replace("run('IF-enabled'","run('incoming-base-unaligned',bad=(15,0x03c5c001),expected=3)\n run('incoming-base-too-high',bad=(15,0x03fff000),expected=3)\n run('scanout-disagrees-with-request',pre=('mm',0x600800,0x03600000),expected=5)\n run('IF-enabled'")
(K/'transaction_model001.py').write_text(t)
(K/'model-source001.json').write_text(json.dumps({'source_only_oracle':str(P),'sha256':pin,'full_image':True},indent=2)+'\n')
