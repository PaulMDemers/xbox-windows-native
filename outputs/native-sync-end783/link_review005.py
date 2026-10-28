"""Compare failed padded ELF002 with compact ELF003 without executing either."""
from pathlib import Path
import struct,json,hashlib,datetime
K=Path(__file__).resolve().parent;P=Path('C:/xwn783')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def elf(path):
 b=path.read_bytes();assert b[:7]==b'\x7fELF\x01\x01\x01'
 at=struct.unpack_from('<I',b,32)[0];size,num,ss=struct.unpack_from('<HHH',b,46)
 assert size==40
 rows=[struct.unpack_from('<10I',b,at+i*size) for i in range(num)];strings=b[rows[ss][4]:rows[ss][4]+rows[ss][5]]
 return {strings[r[0]:].split(b'\0',1)[0].decode():(r,b[r[4]:r[4]+r[5]]) for r in rows}
a=elf(P/'payload002/native.elf');b=elf(P/'payload003/native.elf')
assert a['.text'][0][3]==b['.text'][0][3]==0x100000 and len(a['.text'][1])==len(b['.text'][1])==0x3210
assert b['.rodata'][0][3]%32==0 and a['.rodata'][1]==b['.rodata'][1]
def sy(d):return {v[2]:int(v[0],16) for l in (P/d/'symbols.stdout').read_text().splitlines() if len(v:=l.split())==3}
sa,sb=sy('payload002'),sy('payload003');ta,tb=bytearray(a['.text'][1]),bytearray(b['.text'][1]);count=0
for off,info in struct.iter_unpack('<II',a['.rel.text'][1]):
 i=off-0x100000;va=struct.unpack_from('<I',ta,i)[0];vb=struct.unpack_from('<I',tb,i)[0];kind=info&255
 if kind==1:
  ra=a['.rodata'][0][3];rb=b['.rodata'][0][3]
  assert va-ra==vb-rb
  if va<ra:
   assert i==0x3002 and va==sa['cs']-22 and vb==sb['cs']-22
   assert ta[i-3:i]==tb[i-3:i]==bytes.fromhex('8a8436')
   assert all(ra<=va+2*j<ra+8 for j in range(11,15))
  else:assert va<=ra+len(a['.rodata'][1])
 else:assert kind==2 and va==vb
 ta[i:i+4]=tb[i:i+4]=bytes(4);count+=1
assert ta==tb and count==15
assert len(a['.rel.text'][1])==len(b['.rel.text'][1]) and len(a['.rel.eh_frame'][1])==len(b['.rel.eh_frame'][1])==24
# Unwind records retain all bytes except their relative text offsets.
ea,eb=bytearray(a['.eh_frame'][1]),bytearray(b['.eh_frame'][1])
for (oa,ia),(ob,ib) in zip(struct.iter_unpack('<II',a['.rel.eh_frame'][1]),struct.iter_unpack('<II',b['.rel.eh_frame'][1])):
 i=oa-a['.eh_frame'][0][3];j=ob-b['.eh_frame'][0][3];assert i==j and ia&255==ib&255==2
 va=struct.unpack_from('<i',ea,i)[0];vb=struct.unpack_from('<i',eb,i)[0];assert oa+va==ob+vb
 ea[i:i+4]=eb[i:i+4]=bytes(4)
assert ea==eb
meta=json.loads((K/'payload003.json').read_text());assert meta['passed'] and meta['unpadded_bytes']<=14080
out=K/'link-review005.json';assert not out.exists()
out.write_text(json.dumps({'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'text_bytes':len(ta),'text_relocations':count,'text_equivalent_except_resolved_internal_addresses':True,'rodata_exact':True,'unwind_equivalent_except_relative_offsets':True,'old_ELF_sha256':sha(P/'payload002/native.elf'),'new_ELF_sha256':sha(P/'payload003/native.elf'),'new_raw_bytes':meta['unpadded_bytes'],'payload_reserve':14080,'physical_access':False},indent=2)+'\n')
print('PASS compact ELF equivalence, unchanged reserved bounds')
