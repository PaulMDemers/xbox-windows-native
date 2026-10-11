"""Malformed native evidence and raw-input decoding regressions, no hardware."""
import importlib.util,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('native_xid_parser',k/'analyze.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
device='1201100100000040ffffffff000100000001'
config='0902200001010080320904000002584200000705810320000407050203200004'
xid='1042000101011406ffffffffffffffff'
neutral=b'\x00\x14'+bytes(18)
active=struct.pack('<BBH8B4h',0,20,0x91,255,128,64,1,2,3,42,200,-32768,32767,-1,0)
def log(report=active):
 return ('XWN_XID_CAPTURE 1 physical\r\nDEVICE 1 0 18 '+device+'\r\nCONFIG 2 0 32 '+config+'\r\nENDPOINT 129 3 32 4\r\nENDPOINT 2 3 32 4\r\nXID 3 0 16 '+xid+'\r\nREADY 4 0 3 129\r\nINPUT 1 0 20 '+neutral.hex()+'\r\nINPUT 25 0 20 '+report.hex()+'\r\nCAPTURE_END 2 0\r\n').encode()
b=log();r=m.parse(b);assert r['native_capture_passed'] and r['distinct_reports']==2
assert r['reports'][1]['decoded']['sticks']==[-32768,32767,-1,0]
assert r['reports'][1]['decoded']['analog']['left_trigger']==42
checks=3
for size in range(len(b)):
 try:m.parse(b[:size])
 except (ValueError,UnicodeError):checks+=1
 else:raise AssertionError(('accepted truncation',size))
for old,new in [(b'CAPTURE_END 2',b'CAPTURE_END 3'),(b'INPUT 25 0 20',b'INPUT 25 0 32'),(b'ENDPOINT 129',b'ENDPOINT 130'),(b'READY 4 0 3 129',b'READY 4 0 3 130'),(b'INPUT 25',b'INPUT 0'),(b'XID 3 0 16',b'XID 3 0 15'),(b'ENDPOINT 2 3 32 4',b'ENDPOINT 2 2 32 4'),(b'0040ffffffff',b'0040eeeeeeee')]:
 try:m.parse(b.replace(old,new))
 except ValueError:checks+=1
 else:raise AssertionError(('accepted malformed',old,new))
for offset in [0,1]:
 v=bytearray(active);v[offset]^=1
 r=m.parse(log(bytes(v)));assert not r['native_capture_passed'];checks+=1
r=m.parse(b.replace(b'CAPTURE_END 2 0',b'CAPTURE_END 2 1'));assert not r['native_capture_passed'];checks+=1
r=m.parse(b.replace(b'CAPTURE_END',b'CAPTURE_DEADLINE 45000\r\nCANCEL 45000 0\r\nDRAINED 45002 -205\r\nCAPTURE_END'));assert r['native_capture_passed'];checks+=1
try:m.parse(b.replace(b'CAPTURE_END',b'CAPTURE_DEADLINE 45000\r\nCANCEL 45000 0\r\nCAPTURE_END'))
except ValueError:checks+=1
else:raise AssertionError('undrained session accepted')
(k/'parser-tests.json').write_text(json.dumps(dict(checks=checks,passed=True,physical_access=False),indent=2)+'\n')
print(checks,'parser checks passed')
