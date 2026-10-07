"""Verify immutable interrupted-run evidence without waiving ordinary gates."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['001','002','003']
out=k/case;read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
t=read(out/'trace.json');a=read(out/'interruption-audit.json')
source=out/'trace-source.py' if (out/'trace-source.py').exists() else k/'trace.py'
assert sha(source.read_bytes())==t['source_sha256']
assert sha((k/'sites.json').read_bytes())==t['sites_sha256']
assert sha((out/'trace.json').read_bytes())==a['trace_sha256']
assert a['ordinary_qualified'] is False and a['physical_qualified'] is False and a['physical_access'] is False
assert t['ended_utc']
if a['checkpoint_reached']:
    assert a['trace_guards_passed'] and t['guest_resumed'] is False and t['guest_held_stopped'] is True
else:
    assert not a['trace_guards_passed'] and not a['split_reproduced']
    assert t['status']=='capture_incomplete' and t['guest_resumed'] is True
    recovery=read(out/'trace-recovery.json')
    assert sha((out/'trace-last-published.json').read_bytes())==recovery['original_trace_sha256']
    assert sha((out/'trace-final-recovered.json').read_bytes())==recovery['final_trace_sha256']==sha((out/'trace.json').read_bytes())
assert not t['armed_breakpoints_remaining'] and not t['pending_write_count'] and not t['pending_cache_count']
run=ws/('work/runs/nt5-fatx-interrupted-append-'+case);assert (run/'cleanup.json').exists()
exit_record=read(out/'exit-observation.json')
assert sha((out/'exit-observation.json').read_bytes())==a['exit_observation_sha256']
assert sha((run/'cleanup.json').read_bytes())==exit_record['cleanup_sha256'] and exit_record['owned_pid_absent']
if t.get('atomic_json_source_sha256'):
    assert sha((k/'atomic_json.py').read_bytes())==t['atomic_json_source_sha256']
count=0
for e in t['events']:
    if e.get('buffer_file'):
        data=(out/'artifacts'/e['buffer_file']).read_bytes();assert sha(data)==e['buffer_sha256'] and len(data)==e['length'];count+=1
raw=(out/'artifacts/after-target-raw.bin').read_bytes();prior=(out/'artifacts/before-target-raw.bin').read_bytes()
assert sha(raw)==a['target']['after_raw_sha256'] and sha(prior)==a['target']['before_raw_sha256']
cold=(out/'artifacts/after-setupapi.log').read_bytes();assert sha(cold)==a['target']['cold_log_sha256']
assert (cold[a['target']['logical_offset']:a['target']['logical_offset']+220]==raw)==a['target']['file_and_raw_agree']
for h in a['hives']:assert sha((out/'artifacts'/('after-'+h['name'])).read_bytes())==h['sha256']
v=read(out/'allocation.json')
assert sha((out/'artifacts/fat-metadata.bin').read_bytes())==v['metadata_sha256']
assert sha((out/'artifacts/directories.bin').read_bytes())==v['directory_records_sha256']
files=subprocess.check_output(['git','ls-files','--','outputs/fatx-interrupted-append'],cwd=ws,text=True).splitlines()
for name in files:
    staged=subprocess.check_output(['git','show',':'+name],cwd=ws)
    assert staged==(ws/name).read_bytes(), 'Staged bytes differ: '+name
print(json.dumps(dict(source_buffers_verified=count,staged_files_verified=len(files),split_reproduced=a['split_reproduced'],ordinary_qualified=False)))
