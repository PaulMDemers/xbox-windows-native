"""Prebuild input closure and exact source/byte contract. No guest/network."""
import ast,datetime,hashlib,json,shutil,struct,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'preflight001.json';assert not out.exists()
js=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def host(n):return Path('/mnt/'+n[0].lower()+n[2:].replace(chr(92),'/')) if len(n)>1 and n[1]==':' else Path(n)
inputs={}
def pin(p,want=None):
 p=host(str(p));h=sha(p)
 if want:assert h==want,str(p)
 inputs[str(p.resolve())]=h
 return p
assert js(K/'controller-host002.json')['passed'] and len(js(K/'controller-host002.json')['cases'])==17
assert js(K/'supervisor-host001.json')['passed']
for n,row in js(K/'source-copy001.json').items():
 b=pin(row['parent'],row['parent_sha256']).read_bytes()
 for a,z in row['substitutions']:b=b.replace(a.encode(),z.encode())
 assert b==(K/n).read_bytes();pin(K/n,row['sha256'])
for p in K.glob('*.py'):ast.parse(p.read_text());pin(p)
for p in [K/'runner.c',K/'DESIGN.md',K/'.gitattributes',K/'source-copy001.json',K/'controller-host002.json',K/'supervisor-host001.json']:pin(p)
# Original490 compiler outputs are inherited inputs, never rerun.
prior=js(K.parent/'context-adapter490/build001.json')
for n,row in prior['files'].items():pin(n,row['sha256'])
pin(K.parent/'context-adapter490/build001.json')
for n,h in js(K.parent/'entry-extent520/build001.json')['inputs'].items():
 if n.startswith('/usr/bin/'):pin(n,h)
cc=Path('/home/paul/xbox-windows-native/release-readiness403-bootstrap001/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc')
pin(cc,'8ab0685d97b322aad3c37fd362b26fa5b9408ff6dd55a536c0a2d48de1c22b18')
for n,h in js(K.parent/'blend-precision487/runner-build001.json')['headers'].items():pin(n,h)
for option in ['-print-prog-name=cc1','-print-prog-name=collect2','-print-prog-name=as','-print-prog-name=ld','-print-file-name=libkernel32.a','-print-file-name=libuser32.a','-print-file-name=libadvapi32.a']:
 n=subprocess.check_output([str(cc),option],text=True,timeout=15).strip();p=Path(n)
 if not p.is_absolute():p=Path(shutil.which(n) or '')
 assert p.is_file(),(option,n);pin(p)
exe=pin('/home/paul/xbox-windows-native/blend-precision486-runner-build001/d3d.exe','e7942c5ba903195dbafcfd379caa9a28ba335e9e52901b139263572c7ac6cec1')
for n in ['precision.c','graphics_precision.py','final-review.json','runtime-review001.json','runner.c']:pin(K.parent/'blend-precision486'/n)
# New image must normalize to BOTH original490 and physically successful494.
a=pin('/mnt/c/xwn490/build001/default.xbe',prior['sha256']).read_bytes()
b=pin('/mnt/c/xwn494/build002/default.xbe',js(K.parent/'d3d-transform494/build002.json')['sha256']).read_bytes()
def propose(b,old,new):
 old=old.encode();new=new.encode();assert len(old)==len(new) and b.count(old)==4 and new not in b
 c=bytearray(b.replace(old,new));c[0x36c:0x380]=hashlib.sha1(struct.pack('<I',len(c)-4096)+c[4096:]).digest();return bytes(c)
x=propose(a,'XWNBoot490a','XWNBoot526a');y=propose(b,'XWNBoot494a','XWNBoot526a');assert x==y and len(x)==542839
assert x[0x3000:0x84000]==a[0x3000:0x84000]
free=shutil.disk_usage('/mnt/c').free;assert free-64*1024**2>=20*1024**3
r=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),inputs=inputs,expected_bytes=len(x),expected_sha256=hashlib.sha256(x).hexdigest(),source_reconstructions=18,controller_cases=17,model_services=True,physical_access=False,matched494_and490_expected=True,C_free=free,projected_C_bytes=64*1024**2,E_allocation=0,compiler_discovery='read-only print paths; tool/header/library bytes pinned before build',module_reader_correction='unexecuted487 template imported nonexistent tools/graphics_precision; explicitly select pinned486 oracle before any execution')
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print('PASS',len(inputs),'prebuild pins;expected',r['expected_sha256'])
