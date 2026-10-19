"""MIT. Fresh retail game fixture through ordinary launcher; one launch, owned hook."""
import importlib.util,json,shutil,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn590/physical001')
s=importlib.util.spec_from_file_location('pair532',K.parent/'windows-pair532/controller.py')
pair=importlib.util.module_from_spec(s);s.loader.exec_module(pair)
m=pair.m;read=pair.read
KIT='/E/xwn589-kit';RESULT='/E/xwn589';HOOK=m.START+'/xwn590.cmd'
USED=KIT+'/startup-used590.cmd';FILES=pair.FILES+['/E/documents and settings/Win2K/NTUSER.DAT','/E/winnt/welcome.exe']

def hook():
    return b'@echo off\r\nif exist C:\\xwn589 goto done\r\nC:\\xwn589-kit\\run589.exe\r\n:done\r\nexit\r\n'

def verify():
    pair.verify();q=read(K/'package001.json');assert q['passed']
    for p,h in q['pins'].items():assert m.sha(Path(p).read_bytes())==h,p
    for row in q['files'].values():
        b=Path(row['path']).read_bytes();assert len(b)==row['bytes'] and m.sha(b)==row['sha256']
    for name in q['runtime_module_pins']:assert name==Path(name).name and '/' not in name and chr(92) not in name
    return q

def boot_work_closed():
    assert read(K/'ready001.json')['cold_start_ready']
    assert read(K.parent/'rct583/final001.json')['closed']
    assert read(K.parent/'save588/final001.json')['closed']
    prior=read(K.parent/'rct589/final001.json')
    assert prior['closed'] and prior['input_qualified'] and prior['cleanup_qualified']
    assert read(K.parent/'rct565/final001.json')['closed']
    assert read(K.parent/'rct576/final001.json')['closed']
    assert read(K.parent/'rct566/transfer001.json')['passed']


def startup(f,armed):
    allowed={'xwnsetup.cmd','desktop.ini'}|({'xwn590.cmd'} if armed else set())
    rows=m.names(f,m.START);assert {n.lower() for n in rows}<=allowed
    assert m.sha(m.get(f,m.NORMAL))=='da47fdf32e29b81ba9f5148d86f291ed708c9432c268b1682668c5b50883aa43'
    assert m.sha(m.get(f,m.TARGET))=='6240a801d97c4894e56d516a934059da056446fb77cf895b5364bdd6cd24be9a'
    if armed:assert m.get(f,HOOK)==hook()
    return rows

def budget():assert shutil.disk_usage('C:/').free-128*1024**2>=20*1024**3

def inventory(f,root):
    rows={};todo=[root];seen=set()
    while todo:
        directory=todo.pop();assert directory not in seen and len(seen)<20;seen.add(directory)
        for name,row in m.names(f,directory).items():
            assert name not in ('','.','..') and '/' not in name and chr(92) not in name
            path=directory+'/'+name
            if row['directory']:todo.append(path)
            else:
                rel=path[len(root)+1:];assert rel not in rows and len(rows)<600 and row['bytes']<=64*1024**2
                rows[rel]=row
    return rows

