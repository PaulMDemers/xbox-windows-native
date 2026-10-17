# 427: boot route narrowed to a contiguous NTFS image

The existing Xbox partition hooks offer a smaller initial implementation than
a new file-backed disk driver: validate one contiguous FATX image, then expose
its inner NTFS range as partition1 in both FreeLoader and the HAL. The dashboard
would still see an ordinary file on FATX E. Windows would see the inner NTFS
partition, with outer E absent from ordinary partition enumeration.

This is a **source/static review plus host prototype**, not an installed boot
path or demonstrated filesystem exclusion. Fragmented backing files are refused
by the proposed initial path. No native loader/HAL/driver was changed or built,
no guest prepared/launched, and no physical console access occurred.

## Evidence

- Reviewed actual403 loader and HAL sources, including the inherited Xbox
  phase0 initialization file absent from the partial public overlay. HAL installs
  its partition-table dispatch during phase0. Loader already carries the correct
  physical disk ARC signature/checksum and derives the NTFS boot service from its
  filesystem reader. Detailed source hashes/anchors are in source-review001.json.
- Exact owned Windows kernel84172dbd... and validated DBG/PDB binding identify
  boot-device waits followed by ARC-name creation, with later SystemRoot and
  drive-letter initialization. kernel-calls002.json preserves six static symbol
  intervals and callsites; private disassembly is under E:/xwn427/static002.
  Next-public bounds are not guaranteed function ends; no new runtime claim.
- Original MIT projection/header/read-only adapter passes **4,952 host checks**:
  every header truncation and single-bit mutation; semantic fields with
  recomputed checksums; partition overlap/identity; fragment and stale-map
  refusal;128 independently expected sector reads above128 GiB; prefix/EOF
  bounds; short-read quarantine; unchanged other partitions and paired modeled
  loader/HAL projections. All geometry/complete ownership facts are synthetic
  supplied inputs, not a real FATX scan or kernel authority.
- The wrapper prefix places identity metadata outside normal NTFS writes.
  Its experimental512-byte format has not been used on any disk. A UUID plus
  checksum is not authentication or protection from privileged raw writes.

static001's original age-equality check failed before any disassembly/output
directory. The mismatch was investigated rather than waived: image age1/PDB2/
DBI1 satisfies Microsoft's documented-in-source validation rule. static002
validates the signature, image timestamp/size and actual DBI age. The original
script and failure record remain.32 synthetic signature/age cases are included
in the host checks. No old evidence or binaries changed.

Historical NTFS-on-Xbox emulator shutdown and physical partition-hook
registration records were reviewed only. Neither qualifies this new file/image
projection. No previous guest was relaunched, recollected or used as a new parent.

## Remaining work

A real bounded raw FATX resolver and complete ownership audit must derive the
header/allocation facts. Read-only loader projection comes before HAL integration
and writable boot. The native implementation must prove identical geometry,
no parent E volume exposure, stable repeated queries, correct mounted-device
identity, bounded memory, failure refusal, paging/dumps and actual recovery.
See DESIGN.md and NEXT.md for concrete entry points and test order.

Physical720p demo and its original rollback stay unchanged. Six lossless-transfer
exclusions, current crypto failures, COM+, strict events, clean install/restore
and1080i remain open. No new Windows bundle/release is qualified. All owned
commands are closed; no hardware test is queued. C was21,294,034,944 bytes free
at start, below20GiB; only small host files/read-only analysis were produced.
No build/launch guard bypass, artifact offload or backing-chain move occurred.
