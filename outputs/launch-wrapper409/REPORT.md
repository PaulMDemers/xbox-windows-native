# 409 closeout: A and B allocation results match

The user reported B reached the Xbox logo, went black and returned to the
dashboard. This is the diagnostic's intended return path; it does not start
Windows. B was collected once at 2026-10-16 00:59:02 UTC. Both 80-byte reports
are identical except the two attempt-cookie bytes. All decoded allocation
addresses, statuses, sizes and flags match. Each attempt passed 62 protected
file checks; B's diagnostic and owner also remain exact. No console writes or
C access occurred during collection.

See manual-user-return002.json, manual-collection002.json and pair-review002.json.
The original failed decoder and prior pending-B final-review remain unchanged.
This pair does not reproduce the original launch failure, establish a route
cause, or validate the later relocation/paging/handoff. Neither attempt should
be rerun. The next source review concerns that later boundary.

## Historical report before B collection

# 409: physical allocation prefix succeeded; paired manual observation pending

One physical FTP diagnostic launch was accepted at 2026-10-16 00:45:44 UTC.
UnleashX returned with an exact 80-byte report by 00:46:06; collection closed
00:46:16. All sampled protected files, Startup, SYSTEM/SOFTWARE hives and event
logs remained byte-exact. No Windows boot or event/shutdown claim is made.
Dashboard C was not accessed. Original launcher/drivers/settings are unchanged.

Actual record: payload VA81f00000/PA01f00000, loader VA82000000/PA02000000,
virtual alias02000000, NtAllocateVirtualMemory status0/size4096, payload288316
bytes. Entry EFLAGS246 and pre-copy206 both have DF clear. This diagnostic
entered the wrapper, performed both allocations and the virtual mapping, and
returned normally. It does not establish the earlier failure's cause, validate
the later paging/handoff code, or prove reliable Windows boot.

The first decoder rejected the loader page because its base is exactly32MiB.
That failure is preserved in collection001.json and decode.py. A separate
interpretation002 records actual success and the corrected inclusive-start
boundary; the next page is rejected. No failed record was rewritten.

Manual variant004 is staged/readback-verified at
E:/Applications/XWNBoot409b/default.xbe. No host launch was sent for it. It has
the identical instruction layout to build003, with only the new cookie/path
and section digest. The user has been asked to launch it once through File
Explorer and report return. Do not launch it remotely or repeat physical001.

Build003 compiled with pinned GCC12. Two sets of13 actual x86 host executions
qualified its behavior/serialization under modeled kernel calls; host004 also
ran13 cases on the exact paired XBE. Each independent decoder rejected129
malformed/truncated model reports; the actual next-page mutation was rejected.
There was no Xbox emulator run. Physical001 is separate actual hardware evidence.

Preserved failures: build001 included20 padding bytes in its copied-payload
length and was rejected before deployment; build002's generator accidentally
changed its parent build paths and failed before output creation. Both inputs
remain. Build003 uses the actual embedded descriptor. Neither failed build ran.
The data-only variant is not described as a fresh compiler rebuild.

Host storage: four transparent NTFS compression receipts preserve exact full
hashes and paths. One closed flat fixture, ten closed host executables and two
closed captured RAM files were compressed; no backing chain was moved, deleted
or rebased. Capacity rose above the unchanged20GiB build guard before building.
Do not infer a guest integrity change from storage-attribute compression.

The FATX review confirms native create/update reject >42 encoded bytes. The six
clean-install paths contain exact crypto/SID/COM+ names; a host rename/exclusion
cannot solve application lookup/enumeration. Native long-name storage semantics
and crash-safe namespace integration remain unimplemented. No FATX driver or
clean-install exclusion was changed in409, and no public release/tag is ready.
