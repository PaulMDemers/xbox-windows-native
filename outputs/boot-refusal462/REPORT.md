# First-refusal diagnostic: successful boot and normal restart

462 extends the reviewed461 wrapper with an immutable first-refusal record.
Reasons distinguish report create/write/flush/close, snapshot/eligibility refusals
and post-log payload/high-loader/low-loader mismatch. It captures primary return
status, IOSB, handle and close-attempt state BEFORE cleanup. A separate exclusive
refusal.bin uses its own handle/IOSB, with no recursion, retry or resume after a
refusal. Missing or incomplete refusal bytes mean UNKNOWN. A complete record
does not prove its own flush/close or reboot completion.

Successful-path source is byte-identical to461 after removing only MOV stores
for diagnostic stage/close state and normalizing462 namespace. It adds no success
path file operation. Entire original wrapper reconstructs after reversing11 edits;
original privileged loader and288316-byte embedded payload are unchanged. All
added diagnostics run before paging is discarded. Installed original launcher,
startup, drivers and720p settings remain untouched. No Xbox C access.

Actual assembled x86 host testing passed55 cases: the45 earlier primary cases
and10 fallback-failure variants. Kernel/file effects are MODELED, not Xbox proof.
Successful cases trap at CLI before privileged execution and verify restored
registers/flags. No fallback runs on success; all refusals preserve first status
and never hand off.48 complete fallback records were independently decoded;
976 malformed fallback controls and296 primary-report controls were rejected.
The remaining seven fallback captures are empty or short as expected. No ASan
or actual paging qualification claim.

Build001 SHA256:
`d71cc4e06b8a0477b0a8aa2fa4be8bcbbbf39b22682e8f0db35e37470d325e29`.
One SITE request for `E:\Applications\XWNBoot462a\default.xbe` was accepted at
2026-10-17 23:06:26UTC. No graphics hook or automatic Windows restart was installed.
The bounded dashboard observer did not establish return within its window.
The user subsequently reported the Windows desktop and confirmed dashboard return
after the requested normal restart. FTP absence during the observation window was
not a boot failure. This attempt is closed; never relaunch or recollect it.
Prior460/461 reports and their differing outcomes remain unchanged.

Evidence: [build](build001.json), [source review](source-review001.json),
[host cases](host001.json), [refusal decoder](refusal-tests001.json),
[primary decoder](decoder001.json), [launch](launch001.json).

## Actual collection and closeout

The complete176-byte preparation report passed independent decoding. No
`refusal.bin` was present. The desktop observation and fresh EventLog6005/6009
and6006 separately corroborate a Windows boot and normal shutdown; absence of a
refusal file alone would not prove successful handoff. All recorded nonidentity
preparation words match both failed460 and successful461, including allocations,
copy checks, jump targets and saved registers/flags. The intermittent cause remains
unresolved; this diagnostic is not a boot fix.

Five registry hives passed clean-header and independent raw-value checks. The
existing SOFTWARE DRM type1004 limitation remains a typed-decoder limitation;
raw values agree. Ten before-files and13 after-files were verified, plus four
private decoded event files:27 private files rehashed.269 mutations of the actual
primary report were rejected. No real refusal record was available for the
actual-refusal mutation branch; its host tests remain separate.

New system records589..594 contain Ftdisk49, EventLog6009/6005, Tcpip4201,
Srv2013 and EventLog6006. The Srv warning names Windows `F:` and is retained;
historical partition mapping identifies Windows F as dashboard C. No dashboard
C access or cleanup was performed. There are no new application events.
The scoped boot/selected cold audit passes; strict system qualification remains
FALSE for Ftdisk49 and Srv2013. No full FATX allocation audit or D3D test ran.

Original installed launcher, startup and protected720p files remain unchanged.
All owned processes are closed; no next launch is queued. See
[collection](collection001.json), [cold review](cold-review001.json),
[comparison and byte verification](closeout001.json), and [final review](final-review.json).
