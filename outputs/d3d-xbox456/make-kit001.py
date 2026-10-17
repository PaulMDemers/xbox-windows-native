"""Prepare source-only matched physical inventory; no console access."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;old=K.parent/'lifecycle-xbox454';pc=K.parent/'d3d-discovery455'
def rep(s,a,b):assert a in s,a;return s.replace(a,b)
sample=json.loads((pc/'sample-build001.json').read_text())['executable_sha256'];rows={}
for name in ['physical.py','observe002.py','review001.py','closeout001.py','binary-review001.py','build001.py','package001.py']:
 s=(old/name).read_text(encoding='utf-8').replace('lifecycle-xbox454','d3d-xbox456').replace('454','456').replace('lifecycle453','d3d-discovery455').replace('graphics_lifecycle','graphics_discovery').replace('lifecycle.c','discovery.c').replace('life.exe','d3d.exe').replace('LIFE.EXE','D3D.EXE').replace('r05d','r06d').replace('r05s','r06s').replace('-pixels.bin','-caps.bin').replace('scoped_lifecycle_passed','scoped_inventory_passed').replace('4d1151e57bc04df2318c52df8ca0496cb54bce8610f591145a709d1ac2b97ca9',sample)
 if name=='physical.py':
  s=rep(s,";modules['psapi.dll']=json.loads((K.parent/'d3d-discovery455/modules001.json').read_text())['psapi_sha256']",'')
  s=rep(s,",'psapi.dll'",'')
 if name=='package001.py':s=rep(s,",'modules001.json'",'')
 if name=='closeout001.py':
  s=rep(s,"v['pixel_length_rejections']","v['capability_length_rejections']")
  s=rep(s,"exact_bytes=sum(row.get('review',{}).get('exact_bytes',0) for row in r['rows'])","capability_bytes=sum(236*row['review']['device_count'] for row in r['rows'] if 'review' in row)")
  s=s.replace("'exact_bytes'","'capability_bytes'").replace('Raw system-memory readback, not human visual/scanout qualification','Capability declarations only; no CreateDevice/draw/scanout qualification')
 p=K/name;assert not p.exists();p.write_text(s,encoding='utf-8',newline='\n');rows[name]=hashlib.sha256(p.read_bytes()).hexdigest()
raw=(pc/'runner.c').read_bytes();data=raw.replace(b'455',b'456').replace(b'Owned NT5 PC fixture only',b'Owned physical Xbox Windows fixture only').replace(b'A:\\\\D3D.EXE',b'C:\\\\xwn456-kit\\\\d3d.exe')
assert data.replace(b'C:\\\\xwn456-kit\\\\d3d.exe',b'A:\\\\D3D.EXE').replace(b'Owned physical Xbox Windows fixture only',b'Owned NT5 PC fixture only').replace(b'456',b'455')==raw
(K/'runner.c').write_bytes(data);rows['runner.c']=hashlib.sha256(data).hexdigest()
s=(pc/'actual-controls001.py').read_text();s=rep(s,"c=json.loads((K/'ntfs-cold1-002.json').read_text());p=Path(c['private_path'])/'files/xwn455'","c=json.loads((K/'physical001-collection.json').read_text());s=c['files']['/E/xwn456/runner.txt']['path'];p=Path('/mnt/'+s[0].lower()+s[2:].replace('\\\\','/')).parent")
(K/'actual-controls001.py').write_text(s,encoding='utf-8',newline='\n')
(K/'source-review001.json').write_text(json.dumps(dict(rows=rows,sample_sha256=sample,controller_original_reconstructed_byte_exact=True,scope='Source-only physical inventory adapter; build and package require qualified PC455'),indent=2)+'\n')
