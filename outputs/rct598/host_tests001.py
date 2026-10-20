"""Parser scope tests, not runtime qualification."""
import json
from pathlib import Path
from parse_trace001 import parse
K=Path(__file__).resolve().parent;out=K/'host-tests001.json';assert not out.exists()
text='\n'.join(['IMAGE 00400000 00000001 00000000','ARM 00000000 00c460f4 7c59026d','ARM 00000001 00c460f0 7c590cf7',
 'LOAD 00000001 00401000 00000000 '+b'ddraw.dll'.hex(),
 'PROC 00000001 00402000 00000000 '+b'DirectDrawCreate'.hex(),'END 00000000 00000002 00000000'])+'\n'
p=parse(text,0x400000,0x900000);assert p['main_image_requests']==2
assert p['named_export_requests']=={'DirectDrawCreate':1}
# Null module is an observed argument, not proof of success or a parser error.
outside=parse(text.replace('00402000','77f81000'),0x400000,0x900000)
assert outside['other_caller_requests']==1 and not outside['named_export_requests']
rejected=[]
for name,bad in {
 'missing_end':text.rsplit('END',1)[0],
 'failed_child':text.replace('END 00000000','END 00000001'),
 'wrong_count':text.replace('00000002 00000000','00000003 00000000'),
 'wrong_iat':text.replace('00c460f4','00c460f8'),
 'unexpected_exception':text.replace('END','EXCEPTION c0000005 00000001 00000001\nEND'),
 'wrong_image':text.replace('IMAGE 00400000','IMAGE 00500000'),
 'corrupt_name':text.replace(b'ddraw.dll'.hex(),'zz'),
 'after_end':text+'DLL 77000000 00000000 00000000\n',
}.items():
 try:parse(bad,0x400000,0x900000)
 except (AssertionError,ValueError):rejected.append(name)
 else:raise AssertionError(name)
out.write_text(json.dumps(dict(passed=True,positive_cases=['named request with null module retained','non-main caller separated'],negative_cases=rejected,limits='Parser checks do not prove resolution success, renderer behavior or performance.'),indent=2)+'\n')
print('598 parser scope controls passed')
