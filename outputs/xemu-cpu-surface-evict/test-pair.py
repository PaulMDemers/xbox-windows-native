"""Recorded-trace mutations must fail before native evidence is accepted."""
import copy, importlib.util, json
from pathlib import Path
k=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('pair',k/'verify-pair.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
a,events,_=v.load_case('candidate002');v.verify_candidate(events,a['surfaces']);cases=[]
for depth in [False,True]:
    base=next(r['base'] for r in a['surfaces'] if r['depth']==depth)
    for kind in ['download','upload','create','evict_reason','invalidated']:
        e=copy.deepcopy(events);i=next(i for i,r in enumerate(e) if r['base']==base and r['kind']==kind)
        del e[i]
        try:v.verify_candidate(e,a['surfaces'])
        except AssertionError:cases.append(dict(depth=depth,removed=kind))
        else:raise AssertionError(('Accepted missing event',depth,kind))
    for field,value in [('pitch',1280),('bytes_per_pixel',2)]:
        e=copy.deepcopy(events);r=next(r for r in e if r['base']==base and r['kind']=='download');r[field]=value
        try:v.verify_candidate(e,a['surfaces'])
        except AssertionError:cases.append(dict(depth=depth,corrupted=field))
        else:raise AssertionError(('Accepted bad geometry',depth,field))
    e=copy.deepcopy(events);r=next(r for r in e if r['base']==base and r['kind']=='evict_reason');r['reason']='old'
    try:v.verify_candidate(e,a['surfaces'])
    except AssertionError:cases.append(dict(depth=depth,corrupted='eviction reason'))
    else:raise AssertionError('Accepted wrong eviction cause')
p=k/'recorded-pair-tests.json';assert not p.exists()
p.write_text(json.dumps(dict(passed=True,rejected_mutations=cases,test_sha256=v.sha(Path(__file__))),indent=2)+'\n')
print(len(cases),'recorded-trace mutation gates passed')
