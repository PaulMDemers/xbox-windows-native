# Native XID evidence transport

The human authorized continuation after USB220 captured the real FFFF:FFFF
configuration. The missing evidence is the vendor XID descriptor and interrupt
input bytes. This program runs as an nxdk XBE from a unique E: application
directory. It is not a Windows driver and provides no NT5 input-support claim.
No Windows service, binding, startup, registry, HAL or protected binary changes
are needed. Its sole writable file is D:\xid.log, beside that E: executable.

The native USB core performs ordinary enumeration and selects configuration 1.
The authored interface driver requires FFFF:FFFF, class 58/42/00, alternate 0,
two 32-byte interrupt endpoints at interval 4, IN 81/82 and OUT 02. The emulator
build additionally accepts Microsoft's modeled 045e:0202 device. Both raw device
and configuration descriptors are recorded. It requests 16 bytes using
bmRequestType C1, bRequest 06, wValue 4200, and the actual interface number.
A successful, complete 16-byte XID game-controller descriptor is required.
The program submits no vendor OUT, rumble, or interrupt OUT request.

A single 32-byte interrupt-IN request is outstanding at a time. The program
records the returned length/status and all received bytes, at most 2250 reports,
45 seconds, and 1 MiB of log data. Idle NAKs can last until the session deadline.
Twenty-byte reports with their 00/14 header are decoded separately; unfamiliar
data is retained rather than silently assigned a standard gamepad meaning.
The user can exercise controls during the on-screen capture. Idle reports alone
cannot establish physical button/stick mapping.

## Lifetime review

The installed nxdk commit is 58427c078b4ccb0121f359b6b6c536b3b2914976 and its
libusbohci submodule is 6a0c5fefbcd9db53f4a27ee10df99f93d5bce745. The installed
SDK is unchanged. prepare-build.py copies two library sources into each private
build directory and applies two narrowly checked changes:

1. usbh_ctrl_xfer previously freed its UTR immediately after quit_xfer. OHCI
   removal is deferred to a start-of-frame interrupt. Wait for bIsTransferDone
   for up to a further second before freeing. If it does not complete, retain
   memory and invoke the application's firmware-reboot guard.
2. The OHCI removal walk previously treated its dummy tail TD as a submitted
   request. Detect the recorded TailP before consulting/decrementing the UTR;
   release the dummy TD without delivering a second completion.

The application keeps its transfer, DMA buffer and native USB pool alive until
firmware reboot. After selecting its one target it stops topology polling;
interface/device objects therefore remain pinned even if the plug is pulled.
A pending input request is cancelled only at the session deadline, then drained
for up to one second. A missing drain records a guard failure and reboots while
memory remains allocated. The application never unloads the USB core, retries a
connection, reuses an undrained transfer, or frees a buffer from a completion.
All file I/O occurs in the application thread, not an interrupt callback.
This single-session design is not a general removable-device driver.

The linked map must resolve control and interrupt entry points to the guarded
core object and ohci_driver to the guarded OHCI object. The authored application
compiles with warnings as errors. Five existing warnings in the copied upstream
sources remain documented; no claim that the entire dependency is warning-free.

Host fault tests compile the actual guarded control function with deterministic
submit/completion/cancel faults. They do not establish real IRQ timing. Native
emulator execution, dashboard return and cold disk inspection remain separate
gates before a hardware attempt. No hardware launch is inferred from elapsed
time, and no closed hardware220 ticket may be reused.

## Sources and licensing

- [nxdk](https://github.com/XboxDev/nxdk/tree/58427c078b4ccb0121f359b6b6c536b3b2914976)
  supplies the existing native runtime and USB integration.
- [libusbohci](https://github.com/XboxDev/libusbohci/tree/6a0c5fefbcd9db53f4a27ee10df99f93d5bce745)
  core sources retain their Apache-2.0 headers in private build copies.
- The installed xid_driver.h/c (MIT, Ryan Wendland) is the protocol/structure
  reference; the application does not use its convenience queue or rumble API.
- USB207's pinned xemu XID sources provide model expectations, never physical
  evidence. The physical USB220 endpoint is 81, unlike xemu's 82.
- [Microsoft URBs](https://learn.microsoft.com/en-us/windows-hardware/drivers/usbcon/communicating-with-a-usb-device)
  describes the separate WDM transport needed for a later NT5 driver. That driver
  is not implemented by this native capture utility.

Authored application and host harness files carry their own project provenance.
Copied upstream library sources and compiled binaries remain private artifacts;
the exact transformation and hashes are versioned. No third-party driver is
represented as original project source.
