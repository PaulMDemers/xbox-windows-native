"""Verify actual NT5 cycle imports, forwarding and dynamically queried setup export."""
import hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile
k=Path(__file__).resolve().parent;out=k/'cycle001-review.json';assert not out.exists()
providers=k/'artifacts/providers002';pins=json.loads((k/'providers002.json').read_text())
for name,digest in pins['files'].items():
    if '/' not in name:assert hashlib.sha256((providers/name).read_bytes()).hexdigest()==digest
build=json.loads((k/'cycle001-build.json').read_text());exe=k/'artifacts/cycle001/cycle.exe'
assert hashlib.sha256(exe.read_bytes()).hexdigest()==build['sha256']
cache={}
def resolve(dll,name,seen=()):
    key=(dll.lower(),name);assert key not in seen
    p=providers/key[0]
    if key[0] not in cache:cache[key[0]]=pefile.PE(str(p))
    item=next(v for v in cache[key[0]].DIRECTORY_ENTRY_EXPORT.symbols if (v.name and v.name.decode()==name) or name=='#'+str(v.ordinal))
    row=dict(dll=dll,name=name,forward=item.forwarder.decode() if item.forwarder else None)
    if item.forwarder:
        target,symbol=item.forwarder.decode().rsplit('.',1);row['resolved']=resolve(target+'.dll',symbol,seen+(key,))
    return row
pe=pefile.PE(str(exe));rows=[]
for d in pe.DIRECTORY_ENTRY_IMPORT:
    for i in d.imports:rows.append(resolve(d.dll.decode(),i.name.decode() if i.name else '#'+str(i.ordinal)))
rows.append(resolve('setupapi.dll','CMP_WaitNoPendingInstallEvents'))
assert pe.FILE_HEADER.Machine==0x14c and [pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion]==[5,0]
out.write_text(json.dumps(dict(scope=__doc__,passed=True,sha256=build['sha256'],exports=rows),indent=2)+'\n')
print('Cycle001 actual imports and dynamic lookup verified')
