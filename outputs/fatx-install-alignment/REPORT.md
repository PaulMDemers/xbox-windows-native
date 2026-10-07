# Two actual installer writes at the physical anomaly offset remained intact

7 October 2026 UTC. Two fresh sibling pre-install emulator fixtures completed the
same targeted GPU installation with FATX0101/video0093 and the unchanged prior004
UI helper. The post-copy warning starts at exactly270225 in both cold logs:
sector offset401, 4KiB offset3985. All220 warning bytes and its first111 bytes
match the expected emulator text. No corruption reproduced.

| Case | Launch UTC | Dashboard return UTC | Actual warning offset | Added log bytes | Diagnostic |
|---|---|---|---:|---:|---|
| 001 | 03:45:33 | 03:48:32 | 270225 | 5300 | PASS |
| 002 | 03:50:41 | 03:53:31 | 270225 | 5300 | PASS |

Both cases preserve the original135501-byte log plus131059 bytes of deterministic
ASCII padding, then append5300 ASCII bytes. Five hives parse completely, GPU
class0001/XboxVnt5/oem2.inf/ConfigFlags0 and exact INF are present, runtime/driver/
boot hashes match, the helper completes its three identified UI actions exactly
once, the install queue is idle at120seconds, and EventLog records one normal
shutdown. No new unexpected errors, popup events or application events occurred;
identical inherited SCM7000/Ftdisk49 records retain their explicit classification.

Before each run:322 directories,6738 files,323 directory clusters, zero allocation
errors/orphans. After each:322 directories,6743 files,323 directory clusters, zero
errors/orphans. Directory/FAT audits also cross-check three ranges with an
independent reader. Allocation consistency alone would not prove payload validity.

Preparation changes only the log and required allocation: its existing directory
slot, first cluster and original chain13963/13964/13965 are preserved. Two free
clusters2144540/2144541 extend it. Only the old final FAT link and these two entries
change. Startup, helper, five hives, trace, INF and drivers are hash-preserved.
Both cases use the same immutable first-install0101 parent, never a prior result.

The target emulator sector is LBA290163071. The saved physical scan after the
second GPU boot maps the same log offset to LBA292691839. Both are above the
28-bit address boundary; they are different disk locations. The physical scan
does not establish allocation at the instant of the first damaged write.

The original physical malformed span remains111 bytes. Reinspection clarifies an
old label:91 bytes have their high bit set and one is DEL(0x7f), totaling92
nontext positions. Earlier reports called all92 non-ASCII. The raw evidence and
boundary are unchanged; no repair or causal attribution was made.

## Limits and disposition

This is UI-assisted emulator diagnostic evidence, not ordinary stability or
physical qualification. The helper changes timing; the physical package path
was xwninf102 rather than xwninf99, and allocator history/controller/memory differ.
An intact final SetupAPI line does not expose its original live caller buffer.
The first physical reboot method is still unknown; absence of6006 is not proof
of a power cut. Quiet aligned writes passing does not exonerate all FATX paths.

Both runners, local supervisors and read-only audit processes closed. No physical
FTP, deployment, restart, driver change, new recovery snapshot, tag change or
automation change. Physical0101/video0093, normal startup, GPU registration,
remaining device prompts, raw-C capacity warning, original0088 and immutable
0.1.0 are preserved. NEXT.md records a paired drawing/file-I/O load comparison;
no speculative driver fix is justified by these negative reproduction results.

Evidence: each case's qualification.json pins audit/package/allocation/collection/
launch/alignment/layout reports. context-review.json links the actual warning
contexts. verify-evidence.py checks staged Git bytes and helper provenance;
verify-context.py checks preserved raw log hashes and the count clarification.
Private media stays excluded from Git.
