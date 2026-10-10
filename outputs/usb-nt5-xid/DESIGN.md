# NT5 XID input candidate

This original WDM HID minidriver targets the existing Windows 2000 SP4 USB and
HID providers. It does not replace openhci, usbd, usbhub, hidclass or hidparse.
The initial package binds only the emulator's 045e:0202 device. Physical
FFFF:FFFF binding is deliberately a separate qualification/package step.

One passive system thread reads a 32-byte interrupt buffer. Configuration and
vendor descriptors must match the captured XID type 1/subtype 1 contract; the
input endpoint is taken from the validated configuration, not hard-coded.
The existing tested wire decoder supplies four signed stick axes, eight digital
bits and eight pressure bytes. The HID adapter exposes 14 buttons (the eight
digital bits followed by six pressure-button booleans), four signed axes, and
two independent unsigned trigger axes. No rumble or output reports exist.
Mapping is provisional until an attended physical control test.

HIDCLASS polls a cached report. Start requires an actual valid USB sample;
there is no fabricated initial neutral report. Empty or malformed successful
transfers never change the cache. One read is outstanding at a time. The read
deadline is 100 ms; a timeout cancels the IRP and waits for its real completion
before freeing it or reusing its URB/buffer. A broken lower driver can therefore
hold stop/removal indefinitely; memory safety takes precedence over pretending
cancellation drained. The emulator owner supplies an external watchdog.

The worker is joined before stop, surprise removal, removal, device power-down
or unconfiguration. A passive mutex serializes PnP and queued device-power work.
Short HID cache reads use a spin lock; dispatches hold an NT5 remove lock.
Device power IRPs run in a work item because dispatch may occur at DISPATCH_LEVEL.
D0 is forwarded before restarting USB; departure from D0 quiesces USB first.
System power is forwarded through PoCallDriver. Query-stop/remove is vetoed while
started in this experimental candidate; mandatory stop/remove is implemented.
HIDCLASS owns attachment and deletion of the FDO.

The bundled Mingw DDK hidclass.h explicitly labels its minidriver IOCTL values
incorrect, and has no hidport.h. nt5hid.h therefore declares only the documented
HID minidriver ABI with i386 size assertions, cross-checked against the pinned
ReactOS header and the Microsoft contracts below. No XBCD implementation or its
third-party remove-lock code is incorporated. Kernel imports must resolve in the
actual preserved NT5 providers before any guest boot.

References:
- https://learn.microsoft.com/en-us/windows-hardware/drivers/hid/minidriver-operations
- https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/hidport/nf-hidport-hidregisterminidriver
- https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/hidport/ni-hidport-ioctl_hid_read_report
- https://learn.microsoft.com/en-us/windows-hardware/drivers/usbcon/communicating-with-a-usb-device

This is development work. Compilation and host checks do not qualify NT5 runtime,
physical input, suspend/resume, unplug timing, or storage persistence.
