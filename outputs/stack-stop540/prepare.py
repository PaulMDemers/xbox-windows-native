# SPDX-License-Identifier: MIT
"""Replace only the successful post-stack return with an intentional CLI/HLT loop."""
import datetime,hashlib,json,shutil,struct
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('C:/xwn540/package001')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
def digest(b):
 b=bytearray(b);b[0x36c:0x380]=hashlib.sha1(struct.pack('<I',len(b)-4096)+b[4096:]).digest();return bytes(b)
assert not O.exists() and not (K/'prepared001.json').exists()
assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
p=Path('C:/xwn490/build001/default.xbe');base=p.read_bytes()
assert sha(base)==read(K.parent/'context-adapter490/build001.json')['sha256']
s=read(K.parent/'busy-handoff471/build001.json')['stub_symbols']
address=s['after_stack_ready'];off=0x3000+address-0x2600000
original=base[off:off+5]
assert original[0]==0xe9 and address+5+struct.unpack_from('<i',original,1)[0]==0x26000f5
assert base.count(b'XWNBoot490a')==4
b=bytearray(base.replace(b'XWNBoot490a',b'XWNBoot540a'))
b[off:off+5]=bytes.fromhex('faf4ebfc90')
b=digest(b);assert len(b)==len(base)
undo=bytearray(b.replace(b'XWNBoot540a',b'XWNBoot490a'));undo[off:off+5]=original
assert digest(undo)==base
normalized=digest(b.replace(b'XWNBoot540a',b'XWNBoot490a'))
delta=[i for i,(x,y) in enumerate(zip(base,normalized)) if x!=y]
assert set(delta)<=set(range(0x36c,0x380))|set(range(off,off+5))
assert b[0x30f0:0x30f5]==base[0x30f0:0x30f5]
assert b[0x3000+0x80000+40+16:0x3000+0x80000+40+20]==struct.pack('<I',0xa5)
O.mkdir(parents=True);dest=O/'default.xbe';dest.write_bytes(b)
pins={str(x.resolve()):sha(x.read_bytes()) for x in [p,K/'prepare.py',K.parent/'context-adapter490/build001.json',K.parent/'busy-handoff471/build001.json',K.parent/'marker-busy470/marker.S',K.parent/'marker-handoff466/after-stack.S',K.parent/'entry-footprint539/final001.json']}
r=dict(prepared=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 images={'1':dict(path=str(dest),sha256=sha(b),bytes=len(b),remote='/E/Applications/XWNBoot540a')},pins=pins,
 hold_address=address,hold_file_offset=off,old_instruction_hex=original.hex(),new_instruction_hex='faf4ebfc90',
 normalized_changed_offsets=delta,original490_reconstructed_exactly=True,
 entry_and_loader_and_pre_stack_bytes_unchanged=True,payload_length_unchanged=True,
 marker_masks={'before':255,'after_stack':165},
 intended_outcome='Amber earlier, alternating red/green after stack setup, then intentional halt. No Windows boot. Manual reset required after observation.',
 physical_access=False,compiled=False,requires_watched_LED_and_manual_reset=True,
 limitations='Indicator transaction may fail; an absent color is not proof of absent entry. SMC/cache/interrupt behavior is not qualified by host models.')
(K/'prepared001.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Prepared',sha(b),hex(address))
