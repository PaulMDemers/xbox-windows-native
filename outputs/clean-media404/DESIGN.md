# Scope and evidence rules

Disc identity uses full size/SHA-256, with SHA-1 for catalog comparisons. An online
metadata match is weaker than a complete download/readback; neither establishes
Microsoft authenticity or successful setup. A matching file is not a license.

Clean installation starts with a new blank disk, not a previous runtime. Each
expected setup reboot is a separately recorded phase of the same installation.
Every phase has an output guard and bounded owner. No network adapter, physical
console access or old installed Windows tree is part of this experiment.

The witness requests a normal guest shutdown. Host exit0 alone is insufficient:
cold markers, setup flags, installed kernel identity, event records and hive
structure are checked separately. Disk-only means no CD/floppy in the actual
command and an unreadable CD reported by the guest. Manual witness invocation
cannot satisfy the failed automatic-handoff scope.

Registry raw structure and typed interpretation are distinct. Both independent
readers must agree on all key names, stored types and exact declared value bytes.
The custom VK reader handles inline lengths and allocated contiguous data cells;
segmented/invalid bounds refuse. Unknown typed values remain visible failures.
This is not a reason to change, delete or normalize the guest registry.

Cold extraction never mounts the disk writable. The first interrupted auditor's
completed extraction is resumed read-only, not recopied. Failed scripts/results
remain. Generated RAW copies are removed only after hash/readback and actual
parent-path checks; the installed QCOW2 and selected evidence remain private.

Public output contains source, guides and hashes only. Full image, key-bearing
answer floppy, Windows files/hives and screenshots are private. Fresh Xbox E
assembly from this newly installed volume remains an independent next step.
