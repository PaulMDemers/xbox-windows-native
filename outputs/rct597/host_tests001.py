"""Check the independent oracle rejects missing, duplicate and misleading traces."""
import json
from pathlib import Path
from trace_oracle import validate
K=Path(__file__).resolve().parent;out=K/'host-tests001.json';assert not out.exists()
lines=['IMAGE 00400000 00000001 00000000','ARM 00000000 00403000 77000000','ARM 00000001 00403004 77001000']
def req(kind,tid,name):
    lines.append('%s %08x 00401000 %08x %s'%(kind,tid,0 if kind=='LOAD' else 0x4000000,'%08x'%name if kind=='ORD' else name.encode().hex()))
req('LOAD',1,'user32.dll');req('PROC',1,'MessageBeep');req('LOAD',1,'xwn597-does-not-exist.dll')
for tid in [1,2]:
    req('LOAD',tid,'C:\\xwn597-kit\\fixture.dll')
    for _ in range(4):req('PROC',tid,'probe597');req('ORD',tid,7)
    req('PROC',tid,'missing597');req('ORD',tid,8)
lines.append('END 00000000 0000001b 00000000')
# 4 loads + 11 named requests + 10 ordinal requests = 25, hex19.
lines[-1]='END 00000000 00000019 00000000'
good='\n'.join(lines)+'\n';positive=validate(good,0x400000,0x5000);rejected=[]
variants={
 'missing_request':'\n'.join(lines[:3]+lines[4:]),
 'duplicate_request':good+lines[3]+'\n',
 'failed_target':good.replace('END 00000000','END 00000001'),
 'recorder_failed':good.replace('00000019 00000000','00000019 00000001'),
 'missing_end':'\n'.join(lines[:-1]),
 'duplicate_end':good+lines[-1]+'\n',
 'unknown_exception':good+'EXCEPTION c0000005 00000001 00000001\n',
 'wrong_ordinal':good.replace('04000000 00000008','04000000 00000009'),
 'all_one_thread':good.replace(' 00000002 ',' 00000001 '),
 'non_subject_callers':good.replace(' 00401000 ',' 77001000 '),
 'zero_module':good.replace(' 04000000 ',' 00000000 '),
 'wrong_string':good.replace('70726f6265353937','70726f6265353938'),
}
for name,value in variants.items():
    try:validate(value,0x400000,0x5000)
    except (AssertionError,ValueError,UnicodeError):rejected.append(name)
    else:raise AssertionError(name)
out.write_text(json.dumps(dict(passed=True,positive=positive,negative_cases=rejected,scope='Trace oracle tests only; not debugger or NT5 execution proof.'),indent=2)+'\n')
print('597 oracle positive and',len(rejected),'negative controls passed')
