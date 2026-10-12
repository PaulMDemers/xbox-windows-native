import copy,hashlib,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest()
b=Path('D:/xwn307/physical001/kernel307.bin').read_bytes();assert sha(b)=='717482bc649804080820f05723fce6cc8b114f6ca95d134c94d9d0ed1895083b'
host=json.loads((k/'host001.json').read_text());assert host['passed']
for n,h in host['private_files'].items():assert sha(Path(n).read_bytes())==h
lines=Path('D:/xwn310/host001/result.txt').read_text().splitlines();actual={}
for line in lines:
 v=line.split()
 if v[0]=='PROFILE':actual[int(v[1])]=dict(geometry=list(map(int,v[2:])),CR={},MM={},EN={})
 elif v[0] in ('CR','MM','EN'):actual[int(v[1])][v[0]][int(v[2],16)]=int(v[3],16)
for m,code in [(1,0x880b0a02),(2,0x880e0c03)]:
 ci=(code>>8)&255;mi=(code>>16)&255;ei=code&15
 indices=b[0x3410:0x3432];raw=b[0x3410+34*ci:0x3410+34*(ci+1)]
 cr=dict(zip(indices,raw));pitch=actual[m]['geometry'][2]//8
 cr[0x13]=pitch&255;cr[0x19]|=(pitch>>3)&0xe0;cr[0x25]|=(pitch>>6)&0x20;cr[0x28]=0x83
 mm=dict(zip(struct.unpack_from('<26I',b,0x2c58),struct.unpack_from('<26I',b,0x2c58+104*mi)))
 mm[0x680880]=struct.unpack_from('<I',b,0x2c08+mi*4)[0];mm[0x680600]=0x100030
 en=dict(zip(b[0x3654:0x3661],b[0x3654+13*ei:0x3654+13*(ei+1)]));en[0xba]=0x28
 assert actual[m]['CR']==cr and actual[m]['MM']==mm and actual[m]['EN']==en

r=json.loads((k.parent/'hd-matrix309/physical001/trial.json').read_text());assert r['qualification_passed'] and r['startup_and_five_hives_unchanged']
r=r['independent_log_review'];vectors=[];differences=[]
for m in [1,2]:
 row=r['pixels']['rows'][m-1];tm=r['timings'][m-1];en=r['encoder'][m-1]
 assert actual[m]['geometry']==[int(row['width']),int(row['height']),int(row['width'])*4,int(row['bytes']),int(m==2)]
 for reg,value in tm['crtc'].items():
  reg=int(reg,16);mask={0x19:0xe0,0x2d:0x01}.get(reg,255)
  vectors.append((m,'CR',reg,mask,value))
  if actual[m]['CR'][reg]!=value:differences.append(dict(mode=m,index=hex(reg),programmed=actual[m]['CR'][reg],readback=value,compared_mask=mask,other_bits_semantics='UNKNOWN; not claimed read-only'))
 for i,value in enumerate(row['fp']):
  offset=0x680800+4*i
  if offset in actual[m]['MM']:vectors.append((m,'MM',offset,0xffffffff,value))
  else:assert i in (7,15)
 vectors.append((m,'MM',0x680600,0xffffffff,tm['mmio']['0x680600']))
 for reg,value in en['registers'].items():
  reg=int(reg,16)
  if reg!=0x6c:vectors.append((m,'EN',reg,255,value))
def verify(vs):
 for mode,group,reg,mask,value in vs:assert actual[mode][group][reg]&mask==value&mask,(mode,group,hex(reg),value)
verify(vectors);negative=0
for i,v in enumerate(vectors):
 for bit in range(32):
  if v[3]&(1<<bit):
   changed=list(v);changed[4]^=1<<bit;test=vectors[:i]+[tuple(changed)]+vectors[i+1:]
   try:verify(test)
   except AssertionError:negative+=1
   else:raise AssertionError('Mutation accepted')
result=dict(passed=True,scope='Pure compiled profile output vs independent private stock facts and selected actual309 hardware reads. No programming sequence or Windows execution.',host_checks=host['checks'],physical_compared_fields=len(vectors),physical_value_negative_controls=negative,programmed_vs_readback_differences=differences,encoder_6c_programmed=70,encoder_6c_readback=0,encoder_6c_semantics='UNKNOWN',unobserved_crtc_fields=12,unobserved_mode_mmio_fields=13,private_kernel_sha256=sha(b),actual_trial_sha256=sha((k.parent/'hd-matrix309/physical001/trial.json').read_bytes()),actual_log_sha256=sha((k.parent/'hd-matrix309/physical001/hd309.txt').read_bytes()),native_loader_built=False,physical_deployed=False)
p=k/'review001.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n');print({x:result[x] for x in ['passed','physical_compared_fields','physical_value_negative_controls']})
