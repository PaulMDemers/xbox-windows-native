"""Independent binary reconstruction and direct control-flow inventory."""
import hashlib,json,re,struct,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('C:/xwn510/build001');P=Path('C:/xwn504/build001');R=Path('C:/xwn510/review001');out=K/'review001.json'
assert not out.exists() and not R.exists();R.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def win(p):return Path(p.replace('/mnt/c/','C:/',1))
build=read(K/'build001.json');host=read(K/'host001.json');assert build['status']=='compiled' and host['passed']
for record in [build,host]:
 for n,v in record['files'].items():assert sha(win(n))==v['sha256'],n
old=(P/'default.xbe').read_bytes();actual=(O/'default.xbe').read_bytes();assert sha(P/'default.xbe')=='95a9734048b552fb531cd0c83138f9d7b332c8542573a4f49d5fa385fb0b4ece'
base=struct.unpack_from('<I',old,0x104)[0];section=struct.unpack_from('<I',old,0x120)[0]-base
assert base==0x10000 and section==0x348 and len(old)==len(actual)==545088
expected=bytearray(old);paths=[]
needle=b'\\Device\\Harddisk0\\Partition1\\Applications\\XWNBoot504a\\'
for suffix in [b'entry.bin',b'report.bin',b'refusal.bin',b'handoff.bin',b'context.bin']:
 literal=needle+suffix+b'\0';assert old.count(literal)==1;at=old.index(literal);replacement=literal.replace(b'XWNBoot504a',b'XWNBoot510a')
 expected[at:at+len(literal)]=replacement;paths.append(dict(offset=at,bytes=len(literal),name=suffix.decode()))
target=struct.unpack_from('<I',old,0x128)[0]^0xa8fc57ab;assert target==0x94aff
stub=bytes([0xe9])+int(target-0x11105).to_bytes(4,'little',signed=True)
assert stub==Path('C:/xwn510/host001/trampoline.bin').read_bytes()
expected[0x1100:0x1105]=stub;struct.pack_into('<I',expected,0x128,0x11100^0xa8fc57ab)
expected[section+36:section+56]=hashlib.sha1(struct.pack('<I',len(expected)-0x1000)+expected[0x1000:]).digest()
expected=bytes(expected)
def qualify(b):
 if len(b)!=len(old) or b[0x1100]!=0xe9:raise ValueError('length/opcode')
 entry=struct.unpack_from('<I',b,0x128)[0]^0xa8fc57ab
 dest=0x11105+int.from_bytes(b[0x1101:0x1105],'little',signed=True)
 if entry!=0x11100 or dest!=target:raise ValueError('entry/branch target')
 if b!=expected:raise ValueError('unexpected image change')
 return True
qualify(actual)
assert actual[0x84877:0x84c18]==old[0x84877:0x84c18]
assert actual[0x85000:]==old[0x85000:].replace(b'XWNBoot504a',b'XWNBoot510a')
assert actual[0x1105:0x3000]==old[0x1105:0x3000]
assert actual[0x3000:0x84000]==old[0x3000:0x84000]
# Reconstruct each source without trusting the builder's reconstruction flag.
anchor=b'_start:\n    pushfd\n    pop dword ptr [diag_record+16]'
replacement=b'_start:\n.global entry510_trampoline\nentry510_trampoline:\n    jmp entry503_gate\n    .byte '+(','.join(hex(x) for x in old[0x1105:0x1107])).encode()
source_count=0
for n in ['xbeboot.S','xbe.S','font.S','witness.S','context.S','capture.S','entry.S','combined.S','indicator.S']:
 b=(O/n).read_bytes().replace(b'XWNBoot510a',b'XWNBoot504a')
 if n=='xbeboot.S':assert b.count(replacement)==1;b=b.replace(replacement,anchor)
 assert b==(P/n).read_bytes();source_count+=1
