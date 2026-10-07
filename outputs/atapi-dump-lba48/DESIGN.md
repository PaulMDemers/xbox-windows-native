# Candidate0105: select the existing large-LBA dump routine

The actual pinned Windows2000 ATAPI image bypasses its normal 48-bit selector
when writing a crash dump. The unmodified runtime proof is recorded in
outputs/atapi-dump-address. This correction changes only the dump call site;
ordinary disk I/O functions remain byte-identical.

The owned105-byte assembly selector tail-calls the image's existing extended
PIO routine when the same per-device48-bit flag used by ordinary I/O is set
and the expected extended multiple-write command0x39 is available. Otherwise
it uses the existing legacy routine only when the complete transfer fits
below the28-bit limit. Unsupported or malformed requests return the existing
lower-routine error6, so the dump writer reports failure instead of wrapping.
It does not invent capabilities, change commands or suppress errors.

Scope is the pinned image and WRITE(10) requests on512-byte-sector devices
within its32-bit sector-address limit (2TiB). The upstream writer still uses
a32-bit CDB address; this is not a general256TiB storage implementation.
The existing250GB fixture deliberately places the dump beyond128GiB.

The deterministic transformer requires the exact vendor input hash. It keeps
all old section RVAs and raw offsets, relocations and debug overlay unchanged.
Two contiguous sections with identical nonpaged execute/read flags are merged
to free a section-header slot. The new nonpaged execute/read section contains
only the owned selector. The only pre-existing instruction changed is the
five-byte relative call atRVA1360e. Size/checksum/section headers are updated.
The private transformed binary must not be committed or redistributed;
reproduction uses the user's matching owned input and the published transform.

Host tests execute the exact selector bytes and verify capability, malformed
request, boundary crossing,32-bit overflow, ABI preservation and zero memory
writes. They cannot qualify a guest load or disk write. Require fresh matched
ordinary storage/network tests, then a distinct controlled crash with exact
high-LBA header/wire/write-containment evidence. Preserve the crash image and
boot only a separate recovery child after the address gate passes. No physical
deployment is authorized in this emulator session.
