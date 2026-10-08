# Bounded upload-address diagnostic

Fresh emulator child, unchanged RAM0112 and pinned xemu. Probe141 differs from
probe140 only by exported stage markers and one additional untimed primary draw
before warmup for samples0,1,2. The existing45-case correctness/cold/event workload
continues afterward. All diagnostic timings are excluded, even if timer gates pass.
No physical access, driver changes, settings changes or automatic dialog actions.

At each marker, observe actual XwnUploadBox for solid192x96 at origins(0,0),
(128,0),(0,160). Capture PDEV bytes using offsets corroborated by actual compiled
address operands; rectangle, CR0/CR3/CR4 with recursive PDE check, and both endpoints
of all96 copied rows through bounded raw PDE/PTE reads. Match actual row-call
arguments, local memmove target, forward rep-movsd entry/exit registers, copied
first-row bytes and paired caller/whole-upload return. Thread/process/stack pairing
and relocated resident code pins are required. The compiled memcpy call resolves
to local memmove, not an imported runtime; no driver patch is involved.

Source/destination move together. Raw page-table flags do not establish effective
PAT/MTRR cache type or xemu TLB misses. Current snapshots do not measure a full
transfer-time distribution. Capture is bounded64stops/600seconds, remove every
breakpoint and resume guest in finally. Supervisor requires trace-armed before
one launch and waits normal dashboard return; do not relaunch on failure.

Use owned exclusive xemu/build leases, fresh IDs, pinned source/binary/fixture
chain and full cold audit. Preserve incomplete trace and any failure separately.
Only runtime evidence supports the next implementation hypothesis.

The first kit failed before capture on an unreadable user loader-list pointer.
This fresh kit uses the kernel loader list for driver identity and the executing
probe marker/header/resident bytes for probe identity. No page/register edits or
identity waiver. Exact probe141 and driver binaries are reused.
