#536 warm/cold CPU-context comparison closed

Both instrumented launches reached the Windows desktop, followed by user-requested
normal Windows Restart and dashboard return. Case1 followed the previous Windows
Restart with no intervening power cycle. Case2 followed a separately reported
power-off for10seconds and power-on. Power rails/duration were not instrumented.
Cold-case after2 collection completed on October18,2026 at19:44:04UTC; all host
supervisors are closed. No third launch is planned or allowed in this pair.

| Actual evidence | Warm536a | Cold536b |
| --- | --- | --- |
| Desktop and dashboard observed by user | Yes | Yes |
| Five registry hives independently validated | Clean | Clean |
| New EventLog6005 /6006 | 1 /1 | 1 /1 |
| New Ftdisk49 /shutdown Popup26 | 1 /3 | 1 /3 |
| Preparation, handoff, CPU records decoded | Yes | Yes |
| Refusal record present | No | No |
| Original launcher/startup and720p protected baseline | Exact | Exact |

The raw preparation packet is byte-identical across the pair. Its allocation
addresses, physical backing, saved registers, flags, loader/payload comparisons
and completion marker match. At each corresponding pre-witness/post-witness
snapshot, CR0/CR2/CR3/CR4, EFLAGS, segment selectors, GDTR/IDTR, ESP and return EIP
match. The complete decoded difference list contains only case ordinal, TSC
samples and marker polling count (1170 warm /1158 cold). See comparison001.json.
The two epochs are compared separately; the later snapshot still precedes the
context packet's own file IO and final handoff. No pagewalk, descriptor contents,
cache/device state, own-close or final-transition proof follows. Equal CR2 is an
observed register value, not evidence of a new fault during this launch.

This experiment did not reproduce the ordinary-launch failure. It provides no
CPU/preparation difference explaining532's warm failure, and does not qualify a
boot fix. Recorder code/layout, memory use, IO and timing differ from the ordinary
launcher. Preserve532/533 ordinary success/failure/success and534 cold success/
success; neither deterministic alternation nor a power-cycle fix is established.
Both runs retain Ftdisk49 and shutdown rundll32 Popup26 entries. The hive checks
are not a complete FATX allocation/health audit. No GPU/game/release promotion.

The original after1 supervisor refused host capacity before any network access or
capture. Its failed receipt remains. User-authorized cleanup538 removed six
obsolete negative-test fixture copies, freeing6.2GB while preserving recovery,
source, current dependencies and historical outcomes. New supervisor002 collected
the still-uncollected warm case with the frozen controller; no launch was retried.

No Windows startup hook was installed. Ordinary launcher, drivers and720p settings
were preserved. Xbox dashboardC was not accessed. Console remains at UnleashX;
automation remains paused. final001.json records processes, supervisor outcomes,
all package source/binary pins and every collected record hash.

Next: review the original374 and recorder490 allocation/control-flow footprint,
including unchecked allocation results and DF before the ordinary first copy,
against retained535 disassembly evidence. Design a smaller bounded observer only
if it distinguishes a concrete hypothesis with less perturbation. Validate its
memory access and host checks before a fresh experiment. Do not repeat either
closed536 runtime, clear pending hardware state, or infer a functional patch from
this successful instrumented pair. The next D3D stage remains separate.