def stage():
    q=verify();boot_work_closed();budget();out=K/'stage001.json'
    assert not out.exists() and not P.exists();P.mkdir(parents=True)
    space=read(K/'console-space001.json');assert space['admitted'] and space['projected_remaining_bytes']>=128*1024**2
    r=dict(completed=False,utc=m.utc(),before={},staged={},writes=[],asset_before={},console_C_accessed=False,temporary_hook_installed=False,mode='720p',assets_only_reuse=True)
    m.write_json(out,r);old='/E/xwn582-kit/game'
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');r['startup_listing']=startup(f,False)
        assert not {'xwn589','xwn589-kit'}&{n.lower() for n in m.names(f,'/E')}
        assert m.sha(m.get(f,'/E/xwn582-kit/owner.json'))==q['previous_owner_sha256']
    for n in FILES:
        b=m.cold_pair(n,r,out);assert b is not None;r['before'][n]=m.keep(P/'before',n,b);m.write_json(out,r)
    deadline=time.monotonic()+600
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');assert startup(f,False)==r['startup_listing']
        assert not {'xwn589','xwn589-kit'}&{n.lower() for n in m.names(f,'/E')}
        for n,row in r['before'].items():assert m.sha(m.get(f,n))==row['sha256']
        inv=inventory(f,old);assert set(inv)==set(q['reuse_expected'])
        for rel,row in q['reuse_expected'].items():
            assert time.monotonic()<deadline
            b=m.get(f,old+'/'+rel);assert len(b)==row['bytes'] and m.sha(b)==row['sha256'],rel
            r['asset_before'][rel]=dict(bytes=len(b),sha256=m.sha(b));m.write_json(out,r)
        r['writes'].append(dict(action='mkdir',path=KIT));m.write_json(out,r);f.mkd(KIT)
        owner=json.dumps(dict(project='xbox-windows-native',attempt=590,package_sha256=m.sha((K/'package001.json').read_bytes()),pristine_assets_reused_from_closed583=True),sort_keys=True).encode()
        r['writes'].append(dict(action='put',path=KIT+'/owner.json'));m.write_json(out,r);m.put(f,KIT+'/owner.json',owner);assert m.get(f,KIT+'/owner.json')==owner
        r['staged'][KIT+'/owner.json']=dict(bytes=len(owner),sha256=m.sha(owner));m.write_json(out,r)
        r['writes'].append(dict(action='move-verified-retail-assets-only',source=old,destination=KIT+'/game'));m.write_json(out,r)
        f.rename(old,KIT+'/game')
        assert 'game' not in m.names(f,'/E/xwn582-kit') and set(inventory(f,KIT+'/game'))==set(inv)
        for rel in q['restore_assets']:
            n=KIT+'/game/'+rel;b=Path(q['files']['game/'+rel]['path']).read_bytes()
            r['writes'].append(dict(action='restore-pristine-asset',path=n));m.write_json(out,r);m.put(f,n,b);assert m.get(f,n)==b
        for name,row in q['files'].items():
            assert time.monotonic()<deadline;n=KIT+'/'+name
            if name=='run589.exe':
                b=Path(row['path']).read_bytes();r['writes'].append(dict(action='put',path=n));m.write_json(out,r);m.put(f,n,b)
            b=m.get(f,n);assert len(b)==row['bytes'] and m.sha(b)==row['sha256'],n
            r['staged'][n]=dict(bytes=len(b),sha256=m.sha(b));m.write_json(out,r)
        assert set(m.names(f,KIT))=={'owner.json','run589.exe','game'}
        for name,h in q['runtime_module_pins'].items():assert m.sha(m.get(f,'/E/winnt/system32/'+name))==h
        assert m.get(f,HOOK,True) is None
        r['writes'].append(dict(action='install-hook-last',path=HOOK));m.write_json(out,r);m.put(f,HOOK,hook());assert m.get(f,HOOK)==hook()
        r['temporary_hook_installed']=True;m.write_json(out,r);m.baseline(f,'720p');startup(f,True)
    r.update(completed=True,ended_utc=m.utc());m.write_json(out,r)

def launch():
    q=verify();boot_work_closed();out=K/'launch001.json';assert not out.exists()
    st=read(K/'stage001.json');assert st['completed'] and st['temporary_hook_installed']
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');startup(f,True)
        assert 'xwn589' not in {n.lower() for n in m.names(f,'/E')}
        assert set(m.names(f,KIT))=={'owner.json','run589.exe','game'}
        for n,row in {**st['before'],**st['staged']}.items():
            b=m.get(f,n);assert len(b)==row['bytes'] and m.sha(b)==row['sha256'],n
        for name,h in q['runtime_module_pins'].items():assert m.sha(m.get(f,'/E/winnt/system32/'+name))==h
        pair.request_once(f,out,dict(stage_sha256=m.sha((K/'stage001.json').read_bytes()),ordinary_launcher=True,automatic_restart_requested_by_runner=True,native_pc_control=589,unattended=False,console_C_accessed=False,one_launch_only=True))

