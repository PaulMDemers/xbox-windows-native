# Isolate active data address while retaining image layout

Apply515's reviewed static relocation to an exact510 child. Copy the nine owned
retained source files privately, changing only five510-to516 namespace literals.
Keep the existing entry510_trampoline symbol/name/address. Add `-Tdata 0x94c20`
to the pinned link. Preserve the original XBE header and embedded payload, merge
the newly linked code/data, retain the original old data tail and remaining gap,
and regenerate the section SHA1. Do not deploy the ELF intermediate.

There are two independent checks: candidate.prepare reconstructs the original
ELF object and composes an expected image; candidate.validate normalizes only
the five active names and then invokes515's inverse pointer normalization to
compare every original byte. Review001 reconstructs the ACTUAL new object/link,
compares symbols and nine sources, independently decodes the changed instruction
operands with pinned objdump, and verifies the complete built XBE. A pass is a
binary/static contract only. It is not a dynamic address-ownership proof.

The first non-stack memory access in entry503_gate now addresses state94d10.
The original stack saving, DF clearing, one-shot transitions, file/LED calls,
deadline behavior, restore attempt and firmware return remain unchanged. No
page-table, interrupt, cache, ownership, pending-state or driver patch is made.
The old95000 data bytes remain in the image but no static diagnostic reference
points there. Entry516's actual full observer must reject stale95000 captures
and old510 paths rather than accepting an old helper's modeled success.

RWX intermediate warning: recorded in build001 and explicitly reviewed against
actual ELF program headers and the unchanged final XBE section flags7. No
warning-suppression option was added. This change makes no security/release claim.
Proprietary payload and full binaries remain private; upstream source licensing
is retained, and the new orchestration/review code is MIT.
