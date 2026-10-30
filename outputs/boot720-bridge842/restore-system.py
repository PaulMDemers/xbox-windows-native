"""Restore exact immutable baseline SYSTEM after preserving incomplete841 hive."""
import datetime,hashlib,importlib.util,io,json,zipfile
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn842/restore001')
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
spec=importlib.util.spec_from_file_location('physical842',K/'physical002.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
out=K/'restore-system001.json';assert not out.exists() and not P.exists();P.mkdir(parents=True)
pkg=read(W/'outputs/boot720-native835/package001.json');remote='/E/winnt/system32/config/system'
archive=Path('E:/xwn343/bundle002/stock-e-1080i-001.zip');assert sha(archive.read_bytes())==pkg['archive_sha256']
with zipfile.ZipFile(archive) as z:
 meta=pkg['files'][remote];baseline=z.read('payload'+meta['archive_path']);assert sha(baseline)==meta['sha256']
assert baseline[:4]==b'regf' and len(baseline)==4096+int.from_bytes(baseline[40:44],'little')
at=4096
while at<len(baseline):
 assert baseline[at:at+4]==b'hbin' and int.from_bytes(baseline[at+4:at+8],'little')==at-4096
 size=int.from_bytes(baseline[at+8:at+12],'little');assert size>=4096 and size%4096==0;at+=size
assert at==len(baseline)
prior=read(W/'outputs/boot720-load841/audit001.json')['critical'][remote]
assert sha(Path('C:/xwn841/audit001/winnt/system32/config/system').read_bytes())==prior['sha256']
r={'completed':False,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'remote':remote,'baseline_sha256':sha(baseline),'expected_preimage_sha256':prior['sha256'],'runtime_parent':False,'writes':[]}
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 with m.connect() as f:
  data=m.get(f,remote);assert sha(data)==prior['sha256'];(P/'before-system').write_bytes(data);(P/'baseline-system').write_bytes(baseline)
  r['preimage']={'sha256':sha(data),'bytes':len(data),'private_path':str(P/'before-system')};save()
  r['writes'].append(remote);save()
  for at in range(0,len(baseline),32768):f.storbinary(('STOR ' if at==0 else 'APPE ')+remote,io.BytesIO(baseline[at:at+32768]),1024)
  after=m.get(f,remote);assert after==baseline
  r['readback']={'sha256':sha(after),'bytes':len(after)};r['completed']=True
except BaseException as e:r['error_type']=type(e).__name__;raise
finally:save()
print('Clean SYSTEM restored and exact readback verified')
