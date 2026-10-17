# Xbox inventory attempt closed without a receipt

One accepted dashboard launch on October 17, 2026 returned to FTP without an
`xwn456` result directory or runner receipt. This does not establish whether the
probe ran, or identify the failing boot stage. It is not a Direct3D failure result.

Collection first removed the one-shot startup hook and verified the normal
startup, launcher and protected 720p baseline. All five registry hives and both
event logs are byte-identical to their prelaunch copies. Both independent hive
readers agree and report clean hives. Twenty-one frozen dependencies and both
payloads still match their pins; private captures remain private. Xbox C was
not accessed. No full allocation audit or normal Windows restart is proved.

The read-only observer was explicitly stopped after collection, before its
deadline. Its original partial record remains unchanged with `closed:false`;
the separate stop record states what happened. All owned processes are closed,
and the completed collection receipt and process check are retained.

The sample is the exact qualified PC455 binary, SHA256
`577bd78e1aae562eef1c7bc8c5d500f604e0d340fca50ea553504608dafdb143`.
The fresh controller compiled and its 24 imports match owned NT5 exports; the
sample has 21 matching imports. No runtime DLL, driver or display mode changed.
An inherited reconstruction namespace was corrected before package execution;
both source reviews remain separate. Do not relaunch, rearm or recollect456.

Evidence: [launch](physical001-launch.json), [partial observation](physical001-observation.json),
[observer stop](observer-stop001.json), [collection](physical001-collection.json),
[no-receipt review](no-receipt-review001.json), [closeout](final-review.json).
