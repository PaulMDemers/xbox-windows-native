"""MIT. Fresh retail game fixture through ordinary launcher; one launch, owned hook."""
import importlib.util,json,shutil,sys,time
from batch_read001 import verify_batch
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn594/physical001')
s=importlib.util.spec_from_file_location('pair532',K.parent/'windows-pair532/controller.py')
pair=importlib.util.module_from_spec(s);s.loader.exec_module(pair)
m=pair.m;read=pair.read
KIT='/E/xwn593-kit';RESULT='/E/xwn593';HOOK=m.START+'/xwn594.cmd'
USED=KIT+'/startup-used594.cmd';FILES=pair.FILES+['/E/documents and settings/Win2K/NTUSER.DAT','/E/winnt/welcome.exe']

def hook():
    return b'@echo off\r\nif exist C:\\xwn593 goto done\r\nC:\\xwn593-kit\\run593.exe\r\n:done\r\nexit\r\n'

def verify():
    pair.verify();q=read(K/'package003.json');assert q['passed']
    for p,h in q['pins'].items():assert m.sha(Path(p).read_bytes())==h,p
    for row in q['files'].values():
        b=Path(row['path']).read_bytes();assert len(b)==row['bytes'] and m.sha(b)==row['sha256']
    for name in q['runtime_module_pins']:assert name==Path(name).name and '/' not in name and chr(92) not in name
    return q

def boot_work_closed():
    assert read(K.parent/'rct592/final001.json')['closed']
    assert read(K.parent/'rct593/final001.json')['closed']
    assert read(K.parent/'rct593/save-review002.json')['passed']
    assert read(K.parent/'rct566/transfer001.json')['passed']


def startup(f,armed):
    allowed={'xwnsetup.cmd','desktop.ini'}|({'xwn594.cmd'} if armed else set())
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



def launch():
    q=verify();boot_work_closed();out=K/'launch001.json';assert not out.exists()
    st=read(K/'stage003.json');assert st['completed'] and st['temporary_hook_installed']
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');startup(f,True)
        assert 'xwn593' not in {n.lower() for n in m.names(f,'/E')}
        assert set(m.names(f,KIT))=={'owner.json','run593.exe','game'}
    check=K/'launch-preflight003.json';assert not check.exists()
    rec=dict(completed=False,verified={},remote_writes=[],launch_requested=False);m.write_json(check,rec)
    verify_batch(m,{**st['before'],**st['staged']},rec,check,'verified')
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');startup(f,True)
        assert 'xwn593' not in {n.lower() for n in m.names(f,'/E')}
        assert set(inventory(f,KIT+'/game'))==set(q['reuse_expected'])
        for n in [KIT+'/run593.exe',KIT+'/owner.json']:
            assert m.sha(m.get(f,n))==st['staged'][n]['sha256']
        for name,h in q['runtime_module_pins'].items():assert m.sha(m.get(f,'/E/winnt/system32/'+name))==h
        rec['completed']=True;m.write_json(check,rec)
        pair.request_once(f,out,dict(stage_sha256=m.sha((K/'stage003.json').read_bytes()),preflight_sha256=m.sha(check.read_bytes()),ordinary_launcher=True,automatic_restart_requested_by_runner=True,native_pc_control=593,unattended=False,console_C_accessed=False,one_launch_only=True))


def result_names(rows):
    assert len(rows)<=24
    for name,row in rows.items():
        assert name not in ('','.','..') and '/' not in name and chr(92) not in name
        assert not row['directory'] and 0<=row['bytes']<=2*1024**2
    return [RESULT+'/'+name for name in rows]

def collect():
    q=verify();budget();assert read(K/'launch001.json')['requested']
    out=K/'collection001.json';assert not out.exists();st=read(K/'stage003.json')
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
        if 'xwn593' in {n.lower() for n in m.names(f,'/E')}:
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
    paths=list(dict.fromkeys(FILES+[KIT+'/owner.json',KIT+'/run593.exe']+selected+[USED]+extra+['/E/winnt/system32/'+n for n in q['runtime_module_pins']]))
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
    assert len(sys.argv)==2 and sys.argv[1] in ('launch','collect');globals()[sys.argv[1]]()
