# Serial shrink passed; concurrent coverage attempt failed

October 7, 2026. Both attempts are closed, cold-audited and pinned. Do not
relaunch or recollect. No driver change, physical access or release promotion.

serial001 launched07:24:52UTC and returned07:27:07UTC. It completed792 appends,
32 queried allocation-size decreases,132 exact reopens and11 exact cold files.
Normal shutdown count1. Full allocation:323 directories,6764 files,324 directory
clusters,zero errors/orphans. Five structural hives and protected hashes pass.
Strict qualification remainsFALSE for the exact recurring SCM7000 HID Input
Service and Ftdisk49 events. Intermediate AllocationSize is an API observation;
only final allocation ownership was independently cold-scanned.

flush001 launched07:29:32UTC and failed its measured-overlap gate after the
second file-round: CASE_OVERLAP0/0=12, CASE_OVERLAP0/1=0, FAIL_NO_OVERLAP0/1/0.
The helper exited without normal restart; its failure path did not stop/join
the worker explicitly. The15-minute dashboard observer then timed out. This
is an incomplete coverage test, not evidence of filesystem deadlock or a fix.

After recorded timeout, a diagnostic snapshot paused/resumed the owned guest.
The framebuffer showed the desktop. The pinned offline decoder found no probe
process, no contended FATX resources and no exclusive wait cycles; this is a
single snapshot, not proof of all earlier scheduling behavior. Shared owner
tables/other synchronization types are outside its scope. Host termination
followed capture. No normal-shutdown event exists. The private64MiB RAM,
registers, framebuffer and retained disk are preserved; no UI action was taken.

Cold audit:323 directories,6755 files,324 directory clusters,zero errors/orphans;
five hives and protected files pass. Two present workload files match completed
round0 exactly (partial-round-bytes.json); they correctly FAIL the planned
round3 final-byte oracle. Nine later files are absent. Existing two event errors
remain strict failures. No gate was waived.

Prelaunch source bytes are preserved in each case's source/ directory and
verified against preflight.json. The collector was subsequently extended to
label post-timeout diagnostic capture accurately; verify-evidence.py checks
the immutable prelaunch snapshots. The capture/decoder derive from the prior
directory-order kit using the exact0101 structure offsets; no workload globals
from that older helper are interpreted. comparison.json verifies identical
parent/helper/policy and keeps the failed concurrent result separate.

All owned sessions closed: serial runner39731/supervisor82744/audit35593,
flush runner4186/supervisor21706/audit82702, comparison83995. Configuration
before/after preserves the settled emulator's synthetic QEMU null driver and
01B0/01B4 unsupported-device flags. This is not physical device support.

Next: a NEW unique kit should retain this failure and deliberately provide a
bounded overlap window. Do not remove the overlap requirement. Make every
failure path signal stop and join the worker, record failure separately, then
leave the failing guest for evidence. Repeat the matched serial control with
the same helper before its concurrent partner. Do not modify FATX speculatively.
