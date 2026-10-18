"""Independent ELF relocations and XBE extents; no physical execution claim."""
import hashlib,json,struct
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('C:/xwn499/build001');P=Path('C:/xwn497/build002')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def u32(b,n):return struct.unpack_from('<I',b,n)[0]
def string(b,n):
 assert 0<=n<len(b);end=b.index(0,n);return b[n:end].decode('ascii')
def elf(p):
 b=p.read_bytes();assert b[:7]==b'\x7fELF\x01\x01\x01'
 shoff=u32(b,32);ents,count,strings=struct.unpack_from('<HHH',b,46)
 assert ents==40 and 0<strings<count and shoff+count*40<=len(b)
 sections=[struct.unpack_from('<10I',b,shoff+i*40) for i in range(count)]
 def data(s):
  assert s[4]+s[5]<=len(b);return b[s[4]:s[4]+s[5]]
 names=data(sections[strings]);named={string(names,s[0]):i for i,s in enumerate(sections)}
 sy=sections[named['.symtab']];assert sy[9]==16
 raw=data(sy);snames=data(sections[sy[6]])
 symbols=[]
 for off in range(0,len(raw),16):
  n,value,size,info,other,index=struct.unpack_from('<IIIBBH',raw,off)
  symbols.append(dict(name=string(snames,n),value=value,size=size,section=index,info=info))
 return dict(bytes=b,sections=sections,named=named,data=data,symbols=symbols)

build=json.loads((K/'build001.json').read_text(encoding='utf-8'));assert build['status']=='compiled'
assert all(sha(Path(p.replace('/mnt/c/','C:/',1)))==v['sha256'] for p,v in build['files'].items())
host=json.loads((K.parent/'entry-receipt498/host001.json').read_text(encoding='utf-8'))
gate=O/'entry.S';assert hashlib.sha256(gate.read_bytes().replace(b'XWNBoot499a',b'XWNBoot498a')).hexdigest()==host['source_pins']['entry.S']
e=elf(O/'wrapper.elf');c=elf(O/'entry.o');symbols={s['name']:s['value'] for s in e['symbols'] if s['name']}
old=(P/'default.xbe').read_bytes();actual=(O/'default.xbe').read_bytes()
assert sha(P/'default.xbe')=='09e3043c10837f20a3aef7d2b94ac54145b047ff9fafe02fb111fd25425b9274'
base=0x10000;gate_va=symbols['entry498_gate'];data_va=symbols['entry498_record']
assert gate_va>=base+len(old) and symbols['entry498_continue']==0x11100
bases={c['named']['.text']:gate_va,c['named']['.data']:data_va}
external={'DiagNtCreateFile','DiagNtWriteFile','DiagNtFlushBuffersFile','DiagNtClose','DiagHalReturnToFirmware','entry498_continue'}
relocated={};relocs=[]
for name in ['.text','.data']:
 index=c['named'][name];raw=bytearray(c['data'](c['sections'][index]));start=bases[index]
 for rs in c['sections']:
  if rs[1]!=9 or rs[7]!=index:continue
  assert rs[9]==8
  rb=c['data'](rs)
  for off in range(0,len(rb),8):
   pos,info=struct.unpack_from('<II',rb,off);kind=info&255;s=c['symbols'][info>>8]
   assert pos+4<=len(raw) and kind in [1,2]
   if s['section']==0:assert s['name'] in external;target=symbols[s['name']]
   else:assert s['section'] in bases;target=bases[s['section']]+s['value']
   add=u32(raw,pos);value=(target+add-(start+pos if kind==2 else 0))&0xffffffff
   struct.pack_into('<I',raw,pos,value)
   relocs.append(dict(section=name,offset=pos,kind=kind,symbol=s['name'],target=target,resolved=value))
 relocated[name]=(start,bytes(raw))

def validate(b):
 assert b[:4]==b'XBEH' and u32(b,0x104)==base
 assert u32(b,0x10c)==len(b) and u32(b,0x11c)==1
 sec=u32(b,0x120)-base;assert sec==u32(old,0x120)-base and sec+56<=4096
 flags,va,virtual,rawptr,rawsize=struct.unpack_from('<5I',b,sec)
 assert (flags,va,rawptr)==(7,base+4096,4096)
 assert virtual==rawsize==len(b)-4096
 assert u32(b,0x128)^0xa8fc57ab==gate_va
 assert b[sec+36:sec+56]==hashlib.sha1(struct.pack('<I',rawsize)+b[rawptr:]).digest()
 expected=bytearray(old.replace(b'XWNBoot497a',b'XWNBoot499a'))
 for off,value in [(0x10c,len(b)),(0x128,gate_va^0xa8fc57ab),(sec+8,virtual),(sec+16,rawsize)]:struct.pack_into('<I',expected,off,value)
 expected[sec+36:sec+56]=b[sec+36:sec+56]
 assert b[:len(old)]==expected
 assert b.count(b'XWNBoot499a')==5 and b.count(b'XWNBoot497a')==0
 for start,raw in relocated.values():
  assert va<=start and start+len(raw)<=va+virtual
  assert b[start-base:start-base+len(raw)]==raw
 assert b[gate_va-base:gate_va-base+3]==bytes.fromhex('9c60fc')
 # Existing thunk table and original flags capture are included in exact prefix equality.
 assert b[0x1100:0x1107]==old[0x1100:0x1107]
 return True

r=dict(passed=False,physical_access=False,relocations=relocs)
try:
 validate(actual);count=0
 positions=set()
 for lo,hi in [(0,4),(0x104,0x12c),(0x34c,0x380),(0x1100,0x1107)]:positions.update(range(lo,hi))
 for start,raw in relocated.values():positions.update(range(start-base,start-base+len(raw)))
 for p in sorted(positions):
  b=bytearray(actual);b[p]^=1
  try:validate(bytes(b))
  except (AssertionError,struct.error):count+=1
  else:raise AssertionError(('accepted mutation',p))
 for b in [actual[:-1],actual+b'\0']:
  try:validate(b)
  except AssertionError:count+=1
  else:raise AssertionError('accepted extent')
 r.update(passed=True,mutations_rejected=count,sha256=sha(O/'default.xbe'),bytes=len(actual),
  gate_address=gate_va,old_entry_address=0x11100,record_address=data_va,
  actual_relocations_resolved=len(relocs),original_prefix_except_paths_headers_exact=True,
  core_text_bytes=len(relocated['.text'][1]),core_data_bytes=len(relocated['.data'][1]),
  new_entry_has_no_original_instruction_patch=True,
  historical_build_metadata_note='header_allowed_ranges in build001 is only a min/max summary; reviewer validates five exact header fields/ranges',
  executed=False)
except BaseException as ex:r['error']=repr(ex);raise
finally:
 r['inputs']={str(p):sha(p) for p in [O/'wrapper.elf',O/'entry.o',O/'entry.S',O/'default.xbe',P/'default.xbe',K/'review001.py']}
 assert not (K/'review001.json').exists();(K/'review001.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
print(json.dumps({k:v for k,v in r.items() if k not in ['inputs','relocations']}))
