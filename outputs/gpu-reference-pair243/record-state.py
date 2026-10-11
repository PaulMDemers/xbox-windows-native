"""Replace242 active prefix while retaining exact original2971fb5 tail."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];phase=sys.argv[1];assert phase in ['active','closed']
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));old=k.parent/'gpu-reference-pair242/artifacts/continuation-before242.md';p=ws/'outputs/engineering-notes/CONTINUATION.md'
assert p.read_bytes().endswith(old.read_bytes())
m=read(k/'matrix001.json');h=read(k/'preserve001/host-state.json');build=read(k/'build004.json')
lines=['# Current:243 '+phase.upper()+'; paired readback/reference census','',
'Read outputs/gpu-reference-pair243/DESIGN.md/NEXT.md/OWNERS.md and actual',
'matrix001.json/preserve001 records;242 failure and source ownership report',
'remain separate. Never replay/recollect started/closed cases. Same immutable239',
'seed/native224/219/211 captured core, no synthetic null bindings. Emulator-only,',
'no physical IO/peer integration. Preserve0101/video0093,0088rollback,0.1.0.',
'',
'Actual unchanged242/build004 binary '+build['executable_sha256']+'.',
'Build sources restored.242 preliminary strict-helper/header/setup failures',
'preserved;242 actual paired readback terminal3, then host verifier failed',
'because it treated enabled maskFFFFFFFF as pending work.242 CLOSED1, cold/CPU',
'scope PASS, trace/overall failure preserved, no retroqualification.243 NEW',
'runtime fixes only host field classification: pending/waits/work0, enabled',
'must match pre-observed field5; no emulator/native driver rebuild/change.',
'']
if phase=='active':
 assert not m['closed'] and not h['closed']
 lines+=['Matrix unified60522 ACTIVE; root PID'+str(m['controller_pid'])+', case'+str(h['controller_pid'])+'.',
'Runner'+str(h['runner_pid'])+', tracer'+str(h['tracer_pid'])+', observer'+str(h['observer_pid'])+'.',
'243 trace completed both actual loader pins, paired census and full teardown;',
'normal workload/return/cold audit pending. Inspect/resume, never duplicate.',
'242 matrix85879 and builds24902/45816 CLOSED. After closure review/capture',
'process identities and reports, repository-check/commit/push reviewed text.']
else:
 assert m['closed'] and h['closed'] and read(k/'process-closure001.json')['closed']
 r=read(k/'review001.json');assert r['paired_inventory_scope_passed']
 lines+=['ALL root242/243 processes CLOSED; no root guest queued. Matrix60522 CLOSED0.',
'Actual243 paired census PASS: admission1 in both FIFO/PG intervals,3 dirty',
'surfaces ->0dirty,3callbacks retained,4texture units/24cache entries retained,',
'53shader entries/53save handles/53modules/93element entries retained; display',
'objects unchanged. Save handles NOT thread-liveness proof.3072000 actual GL',
'bytes compared, existing same-conversion oracle. No RAM captures. Both actual',
'Xromwell11100/FreeLoader200a20 pins/full teardown/resume. Both242/243 normal',
'restart/dashboard/orderly exit0/CPU workload/cold allocation5hives/protected',
'PASS; soleFtdisk49 strictFALSE, no application delta. Ordinary/physical/native',
'GPU ownership FALSE. CPU queues/actualGLbindings/per-object completion unknown.',
'',
'Next bounded protocol must prove async CPU callback removal and frontend/display',
'ownership/completion. Do not join/wait holding actors required locks; do not',
'dispose dirty data, treat save handles as live threads or grant native ownership',
'from this census. Read ownership source evidence before new diagnostic.',
'Closed240/241/242 portable copies moved to E with readback hashes/original',
'junction paths; no disk backing chains moved. C near20GiB guard: inspect/project',
'capacity before further builds or instances. No hardware test prepared here.']
prefix=('\n'.join(lines)+'\n\n').encode('utf-8');p.write_bytes(prefix+old.read_bytes())
(k/('continuation-'+phase+'001.json')).write_text(json.dumps(dict(phase=phase,old_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),old_tail_preserved=p.read_bytes().endswith(old.read_bytes()),physical_access=False),indent=2)+'\n',encoding='utf-8')
print('243 continuation',phase)
