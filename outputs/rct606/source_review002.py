"""Check inherited core and new reference transport before game admission."""
import hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'source-review002.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(K.parents[1]/'work/python-packages'));from PIL import Image
read=lambda n:json.loads((K/n).read_text())
s=read('source001.json');b=read('build001.json');assert b['status']=='compiled'
for name,v in b['files'].items():
 p=Path(name.replace('/mnt/c/','C:/'));assert sha(p)==v['sha256']
 if p.suffix in ['.c','.h']:assert p.read_bytes()==(K/p.name).read_bytes()
for n in ['phase.h','dib_header.h','calls.h','dib_oracle.py']:
 assert (K/n).read_bytes()==(K.parent/'rct605'/n).read_bytes(),n
before=(K.parent/'rct605/trace.c').read_text().split('void WINAPI mainCRTStartup(void)')[0]
after=(K/'trace.c').read_text().split('void WINAPI mainCRTStartup(void)')[0]
assert before==after
assert (K/'trace_oracle.py').read_bytes()==(K.parent/'rct605/trace_oracle002.py').read_bytes()
assert (K/'target_iat.h').read_bytes()==(K.parent/'rct602/target_iat.h').read_bytes().replace(b'\r\n',b'\n')
for n in ['runner.c']:
 a=(K.parent/'rct602'/n).read_text()
 for old,new in [('xwn602','xwn606'),('trace602','trace606')]:a=a.replace(old,new)
 assert a==(K/n).read_text()
assert 'count>10000' in (K/'trace.c').read_text() and 'started>360000' in (K/'trace.c').read_text()
p=Path(s['reference']['path']);assert sha(p)==s['reference']['sha256']
raw=p.read_bytes();assert struct.unpack_from('<IiiHHII',raw,14)==(40,640,-480,1,32,0,1228800)
offset=struct.unpack_from('<I',raw,10)[0];rgb=bytearray()
for y in range(80,440):
 for x in range(160,620):
  i=offset+(y*640+x)*4;rgb.extend((raw[i+2],raw[i+1],raw[i]))
assert bytes(rgb)==Image.open(p).convert('RGB').crop((160,80,620,440)).tobytes()
assert hashlib.sha1(rgb).hexdigest()==s['roi_rgb_sha1']
rgb[0]^=1;assert hashlib.sha1(rgb).hexdigest()!=s['roi_rgb_sha1']
assert 'static const BYTE park_digest606[20]={'+','.join(str(v) for v in bytes.fromhex(s['roi_rgb_sha1']))+'};' in (K/'park_reference.h').read_text()
inp=(K/'input.h').read_text()
assert inp.index('capture("park-loaded")')<inp.index('if(!parkphase606())')<inp.index('capture("park-loaded-stable")')
out.write_text(json.dumps(dict(passed=True,qualified_prefix_sha256=hashlib.sha256(before.encode()).hexdigest(),
 reference_rgb_sha1=s['roi_rgb_sha1'],roi=[160,80,620,440],one_pixel_mismatch_rejected=True,
 scope='Exact605 observer helpers,602 runner handoff, corrected parser, frozen sources and independent raw-BGR/reference-RGB equivalence. Actual guest SHA1 and game behavior remain runtime checks.'),indent=2)+'\n')
print('606 source inheritance and reference transport passed')
