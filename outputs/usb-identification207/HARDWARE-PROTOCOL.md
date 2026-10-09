# Physical collection protocol — coordinator only

This is a read-only diagnostic candidate, NOT a gamepad driver. Read the final
build/runtime review before scheduling. This chat performs no console access.

1. Use a new trial identity and confirm the current coordinator-owned baseline
   through fresh readback. Preserve original startup, SYSTEM/SOFTWARE/default/
   SAM/SECURITY, events, SetupAPI and the current loader/HAL/FATX/video/network/
   USB/HID binaries, including openhci/usbd/usbhub/HidUsb/hidclass/hidparse/
   kbdhid/mouhid. Record exact paths and hashes. No use of an old rollback as a
   substitute for the actual current contents; baseline may evolve during video work.
2. Verify the output directory is absent. Stage only reviewed usbprobe.exe to
   a unique F: directory; read back its binary hash. The executable derives its
   output directory from its own path and uses CREATE_NEW for usb.log. Do not
   reuse a directory containing a previous log or overwrite a failed attempt.
3. Have the coordinator's established boot runner invoke the probe at its actual
   C: path once. Preserve normal startup backup/readback. No service, device,
   INF, signing policy, SYSTEM, or driver deployment is part of this probe.
   Keep the boot keyboard unplugged through Xromwell as always. Retain the
   controller and mouse in their observed ports for the first capture.
4. Record displayed device/wizard state without cancelling unknown windows or
   declaring installation complete. The probe's own requests are bounded but
   an external deadline is still necessary for a stuck kernel open/cancel/exit.
   Do not force reboot from this helper or hide setup failures. The coordinator
   controls the normal restart/collection protocol and records any manual action.
5. After return, restore normal startup FIRST, preserve usb.log and before/after
   hives/events/SetupAPI/providers, and compare exact protected hashes and typed
   binding deltas. Parse the complete probe log, retain failed IOCTLs and any
   malformed descriptor. A partial log, timeout or missing port is not PASS.
6. Confirm live parent links and connection status for the FFFF:FFFF device;
   compare the device descriptor's actual VID/PID/bcdDevice, all configuration
   interfaces and interrupt endpoints against persisted class58/42/00 metadata.
   Do not synthesize a manufacturer/product or change IDs to match an INF.
7. Subsequent physical input/report capture requires a separately reviewed
   transport/minidriver; the standard hub API cannot issue the vendor XID
   descriptor request. Do not interpret a standard-request failure as proof
   the controller is broken. No gamepad input or rumble claim follows this probe.

Rollback: restore the exact startup bytes and verify baseline hashes. Since
this package changes no driver, binding or registry value, it has no driver
rollback operation. Preserve the unique directory/log as evidence. If Windows
cannot return normally, use the coordinator's existing recovery procedure;
record that as a failed trial, never relaunch automatically.

Readiness: build007 passed actual NT5 import/ABI review and emu003 captured
device/configuration descriptors for XID, HID keyboard and HID mouse. The one
failed IOCTL was the unbound XID child's absent driver key (error2); retain and
explain such failures rather than requiring a zero-failure count for an unbound
device. A failed descriptor query, truncated log or unexplained omission fails
collection. Collector exit2 indicates a recorded query failure, not necessarily
a crash; inspect the complete log. Emu003 took27.210s and made36 requests.

The screenshots were visibly scrambled and do not qualify input or display.
The diagnostic run used monitor pause/resume and host termination; it does not
qualify ordinary boot or shutdown. Timeout/cancellation failure paths were
reviewed in source but not fault-injected. The package is ready for a controlled
physical descriptor collection trial, not physical driver deployment. The
physical controller's vendor XID descriptor and raw reports remain unavailable.
