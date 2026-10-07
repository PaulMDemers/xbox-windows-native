# Read-only inventory of the physical C range

This nxdk helper opens Partition0 with read-only access and captures only the
fixed Xbox system partition range: offset 2,359,820,288, length 524,288,000.
It requires FATX, 16 KiB clusters and root cluster 1, then saves FAT metadata
and live directory records beside its uniquely staged E: executable. It never
opens a raw write handle, repairs allocation, or modifies a partition table.
Outputs use exclusive creation. The normal Windows startup and drivers are
checked before physical launch and collection and are not replaced.

This avoids assuming that dashboard C or the kernel's Partition2 path exposes
the actual system partition under a softmod. It inventories names/allocation;
it does not establish payload integrity or authorize deleting boot/softmod data.

Build with Build.ps1 using the shared nxdk build lease. build.json preserves
source and binary hashes. prepare.py stages only a new emulator E application.
Host attempt raw-c-inventory-001 failed opening the deep backing chain before
guest boot. flatten.py made a new self-contained fixture and qemu-img compare
verified equivalent virtual bytes without changing its source.

Attempt002 launched the helper once and retained its completed capture. The
FTP data-collection loop failed; dashboard control eventually answered421 after
connection accumulation. No relaunch occurred. Host cleanup closed the owned
emulator, then validate.py extracted the reports offline. The metadata and all
three fixture entries match exact disk bytes and independent traversal; C has
no top-overlay write extents. Allocation is consistent. This is bounded helper
validation in an emulator fixture, not a Windows or physical storage PASS.

physical.py records the separate single physical launch/collection. Inspect its
JSON before doing anything; never repeat a recorded launch. Reports belong only
to /E/Applications/XWNRawC001. All private images and binary captures are ignored.

## Physical result

The single physical probe returned to UnleashX and was collected. It found33
directories,83 files, zero allocation errors/orphans and179 free16KiB clusters
(2,932,736 bytes), exactly matching Windows' prior raw-C capacity reading. The
large allocation is /nkpatcher/shadowc/shadowc.img at508,559,360 bytes. This explains
the apparent discrepancy with dashboard C's small exposed file tree. Every raw
C file, including the shadow image and rescue/dashboard components, was preserved.
This is metadata evidence; the helper does not read/hash each file payload.
