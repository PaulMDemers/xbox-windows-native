# 705: larger native bridge validated on the host

The 32 KiB bridge can carry the 9,916-byte transaction from 704, its own GDT and
IDT, request/result records and an 8 KiB stack. This is host evidence only. No
XBE was built or deployed, and the console was not accessed during this stage.

Use `page002.c`, `bridge.S`, `plan.c` and `build002.json` for the current host
candidate. The retained 704 payload is unchanged. Its 26 internal absolute
relocations are rebased; relative relocations remain unchanged.

## Evidence

- `plan-review002.json`: 131,379 ownership cases, including every page in the
  64 MiB address space in each alias position, separate physical backing pages,
  identity aliases, reservation bounds and allocation overlaps.
- `build002.json`: ASan/UBSan page construction, four placements and 43
  output-preserving rejection cases per placement.
- `cpu-run002.json`: 12 fresh diskless QEMU CPU fixtures. Four mappings reach
  paging-off native context and correctly refuse the PC's PCI hardware. Eight
  malformed/missing-page/corrupted-copy/exception cases stop before the payload.
  Neighbor guards and framebuffer remain unchanged; all VMs are closed.
- `integration001.json`: 30 fresh post-transition model executions exercise
  the exact bridge and relocated transaction at two addresses. Successful paths
  verify all 345,600 pixels and the encoder wire sequence. Failure paths retain
  reblank behavior. PCI refusal paths perform no video transaction. CF8, stack,
  immutable page regions, selectors and protected register state are checked.

The integration model initializes CPU state explicitly; it does not establish
the paging/cache transition. The diskless CPU fixtures establish that transition
in QEMU but do not emulate Xbox display hardware. Neither proves physical mode
initialization, scanout timing or Windows support on revision 1.6.

## Preserved failure

`cpu-run001.json` failed on the identity mapping after its dual mapping passed.
Loading the data selector caused the CPU to set the GDT descriptor's accessed
bit, changing the checked page by 0x100. `page002.c` initializes descriptor
accessed bits to one. Permissions, bases and limits are unchanged. The checksum
was not relaxed. Original page.c, build001, cpu001 and review001 remain intact.

## Physical admission remains open

The bridge's LPC check currently accepts either BAR0 or configuration offset
0x84 equal to 0x8001. Contrary to its comment, that OR condition does not reject
every conflicting pair. It is not a qualified 1.6 PM decode rule. Read-only
inspection of local xemu at e72e76bd1f12ce45c6c63b4196c6918ea2cc705d found BAR0
registration in hw/xbox/acpi_xbox.c and disabled later-revision configuration
handling in hw/xbox/xbox_pci.c. That is model context, not physical evidence.
The initially guessed raw-source lpc.c URL returned 404; it supplied no evidence.

Before a transaction launch, collect the actual PCI/LPC pair, baseline CR11,
CR21, CR44 and preserved VGA state, and test the larger allocations on this
console. Review admission against source and captured values without changing
firmware state to make it pass. The 704 timer/ownership booleans still represent
caller obligations; constructing the request does not discharge them.

The bridge currently holds on an early refusal without rendering a distinct
status. A future launcher must provide bounded observable failure reporting.
The additive checksum is a corruption check, not cryptographic integrity; exact
staging and full-copy comparisons remain required. No physical launch is admitted
by this report. The original 720p installation remains protected.