def result_names(rows):
    assert len(rows)<=24
    for name,row in rows.items():
        assert name not in ('','.','..') and '/' not in name and chr(92) not in name
        assert not row['directory'] and 0<=row['bytes']<=2*1024**2
    return [RESULT+'/'+name for name in rows]

def collect():
    q=verify();budget();assert read(K/'launch001.json')['requested']
    out=K/'collection001.json';assert not out.exists();st=read(K/'stage001.json')
    r=dict(completed=False,utc=m.utc(),files={},remote_writes=[],console_C_accessed=False,mode='720p',hook_removed=False)
    m.write_json(out,r)
    with m.connect(timeout=15) as f:
        # First remote mutation after dashboard return: disable only our exact hook.
        assert m.get(f,HOOK)==hook() and m.get(f,USED,True) is None
        r['remote_writes'].append(dict(action='rename-owned-hook',source=HOOK,destination=USED));m.write_json(out,r)
        f.rename(HOOK,USED);assert m.get(f,HOOK,True) is None and m.get(f,USED)==hook()
        r['hook_removed']=True;m.write_json(out,r)
        m.baseline(f,'720p');r['startup_listing']=startup(f,False);r['protected_code_exact']=True
        extra=[]
        if 'xwn589' in {n.lower() for n in m.names(f,'/E')}:
            rows=m.names(f,RESULT);r['result_directory']=rows;extra=result_names(rows)
        game_rows={};todo=[KIT+'/game'];seen=set()
        while todo:
            directory=todo.pop();assert directory not in seen and len(seen)<1000;seen.add(directory)
            for name,row in m.names(f,directory).items():
                assert name not in ('','.','..') and '/' not in name and chr(92) not in name
                path=directory+'/'+name
                if row['directory']:todo.append(path)
                else:game_rows[path]=row;assert len(game_rows)<=1000 and row['bytes']<=64*1024**2
        r['game_rows']=game_rows;m.write_json(out,r)
    # Full directory inventory, selected payload contents. New files always collected.
    selected=[n for n in game_rows if n not in st['staged'] or n.lower().endswith(('/rct.exe','/data/game.cfg','/data/css0.dat','.sv4','.sv6'))]
    paths=list(dict.fromkeys(FILES+[KIT+'/owner.json',KIT+'/run589.exe']+selected+[USED]+extra+['/E/winnt/system32/'+n for n in q['runtime_module_pins']]))
    r['collection_scope']='Whole game directory inventory; selected executable/config/CSS0/saves/new files and all result files. Other retail contents not rehashed after execution.'
    r['selected_paths']=paths;m.write_json(out,r)
    for n in paths:
        b=m.cold_pair(n,r,out);assert b is not None,n
        if n in extra:assert len(b)==r['result_directory'][n.rsplit('/',1)[1]]['bytes']
        prior=st['before'].get(n) or st['staged'].get(n)
        if n.startswith(KIT+'/game/') and prior and m.sha(b)==prior['sha256']:
            original=q['files'][n[len(KIT)+1:]]
            row=dict(path=original['path'],bytes=len(b),sha256=m.sha(b),unchanged=True,identical_payload_retained_once=True)
        else:row=m.keep(P/'after',n,b)
        if prior:row['unchanged']=row['sha256']==prior['sha256']
        r['files'][n]=row;m.write_json(out,r)
    r.update(completed=True,ended_utc=m.utc(),normal_shutdown_proved=False,graphics_pass=False)
    m.write_json(out,r)

if __name__=='__main__':
    assert len(sys.argv)==2 and sys.argv[1] in ('stage','launch','collect');globals()[sys.argv[1]]()
