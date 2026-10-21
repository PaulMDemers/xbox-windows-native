from pathlib import Path
import sys,json,hashlib,struct
sys.path.insert(0,'work/python-packages');import pefile
k=Path('outputs/windows480p640');old=Path('outputs/windows480p639');out=k/'binary-review001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert (k/'probe.c').read_bytes()==(old/'probe.c').read_bytes().replace(b'639',b'640')
a=pefile.PE('C:/xwn639/build001/probe.exe');b=pefile.PE('C:/xwn640/build001/probe.exe')
imports=lambda p:[(e.dll.decode(),[i.name.decode() if i.name else i.ordinal for i in e.imports]) for e in p.DIRECTORY_ENTRY_IMPORT]
assert imports(a)==imports(b)
sec=lambda p,n:next(s.get_data() for s in p.sections if s.Name.rstrip(b'\0')==n)
x=sec(a,b'.text');y=sec(b,b'.text')
assert len(x)==len(y)
pos=[i for i in range(len(x)) if x[i]!=y[i]]
assert len(pos)==1 and x[pos[0]]==0x7f and y[pos[0]]==0x80 and x[pos[0]+1]==2 and y[pos[0]+1]==2
for p in [a,b]:assert p.FILE_HEADER.Machine==0x14c and (p.OPTIONAL_HEADER.MajorSubsystemVersion,p.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
source=(k/'probe.c').read_bytes()
assert sha(k/'probe.c')==json.loads((k/'build001.json').read_text())['source_pins']['probe.c']
r=dict(passed=True,physical_access=False,source_only_namespace_change=True,compiler_equal=json.loads((old/'build001.json').read_text())['compiler_sha256']==json.loads((k/'build001.json').read_text())['compiler_sha256'],text_difference_offsets=pos,text_change='case immediate 639 to 640 only',imports_identical=True,nt5_PE32=True,qualified_binary_sha256=sha(Path('C:/xwn639/build001/probe.exe')),candidate_binary_sha256=sha(Path('C:/xwn640/build001/probe.exe')),candidate_source_sha256=sha(k/'probe.c'),scope='Namespace-only behavioral equivalence to closed639; not physical proof')
assert r['compiler_equal'];out.write_text(json.dumps(r,indent=2)+'\n');print('640 binary comparison PASS')
