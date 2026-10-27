#719 staged and verified: CR1b setup-boundary observations, awaiting watcher

718's failed restoration is CLOSED. It did not sample between initial85 and
explicit target05 write, so setup could have changed bit7 before that write.
719 samples six boundaries without any CR1b data writes: before setup, after
SEQ1 blank,80d3 blank,CR1f57,80d3 enable andSEQ1 restore. Existing blank/unlock/
output pair retained; no payload wait, new geometry/encoder/clock or CR22 writes.
Green719 requires all six samples85 and restoration checks. Orange needs raw
photo; no bit masking or repair. Read719/REPORT and optical-schema001.json.

190 instruction models,76 optical cases,12 CPU(all closed),23 nxdk page,
372 compiled ownership and131379 host ownership pass. Payload5100 padded9916,
16relocs/four absolute; bridge end558. Preserve failed compilepayload001 and
review-failure001 (reverse namespace comparison; corrected forward comparison).
Stage/readback complete; NO SITE request yet. Asked availability to watch,
photograph all13rows, and reset. Wait reply; do not launch without watcher.

No hook/owned host process; build/xemu released, hardware ticket retained.
Console dashboard at stage; original720p protected. All earlier runtimes CLOSED;
automation and other work tabled. Exact schema:7190000d, bridge phase/checkpoint/
return, payload phase/error, six samples, samplemask. Decode before reset; after
resetReady collect once/audit. Correlation at a setup boundary is not bit7 semantics
proof; no717 exact-error assignment,708/709 cause or Windows1.6 qualification.