assert (O/'indicator.S').read_bytes()==(K.parent/'entry-indicator503/indicator.S').read_bytes()
assert b'.set entry498_continue, entry503_complete' in (O/'combined.S').read_bytes()
assert struct.unpack_from('<I',actual,0x850ec)[0]==0x94bac
cmd=['wsl','-d','Ubuntu','--','objdump','-dw','-Mintel','--start-address=0x94877','--stop-address=0x94c18','/mnt/c/xwn510/build001/wrapper.elf']
text=subprocess.check_output(cmd,text=True,timeout=20);(R/'control-flow-disassembly.txt').write_bytes(text.encode())
instructions={}
for line in text.splitlines():
 m=re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s*([a-z][a-z0-9]*)\s*(.*)',line)
 if m:
  address=int(m[1],16);raw=bytes.fromhex(m[2]);assert actual[address-base:address-base+len(raw)]==raw
  instructions[address]=dict(bytes=len(raw),mnemonic=m[3],operand=m[4])
assert instructions and min(instructions)==0x94877
cursor=0x94877
for address,i in sorted(instructions.items()):assert address==cursor;cursor+=i['bytes']
assert cursor==0x94c18
edges=[];indirect=[];returns=[]
allowed={0x1100c,0x11010,0x11014,0x11018,0x1101c,0x11020,0x11024,0x950ec}
for address,i in instructions.items():
 m=i['mnemonic'];op=i['operand']
 if m.startswith('j') or m.startswith('loop') or m=='call':
  if op.startswith('DWORD PTR ds:'):
   pointer=int(op.split(':')[1],16);assert pointer in allowed;indirect.append(dict(address=address,kind=m,pointer=pointer))
  else:
   dest=int(op.split()[0],16);assert dest in instructions and 0x94877<=dest<0x94c18;edges.append(dict(address=address,kind=m,target=dest))
 if m=='ret':returns.append(address)
assert {x['pointer'] for x in indirect}==allowed
assert all(x['target']>=0x94877 for x in edges)
positions=set(range(0,4096))|set(range(0x1100,0x1107))|set(range(0x84877,0x84c18))|set(range(0x85000,len(old)))
positions.update(range(0x1000,0x102c));positions.update(range(0x3000,0x84000,4096))
for p in paths:positions.update(range(p['offset'],p['offset']+p['bytes']))
rejected=0
for position in sorted(positions):
 b=bytearray(actual);b[position]^=1
 if position>=4096:b[section+36:section+56]=hashlib.sha1(struct.pack('<I',len(b)-4096)+b[4096:]).digest()
 try:qualify(bytes(b))
 except ValueError:rejected+=1;continue
 raise AssertionError(('mutation accepted',position))
for dest in [0,0x11100,0x11105,0x11107,0x94877,0x94afe,0x94b00,0x95000]:
 b=bytearray(actual);b[0x1101:0x1105]=int(dest-0x11105).to_bytes(4,'little',signed=True)
 b[section+36:section+56]=hashlib.sha1(struct.pack('<I',len(b)-4096)+b[4096:]).digest()
 try:qualify(bytes(b))
 except ValueError:rejected+=1;continue
 raise AssertionError(('wrong target accepted',dest))
assert sha(O/'default.xbe')==build['sha256'] and sha(P/'default.xbe')==build['inputs']['/mnt/c/xwn504/build001/default.xbe']
r=dict(passed=True,physical_access=False,executed_XBE=False,full_expected_image_exact=True,source_parent_reconstructions=source_count,bytes=len(actual),sha256=sha(O/'default.xbe'),
 stub_hex=stub.hex(),entry=0x11100,target=target,original_symbol_addresses_unchanged=True,new_data_page_unchanged=0x95000,
 file_LED_code_unchanged_bytes=0x94c18-0x94877,path_literals=paths,direct_edges=edges,indirect_edges=indirect,return_sites=returns,
 static_control_flow_scope='all direct edges remain inside diagnostic; indirect edges limited to seven kernel thunk slots and fixed failure-adapter pointer; external kernel effects not proven',
 old_preparation_fallthrough_guard=0x11105,negative_controls=rejected,
 private_files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in R.iterdir() if p.is_file()},source_sha256=sha(Path(__file__)))
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps({n:r[n] for n in ['passed','sha256','negative_controls','source_parent_reconstructions','file_LED_code_unchanged_bytes']}))
