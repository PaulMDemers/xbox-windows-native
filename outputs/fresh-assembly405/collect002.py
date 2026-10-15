"""Single cold collection of closed fresh assembly emu001; all failures retained."""
import hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'emu001';run=Path('/mnt/c/xwn405/runs/nt5-fresh405-emu001')
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,sha,HIVES
sys.path.insert(0,str(W/'outputs/release-readiness403'));from stock_io002 import scan
sys.path.insert(0,str(W/'work/python-packages'));sys.path.insert(0,str(W/'outputs/clean-media404'));from hive_audit004 import audit as hiveaudit
dest=out/'audit.json';assert not dest.exists() and (run/'cleanup.json').exists() and json.loads((run/'host-exit.json').read_text())['closed']
base=json.loads((K/'assembly001.json').read_text());source=Path(base['fixture_path_linux']);disk=run/'hdd.qcow2'
assert sha(source)==base['fixture_sha256']
for p,digest in json.loads((out/'frozen.json').read_text()).items():assert sha(W/p)==digest,p
P=Path('/mnt/c/xwn405/cold001');assert not P.exists();P.mkdir()
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
r=dict(physical_access=False,source_preserved=True,logs={},hives=[],events={},protected=[],errors=[])
for phase,path in [('before',source),('after',disk)]:
    folder=P/phase;folder.mkdir()
    with ColdIO(path) as io:
        wr=m.Writer(io,m.fatx.open_partition(io,path,'E'))
        for name in ['system','software','default','sam','security','sysevent.evt','appevent.evt']:
            b=wr.read('winnt/system32/config/'+name);(folder/name).write_bytes(b)
        (folder/'setupapi.log').write_bytes(wr.read('winnt/setupapi.log'))
        if phase=='after':
            for name in ['result.log','data.bin']:
                try:b=wr.read('XWN405/'+name)
                except KeyError:r['logs'][name]=None;continue
                (folder/name).write_bytes(b);r['logs'][name]=dict(bytes=len(b),sha256=m.sha(b))
            for row in base['files']:
                key=row['path'].lower()
                if base['sources'][key]['kind'].startswith(('fresh403','fresh405','same customized ISO')) or key=='winnt/system32/ntoskrnl.exe':
                    try:digest=m.sha(wr.read(row['path']))
                    except KeyError:digest=None
                    r['protected'].append(dict(path=row['path'],before=row['sha256'],after=digest,unchanged=digest==row['sha256']))
    if phase=='after':
        for name in HIVES:
            try:row=hiveaudit(folder/name)
            except Exception as exc:row=dict(error=repr(exc))
            r['hives'].append(dict(**row))
    for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
        target=folder/(label+'-events.json')
        subprocess.run([sys.executable,str(W/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(folder/name),'--output',str(target)],check=True,stdout=subprocess.DEVNULL)
        r['events'].setdefault(label,{})[phase]=json.loads(target.read_text())['records']
new=[];history=True
for label,phases in r['events'].items():
    a,b=phases['before'],phases['after'];by={v['record']:v for v in b};history &= all(by.get(v['record'])==v for v in a)
    boundary=max([v['record'] for v in a],default=0);delta=[v for v in b if v['record']>boundary]
    r['events'][label]=dict(before_count=len(a),after_count=len(b),new=delta);new+=delta
logs={}
if (P/'after/result.log').exists():
    for line in (P/'after/result.log').read_text().splitlines():
        if '=' in line:
            key,val=line.split('=',1);assert key not in logs;logs[key]=int(val)
    (out/'result.log').write_bytes((P/'after/result.log').read_bytes())
data_ok=(P/'after/data.bin').exists() and (P/'after/data.bin').read_bytes()==bytes((i*37+(i>>8)+0x5a)&255 for i in range(32768))
scan(disk,out/'after-allocation/artifacts');allocation=json.loads((out/'after-allocation/allocation.json').read_text())
launch=json.loads((out/'launch.json').read_text());closed=json.loads((run/'host-exit.json').read_text())
checks=dict(witness_complete=logs.get('COMPLETE')==405,reported_persistence=logs.get('PERSISTENCE')==1,cold_exact_data=data_ok,
    mode720p=logs.get('WIDTH')==1280 and logs.get('HEIGHT')==720 and logs.get('BPP')==32,memory_gdi=logs.get('MEMORY_GDI')==1,
    audio=logs.get('WAVE_DEVICES',0)>0 and logs.get('AUDIO_RESULT')==0,
    normal_restart=logs.get('NORMAL_RESTART_REQUEST')==1 and sum(v['source']=='EventLog' and v['event_id']==6006 for v in new)==1,
    dashboard_return=any(v.get('dashboard_return') for v in launch['cycles']),orderly_host=closed['passed'],
    event_history_preserved=history,protected_exact=all(v['unchanged'] for v in r['protected']),allocation=allocation['allocation_consistent'],hives=all(v.get('header_valid') and v.get('clean') and v.get('independent_raw_values_agree') for v in r['hives']))
warnings=[v for v in new if v['type'] in [1,2]]
r.update(checks=checks,witness=logs,allocation=allocation,new_warning_error_events=warnings,host_exit=closed,
         strict_lossless_transfer=False,strict_qualification=False,core_boot_scoped_passed=all(v for k,v in checks.items() if k!='audio'),
         runtime_components_all_passed=all(checks.values()),disk_sha256=sha(disk),qcow_check=json.loads(subprocess.check_output(['qemu-img','check','--output=json',str(disk)])),
         scope='Fresh assembly emulator boot/API witness and cold allocation/selected code/hives/events; no hardware or performance qualification. FATX path exclusions and inherited typed DRM decoding limit remain.')
r['private_captures']={p.relative_to(P).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in P.rglob('*') if p.is_file()}
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(checks=checks,warnings=[dict(source=v['source'],id=v['event_id']) for v in warnings])))
