"""Independent 104-word physical result checks; models are not hardware evidence."""
from prefix_schema import validate as prefix_validate

TARGET=[719,779,719,0,738,770,719]
BASELINE=[1279,1649,1279,0,1389,1429,1279]

def validate(v):
 assert len(v)==104 and all(type(n)==int and 0<=n<=0xffffffff for n in v)
 code,forward=v[:2];before,checked,restored=v[76:83],v[83:90],v[90:97]
 attempted,count,first,mask,enabled,expected,observed=v[97:104]
 assert forward in [0x742,0x7421,0x7422,0x7423,0x7424,0x7428,0x7429]
 assert enabled in [0,1] and 0<=mask<128
 # Validate the original prefix independently, retaining its exact full-byte checks.
 p=v[:76].copy();p[1]=0x742 if forward==0x7429 else forward
 p[0]=p[1] if forward==0x7421 else 0x7426 if not v[28] else 0x7425 if forward!=0x7422 and v[30] else p[1]
 prefix=prefix_validate(p)
 if forward in [0x7421,0x7422]:
  assert attempted==count==mask==enabled==expected==observed==0
  assert first==0xffffffff and checked==restored==[0xffffffff]*7
  assert code==p[0]
 else:
  assert before==BASELINE
  assert mask==sum(1<<i for i,(a,b) in enumerate(zip(before,restored)) if a!=b)
  assert enabled==int(mask==0)
  assert code==(0x7426 if not v[28] else 0x742a if mask else 0x7425 if v[30] else forward)
  if forward in [0x742,0x7429]:
   assert attempted==7
   if forward==0x742:
    assert count==7 and first==0xffffffff and checked==TARGET and expected==observed==0
   else:
    assert 0<=first<7 and count==first+1
    assert checked[:first]==TARGET[:first] and checked[first]!=TARGET[first]
    assert [expected,observed]==[TARGET[first],checked[first]]
    assert checked[first+1:]==[0xffffffff]*(6-first)
  else:
   assert attempted==count==expected==observed==0 and first==0xffffffff
   assert checked==[0xffffffff]*7
  if mask:assert v[18]==0x21 and v[30]&(1<<15)
 return {'code':code,'forward_status':forward,'prefix':prefix,
         'horizontal_before':before,'horizontal_checked':checked,'horizontal_restored':restored,
         'horizontal_checked_count':count,'horizontal_first_mismatch':None if first==0xffffffff else first,
         'horizontal_cleanup_mask':mask,'output_enable_attempted':bool(enabled),
         'CPU':v[11:14],'flags':v[8:11],'scope':'kernel horizontal-only checkpoint; not a visible mode switch'}
