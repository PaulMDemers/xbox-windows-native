# Watched first and second standalone launches

The user proposed comparing first and second launches because Windows sometimes
appeared to work every other time. This manual session is separate from the
completed overnight automation, which remains paused.

The first launch followed the requested full power-off/on and the user's reply
"Xbox is ready". This is contextual user evidence, not a measured power trace.
At18:23:32UTC the dashboard accepted one request for the previously unused528
standalone diagnostic. The user saw blue, then a green bar, then the dashboard.
The controller retrieved valid begin and entry receipts from kernel1.0.4034.1.
The first independent cold audit passed all five hives; both event logs and all
ten pre-existing collected files were unchanged. There was no Windows boot.

At18:26:13UTC a separately journaled second request used the exact same110592-byte
XBE, same E application path and same FTP launch method. SHA256:
`d2f32d69247358bddb7dad4274789c8645e496bfe60476ccd41889a39fc24499`.
No first-run receipt was deleted, renamed or reseeded. The user reported:
"Blue, then red this time. Auto returned to dash". No intervening manual reset
was reported. Blue demonstrates visible application execution on the second run;
red is consistent with deliberate CREATE_NEW refusal when the first receipt
already exists. Exact error text was not supplied, so that specific API failure
is not independently established. Old receipts cannot prove second execution.

Read final001.json for the completed second cold comparison. The first audit is
physical-final001.json in the sibling visible-dispatch528 directory. All original
first records are preserved. The second collector only reads owned paths and
relevant baseline files; it does not reset the experiment.

This pair did not reproduce an every-other-launch dispatch failure. It establishes
two observed standalone application entries, not Windows repeatability or a cause
for earlier failures. It cannot rule out state retained across Windows launches,
differences in Xromwell preparation, or diagnostic-file lifecycle. No firmware,
functional driver, ordinary launcher, startup or720p change was made. No temporary
startup hook was installed and dashboardC was not accessed.

Host validation remains distinct: second-host001's18 admission and2 FTP cases use
modeled evidence/transport. The second observer/collector uses528 bounded readback
helpers and a derived supervisor; its source review is syntax/manual review, not
another emulator or kernel qualification. The first PowerShell observation-record
command failed parsing a typographic apostrophe before execution; apply_patch
then wrote the JSON. A combined documentation patch was rejected before mutation
for targeting NEXT.md twice; the subsequent separate writes preserve that failure.
