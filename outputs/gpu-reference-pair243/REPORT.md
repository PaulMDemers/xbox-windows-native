#243 CLOSED: paired preservation/reference census

Same stopped Xromwell entry intervention measured producer admission closed in
both FIFO and PG before/after intervals. Actual preservation cleared all3 dirty
surface flags and compared3,072,000 bytes through actual GL download/fences.
The separate expected buffer uses the same conversion routine; no independent
pixel oracle. No pmemsave or pre/control RAM reads were performed.

References remained after readback:

| Modeled reference | Observed |
| --- | --- |
| Surface CPU callbacks | 3 |
| Bound texture units / texture-cache entries | 4 / 24 |
| Shader entries / initialized shaders / save handles | 53 / 53 / 53 |
| Shader modules / element-cache entries | 53 / 93 |
| Bound color / zeta surface | 1 / 0 |
| Display buffer / dimensions | ID10,640x480 |

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
Full cold allocation6724 files/320 directories/
321 directory clusters,zero errors/orphans;5 structural hives,
protected/staged hashes,startup,typed policy and event/SetupAPI history pass.
Sole warning/error remains Ftdisk49 type1; application delta empty. Strict,
ordinary,physical,native ownership and complete retirement remain FALSE.

No baseline paths disappeared.239 control/241 had an additional generated
/winnt/system32/wbem/logs/wmiadap.log, absent in both242/243; it was absent in
the immutable seed. This path difference is retained in directory-delta001.json;
the census does not establish its cause or all-file-byte/power-loss durability.

243 host correction reuses actual242/build004 executable unchanged:
SHA349cc614194f102d429dfc724a172e8ada2e404c8853dd4686bfb44c00abf24f,bytes191431226.
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
queued. Matrix243 finished2026-10-11T03:31:12.598163+00:00. Closed portable240/241/242/243
copies hash-readback verified on E with original junction paths; no disk backing
chains moved. Preserve20GiB build guard, physical0101/video0093,0088rollback and
immutable0.1.0. Private compiled/media/hive/disk bytes stay local.

Next: use OWNERS.md/SCHEMA.md to design actual bounded CPU callback-removal and
frontend/display completion. Never wait/join while holding locks needed by the
other actor; never dispose dirty data or convert preservation success into native
ownership. Model/cache summaries alone cannot qualify complete reference retirement.
