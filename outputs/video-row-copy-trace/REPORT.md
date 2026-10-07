# First-row copy branch and mapping evidence

The single trace001 run passed diagnostic verification: 186 events, 87 paired
calls, 392 relocated resident code pins, and 24 first-row samples across small
and large upload/overlap brackets. All sampled rows selected the direct kernel
memmove branch. No drivers, settings, device policy or physical console changed.

The observed win32k row target RVA117125 called RVA117179, whose target thunk
RVA c4fa resolves through its actual IAT to ntoskrnl memmove RVA608f0. All 24
descriptor flags at +0x34 were zero. The alternative helper RVA13afc8 and its
MMX/scalar branch markers were not executed in these samples. This verifies the
selected call and return, not an instruction trace inside kernel memmove.

Each captured source/destination byte range belonged to the corresponding
EngCopyBits surface row. Current CR3 matched the recursive page-directory PFN.
Screen destinations mapped through the F3C/F3D framebuffer aperture: for example
VA FC26805C mapped to physical F3C2A05C with PCD and PWT set. Temporary cursor
surfaces used ordinary RAM mappings with those PTE bits clear. Raw page-table
bits do not establish the complete effective memory type; PAT/MTRR state was
not captured. Neither this mapping nor branch evidence proves a hardware
performance cause or justifies changing cache attributes on its own.

After complete breakpoint teardown and resume, the existing probe107 completed
54 cases and 162 full RGB verification stages, requested normal restart and
returned to dashboard. Cold audit passed: 324 directories, 6755 files, 325
directory clusters, zero allocation errors/orphans, five structural hives and
all protected hashes. Warning/error and application event deltas were empty;
one normal shutdown event was present. Configuration and the 96MiB pagefile
map/content remained unchanged. trace-verification.json independently checks
source/module pins, pairing, descriptor arithmetic, row bounds and page walks.

This is a debugger diagnostic PASS with ordinary_qualified=false. Its timings
are not ordinary performance evidence. Prior ordinary QPC results remain the
time attribution evidence. Physical FATX0101/video0093, original0088 rollback,
immutable0.1.0 and completed emulator high-LBA dump recovery are preserved.

Preparation41444, runner69252, tracer59174, supervisor40359 and audit82892 are
closed. The owned run is work/runs/nt5-vrow-trace001; its private disk hash and
cleanup identities are recorded in trace001/closure.json. Never relaunch or
recollect this attempt.

Review: first-row breakpoints are armed only inside the paired outer copy and
removed after the first hit; source/destination/length are read before the call.
The fallback thunk and callee bytes are resident-pinned. Optional MMX state is
read only after a path that itself reads that state. Finally teardown removes
every armed breakpoint and resumes the guest. No argument, return or register
mutation is used. See DESIGN.md and the frozen source snapshot for the protocol.
