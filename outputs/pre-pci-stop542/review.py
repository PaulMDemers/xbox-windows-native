# SPDX-License-Identifier: MIT
"""Pin original source and decode exact C/checkpoint intervals; no console access."""
import datetime,hashlib,json,re,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'))
import capstone
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'review001.json';assert not out.exists()
root='/home/paul/xbox-windows-native/build/resolution-e374-build001/source/'
sources={};texts={}
for rel,h in [('boot/BootResetAction.c','b27a08d5c4e18d331d2794ba0f50731d2768d5edc6addbeba3148a6b942612df'),('lib/misc/BootLibrary.c','9ee047b2a1cc68ae885c0ad5ee569648e12359bd7017d2a10bac878d29ff7312')]:
 b=subprocess.run(['wsl','-d','Ubuntu','-u','paul','--exec','cat',root+rel],check=True,capture_output=True,timeout=20).stdout
 assert hashlib.sha256(b).hexdigest()==h;sources[root+rel]=h;texts[rel]=b.decode()
rel='drivers/pci/BootInterrupts.c';h='b8a7e00bcf4c49b36479506705be4b4cd99b3829a0cdbc27ef85c0e4a596449c'
b=subprocess.run(['wsl','-d','Ubuntu','-u','paul','--exec','cat',root+rel],check=True,capture_output=True,timeout=20).stdout
assert hashlib.sha256(b).hexdigest()==h;sources[root+rel]=h
source_vectors=[(int(n,16),sym) for n,sym in re.findall(r'\{\s*(0x[0-9a-f]+),\s*\(u32\)(\w+)\s*\}',b.decode())];assert len(source_vectors)==33
rawp=Path('E:/xwn374/build001/image-crom.bin');raw=rawp.read_bytes()
assert sha(rawp)=='49f1332526c4155bd16bc2d16d138d7cb67f8498c80bc19ad0b64cd4ab671301'
mp=Path('E:/xwn374/build001/image-crom.map');assert sha(mp)=='fcf5aec3505d0177f0725931d85e6108c716b355eee7eb0a69bf6941b9eb41f2'
symbols={name:int(addr,16) for addr,name in re.findall(r'^\s+(0x[0-9a-f]+)\s+(\w+)\s*$',mp.read_text(),re.M)}
assert [struct.unpack_from('<II',raw,0x460c0+i*8) for i in range(33)]==[(i,symbols[n]) for i,n in source_vectors]
assert raw[0x460c0+33*8:0x460c0+34*8]==bytes(8)
q=read(K/'prepared001.json');p=Path(q['images']['1']['path']);image=p.read_bytes();assert sha(p)==q['images']['1']['sha256']
payload=image[0x3000:0x3000+524862]
assert payload[0x80000:0x80005]==b'\x90'*5
assert payload[0x80038:0x8003c]==struct.pack('<I',0xf5)
assert payload[0x800ee:0x800f5]==bytes.fromhex('817f10f5000000')
assert payload[0x4f8:0x4fd]==b'\xe9'+struct.pack('<i',0x2680000-0x26004fd)
assert payload[0xf0:0x4f8]==raw[0xf0:0x4f8]
assert payload[0x4fd:len(raw)]==raw[0x4fd:]
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
intervals=[]
for lo,hi,label in [(0x420,0x4fd,'first C through PCI call'),(0xefe0,0xf007,'memcpy'),(0xf3a0,0xf3c5,'memory manager'),(0xf9b0,0xfafa,'IDT and PIC setup'),(0xf6c0,0xf6cd,'original APIC disable'),(0x25fc6,0x25fce,'PIC register thunks')]:
 ins=list(md.disasm(raw[lo:hi],0x2600000+lo));assert sum(i.size for i in ins)==hi-lo
 intervals.append(dict(label=label,start=0x2600000+lo,end=0x2600000+hi,instructions=[dict(address=i.address,hex=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str) for i in ins]))
assert symbols['BootPciPeripheralInitialization']==0x2601460
assert next(i for i in intervals[0]['instructions'] if i['address']==0x26004f8)['operands']=='0x2601460'
phases=[dict(red=bool(0xf5&(0x80>>i)),green=bool(0xf5&(8>>i))) for i in range(4)]
assert phases==[{'red':True,'green':False},{'red':True,'green':True}]*2
pub=W/'src/boot/xromwell/boot/BootResetAction.c';assert sha(pub)==sources[root+'boot/BootResetAction.c']
r=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_sha256=sha(Path(__file__)),
 wsl_source_pins=sources,source_tree='0a1b542e92c8697422892c9cfaed633a5aed0de7',source_vector_symbols=source_vectors,
 pins={str(p.resolve()):sha(p) for p in [rawp,mp,pub,K.parent/'pre-c-stop541/prepare.py',K.parent/'pre-c-stop541/review001.json']},
 checkpoint=0x26004f8,original_instruction='CALL BootPciPeripheralInitialization',replacement='JMP same-stack terminal marker',
 checkpoint_esp=0x27fdf84,LED_phases=phases,intervals=intervals,physical_access=False,
 limitations='Preserves original IDT/PIC/APIC setup without claiming correctness on hardware. Actual marker bytes preserve current C stack; halt is deliberate, no Windows or PCI execution intended.')
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n');print('PASS original source, C boundary, stack-preserving marker review')
