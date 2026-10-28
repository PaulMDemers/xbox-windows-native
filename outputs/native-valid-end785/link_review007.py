"""Fresh ELF structure/relocation check and exact raw-byte comparison to failed capacity build.
Actual new instructions must separately pass direct, full-path and CPU tests.
"""
from pathlib import Path
import struct,json,hashlib,datetime
from relocate003 import entries,relocated
K=Path(__file__).resolve().parent;P=Path('C:/xwn785')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def elf(path):
 b=path.read_bytes();assert b[:7]==b'\x7fELF\x01\x01\x01'
 at=struct.unpack_from('<I',b,32)[0];size,num,ss=struct.unpack_from('<HHH',b,46);assert size==40
 rows=[struct.unpack_from('<10I',b,at+i*size) for i in range(num)];strings=b[rows[ss][4]:rows[ss][4]+rows[ss][5]]
 return {strings[r[0]:].split(b'\0',1)[0].decode():(r,b[r[4]:r[4]+r[5]]) for r in rows}
out=K/'link-review007.json';assert not out.exists()
meta=json.loads((K/'payload005.json').read_text());assert meta['passed']
old=json.loads((K/'payload004.json').read_text());assert not old['passed']
assert old['sources']==meta['sources']
for n,h in meta['sources'].items():assert sha(K/n)==h
for n,h in meta['files'].items():assert sha(P/'payload005'/n)==h
a=old['compile32']['command'];b=meta['compile32']['command']
assert [x.replace('payload004','payload005') for x in a]==b
e=elf(P/'payload005/native.elf');raw=(P/'payload005/native.bin').read_bytes();padded=(P/'payload005/payload.bin').read_bytes()
assert len(raw)==meta['unpadded_bytes']==14744<=15360 and len(padded)==15360
assert padded==raw+b'\xcc'*(15360-len(raw))
assert raw==(P/'payload004/native.bin').read_bytes()
allocated=[]
for name,(row,data) in e.items():
 if row[2]&2 and row[5]:
  assert row[1]!=8 and 0x100000<=row[3]<row[3]+row[5]<=0x100000+len(raw)
  i=row[3]-0x100000;assert raw[i:i+len(data)]==data
  assert all(i+len(data)<=lo or hi<=i for lo,hi in allocated)
  allocated.append((i,i+len(data)))
assert e['.text'][0][3]==0x100000 and e['.rodata'][0][3]%32==0
rows=entries((P/'payload005/relocations.stdout').read_text(),padded)
binary=[]
for name in ['.rel.text','.rel.eh_frame']:
 for offset,info in struct.iter_unpack('<II',e[name][1]):binary.append((offset-0x100000,info&255))
assert binary==[(r['offset'],1 if r['type']=='R_386_32' else 2) for r in rows]
for r in rows:
 if r['type']=='R_386_PC32':
  value=struct.unpack_from('<i',raw,r['offset'])[0];target=0x100000+r['offset']+value
  # CALL rel32 is relative to the next instruction; unwind relative words are not.
  if r['offset']<len(e['.text'][1]):
   assert raw[r['offset']-1]==0xe8;target+=4
  assert 0x100000<=target<0x100000+len(e['.text'][1])
for load in [0x1ef1000,0x1ed9000]:
 result=relocated(padded,rows,load);expected=bytearray(padded)
 for r in rows:
  if r['type']=='R_386_32':struct.pack_into('<I',expected,r['offset'],r['value']+load-0x100000)
 assert result==expected
out.write_text(json.dumps({'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical_access':False,'same_source_as_failed_capacity_build':True,'only_build_change':'larger padding reserve; raw executable bytes identical; owned IDT moved by separate page builder','instruction_equivalence_claim':False,'required_execution_checks':['model001','integration004','cpu-run001'],'ELF_sha256':sha(P/'payload005/native.elf'),'unpadded_bytes':len(raw),'payload_reserve':15360,'margin_bytes':15360-len(raw),'relocations':len(rows),'absolute_relocations':13,'allocated_sections':allocated},indent=2)+'\n')
print('PASS785 ELF structure, relocations and exact native executable bytes')
