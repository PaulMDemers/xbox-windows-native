"""Record current work without claiming an unfinished runtime result."""
from pathlib import Path
k=Path(__file__).resolve().parent;p=k.parent/'engineering-notes/CONTINUATION.md'
note='''# NVNet0104 compiled; fresh normal comparison in preparation

2026-10-07 11:55 UTC. Pushed edf81dd closes controlled-dump-observe/crash002;
never relaunch/recollect. Actual nested D1 at IRQL31 proved NVNet shutdown calls
absent PAGE NvNetIdleTransmitter before dump writing. New uncommitted
outputs/nvnet-shutdown-resident contains0104 removing PAGE on both definition
and declaration, unchanged MMIO sequence. Preliminary build001 rejected by
residency gate because header annotation remained; preserved preliminary-build001
and private binary. Corrected build002 source4ab4b8ab56ee8373d60b3fade3ea192c041266c9
and matched control001 compile/import/residency reviewed. Candidate aee9c501...
control3ac30498... All shutdown helpers now nonpaged candidate. No runtime result
yet. Normal kit adds two bounded TCP exchanges, each32x4096 bytes each direction,
local host4597, before/after792append32shrink132reopen workload. Same FATX0103/
HAL0102/video0093/HidServ and emulator-only device policy; strict events retained.
Preparation control001 session77650 ACTIVE; builds17429/15911/93127 CLOSED.
Inspect actual fixture/preflight/launch/cleanup records, never duplicate.
Next normal matched controls/candidate full cold audits, then a NEW controlled
crash with actual NVNet callback return/dump high-LBA evidence; recovery only
after valid dump evidence. C:~28.5GB,20GiB guard unchanged. No physical access.
Original111nonASCIIphysicaldamage/restart unresolved; preserve all baselines.

'''
p.write_text(note+p.read_text())
