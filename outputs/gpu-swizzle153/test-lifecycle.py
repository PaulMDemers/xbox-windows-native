"""Reject damaged swizzled geometry, layout, transfers and eviction causes."""
import copy,importlib.util,json
from pathlib import Path
k=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('series',k/'verify-series.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
checks=[];r=json.loads((k/'verification.json').read_text())
for case in ['control001','candidate001']:
    a=json.loads((k/case/'audit.json').read_text());rows=[e for arena in r['results'][case]['lifecycle'] for e in arena['events']]
    for name in ['missing_download','linear_instead','wrong_pitch','wrong_bpp','wrong_eviction']:
        data=copy.deepcopy(rows)
        if name=='missing_download':data.pop(2)
        elif name=='linear_instead':data[1]['normalized_layout']='linear'
        elif name=='wrong_pitch':data[1]['pitch']+=4
        elif name=='wrong_bpp':data[1]['bytes_per_pixel']=2
        else:data[3 if case.startswith('candidate') else 5]['reason']='old'
        try:m.verify(data,a['surfaces'],case.startswith('candidate'))
        except AssertionError:checks.append(case+':'+name)
        else:raise AssertionError('Incorrect lifecycle accepted: '+name)
p=k/'lifecycle-tests.json';assert not p.exists();p.write_text(json.dumps(dict(passed=True,checks=checks),indent=2)+'\n')
print(len(checks),'negative swizzle lifecycle checks passed')
