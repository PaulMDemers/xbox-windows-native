"""Independent ELF relocations and XBE extents; no physical execution claim."""
import hashlib,json,struct
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('C:/xwn504/build001');P=Path('C:/xwn499/build001')
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


H=K.parent/'entry-indicator503'
build=json.loads((K/'build001.json').read_text(encoding='utf-8'));assert build['status']=='compiled'
assert all(sha(Path(p.replace('/mnt/c/','C:/',1)))==v['sha256'] for p,v in build['files'].items())
assert not (K/'review001.json').exists()
host=json.loads((H/'host001.json').read_text(encoding='utf-8'));assert host['passed'] and host['closed']
assert sha(O/'indicator.S')==host['source_pins']['indicator.S']
assert (O/'entry.S').read_bytes().replace(b'XWNBoot504a',b'XWNBoot498a')==(H/'entry498.S').read_bytes()
assert (O/'combined.S').read_bytes().replace(b'entry.S',b'entry498.S')==(H/'combined.S').read_bytes()
# Independently reconstruct all parent sources; new integration/import lines only.
parent=(P/'xbeboot.S').read_bytes()
new=(O/'xbeboot.S').read_bytes().replace(b'XWNBoot504a',b'XWNBoot499a')
new=new.replace(b'#include "combined.S"',b'.set entry498_continue, _start\n#include "entry.S"')
for name,ordinal in [('Entry503HalWriteSMBusValue',50),('Entry503KeDelayExecutionThread',99)]:
 fragment=(name+':\n\t.long 0x80000000 + '+str(ordinal)+'\n').encode();assert new.count(fragment)==1;new=new.replace(fragment,b'')
assert new==parent
for name in ['xbe.S','font.S','witness.S','context.S','capture.S','entry.S']:
 assert (O/name).read_bytes().replace(b'XWNBoot504a',b'XWNBoot499a')==(P/name).read_bytes()
e=elf(O/'wrapper.elf');c=elf(O/'combined.o');symbols={s['name']:s['value'] for s in e['symbols'] if s['name']}
old=(P/'default.xbe').read_bytes();actual=(O/'default.xbe').read_bytes()
assert sha(P/'default.xbe')=='22d3a9224965159a53cb188be9530f1b211aff8480d3d5773405d7e2974cf6d9'
base=0x10000;gate_va=symbols['entry498_gate'];data_va=symbols['entry498_record'];entry=symbols['entry503_gate']
prior=json.loads((K.parent/'entry-launch499/build001.json').read_text(encoding='utf-8'))
assert gate_va==prior['wrapper_symbols']['entry498_gate']
assert symbols['_start']==0x11100 and symbols['entry498_continue']==symbols['entry503_complete']
bases={c['named']['.text']:gate_va,c['named']['.data']:data_va}
external={'DiagNtCreateFile','DiagNtWriteFile','DiagNtFlushBuffersFile','DiagNtClose','DiagHalReturnToFirmware','Entry503HalWriteSMBusValue','Entry503KeDelayExecutionThread'}
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
assert {r['symbol'] for r in relocs if r['symbol'] in external}==external
for item in c['symbols']:
 if item['name'] and item['section'] in bases:
  assert symbols[item['name']]==bases[item['section']]+item['value'],item['name']
# Full-image reconstruction: unchanged prefix, precisely two imports, independently
# relocated combined code/data, zero linker gap, and explicit five header ranges.
end=data_va+len(relocated['.data'][1])-base
expected=bytearray(end);expected[:gate_va-base]=old[:gate_va-base].replace(b'XWNBoot499a',b'XWNBoot504a')
for start,raw in relocated.values():expected[start-base:start-base+len(raw)]=raw
assert gate_va+len(relocated['.text'][1])<=data_va
struct.pack_into('<II',expected,0x1020,0x80000032,0x80000063)
sec=u32(old,0x120)-base
assert sec==0x348
for off,value in [(0x10c,end),(0x128,entry^0xa8fc57ab),(sec+8,end-4096),(sec+16,end-4096)]:struct.pack_into('<I',expected,off,value)
expected[sec+36:sec+56]=hashlib.sha1(struct.pack('<I',end-4096)+expected[4096:]).digest()
expected=bytes(expected)
imports=[166,173,184,190,236,198,187,49,50,99]
def validate(b):
 assert len(b)==end and b[:4]==b'XBEH' and u32(b,0x104)==base
 assert u32(b,0x10c)==len(b) and u32(b,0x11c)==1 and u32(b,0x120)==base+sec
 assert struct.unpack_from('<5I',b,sec)==(7,base+4096,end-4096,4096,end-4096)
 assert u32(b,0x128)^0xa8fc57ab==entry
 assert u32(b,0x158)^0x5b6d40b6==0x11000
 assert list(struct.unpack_from('<11I',b,4096))==[0x80000000+n for n in imports]+[0]
 assert b[sec+36:sec+56]==hashlib.sha1(struct.pack('<I',len(b)-4096)+b[4096:]).digest()
 assert b==expected
 assert b.count(b'XWNBoot504a')==5 and b.count(b'XWNBoot499a')==0
 assert b[0x3000:0x84000]==old[0x3000:0x84000]
 assert u32(b,symbols['Entry503Return']-base)==symbols['entry503_failed_file']
 assert struct.unpack_from('<q',b,symbols['entry503_interval']-base)[0]==-20000000
 return True
r=dict(passed=False,physical_access=False,executed=False,relocations=relocs)
try:
 validate(actual);positions=set(range(0,4096))|set(range(4096,0x1100))
 for start,raw in relocated.values():positions.update(range(start-base,start-base+len(raw)))
 positions.update(range(gate_va+len(relocated['.text'][1])-base,data_va-base))
 positions.update(range(0x1100,0x1200));positions.update(range(0x3000,0x84000,4096))
 rejected=0
 for p in sorted(positions):
  b=bytearray(actual);b[p]^=1
  if p>=4096:b[sec+36:sec+56]=hashlib.sha1(struct.pack('<I',len(b)-4096)+b[4096:]).digest()
  try:validate(bytes(b))
  except (AssertionError,struct.error):rejected+=1
  else:raise AssertionError(('accepted mutation',p))
 for b in [actual[:-1],actual+b'\0']:
  try:validate(b)
  except AssertionError:rejected+=1
  else:raise AssertionError('accepted extent')
 r.update(passed=True,mutations_rejected=rejected,sha256=sha(O/'default.xbe'),bytes=len(actual),
  new_entry=entry,gate_address=gate_va,record_address=data_va,old_entry_address=0x11100,
  actual_relocations_resolved=len(relocs),text_bytes=len(relocated['.text'][1]),data_bytes=len(relocated['.data'][1]),
  full_image_reconstructed=True,original_preparation_payload_exact_except_namespace=True,
  import_ordinals=imports,original_import_addresses_unchanged=True,
  entry_only_completion=symbols['entry503_complete'],failure_alias=symbols['entry503_failed_file'],
  original_preparation_execution=False,scope='Static relocation/source/header proof only; kernel APIs and console remain untested')
except BaseException as ex:r['error']=repr(ex);raise
finally:
 r['inputs']={str(p):sha(p) for p in [O/'wrapper.elf',O/'combined.o',O/'combined.S',O/'entry.S',O/'indicator.S',O/'default.xbe',P/'default.xbe',K/'review001.py']}
 (K/'review001.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
print(json.dumps({k:v for k,v in r.items() if k not in ['inputs','relocations']}))
