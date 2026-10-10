# USB XID physical capture

The physical FFFF:FFFF controller returned its vendor XID descriptor and raw interrupt input. It reports XID version 0100, type 1/subtype 1, 20-byte input reports and 6-byte output reports. Raw descriptor: `1042000101011406ffffffffffffffff`. This establishes the wire format; it does not identify an exact controller model or provide Windows gamepad support.

One native launch was accepted at 2026-10-10T18:45:46.692385+00:00. The utility ran from /E/Applications/XWNXid226a, captured for 45 seconds and restarted itself. Owned dashboard return was verified at 18:46:57.906567 UTC. Collection finished at 18:47:06.264053 UTC. Windows was not launched; no service, driver, registry or startup changes were made. No rumble, vendor OUT or interrupt OUT was sent.

## Reports and retained failure

There were 1863 successful USB transfer completions and no reported USB transfer errors. The first completion, at 4 ms, contained **zero bytes**. The remaining 1862 contained valid 20-byte packets beginning 00/14. The original strict parser result remains **false** because that first empty completion is not an XID input packet. It is preserved in physical001-review.json and the raw log; no failure was suppressed or reclassified into a clean-run PASS.

The valid packets contain three distinct states: neutral (1631 packets), left-stick X=-25344/Y=25088 (230), and the same state with right-stick X=-25344 (one). Digital buttons and all eight pressure bytes were zero throughout. No operator readiness or labeled control-action reply was received, so these state changes cannot be assigned to intentional physical actions. Button/trigger mapping and complete stick behavior remain unqualified.

A later input driver must distinguish an empty successful transfer from a valid report, preserve the previous state on empty/malformed input, and parse exactly the returned length. The physical interrupt-IN address is 0x81 with maximum packet size 32; the actual input payload is 20 bytes. The emulator uses 0x82. Neither endpoint nor report length should be substituted from the model.

## Baseline and validation

All 55 selected incoming files were captured before launch and remained byte exact afterward, including normal startup, five primary hives, registry companions, three event logs, SetupAPI, trace, and protected loaders/providers. The config-directory inventory and deployed executable were exact. No restoration writes were needed. This is selected-file readback, not a new full physical allocation scan. Existing Windows event failures remain in their unchanged logs; no clean NT5 boot/shutdown qualification is claimed.

The new usb-xid successor ticket was claimed only after the original audio, USB and PCI tickets were closed. It closed at 2026-10-10T18:48:38.316081+00:00; the original tickets remain unchanged. The console is at the dashboard with its incoming baseline intact.

Emulator emu002 retrieved its XID descriptor and 1864 valid idle reports, returned to dashboard, and passed cold readback of all 30 original fixture files. The private overlay had no F: write extents. That is emulator evidence, not a physical storage audit. Emu001 failed at an unforwarded FTP data port before the native app was launched; its stopped fixture and failure record remain preserved.

Host checks: 406 parser cases, 428 actual guarded-control completion/timeout cases, four actual dummy-tail cancellation-walk cases and six hardware-ticket/launch guards passed. They do not establish hardware IRQ timing or general USB-stack reliability. Both builds passed pinned-source and linker-map review. The authored application compiles with warnings as errors; five existing upstream-source warnings and the existing linker section-merge warning are retained.

## Source and continuation

Build004 physical XBE SHA256: d7bfd483a1a4b9ed700c9f7722575c7bb985ac8ad8fab50610c5dff9c726ca15.
Build003 emulator XBE SHA256: 2b46f3d1760eab555b71e46ff2fd5f4cac387e54f6eba775a78f45143280902b.
Both use authored main.c SHA256 1276d3c50ea7da6e297696e74ef9531524120e805b62c68bd456960ad4be30a2, with only the emulator ID allowlist/build-mode macro differing. See DESIGN.md for exact SDK pins, two private USB-library lifetime fixes, ownership limits and licenses. The installed SDK was unchanged.

Raw logs, decoded samples, rollback snapshots and binaries are private in artifacts/. freeze-capture.json preserves the 28 inputs used for the hardware trial. freeze.json is the post-capture manifest after removing three redundant final blank lines; post-capture-formatting.json verifies identical Python syntax trees and records the private archive of every original frozen input. No executable changed. Use physical001.json and physical001-review.json for the original result. No Windows driver is installed. Next work is a bounded NT5 transport and HID input adapter that accepts the observed 20-byte format, ignores empty completions without inventing input, and is validated first in an owned emulator. Physical control mapping requires an attended, labeled input test.

## Decoder foundation

The original portable C module in driver-core/xid_wire.c now decodes the observed 20-byte report without allocation, I/O or unaligned structure overlays. It returns a distinct NO_DATA result for zero bytes and leaves the last output untouched for empty or invalid input. It passed 66,083 host checks covering all 65,536 signed-axis values, digital fields, pressure bytes, short/long packets, bad headers and null arguments. All 1863 captured physical completions were replayed: 1862 valid decodes and the one empty completion preserved without a state update. This is a tested parsing component, not an installable or runtime-qualified NT5 driver.
