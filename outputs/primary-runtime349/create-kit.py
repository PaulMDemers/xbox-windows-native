"""Fresh matched runtime, preserving346 gates and never-executed339 parent."""
import ast,difflib,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;P=K.parent/'hd-phase-runtime346';changes={}
names=['Invoke.ps1','Run.ps1','close-host.py','analyze-allocation002.py','stock_io002.py','analyze-capture.py','typed-state.py','installed-binding.py','supervise.py','audit002.py','prepare.py','contract002.ps1','freeze.py']
for name in names:
    target='audit.py' if name=='audit002.py' else name;old=(P/name).read_text();s=old
    s=s.replace('xwn346','xwn349').replace('phase346','primary349').replace('5166','5176').replace('5167','5177').replace('5168','5178')
    if name=='audit002.py':
        s=s.replace("mode=int(case=='candidate001')","mode=1")
        needle="r['display_workload_passed'] &= all(v['passed'] for v in r['large_phase_samples'])"
        assert s.count(needle)==1;s=s.replace(needle,needle+"\nfrom primary_analysis import analyze as primary_analysis\nr['primary_samples']=[primary_analysis(v,int(case=='candidate001')) for v in texts]\nr['display_workload_passed'] &= all(v['passed'] for v in r['primary_samples'])")
        s=s.replace("r['limits']='New combined audio/video ordinary test; strict warnings retained, no physical or release qualification.'","r['limits']='New348 primary-copy body: clock category1 measures selected fast/Eng body. New coverage required; original strict warnings retained, no physical speed or release qualification.'")
    if name=='prepare.py':
        s=s.replace("K.parent/'hd-profile345/", "K.parent/'primary-copy348/")
        s=s.replace('/mnt/e/xwn345/build001','/mnt/e/xwn348/build001').replace('/mnt/e/xwn344/build001','/mnt/e/xwn348/probe/build001')
        s=s.replace("K.parent/'hd-phase344/build-review001.json'","K.parent/'primary-copy348/probe/build-review001.json'")
        oldreserve="reserve=image['virtual-size']+parent.stat().st_size+512*1024**2\nassert shutil.disk_usage('/mnt/e').free-reserve>=20*1024**3,'Projected full raw + compressed output reserve'"
        newreserve="""mapping=json.loads(subprocess.check_output(['qemu-img','map','--output=json',str(parent)]))
data_bytes=sum(v['length'] for v in mapping if v['data'])
reserve=data_bytes+512*1024**2
assert shutil.disk_usage('/mnt/e').free-reserve>=20*1024**3,'Projected allocated extents plus512MiB metadata/new payload reserve'
rawroot=Path('/home/paul/xbox-windows-native/work/primary349-'+case)
assert not rawroot.exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
rawspace=require_space(rawroot);assert all(v['free_bytes']-image['virtual-size']-512*1024**2>=20*1024**3 for v in rawspace['checks'])
rawroot.mkdir(parents=True)"""
        assert oldreserve in s;s=s.replace(oldreserve,newreserve).replace("raw=P/'staging.raw'","raw=rawroot/'staging.raw'")
        s=s.replace("projected_reserve_bytes=reserve)","projected_reserve_bytes=reserve,parent_data_bytes=data_bytes,raw_staging_space=rawspace,raw_staging_root=str(rawroot))")
        s=s.replace("assert raw.resolve().parent==P.resolve()","assert raw.resolve().parent==rawroot.resolve()")
        s=s.replace("'profile_mode':int(case=='candidate001')","'profile_mode':1,'primary_mode':int(case=='candidate001')")
    if name=='freeze.py':
        s=s.replace("K.parent/'hd-profile345/","K.parent/'primary-copy348/")
        s=s.replace("pins={}","paths+=list((K.parent/'primary-copy348').glob('*.py'))+[K.parent/'primary-copy348/host002.json',K.parent/'primary-copy348/probe/build-review001.json',K.parent/'primary-copy348/probe/build001.json',K/'parser001.json']\npins={}")
    if name=='contract002.ps1':s=s.replace('case_modes=@{control001=0;candidate001=1}','case_modes=@{control001=1;candidate001=1}')
    assert not (K/target).exists();(K/target).write_text(s)
    if target.endswith('.py'):ast.parse(s)
    changes[target]=dict(parent_sha256=hashlib.sha256((P/name).read_bytes()).hexdigest(),sha256=hashlib.sha256((K/target).read_bytes()).hexdigest())
    (K/(target+'.patch')).write_text(''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='346/'+name,tofile='349/'+target)))
(K/'source-review.json').write_text(json.dumps(dict(inputs=changes,physical_access=False,changes='New348 driver/probe, primary coverage gate, profilingON both, unique roots/ports. Raw staging on C-backedWSL with20GiB projected reserve; compressed output budget bounded by allocated parent extents+512MiB. Original functional/event/integrity gates retained.'),indent=2)+'\n')
(K/'.gitignore').write_text('**/artifacts/\n')
