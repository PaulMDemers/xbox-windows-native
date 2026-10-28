"""Independent 143-word physical result checks; models are not hardware evidence."""
from prefix_schema import validate as prefix_validate

TARGET=[719,779,719,0,738,770,719]
BASELINE=[1279,1649,1279,0,1389,1429,1279]

def validate(v):
 assert len(v)==143 and all(type(n)==int and 0<=n<=0xffffffff for n in v)
 code,forward=v[:2];before,checked,restored=v[76:83],v[83:90],v[90:97]
 attempted,count,first,mask,enabled,expected,observed=v[97:104]
 c4,c4check,c4restore,c4attempt,cm,c5,c5check,c5restore=v[104:112]
 c5target,c5attempt,c5after,c4after=v[112:116]
 c0,c0target,c0attempt,c0after,c0restore,zm,c4after0,c5after0=v[116:124]
 c2,c2target,c2attempt,c2after,c2restore,bm,c0after2,c4after2,c5after2=v[124:133]
 c3,c3target,c3attempt,c3after,c3restore,em,c0after3,c2after3,c4after3,c5after3=v[133:143]
 assert c3attempt in [0,1] and em in [0,1]
 assert c2attempt in [0,1] and bm in [0,1]
 assert c0attempt in [0,1] and zm in [0,1]
 assert c5attempt in [0,1]
 assert c4attempt in [0,1] and 0<=cm<4
 assert forward in [0x753,0x7531,0x7532,0x7533,0x7534,0x7538,0x7539,0x753b,0x753d,0x753e,0x75310,0x75312]
 assert enabled in [0,1] and 0<=mask<128
 # Validate the original prefix independently, retaining its exact full-byte checks.
 p=v[:76].copy();p[1]=0x753 if forward in [0x7539,0x753b,0x753d,0x753e,0x75310,0x75312] else forward
 p[0]=p[1] if forward==0x7531 else 0x7536 if not v[28] else 0x7535 if forward!=0x7532 and v[30] else p[1]
 prefix=prefix_validate(p)
 if forward in [0x7531,0x7532]:
  assert attempted==count==mask==enabled==expected==observed==0
  assert first==0xffffffff and checked==restored==[0xffffffff]*7
  assert code==p[0]
 else:
  assert before==BASELINE
  assert mask==sum(1<<i for i,(a,b) in enumerate(zip(before,restored)) if a!=b)
  assert enabled==int(mask==0 and cm==0 and zm==0 and bm==0 and em==0)
  assert code==(0x7536 if not v[28] else 0x75313 if em else 0x75311 if bm else 0x753f if zm else 0x753c if cm else 0x753a if mask else 0x7535 if v[30] else forward)
  if forward in [0x753,0x7539,0x753b,0x753d,0x753e,0x75310,0x75312]:
   assert attempted==7
   if forward in [0x753,0x753b,0x753d,0x753e,0x75310,0x75312]:
    assert count==7 and first==0xffffffff and checked==TARGET and expected==observed==0
   else:
    assert 0<=first<7 and count==first+1
    assert checked[:first]==TARGET[:first] and checked[first]!=TARGET[first]
    assert [expected,observed]==[TARGET[first],checked[first]]
    assert checked[first+1:]==[0xffffffff]*(6-first)
  else:
   assert attempted==count==expected==observed==0 and first==0xffffffff
   assert checked==[0xffffffff]*7
  if mask or cm or zm or bm or em:assert v[18]==0x21 and v[30]&(1<<15)
 if forward in [0x7531,0x7532]:
  assert c4attempt==cm==0 and [c4check,c4restore,c5check,c5restore]==[0xffffffff]*4
  if forward==0x7531:assert c4==c5==0
 else:
  assert [c4,c5]==[0xa7,0x31]
  assert cm==int(c4restore!=c4)+2*int(c5restore!=c5)
  assert c4attempt==int(forward in [0x753,0x753b,0x753d,0x753e,0x75310,0x75312])
  if c4attempt:
   assert c4check<=255 and c5check<=255
   assert (c4check==93 and c5check==c5)==(forward in [0x753,0x753d,0x753e,0x75310,0x75312])
  else:assert c4check==c5check==0xffffffff
 assert c5attempt==int(forward in [0x753,0x753d,0x753e,0x75310,0x75312])
 if c5attempt:
  assert c5target==((c5check&0xe0)|0x1e) and c5after<=255 and c4after<=255
  assert (c5after==c5target and c4after==93)==(forward in [0x753,0x753e,0x75310,0x75312])
 else:assert c5target==0 and c5after==c4after==0xffffffff
 assert c0attempt==int(forward in [0x753,0x753e,0x75310,0x75312])
 if forward in [0x7531,0x7532]:
  assert zm==0 and c0restore==0xffffffff
  if forward==0x7531:assert c0==0
 else:
  assert c0==0xc8 and zm==int(c0restore!=c0)
 if c0attempt:
  assert c0target==92 and c0after<=255 and c4after0<=255 and c5after0<=255
  assert (c0after==92 and c4after0==93 and c5after0==62)==(forward in [0x753,0x75310,0x75312])
 else:assert c0target==0 and [c0after,c4after0,c5after0]==[0xffffffff]*3
 assert c2attempt==int(forward in [0x753,0x75310,0x75312])
 if forward in [0x7531,0x7532]:
  assert bm==0 and c2restore==0xffffffff
  if forward==0x7531:assert c2==0
 else:assert c2==0x9f and bm==int(c2restore!=c2)
 if c2attempt:
  assert c2target==89 and all(n<=255 for n in [c2after,c0after2,c4after2,c5after2])
  assert (c2after==89 and c0after2==92 and c4after2==93 and c5after2==62)==(forward in [0x753,0x75312])
 else:assert c2target==0 and [c2after,c0after2,c4after2,c5after2]==[0xffffffff]*4
 assert c3attempt==int(forward in [0x753,0x75312])
 if forward in [0x7531,0x7532]:
  assert em==0 and c3restore==0xffffffff
  if forward==0x7531:assert c3==0
 else:assert c3==0x8c and em==int(c3restore!=c3)
 if c3attempt:
  assert c3target==((c3&0xe0)|((779//8-1)&31)) and all(n<=255 for n in [c3after,c0after3,c2after3,c4after3,c5after3])
  assert (c3after==c3target and c0after3==92 and c2after3==89 and c4after3==93 and c5after3==62)==(forward==0x753)
 else:assert c3target==0 and [c3after,c0after3,c2after3,c4after3,c5after3]==[0xffffffff]*5
 return {'cr03':{'before':c3,'target':c3target,'attempted':c3attempt,'after':c3after,'restored':c3restore,'cleanup_mask':em,'CR00_after':c0after3,'CR02_after':c2after3,'CR04_after':c4after3,'CR05_after':c5after3},'cr02':{'before':c2,'target':c2target,'attempted':c2attempt,'after':c2after,'restored':c2restore,'cleanup_mask':bm,'CR00_after':c0after2,'CR04_after':c4after2,'CR05_after':c5after2},'cr00':{'before':c0,'target':c0target,'attempted':c0attempt,'after':c0after,'restored':c0restore,'cleanup_mask':zm,'CR04_after':c4after0,'CR05_after':c5after0},'cr04':{'before':c4,'checked':c4check,'after_CR05':c4after,'restored':c4restore,'attempted':c4attempt,'target':93},'cr05':{'before':c5,'checked_before_write':c5check,'after':c5after,'restored':c5restore,'target':c5target,'attempted':c5attempt},'crtc_recovery_mask':cm,'code':code,'forward_status':forward,'prefix':prefix,
         'horizontal_before':before,'horizontal_checked':checked,'horizontal_restored':restored,
         'horizontal_checked_count':count,'horizontal_first_mismatch':None if first==0xffffffff else first,
         'horizontal_cleanup_mask':mask,'output_enable_attempted':bool(enabled),
         'CPU':v[11:14],'flags':v[8:11],'scope':'kernel horizontal-only checkpoint; not a visible mode switch'}
