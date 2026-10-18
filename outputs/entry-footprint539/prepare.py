# SPDX-License-Identifier: MIT
"""Prepare a same-layout post-stack-marker control, without compilation or IO."""
from pathlib import Path
import datetime,hashlib,json,shutil,struct
K=Path(__file__).resolve().parent;W=K.parents[1];O=Path('C:/xwn539/package001')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()

def digest(b):
    b=bytearray(b);b[0x36c:0x380]=hashlib.sha1(struct.pack('<I',len(b)-4096)+b[4096:]).digest();return bytes(b)

if __name__=='__main__':
    assert not O.exists() and not (K/'prepared001.json').exists()
    assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
    ordinary=Path('E:/xwn374/build001/default.xbe');parent=Path('C:/xwn490/build001/default.xbe')
    original=ordinary.read_bytes();base=parent.read_bytes()
    assert sha(original)=='6240a801d97c4894e56d516a934059da056446fb77cf895b5364bdd6cd24be9a'
    assert sha(base)==read(K.parent/'context-adapter490/build001.json')['sha256']
    off,short=struct.unpack_from('<II',original,0x1080);long=struct.unpack_from('<I',base,0x1084)[0]
    assert off==0x3000 and short==288316 and long==524862
    before=original[off:off+short];after=base[off:off+short]
    delta=[i for i,(a,b) in enumerate(zip(before,after)) if a!=b]
    assert delta==list(range(0xf0,0xf5)) and before[0xf0:0xf5]==bytes.fromhex('bc00008002')
    assert after[0xf0]==0xe9 and 0x26000f5+struct.unpack_from('<i',after,0xf1)[0]==0x2680000
    assert not any(base[off+short:off+0x80000])
    stub=Path('C:/xwn471/build001/stub.bin');assert base[off+0x80000:off+long]==stub.read_bytes()
    O.mkdir(parents=True);images={}
    for suffix,restore in [('a',False),('b',True)]:
        name='XWNBoot539'+suffix;assert base.count(b'XWNBoot490a')==4
        b=bytearray(base.replace(b'XWNBoot490a',name.encode()))
        if restore:b[off+0xf0:off+0xf5]=before[0xf0:0xf5]
        b=digest(b);p=O/name;p.mkdir();(p/'default.xbe').write_bytes(b)
        undo=bytearray(b.replace(name.encode(),b'XWNBoot490a'));undo[off+0xf0:off+0xf5]=after[0xf0:0xf5]
        assert digest(undo)==base
        images[suffix]=dict(path=str(p/'default.xbe'),sha256=sha(b),bytes=len(b),remote='/E/Applications/'+name,
            post_stack_marker=not restore,restored_original_instruction=restore,physical_qualified=False)
    a=(O/'XWNBoot539a/default.xbe').read_bytes().replace(b'XWNBoot539a',b'XWNBoot539b')
    b=(O/'XWNBoot539b/default.xbe').read_bytes()
    normalized=[i for i,(x,y) in enumerate(zip(digest(a),b)) if x!=y]
    assert set(normalized)<=set(range(0x36c,0x380))|set(range(0x30f0,0x30f5))
    pins={str(p):sha(p.read_bytes()) for p in [ordinary,parent,stub,K/'prepare.py',K.parent/'context-adapter490/build001.json',K.parent/'marker-handoff466/build001.py',K.parent/'marker-handoff466/after-stack.S',K.parent/'busy-handoff471/build001.json',K.parent/'marker-busy470/marker.S',K.parent/'context-pair536/comparison001.json']}
    r=dict(prepared=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),images=images,pins=pins,
        ordinary_payload_bytes=short,diagnostic_payload_bytes=long,payload_prefix_changed_offsets=delta,padding_bytes=0x80000-short,appended_stub_bytes=long-0x80000,
        normalized_pair_changed_file_offsets=normalized,unchanged=['image size','section extent','copy length','allocation requests','wrapper guards','pre-handoff marker','primary/witness/context IO','all instruction addresses','retained tail bytes'],
        changed_behavior='Case b restores original MOV ESP at026000f0 instead of detouring to the post-stack LED marker. Its failure halt is absent because that diagnostic is not executed; no marker success is fabricated.',
        physical_access=False,compiled=False,new_assembly=False,source_sha256=sha(Path(__file__).read_bytes()))
    (K/'prepared001.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:r[k] for k in ['prepared','ordinary_payload_bytes','diagnostic_payload_bytes','padding_bytes','appended_stub_bytes','normalized_pair_changed_file_offsets']}))
