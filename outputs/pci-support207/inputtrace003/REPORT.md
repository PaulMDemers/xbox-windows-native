# Input trace 003: preserved address-assumption failure

The bounded debugger attempt captured no planned breakpoint. It does not
identify an input-port owner. The same immutable veto source, driver, HAL,
installer and helper from rebalance002 were copied without guest changes.

The harness armed the historical kernel base 0x823DF000. The read-only monitor
observations in veto001/address-check001.json show that address inaccessible.
In address-check002.json, the live IDT vector-zero handler minus the pinned
NT5 _KiTrap00 RVA gives 0x82402000; that address contains an MZ header. This
is an address-selection observation, not full loaded-image verification.
Fresh inputtrace004 uses this address and still requires header and relocated
instruction-byte agreement before interpreting a breakpoint.

The 240-second observer deadline expired with zero hits. Breakpoints were
removed and execution resumed. The runner closed the owned emulator at
2026-10-11T00:56:53.441289Z using a bounded host stop, not normal shutdown.
The immutable source remained unchanged. Pipeline001 completed its cold audits.

Resource-only installation, invalid-only HAL probes, target lifecycle and
QUERY_REMOVE/CANCEL_REMOVE recovery passed. Cold E/F allocation, protected
files, five hive formats/checksums/sequences and event/SetupAPI history passed.
F contained 319 directories and 6726 files with no allocation errors/orphans.
One Kbdclass9 and one Mouclass9 retained CREATE / STATUS_SHARING_VIOLATION;
Ftdisk49 also remains. No DHCP1005 recurred. Pending install258 still held
normal restart, and there is no Event6006 or dashboard-return evidence.

All sources and preflight/run/fixture/trace/audit evidence are retained. No
used runtime disk may be relaunched. No functional input/network, SMBus
transaction, terminal takeover, repeated-boot or physical qualification follows.
No physical access or root/other-driver integration occurred.
