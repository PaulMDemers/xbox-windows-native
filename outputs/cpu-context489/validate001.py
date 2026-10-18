"""Review actual closed capture bytes, instruction boundaries and parser negatives."""
import hashlib,json,re,struct
from pathlib import Path
from decode import decode
from review001 import review
K=Path(__file__).resolve().parent;out=K/'final-review.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
win=lambda p:Path('C:/'+p[7:]) if p.startswith('/mnt/c/') else Path(p)
b=json.loads((K/'build001.json').read_text());r=json.loads((K/'run001.json').read_text())
assert b['passed'] and r['passed'] and r['closed'] and not r['deadline'] and r['exit_code']==33
pins={}
for source in [b['files'],r['files']]:
 for p,v in source.items():
  p=win(p);assert sha(p)==v['sha256'];pins[str(p)]=v['sha256']
data=Path('C:/xwn489/host001/run001/capture.bin').read_bytes();result=review(data,b['symbols'])
elf=Path('C:/xwn489/host001/test.elf').read_bytes();sy=b['symbols']
assert elf[:7]==b'\x7fELF\x01\x01\x01'
phoff=struct.unpack_from('<I',elf,28)[0];phsize,phnum=struct.unpack_from('<HH',elf,42)
assert phsize==32
raw=None
for i in range(phnum):
 typ,off,va,pa,fs,ms,flags,align=struct.unpack_from('<8I',elf,phoff+i*32)
 if typ==1 and va<=sy['capture_begin']<sy['capture_end']<=va+fs:
  assert raw is None;raw=elf[off+sy['capture_begin']-va:off+sy['capture_end']-va]
assert raw is not None and len(raw)==313
dis=Path('C:/xwn489/host001/disassembly.txt').read_text()
instructions=[];covered=bytearray()
for line in dis.splitlines():
 m=re.match(r'^\s*([0-9a-f]+):\s*((?:[0-9a-f]{2}(?: |\t|$))+)',line)
 if not m:continue
 addr=int(m[1],16)
 if not sy['capture_begin']<=addr<sy['capture_end']:continue
 assert addr==sy['capture_begin']+len(covered)
 covered.extend(bytes.fromhex(m[2]))
assert covered==raw
allowed={'pushf','pusha','cmp','jne','jb','ja','mov','rdtsc','sldt','str','sgdtd','sidtd','lea','popa','popf','ret'}
for line in dis.splitlines():
 m=re.match(r'^\s*([0-9a-f]+):\s*([0-9a-f ]+)\t(.+)$',line)
 if not m:continue
 addr=int(m[1],16)
 if not sy['capture_begin']<=addr<sy['capture_end']:continue
 op=m[3].strip();mnemonic=op.split()[0];assert mnemonic in allowed,op
 assert not re.search(r'^mov\s+(cr[0-9]|cs|ds|es|fs|gs|ss)\s*,',op),op
 instructions.append(dict(address=addr,instruction=op))
assert len(instructions)==76,len(instructions)
# Branch targets stay inside the one capture function. No CALL, I/O, CR write,
# descriptor-table load, interrupt/DF control instruction appears in its listing.
for row in instructions:
 op=row['instruction']
 if op.split()[0] in ('jne','jb','ja'):
  target=int(op.split()[1],16);assert sy['capture_begin']<=target<sy['capture_end']
neg=0
def reject(fn,payload):
 global neg
 try:fn(payload)
 except ValueError:neg+=1;return
 raise AssertionError('malformed bytes accepted')
q=lambda x:review(x,sy)
for n in range(len(data)):reject(q,data[:n])
reject(q,data+b'\0')
timestamps=set(range(84,100))|set(range(244,260))
for offset in range(len(data)):
 if offset in timestamps:continue
 for bit in range(8):
  changed=bytearray(data);changed[offset]^=1<<bit;reject(q,changed)
for i in range(2):
 record=data[4+160*i:164+160*i]
 for size in range(160):reject(decode,record[:size])
 reject(decode,record+b'\0')
 changed=bytearray(record);changed[88:96]=bytes(8);reject(decode,changed)
assert all(sha(Path(p))==h for p,h in pins.items())
out.write_text(json.dumps(dict(passed=True,physical_access=False,closed=True,actual_assembled_capture_bytes=len(raw),capture_sha256=hashlib.sha256(raw).hexdigest(),instruction_rows=instructions,host_records=result,negative_controls=neg,private_files=pins,source_rehashed_unchanged=True,scope='synthetic privileged CPU execution only; no kernel-memory provider/page walk/descriptor contents/atomicity/Xbox boot authority'),indent=2)+'\n')
