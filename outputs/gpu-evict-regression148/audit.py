"""Collect closed native run once; independently verify pixels and unchanged disk ranges."""
import subprocess
from common import *
from oracle import expected,compare,validate_log
case=sys.argv[1];assert case in ['control001','candidate001']
out=k/case;art=out/'artifacts';art.mkdir(exist_ok=False)
assert not (out/'audit.json').exists()
f=read(k/('fixture-'+case+'.json'));base=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name']
disk=ws/('work/runs/gpu-regression148-'+case+'/hdd.qcow2')
assert (disk.parent/'cleanup.json').exists() and sha(base)==f['fixture_sha256']
for row in f['parents']:assert sha(Path(row['path']))==row['sha256']
r=dict(physical_access=False,windows_launched=False,debugger=False,timing_qualified=False,files=[])
with ColdIO(disk) as io:
    w=e_reader(io,disk);state=inventory(w);save(out/'after-e.json',state)
    def optional(p):
        try:return w.read(p)
        except KeyError:return None
    bootstrap=optional('Applications/XWNGpu144/bootstrap.log')
    if bootstrap is not None:(art/'bootstrap.log').write_bytes(bootstrap)
    r['bootstrap_log']=None if bootstrap is None else bootstrap.decode('ascii',errors='backslashreplace')
    log=optional('xwngpu144/result.log');r['log']=None if log is None else log.decode('ascii',errors='backslashreplace')
    r['protocol_passed']=False
    if log is not None:
        (art/'result.log').write_bytes(log)
        try:r['surfaces']=validate_log(log);r['protocol_passed']=True
        except (AssertionError,UnicodeDecodeError) as e:r['protocol_error']=str(e)
    for epoch in range(2):
        for depth in range(2):
            for stage in range(4):
                name=f'e{epoch}-'+('z' if depth else 'c')+f'-s{stage}.raw'
                data=optional('xwngpu144/'+name);ref=expected(epoch,depth,stage)
                if data is not None:(art/name).write_bytes(data)
                r['files'].append(dict(name=name,sha256=None if data is None else m.sha(data),expected_sha256=m.sha(ref),**compare(data,ref)))
staged=read(out/'staged-e.json');r['changed_existing_e_files']=[p for p,record in staged['files'].items() if state['files'].get(p)!=record]
r['new_e_files']=sorted(set(state['files'])-set(staged['files']))
r['allocation_passed']=state['allocation_consistent'] and not state['errors']
# No top-overlay sectors anywhere in F: proves its entire inherited contents unchanged.
mapping=json.loads(subprocess.check_output(['qemu-img','map','--output=json',str(disk)]))
fstart,flen=m.fatx.PARTITIONS['F']
r['top_f_ranges']=[x for x in mapping if x['depth']==0 and x['start']<fstart+flen and x['start']+x['length']>fstart and (x.get('data') or x.get('zero'))]
r['entire_f_unchanged']=not r['top_f_ranges']
r['overlay_map_sha256']=m.sha(json.dumps(mapping,sort_keys=True).encode());save(out/'overlay-map.json',mapping)
r['dashboard_return']=read(out/'launch.json').get('dashboard_return') is True
r['exact_pixels_passed']=len(r['files'])==16 and all(row['matched'] for row in r['files'])
r['bootstrap_passed']=r.get('bootstrap_log')=='MOUNT_E 0 1 0\r\nCREATE_OUTPUT 1 0\r\n'
r['new_files_exact']=set(r['new_e_files'])=={'applications/xwngpu144/bootstrap.log','xwngpu144/result.log'}|{'xwngpu144/'+v['name'] for v in r['files']}
r['cold_passed']=r['bootstrap_passed'] and r['new_files_exact'] and r['protocol_passed'] and r['exact_pixels_passed'] and r['allocation_passed'] and r['entire_f_unchanged'] and not r['changed_existing_e_files'] and r['dashboard_return']
r['limits']='Native nxdk coherence baseline, not a Windows/physical or performance qualification. Lifecycle coverage is a separate gate.'
save(out/'audit.json',r)
print(json.dumps({key:r[key] for key in ['cold_passed','protocol_passed','exact_pixels_passed','allocation_passed','entire_f_unchanged','changed_existing_e_files','dashboard_return']},indent=2))
