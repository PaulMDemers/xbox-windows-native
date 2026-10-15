"""One cold collection of the OEM/WMP continuation; retain all strict failures."""
import ast,json,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'emu001';run=Path('/mnt/e/xwn406/runs/nt5-validation406-emu001');P=Path('/mnt/e/xwn406/cold001')
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,sha,HIVES,STARTUP
from oem_reader import OemReader
sys.path.insert(0,str(W/'outputs/release-readiness403'));from stock_io002 import scan
sys.path.insert(0,str(W/'work/python-packages'));sys.path.insert(0,str(W/'outputs/clean-media404'));from hive_audit004 import audit as hiveaudit
dest=out/'audit.json';assert not dest.exists() and (run/'cleanup.json').exists()
host=json.loads((run/'host-exit.json').read_text());assert host['closed']
base=json.loads((K/'assembly003.json').read_text());source=Path(base['fixture_path_linux']);disk=run/'hdd.qcow2';assert sha(source)==base['fixture_sha256']
for p,d in json.loads((out/'frozen.json').read_text()).items():assert sha(W/p)==d,p
assert not P.exists();P.mkdir();m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
tree=ast.parse((W/'outputs/fresh-assembly405/normal-stage006.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='inventory')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'original405-inventory','exec'))
r=dict(physical_access=False,source_unchanged=True,events={},hives=[],files={},shortcuts=[],host_exit=host)
for phase,path in [('before',source),('after',disk)]:
    folder=P/phase;folder.mkdir()
    with ColdIO(path) as io:
        wr=OemReader(io,m.fatx.open_partition(io,path,'E'));allfiles=inventory(wr)
        assert STARTUP.lower() not in allfiles
        (folder/'files.json').write_text(json.dumps(allfiles,indent=2)+'\n')
        r['files'][phase]=len(allfiles)
        for name in HIVES+['sysevent.evt','appevent.evt']:(folder/name).write_bytes(wr.read('winnt/system32/config/'+name))
        (folder/'setupapi.log').write_bytes(wr.read('winnt/setupapi.log'))
        if phase=='after':
            for p in ['XWN409/result.log','XWN409/drm-value.bin']:
                try:b=wr.read(p);(folder/Path(p).name).write_bytes(b)
                except KeyError:pass
            for user in ['Default User','Win2K']:
                p='Documents and Settings/'+user+'/SendTo/3\u00bd Floppy (A).lnk'
                try:digest=m.sha(wr.read(p))
                except KeyError:digest=None
                r['shortcuts'].append(dict(path=p,sha256=digest,exact_original=digest=='a17666e9f5ca27b79b5d8b925dcce3a6e60367031402a31278d354cace814b42'))
            original=json.loads((W/'outputs/fresh-assembly405/installed-final001.json').read_text())
            r['protected']=[dict(path=v['path'],exact=allfiles.get(v['path'].lower())==v['sha256']) for v in original['fresh403_components']]
            r['staged_files_exact']=all(allfiles.get(v['path'].lower())==v['sha256'] for v in base['changes'])
    if phase=='after':r['hives']=[hiveaudit(folder/name) for name in HIVES]
    for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
        target=folder/(label+'-events.json')
        subprocess.run([sys.executable,str(W/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(folder/name),'--output',str(target)],stdout=subprocess.DEVNULL,check=True)
        r['events'].setdefault(label,{})[phase]=json.loads(target.read_text())['records']
new=[];history=True
for label,phases in r['events'].items():
    a,b=phases['before'],phases['after'];by={v['record']:v for v in b};history &= all(by.get(v['record'])==v for v in a)
    boundary=max([v['record'] for v in a],default=0);delta=[v for v in b if v['record']>boundary]
    r['events'][label]=dict(before_count=len(a),after_count=len(b),new=delta);new+=delta
logs={}
if (P/'after/result.log').exists():
    for line in (P/'after/result.log').read_text().splitlines():
        key,val=line.split('=',1);assert key not in logs;logs[key]=int(val)
    (out/'result.log').write_bytes((P/'after/result.log').read_bytes())
scan(disk,out/'after-allocation/artifacts');allocation=json.loads((out/'after-allocation/allocation.json').read_text())
launch=json.loads((out/'launch.json').read_text())
drm=(P/'after/drm-value.bin')
checks=dict(native_oemcp437=logs.get('OEMCP')==437,exact_restored_shortcuts=all(v['exact_original'] for v in r['shortcuts']),
    native_drm_query=logs.get('DRM_QUERY')==0 and logs.get('DRM_TYPE')==1028 and logs.get('DRM_BYTES')==80 and drm.exists() and sha(drm)=='781086c1ea4f406b9b33e8b0cb8fcf10a7d4c2636bf0f409f88136d4110fde4a',
    witness=logs.get('COMPLETE')==406,normal_restart=logs.get('NORMAL_RESTART_REQUEST')==1 and sum(v['source']=='EventLog' and v['event_id']==6006 for v in new)==1,
    dashboard_return=any(v.get('dashboard_return') for v in launch['cycles']),orderly_host=host['passed'],
    event_history=history,allocation=allocation['allocation_consistent'],protected=all(v['exact'] for v in r['protected']),
    hives=all(v['header_valid'] and v['clean'] and v['independent_raw_values_agree'] for v in r['hives']))
r.update(checks=checks,witness=logs,allocation=allocation,warning_error_events=[v for v in new if v['type'] in [1,2]],
         disk_sha256=sha(disk),qcow_check=json.loads(subprocess.check_output(['qemu-img','check','--output=json',str(disk)])),
         strict_qualification=False,remaining_long_path_exclusions=6,typed_decoder_still_unsupported=True,
         wmp_process_completion_is_not_playback_proof=True,scope='Native filename and registry evidence plus cold integrity. Video/audio captures qualified independently. Original405 verdict unchanged.')
r['private_captures']={p.relative_to(P).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in P.rglob('*') if p.is_file()}
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(checks=checks,witness=logs,warnings=[dict(source=v['source'],id=v['event_id']) for v in r['warning_error_events']])))
