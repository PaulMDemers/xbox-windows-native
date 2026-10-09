"""Reject short/malformed external descriptors instead of classifying repaired bytes."""
import random,struct
from analyze import configuration,parse
good=bytes.fromhex('0902200001010080320904000002584200000705820320000407050203200004')
r=configuration(good);assert r['interfaces'][0]['classification']=='xid_interface'
cases=[good[:n] for n in range(len(good))]
for offset,value in [(0,8),(1,3),(2,31),(4,2),(9,0),(9,1),(13,1),(18,6),(25,8)]:
 b=bytearray(good);b[offset]=value;cases.append(bytes(b))
for b in cases:
 try:configuration(b)
 except ValueError:pass
 else:raise AssertionError(b.hex())
raw=b'USB_PROBE_BEGIN 1 123 0\r\nUSB_PROBE_END 0 0 1\r\n'
assert parse(raw)['complete']
for b in [raw[:-1],raw[:-27],raw+b'garbage\r\n',raw.replace(b'USB_PROBE_BEGIN 1',b'USB_PROBE_BEGIN 2')]:
 try:parse(b)
 except (ValueError,AssertionError):pass
 else:raise AssertionError('accepted incomplete log')
rng=random.Random(207)
for n in range(10000):
 b=bytearray(good)
 for _ in range(1+n%4):b[rng.randrange(len(b))]=rng.randrange(256)
 try:configuration(bytes(b))
 except ValueError:pass
 # IndexError/struct.error, unexpected exceptions and a nonterminating walk are bugs.
print('PASS',len(cases)+10006,'descriptor mutation/framing checks; synthetic host tests, no hardware claim')
