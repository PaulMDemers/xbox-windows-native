import json,sys,struct
from pathlib import Path
from decode import decode,CR,MM
k=Path(__file__).resolve().parent
old=(k.parent/'hd-physical292/physical001/hd292.txt').read_text().replace('XWN_HD292','XWN_HD307').splitlines()
lines=[]
for line in old:
 lines.append(line)
 if line.startswith('SETTINGS'):
  lines+=['KPAGE offset=00000000 valid=1','KERNEL base=80010000 bytes=4096 avset=80010100 avoption=80010200 smbwrite=80010300 smbread=80010400 pages=1 valid=1 saved=1']
 if line.startswith('FP ') and 'index=15 ' in line:
  stage=int(line.split()[1].split('=')[1])
  lines += [f'TIMING stage={stage} index_before=7 index_after=7 flags_before=00000202 flags_after=00000202']
  lines += [f'CRTC stage={stage} index={x:02x} value=00' for x in CR]
  lines += [f'MMIO stage={stage} offset={x:08x} value=00000000' for x in MM]
data=('\r\n'.join(lines)+'\r\n').encode();kernel=bytearray(4096);kernel[:2]=b'MZ';struct.pack_into('<I',kernel,0x3c,0x100);kernel[0x100:0x104]=b'PE\0\0';struct.pack_into('<I',kernel,0x150,4096)
assert decode(data,kernel)['passed'];tests=[]
for a,b in [(b'index_after=7',b'index_after=8'),(b'flags_after=00000202',b'flags_after=00000002'),(b'pages=1',b'pages=2'),(b'valid=1 saved',b'valid=0 saved'),(b'saved=1',b'saved=0'),(b'avset=80010100',b'avset=8000ffff'),(b'index=39 value=00',b'index=39 value=100'),(b'offset=00680508',b'offset=00680509'),(b'crc=dfa8cb56',b'crc=dfa8cb57')]:
 assert a in data
 try:decode(data.replace(a,b,1),kernel)
 except (AssertionError,ValueError):tests.append(a.decode())
 else:raise AssertionError(a)
for i,line in enumerate(lines):
 if line.startswith(('KPAGE','KERNEL','TIMING','CRTC','MMIO')):
  for new in [lines[:i]+lines[i+1:],lines[:i]+[line]+lines[i:]]:
   try:decode(('\r\n'.join(new)+'\r\n').encode(),kernel)
   except (AssertionError,ValueError):tests.append('drop/duplicate:'+str(i))
   else:raise AssertionError(i)
r=dict(passed=True,synthetic_transport_only=True,negative_controls=len(tests),actual_timing_values_qualified=False,original292_log_unchanged=True)
p=k/'decoder-tests001.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n');print(r)
