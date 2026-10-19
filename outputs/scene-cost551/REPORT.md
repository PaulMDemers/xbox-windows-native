# 551 Xbox scene process costs: scoped PASS

After the user-confirmed full power cycle, one launch through the unchanged
ordinary launcher completed six scene processes: three default and three HEL.
The exact 550 benchmark and exact 547/549 scene executables were used. All six
five-stage pixel checks passed at protected 720p/RGB32, including native CPU
staging, clipping, occlusion, window movement and source preservation.

| Mode | Run | Elapsed seconds | Process CPU seconds | Reported peak WS KiB | Reported peak commit KiB |
|---|---:|---:|---:|---:|---:|
| default | 1 | 22.455 | 0.480 | 1996 | 656 |
| default | 2 | 7.770 | 0.480 | 1992 | 656 |
| default | 3 | 7.350 | 0.510 | 1988 | 656 |
| hel | 1 | 7.410 | 0.450 | 1992 | 656 |
| hel | 2 | 8.145 | 0.390 | 1992 | 656 |
| hel | 3 | 7.350 | 0.405 | 1992 | 656 |

The first default process took 22.455 seconds; the remaining five took 7.350–8.145
seconds. Preserve that first result. Its observed starting system-available
memory was 1,200,128 bytes and later observations varied widely. These observations
do not isolate startup activity, caching, paging or storage as the cause of the
longer first run. The modes ran in fixed order, so this is not a controlled
backend-speed comparison. Process CPU time excludes other processes and can
exclude work performed elsewhere in the system.

These are whole-process measurements including startup, deliberate window
pauses, CPU conversion and capture writes, not FPS or rendering-only timings.
Sampled memory counters can miss brief peaks; the separately reported process
peak counters are retained. Six separate processes do not prove repeated work
within one process is leak-free. Global memory changes are contextual, not
attributed to the scene. No GPU, game, varying-W or ideal-alpha qualification.

One SITE request accepted 2026-10-19 00:58:27UTC; observer returned with a runner
receipt and 73 result files. All child and wrapper exits are zero. The runner
requested normal restart and cold EventLog 6006 delta is one. Collection completed
01:04:33UTC at authenticated UnleashX: the exact owned startup hook was removed
FIRST, then 99 files received paired readback. Five before/after hives pass the
independent structural/value checks. A whole allocation audit was not performed.

Ftdisk 49 recurred. No new application-log records or shutdown-popup record were
found in this run's audited delta; that does not resolve the earlier popup.
Strict whole-system qualification remains false. Event review uses decoded
record-sequence boundaries, not proof of complete active-ring coverage. Boot
reliability remains unresolved and its investigation stays tabled.

All 11 live scene module entries match cold bytes and PE image sizes for each
of six children. All 11 pinned runtime DLLs, including PSAPI, match cold readback.
The wrapper itself has no live module trace; its exact binary and installed
PSAPI identity are pinned.372 malformed actual-telemetry variants were rejected.
Protected launcher/startup and 720p remain exact. All 54 frozen inputs archived
privately; all owned supervisors and observer are closed. No next launch queued.
Never rerun or recollect 551. See final001.json, runtime-review001.json,
module-review001.json, actual-controls001.json and audit1.json.

Visual screen confirmation is not yet recorded; the pixel evidence above is
independent of that pending observation. Public sample build/run instructions
are in docs/graphics-samples.md. The public rebuild source/import comparison
is separate from the runtime-qualified exact binaries used here.
