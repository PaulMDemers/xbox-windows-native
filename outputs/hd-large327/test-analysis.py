"""Synthetic transport only; never label these packets guest observations."""
import copy,hashlib,json
from pathlib import Path
from large_analysis import analyze
k=Path(__file__).resolve().parent;dest=k/'parser001.json';assert not dest.exists()
rows=[['XWN_GDI_PROBE_VERSION',11,256,128],['LARGE_VERSION',327,3,5]]
def add(tag,*v):rows.append([tag,*v])
for size,(w,h) in enumerate([(256,128),(640,360),(960,540)]):
    cw,ch=w+48,h+48
    add('LARGE_SIZE',size,w,h);add('LARGE_LAYOUT',size,cw*4,cw*ch*4);add('LARGE_CLIENT',size,cw,ch)
    for kind in range(5):
        ident=size*5+kind;count=173
        add('LARGE_PIXEL_CHECK',ident,cw*ch,1)
        before=[0x53525758,112]+[100]*15+[0xfffff000,2,0,1]+[0]*11
        after=before[:];after[16]+=count;total=before[17]+(before[18]<<32)+w*h*4*count
        after[17]=total&0xffffffff;after[18]=total>>32
        for phase,values in enumerate([before,after]):
            if phase:
                add('LARGE_TIMING',ident,count,800);add('LARGE_PAINTS',ident,count if kind==4 else 0,0)
            add('LARGE_STATS_CALL',ident,phase,1)
            for index,v in enumerate(values):add('LARGE_STATS_AFTER' if phase else 'LARGE_STATS_BEFORE',ident,index,v)
        add('LARGE_UPLOADS',ident,count,0);amount=w*h*4*count;add('LARGE_BYTES',ident,amount&0xffffffff,amount>>32)
        add('LARGE_PIXEL_CHECK',ident,cw*ch,1);add('LARGE_CASE_PASS',ident,1,0)
add('LARGE_COMPLETE',3,15,0);add('PASS',0,0,0)
render=lambda r:'\n'.join(' '.join(map(str,v)) for v in r)+'\n'
valid=render(rows);assert analyze(valid)['passed'];checks=[]
def reject(name,r):
    result=analyze(render(r) if isinstance(r,list) else r)
    assert not result['passed'],name
    checks.append(dict(name=name,error=result.get('error')))
for index,row in enumerate(rows):
    if row[0].startswith('LARGE_'):
        reject('missing-row-'+str(index),rows[:index]+rows[index+1:])
        reject('duplicate-row-'+str(index),rows[:index]+[row]+rows[index:])
        changed=copy.deepcopy(rows);changed[index][1]=0xffffffff;reject('wrong-id-'+str(index),changed)
for tag,column,value in [('LARGE_LAYOUT',3,0),('LARGE_CLIENT',2,1),('LARGE_TIMING',2,0),('LARGE_TIMING',2,20001),('LARGE_TIMING',3,749),('LARGE_TIMING',3,30001),('LARGE_PAINTS',3,1),('LARGE_PIXEL_CHECK',3,0),('LARGE_UPLOADS',2,172),('LARGE_BYTES',2,0),('LARGE_COMPLETE',2,14)]:
    changed=copy.deepcopy(rows);next(v for v in changed if v[0]==tag)[column]=value;reject(f'{tag}-{column}-{value}',changed)
for phase in ['LARGE_STATS_BEFORE','LARGE_STATS_AFTER']:
    for slot,value in [(0,0),(1,111),(2,0xffffffff),(19,1),(20,0),(21,1),(31,1)]:
        changed=copy.deepcopy(rows);next(v for v in changed if v[0]==phase and v[2]==slot)[3]=value;reject(f'{phase}-contract-{slot}',changed)
for slot,value in [(2,99),(16,100),(18,1)]:
    changed=copy.deepcopy(rows);next(v for v in changed if v[0]=='LARGE_STATS_AFTER' and v[2]==slot)[3]=value;reject(f'counter-regression-{slot}',changed)
for value in ['-1','4294967296','1.0','NaN','+1']:
    changed=copy.deepcopy(rows);changed[1][1]=value;reject('integer-'+value,changed)
reject('unknown-large-row',rows[:-1]+[['LARGE_UNKNOWN',0,0,0]]+rows[-1:])
reject('partial',rows[:-2]);reject('failure',rows[:-1]+[['FAIL',1,0,0]]+rows[-1:])
reject('empty','');reject('oversized','x'*(4*1024*1024+1));reject('null',None)
r=dict(passed=True,scope='synthetic327 packet and independent parser; no actual guest log',negative_controls=len(checks),checks=checks,
       synthetic_sha256=hashlib.sha256(valid.encode()).hexdigest(),rows=len(rows),cases=15,
       inputs={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['large_analysis.py','test-analysis.py']})
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({v:r[v] for v in ['passed','negative_controls','rows','cases']}))
