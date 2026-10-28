"""Pure result-schema checks, independent of the execution harness."""
def validate(v):
 assert len(v)==76 and all(isinstance(n,int) and 0<=n<=0xffffffff for n in v)
 code,forward,mm_attempt,cr_attempt,first,expected,observed,checked=v[:8]
 assert forward in [0x768,0x7681,0x7682,0x7683,0x7684,0x7688]
 assert v[8]==v[10] and not v[9]&0x200
 assert 0<=mm_attempt<=11 and 0<=cr_attempt<=3 and v[28] in [0,1] and v[29] in [0,1]
 if forward==0x7681:
  assert code==forward and not (mm_attempt or cr_attempt or checked or v[28] or v[29])
  assert v[11]&0x80000001!=0x80000001 or v[13]&0x20
 else:
  assert v[11]&0x80000001==0x80000001 and not v[13]&0x20
  if forward==0x7682:
   assert not (mm_attempt or cr_attempt or checked)
   assert code==(0x7682 if v[28] else 0x7686)
  else:
   pairs=list(zip(v[31:42],v[53:64]))+list(zip(v[64:68],v[72:76]))
   pairs += [(v[a],v[b]) for a,b in [(17,18),(19,20),(21,22),(23,24),(25,26)]]
   mask=sum(1<<i for i,(a,b) in enumerate(pairs) if a!=b)
   assert v[30]==mask and v[29]==(mask==0)
   assert code==(0x7686 if not v[28] else 0x7685 if mask else forward)
   if forward in [0x768,0x7688]:
    assert [mm_attempt,cr_attempt]==[11,3]
    target=[0,0,0x10001000,0x10000000,0x10000000,0x10000000,0x10000000,0x21101100,2,0x00801080,0x40801080,0,0xe3,0x10,v[67]]
    values=v[42:53]+v[68:72]
    if forward==0x768:
     assert checked==15 and first==0xffffffff and values==target and expected==observed==0
    else:
     assert 0<=first<15 and checked==first+1
     assert values[:first]==target[:first] and values[first]!=target[first]
     assert expected==target[first] and observed==values[first]
     assert values[first+1:]==[0xffffffff]*(14-first)
   else:assert mm_attempt==cr_attempt==checked==0
 if forward not in [0x768,0x7688]:
  assert first==0xffffffff and expected==observed==0
  assert v[42:53]+v[68:72]==[0xffffffff]*15
 return {'code':code,'forward_status':forward,'first_mismatch':None if first==0xffffffff else first,
         'expected':expected,'observed':observed,'checked':checked,'cleanup_mask':v[30],
         'cleanup_ok':bool(v[29]),'selectors_restored':bool(v[28]),'CPU':v[11:14],'flags':v[8:11]}
