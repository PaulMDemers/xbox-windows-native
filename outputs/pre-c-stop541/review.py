# SPDX-License-Identifier: MIT
"""Independent source/binary boundary and color review; no physical access."""
import datetime,hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'review001.json';assert not out.exists()
root='/home/paul/xbox-windows-native/build/resolution-e374-build001/source/'
sources={}
for rel,expected in [('boot/BootStartup.S','3dfbb3c3fedfaa36d6c2c7b8429e9575008c4be3b2b7bf28cb3fff95456b858f'),('boot/BootResetAction.c','b27a08d5c4e18d331d2794ba0f50731d2768d5edc6addbeba3148a6b942612df')]:
 b=subprocess.run(['wsl','-d','Ubuntu','-u','paul','--exec','cat',root+rel],check=True,capture_output=True,timeout=20).stdout
 assert hashlib.sha256(b).hexdigest()==expected
 sources[root+rel]=expected
pub=W/'src/boot/xromwell/boot/BootResetAction.c'
assert sha(pub)==sources[root+'boot/BootResetAction.c']
text=pub.read_text();names=['MemoryManagementInitialization','BootInterruptsWriteIdt','BootPciPeripheralInitialization','BootAGPBUSInitialization','cache_disable','display_cpuid_update_microcode','cache_enable','BootDetectMemorySize','BootEepromReadEntireEEPROM','BootVgaInitializationKernelNG']
positions=[text.index(n+'(') for n in names];assert positions==sorted(positions)
mp=Path('E:/xwn374/build001/image-crom.map')
assert sha(mp)=='fcf5aec3505d0177f0725931d85e6108c716b355eee7eb0a69bf6941b9eb41f2'
assert '0x02600420                BootResetAction' in mp.read_text()
elf=Path('E:/xwn374/build001/image-crom.elf')
assert sha(elf)=='f64c05c1c07797945244b4a8db7fe79256db3a8f0fefac48cc8508b966cc2f0d'
q=read(K/'prepared001.json');image=Path(q['images']['1']['path']).read_bytes()
assert hashlib.sha256(image).hexdigest()==q['images']['1']['sha256']
assert image[0x83038:0x8303c]==bytes.fromhex('5f000000')
assert image[0x830ee:0x830f5]==bytes.fromhex('817f105f000000')
led=W/'src/boot/xromwell/boot_xbe/xbeboot.S';defs=led.read_text()
for i in range(4):
 assert f'#define LED_RED_C{i}\t0x{0x80>>i:02X}'.lower() in defs.lower()
 assert f'#define LED_GREEN_C{i}\t0x{0x08>>i:02X}'.lower() in defs.lower()
phases=[dict(red=bool(0x5f&(0x80>>i)),green=bool(0x5f&(8>>i))) for i in range(4)]
assert phases==[{'red':False,'green':True},{'red':True,'green':True}]*2
old=read(K.parent/'stack-stop540/interval-review001.json')
assert old['passed']
# The inherited handoff clears DF; this host test does not alter it on console.
def instructions(v):
 if isinstance(v,dict):
  if 'mnemonic' in v:yield v
  for x in v.values():yield from instructions(x)
 elif isinstance(v,list):
  for x in v:yield from instructions(x)
clds=[x for x in instructions(old) if x['mnemonic']=='cld']
assert [x['address'] for x in clds]==[606213,606638]
r=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_sha256=sha(Path(__file__)),
 source_tree='0a1b542e92c8697422892c9cfaed633a5aed0de7',wsl_source_pins=sources,
 pins={str(p.resolve()):sha(p) for p in [pub,mp,elf,led,K.parent/'stack-stop540/interval-review001.json']},
 first_C_address=0x2600420,checkpoint_address=0x2600200,first_C_initialization_order=names,
 LED_phases=phases,earlier_handoff_cld_instructions=clds,
 BSS=[0x264663c,0x265f048],IDT_clear=[0xb0000,0xb5000],marker=[0x2680000,0x2680000+574],
 observed_final_cr3_write_operand=0x800,original_code_not_modified=True,
 limitations='Static source/byte review plus modeled execution. CR3=0x800 write is existing code, not diagnosed as a defect or changed. No actual cache/MSR/descriptor or display proof.',physical_access=False)
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n');print('PASS source and boundary review')
