"""Offline review of captured rollback and exact package before any deployment."""
import ast,hashlib,json,struct,sys
from pathlib import Path
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
k=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda b:hashlib.sha256(b).hexdigest()
dest=k/'preflight001.json';assert not dest.exists();capture=read(k/'capture001.json');assert capture['completed'] and not capture['physical_writes']
for name,row in capture['files'].items():assert sha((k/'artifacts/before001'/name.lstrip('/')).read_bytes())==row['sha256']
hives=[]
for name in ['system','software','sam','security','default']:
 p=k/'artifacts/before001/F/winnt/system32/config'/name;data=p.read_bytes();h=hivex.Hivex(str(p));todo=[h.root()];seen=set();values=0
 while todo:
  n=todo.pop();assert n not in seen;seen.add(n);h.node_name(n)
  for v in h.node_values(n):h.value_key(v);h.value_value(v);values+=1
  todo.extend(h.node_children(n))
 a,b=struct.unpack_from('<II',data,4);c=0
 for at in range(0,508,4):c^=struct.unpack_from('<I',data,at)[0]
 c=0xfffffffe if c==0xffffffff else 1 if c==0 else c
 assert a==b and c==struct.unpack_from('<I',data,508)[0]
 hives.append(dict(name=name,keys=len(seen),values=values,sha256=sha(data)))
package=read(k/'package.json');assert len(package['video'])==6 and len(package['helpers'])==5 and package['registry_edits'] is False
for row in package['video']+package['helpers']:
 data=(k/'artifacts/payload'/row['name']).read_bytes();assert sha(data)==row['sha256'] and len(data)==row['bytes']
for p in k.glob('*.py'):ast.parse(p.read_text())
r=dict(passed=True,captured_files=len(capture['files']),hives=hives,payloads=11,physical_writes=False,limits='Structural rollback/package/source review; no hardware1080i qualification')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Preflight passed:',len(capture['files']),'captured files/five structural hives/eleven exact payloads')
