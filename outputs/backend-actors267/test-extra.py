import copy,importlib.util,json,hashlib
from pathlib import Path
k=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('extra',k/'analyze-extra.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def row(kind,*args):return [kind,*args,*([0]*(7-len(args)))]
r=[row(9,100,1,90,0,0,123,0),row(50,100,1000,1,3,88,1,999),row(50,200,1001,2,3,89,2,998)]
r += [row(7,i,i+10) for i in range(14)]
r += [row(51,role,role*100,role*100+1,role*100+1,role*100+2,role*100+2,1) for role in [1,2]]
u=[row(64,400,401,0,640,480,301,302),row(65,301,302,301,302)]
for out,roles in [(r,[1,2]),(u,[3])]:
    for role in roles:
        for family in [0,1]:out.extend([row(52,role,family,1),row(53,role,family,0,0,0,0)])
for role,name in [(1,10),(1,15),(2,19)]:
    r.extend([row(54,role,name,1),row(56,role,name,0,0,0,0,1)])
    for attachment in [0x8ce0,0x8d00,0x8d20]:r.append(row(55,role,name,attachment,0))
for role,name in [(1,14),(1,16),(2,20)]:
    r.extend([row(57,role,name,1),row(58,role,name,0,1),row(59,role,name,0,0,0,0,0),row(60,role,name,0,0)])
for role,name in [(1,90),(1,18),(2,22)]:r.extend([row(61,role,name,1),row(62,role,name,1),row(63,role,name,0,77)])
u.extend([row(54,3,0,0),row(57,3,0,0),row(61,3,0,0)])
assert m.inspect(r,u)['unknown_actor_work']==0
# Pending work remains a valid observation, never completion.
p=copy.deepcopy(r);next(v for v in p if v[0]==50)[4]=2
assert m.inspect(p,u)['unknown_actor_work']==1
mutations=[(50,3,0),(50,4,4),(50,5,0),(50,6,7),(50,7,0),
 (51,4,999),(51,6,999),(51,7,0),(52,3,1025),(53,3,9),
 (56,4,9),(56,6,9),(56,7,2),(55,3,7),(55,4,777),
 (58,4,2),(59,3,1),(60,4,9),(62,3,2),(63,4,0)]
rejected=0
for kind,column,value in mutations:
    p=copy.deepcopy(r);next(v for v in p if v[0]==kind)[column]=value
    try:m.inspect(p,u)
    except AssertionError:rejected+=1
    else:raise AssertionError((kind,column,value))
for kind in [50,51,52,53,54,55,56,57,58,59,60,61,62,63]:
    p=copy.deepcopy(r);p.remove(next(v for v in p if v[0]==kind))
    try:m.inspect(p,u)
    except AssertionError:rejected+=1
    else:raise AssertionError(('missing',kind))
for kind,col in [(64,2),(65,1)]:
    p=copy.deepcopy(u);next(v for v in p if v[0]==kind)[col]=0
    try:m.inspect(r,p)
    except AssertionError:rejected+=1
    else:raise AssertionError(('ui',kind))
dest=k/'extra-tests001.json';assert not dest.exists()
dest.write_text(json.dumps(dict(passed=True,negative_controls=rejected,pending_not_completed=True,
    input_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [k/'analyze-extra.py',Path(__file__)]},
    guest_executed=False,gl_executed=False),indent=2)+'\n')
print(rejected,'independent synthetic negative controls PASS')
