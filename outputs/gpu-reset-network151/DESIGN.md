# Reset networking discriminator

Use fresh control001/candidate001 children and the unchanged build003 executables.
Stage the exact native150/149 apps from the previous kits; no compilation or
Windows/physical access is required. Keep the previous reset protocol and its
60/120/150-second waits. Never repeat a launch or reset within a recorded case.

A private runner adds filter-dump Ethernet capture and nine NVNet events: PHY
reads/writes, link status and negotiation, unavailable receive/transmit conditions,
packet transmit and receive DMA. CPU access/register/IRQ/descriptor tracing stays
off. Trace and packet files each have a 16 MiB guard. Packet record offsets mark
the reset and second-launch boundaries; raw capture remains private. The pinned
net/dump.c uses writev for each record rather than buffered stdio.

Record actual DHCP transaction IDs, client MACs, requested/offered addresses and
message types. An ACK in a host packet capture alone does not prove guest receipt;
correlate receive DMA, subsequent traffic and the fresh FTP session. Preserve a
timeout and all missing output gates if either test fails. Host info network
queries are observations. There is no post-reset link toggle, guest register or
memory change, configuration intervention or added timeout.

The separate lifecycle verifier and cold audit still require the original twelve
exact files, reset evidence, normal second-phase reboot and complete E/F safety.
Successful diagnostic tracing does not establish a performance result or erase
the older control150 failure. A recurring loss needs a concrete producer before
any patch. If both new cases return, report the unresolved intermittent failure.
