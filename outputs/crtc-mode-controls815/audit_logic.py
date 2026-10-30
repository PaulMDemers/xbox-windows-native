"""Independent successful four-control record contract; fail closed on refusal."""
from prefix_audit import validate as prefix_validate
BASE=[56,16,131,224,104,48,227,255,62,64]
TARGET=[4,16,131,224]
def validate(v):
 assert len(v)==917 and all(type(n)==int and 0<=n<=0xffffffff for n in v)
 assert v[:2]==[0x815,0x815]
 parent=prefix_validate(v[:820])
 m=v[820:]
 assert m[:10]==BASE and m[10:14]==TARGET and m[14]==4
 for i in range(4):
  assert m[15+10*i:25+10*i]==[TARGET[j] if j<=i else BASE[j] for j in range(10)]
  assert m[55+10*i:65+10*i]==[TARGET[j] if j<i else BASE[j] for j in range(10)]
 assert m[95:]==[0,0]
 return dict(passed=True,prefix=parent,controls=['CR1A','CR25','CR28','CR2D'],
  before=m[:4],target=m[10:14],after=[m[15+11*i] for i in range(4)],
  restored=[m[55+11*i] for i in range(4)],attempts=4,neighbor_count=10,
  same_value_controls=['CR25','CR28','CR2D'],native_proof=False)
