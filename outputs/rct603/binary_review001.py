"""Check exact frozen source bytes and NT5 PE contract, without executing guest."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;sys.path.insert(0,str(K.parents[1]/'work/python-packages'));import pefile
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
b=json.loads((K/'build002.json').read_text());assert b['status']=='compiled'
out=K/'binary-review001.json';assert not out.exists();rows=[]
for n,v in b['files'].items():
    p=Path(n.replace('/mnt/c/','C:/'));assert sha(p)==v['sha256']
    if p.suffix in ['.c','.h']:assert p.read_bytes()==(K/p.name).read_bytes()
for row in b['rows']:
    p=Path(row['path'].replace('/mnt/c/','C:/'));pe=pefile.PE(str(p))
    assert pe.FILE_HEADER.Machine==0x14c and pe.OPTIONAL_HEADER.Magic==0x10b
    assert (pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
    imports={x.dll.decode():[v.name.decode() if v.name else '#'+str(v.ordinal) for v in x.imports] for x in pe.DIRECTORY_ENTRY_IMPORT}
    assert set(n.lower() for n in imports)<={'kernel32.dll','user32.dll','advapi32.dll','gdi32.dll'}
    rows.append(dict(path=str(p),sha256=sha(p),imports=imports,subsystem=[5,0]))
out.write_text(json.dumps(dict(passed=True,files=rows,scope='PE target/import and frozen source contract, not NT5 runtime validation',physical_access=False),indent=2)+'\n');print('Frozen NT5 binary contracts passed')
