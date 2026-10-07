# Actual SetupAPI.log traffic is on the paging-write path

Case001 launched05:42:13UTC7October2026 on the unchanged draw001 input. The
read-only debugger observed52 writes to the exact FATX path\winnt\setupapi.log,
all with IRP flags0x43 (including paging I/O), each paired with VfatWrite success.
No CcCopyWrite call for this file was observed. This identifies a paging path;
it does not yet identify the user-mode mapping APIs or imply a driver defect.

Every entry MDL had flags2 (pages locked, no existing system mapping). The tracer
intentionally did not map guest pages or read an unverified pointer. Consequently
zero source buffers were captured. Both source-coverage fields remain false.
Entry lengths sometimes exceed EOF and differ from returned information; the
pinned source clips paging writes at EOF. Post-mapping capture is needed to see
the buffer and effective length actually consumed by the driver.

The20,000-hit limit stopped the debugger after52 paired records, with no pending
records, breakpoints removed and guest resumed. The ordinary helper then finished
its normal restart. Owned cleanup preceded all cold reads. The target warning
remains exact at270225, with its111-byte prefix ending at270336. Full allocation,
selected binary hashes, five structural hives, installation and event checks
passed. This is still a debugger diagnostic, not ordinary or physical qualification.

review-sites.py pins candidate0101, compiler-derived offsets and exact relocated
instruction bytes. VfatWrite receives a pointer to a context pointer, not the
context directly. Return capture occurs before dispatch completion; pending
statuses are never treated as completed writes. The next isolated attempt adds
the verified post-VfatGetUserBuffer site to observe mapped paging input.
