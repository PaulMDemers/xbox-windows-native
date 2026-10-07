# Live-address scanout diagnostic

The prior video-ram-scanout attempt is preserved as a failed observer: its fixed
kernel base from an earlier run did not yield a valid module list, so it captured
zero pixel frames, removed its breakpoint and resumed. No driver change follows.
This NEW child uses identical compiled display and probe binaries and fresh disk
inputs. Never reuse the old child or recollect its results.

At the first probe checkpoint, discover_kernel.py reads the live IDT location,
decodes vector0 and vector2e gates, subtracts the pinned kernel's KiTrap00 and
KiSystemService RVAs, requires both bases to agree, and verifies MZ/PE timestamp
and image size before walking modules. No historical load-address guess is used.
Discovery was replayed against an older closed RAM snapshot and agreed with its
independent page-table/image search:823e0000. That is a host replay, not the
new guest's base. Record and pin the actual new runtime result separately.

The rest of the bounded diagnostic is unchanged: twelve physical03c00000 frame
snapshots, client coordinates from the guest API, cursor outside the test area,
allRGBpixels compared with a host-computed pattern, actual probe/display/kernel
code pins, complete breakpoint teardown/resume, then normal restart and full
strict cold/event gates. Diagnostic timings do not qualify ordinary performance.
This covers two copy paths at two sizes; wider DDI/cursor/mode/crash tests remain.
