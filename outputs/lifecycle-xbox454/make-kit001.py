"""Fresh physical lifecycle controller derived from the qualified453 PC sample."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;old=K.parent/'sprites-retry452';pc=K.parent/'lifecycle453'
def rep(s,a,b):assert a in s,a;return s.replace(a,b)
rows={}
for name in ['physical.py','observe002.py','review001.py','actual-controls001.py','closeout001.py','binary-review001.py']:
 s=(old/name).read_text(encoding='utf-8').replace('sprites-retry452','lifecycle-xbox454').replace('452','454').replace('sprites-depth450','lifecycle453')
 if name=='physical.py':
  s=rep(s,"modules['ddraw.dll']=ddraw[0]['sha256']", "modules['ddraw.dll']=ddraw[0]['sha256'];modules['psapi.dll']=json.loads((K.parent/'lifecycle453/modules001.json').read_text())['psapi_sha256']")
  s=rep(s,"'gdi32.dll','ddraw.dll'", "'gdi32.dll','ddraw.dll','psapi.dll'")
 if name=='review001.py':
  s=s.replace('graphics_sprites','graphics_lifecycle').replace('sprites.exe','life.exe')
  s=rep(s,'23fcd2208b74a80feaf55d6a52be1b4a34a4138da859fa10bc06d5867862776f','4d1151e57bc04df2318c52df8ca0496cb54bce8610f591145a709d1ac2b97ca9')
  s=rep(s,'range(6)','range(2)');s=rep(s,"runner['completed_cases']=='6'","runner['completed_cases']=='2'")
  s=rep(s,"for i,(name,backend,fmt) in enumerate([('r04di','default','index8'),('r04si','hel','index8'),('r04d6','default','rgb565'),('r04s6','hel','rgb565'),('r04d3','default','rgb32'),('r04s3','hel','rgb32')]):","for i,(name,backend) in enumerate([('r05d','default'),('r05s','hel')]):")
  s=rep(s,'format=fmt,','')
  s=rep(s,"{kind:(root/(name+'-'+kind+'.bin')).read_bytes() for kind in g.KINDS},backend,fmt,int(code)","(root/(name+'-pixels.bin')).read_bytes(),backend,int(code)")
 if name=='actual-controls001.py':
  s=(pc/name).read_text(encoding='utf-8')
  s=rep(s,"c=json.loads((K/'ntfs-cold1-002.json').read_text());p=Path(c['private_path'])/'files/xwn453'", "c=json.loads((K/'physical001-collection.json').read_text());s=c['files']['/E/xwn454/runner.txt']['path'];p=Path('/mnt/'+s[0].lower()+s[2:].replace('\\\\','/')).parent")
 if name=='closeout001.py':
  s=s.replace('scoped_sprites_passed','scoped_lifecycle_passed');s=rep(s,"[['1280','720','32']]*6","[['1280','720','32']]*2")
 p=K/name;assert not p.exists();p.write_text(s,encoding='utf-8');rows[name]=hashlib.sha256(p.read_bytes()).hexdigest()
s=(pc/'runner.c').read_text().replace('453','454').replace('Owned NT5 PC fixture only','Owned physical Xbox Windows fixture only');s=rep(s,'A:\\\\LIFE.EXE','C:\\\\xwn454-kit\\\\life.exe')
p=K/'runner.c';assert not p.exists();p.write_text(s);rows[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
(K/'source-review001.json').write_text(json.dumps(dict(rows=rows,scope='PC453 two-case controller with only namespace/schema/source-copy path change; physical452 harness adapted to lifecycle, two cases and actual PSAPI pin'),indent=2)+'\n')
