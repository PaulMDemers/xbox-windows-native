# 686 positive encoder-address response — physical attempt closed

The incoming user-identified 1.6 answered a kernel byte read at the Xcalibur
address. This provides positive device-presence evidence, beyond the older
inventory's two failed probes. It does not establish a unique silicon ID or a
working native video driver.

One SITE request was accepted at 2026-10-26 23:41:34 UTC. The tool made one
`HalReadSMBusValue` call per address, register zero, `ReadWordValue=FALSE`, with
no application retry or encoder configuration write. Kernel service duration
was not independently bounded. Five exclusive checkpoints were collected twice
byte-identically after dashboard return; the final one records a restart request.
No Windows boot or Windows normal shutdown was involved.

| Address (8-bit convention) | API status | Valid returned value | QPC ticks elapsed |
| --- | --- | --- | --- |
| Xcalibur `0xe0` | `0` | `4` | 2,012 |
| Conexant `0x8a` | `0xc0000185` | None | 203,430 |
| Focus `0xd4` | `0xc0000185` | None | 200,403 |

The failed calls also left `4` in their output variables. Those values are not
valid device data and are not used for classification. QPC reports 3,375,000 Hz;
these intervals describe kernel API duration, not raw wire timing. Entry and
all three post-call SMBus status snapshots were zero.

Kernel 1.0.5838.1, 64 MiB, GPU `0xd3`, MCP `0xd5`, and encoder settings 5112068
match the current unit's earlier records. Inventory630's GPU `0xe1` remains a
separate observation; this does not infer board revision from the GPU byte.

[Primary-source references](references.json) document the explicit address and
kernel-call convention. No OpenSauce implementation was copied. All eight
response-classification combinations and 14 compiled nxdk I/O fixtures passed
before launch. The latter used modeled port inputs, not physical I/O.

Exact source/binary pins are in [build001](build001.json). See
[launch](launch001.json), [collection](collection001.json) and
[closure](closure001.json). Staged bytes and unrelated E directory entries were
unchanged at collection. This is not a whole-volume health audit. The owned tool
and reports remain on E. No startup hook, C filesystem access, mode change or
ordinary launcher modification occurred. No host process remains owned by this
attempt. Do not rerun or recollect the closed runtime.

Next: [687 native integration plan](../xcal-entry687/NEXT.md).
