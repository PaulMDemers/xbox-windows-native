import json
from pathlib import Path
from decode import decode,REGS
k=Path(__file__).resolve().parent
original=(k.parent/'hd-timing-capture307/physical001/hd307.txt').read_bytes().decode().replace('XWN_HD307','XWN_HD308').splitlines()
lines=[]
for line in original:
 lines.append(line)
 if line.startswith('MMIO ') and 'offset=00680600 ' in line:
  stage=int(line.split()[1].split('=')[1])
  for pa in range(2):
   for reg in REGS:lines.append(f'ENC stage={stage} pass={pa} index={reg:02x} status=00000000 value={0x46 if reg==0x6c else 1:08x}')
  lines.append(f'ENCPIN stage={stage} profile=1 crc=b812777b')
data=('\r\n'.join(lines)+'\r\n').encode();assert decode(data)['passed'];n=0
for i,line in enumerate(lines):
 if line.startswith(('ENC ','ENCPIN ')):
  cases=[lines[:i]+lines[i+1:],lines[:i]+[line]+lines[i:]]
  if line.startswith('ENC '):
   cases += [lines[:i]+[line.replace('status=00000000','status=c0000001')]+lines[i+1:],lines[:i]+[line[:-8]+'00000100']+lines[i+1:]]
  for case in cases:
   try:decode(('\r\n'.join(case)+'\r\n').encode())
   except (AssertionError,ValueError):n+=1
   else:raise AssertionError(i)
for a,b in [(b'value=00000046',b'value=00000006'),(b'crc=b812777b',b'crc=b812777a'),(b'profile=1',b'profile=2')]:
 try:decode(data.replace(a,b))
 except (AssertionError,ValueError):n+=1
 else:raise AssertionError(a)
r=dict(passed=True,synthetic_transport_only=True,negative_controls=n,actual_encoder_readback=False)
p=k/'decoder-tests001.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n');print(r)
