"""Resume cold collection safely and summarize the paired recorder experiment."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text())

def collect(case):
    run=ws/('work/runs/nt5-native-event-recorder-'+case)
    assert (run/'cleanup.json').exists(), 'Cold collection requires owned cleanup'
    out=k/case
    manifest=out/'collection.json'
    r=read(manifest) if manifest.exists() else dict(case=case,physical_access=False,stages={})
    stages=[('audit','audit.py','audit.json'),('package','audit-package.py','package-audit.json'),
            ('allocation','audit-allocation.py','allocation.json')]
    for name,script,output in stages:
        target=out/output
        if target.exists():
            # Existing evidence is never rerun by the collector; parse it or stop.
            read(target)
            r['stages'].setdefault(name,dict(adopted_existing=True,output=output))
        else:
            script_path=(k/script).resolve()
            if sys.platform=='win32':
                posix='/mnt/'+script_path.drive[0].lower()+script_path.as_posix()[2:]
                cmd=['wsl','-d','Ubuntu','--','env',
                     'LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu',
                     'python3',posix,case]
            else:cmd=[sys.executable,str(script_path),case]
            subprocess.run(cmd,check=True)
            read(target)
            r['stages'][name]=dict(output=output,completed=True)
        r['stages'][name]['sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
        manifest.write_text(json.dumps(r,indent=2)+'\n')
    if case!='001':
        subprocess.run([sys.executable,str(k/'decode.py'),str(out/'events.bin'),str(out/'events.json')],check=True)
    print('Cold collection complete for '+case)

def compare():
    rows=[]
    for case in ['001','002']:
        f=read(k/('fixture-'+case+'.json'));a=read(k/case/'audit.json')
        p=read(k/case/'package-audit.json');alloc=read(k/case/'allocation.json')
        launch=read(k/case/'launch.json');host=read(k/case/'host-config.json')
        rows.append(dict(case=case,role=f['role'],seed_sha256=f['seed_sha256'],
            emulator_sha256=host['emulator_sha256'],recorder_enabled=host['recorder_enabled'],
            idle_ms=a['idle_elapsed_ms'],popup_records=a['popup_records'],unexpected_errors=a['unexpected_errors'],
            normal_shutdown_count=a['normal_shutdown_count'],dashboard_return=a['dashboard_return'],
            installation_checks_passed=p['installation_checks_passed'],diagnostic_checks_passed=a['diagnostic_checks_passed'],
            ordinary_run_valid=a['ordinary_run_valid'],allocation_consistent=alloc['allocation_consistent'],
            orphan_clusters=alloc['orphan_cluster_count'],files=alloc['files'],directories=alloc['directories'],
            runtime_hashes_match=all(v['matched'] for v in a['runtime_binary_checks']),
            payload_hashes_match=all(v['matched'] for v in a['payloads']),
            structural_hives=len(a['hives']),launch=launch['cycles']))
    assert rows[0]['seed_sha256']==rows[1]['seed_sha256']
    assert rows[0]['emulator_sha256']==rows[1]['emulator_sha256']
    events=read(k/'002/events.json')
    r=dict(scope=__doc__,physical_access=False,hardware_qualified=False,cases=rows,
           trace_records=events['record_count'],invalid_site_records=events['invalid_site_records'],
           kernel_shutdown_observed=events['kernel_shutdown_observed'],
           limits='One matched pair cannot quantify recorder overhead or establish a fix; no debugger attachment or paused capture in either run.')
    (k/'comparison.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['collect','compare']);p.add_argument('case',nargs='?',choices=['001','002','003','004','005'])
    a=p.parse_args()
    if a.action=='collect':
        assert a.case;collect(a.case)
    else:compare()
