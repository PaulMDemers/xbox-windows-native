"""Extract the actual linked nxdk diagnostic template and symbol offsets."""
import hashlib,json,struct
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn695/build001');out=K/'extract001.json';assert not out.exists()
b=(P/'stub.obj').read_bytes();r={'passed':False,'object_sha256':hashlib.sha256(b).hexdigest()}
try:
 m,ns,_,sp,nsy,op,_=struct.unpack_from('<HHLLLHH',b);assert m==0x14c and not op
 strings=b[sp+18*nsy:];sec=[];sy={};idx={};i=0
 for j in range(ns):
  h=struct.unpack_from('<8sLLLLLLHHL',b,20+j*40);sec.append({'data':bytearray(b[h[4]:h[4]+h[3]]),'reloc':h[5],'count':h[7]})
 while i<nsy:
  n,v,s,t,storage,aux=struct.unpack_from('<8sLhHBB',b,sp+i*18)
  n=(strings[struct.unpack('<L',n[4:])[0]:] if n[:4]==b'\0'*4 else n).split(b'\0')[0].decode()
  if s>0:sy[n]=(s,v);idx[i]=(s,v)
  i+=aux+1
 section,start=sy['_stub695_start'];s=sec[section-1]
 for j in range(s['count']):
  off,i,typ=struct.unpack_from('<LLH',b,s['reloc']+j*10);ts,tv=idx[i]
  assert ts==section and typ==20,'template must contain only intra-page relative relocations'
  old=struct.unpack_from('<L',s['data'],off)[0];struct.pack_into('<L',s['data'],off,(old+tv-off-4)&0xffffffff)
 offsets={n.removeprefix('_stub695_'):v-start for n,(ss,v) in sy.items() if n.startswith('_stub695_') and ss==section}
 assert offsets['start']==0 and offsets['end']==4096 and offsets['code_end']<=1024
 blob=bytes(s['data'][start:start+4096]);pe=(P/'main.exe').read_bytes()
 assert pe.count(blob)==1,'actual PE must contain precisely this linked template once'
 (P/'stub.bin').write_bytes(blob)
 r.update(passed=True,offsets=offsets,template_sha256=hashlib.sha256(blob).hexdigest(),linked_pe_offset=pe.index(blob),bytes=4096,all_relocations_internal_relative=True)
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
