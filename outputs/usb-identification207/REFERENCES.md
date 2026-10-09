# Primary references and provenance

- [Pinned xemu XID model](https://github.com/xemu-project/xemu/blob/e72e76bd1f12ce45c6c63b4196c6918ea2cc705d/hw/xbox/xid-gamepad.c)
  and [XID request handling](https://github.com/xemu-project/xemu/blob/e72e76bd1f12ce45c6c63b4196c6918ea2cc705d/hw/xbox/xid.c).
  LGPL-2.0-or-later. Used to identify the existing emulator model and expected
  descriptors, not copied into the probe. Downloaded bytes independently equal
  build003/candidate-source-pins.json:
  xid.c f196686d75beb555ec5e1158f60aa8f881297d4c1811c53317cf9ba594a749e0;
  xid-gamepad.c a75775c8d4bc8db81dcf29ef149a3107170713d60fa0bb2104dd19694d48a134;
  xid.h 9c5dfac6ca537a7bffe2a226fba64dc3111446b5d76d768d1b6bb17976236965.
- [XBCD source](https://github.com/thundercatsNZ/xbcd/tree/0459aecb020faf85b918680d7dcd5fa49b6b9036/Source%20Code/XBCD%20Driver).
  XBCD.inf includes FFFF:FFFF; XBCD_driver.c is a HID minidriver and cites
  GPL-2.0-or-later. Source audit only. RemoveLock.c has a separate Walter Oney
  copyright and must not be assumed covered by another file's license.
- [Xb2XInput controller list](https://github.com/emoose/Xb2XInput/blob/master/Xb2XInput/XboxController.cpp)
  independently documents FFFF:FFFF as an original Xbox controller ID.
  This is evidence that the ID can be real, not an identification of this unit.
- [Microsoft classic USB connection information IOCTL](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/usbioctl/ni-usbioctl-ioctl_usb_get_node_connection_information)
  supplies cached device descriptor and connection status; available in Windows2000.
- [Microsoft descriptor request](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/usbioctl/ns-usbioctl-_usb_descriptor_request)
  specifies that the stack forces bmRequest=0x80 and bRequest=GET_DESCRIPTOR.
  The probe therefore does NOT pretend this interface can fetch the vendor XID
  descriptor (0xc1,6,0x4200) or raw interrupt reports.
- [Microsoft CancelIo](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-cancelio)
  cancels this thread's requests. Cancellation is asynchronous; retained static
  OVERLAPPED/buffers and completion drain are mandatory. No CancelIoEx import.

Original authored source: probe.c, analyze.py and its framing tests. Existing
project FATX/fixture tools are reused through read-only imports with bytecode
writes disabled. Pinned RosBE2.2.1 i386 compiler and actual NT5 DLL exports are
reviewed by build/review scripts; SDK headers do not establish runtime ABI alone.
