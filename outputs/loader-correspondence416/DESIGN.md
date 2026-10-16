# Reconstruction discriminator

Keep source semantics, selected profile definitions and fresh compiler fixed.
First reproduce the exact original diagnostic source-root spelling AND length;
ReactOS relative-file offsets use root length independently of compiler prefix
mapping. Preserve this first result. If a generated banner differs, use a new
output ID to reproduce its input date/revision metadata and verify the complete
generated header before claiming correspondence. No post-link binary rewriting.

Complete-file comparison allows only parsed COFF timestamp, PE checksum and
export timestamp fields under identical layouts. All other bytes must match.
Reject length, header, code/data, relocation and prepended-stub mutations. Keep
private original Windows material separate from source/report commits.

Host projected reserve:2GiB for the first two builds,1GiB for loader002, each
above the existing20GiB minimum. Fresh source directories and build resource
lease; shared toolchain files verified by receipt. Never rerun consumed IDs.

An inactive stage is not a boot result. The fixed XWNEBoot paths require a
separate activation record with verified original files/rollback. Testing a
copied XBE from another directory alone would still load the original path and
would not qualify the candidate. Any failed or uncertain activation must retain
an exact file-by-file journal and be restored before further tests.
