# 678 Host-only full-firmware timer integration

The unchanged 675 probe now links into a fresh full firmware build based on the
retained 674 source tree. Its only export-route change is to call `terminal675`
after the existing post-capture interrupt freeze, RAM copy and packet encoding.
The old entry indicator and network terminal are not called on this route.
All original capture fields and the encoded packet remain separate from the
new probe record. Earlier capture observations are not made atomic retroactively.

`build001.json` pins the parent/new trees, compiler, sources, identity and private
artifacts. The build succeeded under the build lease. Nineteen existing objects
have identical `.text` and `.rodata` sections, including display initialization,
timer, SMC, encoder, bridge, transport, CPU and reset components.

`entry001.json` passes 25 fresh isolated full-image function executions, with
actual compiled export/bridge/codec/probe/hold code and explicit synthetic I/O:

- IF-set/clear entry, successful/unsupported/failed display results;
- advancing, slow, frozen, backward, jumping, 32-bit wrapping and hypothetical
  24-bit wrapping clocks (the latter is not evidence of Xbox counter width);
- IF corruption after entry or timer, export reentry, corrupted freeze flags
  and invalid codec identity;
- busy, pending and error SMC results at each of three transactions.

All fixtures preserve source capture bytes and terminate at CLI/HLT. Where
encoding completes, both 772-byte packet copies match an independent CRC oracle
and remain in prepared state with no send. Reentry adds no I/O and preserves
records. No sender, old entry indicator, PCI or NIC operation is admitted by the
harness. Raw timer prefixes, counts, last values and errors match each model.
The frozen-clock case stops at 200,001 reads. No LED-off mask is requested.

`review001.json` passes 313 provenance, layout and instruction checks, including
record separation, BSS bounds, exact unchanged object sections, call order and
absence of IF-enabling/reset/allocator/sender operations in the probe route.

## Boundary

This is host-only function evidence, not an emulated boot or physical result.
The private XBE has not been staged or launched. The timer, SMC waiting behavior,
network admission and functional drivers are not repaired or relaxed. An SMC
operation that requires a wait still fails closed; physical indicator viability
remains unknown. In-memory samples are tested here but are not remotely retrieved
by this timer-only route. No UDP is expected.

Physical 674 remains zero datagrams, late lights-off/black observation and manual
reset, with no identified timer/SMC/NIC cause. Console last known dashboard674,
no owned startup hook. No hardware contact occurred in 677/678. Installed720p,
ordinary startup, XBOX480, releases and private256 remain unchanged.

Private output: `C:/xwn678/build001`; source:
`/home/paul/xbox-windows-native/timer678-source001`. Owned build and fixture
processes finished; build lease released. See [NEXT](NEXT.md) for physical gates.
