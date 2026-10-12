import importlib.util,re
from pathlib import Path
p=Path(__file__).resolve().parent.parent/'hd-timing-capture307/decode.py'
spec=importlib.util.spec_from_file_location('parent307decoder',p);parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
REGS=[0x6c,0xd6,0x2e,0x32,0x3c,0x3e,0x40,0xc4,0xc6,0xce,0xa0,0x9e,0x9c,0xba]
MATRIX=[[12, 170, 73, 144, 140, 140, 1, 156, 225, 33, 0, 0, 40], [12, 171, 73, 144, 140, 140, 1, 156, 225, 33, 0, 0, 40], [12, 173, 72, 144, 140, 140, 1, 156, 225, 140, 0, 0, 40]]

def decode(data,kernel=None):
 lines=data.decode('ascii').splitlines();assert all(lines)
 base=[x for x in lines if not x.startswith(('ENC ','ENCPIN '))]
 r=parent.decode(('\r\n'.join(base).replace('XWN_HD309','XWN_HD307')+'\r\n').encode(),kernel)
 rows=[]
 for stage in range(1,4):
  group=[x for x in lines if x.startswith('ENC stage='+str(stage)+' ')];assert len(group)==28
  values=[]
  for j,line in enumerate(group):
   m=re.fullmatch(r'ENC stage=(\d+) pass=(\d+) index=([0-9a-f]{2}) status=([0-9a-f]{8}) value=([0-9a-f]{8})',line);assert m
   st,pa,index,status,value=m.groups();assert int(st)==stage and int(pa)==j//14 and int(index,16)==REGS[j%14] and int(status,16)==0 and 0<=int(value,16)<=255;values.append(int(value,16))
  assert values[:14]==values[14:] and values[1:14]==MATRIX[stage-1]
  pin=[x for x in lines if x.startswith('ENCPIN stage='+str(stage)+' ')];assert pin==[f'ENCPIN stage={stage} profile=1 crc=b812777b']
  rows.append(dict(stage=stage,registers=dict(zip(map(hex,REGS),values[:14])),readback_identical_twice=True))
 assert len(lines)==len(base)+87
 r.update(addressed_configuration_matrix_passed=True,register_6c_semantics="UNKNOWN",full_encoder_readback=False,encoder=rows,encoder_access=True,source_pin_scope='Actual4034 entire AvSetDisplayMode CRC; no runtime SMBus write trace')
 return r
