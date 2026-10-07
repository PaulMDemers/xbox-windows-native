# Normal mapped append: exact cold bytes in both modes

Two fresh settled-device runs each completed936 mapping/seek/unmap/truncate/
close cycles and52 full-file reopen checks, requested normal restart and returned
to dashboard. All13 final files match independently generated expected bytes
and match between modes. Each full F: allocation audit has323 directories,
6766 files,324 directory clusters, zero errors and zero orphan clusters. Five
registry hives parse; selected runtime/driver/boot and test payload hashes match.

Mode0 follows the observed SetupAPI cleanup sequence without adding flush calls
within each append. Mode1 adds FlushViewOfFile/FlushFileBuffers before unmapping
and FlushFileBuffers after truncation. Both modes flush initial file contents
and diagnostic logs. They use the same helper, parent, startup and data; only
the mode byte differs. No debugger or UI action occurs in either settled run.
No filesystem driver was changed.

This is a bounded workload/persistence result, **not a strict qualification PASS**.
Both boots reproduce two exactly recurring historical error signatures:
Service Control Manager7000 for HID Input Service and Ftdisk49 for
HarddiskVolume6. All new errors remain strict failures. There are no new
application records or Application Popup events. No physical/release promotion
or recovery snapshot follows from these results.

## Preserved attempts and configuration

- mode0: xemu host startup failed before any guest/Windows launch because Windows
  could not resolve an expanded nested relative backing path. Source/preflight,
  stderr and cleanup are retained. The parent was copied into the common fixture
  directory and rebased; qemu-img compare proved identical virtual contents and
  the original remained unchanged.
- mode0b: one launch at06:55:07UTC. A Found New Hardware wizard recurred. The log
  records ATTEMPT_ONCE and INSTALL_IDLE_START258; no append file was created. The
  held guest was stopped at06:59:32UTC for cold diagnosis. No normal shutdown or
  persistence pass is claimed. Allocation, selected hashes and hives are intact.
- mode1: sibling of that unresolved-installation fixture was prepared but never
  launched. It is retained and must not be mistaken for the completed pair.
- settled0/settled1: fresh children of the previously verified0101 directory-order
  fixture with installed GPU and the explicit QEMU1B36:0005 null package. They
  inherit documented01B0/01B4 FAILEDINSTALL flags from old emulator isolation.
  Before/after configuration audits record this; no hive or device policy was
  changed here. This is not physical device support. Launch/return timestamps,
  exact hashes and strict outcomes are in comparison.json.

The settled fixture prevents a pending installer from replacing the intended
test. It is not a fix for the earlier installation failure. All launched attempts
are closed and collected once. Never relaunch or overwrite them. Immutable seeds
and raw disk/data/hive evidence remain private.

## Coverage and limits

Four rounds of13 files each use18 observed append lengths totaling1635 bytes.
Prefixes cover512-byte,4096-byte and65536-byte boundaries, including270225:
the actual220-byte warning crosses the same111/109 page split. Per mode there
are168 sector-crossing writes,20 page-crossing writes and8 cluster-crossing
writes. The independent coverage report identifies **zero cases that free a
cluster when truncating the35-byte mapping allowance**. That is an explicit
remaining gap. The test also has no concurrent mapped writer or volume flusher.

Both flush variants produce correct ordinary-shutdown output. This does not
establish equal durability under interruption, that explicit flushing is
unnecessary, or the cause of the physical111-byte non-ASCII span. Intentional-stop
splits, actual SetupAPI debugger observations and these ordinary synthetic
regressions remain separate evidence classes.

Build/import/compiler identities are in build-review.json; preflight.json pins
each run's exact harness/source. Earlier harnesses are in mode0/source and
mode0b/source. verify-evidence.py checks source/raw payload/hive/disk pins and
preserves failed outcomes. compare.py verifies the matched pair; evidence
consistency is not equivalent to strict qualification.
