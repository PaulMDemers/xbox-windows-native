# Function ownership and integration

The two physical "PCI Device" dialogs are different functions. Identification
comes from pinned physical189 hives and newdev command lines, not their labels.

| PCI BDF | ID and class | Classification | Workstream |
|---|---|---|---|
| 0:1.1 | 10DE:01B4,0C0500 | MCPX SMBus controller | PCI207 |
| 0:6.1 | 10DE:01C1,070300 | nForce AC'97 modem function | PCI inventory; audio/codec overlap |
| 0:6.0 | 10DE:01B1,040100 | ACI audio codec interface | Audio |
| 0:5.0 | 10DE:01B0,040100 | APU multimedia audio | Audio |
| 0:2.0 and0:3.0 | 10DE:01C2,0C0310 | OHCI USB controllers | USB |

Linux intel8x0m explicitly matches01C1 and tests AC'97 modem codec-ready bits.
That establishes function identity, not codec presence on this Xbox. No physical
register dump proving modem codec availability was found in the pinned189 hives.
xemu's actual paused PCI configuration returned FFFFFFFF at0:6.1 in model001;
its model implements ACI0:6.0 only. Supporting01C1 cannot be validated by assigning
a service to a stale registry node, substituting1B36:0005 or inventing a device.

The installed oem1.inf matches01B1 only. No audio/USB package or their bindings
were edited. The coordinator can inspect this file/branch to coordinate the shared
AC'97 link, semaphore and codec reset resources before any01C1 implementation.
No inter-chat messages were sent.

SMBus also overlaps HAL reboot ownership and video encoder access. PCI207's
restricted telemetry reads avoid encoder writes, power/fan control, EEPROM and
SMC read-to-clear interrupts. Real resource assignment, shutdown quiescence and
HAL address compatibility remain promotion gates, not assumptions from qtest.
