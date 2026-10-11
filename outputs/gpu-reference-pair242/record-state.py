"""Preserve old continuation bytes; keep owned running/closed state accurate."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];phase=sys.argv[1];assert phase in ['active','closed']
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
p=ws/'outputs/engineering-notes/CONTINUATION.md';old=k/'artifacts/continuation-before242.md'
if not old.exists():old.write_bytes(p.read_bytes())
else:assert p.read_bytes().endswith(old.read_bytes())
matrix=read(k/'matrix001.json');state=read(k/'preserve001/host-state.json');build=read(k/'build004.json')
lines=['# Current:242 '+phase.upper()+' paired post-readback reference census','',
'Read outputs/gpu-reference-pair242/DESIGN.md/OWNERS.md/NEXT.md and actual',
'matrix001.json/preserve001 records. Never relaunch/recollect started cases.',
'Same immutable239 seed, unchanged native224/219/211 captured core/no null',
'bindings. Emulator-only: no physical IO or peer integration. Preserve all',
'239/240/241 evidence,physical0101/video0093,0088rollback,immutable0.1.0.',
'',
'Build004 candidate SHA'+build['executable_sha256']+'.',
'Borrowed sources restored; only nv2a.c/int.h/GL renderer changed. Preliminary',
'build001 failed strict helper review;002/003 parent-path setup failures and',
'failed host-test/header/capsule attempts preserved. No guest in those stages.',
'',
'New242 slots capture FIFO/PG before and after actual readback within one',
'closed-admission intervention. Existing227 terminal publication orders slots;',
'timeout hides them. No callback removal/GL disposal/join/native permit.',
'CPU callback queues and actual GL bindings are explicitly unobserved.',
'Shader/element/module summaries do not prove all per-object refs retired.',
'']
if phase=='active':
 assert not matrix['closed'] and not state['closed']
 lines+=['Owned matrix unified85879 ACTIVE, root controller'+str(matrix['controller_pid'])+'.',
'Case controller'+str(state['controller_pid'])+', runner'+str(state['runner_pid'])+',',
'tracer'+str(state['tracer_pid'])+', observer'+str(state['observer_pid'])+'.',
'Build unified24902/45816 and host-test76240 CLOSED. Inspect/resume owned',
'sessions; never duplicate. Single preserve001 launch accepted via sole tracer.',
'After teardown/normal restart/orderly host exit cold audit executes ONCE.',
'Then review actual raw pair and strict events, update notes/commit/push.']
else:
 assert matrix['closed'] and state['closed'] and read(k/'process-closure001.json')['closed']
 review=read(k/'review001.json');lines+=['All root242 processes CLOSED; no root guest queued. Matrix85879 CLOSED0.',
'Paired inventory scope '+str(review['paired_inventory_scope_passed'])+'; strict/ordinary/physical/native ownership',
'remain FALSE. Read REPORT.md/review001.json for actual retained refs and gates.',
'Next bounded protocol must establish asynchronous CPU hook removal and',
'display/frontend completion without holding locks needed by another actor.']
prefix=('\n'.join(lines)+'\n\n').encode('utf-8');p.write_bytes(prefix+old.read_bytes())
(k/('continuation-'+phase+'001.json')).write_text(json.dumps(dict(phase=phase,old_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),old_tail_preserved=p.read_bytes().endswith(old.read_bytes()),physical_access=False),indent=2)+'\n',encoding='utf-8')
print('242 continuation',phase)
