# 688 early native entry integration — host fixtures closed

The checked reader is now linked into a fresh full Cromwell image. A separate
branch at the beginning of `BootResetAction` captures CPU context and performs
the configuration reads, then halts. It cannot fall through into legacy PCI,
EEPROM, video initialization or Windows. This image was not deployed: its result
was only retained in RAM, without a useful visible indication.

Source review found another earlier SMBus transaction: `BootPciPeripheralInitialization`
sends the SMC audio command `0x0b00` before reading EEPROM. Two fresh executions
of the retained compiled `I2CTransmitWord` show it leaves terminal status behind
under the explicit W1C model; it also accepts combined done/error status. These
are source/model findings, not a physical failure diagnosis. Moving only before
EEPROM would not avoid this earlier transaction.

The new entry captures flags, CR0/3/4 and CS/DS/SS. It refuses IF-set entry,
paging, missing protected mode or unexpected segments. It selects and restores
PCI CF8 while reading the SMBus identity, command and BAR1. Only the expected
NVIDIA SMBus device with I/O enabled at C000 proceeds. The fixed topology and
identity are checked expectations, not a motherboard-revision decoder; see
[reference provenance](pci-reference001.json).

After refusing busy/inherited terminal status, it reads the SMC cable byte, four
video-standard bytes and video flags through687's bounded helper. Only HDTV,
NTSC-M/NTSC-J and enabled480p proceed to a four-byte read at Xcalibur register0.
The response is presence/protocol data, not a unique chip ID. No encoder,
EEPROM, GPU, LED or reset programming occurs in688.

This is **post-BootStartup context**, not untouched kernel context. The unchanged
XBE/assembly path already changes paging, descriptors, cache and MTRRs. These
fixtures do not execute that preceding assembly path or validate its physical
handoff. Clock qualification, GPU setup and the visible pattern remain open.

GCC12 built a fresh XBE from pinned677 tree
`70c0a6c5aff82537f489e7d18410d5980fa797a7`, with a new private integration tree.
27 linked-image fixtures passed: native configuration and block-read success,
CPU/PCI/configuration rejection, busy/dirty entry, errors at all seven reads,
bounded timeouts, short response, final dirty status, and entry-to-halt control
flow. IF and PCI-selector restoration were checked. No emulator or console was
used. Existing build warnings (Makefile recipe overrides, RWX segments and the
Perl Unicode warning) remain in the pinned private logs; build exit was zero.

See [build](build001.json), [compiled fixtures](compiled001.json),
[legacy audio fixtures](audio001.json), [review](review001.json) and
[closure](closure001.json). All invoked fixtures are closed. The ordinary
launcher, manifests and original720p installation are unchanged.

The fresh [689](../xcal-visible689/REPORT.md) adds a success-only LED signal and
records the subsequent physical attempt. Do not launch or rerun688.
