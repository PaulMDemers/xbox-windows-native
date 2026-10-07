# Disposable crash-write and separate recovery protocol

Prerequisite: dump-map-trace/trace001 is closed and verifies the actual returned
and retained NT5 mapping against the cold FAT oracle. This kit is emulator-only.
Its intentional crash is a separate protocol, never an ordinary clean-shutdown
PASS. The physical baseline, release archives and prior run disks are untouched.

A tiny demand-start driver exposes one exclusive device. A private buffered
IOCTL requires an exact 16-byte cookie and write access before calling
KeBugCheckEx with code E058D103 and four fixed identifying parameters. No other
operation crashes. It contains no disk-writing code. The standalone user helper
creates a CREATE_NEW guard, flushes a durable intent log, checks enabled3 dump
configuration, starts the demand service, opens the exact device, waits and
issues the cookie once. An existing guard or any failure aborts. Normal reboot
must not silently repeat the trigger.

Each new child pins source, binaries, fixture/backing chain, inherited device
policy and dump settings. The existing0103 FATX/0102 HAL/video0093 remain exact.
The crash runner omits StopOnBugcheck. A bounded observer pins the actual kernel,
trigger driver and storage modules, records the intended KeBugCheckEx arguments,
pairs IoWriteCrashDump entry/return, and captures the final dump status/context.
It removes every breakpoint, resumes, allows final screen output, then requests
owned runner cleanup. ATA/block writes are traced to distinguish high-LBA writes
from truncated addresses. A timeout or unexpected crash is a retained failure.

The closed crash image is immutable evidence. Cold inspection compares pagefile
bytes, the expected 64KiB extent and its 28-bit-LBA alias, and audits allocation,
protected binaries and hives. A clean allocation does not excuse a wrong dump
address or failed write. A later NEW recovery overlay may restore normal startup
and boot once to capture dump recovery, using unique records and no autorun of
the crash driver. It must preserve the original crash image. No recovery launch
is implied merely by completing preparation; inspect the crash result first.

No dump-policy disabling, service/event suppression, fake successful completion
or speculative filesystem/miniport patch is permitted. Any deliberately induced
crash events are reported under this explicit protocol, not removed from an
ordinary strict event audit. Actual dump writing and recovery remain separate
qualification claims. C: keeps the unchanged20GiB build guard.
