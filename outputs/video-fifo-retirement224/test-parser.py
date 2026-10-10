"""Parser rejects changed coverage/order/unsigned fields/reasons and truncated completion."""
import importlib.util,json,hashlib
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'parser-tests001.json';assert not dest.exists()
spec=importlib.util.spec_from_file_location('p224',k/'analyze-retirement.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
def sample(on):
    v=[0]*16;v[3]=v[11]=16
    lines=['RET_OWNER 2 0 0','RET_STALE 3 0 0','RET_SUMMARY '+('21 8 128' if on else '20 0 0'),'RET_REASONS 3221225472 1 0']
    if on:lines+=['RET_WORD %d %d %d'%(round,i,x) for round in range(8) for i,x in enumerate(v)]
    lines+=['RET_COMPLETE_NO_GRANT 224 0 0'];return ('\r\n'.join(lines)+'\r\n').encode()
checks=0
for on in [False,True]:
    b=sample(on);assert p.analyze(b,on)['passed'];checks+=1
    bad=[b[:-1],b.replace(b'RET_OWNER 2',b'RET_OWNER 0'),b.replace(b'3221225472',b'0'),b.replace(b'RET_COMPLETE_NO_GRANT',b'RET_GPU_GRANT'),b+b'RET_COMPLETE_NO_GRANT 224 0 0\r\n']
    if on:bad += [b.replace(b'RET_WORD 0 0 0',b'RET_WORD 0 0 4294967296'),b.replace(b'RET_WORD 0 0 0',b'RET_WORD 0 1 0'),b.replace(b'21 8 128',b'21 8 127'),b.replace(b'RET_WORD 7 0 0',b'RET_WORD 7 0 1')]
    for x in bad:assert not p.analyze(x,on)['passed'];checks+=1
    assert not p.analyze(b,not on)['passed'];checks+=1
v=[0]*16;v[3]=v[11]=16;v[5]=1<<18
assert p.decode([v]*8)&2;checks+=1
dest.write_text(json.dumps(dict(passed=True,checks=checks,parser_sha256=hashlib.sha256((k/'analyze-retirement.py').read_bytes()).hexdigest(),test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n');print('Parser checks',checks)
