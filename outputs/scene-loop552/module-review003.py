"""Join actual live-module names/sizes to independent cold file bytes."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));import pefile
out=K/'module-review003.json';assert not out.exists()
r=json.loads((K/'pixel-review003.json').read_text());assert r['pixel_endpoints_passed'] and not r['all_allowed_cases_passed']
i=json.loads((K/'independent003.json').read_text());assert i['passed'] and i['closed'] and i['mount_absent'] and i['disk_unchanged']
rows={x['path']:x for x in i['rows']};private=Path(i['private_path'])/'files'
c=json.loads((K/'ntfs-cold1-002.json').read_text());m=json.loads((Path(c['private_path'])/'manifest.json').read_text())
review=[]
for case in r['rows']:
 current=[]
 for j,name in enumerate(case['review']['modules']):
  n=name[3:].replace('\\','/').lower();p=private/m[n]['path'];h=hashlib.sha256(p.read_bytes()).hexdigest()
  assert h==rows[n]['sha256']==m[n]['sha256'];pe=pefile.PE(str(p))
  assert pe.OPTIONAL_HEADER.SizeOfImage==int(case['fields'][f'module{j}.bytes'])
  current.append(dict(path=n,sha256=h,bytes=p.stat().st_size,image_bytes=pe.OPTIONAL_HEADER.SizeOfImage))
 review.append(dict(case=case['name'],modules=current))
out.write_text(json.dumps(dict(passed=True,rows=review,scope='Actual module snapshot while D3D device exists, two cold readers agree. Not a trace of previously unloaded helpers.'),indent=2)+'\n')
print('Live module snapshots joined to independent cold bytes:',[len(x['modules']) for x in review])
