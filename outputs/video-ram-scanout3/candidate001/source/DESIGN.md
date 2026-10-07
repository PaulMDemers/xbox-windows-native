# Loader identity and exact resident text

Two earlier diagnostic failures remain intact: video-ram-scanout assumed a stale
kernel base; video-ram-scanout2 discovered the correct823e0000 live kernel and
xwnram loader record, then got GDB E14 while reading the display PE header. It
captured no pixels and tore down/resumed. No display-driver change follows.

This NEW child retains identical binaries/probe. Kernel discovery/header checks
are unchanged. For xwnram only, an E14 header read is recorded as unavailable;
a readable mismatching header still fails. Identity must instead match the live
loader name/base/image size, five exact relocated function prefixes AND every
byte of the resident .text section against the owned hash-pinned PE. A missing
or different code byte still fails; no page is faulted in or modified by the
observer. Kernel/probe headers and code pins remain mandatory.

The identity method is explicitly changed in response to observed header-read
failure, not silently relaxed. It strengthens code coverage while distinguishing
unavailable header data from a mismatch. Twelve physical-framebuffer pattern
comparisons,600second bound, full breakpoint teardown, normal workload/shutdown,
strict cold/event/config/pagefile gates are unchanged. No physical access, driver
patch, cache/mode/device-policy change or performance claim.
