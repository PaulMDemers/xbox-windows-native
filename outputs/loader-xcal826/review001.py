"""Exact-source/full-image review for the isolated826 physical diagnostic."""
from pathlib import Path
import datetime,hashlib,json,re
K=Path(__file__).resolve().parent;B=Path('C:/xwn826/build003')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
out=K/'review001.json';assert not out.exists()
r={'passed':False,'physical_access':False,'checks':{},'limitations':['Original XBE kernel allocation/bootstrap unchanged; actual kernel allocation behavior not modeled','Device/timing/cache models do not prove physical behavior','Stops before Windows; no desktop admission']}
try:
 b=read(K/'build003.json');assert b['passed']
 for n,h in b['source_pins'].items():assert sha(K/n)==h
 for n,h in b['artifacts'].items():assert sha(B/n)==h['sha256']
 for n,count in [('entry-model002.json',47),('transaction-model002.json',912)]:
  t=read(K/n);assert t['passed'] and len(t['cases'])==count
  r['checks'][n]=sha(K/n)
 assert read(K/'transaction-model002.json')['bounds_cases']==32770
 x=(B/'default.xbe').read_bytes();image=(B/'image-crom.bin').read_bytes()
 assert x[0x3000:0x3000+len(image)]==image
 dis=(B/'disassembly.stdout').read_text();entry=dis.split('<BootResetAction>:')[1].split('\n\n')[0]
 calls=re.findall(r'call\s+[^<]*<([^>]+)>',entry)
 assert calls==['__x86.get_pc_thunk.bx','XcalEntry826'],calls
 sym={a[2]:int(a[0],16) for l in (B/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}
 assert sym['BSS_END']<0x02700000<0x02800000<0x03700000
 t=(K/'transaction826.c').read_text()
 assert 'r32(g,0x600800)!=r->incoming_base' in t
 assert 'w32(g,0x600800,r->base)' in t and 'r->base!=0x03700000' in t
 assert 'r->incoming_base<0x02800000' in t
 assert 'i<16?i:(i|0x20)' in t and '((r->base>>18)&0x1fu)' in t
 c=(K/'physical001.py').read_text()
 assert c.count('f.sendcmd(COMMAND)')==1 and 'f.sock.settimeout(20)' in c
 assert "out.open('x')" in c and "assert not out.exists()" in c
 assert "read(Path('C:/xwn820/connection.json'))" in c
 r.update(passed=True,embedded_firmware_exact=True,early_calls=calls,bss_end=hex(sym['BSS_END']),
  fixed_reservation=[0x03700000,0x04000000],xbe_sha256=sha(B/'default.xbe'),firmware_sha256=sha(B/'image-crom.bin'),
  source_pins={p.name:sha(p) for p in K.glob('*.[ch]')},
  controller_sha256=sha(K/'physical001.py'),build_receipt_sha256=sha(K/'build003.json'))
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS exact826 full-image review; isolated held test only')
