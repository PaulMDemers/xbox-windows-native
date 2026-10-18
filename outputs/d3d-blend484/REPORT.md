# PC484: alpha endpoint qualification FAILED

One fresh PC fixture boot ran both default and HEL software cases and restarted
normally. QEMU exited0 at2026-10-18 04:35:25UTC, without host quit/terminate/kill
or watchdog expiry. This fixture is closed; never relaunch or parent it.
No physical console access occurred.

The original MIT sample compiled without warnings using pinned RosBE GCC8.4:
19,611bytes, SHA256
`edf7b7c796cd1ca1ba44a6c2cbbbab14007be003e7239cd2c92df65389927c12`.
Controller24 and sample26 static imports match the installed NT5 exports.

Both actual processes return0 and complete API/state/readback/cleanup records.
Both independently selected RGB software devices produce byte-identical images
for all six stages. The original independent oracle rejects alpha0 at pixel8,8.
Read-only analysis finds endpoint failures in1176 drawn pixels per stage/case:

| Stage | Ideal RGB | Actual drawn RGB | Original criterion |
|---|---|---|---|
| Clear | 00FF00 | 00FF00 throughout | Exact pass |
| Alpha0 | 00FF00 | 00FE00 | FAIL |
| Alpha85 | 55AA55 | 54A954 | Within predeclared one-level tolerance |
| Alpha170 | AA55AA | A954A9 | Within predeclared one-level tolerance |
| Alpha255 | FF00FF | FE00FE | FAIL |
| Blending disabled, alpha85 | FF00FF | FF00FF | Exact pass |

All2199 safe exterior pixels per image remain exact green. Full captures contain
1176 drawn and2920 background pixels, except the entirely green clear image.
The two endpoint failures total4704 pixels across both processes. The old oracle
and original results remain unchanged. No actual negative-control PASS is claimed
for already failing inputs; the success-only mutation/closeout scripts were not run.

The values fit division-by256-style arithmetic, but this is an inference from
selected pixels, not an instruction trace or proof of a particular implementation.
Primary-only colors cannot distinguish rounding each contribution from rounding
the sum. A separate486 mixed-color/factor-identity test was designed to distinguish
three fixed hypotheses before execution. It cannot retroactively qualify484.

Three host tests passed, including3456 synthetic row/channel pixel mutations,
metadata/vertex mutations and tolerance discriminators. The public batch checks
all six result suffixes; the initial generator inherited depth suffixes and was
corrected in the public batch BEFORE the sample build. The executed generator
is retained as preparation history, not a reproducible current batch recipe.

Cold audit:6493files/309directories, five clean/header-valid hives with independent
raw-value agreement, protected OS binaries unchanged, EventLog6006delta1. Source
and read-only1474560-byte floppy unchanged; QCOWcheck clean. Initial independent
read001 covered the failed-result subset. Read002 adds all actual module paths;
both are preserved. All11 live modules per process match independent cold bytes
and PE image sizes.154 frozen inputs archived privately. No QEMU/NBD/FUSE remains.
This is not a full NTFS allocation audit; inherited SOFTWARE typed DRM limitation
is retained. No presentation, performance, game, GPU or Xbox alpha qualification.

Evidence: [runtime](runtime-review001.json), [actual colors](failure-analysis001.json),
[complete independent reader](independent002.json), [modules](module-review002.json),
[closed failure](final-review.json). Binaries, images and Windows files stay private.
