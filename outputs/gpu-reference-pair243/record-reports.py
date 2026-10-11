"""Reports from closed reviewed evidence; no launches/collections/repair."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'gpu-reference-pair242';read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=read(k/'review001.json');bad=read(old/'review001.json');assert r['paired_inventory_scope_passed'] and not bad['paired_inventory_scope_passed']
d=read(k/'directory-delta001.json');assert d['passed'] and not any(v['absent'] for v in d['cases'])
build=read(old/'build004.json');a=read(k/'preserve001/audit.json');m=r['matrix'];observed=r['observed']
report=f'''#243 CLOSED: paired preservation/reference census

Same stopped Xromwell entry intervention measured producer admission closed in
both FIFO and PG before/after intervals. Actual preservation cleared all3 dirty
surface flags and compared3,072,000 bytes through actual GL download/fences.
The separate expected buffer uses the same conversion routine; no independent
pixel oracle. No pmemsave or pre/control RAM reads were performed.

References remained after readback:

| Modeled reference | Observed |
| --- | --- |
| Surface CPU callbacks | {observed['callbacks']} |
| Bound texture units / texture-cache entries | {observed['texture_units']} / {observed['texture_cache']} |
| Shader entries / initialized shaders / save handles | {observed['shader_entries']} / {observed['initialized_shaders']} / {observed['shader_save_handles']} |
| Shader modules / element-cache entries | {observed['module_entries']} / {observed['element_entries']} |
| Bound color / zeta surface | {observed['color_binding']} / {observed['zeta_binding']} |
| Display buffer / dimensions | ID{observed['display_buffer']},640x480 |

All modeled reference data was identical before/after except dirty/download flags.
One texture cache entry's range exactly aliases a retained color surface:
offset65,208,320,length1,228,800. This is a modeled VRAM range overlap, not proof
of a live GPU hazard or latest-content ownership. Save handles are not proof of
running threads. CPU callback queues/actual GL bindings and complete per-object
identities/completion remain unobserved. Existing finish restores old producer
admission AFTER these samples; no persistent handoff or native permit granted.

Actual pinned Xromwell11100 and FreeLoader200a20 instructions observed in this
same boot; all breakpoints removed, physical-read mode0 confirmed, guest resumed.
Unchanged native224/219/211 captured-core policy, no synthetic null bindings or
driver/device changes. Known exact wizard helper remains assisted. No hardware
access or physical/ordinary acceleration qualification.

65 allocations/releases/exposure refusals,3,194,880 verified CPU bytes,four joined
workers;8 retirement rounds/128 MMIO reads retain UNMODELED_BUSY/NO_OWNERSHIP.
Normal restart/dashboard,6006 count1,orderly host exit0 with no Kill fallback.
Full cold allocation{r['allocation']['files']} files/{r['allocation']['directories']} directories/
{r['allocation']['directory_clusters']} directory clusters,zero errors/orphans;5 structural hives,
protected/staged hashes,startup,typed policy and event/SetupAPI history pass.
Sole warning/error remains Ftdisk49 type1; application delta empty. Strict,
ordinary,physical,native ownership and complete retirement remain FALSE.

No baseline paths disappeared.239 control/241 had an additional generated
/winnt/system32/wbem/logs/wmiadap.log, absent in both242/243; it was absent in
the immutable seed. This path difference is retained in directory-delta001.json;
the census does not establish its cause or all-file-byte/power-loss durability.

243 host correction reuses actual242/build004 executable unchanged:
SHA{build['executable_sha256']},bytes{build['executable_bytes']}.
Source revision e72e76bd1f12ce45c6c63b4196c6918ea2cc705d and pinned toolchain in
242/build004.json. Only nv2a.c,nv2a_int.h,GL renderer changed versus241; actual
preservation/consume/surface implementation unchanged. Borrowed sources restored.
243 does not represent a new compile or sanitizer run.

242 original runtime preserved bytes and both real reference slots, but host
qualifier failed at enabled maskFFFFFFFF mistaken for pending work. It remains
CLOSED failed; cold/CPU success does not retroqualify its trace.243 NEW runtime
gates pending/waits/work0 and enabled mask equal actual pre-PG sourcefield5.
No event suppression or relaxed pending-work gate. Header/compile/setup/helper
failures retained under242 before any guest launch in those stages.

Actual compiled242 C helper23 cases/98 checks each O0/O2 ASan/UBSan; unchanged
actual consume18,432 cases/110,593 checks each; no leaks/sanitizer diagnostics.
243 actual host parser/intervention54,guards72,connection12,closure25 checks.
849 frozen pins unchanged; both242/243 process identities closed/no root guest
queued. Matrix243 finished{m['finished_utc']}. Closed portable240/241/242/243
copies hash-readback verified on E with original junction paths; no disk backing
chains moved. Preserve20GiB build guard, physical0101/video0093,0088rollback and
immutable0.1.0. Private compiled/media/hive/disk bytes stay local.

Next: use OWNERS.md/SCHEMA.md to design actual bounded CPU callback-removal and
frontend/display completion. Never wait/join while holding locks needed by the
other actor; never dispose dirty data or convert preservation success into native
ownership. Model/cache summaries alone cannot qualify complete reference retirement.
'''
p=k/'REPORT.md';assert not p.exists();p.write_text(report,encoding='utf-8')
p=old/'REPORT.md';assert not p.exists();p.write_text('''#242 CLOSED failed host verifier

One real preserve001 at pinned Xromwell11100 produced terminal3:3 dirty surfaces,
3 actual downloads,3,072,000 compared bytes. New bounded before/after slots both
valid while FIFO admission1; dirty flags cleared, model refs remained unchanged.
Host qualifier incorrectly included enabled-interrupt maskFFFFFFFF in pending
work check. Original trace failed, guest resumed/full teardown/mode0; FreeLoader
entry was not subsequently traced. Matrix85879 CLOSED1, never replay/recollect.

Normal workload/restart/dashboard/orderly VM exit0 and full cold allocation
6724 files/320dirs/321dirclusters/zeroerrors/orphans,5 hives/protected/startup/
typedpolicy/history pass. SoleFtdisk49 warning/error remains. Trace/paired scope/
strict/ordinary/physical/native ownership remain FALSE. review001 verifies raw
source fields while explicitly preserving original failure, no retroqualification.

Retained3callbacks,4textureunits/24textureentries,53shaderentries/savehandles/
modules,93elements/displaybuffer. A save handle isn't proof of thread liveness.
CPU callback queues and actual GL bindings remain unobserved. Old finish restores
admission after observation; no release/native permit/acceleration qualified.

Build001 compiled but strict helper review found signed comparisons. Build002
stopped before source borrowing at renamed nonexistent prior manifest; build003
stopped at renamed prior capsule path with finally restoration. Build004 compiled
corrected bounded comparison, sources restored. Test001 retains actual helper/
header/redefinition failure;004 retains primary-header unused-parameter warnings;
005 passes23cases/98checks each O0/O2 ASan/UBSan using real QEMU headers as system
headers and strict actual-helper warnings. Guard002 missing capsule failure
retained;003 passes72checks. Consume18,432cases/110,593checks each,hostparser53,
closure25,connection12 pass. Failed preparatory stages never launched a guest.

772 frozen pins unchanged. Candidate349cc614194f102d429dfc724a172e8ada2e404c8853dd4686bfb44c00abf24f.
Read243 REPORT/DESIGN for fresh corrected host interpretation on same compiled
binary and source-owner notes here. All old/hardware/0.1.0 evidence preserved.
No physical IO/peer integration. All root242/243 process identities closed in243
process-closure001.json. Capacity offloads preserve hashes/original paths; no disk
backing chains moved. Future disposal needs actual async CPU completion and
frontend/display ownership, not counts or forced success.
''',encoding='utf-8')
dest=k/'report-review001.json';assert not dest.exists();dest.write_text(json.dumps(dict(passed=True,reports={str(p.relative_to(k.parents[1])):sha(p) for p in [k/'REPORT.md',old/'REPORT.md']},actual_reviews={str(p.relative_to(k.parents[1])):sha(p) for p in [k/'review001.json',old/'review001.json',k/'directory-delta001.json']},no_requalification_of242=True,physical_access=False),indent=2)+'\n',encoding='utf-8')
print('242 negative/243 qualified-scope reports recorded from actual closed evidence')
