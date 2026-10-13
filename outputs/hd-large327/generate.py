"""Preserve every original206 byte except the explicit327 extension hooks."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;p=k.parent/'video-text-oracle206'
assert not (k/'gdi-probe.c').exists()
source=(p/'gdi-probe.c').read_bytes();data=source
newline=b'\r\n' if b'\r\n' in source else b'\n'
hooks=[(b'static BOOL PaintPattern, PaintFailed;',
        b'static BOOL PaintPattern, PaintFailed;\nstatic BOOL LargePaint,LargePaintFailed;\nstatic DWORD LargeW,LargeH,LargePaintCount;\nstatic HDC LargeSource;'),
       (b'        if(PaintPattern) {',
        b'        if(LargePaint) {\n            if(!BitBlt(ps.hdc,16,16,LargeW,LargeH,LargeSource,16,16,SRCCOPY))LargePaintFailed=TRUE;\n            ++LargePaintCount;\n        }\n        if(PaintPattern) {'),
       (b'#include "text-cases.c"',b'#include "text-cases.c"\n#include "large_cases.c"'),
       (b'    if(!Failures&&!windowcase())++Failures;',
        b'    if(!Failures&&!windowcase())++Failures;\n    if(!Failures&&!large_cases())++Failures;')]
actual=[]
for old,new in hooks:
    new=new.replace(b'\n',newline)
    assert data.count(old)==1;data=data.replace(old,new);actual.append((old,new))
restored=data
for old,new in reversed(actual):
    assert restored.count(new)==1;restored=restored.replace(new,old)
assert restored==source
(k/'gdi-probe.c').write_bytes(data)
(k/'text-cases.c').write_bytes((p/'text-cases.c').read_bytes())
r={'original_source_reconstructed_exactly':True,'hook_count':len(hooks),'driver_changes':False,
   'source_sha256':hashlib.sha256(source).hexdigest(),'probe_sha256':hashlib.sha256(data).hexdigest(),
   'text_cases_unchanged':True,'inputs':{n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['large_cases.c','large_oracle.h','text-cases.c','generate.py']}}
(k/'source-review.json').write_text(json.dumps(r,indent=2)+'\n')
print(r['original_source_reconstructed_exactly'])
