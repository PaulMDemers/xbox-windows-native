"""Bounds and pairing controls; modeled memory only, not runtime coverage."""
import json,struct
from pathlib import Path
from parsing import object_name,pair_key,user_span
K=Path(__file__).resolve().parent;out=K/'parser-tests001.json';assert not out.exists()
checks=0
def reject(fn):
    global checks
    try:fn()
    except (AssertionError,UnicodeError):checks+=1;return
    raise AssertionError('Invalid model accepted')
def model(name,root=0):
    data=bytearray(4096);b=name.encode('utf-16le');struct.pack_into('<6I',data,0,24,root,0x10100,64,0,0);struct.pack_into('<HHI',data,256,len(b),len(b),0x10200);data[512:512+len(b)]=b
    def read(p,n):
        assert 0x10000<=p and p+n<=0x11000 and n<=4096
        return bytes(data[p-0x10000:p-0x10000+n])
    return data,read
for n in [0,1,41,42,43,69,512]:
    data,read=model('\\??\\C:\\'+'a'*n);r=object_name(read,0x10000);assert r['absolute_name_observed'] and r['name_bytes']==(7+n)*2;checks+=1
    data,read=model('a'*n,4);r=object_name(read,0x10000);assert not r['absolute_name_observed'];checks+=1
for off,value in [(0,23),(8,0x7fffffff),(8,0x20)]:
    data,read=model('abc');struct.pack_into('<I',data,off,value);reject(lambda:object_name(read,0x10000))
for length,maximum in [(3,4),(6,4),(2050,2050),(0,4097)]:
    data,read=model('abc');struct.pack_into('<HH',data,256,length,maximum);reject(lambda:object_name(read,0x10000))
for p,n in [(0,1),(0xffff,1),(0x80000000,1),(0x7fffffff,2),(0x10000,4097)]:reject(lambda:user_span(p,n))
data,read=model('a\0b');reject(lambda:object_name(read,0x10000))
data,read=model('abc');data[512:514]=b'\x00\xd8';reject(lambda:object_name(read,0x10000))
keys=set()
for t in [0x81000000,0x81001000]:
 for p in [0x82000000,0x82001000]:
  for sp in [0x120000,0x120010]:
   for api in ['NtCreateFile','NtOpenFile','NtQueryAttributesFile','NtQueryFullAttributesFile']:
    key=pair_key(t,p,sp,api);assert key not in keys;keys.add(key);checks+=1
for t,p,sp,api in [(0,0x82000000,0x120000,'NtCreateFile'),(0x81000000,0,0x120000,'NtCreateFile'),(0x81000000,0x82000000,0,'NtCreateFile'),(0x81000000,0x82000000,0x120000,'unknown')]:reject(lambda:pair_key(t,p,sp,api))
out.write_text(json.dumps({'passed':True,'checks':checks,'scope':'Synthetic bounded Unicode/argument and thread/process/frame/API pairing only'})+'\n');print(checks)
