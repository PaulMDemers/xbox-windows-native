"""Decode actual host-produced bytes; inject independent transport negatives."""
import hashlib,json,struct
from pathlib import Path
from witness_decode import decode_witness,decode_refusal,classify
K=Path(__file__).resolve().parent;H=Path('C:/xwn487/host002')
out=K/'transport001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(status='running',physical_evidence=False,decoded_witnesses=0,decoded_refusals=0,negative_controls=0)
def fail(fn,*args):
    try:fn(*args)
    except ValueError:r['negative_controls']+=1;return
    raise AssertionError('negative accepted')
def save():out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
save()
try:
 primary=(H/'case00.bin').read_bytes();valid=(H/'witness000.bin').read_bytes()
 for p in H.glob('witness*.bin'):
    data=p.read_bytes();n=int(p.stem[7:])
    parent=(H/f'case{n:02d}.bin').read_bytes() if n<104 else primary
    if len(data)==256:decode_witness(data,parent);r['decoded_witnesses']+=1
    else:fail(decode_witness,data,parent)
 for pattern in ('refusal*.bin','newrefusal*.bin'):
    for p in H.glob(pattern):
     data=p.read_bytes()
     if len(data)==192:decode_refusal(data);r['decoded_refusals']+=1
     else:fail(decode_refusal,data)
 for size in range(256):fail(decode_witness,valid[:size],primary)
 fail(decode_witness,valid+b'\0',primary)
 # Every fixed/relational word and all reserved bytes, independently flipped.
 for word in list(range(16))+list(range(40,64)):
    for bit in range(32):
     b=bytearray(valid);b[word*4+bit//8]^=1<<(bit%8);fail(decode_witness,bytes(b),primary)
 for word,value in [(16,0),(21,0),(22,1),(23,1),(24,8),(25,4097),(30,8),(31,8),(32,0),(33,0),(34,0),(35,0),(36,3),(37,0),(38,0),(39,1)]:
    b=bytearray(valid);struct.pack_into('<I',b,word*4,value);fail(decode_witness,bytes(b),primary)
 # Complete-looking witness coexists with later failures; never promote to boot.
 for n in range(111,132):
    w=(H/f'witness{n:03d}.bin').read_bytes();f=(H/f'newrefusal{n:03d}.bin').read_bytes()
    if len(w)!=256:continue
    result=classify(primary,w,f or None)
    assert result['boundary_observed'] and result['boot_qualified'] is False and result['windows_started'] is None
    assert result['wrapper_refused']==bool(f)
 # Reusing an old namespace or mixing a pre-boundary refusal is forbidden.
 b=bytearray(valid);struct.pack_into('<I',b,12,0x48200101);fail(decode_witness,b,primary)
 fail(classify,primary,valid,(H/'refusal32.bin').read_bytes())
 r.update(status='passed',host_input_sha256={str(p):sha(p) for p in H.glob('*.bin')},limits='Models only; terminal witness cannot prove its own close or actual Windows entry.')
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:save()
