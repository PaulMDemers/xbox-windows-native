import hashlib,json
from pathlib import Path
from analysis import analyze
K=Path(__file__).resolve().parent;dest=K/'analysis-tests001.json';assert not dest.exists()
rows=['STRETCH_VERSION 370 12 16']
for case in range(12):
    for phase in ['BEFORE','AFTER']:
        v=[0]*32;v[0]=0x53525758;v[1]=112;v[20]=1
        if phase=='AFTER':v[11]=16;v[16]=16;v[17]=131072
        rows += ['STRETCH_%s %d %d %d'%(phase,case,i,x) for i,x in enumerate(v)]
    rows += ['STRETCH_TIMING %d 16 0'%case,'STRETCH_BYTES %d 131072 0'%case,
             'STRETCH_DISPATCH %d 0 16'%case,'STRETCH_CASE_PASS %d 32768 %d'%(case,case%4==0)]
rows+=['STRETCH_COMPLETE 12 192 0']
text='\n'.join(rows);assert analyze(text)['passed'];rejected=0
for i in range(len(rows)):
    assert not analyze('\n'.join(rows[:i]+rows[i+1:]))['passed'];rejected+=1
    assert not analyze('\n'.join(rows[:i]+[rows[i]]+rows[i:]))['passed'];rejected+=1
for old,new in [('STRETCH_AFTER 0 19 0','STRETCH_AFTER 0 19 1'),
                ('STRETCH_AFTER 0 20 1','STRETCH_AFTER 0 20 0'),
                ('STRETCH_AFTER 0 31 0','STRETCH_AFTER 0 31 1'),
                ('STRETCH_TIMING 0 16 0','STRETCH_TIMING 0 16 30001'),
                ('STRETCH_DISPATCH 0 0 16','STRETCH_DISPATCH 0 0 15'),
                ('STRETCH_BYTES 0 131072 0','STRETCH_BYTES 0 131073 0'),
                ('STRETCH_CASE_PASS 0 32768 1','STRETCH_CASE_PASS 0 32768 0')]:
    assert old in text and not analyze(text.replace(old,new))['passed'];rejected+=1
assert not analyze(text+'\nFAIL_STRETCH 0 0 0')['passed'];rejected+=1
dest.write_text(json.dumps(dict(passed=True,synthetic_positive=1,negative_cases=rejected,
    source_sha256={n:hashlib.sha256((K/n).read_bytes()).hexdigest() for n in ['analysis.py','test-analysis.py']},
    limits='Synthetic transport/accounting checks, not guest drawing evidence.'),indent=2)+'\n')
print('Independent stretch parser negative cases',rejected)
