# Next: prove the boot-device handoff before native implementation

426 is host-only; tests001/002 are consumed, not guest attempts. No driver or
physical change. Do not repeat423/424/425 or any earlier closed runtime.

Read DESIGN.md and source-review001.json. Fixed NTFS-in-FATX is the selected
prototype route, not a supported installation option. Block translation works
only under modeled complete ownership; no real exclusion/handoff is implemented.

Next inspect exact NT5 loader boot-device/ARC-name registration, boot-driver
ordering, storage stack enumeration and mounted-device identity. Determine how
an image device can be present before NTFS mounts the system volume, with parent
E excluded from Windows FATX writes and no recursive backing-file opens. Pin the
actual upstream materialized files, not just partial public overlays. Compare
existing read-only NTFS loader experiments without replaying their guests.

Produce a concrete init/teardown and memory-budget design with actual entry
points and error paths. Resolve paging/dump behavior and the disk/volume identity
contract; a matching NTFS serial alone cannot detect same-serial replacement.
Only then implement a separate read-only image-device prototype and independently
compare mapped reads to the original file on a disposable fixture. Do not start
with writable system-volume boot. Never weaken the six lossless transfer or
strict-event gates, disable dumps, or patch FATX name limits.

After read-only proof, validate actual exclusion/flush/lower failure, bounded
memory/IRP concurrency and interrupted recovery before writable NTFS boot.
Then two-boot RSA/DPAPI, COM+, create/open/enumerate/case/rename/delete with open
handles, install/restore and full cold audits are still required. Windows crypto
keys/media/private disk bytes stay outside the public repo.

C was below20GiB at426 start; no native build or guest launch was attempted.
Recheck projected capacity and recover only reviewed closed non-backing artifacts
if necessary. No build guard changes or backing-chain moves. E remains scratch.
Physical720p demo stays restored; no hardware test queued.
