# 499 early-entry candidate compiled and independently checked; NEVER launched

Private C:/xwn499/build001/default.xbe is 545,004 bytes, SHA256
22d3a9224965159a53cb188be9530f1b211aff8480d3d5773405d7e2974cf6d9.
Its new entry is 0x94877, success target original0x11100, static record0x95000.
All original instructions and addresses are unchanged. Changes are four owned
receipt paths, five header fields/ranges, and the appended gate/data. The protected
original kernel payload and privileged loader/capture functions remain byte-exact.

Independent ELF relocation review resolves60 actual relocations and compares648
code bytes plus236 data bytes against the XBE. It verifies image/section extents,
entry encoding, section SHA1 and all five unique paths. review002 rejects989
mutations, repairing the outer SHA1 for content mutations before validation.
review001's weaker outer-hash tests are retained separately. No compile failure or
warning occurred. The build metadata's min/max header-range summary is documented
as imprecise; it is not used as a permissive byte-change predicate.

498's199 host assembly cases/1019 transport mutations remain the gate's host
evidence. Actual Xbox kernel services, loading, ring0 context and boot behavior
are untested. A file alone never proves final flush/close or Windows startup.
The new I/O and increased XBE size are interventions, not a functional boot fix.

No staging, FTP access, physical launch, Windows workload hook or SDK/shared-source
modification occurred. All owned build/review processes are closed. 497 stays
closed and its pending user screen observation is unanswered. 496 PC combined
scene PASS remains separate; Xbox combined scene remains unqualified. Ordinary
720p, startup/launcher, dashboard C, releases and all historical failures are intact.
