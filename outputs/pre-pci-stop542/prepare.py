# SPDX-License-Identifier: MIT
"""Pinned late checkpoint; no compile, network, or runtime parent reuse."""
import datetime,hashlib,json,shutil,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];O=Path('C:/xwn542/package001')
sys.path.insert(0,str(W/'work/python-packages'))
import capstone
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
def digest(b):
 b=bytearray(b);b[0x36c:0x380]=hashlib.sha1(struct.pack('<I',len(b)-4096)+b[4096:]).digest();return bytes(b)
assert not O.exists() and not (K/'prepared001.json').exists()
assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
p=Path('C:/xwn490/build001/default.xbe');base=p.read_bytes()
assert sha(base)==read(K.parent/'context-adapter490/build001.json')['sha256']
orig=Path('E:/xwn374/build001/image-crom.bin');raw=orig.read_bytes()
assert sha(raw)=='49f1332526c4155bd16bc2d16d138d7cb67f8498c80bc19ad0b64cd4ab671301'
assert raw[0xf0:0xf5]==bytes.fromhex('bc00008002')
assert raw[0x200:0x205]==bytes.fromhex('e91b020000')
assert base[0x30f5:0x3205]==raw[0xf5:0x205]
# Each original byte span is asserted; never search/replace an opcode globally.
patches=[(0x30f0,bytes.fromhex('e90bff0700'),raw[0xf0:0xf5],'restore original MOV ESP'),
 (0x34f8,bytes.fromhex('e8630f0000'),b'\xe9'+struct.pack('<i',0x2680000-(0x26004f8+5)),'detour before PCI call'),
 (0x83000,bytes.fromhex('bc00008002'),bytes.fromhex('9090909090'),'preserve active C stack'),
 (0x8301f,bytes.fromhex('e9d100f8ff'),bytes.fromhex('faf4ebfc90'),'intentional terminal hold'),
 (0x83038,struct.pack('<I',0xa5),struct.pack('<I',0xf5),'late marker color'),
 (0x830ee,bytes.fromhex('817f10a5000000'),bytes.fromhex('817f10f5000000'),'matching guarded color')]
assert base.count(b'XWNBoot490a')==4
b=bytearray(base.replace(b'XWNBoot490a',b'XWNBoot542a'))
for off,old,new,why in patches:
 assert b[off:off+len(old)]==old,(why,b[off:off+len(old)].hex())
 assert len(old)==len(new);b[off:off+len(old)]=new
b=digest(b);assert len(b)==len(base)
undo=bytearray(b.replace(b'XWNBoot542a',b'XWNBoot490a'))
for off,old,new,why in patches:undo[off:off+len(old)]=old
assert digest(undo)==base
normalized=digest(b.replace(b'XWNBoot542a',b'XWNBoot490a'))
delta=[i for i,(x,y) in enumerate(zip(base,normalized)) if x!=y]
allowed=set(range(0x36c,0x380))
for off,old,new,why in patches:allowed.update(range(off,off+len(old)))
assert set(delta)<=allowed
assert b[0x30f0:0x34f8]==raw[0xf0:0x4f8]
assert b[0x34fd:0x3000+len(raw)]==raw[0x4fd:]
# BSS ends before the preserved marker; terminal boundary is an actual JMP.
assert 0x264663c+0x6283*4==0x265f048<0x2680000
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
ins=list(md.disasm(raw[0xf0:0x205],0x26000f0))
assert sum(i.size for i in ins)==0x115 and ins[-1].op_str=='0x2600420'
O.mkdir(parents=True);dest=O/'default.xbe';dest.write_bytes(b)
pins={str(x.resolve()):sha(x.read_bytes()) for x in [p,orig,K/'prepare.py',K.parent/'context-adapter490/build001.json',K.parent/'busy-handoff471/build001.json',K.parent/'marker-busy470/marker.S',K.parent/'marker-handoff466/after-stack.S',K.parent/'pre-c-stop541/final001.json',K.parent/'resolution-e374/build001.json',W/'src/boot/xromwell/boot_xbe/xbeboot.S']}
r=dict(prepared=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 images={'1':dict(path=str(dest),sha256=sha(b),bytes=len(b),remote='/E/Applications/XWNBoot542a')},pins=pins,
 patches=[dict(offset=o,old=a.hex(),new=n.hex(),reason=w) for o,a,n,w in patches],
 original490_reconstructed_exactly=True,normalized_changed_offsets=delta,payload_length_unchanged=True,
 setup_interval_identical_to374=True,hook_address=0x26004f8,hold_address=0x268001f,
 original_setup_disassembly=[dict(address=i.address,hex=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str) for i in ins],
 marker_masks={'before':255,'before_PCI':245},
 intended_outcome='Earlier amber, then alternating red/amber before PCI initialization, then intentional halt. Manual reset required.',
 limitations='Removing the earlier post-stack marker also removes its I/O/delay. This is a new instrumented checkpoint, not a one-variable causal comparison to541. Register/cache/SMBus host models do not prove physical execution.',
 physical_access=False,compiled=False,requires_watched_LED_and_manual_reset=True)
(K/'prepared001.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Prepared',sha(b))
