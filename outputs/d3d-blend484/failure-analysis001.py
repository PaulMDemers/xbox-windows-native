"""Read-only actual color inventory; never changes the predefined pixel oracle."""
import collections,hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'tools'));import graphics_blend as g
out=K/'failure-analysis001.json';assert not out.exists()
c=json.loads((K/'ntfs-cold1-002.json').read_text());P=Path(c['private_path'])/'files/xwn484'
results=[]
for name in ('r08cd','r08cs'):
    fields=g.decode((P/(name+'.txt')).read_bytes());stages=[]
    for stage in g.STAGES:
        p=P/(name+'-'+stage+'.bin');raw=p.read_bytes();assert len(raw)==16384
        counts={k:collections.Counter() for k in ('all','interior','exterior','boundary')};failures=collections.Counter();first=[]
        for index,(word,) in enumerate(struct.iter_unpack('<I',raw)):
            x,y=index%64,index//64;rgb=word&0xffffff
            if x>=12 and y>=12 and x+y<=56:kind='interior';allowed=g.allowed(stage)
            elif x<=4 or y<=4 or x+y>=72 or x>=60 or y>=60:kind='exterior';allowed={g.BG}
            else:kind='boundary';allowed=g.allowed(stage)|{g.BG}
            counts['all'][rgb]+=1;counts[kind][rgb]+=1
            if rgb not in allowed:
                failures[kind]+=1
                if len(first)<8:first.append(dict(x=x,y=y,rgb=f'{rgb:06x}'))
        stages.append(dict(stage=stage,sha256=hashlib.sha256(raw).hexdigest(),colors={k:{f'{rgb:06x}':n for rgb,n in sorted(v.items())} for k,v in counts.items()},failed_pixels=dict(failures),first_failures=first))
    results.append(dict(case=name,states={k:v for k,v in fields.items() if k.endswith(('.alpha','.blend','.src','.dest'))},stages=stages))
record=dict(qualification_passed=False,oracle_unchanged=True,analysis_only=True,rows=results)
out.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(results,indent=2))
