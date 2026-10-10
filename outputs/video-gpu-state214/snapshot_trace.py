"""Fail-closed exact214 observational records, not a GPU ownership/idle gate."""
import hashlib,struct
OFFSETS=[0,0x100,0x140,0x2210,0x2214,0x2218,0x2100,0x2140,0x3200,0x3204,0x3220,0x3228,
 0x3240,0x3244,0x3250,0x400100,0x400140,0x400148,0x400720,0x600100,0x600140,0x600800]
def analyze(data,mode):
 r=dict(passed=False,mode=mode,snapshots=[],limits='Bounded source-reviewed emulator register observations. No atomic GPU state,exclusive ownership,submission/completion,physical fidelity or speed authority.')
 if mode not in [0,1] or len(data)!=4096 or data[:16]!=b'XWN-VID-TRACE01\n':r['reason']='mode/length/magic';return r
 count,missed,a,b=struct.unpack_from('<IIII',data,16);r.update(trace_count=count,missed=missed,sha256=hashlib.sha256(data).hexdigest())
 if count>254 or missed or a or b:r['reason']='count/missed/reserved';return r
 rows=[list(struct.unpack_from('<IIII',data,32+i*16)) for i in range(count)];rows=[v for v in rows if 21400<=v[0]<21500]
 r['records']=rows
 if not mode:r['passed']=rows==[[21400,0,0,0],[21400,1,0,0]];r['actual_new_reads']=0;return r
 if len(rows)!=48:r['reason']='incomplete/duplicate/unknown records';return r
 for phase in [0,1]:
  part=rows[phase*24:(phase+1)*24]
  if part[0]!=[21400,phase,1,0]:r['reason']='phase/order/mode/IRQL';return r
  values={};checksum=0
  for offset,v in zip(OFFSETS,part[1:23]):
   if v[:3]!=[21401,phase,offset]:r['reason']='register/order/phase';return r
   values['%08x'%offset]=v[3];checksum^=offset^v[3]
  if part[23]!=[21402,phase,22,checksum]:r['reason']='count/checksum/end';return r
  if values['00000000']!=0x02a000a3 or values['00600800']&0x07ffffff not in [0x03c00000,0x07c00000]:
   r['reason']='matched emulator identity/retained framebuffer';return r
  r['snapshots'].append(dict(phase=phase,values=values,checksum=checksum))
 r.update(passed=True,actual_new_reads=44);return r
