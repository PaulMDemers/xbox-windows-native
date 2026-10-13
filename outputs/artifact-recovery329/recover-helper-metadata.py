"""Test timestamp/checksum-only reconstruction against the existing full hash.

No candidate is accepted on similarity. Only exact original SHA256 is written.
The fresh compiler output is preserved untouched.
"""
import datetime
import hashlib
import json
import struct
import sys
from pathlib import Path
K=Path(__file__).resolve().parent
W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'))
import pefile
source=Path('E:/xwn329/helper001/wizard.exe')
dest=Path('E:/xwn329/helper-restored001')
assert not dest.exists() and not (K/'helper-metadata001.json').exists()
original=source.read_bytes()
b=bytearray(original)
pe=pefile.PE(data=original)
ts=pe.FILE_HEADER.get_field_absolute_offset('TimeDateStamp')
cs=pe.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum')
assert pe.generate_checksum()==pe.OPTIONAL_HEADER.CheckSum
expected=json.loads((W/'outputs/hd-ui313/build-review001.json').read_text())['binary_sha256']
struct.pack_into('<I',b,ts,0)
struct.pack_into('<I',b,cs,0)
padded=b+bytes(len(b)%2)
total=sum(struct.unpack('<'+'H'*(len(padded)//2),padded))
start=int(datetime.datetime(2026,10,12,0,0,tzinfo=datetime.timezone.utc).timestamp())
found=None
for timestamp in range(start,start+86400):
    struct.pack_into('<I',b,ts,timestamp)
    value=total+(timestamp&65535)+(timestamp>>16)
    while value>>16:
        value=(value&65535)+(value>>16)
    struct.pack_into('<I',b,cs,value+len(b))
    if hashlib.sha256(b).hexdigest()==expected:
        found=timestamp
        break
result=dict(passed=found is not None, hypothesis='Only COFF timestamp and PE checksum differ',
            timestamp_search_start=start,timestamp_search_end_exclusive=start+86400,
            input_sha256=hashlib.sha256(original).hexdigest(),expected_sha256=expected,
            original_build_record_unchanged=True,physical_access=False,guest_launched=False)
if found is not None:
    assert pefile.PE(data=bytes(b)).generate_checksum()==struct.unpack_from('<I',b,cs)[0]
    changed=[i for i,(a,z) in enumerate(zip(original,b)) if a!=z]
    assert all(i in range(ts,ts+4) or i in range(cs,cs+4) for i in changed)
    dest.mkdir()
    (dest/'wizard.exe').write_bytes(b)
    result.update(original_timestamp_recovered=found,output=str(dest/'wizard.exe'),changed_byte_offsets=changed,
                  output_sha256=hashlib.sha256((dest/'wizard.exe').read_bytes()).hexdigest())
assert source.read_bytes()==original
(K/'helper-metadata001.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
