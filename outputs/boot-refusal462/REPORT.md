# New first-refusal diagnostic; console observation pending

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
Screen observation is pending; FTP absence is not a boot failure. Do not repeat
this launch. Prior460/461 reports and their differing outcomes remain unchanged.

Evidence: [build](build001.json), [source review](source-review001.json),
[host cases](host001.json), [refusal decoder](refusal-tests001.json),
[primary decoder](decoder001.json), [launch](launch001.json).
