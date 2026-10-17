"""Close the existing diagnostic with hash/read-only process verification."""
import ast,datetime,hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'final-review.json';assert not out.exists()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for data in iter(lambda:f.read(1048576),b''):h.update(data)
    return h.hexdigest()
load=lambda p:json.loads(p.read_text())
frozen=load(K/'emu001/frozen.json')
for p,h in frozen.items():assert sha(W/p)==h,p
for p in K.glob('*.py'):ast.parse(p.read_text())
source=(K/'probe.c').read_text();a=source.index('/* Diagnostic checkpoint only:');b=source.index('void WINAPI mainCRTStartup',a)
source=source[:a]+source[b:];source=source.replace('    trace_init425();\n','')
source=source.replace('    xwn_checkpoint425(1);names();xwn_checkpoint425(2);rsa(FALSE);xwn_checkpoint425(3);rsa(TRUE);xwn_checkpoint425(4);dpapi(FALSE);xwn_checkpoint425(5);dpapi(TRUE);xwn_checkpoint425(6);','    names();rsa(FALSE);rsa(TRUE);dpapi(FALSE);dpapi(TRUE);')
assert source.replace('\n\nvoid WINAPI mainCRTStartup','\nvoid WINAPI mainCRTStartup')==(W/'outputs/crypto-persistence423/probe.c').read_text()
a=load(K/'emu001/audit.json');trace=load(K/'emu001/trace.json');proof=load(K/'trace-verification001.json')
assert proof['passed'] and sha(K/'emu001/trace.json')==proof['trace_sha256']
assert trace['status']=='all_checkpoints_complete' and not trace['armed_remaining'] and trace['guest_resumed']
assert a['host_exit']['passed'] and a['host_exit']['exit_code']==0 and not a['host_exit']['fallback_kill'] and not a['host_exit']['timeout']
assert a['normal_shutdown_delta']==1 and a['event_history'] and a['allocation']['allocation_consistent']
assert not a['allocation']['errors'] and a['allocation']['orphan_cluster_count']==0
assert len(a['hives'])==5 and all(h['clean'] and h['independent_raw_values_agree'] for h in a['hives'])
assert a['protected_os_exact'] and a['staged_exact'] and a['source_unchanged'] and a['audit_unchanged']
assert a['probe']['api_errors']==[['rsa_user.acquire',206],['rsa_machine.acquire',0x80090020],['dpapi_user.protect',206]]
assembly=load(K/'assembly001.json');run=Path('E:/xwn425/runs/nt5-crypto425-emu001')
paths={run/'hdd.qcow2':a['disk_sha256'],Path(assembly['fixture_path_windows']):assembly['fixture_sha256'],Path(assembly['source'].replace('/mnt/e/','E:/')):assembly['source_sha256']}
build=load(K/'build002.json')
for row in build['rows']:paths[Path(row['path'].replace('/mnt/e/','E:/'))]=row['sha256']
for p,h in paths.items():assert sha(p)==h,str(p)
captures={str(p):sha(p) for p in run.iterdir() if p.suffix in ['.png','.json','.raw']}
host=load(K/'host-closeout001.json');assert host['xemu_count']==0
linux=json.loads(subprocess.check_output(['wsl','-d','Ubuntu','--','python3','-c',"import json;from pathlib import Path;print(json.dumps([{'pid':int(p.name),'name':(p/'comm').read_text().strip()} for p in Path('/proc').iterdir() if p.name.isdigit() and (p/'comm').exists() and (p/'comm').read_text().strip().startswith(('qemu-system','qemu-nbd','nbdfuse'))]))"]).decode());assert not linux,linux
r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'diagnostic_completed':True,'ordinary_qualified':False,'strict_qualification':False,
   'frozen_inputs_exact':len(frozen),'original_probe_operation_text_reconstructed':True,'trace_events':proof['events'],'checkpoints':proof['checkpoints'],
   'actual_mutations_rejected':proof['actual_mutations_rejected'],'synthetic_checks':load(K/'parser-tests001.json')['checks'],
   'normal_shutdown_delta':a['normal_shutdown_delta'],'allocation':a['allocation'],'protected_windows_binaries_exact':a['protected_os_files'],
   'source_fixture_binary_hashes':{str(p):h for p,h in paths.items()},'private_capture_hashes':captures,'host_exit':a['host_exit'],
   'all_owned_processes_closed':True,'linux_qemu_nbd_fuse':linux,'host_closeout_sha256':sha(K/'host-closeout001.json'),
   'evidence_hashes':{n:sha(K/n) for n in ['REPORT.md','DESIGN.md','NEXT.md','emu001/audit.json','emu001/trace.json','trace-verification001.json','source-closure001.json']},
   'physical_access':False,'functional_driver_patch':False,'limitations':['No internal FATX instruction breakpoint','No RPC call-ID/impersonation trace','Strict inherited event failures retained','No long-name storage implementation']}
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'closed':True,'frozen':len(frozen),'trace_pairs':proof['paired'],'negative_controls':proof['actual_mutations_rejected']}))
