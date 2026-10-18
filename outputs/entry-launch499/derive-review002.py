from pathlib import Path
K=Path(__file__).resolve().parent
p=K/'review002.py';assert not p.exists()
b=(K/'review001.py').read_bytes()
old=b"b=bytearray(actual);b[p]^=1\n"
new=b"b=bytearray(actual);b[p]^=1\n  if p>=4096:\n   sec=u32(actual,0x120)-base\n   b[sec+36:sec+56]=hashlib.sha1(struct.pack('<I',len(b)-4096)+b[4096:]).digest()\n"
assert b.count(old)==1
b=b.replace(old,new).replace(b'review001.py',b'review002.py').replace(b'review001.json',b'review002.json')
p.write_bytes(b)
