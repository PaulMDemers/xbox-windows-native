"""Closed241 report and exact continuation, preserving original history bytes."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'report-review001.json';assert not dest.exists() and not (k/'REPORT.md').exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
review=read(k/'review001.json');assert review['passed'] and review['backend_preservation_scope_passed'] and not review['strict_qualified']
assert read(k/'process-closure001.json')['closed'] and read(k/'process-closure001.json')['no_root_guest_queued']
build=read(k/'build001.json');assert build['passed'] and build['borrowed_sources_restored'] and build['changed_sources']==['hw/xbox/nv2a/pfifo.c']
rows=review['cases'];assert len(rows)==2 and all(v['cold_integrity_passed'] and v['normal_shutdown_count']==1 for v in rows)
candidate=rows[1];assert candidate['worker_preservation_scope_passed'] and sum(v['bytes'] for v in candidate['ram'])==3072000
delta=read(k/'directory-delta001.json');assert delta['passed'] and not delta['control_only'] and not delta['candidate_only']
tests=read(k/'consume-test001.json');assert tests['passed'] and len(tests['runs'])==2 and all(v['exit_code']==0 and not v['stderr'] for v in tests['runs'])
table='\n'.join('| '+v['case']+' | '+str(v['allocation']['files'])+' | '+str(v['allocation']['directories'])+' | '+str(v['allocation']['directory_clusters'])+' | '+str(v['allocation']['orphan_cluster_count'])+' |' for v in rows)
ram='\n'.join(f"- Physical RAM {v['address']:#x}, {v['bytes']} bytes: `{v['sha256']}`." for v in candidate['ram'])
text=f'''#241 Xromwell dirty-pixel preservation succeeded; ownership still unproved

The concrete failure in CLOSED240 was a disabled-pusher refusal before its empty-queue check: state4/reason21/consume_stop5, GET=PUT=0/parser0/waits0, no commands or readback. New241 changes only the diagnostic consume function in pfifo.c. A live unexpired request with no waits and an empty completed parser skips pusher invocation; outstanding work, parser errors and waits retain existing bounded paths. No pusher enabling, register/wait clearing, fake completion, reference disposal or native-driver change.

Build001 reconstructed the exact238 source under the build lease, changed only pfifo.c and restored all borrowed source bytes. Toolchain is the unchanged pinned gcc image. Actual candidate executable `{build['executable_sha256']}`, {build['executable_bytes']} bytes; source manifest `{build['source_manifest_sha256']}`. Compiled artifacts were created on E and exposed through the original workspace junction, with no disk backing chain move.

Fresh241/preserve001 paired with CLOSED239/control001 on the exact SAME verified immutable239 seed, native224/219 payload and211 captured-core device policy. No synthetic null binding or physical access. Both pin executing Xromwell11100 and FreeLoader200a20, with exact32-byte resident matches; FreeLoader magic2badb002/IF0. Each removes both breakpoints, verifies virtual mode0 and resumes. No debugger register/memory-write packets or native GPU commands.

At pinned Xromwell, each passive238 snapshot observed three dirty non-overlapping surfaces3072000 bytes, empty FIFO/parser, no waits/frontend batches/framebuffer/flush/sync work. FIFO and PG observations have distinct times, not simultaneous locks. In241 the actual preservation setter closes producer admission; its worker rechecks under FIFO/renderer/PG lock ownership, fences and downloads real GL pixels, compares every byte of all three expected buffers against VRAM and fences again. Immutable terminal3 reports surfaces3/dirty3/downloaded3/bytes3072000/error0/reason0/old_halt0/consume_stop0/steps0/words0/waits0. Request/gate vectors match; no FIFO commands consumed. This qualifies the bounded debugger preservation scope, not native ownership or hardware acceleration.

Primary qmp_pmemsave -> cpu_physical_memory_read -> flatview_read_continue invokes GPU read callbacks. No control/before RAM capture was performed. Only after worker success were these three exact post-preservation RAM buffers captured and privately retained:

{ram}

These callback-bearing RAM captures do not independently prove GPU pixels. The compiled worker's actual full byte comparisons supply that scope. Its expected buffers preserve existing padding bytes as well as the downloaded pixels. Existing finish restores previous producer admission on success. Bindings/callbacks/textures are retained by the reviewed implementation; complete post-preservation runtime reference inventory and retirement remain unproved. `references_retired=0/native_grant=0` are contract fields, not a new comprehensive runtime inventory. See RETIREMENT.md for the next separate gate.

Both runs completed65 CPU allocations/releases/exposure refusals,3194880 verified bytes and four joins. Eight retirement rounds/128 sequential MMIO reads correctly retain UNMODELED_BUSY/NO_OWNERSHIP. One normal EventLog6006 shutdown/dashboard return and orderly host stop/quit/exit0, no Kill fallback. Complete allocation, five structural hives, protected/staged hashes, startup/device policy/SetupAPI and event history passed:

| Case | Files | Directories | Directory clusters | Orphans |
| --- | ---: | ---: | ---: | ---: |
{table}

Existing directory captures show identical control/candidate paths and no baseline path missing. This is selected-content/full-allocation scope, not all-file or power-loss/repeated-boot durability. Application event deltas empty; sole Ftdisk49 type1 remains a strict failure in both. Overall strict/ordinary/physical/native GPU ownership remain FALSE; no gate waived and no physical baseline changed.

Actual compiled consume/wait functions tested at O0/O2 with real QEMU atomics and ASan/UBSan:18432 cases/110593 checks per build, zero sanitizer stderr/leaks. Cases cover empty parked queues, outstanding methods/errors/work, all wait masks, request states, deadline boundary and delegation under explicit clock/FIFO/pusher adapters. These models are not GPU scheduling/readback proof. Actual host experiment/parser62, guard72, single-connection12 and bounded closure25 checks PASS.661 frozen inputs unchanged. Runtime records are reviewed in review001.json; all239/240/241 root identities are closed, no root guest queued.

Preserve239 successful control, pre-VM capacity refusal and all host setup guards; preserve240 accepted safe refusal/normal cold recovery, without retry/recollection. Success reviewers authored for failed earlier cases were not executed on them; actual failure review scripts retain negative gates. Generic inherited helper print labels239/238 and protocol232 remain historical names: actual case paths, compiled sources/binary pins and runtime records identify241. Closed build/portable offloads were hash/readback verified and original paths preserved; physical0101/video0093,0088rollback,immutable0.1.0 and peer branches unchanged.

Next: new bounded SAME-intervention post-preservation reference inventory with producer admission still closed, then actual retirement/completion proof including asynchronous CPU callbacks and display/texture/shader references. Only then consider native ownership and accelerated fills/blits, followed by a separate hardware comparison with rollback. No root process remains running.
'''
(k/'REPORT.md').write_text(text,encoding='utf-8')
note=ws/'outputs/engineering-notes/CONTINUATION.md';previous=note.read_bytes();(k/'artifacts/continuation-active-before241.bin').write_bytes(previous)
old=(k.parent/'gpu-preserve-entry239/artifacts/continuation-before239.bin').read_bytes();assert previous.endswith(old)
prefix=f'''# Current:241 CLOSED; all3 dirty surfaces preserved at Xromwell entry

Read outputs/gpu-preserve-empty241/REPORT.md/DESIGN.md/RETIREMENT.md/NEXT.md,
review001.json/process-closure001.json and actual stage records. Matrix51665
CLOSED0 at{read(k/'matrix001.json')['finished_utc']}. Build24380 CLOSED0,
borrowed sources restored; only pfifo.c changed. Candidate SHA{build['executable_sha256']}.
All239/240/241 root process identities closed, no root guest queued.

Actual241 terminal3:3 dirty/3 downloaded/3072000 full bytes compared by actual
GL worker with fences, no errors, no FIFO steps/words consumed. Exact actual
Xromwell11100/FreeLoader200a20 pins; full teardown/mode0/resumed. Post-success
RAM buffers privately retained/hashes in REPORT. No before/control RAM capture:
pmemsave invokes GPU read callbacks, not passive observation. Finish restores
old producer admission; references retained, retirement/native ownership NOT
proved. Next NEW bounded post-preservation inventory within SAME intervention
and admission still closed; account for asynchronous CPU callback removal and
texture/shader/display refs before any native grant/accelerated allocator.

Matched CLOSED239/control001 exact SAME immutable239 seed/native224/219/211
captured-core policy/no null bindings. Both65 allocations/releases/refusals,
3194880 bytes/four joins, normal6006=1/dashboard/orderly hostexit0/no Kill,
clean full allocation/five hives/protected/startup/policy/history. Paths match.
Sole Ftdisk49 type1 remains strict FALSE; no application events. Debugger
preservation scope TRUE, ordinary/physical/native ownership FALSE.

661 frozen pins; compiled O0/O2 ASan/UBSan18432 cases110593 checks each,
host62/guards72/connection12/closure25 PASS. Preserve239 pre-VM space refusal
and240 safe state4/reason21/stop5 inactive pusher refusal with zero readback;
never replay/recollect any cases. Diagnostic correction skips only live,
unexpired/no-wait empty completed parser under actual FIFO/halted admission;
all other bounded worker/fence/byte-comparison/refusal gates unchanged.
No physical IO/peer integration. Preserve0101/video0093,0088rollback,
immutable0.1.0/all failures. E compiled241 and closed build/portable offloads
readback/hash verified with original paths; no disk backing chains moved.
C near20GiB guard again: inspect/project capacity before more work.

'''.encode('utf-8')
note.write_bytes(prefix+old);assert note.read_bytes().endswith(old)
for p in k.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
dest.write_text(json.dumps(dict(passed=True,report_sha256=sha(k/'REPORT.md'),old_tail_preserved=True,old_tail_sha256=hashlib.sha256(old).hexdigest(),continuation_sha256=sha(note),physical_access=False),indent=2)+'\n',encoding='utf-8')
print('241 closed report and continuation recorded')
