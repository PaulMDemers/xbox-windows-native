"""Independently reject incomplete/changed proposed worker transport."""
import argparse,copy,hashlib,json,struct
from pathlib import Path
import transport
k=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('attempt');a=p.parse_args();assert a.attempt.isdecimal()
dest=k/('transport-host'+a.attempt+'.json');assert not dest.exists()
out=Path('E:/Codex-archive/xbox-windows-native/release280-transport'+a.attempt);out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['test-transport.py','transport.py','decode.py']:(out/n).write_bytes((k/n).read_bytes())
prior=Path('E:/Codex-archive/xbox-windows-native/release280-worker004')
pins=json.loads((k/'worker-host004.json').read_text())['files']
rejected=0
def reject(call):
 global rejected
 try:call()
 except (AssertionError,KeyError,IndexError,struct.error):rejected+=1
 else:raise AssertionError('Invalid transport accepted')
r=dict(passed=False,host_only=True,guest_launched=False,models='Actual proposed worker output from explicit host CPU/GL/graph models; not guest evidence')
try:
 for mode in range(2):
  f=prior/f'mode{mode}.bin';assert sha(f)==pins[f.name];data=f.read_bytes();(out/f.name).write_bytes(data)
  records,groups=transport.read(data);transport.inspect(records,groups,bool(mode))
  reject(lambda:transport.inspect(records,groups,not bool(mode)))
  for i in range(2):
   for col in range(13):
    m=copy.deepcopy(records);m[i][col]^=1
    reject(lambda:transport.inspect(m,groups,bool(mode)))
   for col in range(13,16):
    m=copy.deepcopy(records);m[i][col]=0
    reject(lambda:transport.inspect(m,groups,bool(mode)))
  for stage,g in enumerate(groups):
   for idx,row in enumerate(g):
    if row[0] not in (17,64,65,66,67,68,69,70,71,72):continue
    for mutation in ('delete','duplicate'):
     m=copy.deepcopy(groups)
     if mutation=='delete':del m[stage][idx]
     else:m[stage].append(row.copy())
     reject(lambda:transport.inspect(records,m,bool(mode)))
    columns={17:[1,3,4,5,6,7],64:[1,2,3,4,5,6,7],65:[1,2,3,4,5,6,7],66:[1,2,3,4,5,6,7],67:[1,2,3,4,5,6,7],68:[1,2,3,4,5,6,7],69:[1,2,3,4,5,6,7],70:[1,2,3,4,5,6,7],71:[1,2,6,7],72:[1,2,3,5,6,7]}[row[0]]
    for col in columns:
     m=copy.deepcopy(groups);m[stage][idx][col]^=1
     reject(lambda:transport.inspect(records,m,bool(mode)))
   # Unknown rows, changed retained surface, or ambiguous boundary times refuse.
   m=copy.deepcopy(groups);m[stage].append([999,0,0,0,0,0,0,0]);reject(lambda:transport.inspect(records,m,bool(mode)))
   for kind,col in [(71,3),(71,4),(71,5),(72,4)]:
    m=copy.deepcopy(groups);row=next(v for v in m[stage] if v[0]==kind);row[col]=0
    reject(lambda:transport.inspect(records,m,bool(mode)))
  for trim in (1,8,64,128,256,len(data)-8):reject(lambda:transport.read(data[:-trim]))
  reject(lambda:transport.read(data+b'\0'*8))
 r.update(passed=True,negative_mutations=rejected,modes=2,stages_per_mode=3,
          remaining='Complete runtime graph/UI provider, caller/getters, real seal273 and guest source/pixel observations are not implemented or qualified by this transport test')
except BaseException as e:r['error']=repr(e)
r['files']={p.name:sha(p) for p in out.iterdir() if p.is_file()}
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:b for a,b in r.items() if a!='files'},indent=2));assert r['passed']
