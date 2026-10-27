"""Independent 116-word physical result checks; models are not hardware evidence."""
from prefix_schema import validate as prefix_validate

TARGET=[719,779,719,0,738,770,719]
BASELINE=[1279,1649,1279,0,1389,1429,1279]

def validate(v):
 assert len(v)==116 and all(type(n)==int and 0<=n<=0xffffffff for n in v)
 code,forward=v[:2];before,checked,restored=v[76:83],v[83:90],v[90:97]
 attempted,count,first,mask,enabled,expected,observed=v[97:104]
 c4,c4check,c4restore,c4attempt,cm,c5,c5check,c5restore=v[104:112]
 c5target,c5attempt,c5after,c4after=v[112:116]
 assert c5attempt in [0,1]
 assert c4attempt in [0,1] and 0<=cm<4
 assert forward in [0x746,0x7461,0x7462,0x7463,0x7464,0x7468,0x7469,0x746b,0x746d]
 assert enabled in [0,1] and 0<=mask<128
 # Validate the original prefix independently, retaining its exact full-byte checks.
 p=v[:76].copy();p[1]=0x746 if forward in [0x7469,0x746b,0x746d] else forward
 p[0]=p[1] if forward==0x7461 else 0x7466 if not v[28] else 0x7465 if forward!=0x7462 and v[30] else p[1]
 prefix=prefix_validate(p)
 if forward in [0x7461,0x7462]:
  assert attempted==count==mask==enabled==expected==observed==0
  assert first==0xffffffff and checked==restored==[0xffffffff]*7
  assert code==p[0]
 else:
  assert before==BASELINE
  assert mask==sum(1<<i for i,(a,b) in enumerate(zip(before,restored)) if a!=b)
  assert enabled==int(mask==0 and cm==0)
  assert code==(0x7466 if not v[28] else 0x746c if cm else 0x746a if mask else 0x7465 if v[30] else forward)
  if forward in [0x746,0x7469,0x746b,0x746d]:
   assert attempted==7
   if forward in [0x746,0x746b,0x746d]:
    assert count==7 and first==0xffffffff and checked==TARGET and expected==observed==0
   else:
    assert 0<=first<7 and count==first+1
    assert checked[:first]==TARGET[:first] and checked[first]!=TARGET[first]
    assert [expected,observed]==[TARGET[first],checked[first]]
    assert checked[first+1:]==[0xffffffff]*(6-first)
  else:
   assert attempted==count==expected==observed==0 and first==0xffffffff
   assert checked==[0xffffffff]*7
  if mask or cm:assert v[18]==0x21 and v[30]&(1<<15)
 if forward in [0x7461,0x7462]:
  assert c4attempt==cm==0 and [c4check,c4restore,c5check,c5restore]==[0xffffffff]*4
  if forward==0x7461:assert c4==c5==0
 else:
  assert [c4,c5]==[0xa7,0x31]
  assert cm==int(c4restore!=c4)+2*int(c5restore!=c5)
  assert c4attempt==int(forward in [0x746,0x746b,0x746d])
  if c4attempt:
   assert c4check<=255 and c5check<=255
   assert (c4check==93 and c5check==c5)==(forward in [0x746,0x746d])
  else:assert c4check==c5check==0xffffffff
 assert c5attempt==int(forward in [0x746,0x746d])
 if c5attempt:
  assert c5target==((c5check&0xe0)|0x1e) and c5after<=255 and c4after<=255
  assert (c5after==c5target and c4after==93)==(forward==0x746)
 else:assert c5target==0 and c5after==c4after==0xffffffff
 return {'cr04':{'before':c4,'checked':c4check,'after_CR05':c4after,'restored':c4restore,'attempted':c4attempt,'target':93},'cr05':{'before':c5,'checked_before_write':c5check,'after':c5after,'restored':c5restore,'target':c5target,'attempted':c5attempt},'crtc_recovery_mask':cm,'code':code,'forward_status':forward,'prefix':prefix,
         'horizontal_before':before,'horizontal_checked':checked,'horizontal_restored':restored,
         'horizontal_checked_count':count,'horizontal_first_mismatch':None if first==0xffffffff else first,
         'horizontal_cleanup_mask':mask,'output_enable_attempted':bool(enabled),
         'CPU':v[11:14],'flags':v[8:11],'scope':'kernel horizontal-only checkpoint; not a visible mode switch'}
