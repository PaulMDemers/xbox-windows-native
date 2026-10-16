"""One journaled activation or restoration of the three reviewed loader files.

Never sends a launch command. Refuses unknown file bytes and keeps every original
under a same-directory name as well as the inactive staged rollback.
"""
import importlib.util
import json
import sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
s=importlib.util.spec_from_file_location('media407',W/'outputs/media-physical407/physical.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
from common001 import put
ACTIVE='/E/Applications/XWNEBoot/'
ROOT='/E/xwn416-stage'

def restore_plan(active,old,new,used,baseline,candidate):
    """Explicit recovery of only known bytes; no wildcard deletion or overwrite."""
    if active not in (None,baseline,candidate) or old not in (None,baseline) or new not in (None,candidate) or used not in (None,candidate):
        raise ValueError('Unknown loader bytes')
    if active==baseline:return []
    if old!=baseline:raise ValueError('Original rollback name missing')
    if active==candidate:
        if used is not None:raise ValueError('Candidate evidence name already exists')
        return [('active','used'),('old','active')]
    return [('old','active')]

def paths(row):
    active=ACTIVE+row['relative']
    return dict(active=active,old=active+'.416old',new=active+'.416new',used=active+'.416used')

def load():
    q=m.read(K/'comparison002.json');stage=m.read(K/'stage001.json')
    assert q['passed'] and stage['completed'] and stage['inactive']
    assert m.sha((K/'comparison002.json').read_bytes())==stage['comparison_sha256']
    m.ticket()
    return q,stage

def digest(f,path):
    b=m.get(f,path,optional=True)
    return None if b is None else m.sha(b)

def record(out,r):m.write_json(out,r)

def activate():
    q,stage=load();out=K/'activation001.json'
    assert not out.exists(),'Consumed activation; inspect journal, never relaunch'
    r=dict(completed=False,started_utc=m.utc(),launch_requested=False,console_C_accessed=False,
           operations=[],files={},script_sha256=m.sha(Path(__file__).read_bytes()))
    record(out,r)
    try:
        with m.connect() as f:
            for path,h in stage['protected'].items():assert digest(f,path)==h,path
            for path,v in stage['verified'].items():assert digest(f,path)==v['sha256'],path
            for row in q['files']:
                p=paths(row)
                assert digest(f,p['active'])==row['baseline_sha256']
                assert all(digest(f,p[n]) is None for n in ['old','new','used'])
            private=Path('E:/xwn416/before001');private.mkdir(exist_ok=False)
            for path in ['/E/winnt/system32/config/sysevent.evt','/E/winnt/system32/config/appevent.evt',m.START]:
                data=m.get(f,path);dest=private/path.rsplit('/',1)[1];dest.write_bytes(data)
                r.setdefault('captures',{})[str(dest)]=m.sha(data)
            record(out,r)
            # Upload/read back all temporary candidate files before any active rename.
            for row in q['files']:
                p=paths(row);data=m.get(f,ROOT+'/candidate/'+row['relative'])
                assert m.sha(data)==row['candidate_sha256']
                r['operations'].append(dict(op='upload',target=p['new']));record(out,r)
                put(f,p['new'],data)
            for row in q['files']:
                p=paths(row)
                for source,target in [('active','old'),('new','active')]:
                    r['operations'].append(dict(op='rename',source=p[source],target=p[target]));record(out,r)
                    f.rename(p[source],p[target])
                assert digest(f,p['active'])==row['candidate_sha256']
                assert digest(f,p['old'])==row['baseline_sha256']
                r['files'][p['active']]=row['candidate_sha256'];record(out,r)
            for path,h in stage['protected'].items():
                if path in r['files']:h=r['files'][path]
                assert digest(f,path)==h,path
            r.update(completed=True,ended_utc=m.utc(),rollback_verified=True,
                     launch_path=r'E:\Applications\XWNEBoot\default.xbe',launch_route='Manual UnleashX File Explorer only')
    except BaseException as exc:r['error']=repr(exc);raise
    finally:record(out,r)
    print('Candidate active; rollback verified; no launch requested',flush=True)

def restore():
    q,stage=load();activation=m.read(K/'activation001.json')
    out=K/'restore001.json';assert not out.exists()
    r=dict(completed=False,started_utc=m.utc(),operations=[],before={},after={},console_C_accessed=False,
           script_sha256=m.sha(Path(__file__).read_bytes()))
    record(out,r)
    try:
        with m.connect() as f:
            plans=[]
            for row in q['files']:
                p=paths(row);state={k:digest(f,v) for k,v in p.items()};r['before'][row['relative']]=state
                plan=restore_plan(**state,baseline=row['baseline_sha256'],candidate=row['candidate_sha256'])
                plans.append((row,p,plan))
            record(out,r)
            private=Path('E:/xwn416/after001');private.mkdir(exist_ok=False)
            for path in ['/E/winnt/system32/config/sysevent.evt','/E/winnt/system32/config/appevent.evt',m.START]:
                data=m.get(f,path);dest=private/path.rsplit('/',1)[1];dest.write_bytes(data)
                r.setdefault('captures',{})[str(dest)]=m.sha(data)
            for row,p,plan in plans:
                for source,target in plan:
                    r['operations'].append(dict(op='rename',source=p[source],target=p[target]));record(out,r)
                    f.rename(p[source],p[target])
                assert digest(f,p['active'])==row['baseline_sha256']
                r['after'][p['active']]=row['baseline_sha256'];record(out,r)
            for path,h in stage['protected'].items():
                if '/config/' in path.lower():continue
                assert digest(f,path)==h,path
            r.update(completed=True,ended_utc=m.utc(),baseline_restored=True,
                     scope='Rollback and selected code/startup readback; no full cold disk or boot qualification')
    except BaseException as exc:r['error']=repr(exc);raise
    finally:record(out,r)
    print('Original loader files restored; code/startup verified',flush=True)

if __name__=='__main__':
    assert len(sys.argv)==2 and sys.argv[1] in ('activate','restore')
    globals()[sys.argv[1]]()
