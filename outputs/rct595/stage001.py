"""MIT. Move verified assets back to the qualified loader path; preserve both saves."""
import importlib.util
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('stage595controller',K/'controller001.py')
c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
m=c.m
SOURCE='/E/xwn593-kit'

def layout(f,q,moved=False):
    assert set(m.names(f,SOURCE))=={'owner.json','run593.exe','startup-used594.cmd'}| (set() if moved else {'game'})
    assert set(m.names(f,c.KIT))=={'owner.json','run586.exe','startup-used591.cmd','startup-used592.cmd'}|({'game'} if moved else set())
    assert 'xwn586p2' not in {n.lower() for n in m.names(f,'/E')}
    assert m.get(f,c.USED,True) is None
    root=(c.KIT if moved else SOURCE)+'/game'
    assert set(c.inventory(f,root))==set(q['reuse_expected'])

def run():
    q=c.verify();c.boot_work_closed();c.budget()
    out=K/'stage001.json';assert not out.exists() and not (K/'launch001.json').exists()
    r=dict(completed=False,utc=m.utc(),before={},staged={},writes=[],temporary_hook_installed=False,console_C_accessed=False,mode='720p')
    m.write_json(out,r)
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');r['startup_listing']=c.startup(f,False);layout(f,q)
    expected={SOURCE+'/game/'+n:v for n,v in q['reuse_expected'].items()}
    c.verify_batch(m,{**expected,**q['preserved']},r,out,'source_verified')
    for n in c.FILES:
        b=m.cold_pair(n,r,out);assert b is not None
        r['before'][n]=m.keep(c.P/'before',n,b);m.write_json(out,r)
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');assert c.startup(f,False)==r['startup_listing'];layout(f,q)
        for n,row in q['preserved'].items():assert m.sha(m.get(f,n))==row['sha256']
        r['writes'].append(dict(action='move-owned-game-once',source=SOURCE+'/game',destination=c.KIT+'/game'));m.write_json(out,r)
        f.rename(SOURCE+'/game',c.KIT+'/game');layout(f,q,True)
        for name in q['restore_assets']:
            n=c.KIT+'/game/'+name;row=q['files']['game/'+name]
            assert m.sha(m.get(f,n))==q['reuse_expected'][name]['sha256']
            r['writes'].append(dict(action='restore-pristine-mutable-asset',path=n));m.write_json(out,r)
            b=Path(row['path']).read_bytes();m.put(f,n,b);assert m.get(f,n)==b
    expected={c.KIT+'/'+n:row for n,row in q['files'].items() if n.startswith('game/')}
    c.verify_batch(m,{**expected,**q['preserved']},r,out,'staged')
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');assert c.startup(f,False)==r['startup_listing'];layout(f,q,True)
        for n,row in r['before'].items():assert m.sha(m.get(f,n))==row['sha256']
        for name,h in q['runtime_module_pins'].items():assert m.sha(m.get(f,'/E/winnt/system32/'+name))==h
        n=c.KIT+'/load586.exe';b=Path(q['files']['load586.exe']['path']).read_bytes();assert m.get(f,n,True) is None
        r['writes'].append(dict(action='put-new-helper-once',path=n));m.write_json(out,r);m.put(f,n,b)
        assert m.get(f,n)==b;r['staged'][n]=dict(bytes=len(b),sha256=m.sha(b));m.write_json(out,r)
        assert m.get(f,c.HOOK,True) is None
        r['writes'].append(dict(action='install-hook-last',path=c.HOOK));m.write_json(out,r);m.put(f,c.HOOK,c.hook())
        assert m.get(f,c.HOOK)==c.hook();r['temporary_hook_installed']=True;m.write_json(out,r)
        c.startup(f,True)
    r.update(completed=True,ended_utc=m.utc());m.write_json(out,r)

if __name__=='__main__':run()
