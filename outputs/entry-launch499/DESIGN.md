# 499 private XBE integration of the tested early-entry gate

Exact497 is the parent. Its private payload and every original instruction keep
their addresses and bytes. Four old receipt path literals change to XWNBoot499a.
The new gate is appended after the original image and the XBE header entry field
points there. On success the tested gate jumps to original _start at 0x11100.
Original flags capture and refusal/preparation/privileged loader code are intact.
The added gate's only path change from executed498 entry.S is 498a to 499a.

The header changes are limited to image size, entry address, section virtual/raw
sizes and section SHA1. A single existing writable/executable section covers the
appended text and static data. No extra kernel imports, driver, mode, mapping or
interrupt changes are introduced. Kernel-file thunks remain at their old addresses.
All actual compiler/tool/source inputs and resolved dynamic dependencies are pinned
before compilation and rechecked afterward. Private input copies preserve them.

The independent reviewer parses both ELF32 symbol/relocation tables itself,
resolves every R_386_32/R_386_PC32 in a separately assembled copy of the tested
gate, and compares the resulting text/data with actual XBE bytes. It independently
checks section extents, encoded entry address, SHA1, all original prefix bytes
(except the explicit header fields and four paths), and the five new owned paths.
No changed original instruction or shifted original text symbol is permitted.

review001 checked 989 corruptions, but mutations in appended data/code could be
rejected by the outer SHA1 before exercising relocation checks. review002 retains
the same validator and recomputes the section SHA1 after each content mutation;
all 989 are still rejected. Both originals are preserved. Only002 establishes
that content corruption cannot pass merely by repairing the outer section hash.

The build record's header_allowed_ranges field is an imprecise min/max summary;
it is not the admission predicate. Both builder and independent reviewer enforce
the five exact field/range changes. actual_header_changes retains the real bytes.

This candidate has NOT executed. The gate was tested in498 with actual Linux i386
execution and modeled NT calls. Relocation/extent checks do not prove Xbox loading,
kernel I/O or preservation of actual privileged context. Early I/O and the larger
XBE may perturb timing/memory/cache behavior; this is a diagnostic intervention.
A complete entry receipt proves neither final close nor Windows boot. Missing
receipt is still ambiguous. No stable-boot or D3D qualification follows.

Before any launch, implement and host-test a NEW controller and provenance-aware
entry collection. Preserve the pending497 screen observation independently.
No temporary startup hook is needed solely for entry collection. This binary
continues the old boot path on success, so an eventual physical plan must explicitly
handle Windows remaining at the desktop, rather than invent an automatic restart.
One SITE with20s reply bound; no accepted/uncertain retry; bounded observation and
full paired cold collection whenever dashboard returns. Dashboard C remains off
limits and 720p/ordinary launcher/startup remain protected.
