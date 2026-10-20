"""MIT. Freeze unchanged PC586 Load helper with both physical saved parks."""
import datetime,hashlib,importlib.util,json,shutil,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
out=K/'package001.json';assert not out.exists()
old=K.parent/'rct594';col=read(old/'collection001.json');st=read(old/'stage003.json')
assert read(old/'final001.json')['closed'] and col['completed'] and col['hook_removed']
assert read(K.parent/'rct586/final002.json')['passed']
helper=Path('C:/xwn586/phase2-build001/load586.exe')
assert sha(helper)==read(K.parent/'rct586/phase2-source/media001.json')['exe_sha256']=='63839df4fbc77ac6aca4928b33570be8d1c64f487c235ad3e77a68881bac09f8'
priorq=read(old/'package003.json')
files={n:v for n,v in priorq['files'].items() if n.startswith('game/')}
files['game/Saved Games/XWN593.SV4']=col['files']['/E/xwn593-kit/game/Saved Games/XWN593.SV4']
files['load586.exe']=dict(path=str(helper),bytes=helper.stat().st_size,sha256=sha(helper))
expected={};restore=[]
for n,row in files.items():
    if not n.startswith('game/'):continue
    remote='/E/xwn593-kit/'+n;v=col['files'].get(remote) or st['staged'][remote]
    expected[n[5:]]=dict(bytes=v['bytes'],sha256=v['sha256'])
    if v['sha256']!=row['sha256']:restore.append(n[5:])
assert len(expected)==504 and set(restore)<= {'Data/Game.cfg','Data/CSS0.DAT'}
assert set(col['game_rows'])=={'/E/xwn593-kit/game/'+n for n in expected}
preserved={}
for root in ['rct591','rct592','rct594']:
    for n,row in read(K.parent/root/'collection001.json')['files'].items():
        if n.startswith(('/E/xwn586-kit/','/E/xwn593-kit/')) and '/game/' not in n:preserved[n]=row
assert len(preserved)==7
for row in list(files.values())+list(preserved.values()):
    p=Path(row['path']);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
free=shutil.disk_usage('C:/').free;assert free-128*1024**2>=20*1024**3
# Prior594 reserved128MiB explicitly for save AND next load; actual saved results <30MiB.
used=sum(r['bytes'] for n,r in col['files'].items() if n.startswith('/E/xwn593/'))+290247+helper.stat().st_size
assert used<64*1024**2
space=read(old/'console-space001.json');assert space['projected_remaining_bytes']>=128*1024**2
(K/'console-space001.json').write_text(json.dumps(dict(admitted=True,fresh_measurement=False,source='594 joint128MiB save/load allowance;594 actual result bytes plus595 bounded40x2MiB and8MiB OS allowance',prior_joint_allowance=128*1024**2,actual594_new_bytes=used,load_allowance=88*1024**2,projected_remaining_bytes=space['previous_remaining']-used-88*1024**2),indent=2)+'\n')
assert space['previous_remaining']-used-88*1024**2>=128*1024**2
test=read(K/'host002.json');assert test['passed']
for n,h in test['pins'].items():assert sha(K/n)==h
s=importlib.util.spec_from_file_location('package595',K/'controller001.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c);c.pair.verify();c.boot_work_closed()
pins=dict(read(K.parent/'windows-pair532/preflight001.json')['pins'])
for p in K.iterdir():
    if p.is_file():pins[str(p.resolve())]=sha(p)
for module in list(sys.modules.values()):
    n=getattr(module,'__file__',None)
    if n:
        p=Path(n).resolve()
        if p.is_relative_to(W) and p.is_file():pins[str(p)]=sha(p)
for rel in ['rct594/final001.json','rct594/collection001.json','rct594/stage003.json','rct586/final002.json','rct586/load-visual001.json','rct586/phase2-source/media001.json','rct586/phase2-source/build002.json']:
    p=K.parent/rel;pins[str(p.resolve())]=sha(p)
r=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=files,reuse_expected=expected,restore_assets=restore,preserved=preserved,runtime_module_pins=priorq['runtime_module_pins'],pins=pins,physical_attempt=595,pc_probe=586,phase=2,allowed_launches=1,cold_start_confirmed=False,helper_binary_unchanged=True,closed_runtime_reopened=False,manual_observation_seconds=360,host_free_bytes=free,host_allowance_bytes=128*1024**2,limits='Watched Load only; elapsed time/input sequence0 are not load proof. No FPS or GPU claim.')
out.write_text(json.dumps(r,indent=2)+'\n');print('Frozen595',len(files),'files; restore',restore)
