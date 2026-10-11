# Actual invalidation paths observed

One new emulator diagnostic launched at 19:14:38 UTC on October 11, 2026,
returned to dashboard at 19:16:04, and closed all owned guest/debugger processes.
The unchanged phase250 guest fixture ran with a scalar-instrumented xemu build.
This is debugger evidence, not an ordinary run, physical qualification or speedup.

The complete, untruncated trace contains 49 observation groups and 23 paired
caller/common-entry removals:

| Path | Removals | GPU-dirty at caller | GPU-dirty at common entry |
| --- | ---: | ---: | ---: |
| Age eviction | 20 | 15 | 0 |
| CPU-write eviction | 3 | 0 | 0 |

All three CPU-write removals retained upload_pending. Three CPU-write callbacks
were observed; there were no CPU-read callbacks, overlapping replacements,
incompatible replacements or flush removals. There were no unmatched pairs.
The CPU-write observation point is after the earlier pending download: it does
not demonstrate that dirty GPU data was absent before that download.

This establishes actual state transitions through existing download paths.
It does **not** prove the latest pixels were preserved. In particular, no new
permission follows to download old GPU contents over newer CPU stores. The next
experiment needs independent expected bytes and both directions of alias access.

The original workload completed 64 leases, 65 allocations/releases/refusals,
3,194,880 verified CPU bytes and four joined workers. Read-only GPU preflight
continued to refuse ownership. All 23 callback lifecycles retired; 1,859 frontend
loans completed (1,606 accelerated emulator display loans, 253 fallbacks).
These are emulator presentation operations, not native Windows acceleration.
The worker pause lasted 249,465,000 ns, with no observed rendering, surface
activity or loans inside it, and normal resume afterward.

Cold audit: 320 directories, 6,724 files, 321 directory clusters, zero allocation
errors/orphans, five structural hives and 28 protected files passed. There was
one normal-shutdown event and dashboard return. Scoped CPU/observation/integrity
checks passed. Strict qualification remains FALSE, including the inherited
Ftdisk 49 error and the unqualified preservation/ownership contract.

## Failures preserved and corrected host analysis

Build001 failed before its first write because the default WSL user could not
write the historical root-owned source. All 13 borrowed originals were unchanged.
Build002 used the existing root build convention under the build lease and
restored all borrowed sources. Only surface.c changed. Its executable SHA-256 is
785c53bf71a7a289361de5859ece8503130b3e58682b482eb55dfb486e6a4311.

The initial cold auditor stopped on a missing diagnostic module before any cold
collection. Audit-resume001 supplied the exact already-frozen phase250 parser
through PYTHONPATH; the same closed disk then completed its first cold audit.
The controller's original failure remains intact. No guest was relaunched.

The inherited worker parser rejected new phase100 telemetry. Its failure remains
in worker.json. Explicit lifecycle257/worker257/closed257 analysis validates every
new bounded group, keeps those events in order, and rejects new activity inside
the parked interval. Four negative cases reject missing/duplicate groups, an
unknown phase and a complete group injected during that interval. Corrected
analysis is separately recorded in worker257.json; no raw log was filtered.

The raw trace hash is
7e37e0017b705df62a821f4c66b3b00c691dcf497d576ce4eacbb34f4366a6e0.
All original frozen inputs remain unchanged. See site-observation.json,
site-pairs.json, audit.json, worker257.json and parser-review257.json.

Physical audio004/software-video118/shared158/FATX0101 remains unchanged. The
separate 256 recovery capture completed with 6,638 files and verified system
and boot/dashboard archives; it is a private file snapshot, not restore-tested.
