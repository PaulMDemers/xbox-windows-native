"""Independent schema for actual 30-word read-only sample, including refusals."""
def validate(v):
 assert len(v)==30 and all(type(n)==int and 0<=n<=0xffffffff for n in v)
 code,count,mismatch,invalid,entry,exit,c0,c3,c4=v[:9]
 first,second,third=v[9:16],v[16:23],v[23:30]
 assert (entry^exit)&0x200==0
 cpu_bad=(c0&0x80000001)!=0x80000001 or bool(c4&0x20)
 if cpu_bad:assert code==0x7751 and count==mismatch==invalid==0 and v[9:]==[0]*21
 else:
  assert count==21
  assert mismatch==sum(1<<i for i in range(7) if len({first[i],second[i],third[i]})!=1)
  assert invalid==sum(1<<i for i in range(7) if any(a[i]&0xffff0000 for a in [first,second,third]))
  assert code==(0x7753 if invalid else 0x7752 if mismatch else 0x775)
 return dict(code=code,first=first,second=second,third=third,mismatch_mask=mismatch,invalid_mask=invalid,CPU=[c0,c3,c4],interrupt_enable_unchanged=True,scope='Read-only kernel samples; no atomicity, native, mode-switch or write/recovery proof')
