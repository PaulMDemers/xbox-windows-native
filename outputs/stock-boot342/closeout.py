"""Fresh post-scan readback and exact closure; never promotes a failed event gate."""
import array,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'physical001'
sys.path.insert(0,str(K.parent/'demo-audio-level256'))
from common001 import connect,get,sha,utc
sys.path.insert(0,str(K.parent/'stock-stage340'))
from completion002 import staged
read=lambda p:json.loads(p.read_text());stage=staged()
dest=K/'final-review.json';assert not dest.exists()
for p,h in read(K/'frozen002.json').items():assert sha((W/p).read_bytes())==h,p
trial=read(out/'trial.json');collection=read(out/'collection.json');audit=read(out/'audit.json')
assert trial['launch_requested'] and not trial['startup_enabled']
assert collection['completed'] and collection['startup_restored']
for phase in ['before','after']:
    scan=K.parent/'stock-scan341'/phase
    assert read(scan/'trial.json')['collected'] and read(scan/'return.json')['returned']
allocation=read(out/'allocation.json');assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
pkg=read(K.parent/'stock-physical337/package001.json')['files'];lookup={p.lower():p for p in pkg}
policy=read(W/'tools/hd-overlay-0.2.0.json')['baseline_files']
original=read(K.parent/'stock-physical337/capture001.json')['files']
def translate(p):return '/E/'+p[3:] if p.startswith('/F/') else p.replace('/XWNFBoot/','/XWNEBoot/')
startup='/E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd'
with connect() as f:
    echecks={}
    for p in policy:
        p=lookup[translate(p).lower()];echecks[p]=sha(get(f,p))==pkg[p]['sha256']
    fchecks={p:dict(bytes=len(b),sha256=sha(b))==meta for p,meta in policy.items() for b in [get(f,p)]}
    hives={}
    for n in ['system','software','sam','security','default']:
        p='/F/winnt/system32/config/'+n;hives[p]=sha(get(f,p))==original[p]['sha256']
        p='/E/winnt/system32/config/'+n;hives[p]=sha(get(f,p))==collection['files'][p]['sha256']
    normal=get(f,startup)==Path('E:/xwn337/package001'+startup).read_bytes()
assert all(echecks.values()) and all(fchecks.values()) and all(hives.values()) and normal
private={}
for p in (K/'artifacts/physical001').rglob('*'):
    if p.is_file():private[p.relative_to(K).as_posix()]=dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes()))
(out/'private-artifacts.json').write_text(json.dumps(private,indent=2)+'\n')
meta=Path('E:/xwn341/physical-after/fat-metadata.bin').read_bytes();assert sha(meta)==allocation['metadata_sha256']
fat=array.array('I');fat.frombytes(meta[4096:]);count=(10000048*512-len(meta))//16384
free=sum(fat[c]==0 for c in range(1,count+1))
r=dict(closed=True,closed_utc=utc(),launch_utc=trial['launch_utc'],dashboard_available=True,
       normal_E_startup_restored=normal,console_C_accessed=False,console_C_written=False,
       original_F_rollback_retained=True,E_protected=echecks,F_protected=fchecks,hives_readback=hives,
       staging_files=stage['files'],private_captures=len(private),allocation=allocation,
       E_free_bytes_from_cold_FAT=free*16384,E_data_clusters=count,
       mode1080i_gate_passed=audit['mode1080i_passed'],display_workload_passed=audit['display_workload_passed'],
       audio_workload_passed=audit['audio_probe_passed'] and audit['audio_state_passed'],
       integrity_passed=audit['integrity_passed'],normal_shutdown_count=audit['normal_shutdown_count'],
       stock_E_binding_persisted=audit['stock_E_binding_persisted'],
       scoped_combined_passed=audit['scoped_combined_passed'],strict_qualification_passed=audit['strict_qualification_passed'],
       warning_errors=audit['warnings_errors'],release_qualified=False,
       audit_sha256=sha((out/'audit.json').read_bytes()),source_sha256=sha(Path(__file__).read_bytes()),
       limits='One physical E boot, five drawing samples, six API audio phases. No new audibility/visual observation, stereo, speedup, full-disk content, crash-dump or release qualification. Strict/event failures retained. Tools did not access dashboard C. F received only the two owned scanner app/report directories; original F Windows stayed unchanged.')
dest.write_text(json.dumps(r,indent=2)+'\n')
(out/'closure.json').write_text(json.dumps(dict(closed=True,never_relaunch_or_recollect=True,normal_startup_restored=True,final_review_sha256=sha(dest.read_bytes())),indent=2)+'\n')
print(json.dumps({k:r[k] for k in ['closed','E_free_bytes_from_cold_FAT','mode1080i_gate_passed','audio_workload_passed','integrity_passed','scoped_combined_passed','strict_qualification_passed','normal_shutdown_count']},indent=2))
