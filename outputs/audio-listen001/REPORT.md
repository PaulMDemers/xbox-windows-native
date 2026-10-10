# Xbox analog audio listening result

The user heard the Windows login sound through speakers connected to the
composite cable audio connectors. The unchanged build004 driver also passed
genuine installation and a subsequent twelve-cycle playback/reset test on the
physical Xbox. The captured incoming baseline has been restored and verified.

## What the evidence establishes

| Evidence | Result |
| --- | --- |
| User listening observation | Windows login sound heard during installation; reboot observed. |
| Genuine installation | Exact ACI device, SetupAPI success, xwnaci207 binding, problem 0. |
| Subsequent playback boot | xwnaci207 loaded, legacy module absent, twelve cycles passed; eight full 96,000-sample plays and four reset-shortened plays. |
| Shutdown | Joined helpers, unforced restart, one new EventLog6006 and dashboard return on each Windows boot. |
| Cold integrity | Five hives, protected bytes, event/setup history and policy checks passed on both boots. |
| Allocation | Before Windows, after installation, after playback and after restoration: zero errors/orphans. |
| Restoration | 1202 readback checks; 11 changed files restored and 3 exact new files removed after preservation. |
| Strict whole-boot qualification | FAIL: Ftdisk49 on both Windows boots; never waived. |

The listening observation is separate from the driver's runtime evidence.
The login sound occurred with build004 staged under the incoming legacy filename,
before or during the genuine SetupAPI installation; the subsequent playback boot
independently verified xwnaci207 service and module ownership.

No user observation of the dedicated tone pattern was received before closure. Correct left/right routing and measured signal quality remain unverified.

No instrumented audio capture was made. APU, digital/S/PDIF/HDMI output, capture,
hardware mixer controls, protected content and suspend/resume remain unqualified.
Known unrelated wizard cancellation means these were not prompt-free boot tests.
Later emulator storage failures remain separate unresolved evidence; these
bounded physical results do not establish general repeated-boot storage safety.

## Candidate and rollback

Driver version 0.0.4.207, SHA256
`c5736457d9f4b7c6dafc730eb19bc0eda6c6820cee8e21580d357708df36cd75`.
Source/package commit `7cdb191bd2ef72e24001370726f97a7383a7250b`.
No driver, helper, HAL, kernel, video or APU implementation changes were made.

A fresh capture saved and double-read 1,223 actual incoming files. The five
hives passed traversal and header checks; 11 actual providers and three native
export tables passed. The fresh capture, rather than an older trial's registry,
was used for restoration. Original startup, hives/companions, INF and audio files
are restored. Event and SetupAPI history are retained.

New inactive evidence directories are /F/xwnaL01i, /F/xwnaL01p and
/E/Applications/XWNAL01scanB, scanI, scanP, scanR (each with the XWNAL01 prefix).
Normal startup invokes none of them. Original0088, physical FATX0101/video0093,
immutable0.1.0 and prior closed evidence were preserved.

## Records

- [User observation](user-observation001.json)
- [Installation audit](install001/audit.json)
- [Playback audit](playback001/audit.json)
- [Restoration](restored001/restoration.json) and [final confirmation](restored001/confirmation.json)
- [Review and evidence hashes](review001.json)
- [Controller provenance](controller-provenance.json) and [frozen inputs](frozen001.json)
- [Successor ticket closure](queue-close.json)

The new audio-listen001 ticket is closed after verified restoration and dashboard
return. No active physical session remains. The original hardware220 ticket was
never reopened. This test did not permanently install the candidate or promote a
combined device/video fixture.
