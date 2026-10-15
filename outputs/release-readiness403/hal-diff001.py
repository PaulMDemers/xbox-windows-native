import struct,json,hashlib
from pathlib import Path
k=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/release-readiness403')
a=Path('/mnt/c/xwn403/installed-reference001/payload/E/Applications/XWNEBoot/loader/halxboxnt5.dll').read_bytes()
b=Path('/home/paul/xbox-windows-native/build/reconstruction-005/artifacts/halxboxnt5.dll').read_bytes()
def sections(b):
 p=struct.unpack_from('<I',b,60)[0];n=struct.unpack_from('<H',b,p+6)[0];opt=struct.unpack_from('<H',b,p+20)[0];out={}
 for i in range(n):
  off=p+24+opt+40*i;name=b[off:off+8].rstrip(b'\0').decode();vs,va,sz,raw=struct.unpack_from('<4I',b,off+8);out[name]=(va,raw,sz)
 return out
s=sections(a); t=sections(b);out={}
for name,(va,raw,sz) in s.items():
 x=a[raw:raw+sz];y=b[t[name][1]:t[name][1]+t[name][2]];diff=[i for i,(u,v) in enumerate(zip(x,y)) if u!=v]
 if diff:
  runs=[]
  for i in diff:
   if runs and i==runs[-1][-1]+1:runs[-1].append(i)
   else:runs.append([i])
  out[name]={'different_bytes':len(diff),'runs':len(runs),'samples':[{'rva':hex(va+v[0]),'count':len(v),'a':x[max(0,v[0]-8):v[-1]+9].hex(),'b':y[max(0,v[0]-8):v[-1]+9].hex()} for v in runs[:12]]}
(k/'hal-diff001.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({n:{k:v for k,v in r.items() if k!='samples'} for n,r in out.items()}))
for v in out.get('.rdata',{}).get('samples',[])[:4]:print(v)
