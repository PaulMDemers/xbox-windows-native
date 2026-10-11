"""Supplement driver004 static import review with forwarding and dynamic lookup."""
import hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile
k=Path(__file__).resolve().parent;out=k/'driver004-exports.json';assert not out.exists()
review=json.loads((k/'driver004-review.json').read_text());assert review['passed']
providers=k/'artifacts/providers001';pins=json.loads((k/'providers001.json').read_text())
for row in pins['files'].values():assert hashlib.sha256((providers/row['output']).read_bytes()).hexdigest()==row['sha256']
cache={};rows=[]
def resolve(dll,name,seen=()):
    key=(dll.lower(),name);assert key not in seen
    p=providers/({'hal.dll':'halxboxnt5.dll'}.get(key[0],key[0]))
    if key[0] not in cache:cache[key[0]]=pefile.PE(str(p))
    symbols=cache[key[0]].DIRECTORY_ENTRY_EXPORT.symbols
    entry=next(v for v in symbols if (v.name and v.name.decode()==name) or name=='#'+str(v.ordinal))
    row=dict(dll=dll,name=name,provider_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),forward=entry.forwarder.decode() if entry.forwarder else None)
    if entry.forwarder:
        target,symbol=entry.forwarder.decode().rsplit('.',1)
        row['resolved']=resolve(target+'.dll',symbol,seen+(key,))
    return row
for f in review['files']:
    for imp in f['imports']:rows.append(dict(consumer=f['name'],**resolve(imp['dll'],imp['name'])))
rows.append(dict(consumer='install.exe (GetProcAddress)',**resolve('newdev.dll','UpdateDriverForPlugAndPlayDevicesA')))
out.write_text(json.dumps(dict(passed=True,scope=__doc__,exports=rows),indent=2)+'\n')
print('All '+str(len(rows))+' imports/dynamic lookup resolved; no runtime claim')
