#717 CLOSED: ORANGE; exact failed check unknown

One launch. User reported Orange; no separate hold or visible blank/return
observation. Manual reset Ready confirmed. Nine preparation files collected once,
double-read and audited. Exact source/binary/report pins, independent alias
ownership, and unrelated entry checks pass. PCI/CRTC/SEQ/geometry/allocation words
match715 and716. This is preparation integrity, not a successful native test.

Orange is shared by bridge refusals and payload errors. The exact bridge/payload
phase, target readback and restoration result remain UNKNOWN. Do not claim
CR1b bit7 is unwritable, mask it, or identify the708/709 fault from this indication.
The retained last file phase handoff_armed is preparation, not a native dump.

Next NEW718 add independently validated optical bridge phase/refusal and payload
result/phase/saved/target/readback/restored values. Preserve the bounded transaction
and disambiguate execution before changing values. No718 build/stage/launch yet.
717 is closed; no rerun/recollection. Console dashboard, no hook/host child.

## Test design and validation

716 left the console at its matched720p baseline. The remaining704 common-setup
CRTC differences are CR1b85->05 and CR22fe->ff. This test selects CR1b only.
Cromwell labels it arbitration0; Linux nouveau identifies it as FIFO control and
writes a calculated burst field there. Neither establishes physical NV2A bit7
semantics. CR22 remains undocumented and is not written. See source-review001.

The candidate keeps the716 kernel preparation, ownership and32KiB native bridge.
It replaces the630 pair with indexed byte CR1b: require85, request05 once, read
full byte, restore saved85 once, read full byte; check pitch5120 and CR11 before
the bounded wait and output restoration. Recheck CR1b afterward. Exact target
readback is required, including bit7; no mask or retry hides a refusal. Only
CR1f unlock, SEQ1 blank/restore, ACPI output pair and CR1b are allowed writes;
indexed selectors are restored. No630, CR19, CR22, encoder, timing, clock or
interrupt programming occurs in the reachable native diagnostic.

The target is immediately restored before visible operation. A successful result
would not qualify sustained05 use, FIFO performance, combined704 setup, the
708/709 black-screen cause, full mode switching or Windows1.6. Models establish
control flow and scope, not actual write semantics or physical output behavior.

GREEN second bar means native0x717. ORANGE can be a bridge refusal or payload error, CYAN is
the pre-call checkpoint. BLACK does not identify a failure instruction. Native
status is optical; saved preparation files ending handoff_armed do not prove
native execution. A held result requires user-observed manual reset and one
collection/audit cycle. No hook or Windows launch is installed.

Host checks passed:131379 ownership, four ASan/UBSan pages,12 CPU instances
(all closed),186 relocated instruction/whole-framebuffer models,23 actual nxdk
page and372 compiled ownership cases. Source and linked byte writes reviewed.
Payload5120 padded9916;17relocations/four absolute.
One SITE accepted2026-10-27T07:04:52.868168+00:00 after exact stage/readback.
User reported ORANGE. Exact bridge/payload phase and error unknown.
Holding and visible blank/return not separately reported. Manual reset Ready
confirmed; collection/audit completed below.
No repeat launch. Previous runtimes remain closed.
