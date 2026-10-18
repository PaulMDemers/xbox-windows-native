# SPDX-License-Identifier: MIT
"""One bounded native lossless-compression operation on the reviewed exact list."""
import datetime,json,shutil,subprocess,traceback
from pathlib import Path
from common002 import K,COMPACT,MINIMUM,PROJECTED,sha,js,volume,processes,metadata,validate_path
OUT=K/'apply002.json';assert not OUT.exists()
plan=js(K/'plan002.json');assert plan['passed']
r=dict(passed=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),attempted=False,physical_access=False,deleted_files=[],moved_files=[],modified_content_files=[],after=[],plan_sha256=sha(K/'plan002.json'),source_sha256=sha(Path(__file__)))
def save():OUT.write_bytes((json.dumps(r,indent=2)+'\n').encode())
save()
try:
    assert volume()==plan['volume'];r['processes']=processes()
    assert sha(COMPACT)==plan['compact_sha256']
    for n,h in {**plan['records'],**plan['sources']}.items():assert sha(Path(n))==h,n
    for row in plan['files']:
        p=validate_path(Path(row['path']),row['case']);assert metadata(p)==row['metadata'],str(p)
    r['free_before']={d:shutil.disk_usage(d+':/').free for d in ['C','E']}
    r['guard_before']=r['free_before']['C']-PROJECTED>=MINIMUM
    r['operational_target_before']=r['free_before']['C']-PROJECTED-MINIMUM>=512*1024**2
    if r['operational_target_before']:
        r['skipped']='existing guard plus512MiB operational headroom already passes; no storage mutation needed'
    else:
        r.update(attempted=True,command=[str(COMPACT),'/C','/I','/Q',*[v['path'] for v in plan['files']]],timeout_seconds=120);save()
        p=subprocess.run(r['command'],capture_output=True,text=True,timeout=120,check=False)
        r.update(tool_exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr);save()
        assert p.returncode==0,'native compressor returned failure'
    r['tool_completed']=True
except Exception:r['failure']=traceback.format_exc()
finally:
    # Preserve exact readback even when the native process partially fails.
    for row in plan['files']:
        a=dict(path=row['path'],verified=False)
        try:
            p=validate_path(Path(row['path']),row['case']);m=metadata(p);a['metadata']=m
            for key in ['bytes','sha256','file_id','device','links']:assert m[key]==row['metadata'][key],(str(p),key)
            if r['attempted'] and r.get('tool_exit_code')==0:assert m['attributes']&0x800,str(p)
            elif not r['attempted']:assert m==row['metadata']
            a['verified']=True
        except Exception:a['failure']=traceback.format_exc()
        r['after'].append(a);save()
    r['free_after']={d:shutil.disk_usage(d+':/').free for d in ['C','E']}
    r['guard_after']=r['free_after']['C']-PROJECTED>=MINIMUM
    r['logical_bytes']=sum(v['metadata']['bytes'] for v in plan['files'])
    r['allocated_before']=sum(v['metadata']['allocated_bytes'] for v in plan['files'])
    if all(v['verified'] for v in r['after']):
        r['allocated_after']=sum(v['metadata']['allocated_bytes'] for v in r['after']);r['allocated_bytes_recovered']=r['allocated_before']-r['allocated_after']
    r['passed']=bool(r.get('tool_completed') and 'failure' not in r and all(v['verified'] for v in r['after']))
    r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
    print(json.dumps({n:r[n] for n in ['passed','attempted','failure','tool_exit_code','allocated_bytes_recovered','guard_after'] if n in r}))
if not r['passed']:raise SystemExit(1)
