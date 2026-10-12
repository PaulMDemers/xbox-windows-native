"""Actual rollback body against modeled FTP, including interrupted owned STOR."""
import ast,copy,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent
tree=ast.parse((k/'physical.py').read_text());node=next(v for v in tree.body if isinstance(v,ast.FunctionDef) and v.name=='rollback')
source=ast.Module(body=[node],type_ignores=[])
digest=lambda b:hashlib.sha256(b).hexdigest()
rows=[dict(path='/p'+str(i),sha256=digest(b'new'+bytes([i]))) for i in range(6)]
before={v['path']:b'old'+bytes([i]) for i,v in enumerate(rows)};before['startup']=b'normal'
checks=0
for partial in range(-1,6):
 disk={v['path']:b'new'+bytes([i]) for i,v in enumerate(rows)};disk['startup']=b'test'
 if partial>=0:disk[rows[partial]['path']]=b'partial-STOR'
 order=[];r=dict(launch_requested=False,writes=[dict(path=v['path']) for v in rows],startup_enabled=True)
 def put(f,p,d):order.append(p);disk[p]=d
 def check_fixed(f):assert disk==before
 env=dict(startup='startup',incoming=lambda p:before[p],put=put,get=lambda f,p:disk[p],sha=digest,save=lambda p,r:None,record=None,package={'video':rows},check_fixed=check_fixed)
 exec(compile(source,'actual-rollback','exec'),env);env['rollback'](None,r,prelaunch_partial=True)
 assert disk==before and order==['startup']+[v['path'] for v in rows] and r['baseline_restored'];checks+=1
for requested,partial_flag,recorded in [(True,True,True),(False,False,True),(False,True,False)]:
 disk=dict(before);disk['/p0']=b'unknown';r=dict(launch_requested=requested,writes=[{'path':'/p0'}] if recorded else [])
 try:env['rollback'](None,r,prelaunch_partial=partial_flag)
 except AssertionError:checks+=1
 else:raise AssertionError('Unknown target accepted')
dest=k/'rollback-tests001.json';assert not dest.exists();dest.write_text(json.dumps(dict(passed=True,cases=checks,scope='Actual rollback AST; FTP/readback interfaces MODELED'),indent=2)+'\n');print('Rollback cases',checks)
