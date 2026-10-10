"""Fail-closed actual seeded NT5 trace parser, including exact probe mode."""
import hashlib,struct
def analyze(data,mode):
 r=dict(passed=False,mode=mode,records=[],limits='Native ephemeral buffer probe only; no DMA/completion/acceleration proof.')
 if mode not in [0,1] or len(data)!=4096 or data[:16]!=b'XWN-VID-TRACE01\n':
  r['reason']='invalid mode/length/magic';return r
 count,missed,reserved1,reserved2=struct.unpack_from('<IIII',data,16)
 r.update(trace_count=count,missed=missed,sha256=hashlib.sha256(data).hexdigest())
 if count>254 or missed or reserved1 or reserved2:
  r['reason']='record bound/missed/reserved';return r
 rows=[list(struct.unpack_from('<IIII',data,32+i*16)) for i in range(count)]
 probe=[x for x in rows if 21300<=x[0]<21400];r['records']=probe
 if mode==0:r['passed']=probe==[[21300,0,0,0]]
 else:
  r['passed']=(len(probe)==4 and probe[0]==[21300,1,16384,0] and
      probe[1][0]==21301 and probe[1][2:]==[0,0] and
      0x100000<=probe[1][1]<=0x03bfc000 and not probe[1][1]%4096 and
      probe[2]==[21302,15365,4,0] and probe[3]==[21303,1,16384,0])
 if not r['passed']:r['reason']='actual records do not prove the expected allocation/copy/release'
 return r
