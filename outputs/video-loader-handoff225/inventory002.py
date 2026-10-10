"""Pin actual XBE payload/linked ELF and derive bounded executable handoff sites."""
import hashlib,json,re,struct,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'inventory002.json'
assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
root=Path('/home/paul/xbox-windows-native/build/cromwell-physical-f-001')
old=json.loads((k.parent/'video-gpu-handoff216/handoff-inventory.json').read_text())
art=k/'artifacts/inventory002';art.mkdir(exist_ok=False)
pins={}
for name,source in {'xromwell.xbe':root/'xbe/xromwell.xbe','image-crom.elf':root/'obj/image-crom.elf','image-crom.bin':root/'obj/image-crom.bin','freeldr.sys':Path('/home/paul/xbox-windows-native/build/physical-f-loader/boot/freeldr/freeldr/freeldr.sys')}.items():
 p=art/name;p.write_bytes(source.read_bytes());assert sha(p)==sha(source)
 pins[name]=dict(path=str(p.relative_to(ws)),source=str(source),sha256=sha(p),bytes=p.stat().st_size)
assert pins['xromwell.xbe']['sha256']==old['binaries']['E/Applications/XWNFBoot/default.xbe']['sha256']
assert pins['freeldr.sys']['sha256']==old['binaries']['E/Applications/XWNFBoot/freeldr.sys']['sha256']
xbe=(art/'xromwell.xbe').read_bytes();raw=(art/'image-crom.bin').read_bytes();elf=(art/'image-crom.elf').read_bytes()
start,size=struct.unpack_from('<II',xbe,0x1080)
assert start==0x3000 and size==len(raw) and xbe[start:start+size]==raw
assert elf[:7]==b'\x7fELF\x01\x01\x01'
shoff=struct.unpack_from('<I',elf,32)[0];shsize,shnum=struct.unpack_from('<HH',elf,46)
sections=[]
for i in range(shnum):
 _,typ,flags,addr,off,n,_,_,_,_=struct.unpack_from('<10I',elf,shoff+i*shsize)
 if flags&2 and typ==1 and n:
  assert 0x03a00000<=addr<0x03a00000+len(raw) and elf[off:off+n]==raw[addr-0x03a00000:addr-0x03a00000+n]
  sections.append(dict(address=addr,bytes=n,sha256=hashlib.sha256(elf[off:off+n]).hexdigest()))
assert len(sections)==3
dis=subprocess.check_output(['/usr/bin/objdump','-d',str(art/'image-crom.elf')],text=True)
(art/'linked-disassembly.txt').write_text(dis)
symbols={name:int(addr,16) for addr,kind,name in (line.split(maxsplit=2) for line in subprocess.check_output(['/usr/bin/nm','-n',str(art/'image-crom.elf')],text=True).splitlines() if len(line.split())==3)}
sites={'producer_exit_entry':symbols['startReactOS.part.0'],'usb_stopped':0x03a0c506,'interrupts_revoked':0x03a0c530,'multiboot_transfer':0x03a0c6d8}
expected={'producer_exit_entry':'5789c756','usb_stopped':'c7c0604ea403','interrupts_revoked':'83c40c','multiboot_transfer':'c3ebfe'}
for name,a in sites.items():assert raw[a-0x03a00000:a-0x03a00000+len(bytes.fromhex(expected[name]))]==bytes.fromhex(expected[name])
assert raw[0xc501]==0xe8 and 0x03a0c506+struct.unpack_from('<i',raw,0xc502)[0]==symbols['BootStopUSB']
assert raw[0xc52f]==0xfa
freeldr=(art/'freeldr.sys').read_bytes();mb=freeldr.find(bytes.fromhex('02b0ad1b'),0,8192);assert mb>=0
header=list(struct.unpack_from('<8I',freeldr,mb));assert sum(header[:3])&0xffffffff==0
assert header[3]-header[4]==mb and header[5:7]==[0,0] and header[7]==0x200a20
sites['freeldr_entry']=header[7]
source_pins={};census=[]
pattern=re.compile(r'(?:PFIFO|PGRAPH|PRAMIN|RAMHT|RAMFC|MmClaimGpu|FD[0247][0-9A-F]{4}|fd[0247][0-9a-f]{4}|FB_START|FB_SIZE|BootStopUSB|cli\\n)')
for p in sorted(root.rglob('*')):
 if p.is_file() and p.suffix in ['.c','.h','.S','.s']:
  data=p.read_bytes();source_pins[str(p.relative_to(root))]=dict(sha256=sha(p),bytes=len(data))
  for n,line in enumerate(data.decode('utf-8',errors='replace').splitlines(),1):
   if pattern.search(line):census.append(dict(path=str(p.relative_to(root)),line=n,text=line))
for name,row in old['files'].items():
 if name.startswith('cromwell/'):assert source_pins[name[len('cromwell/'):]]['sha256']==row['sha256']
function_sizes={}
for line in subprocess.check_output(['/usr/bin/nm','-S','-n',str(art/'image-crom.elf')],text=True).splitlines():
 parts=line.split()
 if len(parts)==4 and parts[2] in ['t','T']:
  function_sizes[parts[3]]=(int(parts[0],16),int(parts[1],16))
closure={};todo=['startReactOS.part.0'];seen=set()
while todo:
 name=todo.pop()
 if name in seen:continue
 seen.add(name)
 if name not in function_sizes:
  closure[name]=dict(sized=False,calls=[],unresolved='No ELF function size; no decode across following embedded data');continue
 addr,n=function_sizes[name];body=subprocess.check_output(['/usr/bin/objdump','-d','--start-address='+hex(addr),'--stop-address='+hex(addr+n),str(art/'image-crom.elf')],text=True)
 calls=[line.strip() for line in body.splitlines() if re.search(r'\bcall\b',line)]
 closure[name]=dict(sized=True,address=addr,bytes=n,calls=calls)
 for line in calls:
  target=re.search(r'call\s+[0-9a-f]+ <([^>]+)>',line)
  if target and target[1] in symbols:todo.append(target[1])
r=dict(passed=True,scope=__doc__,physical_access=False,guest_launch=False,gpu_ownership_qualified=False,
 source_sha256=sha(Path(__file__)),binaries=pins,linked_load_sections=sections,xbe_payload_offset=start,
 xbe_payload_bytes=size,linked_image_matches_executing_payload=True,sites=sites,
 multiboot_file_offset=mb,multiboot_header=header,cromwell_symbols=symbols,
 source_pins=source_pins,consumer_source_leads=census,exit_direct_call_closure=closure,
 disassembly_sha256=sha(art/'linked-disassembly.txt'),tools={name:sha(Path('/usr/bin/'+name)) for name in ['objdump','nm']},
 source_relationship='Nine historical216 Cromwell source pins still match; remaining current source is a consumer lead. Linked ELF load sections match exact XBE bytes; not a clean rebuild or historical compiler-input claim.',
 limits='CPU shutdown and memory reservation do not prove GPU idle, backend drain or ownership release. Indirect calls/source census are explicitly bounded and incomplete for firmware/kernel consumers.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('225 exact executable bridge passed; sites',sites,'source leads',len(census))
