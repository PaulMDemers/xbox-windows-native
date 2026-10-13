"""Synthetic ordered transport and failure tests; no guest observations."""
import copy,hashlib,json
from pathlib import Path
from phase_analysis import analyze
K=Path(__file__).resolve().parent;dest=K/'parser001.json';assert not dest.exists()
def fixture(mode):
    rows=[];add=lambda tag,*v:rows.append([tag,*v]);calls=[100]*4;ticks=[200]*4 if mode else [0]*4
    def packet():
        a=[0x544d5758,113,128,mode,1125000,0,128,0,0,22,0,0,0,0]
        for c,t in zip(calls,ticks):a.extend([c,t&0xffffffff,t>>32])
        return a+[256+2*sum(calls)*mode]+[0]*5
    add('PHASE344_VERSION',344,15,2);add('LARGE_VERSION',327,3,5)
    for size,(w,h) in enumerate([(256,128),(640,360),(960,540)]):
        cw,ch=w+48,h+48;add('LARGE_SIZE',size,w,h);add('LARGE_LAYOUT',size,cw*4,cw*ch*4);add('LARGE_CLIENT',size,cw,ch)
        for kind in range(5):
            ident=size*5+kind;count=20;add('LARGE_PIXEL_CHECK',ident,cw*ch,1)
            before=[0x53525758,112]+[100]*15+[0xfffff000,2,0,1]+[0]*11
            after=before[:];after[16]+=count;total=before[17]+(before[18]<<32)+w*h*4*count;after[17]=total&0xffffffff;after[18]=total>>32
            add('LARGE_STATS_CALL',ident,0,1)
            for i,v in enumerate(before):add('LARGE_STATS_BEFORE',ident,i,v)
            a=packet();calls=[c+count for c in calls];ticks=[t+22500*mode for t in ticks];b=packet()
            for side,p in enumerate([a,b]):
                add('PHASE344_PACKET',ident,side,1)
                for i,v in enumerate(p):add('PHASE344_AFTER' if side else 'PHASE344_BEFORE',ident,i,v)
            add('LARGE_TIMING',ident,count,800);add('LARGE_PAINTS',ident,count if kind==4 else 0,0);add('LARGE_STATS_CALL',ident,1,1)
            for i,v in enumerate(after):add('LARGE_STATS_AFTER',ident,i,v)
            amount=w*h*4*count;add('LARGE_UPLOADS',ident,count,0);add('LARGE_BYTES',ident,amount&0xffffffff,amount>>32)
            add('LARGE_PIXEL_CHECK',ident,cw*ch,1);add('LARGE_CASE_PASS',ident,1,0)
    add('LARGE_COMPLETE',3,15,0);add('PHASE344_COMPLETE',15,30,0);add('PASS',0,0,0);return rows
render=lambda rows:'\n'.join(' '.join(map(str,r)) for r in rows)+'\n'
checks=[]
def reject(label,rows,mode=1):
    assert not analyze(render(rows),mode)['passed'],label;checks.append(label)
for mode in (0,1):
    rows=fixture(mode);r=analyze(render(rows),mode);assert r['passed'],r
    assert len(r['intervals'])==15 and r['intervals'][0]['elapsed_ms']==([20]*4 if mode else [0]*4)
rows=fixture(1)
for i,row in enumerate(rows):
    if row[0].startswith('PHASE344'):
        reject('missing-'+str(i),rows[:i]+rows[i+1:]);reject('duplicate-'+str(i),rows[:i]+[row]+rows[i:])
for slot,value in [(0,0),(1,112),(2,127),(3,2),(4,0),(6,127),(11,1),(12,1),(13,1),(14,0xffffffff),(15,0xffffffff),(16,0xffffffff),(26,0),(27,1),(31,1)]:
    c=copy.deepcopy(rows);next(v for v in c if v[0]=='PHASE344_AFTER' and v[2]==slot)[3]=value;reject('bad slot'+str(slot),c)
for tag,slot,value in [('PHASE344_AFTER',14,99),('PHASE344_AFTER',15,199),('PHASE344_BEFORE',7,23)]:
    c=copy.deepcopy(rows);next(v for v in c if v[0]==tag and v[2]==slot)[3]=value;reject('regression/calibration '+tag+str(slot),c)
reject('wrong mode',rows,0)
c=copy.deepcopy(rows);next(v for v in c if v[0]=='LARGE_PIXEL_CHECK')[3]=0;reject('failed pixel gate',c)
c=copy.deepcopy(rows);next(v for v in c if v[0]=='LARGE_BYTES')[2]=0;reject('failed byte gate',c)
c=copy.deepcopy(rows);c.insert(-1,['PHASE344_UNKNOWN',0,0,0]);reject('unknown record',c)
c=copy.deepcopy(rows);next(v for v in c if v[0]=='PHASE344_PACKET')[1]=-1;reject('signed id',c)
# Coherent backward reset between packets must still be rejected, even with corrected read count.
c=copy.deepcopy(rows)
for v in c:
    if v[0]=='PHASE344_BEFORE' and v[1]==1:
        if v[2] in (14,17,20,23):v[3]=90
        if v[2]==26:v[3]=256+2*360
reject('between-interval reset with coherent query count',c)
dest.write_text(json.dumps(dict(passed=True,synthetic_modes=[0,1],negative_controls=len(checks),checks=checks,fixture_sha256=hashlib.sha256(render(rows).encode()).hexdigest(),sources={n:hashlib.sha256((K/n).read_bytes()).hexdigest() for n in ['phase_analysis.py','large_analysis.py','test-analysis.py']},guest_coverage=False),indent=2)+'\n')
print('PASS synthetic modes0/1;',len(checks),'negative controls')
