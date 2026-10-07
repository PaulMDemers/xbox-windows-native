# Cache handoff diagnostic PASS; early WC request would fail

The observed boot-video map occurs before NT5 permits write-combining PTEs.
The same internal flag is enabled by desktop mapping time. Replaying the actual
resident kernel mapping function with those captured states rejects an early
WC request and accepts a late one. Consequently, changing both mapping calls to
WC at startup is not a viable candidate. No live cache setting was changed.

## Observed calls and mappings

The fresh trace002 pairs three real calls by thread and stack, with pinned entry
and caller code:

| Caller/path | Physical range | Cache argument | Returned view | MiWriteCombiningPtes |
| --- | --- | --- | --- | --- |
| Bootvid -> MmMapIoSpace | 03C00000 +4MiB | 0 (uncached) | FCED6000 | 0 |
| Videoprt -> MmMapVideoDisplay | F3C00000 +4MiB | 0 | FC23E000 | 1 |
| Nested MmMapIoSpace | F3C00000 +4MiB | 0 | FC23E000 | 1 |

Actual bootvid text/globals, all resident0094 miniport text, the videoprt caller,
kernel entries and the complete418-byte MmMapIoSpace function match the pinned
owned executables after relocation. The002 trace uses the established breakpoint
step-over sequence; the failed001 observer is preserved separately.

Immediately before the first bootvid map, the current System CR3 has no present
translation into either framebuffer physical window. This early snapshot covers
that root only, not all possible roots or stale TLBs. At the first probe marker,
the full walk of20 active roots examined20,480PDEs and3,947,520PTEs. Each root
contains both full4MiB views, PCD/PWT set, PAT clear and supervisor-only, totaling
40,960 matching entries. The same retained bootvid owner found in the prior
inventory is confirmed again.

The read-only0094 logger captured PAT `0007010600070106`, MTRR default `800`
and all eight advertised variable ranges at desktop mapping time. PAT index3
is UC. This is a mapping-time MSR sample paired with the later full PTE inventory,
not simultaneous MSR sampling at the desktop breakpoint. Raw values are retained
in mapping.json. No MSRs, PTEs, registers, mode or pixels were edited by the tracer.

## Actual-code replay, separate from runtime

`replay-map.py` executes the pinned kernel's real MmMapIoSpace instructions in
Unicorn, using captured KeFeatureBits, MiWriteCombiningPtes and ValidKernelPte.
Allocation/release, cache invalidation and TLB helpers are explicitly modeled;
this does not run a WC request in the guest. Four bounded cases pass:

| Captured state | Request | Result |
| --- | --- | --- |
| Boot-video | UC (0) | All1024 expected UC PTEs; non-null mapping |
| Boot-video | WC (2) | NULL; reservation released; no PTEs written |
| Desktop | UC (0) | All1024 expected UC PTEs; non-null mapping |
| Desktop | WC (2) | All1024 expected WC PTEs; modeled cache/TLB helpers called |

The relevant branch is in MmMapIoSpace RVAs37dce..37e33: when the feature bit
is present but MiWriteCombiningPtes is not1, requests2/5 take the failure path.
No kernel patch or private-global write is proposed. Replay establishes the
conditional API behavior, not real WC hardware correctness or performance.

## Validation and provenance

`contract-verification.json` cross-checks paired calls, resident bytes, early/late
globals, observer trace hash, aliases, replay, cold audit and closure. Baseline
runtime and replay evidence are distinct. `ordinary_qualified=false` because
this run used a debugger and the diagnostic0094 miniport.

The unchanged drawing workload completed54 cases/162RGB stages, normal restart
and dashboard return. Cold checks passed:324directories,6755files,325directory
clusters, zero allocation errors/orphans, five structural hives and protected
hashes. The actual loader bootvid, configuration and96MiB pagefile were unchanged.
No new warning/error/application events. Source/binary/fixture pins remain in the
case's frozen preflight sources; private RAM and full alias entries are hash-pinned
by compact tracked summaries. A verifier initially compared videoprt's unrounded
PE image size to its loader allocation; it was corrected to the page-rounded
size after checking50368 versus53248. No guest data or acceptance gate changed.

No new guest driver was compiled. Existing0094 (SHAea18fa6c...) adds read-only
observations to0093's mapping requests. The rest of the emulator remains
FATX0103/HAL0102/NVNet0104/ATAPI0105, restored HidServ, Microsoft framebuf and the
inherited settled null/unsupported-device policy. The historical0094 physical
popup failure is not waived. Physical0101/video0093, original0088 rollback,
immutable0.1.0 and completed128GiB dump recovery are untouched. The physical
111-byte anomaly remains unresolved.

Preparation58615, runner83512, tracer88800, supervisor81846 and audit39517 are
closed. Accepted2026-10-07T19:34:24UTC. Retained disk:
`work/runs/nt5-vhandoff-trace002/hdd.qcow2`; closure.json pins its hash. Never
relaunch/recollect either case. No owned emulator remains. See NEXT.md for the
ownership prototype now required before a WC speed trial.
