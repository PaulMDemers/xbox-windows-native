# Inventory scanner 421

The corrected ordinary scanner saved a complete schema-2 report on the physical
development console and dashboard FTP returned. One automatic launch was sent at
23:18:36.802 UTC on October 16, 2026; the first successful dashboard observation
with the new report was at 23:19:19.586 UTC. Collection completed at 23:19:27 UTC.
No further launch or collection is needed for this closed attempt.

## Failure and change

The preceding 420 diagnostic failed, as reported by the user: black screen and
manual restart. Its preserved 896-byte trace contains 28 records and ends just
before PCI ID query bus 0, device 0, function 1. The preceding function-0 ID and
class reads completed. Pinned ReactOS commit
7c35fc4ead884e1bd0640a9613f652c40bca8b2e explicitly documents that configuration
queries to 0:0:1 and 0:0:2 hang an Xbox, and that bus-1 device numbers alias the GPU.
The raw trace alone cannot exclude a failed following trace write, but its stop
location, documented hazard and successful corrected run strongly agree.

The original MIT policy now omits those two hazardous locations and bus-1 devices
1 through 31. This expresses documented hardware constraints; no ReactOS function
was copied. It allows 262 of the prior 512 query locations. Excluded locations are
unprobed, not fabricated absent devices. Raw responding function aliases remain
in the report; the record count is not the number of independent devices.

The ordinary source has no 420 trace instrumentation. Schema 2 explicitly records
`pci_scan_policy: xbox-safe-v1`; the host decoder enforces its excluded locations.
Schema 1 remains readable only for historical evidence. The decoded summary calls
the count `pci_response_records`. Legacy binary and failed attempts remain preserved.

## Build and verification

- nxdk revision 58427c078b4ccb0121f359b6b6c536b3b2914976, pinned prebuilt libraries;
  no SDK modifications or full SDK rebuild. Only inherited edata merge warning.
- XBE: 110592 bytes, SHA-256
  `f9163c73c3baa556c80138e122dbc81fe9aec77bd7ec3d951ec9fd9ad0778d5d`.
  Private build: E:/xwn421/build001. Source/library/tool pins are in build001.json.
- The actual policy header passed 524 ASan/UBSan checks covering all 512 old
  locations, excluded-call prevention and out-of-range inputs. Five Python
  report-validator tests passed, including policy violations and missing fields.
- Fresh unused blank 8 GiB emulator child at C:/xwn421/emu001, private EEPROM,
  owned lease and unique ports; no executed runtime parent. Closed exit 0,
  no fallback. Cold report valid, 12 responding records; full E allocation has
  3 directories, 1 file, 4 owned clusters, zero errors/orphans. QCOW checks and
  EEPROM equality passed. Absolute byte 1540 changed outside E, preserving the
  existing strict whole-disk equality failure; no gate was waived.

## Physical scope

Only E:/Applications/XWNInfo421/default.xbe was staged, read back and launched.
The new 5353-byte E:/xwn-report-00.json was retrieved twice with identical bytes,
SHA-256 `0cfa10dd4caf622d7a5c72611d2860977ec781d1d1016cf19f7d0caa1256fa2c`.
It reports kernel 1.0.4034.1, 16384 pages/64 MiB, Conexant response, AV pack 4,
and enumerated 480-, 720- and 1080-line modes. Mode enumeration is not display
quality or Windows compatibility qualification.

All selected Windows/boot files, old inventory binaries and the 420 trace remain
byte-identical. Console C was not accessed. This was not a Windows boot, full
physical disk audit, user-observed display check, or qualification of other Xbox
revisions. The 416 loader candidate remains inactive; the E/720p demo is unchanged.

All owned build, emulator and physical-observer processes are closed. The next
tester artifact is a corrected utilities preview with this binary, matching
source, notices and host validator. Windows clean-assembly/boot-chain validation
and the separate 1080i scanout investigation remain open.

## Corrected tester archive

`E:/xwn421/xwn-utilities-preview-421.zip` contains 2247 files and 324 directories,
7208064 compressed bytes. SHA-256 `24a52f961bddd1911dcf7003a606b8b5c997ebd90a0c275a3a21d2e0c942011d`. Archive and staging tree were
readback-verified. Matching source/header, SDK notices, host validators and current
instructions are included. Only binary member is the corrected inventory XBE;
selected credential-pattern checks found no matches. This is not a Windows kit
or a public release upload. The manifest conservatively retains the experimental
qualification label; the README records the one-console result and its limits.
