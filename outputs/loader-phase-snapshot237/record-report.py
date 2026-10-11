"""Generate phase matrix report only after reviewed closure."""
import json
from pathlib import Path
k=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text());review=read(k/'review001.json');assert review['passed']
assert not (k/'REPORT.md').exists()
lines=['#237 independent GPU snapshots at loader boundaries','',
 'Three independent debugger runs used one fresh immutable seed and three unique writable copies. Unchanged234 emulator and224/219/211 native fixture. No physical access, driver changes, device integration or release tag changes. CPU-stopped PG worker observations; no ordinary accelerated-driver qualification.','',
 '| Independent case | CPU phase EIP | Snapshot | Pending | Wait flags | Trace / CPU / cold integrity |','|---|---:|---|---:|---|---|']
for row in review['cases']:
 s=row['snapshot'];pc=s.get('cpu_eip');pending=s.get('pending');flags=', '.join(s.get('wait_labels',[])) or 'none'
 lines.append(f"| {row['case']} | {hex(pc) if pc is not None else 'unknown'} | state{s.get('terminal_state')} | {hex(pending) if pending is not None else 'unknown'} | {flags} | {row['trace_passed']} / {row['cpu_scope_passed']} / {row['integrity_passed']} |")
lines+=['',
 'Each loader stop matched owned cold executable bytes. Xromwell entry11100 and FreeLoader multiboot200a20 are actual executing stops; magic2badb002/IF0 at FreeLoader. Dashboard is arbitrary CPU stop, unlike prior mid-IRQ acknowledgement. These are independent boots, not a simultaneous single-boot timeline.','',
 'Published tuples reread byte-identically. Current PG row FIFO-valid0: historical valid journal rows do not establish current DMA GET/PUT. Worker can progress while CPU stopped. Compiled wait bits1FIFO access disabled,2NOP,4flip,8context switch. No flag silently cleared.','']
for row in review['cases']:
 s=row['snapshot'];h=s.get('header',{});a=row['allocation']
 lines.append(f"{row['case']}: publication passed{s['passed']}; journal total{h.get('total')}/count{h.get('count')}/overwritten{h.get('overwritten')}, lost prefix retained. Normal shutdown{row['normal_shutdown_count']}/dashboard{row['dashboard_return']}; allocation{a}; five structural hives. Warning/error deltas{row['warnings_errors']}. Strict/ordinary/physical GPU qualification FALSE.")
lines+=['',
 'Unchanged CPU regression requires65 allocations/releases/exposure refusals,3194880 verified bytes/four joined workers; actual per-case results are shown above. Eight MMIO retirement rounds/128 sequential reads are required to refuse UNMODELED_BUSY/NO_OWNERSHIP. No renderer-reference retirement, dirty-surface readback, alias coherence, instance allocation or native permit proven.','',
 'Host tests57 actual sampler/parser checks,72 helper guards,12 actual supervisor connection checks; PowerShell syntax/prelaunch review passed. Initial parser rejected producer kind1, caught on preserved236 raw evidence before launch and retained in parser-preliminary001-failure.json; corrected using actual journal-kind evidence. No guest replay.','',
 f"All{review['frozen_pins_unchanged']} frozen pins unchanged. Actual resident pins/raw immutable tuples reviewed; breakpoint removals/mode0/resume/closure recorded. Every new runtime cold-audited exactly once.",'',
 'Closure caveat: inherited host runner uses vm.Kill after capture. Cold evidence is recovered-image allocation/hives/selected-content scope, not all-file-content durability, completed emulator cache flush or repeated boots. USB peer cda0476 isolated forced-exit mapping loss versus orderly closure on its own fixture; no silent closure change in this frozen matrix. Physical0101/video0093,0088rollback,immutable0.1.0 untouched.','',
 'Read review001.json/prelaunch-review001.json/matrix001.json and each trace.json/audit.json/closure.json plus DESIGN.md for actual scope.']
if all(row['snapshot'].get('pending')==0 and row['snapshot'].get('wait_mask')==0 for row in review['cases'][1:]):
 lines+=['','Both executing loader-entry samples have no pending PGRAPH interrupt and no wait flags. This does not support diagnosing a persistent PGRAPH wait at those sampled transfers from the earlier dashboard stop. It does not establish FIFO drain, producer admission close, renderer-reference retirement or complete GPU idle. The next discriminator is current FIFO and referenced context/surface lifetime, not forced wait clearing.']
(k/'REPORT.md').write_text('\n'.join(lines)+'\n')
(k/'NEXT.md').write_text("""#237 CLOSED; next discriminator

Never relaunch/recollect dashboard001/xbe001/freeldr001 or235/236. Read REPORT.md/review001.json and actual records. Verify all root PIDs absent and leases released before new launch.

Use actual phase matrix to locate the real dashboard/loader producer-admission close; distinguish CPU-stop-induced NOP from remaining producer/reference. Current234 PG-only tuples do not expose current DMA pointers or dirty/context references. Any NEW finite observer retains lock-safe validity, timeout/immutability and exact compiled/runtime pins. No force-clear, speculative patch, unsafe guest MMIO debugger reads, reference disposal or native ownership grant.

Before claiming further cold images durable/repeated-boot qualified, separately review/test bounded orderly closure against USB peer cda0476. Never alter closure of an already frozen run or erase recovered-image limitations. Pending setup/restart/storage failures remain separate peer evidence.

Preserve physical0101/video0093,0088rollback,immutable0.1.0/all failures. No peer integration/release/physical deployment without review/qualification. Serial owned fixtures, fresh IDs, source/binary/seed pins,20GiB guard, full debugger teardown/cold/events. Strict Ftdisk49 remains failure; no suppression/waiver.
""")
print('237 reviewed report saved')
