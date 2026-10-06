# Emulator device and recorder design

The captured `PCI\VEN_1B36&DEV_0005\...\03` installer targets xemu's generic
PCI test device at bus 0, device 0, function 3. In the exact source revision
`e72e76bd1f12ce45c6c63b4196c6918ea2cc705d`, Xbox machine initialization creates
that device under a memory-controller placeholder comment. It is not an extra
device inserted by the Windows test launcher.

The local machine, PCI-ID and test-device sources match that revision exactly.
`research-device.py` records their hashes and relevant line numbers, and checks
the retained failing emulator executable against its build manifest. The
resource-model patch changes NV2A resources; it does not introduce this device.
The separate existing nvnet patch is preserved by the recorder build.

Primary references:

- [Pinned Xbox machine initialization](https://github.com/xemu-project/xemu/blob/e72e76bd1f12ce45c6c63b4196c6918ea2cc705d/hw/xbox/xbox.c)
- [Pinned test-device implementation](https://github.com/xemu-project/xemu/blob/e72e76bd1f12ce45c6c63b4196c6918ea2cc705d/hw/misc/pci-testdev.c)
- [QEMU PCI IDs](https://www.qemu.org/docs/master/specs/pci-ids.html)
- [QEMU test-device interface](https://www.qemu.org/docs/master/specs/pci-testdev.html)

The test interface provides synthetic MMIO and I/O regions. Its generic PCI
class and ID do not describe a real Xbox memory controller. The recorded Windows
fixture has no matching driver. Neither assigning an NVIDIA ID nor suppressing
the installer would establish hardware fidelity or fix Windows shutdown.
No such model or registry intervention is part of these runs.

## Instrumentation

The opt-in prototype adds TCG helper calls only at eleven reviewed instruction
addresses: PnP create/call return/wait/control boundaries; process resume, exit
and termination; public/internal hard errors; win32k's termination call; and
kernel shutdown. It uses pinned NT5 binaries and the previously observed kernel
base. It is not a generic debugger or a relocation-independent tracer.

At a selected site the helper reads registers, code bytes, current-thread and
process identity, and selected stack data. Page-table walks read only low 64 MiB
physical RAM. They never access MMIO or write guest memory. The owning command
line uses its own process page tables. Nonresident data stays invalid; the
decoder does not interpret fields without valid read flags or matching site
bytes. The helper has no return-value, register, exception or scheduling control.

At most 4,096 fixed-size records are retained in host memory. Host output is
exclusive-created and buffered, flushing at 256-record boundaries, hard-error
and shutdown sites. A full-capacity capture is rejected as incomplete. Host
termination can omit events after the last flush; the kernel-shutdown boundary
must be captured before claiming a complete observation through that boundary.

The build uses the pinned existing toolchain under the build lease, retains the
NV2A resource experiment, and restores all borrowed sources, including the
unchanged pre-existing nvnet modification. It produces a separate executable.
Recording is disabled unless XWN_NATIVE_EVENT_LOG names a fresh local output.

The paired runs use identical seed bytes and the same new executable, first
with recording disabled, then enabled. They retain the same two-minute guest
helper. No GDB attachment, paused memory capture, device removal or manual
installer dismissal is used. Host recording still has overhead; a clean enabled
run would not establish a fix or prove absence of timing effects. Compare cold
events, actual guest timing, installation, hashes, hives and allocation.

The physical console and its popup remain a separate investigation.
