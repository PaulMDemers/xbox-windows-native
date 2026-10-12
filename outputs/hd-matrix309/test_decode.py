import json
from pathlib import Path
from decode import decode,REGS,MATRIX
k=Path(__file__).resolve().parent
original=(k.parent/'hd-timing-capture307/physical001/hd307.txt').read_text().replace('XWN_HD307','XWN_HD309').splitlines()
lines=[]
for line in original:
 lines.append(line)
 if line.startswith('MMIO ') and 'offset=00680600 ' in line:
  stage=int(line.split()[1].split('=')[1])
  for pa in range(2):
   for reg,value in zip(REGS,[0]+MATRIX[stage-1]):lines.append(f'ENC stage={stage} pass={pa} index={reg:02x} status=00000000 value={value:08x}')
  lines.append(f'ENCPIN stage={stage} profile=1 crc=b812777b')
pack=lambda ls: ('\r\n'.join(ls)+'\r\n').encode()
data=pack(lines);assert decode(data)['passed'];n=0
for i,line in enumerate(lines):
 if line.startswith(('ENC ','ENCPIN ')):
  cases=[lines[:i]+lines[i+1:],lines[:i]+[line]+lines[i:]]
  if line.startswith('ENC '):
   cases += [lines[:i]+[line.replace('status=00000000','status=c0000001')]+lines[i+1:],lines[:i]+[line[:-8]+'00000100']+lines[i+1:]]
   if 'index=6c ' not in line:
    for bit in range(8):cases.append(lines[:i]+[line[:-8]+f'{int(line[-8:],16)^(1<<bit):08x}']+lines[i+1:])
  for case in cases:
   try:decode(pack(case))
   except (AssertionError,ValueError):n+=1
   else:raise AssertionError(i)
# Equal corruption in BOTH passes must fail the independent mode expectation.
for stage in range(1,4):
 for reg in REGS[1:]:
  case=[x[:-8]+f'{int(x[-8:],16)^1:08x}' if x.startswith(f'ENC stage={stage} ') and f'index={reg:02x} ' in x else x for x in lines]
  try:decode(pack(case))
  except (AssertionError,ValueError):n+=1
  else:raise AssertionError((stage,reg))
for value in [0,0x46,0xc6,0xff]:
 case=[x[:-8]+f'{value:08x}' if x.startswith('ENC ') and 'index=6c ' in x else x for x in lines]
 r=decode(pack(case));assert r['register_6c_semantics']=='UNKNOWN' and not r['full_encoder_readback']
for a,b in [(b'crc=b812777b',b'crc=b812777a'),(b'profile=1',b'profile=2')]:
 try:decode(data.replace(a,b))
 except (AssertionError,ValueError):n+=1
 else:raise AssertionError(a)
p=k/'decoder-tests001.json';assert not p.exists();r=dict(passed=True,synthetic_transport_and_matrix=True,negative_controls=n,actual_encoder_readback=False,register_6c_unknown_examples=4)
p.write_text(json.dumps(r,indent=2)+'\n');print(r)
