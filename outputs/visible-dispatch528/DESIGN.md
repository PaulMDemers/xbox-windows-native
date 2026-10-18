# 528 visible standalone control (preparation only)

527 closed with no physical receipt despite a scoped emulator pass. A silent
control cannot distinguish failed dispatch/runtime initialization from E-alias
or I/O refusal. This new candidate gives an early blue band and explicit text
before alias/file operations. It then prints each completed kernel/API result
and shows green for both verified receipt sequences or red for refusal/failure.
Blue is requested for12seconds, result for20seconds, then ordinary firmware
return. Kernel calls can block; requested delays are not hard guest deadlines.

Use standard nxdk720p API only, temporary for this standalone application. No
Windows driver, startup, resolution configuration, PCI scan, EEPROM change,
custom register patch, interrupt manipulation, pending clearing or consoleC
access. SDK mode setup itself programs video hardware; this is not a read-only
hardware query. nxdk CRT including automatic D alias setup runs before main;
an absent blue marker cannot distinguish those earlier stages from dispatch.

Inspect main.c against pinned SDK video/debug/mount/automount_d implementations.
Do not substitute different SDK or reconstruct a host model as runtime proof.
Host tests compile the actual engine and main with explicitly modeled APIs;
the actual Xbox build uses normal SDK headers. Validate early marker ordering,
bounded framebuffer access, alias refusal, status/error formatting, and one
close attempt per acquired handle. Existing aliases are never replaced.

48-byte schema and engine semantics are identical to527 except X528/attempt528.
Unique E:\Applications\XWNDispatch528 namespace; begin then entry CREATE_NEW,
no retry/deletion. Successful entry proves the earlier begin pipeline, not
its own final close/display/firmware return. Outcome text follows both pipelines
and is separate user/emulator image evidence. No Windows or stability promotion.

A screen-observer availability question is pending. Prepare host/build and fresh
emulator qualification independently; do not queue a physical launch yet. Once
ready, tell the observer blue->green/red->dashboard and ask for exact failure
text/photo only if needed. Physical deployment/launch requires a fresh one-shot
controller, exact readback/pins/paired cold audit and existing hardware ticket.
Never retry a closed or accepted/uncertain launch. Protect720p/ordinarybaseline,
20GiB C/WSL guard; no hostEallocation.13:50UTC reviewonly;14UTCclose/pause.
