"""Independent transport and coverage negatives; no guest completion claim."""
import json
import struct
from pathlib import Path
from decode import decode

K = Path(__file__).resolve().parent
out = K / 'decoder-tests001.json'
assert not out.exists()
rows = [(0, 1, 0, 0)]
def pair(stage, arg=0, result=0):
    rows.extend([(stage, 0, arg, 0), (stage, 1, arg, result)])
for stage in range(1, 7): pair(stage, result=1 if stage in (1, 6) else 0)
pair(7)
for bus in range(2):
    for device in range(32):
        for function in range(8): pair(20, (bus << 8) | device | (function << 5), 0xffffffff)
pair(30); pair(31, 480, 1); pair(32)
rows.append((33, 0, 0, 0))
def encode(items):
    result = bytearray()
    for seq, (stage, phase, arg, status) in enumerate(items):
        fields = [0x58573420, seq, stage, phase, arg, status, 0]
        checksum = 0
        for field in fields: checksum ^= field
        result.extend(struct.pack('<8I', *fields, checksum))
    return bytes(result)
data = encode(rows)
assert decode(data)['complete']
assert not decode(data[:-32])['complete']
assert decode(data[:-64])['pending_call']['stage'] == 32
refused = 0
def reject(blob):
    global refused
    try: decode(blob)
    except ValueError: refused += 1; return
    raise AssertionError('Invalid trace accepted')
for at in range(len(data)):
    changed = bytearray(data); changed[at] ^= 1; reject(changed)
reject(data + b'x'); reject(data[:31]); reject(data + data[-32:])
reject(encode(rows[:1] + rows[-1:]))
changed = rows.copy(); changed[2] = (1, 1, 0, 0); reject(encode(changed))
changed = rows.copy(); changed[-1] = (33, 0, 0, 1); reject(encode(changed))
changed = rows.copy(); changed[15] = (20, 0, 32, 0); reject(encode(changed))
out.write_text(json.dumps(dict(passed=True, negatives=refused, full_records=len(rows),
    model_only=True, incomplete_traces_never_complete=True), indent=2)+'\n')
print(out.read_text())
