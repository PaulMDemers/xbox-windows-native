"""Fresh host library; independent wide-integer ownership oracle."""
import ctypes as c,json,sys,hashlib,datetime
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path(sys.argv[1]);lib=c.CDLL(str(O/'plan.so'))
class Plan(c.Structure):
 _fields_=[('words',c.c_uint32*31)]
lib.admit705.argtypes=[c.POINTER(Plan)];lib.admit705.restype=c.c_uint32
def good():return [0x1c00000,0x100000,0x100000,1,0x1ef0000,32768,32768,1,0,0x1ef0000,0x1ef0000,65536]+[0x2200000+i*8192 for i in range(8)]+[0x2200000+i*8192+4095 for i in range(8)]+[0x3000000,3686400,3686400]
def oracle(v):
 e=0
 fits=lambda a,n,l,h:n>0 and a>=l and a+n<=h
 if not (v[1]==1048576 and v[2]>=v[1] and v[3]==1 and not v[0]%4096 and fits(v[0],v[2],0x200000,0x2000000)):e|=1
 if not (v[5]==32768 and v[6]>=v[5] and v[7]==1 and not v[4]%4096 and fits(v[4],v[6],0x1000000,0x2000000)):e|=2
 if not (v[8]<0x80000000 and v[9]==v[4] and all(not v[i]%4096 for i in (9,10,11)) and 32768<=v[11]<=131072 and 0<=v[10]<=v[9] and v[9]+32768<=v[10]+v[11]<=0x80000000):e|=4
 for i in range(8):
  if not (v[12+i]%4096==0 and fits(v[12+i],4096,0,0x4000000) and v[20+i]==v[12+i]+4095):e|=4
 if not (v[29]==3686400 and v[30]>=v[29] and v[28]%4096==0 and fits(v[28],v[30],0x2000000,0x4000000)):e|=16
 if not e:
  intervals=[(v[0],v[0]+v[2]),(v[4],v[4]+v[6]),(v[28],v[28]+v[30])]
  ov=lambda a,b:max(a[0],b[0])<min(a[1],b[1])
  if ov(intervals[0],intervals[1]) or ov(intervals[2],(0x2600000,0x2800000)):e|=8
  for i in range(8):
   a=(v[12+i],v[12+i]+4096)
   if ov(a,intervals[0]) or ov(a,intervals[2]) or (ov(a,intervals[1]) and v[12+i]!=v[4]+i*4096) or v[12+i] in v[12:12+i]:e|=8
 return e
r={'passed':False,'physical_access':False,'cases':0,'library_sha256':hashlib.sha256((O/'plan.so').read_bytes()).hexdigest()}
def check(v):
 actual=lib.admit705(Plan((c.c_uint32*31)(*v)));wanted=oracle(v)
 assert actual==wanted,(v,actual,wanted);r['cases']+=1
try:
 assert lib.admit705(None)==31;check(good())
 for i in range(31):
  for n in (0,1,4095,4096,0x7fffffff,0x80000000,0xffffffff):
   v=good();v[i]=n;check(v)
 # Every possible alias page independently, including identity and cross-page aliases.
 for i in range(8):
  for a in range(0,0x4001000,4096):
   v=good();v[12+i]=a;v[20+i]=a+4095;check(v)
 v=good()
 for i in range(8):v[12+i]=v[4]+i*4096;v[20+i]=v[12+i]+4095
 check(v)
 for size in (32768,36864,65536,98304,131072):
  for offset in range(0,65536,4096):
   v=good();v[10]=v[9]-offset;v[11]=size;check(v)
 r['passed']=True
finally:(K/'plan-review002.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS',r['cases'],'ownership and alias cases')
