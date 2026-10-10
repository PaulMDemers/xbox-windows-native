# Next diagnostic boundary

Use a new sibling child of the same closed no-XID first-boot parent. Preserve
all existing failed disks, storage/probe pins and cold integrity/event gates.
Do not change storage drivers or use this result to qualify a physical boot.

Capture a bounded set of writes for C:\xwnctl\payload2.txt at these boundaries:

1. FATX cached-write input and paging-write input: file offset, actual bytes,
   IRP flags, current thread/process, MDL flags/PFNs and effective mapped address.
2. The sector-tail read/modify/write path: old sector, caller prefix/tail bytes,
   final private sector buffer, and child request status/information count.
3. IDE DMA scatter/gather source bytes and completion: correlate the virtual
   disk byte offset with the matching top-level/root block request.
4. Independent cold sector readback and full allocation audit after closure.

Prefer observing the existing binaries. Any debugger pauses or host diagnostic
instrumentation must be recorded as such, bounded, and kept separate from an
ordinary boot. Verify loaded binary/site bytes and structure layouts before
reading pointers. Do not assume the source buffer is valid merely because an
address is readable. Retain missing, failed and partial captures as unknown.

The current evidence cannot distinguish stale buffers submitted for writing,
correct writes later overwritten, or completion/backend failures. It also does
not prove that the broken WMI chains share the same cause as stale file data.
