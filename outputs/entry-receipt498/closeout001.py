"""Read back all executed host inputs/results; no console access."""
import datetime,hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;R=K.parent.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def local(s):return Path(s.replace('/mnt/c/','C:/',1))
r=json.loads((K/'host001.json').read_text(encoding='utf-8'))
assert r['passed'] and r['closed'] and r['case_count']==199
assert all(sha(local(p))==v['sha256'] for p,v in r['files'].items())
assert all(sha(K/n)==v for n,v in r['source_pins'].items())
original=Path('C:/xwn497/build002/xbeboot.S')
assert sha(original)=='1b2467cf01bfc5525cab554e704f425f7ad375056fbc3a810cf428f4898a07a9'
assert sha(Path('C:/xwn497/build002/default.xbe'))=='09e3043c10837f20a3aef7d2b94ac54145b047ff9fafe02fb111fd25425b9274'
gate=(K/'entry.S').read_text(encoding='utf-8');asm=gate.split('.data')[0]
assert 'pushfd\n    pushad\n    cld' in asm and 'popad\n    popfd\n    jmp entry498_continue' in asm
assert 'mov dword ptr [entry498_close_attempted], 1\n    push' in asm
assert not any(x in asm for x in [' cli',' sti','mov cr','lgdt','lidt','wrmsr','out dx','in al'])
result=dict(passed=True,finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 host_only=True,actual_assembly_cases=199,transport_mutations=1019,
 private_files_rehashed=len(r['files']),source_inputs_exact=True,
 original497_source_binary_unchanged=True,new_xbe_built=False,physical_access=False,
 pending_user_screen_observation=True,console_last_observed='dashboard in closed497',
 temporary_hook=False,queued_launch=False,all_owned_processes_closed=True,
 limitations=['NT filesystem and firmware functions modeled','Linux ring3 CPU, not actual Xbox context','Postbuild host tool hashes, no full prebuild closure','Absent file does not prove absent entry','Complete file does not prove final flush/close or Windows boot'])
assert not (K/'final-review.json').exists()
(K/'final-review.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
note='''# 498 host entry gate complete; 497 remains closed awaiting screen observation

497 PUSHED8935db5a. Read entry-receipt498 REPORT/DESIGN/NEXT/final-review.
199 actual Linux i386 assembly cases pass (128 register/flag,71 modeled I/O failure),
1019 independent transport negatives.606 private files rehashed, all processes closed.
No XBE integration/build, console access, hook or queued launch. Exact497 source/
binary untouched; no requalification. Pending user screen question still unanswered.
Complete entry receipt does NOT prove final flush/close/Windows; missing stays
ambiguous. Early I/O changes timing/memory and is only a diagnostic intervention.
Next NEW pinned integration/appended gate preserving original instructions and
controller host checks before a distinct physical run; no identical retry.
496 PC combined-scene PASS unchanged; Xbox scene still unqualified.720p/C protected.
HostC~23.08GB/E21499871232B; projected20GiB guard. Deadline14UTC/closeout13:50.
498 repository check and commit/push next. No hardware observation invented.

'''
for name in ['CONTINUATION.md','STATUS.md']:
 p=R/'outputs/engineering-notes'/name;p.write_bytes(note.encode()+p.read_bytes())
print(json.dumps(result))
